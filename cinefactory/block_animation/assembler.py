from __future__ import annotations
from pathlib import Path
from cinefactory.block_animation.camera import CameraCoverageEngine
from cinefactory.block_animation.contracts import ActionCue,BlenderAnimationJob,CompiledEpisode,CompiledShot,EpisodeQCReport,EpisodeSpec,ExpressionCue,FactoryEnqueuePlan,QCFinding,SemanticEventCue,Severity
from cinefactory.block_animation.crowd import CrowdBehaviorEngine
from cinefactory.block_animation.events import VFXSoundEventEngine
from cinefactory.block_animation.expression import ExpressionEngine
from cinefactory.block_animation.props import PropSocketSystem
from cinefactory.block_animation.qc import BlockAnimationQC
from cinefactory.block_animation.reaction import ReactionEngine
from cinefactory.block_animation.registry import BlockAnimationLibraries
from cinefactory.block_animation.styles import validate_episode_style
from cinefactory.turbo.contracts import ResourceClass,WorkItem
from cinefactory.turbo.store import TurboStore

class EpisodeAssemblyError(ValueError):
    def __init__(self,report):
        self.report=report; errors=[x.message for x in report.findings if x.severity is Severity.ERROR]
        super().__init__('episode failed QC: '+'; '.join(errors[:8]))

class EpisodeAssembler:
    def __init__(self,libraries:BlockAnimationLibraries,*,root:Path|None=None):
        self.libraries=libraries; self.root=Path(root).resolve() if root is not None else None
        self.expressions=ExpressionEngine(libraries.expressions); self.reactions=ReactionEngine(libraries.reactions)
        self.props=PropSocketSystem(libraries.rigs,libraries.props); self.cameras=CameraCoverageEngine(libraries.cameras)
        self.crowds=CrowdBehaviorEngine(libraries.crowds,libraries.expressions); self.events=VFXSoundEventEngine(libraries.events); self.qc=BlockAnimationQC()
    @classmethod
    def from_root(cls,root:Path):
        root=Path(root).resolve(); return cls(BlockAnimationLibraries.load(root),root=root)
    def _asset_path_finding(self,source_path,*,asset_kind,asset_id,shot_id):
        if not source_path or self.root is None:return None
        p=Path(source_path); p=(self.root/p if not p.is_absolute() else p).resolve()
        if p!=self.root and self.root not in p.parents:return QCFinding(code='ASSET_PATH_ESCAPE',severity=Severity.ERROR,message=f'{asset_kind} {asset_id} source escapes CineFactory root: {p}',shot_id=shot_id)
        if not p.exists():return QCFinding(code='ASSET_NOT_FOUND',severity=Severity.ERROR,message=f'{asset_kind} {asset_id} source not found: {p}',shot_id=shot_id)
        return None
    def _safe_timing_action(self,action,*,duration,default_duration,shot_id,findings):
        start=action.start_seconds
        if start>=duration:
            new=max(0,duration-min(1/24,duration/2)); findings.append(QCFinding(code='ACTION_START_CLAMPED',severity=Severity.WARNING,message=f'action {action.clip_id} start exceeded shot duration',shot_id=shot_id,repaired=True,detail={'from':start,'to':new})); start=new
        end=action.end_seconds if action.end_seconds is not None else start+default_duration/action.speed
        if end>duration: findings.append(QCFinding(code='ACTION_END_CLAMPED',severity=Severity.WARNING,message=f'action {action.clip_id} end exceeded shot duration',shot_id=shot_id,repaired=True,detail={'from':end,'to':duration})); end=duration
        if end<=start: end=min(duration,start+max(1/24,default_duration/max(action.speed,.05))); findings.append(QCFinding(code='ACTION_RANGE_REPAIRED',severity=Severity.WARNING,message=f'action {action.clip_id} had non-positive duration',shot_id=shot_id,repaired=True))
        return action.model_copy(update={'start_seconds':start,'end_seconds':end})
    def _validate_expression_channels(self,cue,*,rig,shot_id,findings):
        if not rig.expression_map:return cue
        unsupported=sorted(set(cue.channels)-set(rig.expression_map))
        if not unsupported:return cue
        channels={k:v for k,v in cue.channels.items() if k in rig.expression_map}; findings.append(QCFinding(code='UNSUPPORTED_EXPRESSION_CHANNELS_DROPPED',severity=Severity.WARNING if channels else Severity.ERROR,message=f'rig {rig.rig_id} does not map expression channels {unsupported}',shot_id=shot_id,repaired=bool(channels),detail={'channels':unsupported}))
        return cue.model_copy(update={'channels':channels})
    def compile(self,episode:EpisodeSpec,*,output_dir:Path|None=None):
        findings=self.qc.originality_findings(episode)+self.qc.structural_findings(episode)
        if episode.metadata.get('visual_style_gate'):
            findings += validate_episode_style(episode, self.libraries)
        if any(x.severity is Severity.ERROR for x in findings): raise EpisodeAssemblyError(EpisodeQCReport(passed=False,findings=findings,repairs_applied=sum(x.repaired for x in findings)))
        try:
            render_quality=self.libraries.render_quality.get(episode.quality_profile)
        except KeyError as exc:
            findings.append(QCFinding(code='UNKNOWN_RENDER_QUALITY_PROFILE',severity=Severity.ERROR,message=str(exc)))
            raise EpisodeAssemblyError(EpisodeQCReport(passed=False,findings=findings,repairs_applied=sum(x.repaired for x in findings)))
        compiled=[]
        for order,shot in enumerate(episode.shots):
            try: scene=self.libraries.scenes.get(shot.scene_template_id)
            except KeyError as exc: findings.append(QCFinding(code='UNKNOWN_SCENE_TEMPLATE',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id)); continue
            issue=self._asset_path_finding(scene.source_path,asset_kind='scene',asset_id=scene.scene_id,shot_id=shot.shot_id)
            if issue:findings.append(issue)
            actor_by_id={a.actor_id:a for a in shot.actors}; rigs={}; resolved_actors=[]
            for actor in shot.actors:
                try: rig=self.libraries.rigs.get(actor.rig_id)
                except KeyError as exc: findings.append(QCFinding(code='UNKNOWN_RIG',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id)); continue
                rigs[actor.actor_id]=rig; issue=self._asset_path_finding(rig.source_path,asset_kind='rig',asset_id=rig.rig_id,shot_id=shot.shot_id)
                if issue:findings.append(issue)
                if actor.marker and actor.transform is None:
                    marker=scene.markers.get(actor.marker)
                    if marker is None: findings.append(QCFinding(code='UNKNOWN_SCENE_MARKER',severity=Severity.ERROR,message=f'scene {scene.scene_id} has no marker {actor.marker!r}',shot_id=shot.shot_id))
                    else: actor=actor.model_copy(update={'transform':marker})
                resolved_actors.append(actor)
            clips={}; actions=[]
            for action in shot.actions:
                rig=rigs.get(action.actor_id)
                if not rig:continue
                try:
                    clip=self.libraries.clips.ensure_compatible(action.clip_id,rig.skeleton_profile)
                    issue=self._asset_path_finding(clip.source_path,asset_kind='clip',asset_id=clip.clip_id,shot_id=shot.shot_id)
                    if issue:findings.append(issue)
                    if clip.source_path and not clip.action_name:findings.append(QCFinding(code='CLIP_ACTION_NAME_MISSING',severity=Severity.ERROR,message=f'clip {clip.clip_id} has source_path but no action_name',shot_id=shot.shot_id))
                except (KeyError,ValueError) as exc: findings.append(QCFinding(code='INVALID_ACTION_CLIP',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id)); continue
                clips[clip.clip_id]=clip; action=self._safe_timing_action(action,duration=shot.duration_seconds,default_duration=clip.duration_seconds,shot_id=shot.shot_id,findings=findings)
                if action.layer is None:action=action.model_copy(update={'layer':clip.layer})
                actions.append(action)
            expressions=[]
            for cue in shot.expressions:
                rig=rigs.get(cue.actor_id)
                if not rig:continue
                try: expressions.append(self._validate_expression_channels(self.expressions.compile(cue,shot_id=shot.shot_id,duration_seconds=shot.duration_seconds),rig=rig,shot_id=shot.shot_id,findings=findings))
                except KeyError as exc:findings.append(QCFinding(code='UNKNOWN_EXPRESSION',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id))
            resolved_reactions=[]
            for trigger in shot.reactions:
                if trigger.at_seconds>shot.duration_seconds:findings.append(QCFinding(code='REACTION_TRIGGER_CLAMPED',severity=Severity.WARNING,message=f'reaction trigger {trigger.trigger} exceeded shot duration',shot_id=shot.shot_id,repaired=True)); trigger=trigger.model_copy(update={'at_seconds':shot.duration_seconds})
                rs=self.reactions.compile(trigger,shot_id=shot.shot_id,candidate_actor_ids=list(actor_by_id),duration_seconds=shot.duration_seconds)
                if not rs: findings.append(QCFinding(code='NO_REACTION_RULE',severity=Severity.WARNING,message=f'no reaction rule for {trigger.trigger}',shot_id=shot.shot_id))
                for r in rs:
                    rig=rigs.get(r.actor_id)
                    if not rig:continue
                    if r.clip_id:
                        try:
                            clip=self.libraries.clips.ensure_compatible(r.clip_id,rig.skeleton_profile); clips[clip.clip_id]=clip; actions.append(ActionCue(actor_id=r.actor_id,clip_id=clip.clip_id,start_seconds=r.start_seconds,end_seconds=min(shot.duration_seconds,r.start_seconds+clip.duration_seconds),intensity=r.intensity,layer=clip.layer))
                        except (KeyError,ValueError) as exc:findings.append(QCFinding(code='INVALID_REACTION_CLIP',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id))
                    if r.expression_id:
                        try: expressions.append(self._validate_expression_channels(self.expressions.compile(ExpressionCue(actor_id=r.actor_id,expression_id=r.expression_id,start_seconds=r.start_seconds,intensity=r.intensity),shot_id=shot.shot_id,duration_seconds=shot.duration_seconds),rig=rig,shot_id=shot.shot_id,findings=findings))
                        except KeyError as exc:findings.append(QCFinding(code='INVALID_REACTION_EXPRESSION',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id))
                    resolved_reactions.append(r)
            resolved_gaze=[]
            for cue in shot.gaze:
                if cue.actor_id not in actor_by_id:
                    findings.append(QCFinding(code='UNKNOWN_GAZE_ACTOR',severity=Severity.ERROR,message=f'gaze references unknown actor {cue.actor_id}',shot_id=shot.shot_id))
                    continue
                if cue.target_actor_id and cue.target_actor_id not in actor_by_id:
                    findings.append(QCFinding(code='UNKNOWN_GAZE_TARGET',severity=Severity.ERROR,message=f'gaze references unknown target actor {cue.target_actor_id}',shot_id=shot.shot_id))
                    continue
                start=min(float(cue.start_seconds),max(0.0,shot.duration_seconds-1/24))
                end=float(cue.end_seconds) if cue.end_seconds is not None else shot.duration_seconds
                end=min(end,shot.duration_seconds)
                if end<=start:
                    end=min(shot.duration_seconds,start+max(1/24,shot.duration_seconds/8))
                    findings.append(QCFinding(code='GAZE_RANGE_REPAIRED',severity=Severity.WARNING,message=f'gaze range repaired for {cue.actor_id}',shot_id=shot.shot_id,repaired=True))
                resolved_gaze.append(cue.model_copy(update={'start_seconds':start,'end_seconds':end}))
            resolved_props=[]
            for cue in shot.props:
                actor=actor_by_id.get(cue.actor_id)
                if not actor:continue
                try:
                    pdef=self.libraries.props.get(cue.prop_id); issue=self._asset_path_finding(pdef.source_path,asset_kind='prop',asset_id=pdef.prop_id,shot_id=shot.shot_id)
                    if issue:findings.append(issue)
                    resolved_props.append(self.props.resolve(cue,rig_id=actor.rig_id,duration_seconds=shot.duration_seconds))
                except (KeyError,ValueError) as exc:findings.append(QCFinding(code='INVALID_PROP_BINDING',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id))
            try:camera_takes=self.cameras.compile(shot.camera,shot_id=shot.shot_id,duration_seconds=shot.duration_seconds,scene=scene)
            except (KeyError,ValueError) as exc:findings.append(QCFinding(code='INVALID_CAMERA_COVERAGE',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id)); camera_takes=[]
            rcrowd=[]
            for cue in shot.crowd:
                try: crowd=self.crowds.compile(cue,shot_id=shot.shot_id,duration_seconds=shot.duration_seconds)
                except KeyError as exc:findings.append(QCFinding(code='INVALID_CROWD_BEHAVIOR',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id)); continue
                for m in crowd:
                    rig=rigs.get(m.actor_id)
                    if not rig:continue
                    try:clip=self.libraries.clips.ensure_compatible(m.clip_id,rig.skeleton_profile); clips[clip.clip_id]=clip
                    except (KeyError,ValueError) as exc:findings.append(QCFinding(code='INVALID_CROWD_CLIP',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id))
                    if m.expression_id and rig.expression_map:m=m.model_copy(update={'expression_channels':{k:v*m.intensity for k,v in m.expression_channels.items() if k in rig.expression_map}})
                    rcrowd.append(m)
            revents=[]
            for cue in shot.events:
                try:revents.append(self.events.compile(cue,duration_seconds=shot.duration_seconds))
                except KeyError as exc:findings.append(QCFinding(code='UNKNOWN_EVENT',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id))
            for action in actions:
                if not action.emit_event:continue
                try:revents.append(self.events.compile(SemanticEventCue(event_id=action.emit_event,at_seconds=action.start_seconds,source_actor_id=action.actor_id,target_id=action.target,intensity=action.intensity),duration_seconds=shot.duration_seconds))
                except KeyError as exc:findings.append(QCFinding(code='UNKNOWN_ACTION_EVENT',severity=Severity.ERROR,message=str(exc),shot_id=shot.shot_id))
            out_path=str((Path(output_dir)/'shots'/f'{order:04d}_{shot.shot_id}.mp4').resolve()) if output_dir is not None else None
            compiled.append(CompiledShot(shot_id=shot.shot_id,order=order,scene=scene,duration_seconds=shot.duration_seconds,fps=episode.fps,width=episode.width,height=episode.height,render_engine=episode.render_engine,render_quality=render_quality,actors=resolved_actors,rigs=rigs,actions=actions,clips=clips,expressions=expressions,reactions=resolved_reactions,gaze=resolved_gaze,props=resolved_props,creative_intent=dict(shot.creative_intent),performance_directives=list(shot.performance_directives),lighting_intent=dict(shot.lighting_intent),prop_definitions={p.prop_id:self.libraries.props.get(p.prop_id) for p in shot.props if p.prop_id in self.libraries.props},camera_takes=camera_takes,crowd=rcrowd,events=sorted(revents,key=lambda x:x.at_seconds),output_path=out_path,visual_style=scene.style))
        report=EpisodeQCReport(passed=not any(x.severity is Severity.ERROR for x in findings),findings=findings,repairs_applied=sum(x.repaired for x in findings))
        if not report.passed:raise EpisodeAssemblyError(report)
        return CompiledEpisode(project_id=episode.project_id,episode_id=episode.episode_id,title=episode.title,fps=episode.fps,width=episode.width,height=episode.height,shots=compiled,qc=report,library_fingerprint=self.libraries.fingerprint(),output_dir=str(Path(output_dir).resolve()) if output_dir is not None else None)
    def write_compiled(self,compiled,path):
        path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(compiled.model_dump_json(indent=2),encoding='utf-8'); return path
    def enqueue(self,compiled,store:TurboStore,*,output_dir:Path,blender_executable:str|None=None):
        output_dir=Path(output_dir).resolve(); output_dir.mkdir(parents=True,exist_ok=True); render_ids=[]; timeline_ids=[]
        for shot in compiled.shots:
            output_path=Path(shot.output_path) if shot.output_path else output_dir/'shots'/f'{shot.order:04d}_{shot.shot_id}.mp4'
            payload={'job':BlenderAnimationJob(project_id=compiled.project_id,episode_id=compiled.episode_id,shot=shot,output_path=str(output_path)).model_dump(mode='json'),'output_units':max(1,shot.frame_end)}
            if blender_executable: payload['blender_executable']=blender_executable
            r=WorkItem(project_id=compiled.project_id,kind='block.render',handler='blender.animation.render',resource=ResourceClass.GPU,priority=max(50,90-shot.order),model_affinity=f'BLENDER:{shot.render_engine}',payload=payload,max_attempts=2); store.enqueue_work(r); render_ids.append(r.work_id)
            t=WorkItem(project_id=compiled.project_id,kind='timeline.accept',handler='timeline.accept',resource=ResourceClass.IO,priority=60,dependencies=[r.work_id],payload={'shot_id':shot.shot_id,'path':str(output_path),'order':shot.order,'duration_seconds':shot.duration_seconds,'edit_intent':{'camera_take':shot.camera_takes[0].take_id if shot.camera_takes else None}}); store.enqueue_work(t); timeline_ids.append(t.work_id)
        a=WorkItem(project_id=compiled.project_id,kind='block.episode.assemble',handler='block.episode.assemble',resource=ResourceClass.IO,priority=55,dependencies=timeline_ids,payload={'episode_id':compiled.episode_id,'output_path':str(output_dir/f'{compiled.episode_id}.mp4'),'shots':[{'shot_id':s.shot_id,'order':s.order,'path':s.output_path or str(output_dir/'shots'/f'{s.order:04d}_{s.shot_id}.mp4')} for s in compiled.shots]}); store.enqueue_work(a)
        return FactoryEnqueuePlan(render_work_ids=render_ids,timeline_work_ids=timeline_ids,assemble_work_id=a.work_id)
