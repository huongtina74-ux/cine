from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from cinefactory.autopilot.contracts import AutopilotRequest, AutopilotResult, StageStatus
from cinefactory.autopilot.scaffold import LocalScaffoldPlanner
from cinefactory.domain.enums import CreativeStage, ProjectState
from cinefactory.domain.models import AssetBibleSpec, DirectorPlan, ProjectSpec, ScriptSpec, ShotSpec, ShotSpecBatch, StorySpec
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.post.editor import AutoEditor
from cinefactory.post.openchatcut import OpenChatCutBridge
from cinefactory.post.mastering import MasteringService
from cinefactory.post.upscale import CommandUpscaler
from cinefactory.post.timeline import TimelineClip, TimelineSpec
from cinefactory.prompts.compiler import ShotPromptCompiler
from cinefactory.qc.technical import TechnicalQC
from cinefactory.qc.cinematic import CinematicQC
from cinefactory.qc.visual_command import CommandVisualQC
from cinefactory.qc.visual_policy import normalized_visual_review
from cinefactory.production.asset_factory import AssetFactory
from cinefactory.production.storyboard import StoryboardGate
from cinefactory.production.video_factory import VideoFactory
from cinefactory.production.intent import BackendKind, ProductionIntentRouter, WorkflowFamily, WorldTarget
from cinefactory.production.premium_gate import premium_preflight, premium_shot_gate
from cinefactory.reasoning.command_bridge import CommandReasoningBridge
from cinefactory.reasoning.file_bridge import FileReasoningBridge
from cinefactory.reasoning.prompts import StagePromptLibrary
from cinefactory.audio import AudioMixer, CommandTTS, EspeakTTS, SubtitleBuilder
from cinefactory.creative.contracts import CONTRACTS
from cinefactory.discovery.models import ResearchBrief, TopicStrategy
from cinefactory.discovery.gates import FactualityGate
from cinefactory.studio.contracts import ArtifactState, DepartmentId, StudioProjectSpec
from cinefactory.studio.governance import TraceEvent
from cinefactory.studio.production import ProductionCompiler
from cinefactory.originality import (
    DifferentiationPlan, OriginalityGuard, OriginalityPolicy, PackagingHypothesis, ReleasePackage,
    ScriptCritic, fingerprint_from_project, prior_project_references,
)


def now():
    return datetime.now(timezone.utc)


class AutopilotRunner:
    """End-to-end project runner.

    `slate` production mode is a deterministic local acceptance path that proves every
    factory stage and produces a real MP4 using FFmpeg. `comfyui` mode uses the same
    creative contracts and prepares/executes local workflow jobs when workflow manifests
    are installed by the operator.
    """

    def __init__(self, ctx) -> None:
        self.ctx = ctx
        self.scaffold = LocalScaffoldPlanner()
        self.compiler = ShotPromptCompiler()
        self.media = FFmpegToolchain()
        self.qc = TechnicalQC(self.media)
        self.cinematic_qc = CinematicQC()
        self.editor = AutoEditor(self.media)
        self.mastering = MasteringService(self.media)
        self.audio_mixer = AudioMixer(self.media)
        self.subtitles = SubtitleBuilder()
        self.stage_prompts = StagePromptLibrary(ctx.root / "knowledge")
        self.originality = OriginalityGuard(OriginalityPolicy.model_validate(ctx.policy.raw.get("originality", {})))
        self.script_critic = ScriptCritic()
        self.factuality = FactualityGate()
        self.intent_router = ProductionIntentRouter()
        self.studio_control = ctx.studio.control_plane
        self.production_compiler = ProductionCompiler()

    def _reasoner(self, req: AutopilotRequest, project_id: str):
        if req.reasoning_mode == "file":
            return FileReasoningBridge(self.ctx.root / "data" / "projects" / project_id / "reasoning")
        if req.reasoning_mode == "command":
            if not req.reasoning_command:
                raise ValueError("reasoning_command is required when reasoning_mode=command")
            return CommandReasoningBridge(req.reasoning_command)
        if req.reasoning_mode != "scaffold":
            raise ValueError("reasoning_mode must be scaffold, file, or command")
        return None

    @staticmethod
    def _finish(stage: StageStatus, status: str = "PASS", detail: str | None = None) -> None:
        stage.status = status; stage.detail = detail; stage.finished_at = now()

    def run(self, req: AutopilotRequest) -> AutopilotResult:
        # Fail before creating a project or invoking any renderer.
        premium_sources = premium_preflight(req)
        diagnostic_slate = req.production_mode == "slate" and req.quality_tier == "diagnostic"
        stages: list[StageStatus] = []
        warnings: list[str] = []
        final_video: str | None = None
        project = self.ctx.orchestrator.create_project(ProjectSpec(
            prompt=req.prompt, profile=req.profile, language=req.language, duration_seconds=req.duration_seconds
        ))
        pid = project.spec.project_id
        root = self.ctx.root / "data" / "projects" / pid
        root.mkdir(parents=True, exist_ok=True)
        reasoner = self._reasoner(req, pid)
        visual_qc = CommandVisualQC(req.visual_qc_command) if req.visual_qc_command else None
        if req.production_mode != "slate" and visual_qc is None:
            raise RuntimeError("LOCAL_VISUAL_QC_REQUIRED: missing review command; bypass is forbidden for generated footage")
        if diagnostic_slate:
            warnings.append("DIAGNOSTIC_SLATE_ONLY: generated MP4 is a technical test with ZERO artistic QC score, not a commercially approved video.")

        def stage(name: str) -> StageStatus:
            s=StageStatus(name=name,status="RUNNING"); stages.append(s); return s

        try:
            s=stage("policy")
            self.ctx.orchestrator.policy_check(pid); self._finish(s)

            s=stage("production_intent")
            intent = self.intent_router.route(
                req.prompt,
                workflow_family=WorkflowFamily(req.workflow_family) if req.workflow_family else None,
                world=WorldTarget(req.world_target) if req.world_target else None,
                backend=BackendKind(req.backend) if req.backend else None,
            )
            reports_dir = root / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            (reports_dir / "production_intent.json").write_text(intent.model_dump_json(indent=2), encoding="utf-8")
            warnings.extend(intent.warnings)
            self._finish(s, detail=f"{intent.workflow_family.value}/{intent.backend.value}; executable={intent.executable}")

            s=stage("studio_bootstrap")
            studio_project = StudioProjectSpec(
                studio_project_id=pid,
                prompt=req.prompt,
                language=req.language,
                duration_seconds=req.duration_seconds,
            )
            studio_plan = self.studio_control.plan(studio_project)
            route_map = {
                item.segment.segment_id: item.routes
                for item in studio_plan.segments
            }
            studio_recipe = self.production_compiler.compile(
                pid,
                [item.segment for item in studio_plan.segments],
                route_map,
            )
            project_dna = self.ctx.studio.dna_compiler.compile(studio_project, studio_plan.product)
            project_pod = self.ctx.studio.pod_builder.build(pid, studio_plan.product.format)

            bb = self.ctx.studio.blackboard
            bb.put(
                pid,
                "media_product",
                DepartmentId.CREATIVE_STRATEGY,
                studio_plan.product,
                state=ArtifactState.VALIDATED,
            )
            bb.put(
                pid,
                "project_dna",
                DepartmentId.CREATIVE_STRATEGY,
                project_dna,
                state=ArtifactState.VALIDATED,
            )
            bb.put(
                pid,
                "project_pod",
                DepartmentId.STUDIO_MANAGEMENT,
                project_pod,
                state=ArtifactState.VALIDATED,
            )
            bb.put(
                pid,
                "production_recipe",
                DepartmentId.TECHNICAL_DIRECTION,
                studio_recipe,
                state=ArtifactState.VALIDATED,
            )
            self.ctx.studio.trace.append(
                TraceEvent(
                    project_id=pid,
                    actor=DepartmentId.STUDIO_MANAGEMENT,
                    action="STUDIO_BOOTSTRAP",
                    decision=f"format={studio_plan.product.format.value}",
                    outputs=["media_product", "project_dna", "project_pod", "production_recipe"],
                    metadata={"blocked": studio_recipe.blocked, "blocker_count": len(studio_plan.blockers)},
                )
            )

            (reports_dir / "studio_bootstrap.json").write_text(
                json.dumps(
                    {
                        "project": studio_project.model_dump(mode="json"),
                        "product": studio_plan.product.model_dump(mode="json"),
                        "plan": studio_plan.model_dump(mode="json"),
                        "recipe": studio_recipe.model_dump(mode="json"),
                    },
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                ),
                encoding="utf-8",
            )
            warnings.extend(f"STUDIO_CAPABILITY_GAP:{item}" for item in studio_plan.blockers)
            warnings.extend(f"STUDIO_RECIPE_GAP:{item}" for item in studio_recipe.blockers)
            self._finish(
                s,
                detail=f"format={studio_plan.product.format.value}; blocked={len(studio_plan.blockers)}",
            )

            # Strategy + originality. Competitor raw text never enters creative reasoning context.
            references = self.ctx.references.list()
            if req.include_prior_projects:
                references += prior_project_references(self.ctx.root / "data" / "projects", exclude_project_id=pid)
            quarantined_refs = [r.quarantine_view() for r in references]

            s=stage("research")
            research = reasoner.generate(
                "research", self.stage_prompts.compose("research", req.prompt), ResearchBrief,
                {
                    "project": project.spec.model_dump(mode="json"),
                    "competitor_quarantine": quarantined_refs,
                    "instruction": "Competitor material is for collision avoidance only. Verify factual claims from independent primary/authoritative sources.",
                },
            ) if reasoner else ResearchBrief(topic=req.prompt, target_audience=None)
            research_decision = self.factuality.research(research)
            if not research_decision.passed:
                raise RuntimeError("RESEARCH_FACTUALITY_FAILED: " + "; ".join(research_decision.findings))
            c=CONTRACTS[CreativeStage.RESEARCH]
            self.ctx.creative.store.put(pid, c.stage, c.owner, research)
            self._finish(s, detail=f"claims={len(research.claims)}; gaps={len(research.gaps)}")

            s=stage("topic_strategy")
            strategy = reasoner.generate(
                "topic_strategy", self.stage_prompts.compose("topic_strategy", req.prompt), TopicStrategy,
                {
                    "project": project.spec.model_dump(mode="json"),
                    "research": research.model_dump(mode="json"),
                    "competitor_quarantine": quarantined_refs,
                },
            ) if reasoner else self.scaffold.topic_strategy(req.prompt)
            c=CONTRACTS[CreativeStage.TOPIC_STRATEGY]
            self.ctx.creative.store.put(pid, c.stage, c.owner, strategy); self._finish(s, detail=f"score={strategy.score.overall}")

            s=stage("packaging_v1")
            packaging = reasoner.generate(
                "packaging", self.stage_prompts.compose("packaging", req.prompt), PackagingHypothesis,
                {"topic_strategy": strategy.model_dump(mode="json"), "research": research.model_dump(mode="json")},
            ) if reasoner else self.scaffold.packaging(req.prompt, strategy)
            pkg_report = self.originality.check_packaging(
                title=packaging.title_candidates[0],
                thumbnail_concept=packaging.thumbnail_concepts[0],
                supporting_text=packaging.model_dump_json(),
                references=references,
                artifact_kind="PACKAGING_V1",
            )
            if req.originality_strict:
                self.originality.require_pass(pkg_report)
            c=CONTRACTS[CreativeStage.PACKAGING]
            pkg_meta=self.ctx.creative.store.put(pid, c.stage, c.owner, packaging)
            c=CONTRACTS[CreativeStage.ORIGINALITY]
            self.ctx.creative.store.put(pid, c.stage, c.owner, pkg_report, [pkg_meta.content_hash])
            self._finish(s, detail=f"originality={pkg_report.highest_similarity:.3f}")

            s=stage("originality_plan")
            diff_plan = reasoner.generate(
                "originality", self.stage_prompts.compose("originality", req.prompt), DifferentiationPlan,
                {
                    "topic_strategy": strategy.model_dump(mode="json"),
                    "packaging": packaging.model_dump(mode="json"),
                    "competitor_quarantine": quarantined_refs,
                },
            ) if reasoner else self.scaffold.originality_plan(strategy)
            c=CONTRACTS[CreativeStage.ORIGINALITY]
            diff_meta=self.ctx.creative.store.put(pid, c.stage, c.owner, diff_plan, [pkg_meta.content_hash])
            self._finish(s, detail=f"{len(diff_plan.differentiation_axes)} differentiation axes")

            # Creative chain. Reasoning bridges can replace deterministic fallback per stage.
            s=stage("story")
            story_context={
                "project": project.spec.model_dump(mode="json"),
                "topic_strategy": strategy.model_dump(mode="json"),
                "packaging_hypothesis": packaging.model_dump(mode="json"),
                "differentiation_plan": diff_plan.model_dump(mode="json"),
            }
            story=None; story_report=None
            for attempt in range(req.originality_retries + 1):
                story = reasoner.generate("story", self.stage_prompts.compose("story", req.prompt), StorySpec, story_context) if reasoner else self.scaffold.story(req.prompt)
                story_report=self.originality.check_story(story, references)
                story_fingerprint = fingerprint_from_project(story, strategy=strategy, differentiation=diff_plan)
                story_auth = self.originality.authenticity_report(
                    expression_report=story_report, fingerprint=story_fingerprint, references=references
                )
                if story_auth.passed or not req.originality_strict:
                    break
                if not reasoner or attempt >= req.originality_retries:
                    self.originality.require_authenticity_pass(story_auth)
                story_context={**story_context, "previous_draft": story.model_dump(mode="json"), "mandatory_rewrite_directives": story_auth.required_changes}
            assert story is not None and story_report is not None
            self.ctx.creative.submit_story(pid, story)
            c=CONTRACTS[CreativeStage.ORIGINALITY]
            self.ctx.creative.store.put(pid, c.stage, c.owner, story_report, [diff_meta.content_hash])
            self.ctx.creative.store.put(pid, c.stage, c.owner, story_auth, [diff_meta.content_hash])
            self._finish(s, detail=f"originality={story_report.highest_similarity:.3f}; channel_repeat={story_auth.channel_repetition_risk}")

            s=stage("script")
            script_context={
                "story": story.model_dump(mode="json"),
                "packaging_hypothesis": packaging.model_dump(mode="json"),
                "differentiation_plan": diff_plan.model_dump(mode="json"),
            }
            script=None; script_report=None; critic_report=None
            for attempt in range(req.originality_retries + 1):
                script = reasoner.generate("script", self.stage_prompts.compose("script", req.prompt), ScriptSpec, script_context) if reasoner else self.scaffold.script(story)
                critic_report=self.script_critic.review(script)
                script_report=self.originality.check_script(script, references)
                if (critic_report.passed and script_report.passed) or not req.originality_strict:
                    break
                directives=list(critic_report.revision_directives)+list(script_report.rewrite_directives)
                if not reasoner or attempt >= req.originality_retries:
                    if not critic_report.passed:
                        raise RuntimeError("SCRIPT_CRITIC_FAILED: " + "; ".join(directives))
                    self.originality.require_pass(script_report)
                script_context={**script_context, "previous_draft": script.model_dump(mode="json"), "mandatory_revision_directives": directives}
            assert script is not None and script_report is not None and critic_report is not None
            factual_script = self.factuality.script(script, research)
            if not factual_script.passed:
                raise RuntimeError("SCRIPT_FACTUALITY_FAILED: " + "; ".join(factual_script.findings))
            self.ctx.creative.submit_script(pid, script)
            c=CONTRACTS[CreativeStage.SCRIPT_REVIEW]
            critic_meta=self.ctx.creative.store.put(pid, c.stage, c.owner, critic_report)
            c=CONTRACTS[CreativeStage.ORIGINALITY]
            self.ctx.creative.store.put(pid, c.stage, c.owner, script_report, [critic_meta.content_hash])
            self._finish(s, detail=f"originality={script_report.highest_similarity:.3f}; critic={'PASS' if critic_report.passed else 'FAIL'}")

            s=stage("asset_bible")
            bible = reasoner.generate("asset_bible", self.stage_prompts.compose("asset_bible", req.prompt), AssetBibleSpec, {"story": story.model_dump(mode="json"), "script": script.model_dump(mode="json")}) if reasoner else self.scaffold.assets(script)
            self.ctx.creative.submit_asset_bible(pid, bible); self._finish(s)

            s=stage("asset_factory")
            asset_report = AssetFactory(self.ctx, visual_qc=visual_qc, min_visual_score=req.min_visual_score,
                                        diagnostic_slate=diagnostic_slate).build(
                pid, bible, root, mode=req.production_mode,
                workflow_id=req.asset_workflow_id, workflow_version=req.asset_workflow_version,
                candidates_per_asset=req.asset_candidates, width=1024, height=1024,
            )
            (root / "reports").mkdir(parents=True, exist_ok=True)
            (root / "reports" / "asset_factory.json").write_text(asset_report.model_dump_json(indent=2), encoding="utf-8")
            if not asset_report.passed:
                raise RuntimeError("ASSET_FACTORY_FAILED: " + "; ".join(asset_report.findings))
            # Persist the canonical reference IDs into a new immutable AssetBible version.
            self.ctx.creative.submit_asset_bible(pid, bible)
            self._finish(s, detail=f"canonical_assets={len(asset_report.selections)}")

            s=stage("director")
            director = reasoner.generate("director", self.stage_prompts.compose("director", req.prompt), DirectorPlan, {"script": script.model_dump(mode="json"), "assets": bible.model_dump(mode="json")}) if reasoner else self.scaffold.director(script)
            self.ctx.creative.submit_director_plan(pid, director); self._finish(s)

            s=stage("shot_specs")
            if reasoner:
                batch = reasoner.generate(
                    "shot_specs", self.stage_prompts.compose("shot_specs", req.prompt), ShotSpecBatch,
                    {"script":script.model_dump(mode="json"),"assets":bible.model_dump(mode="json"),"director":director.model_dump(mode="json")}
                )
                shots = batch.shots
            else:
                shots = self.scaffold.shots(script, director)
            self.ctx.creative.submit_shots(pid, shots); self._finish(s, detail=f"{len(shots)} shots")

            if req.quality_tier == "premium":
                s=stage("premium_director_binding")
                binding = premium_shot_gate(premium_sources, shots)
                (root / "reports").mkdir(exist_ok=True)
                (root / "reports" / "premium_director_binding.json").write_text(
                    json.dumps(binding, ensure_ascii=False, indent=2), encoding="utf-8")
                self._finish(s, detail=f"quality-first director route binding: {len(shots)} matched shots")

            s=stage("preproduction_authenticity_gate")
            final_fingerprint = fingerprint_from_project(
                story, strategy=strategy, differentiation=diff_plan, shots=shots
            )
            preprod_auth = self.originality.authenticity_report(
                expression_report=story_report, fingerprint=final_fingerprint, references=references
            )
            if req.originality_strict:
                self.originality.require_authenticity_pass(preprod_auth)
            c=CONTRACTS[CreativeStage.ORIGINALITY]
            self.ctx.creative.store.put(pid, c.stage, c.owner, preprod_auth)
            self._finish(s, detail=f"channel_repeat={preprod_auth.channel_repetition_risk}; concept_findings={len(preprod_auth.concept_findings)}")

            s=stage("storyboard_keyframe_gate")
            storyboard_report = StoryboardGate(self.ctx, visual_qc=visual_qc, min_visual_score=req.min_visual_score,
                                              diagnostic_slate=diagnostic_slate).build(
                shots, bible, root, mode=req.production_mode,
                workflow_id=req.keyframe_workflow_id, workflow_version=req.keyframe_workflow_version,
                candidates_per_shot=req.keyframe_candidates, width=req.render_width, height=req.render_height,
            )
            (root / "reports" / "storyboard_gate.json").write_text(storyboard_report.model_dump_json(indent=2), encoding="utf-8")
            if not storyboard_report.passed:
                raise RuntimeError("STORYBOARD_GATE_FAILED: " + "; ".join(storyboard_report.findings))
            keyframes = {x.shot_id: x.selected_path for x in storyboard_report.shots if x.selected_path}
            self._finish(s, detail=f"approved_keyframes={len(keyframes)}")

            s=stage("production")
            if req.production_mode == "slate":
                warnings.append("Slate mode validates pilot-first, keyframe-gated, multi-take production with diagnostic media instead of generative model footage.")
            video_workflow_id = req.video_workflow_id or req.workflow_id
            video_workflow_version = req.video_workflow_version if req.video_workflow_id else req.workflow_version
            factory = VideoFactory(
                self.ctx, visual_qc=visual_qc, min_visual_score=req.min_visual_score,
                early_accept_score=req.early_accept_score, max_repair_rounds=req.max_repair_rounds,
                turbo_dispatch=req.turbo_dispatch, turbo_timeout_seconds=req.turbo_timeout_seconds,
                diagnostic_slate=diagnostic_slate,
            )
            workflow_lanes = {
                "fast": (req.video_fast_workflow_id or video_workflow_id, req.video_fast_workflow_version if req.video_fast_workflow_id else video_workflow_version),
                "standard": (req.video_standard_workflow_id or video_workflow_id, req.video_standard_workflow_version if req.video_standard_workflow_id else video_workflow_version),
                "master": (req.video_master_workflow_id or video_workflow_id, req.video_master_workflow_version if req.video_master_workflow_id else video_workflow_version),
            }
            production_result = factory.run(
                project_root=root, shots=shots, bible=bible, keyframes=keyframes, mode=req.production_mode,
                workflow_id=video_workflow_id, workflow_version=video_workflow_version, workflow_lanes=workflow_lanes,
                render_width=req.render_width, render_height=req.render_height, pilot_count=req.pilot_count,
            )
            (root / "reports" / "dailies.json").write_text(production_result.dailies.model_dump_json(indent=2), encoding="utf-8")
            self.ctx.orchestrator.transition(pid, ProjectState.PILOT_GENERATED)
            if any(not x.passed for x in production_result.pilot_reports):
                failed = [x.shot_id for x in production_result.pilot_reports if not x.passed]
                raise RuntimeError("PILOT_FAILED: " + ",".join(failed))
            self.ctx.orchestrator.transition(pid, ProjectState.PILOT_APPROVED)
            self.ctx.orchestrator.transition(pid, ProjectState.BATCH_PRODUCTION)
            if not production_result.dailies.passed:
                raise RuntimeError("DAILIES_FAILED: " + "; ".join(production_result.dailies.findings))
            selected = production_result.selected_paths
            clips = [Path(selected[shot.shot_id]) for shot in shots]
            self._finish(s, detail=f"pilot={production_result.pilot_shot_ids}; accepted_takes={len(clips)}")

            s=stage("shot_qc")
            for shot, clip in zip(shots, clips):
                q=self.qc.video(clip)
                if not q.passed: raise RuntimeError(f"QC failed {shot.shot_id}: {q.findings}")
            self.ctx.orchestrator.transition(pid, ProjectState.SHOT_QC_COMPLETE); self._finish(s, detail="selected takes passed technical QC")

            s=stage("sequence_qc")
            cq = self.cinematic_qc.sequence(shots)
            if not cq.passed:
                raise RuntimeError(f"Cinematic sequence QC failed: {cq.findings}")
            self.ctx.orchestrator.transition(pid, ProjectState.SEQUENCE_QC_COMPLETE); self._finish(s, detail="cinematic sequence grammar passed")

            s=stage("auto_edit")
            timeline = TimelineSpec(project_id=pid, fps=project.spec.output.fps, width=project.spec.output.width, height=project.spec.output.height,
                clips=[TimelineClip(clip_id=f"CLIP_{i:03d}", shot_id=shot.shot_id, path=str(path), order=i) for i,(shot,path) in enumerate(zip(shots,clips))])
            timeline_path=root/"post"/"timeline.json"; timeline_path.parent.mkdir(parents=True, exist_ok=True); timeline_path.write_text(timeline.model_dump_json(indent=2),encoding="utf-8")
            if req.openchatcut_command:
                bridge_result = OpenChatCutBridge(req.openchatcut_command).send(timeline)
                candidate = bridge_result.get("output_path") or bridge_result.get("rendered_video")
                if candidate and Path(candidate).is_file():
                    rough = Path(candidate).resolve()
                else:
                    warnings.append("OpenChatCut bridge returned no rendered output; deterministic FFmpeg fallback was used.")
                    rough=self.editor.render_rough_cut(timeline, root/"post"/"rough_cut.mp4")
            else:
                rough=self.editor.render_rough_cut(timeline, root/"post"/"rough_cut.mp4")
            self.ctx.orchestrator.transition(pid, ProjectState.EDIT_LOCKED); self._finish(s, detail=str(rough))

            s=stage("audio_master")
            active_cut = rough
            total_duration = self.media.probe(rough).duration
            subtitle_path = self.subtitles.from_script(script, root/"post"/"subtitles.srt", total_duration)
            if req.tts_mode != "none":
                dialogue_text = " ".join(line.text for scene in script.scenes for line in scene.dialogue).strip()
                if dialogue_text:
                    if req.tts_mode == "espeak":
                        tts = EspeakTTS()
                    elif req.tts_mode == "command":
                        if not req.tts_command: raise ValueError("tts_command required when tts_mode=command")
                        tts = CommandTTS(req.tts_command)
                    else:
                        raise ValueError("tts_mode must be none, espeak, or command")
                    voice_path = tts.synthesize(dialogue_text, root/"post"/"voice.wav", language=req.language, voice=req.voice)
                    active_cut = self.audio_mixer.replace_or_mix_voice(rough, voice_path, root/"post"/"rough_cut_voiced.mp4")
            self.ctx.orchestrator.transition(pid, ProjectState.AUDIO_MASTERED); self._finish(s, detail=f"audio={active_cut}; subtitles={subtitle_path}")

            s=stage("color_master")
            self.ctx.orchestrator.transition(pid, ProjectState.COLOR_MASTERED); self._finish(s, detail="BT.709 mastering path")

            s=stage("master_4k")
            master_path=root/"master"/"final_4k.mp4"
            if req.master_4k:
                upscaler = CommandUpscaler(req.upscale_command) if req.upscale_command else None
                if upscaler is None:
                    warnings.append("4K master uses deterministic Lanczos resize/encode only. Configure --upscale-command for perceptual local restoration.")
                master,q=self.mastering.master(active_cut, master_path, width=project.spec.output.width,height=project.spec.output.height,fps=project.spec.output.fps, upscaler=upscaler)
                if not q.passed: raise RuntimeError(f"Master QC failed: {q.findings}")
                final_video=str(master)
            else:
                final_video=str(active_cut)
            self.ctx.orchestrator.transition(pid, ProjectState.MASTER_4K_VALIDATED); self._finish(s, detail=final_video)

            s=stage("whole_film_qa")
            master_qc = self.qc.video(Path(final_video))
            if not master_qc.passed:
                raise RuntimeError("WHOLE_FILM_TECHNICAL_QC_FAILED: " + "; ".join(master_qc.findings))
            if visual_qc is not None:
                whole = visual_qc.review(final_video, {
                    "kind": "whole_film",
                    "story": story.model_dump(mode="json"),
                    "script": script.model_dump(mode="json"),
                    "director": director.model_dump(mode="json"),
                    "shots": [x.model_dump(mode="json") for x in shots],
                    "requirements": [
                        "story clarity", "emotional progression", "pacing", "visual continuity",
                        "camera grammar", "performance continuity", "absence of severe artifacts"
                    ],
                })
                (root / "reports" / "whole_film_visual_qc.json").write_text(whole.model_dump_json(indent=2), encoding="utf-8")
                whole_passed, whole_scores, whole_findings = normalized_visual_review(
                    whole, min_score=req.min_visual_score)
                if not whole_passed:
                    raise RuntimeError("WHOLE_FILM_VISUAL_QC_FAILED: " + "; ".join(whole_findings))
            self._finish(s, detail="technical" + (" + local VLM" if visual_qc is not None else ""))

            s=stage("final_packaging")
            release = reasoner.generate(
                "release_package", self.stage_prompts.compose("release_package", req.prompt), ReleasePackage,
                {"story":story.model_dump(mode="json"),"script":script.model_dump(mode="json"),"packaging_hypothesis":packaging.model_dump(mode="json"),"final_video":final_video},
            ) if reasoner else self.scaffold.release_package(script, packaging)
            release_text="\n".join([release.final_title, release.thumbnail_concept, release.description, *release.chapters])
            release_report=self.originality.check_packaging(
                title=release.final_title,
                thumbnail_concept=release.thumbnail_concept,
                supporting_text=release_text,
                references=references,
                artifact_kind="RELEASE_PACKAGE",
            )
            if req.originality_strict:
                self.originality.require_pass(release_report)
            release.originality_report=release_report
            release_path=root/"release"/"package.json"; release_path.parent.mkdir(parents=True, exist_ok=True); release_path.write_text(release.model_dump_json(indent=2),encoding="utf-8")
            c=CONTRACTS[CreativeStage.RELEASE_PACKAGE]
            rel_meta=self.ctx.creative.store.put(pid, c.stage, c.owner, release)
            c=CONTRACTS[CreativeStage.ORIGINALITY]
            self.ctx.creative.store.put(pid, c.stage, c.owner, release_report, [rel_meta.content_hash])
            self._finish(s, detail=f"originality={release_report.highest_similarity:.3f}")

            s=stage("rights_final")
            rights=self.ctx.rights_gate.project_assets(pid)
            if not rights.passed:
                raise RuntimeError("RIGHTS_FINAL_FAIL: " + "; ".join(rights.findings))
            self.ctx.orchestrator.transition(pid, ProjectState.RIGHTS_FINAL_PASS)
            self._finish(s, detail="registered assets cleared")

            manifest = AutopilotResult(project_id=pid, success=True, stages=stages,
                                      final_video=final_video, release_package_path=str(release_path),
                                      warnings=warnings, quality_certified=False, release_ready=False)
            manifest_path=root/"autopilot_manifest.json"; manifest.manifest_path=str(manifest_path); manifest_path.write_text(manifest.model_dump_json(indent=2),encoding="utf-8")
            return manifest
        except Exception as exc:
            if stages and stages[-1].status == "RUNNING": self._finish(stages[-1], "FAIL", str(exc))
            try:
                self.ctx.orchestrator.block(pid, str(exc))
            except Exception:
                pass
            result=AutopilotResult(project_id=pid,success=False,stages=stages,final_video=final_video,
                                   warnings=warnings+[str(exc)],quality_certified=False,release_ready=False)
            path=root/"autopilot_manifest.json"; result.manifest_path=str(path); path.write_text(result.model_dump_json(indent=2),encoding="utf-8")
            return result
