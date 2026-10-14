from typing import Any
from cinefactory.block_animation.contracts import QCFinding,Severity
class BlockAnimationQC:
    def originality_findings(self,episode):
        tokens=[x.strip().casefold() for x in episode.blocked_reference_tokens if x.strip()]; payload=episode.model_dump(mode='json',exclude={'blocked_reference_tokens'}); strings=[]
        def visit(v:Any):
            if isinstance(v,str): strings.append(v.casefold())
            elif isinstance(v,dict):
                for k,x in v.items(): strings.append(str(k).casefold()); visit(x)
            elif isinstance(v,list):
                for x in v: visit(x)
        visit(payload); text='\n'.join(strings)
        return [QCFinding(code='BLOCKED_REFERENCE_TOKEN',severity=Severity.ERROR,message=f'episode contains blocked reference token {t!r}; reusable mechanics are allowed, copied branding/story identifiers are not',detail={'token':t}) for t in tokens if t in text]
    def structural_findings(self,episode):
        out=[]; seen=set()
        for shot in episode.shots:
            if shot.shot_id in seen: out.append(QCFinding(code='DUPLICATE_SHOT_ID',severity=Severity.ERROR,message=f'duplicate shot_id {shot.shot_id}',shot_id=shot.shot_id))
            seen.add(shot.shot_id); ids=[a.actor_id for a in shot.actors]; aset=set(ids)
            if len(ids)!=len(aset): out.append(QCFinding(code='DUPLICATE_ACTOR_ID',severity=Severity.ERROR,message='actor_id repeated inside shot',shot_id=shot.shot_id))
            for a in shot.actions:
                if a.actor_id not in aset: out.append(QCFinding(code='UNKNOWN_ACTION_ACTOR',severity=Severity.ERROR,message=f'action references unknown actor {a.actor_id}',shot_id=shot.shot_id))
            for e in shot.expressions:
                if e.actor_id not in aset: out.append(QCFinding(code='UNKNOWN_EXPRESSION_ACTOR',severity=Severity.ERROR,message=f'expression references unknown actor {e.actor_id}',shot_id=shot.shot_id))
            for p in shot.props:
                if p.actor_id not in aset: out.append(QCFinding(code='UNKNOWN_PROP_ACTOR',severity=Severity.ERROR,message=f'prop binding references unknown actor {p.actor_id}',shot_id=shot.shot_id))
            for c in shot.crowd:
                missing=sorted(set(c.actor_ids)-aset)
                if missing: out.append(QCFinding(code='UNKNOWN_CROWD_ACTOR',severity=Severity.ERROR,message=f'crowd behavior references unknown actors {missing}',shot_id=shot.shot_id))
            for r in shot.reactions:
                if r.source_actor_id and r.source_actor_id not in aset: out.append(QCFinding(code='UNKNOWN_REACTION_SOURCE',severity=Severity.ERROR,message=f'reaction source references unknown actor {r.source_actor_id}',shot_id=shot.shot_id))
                missing=sorted(set(r.target_actor_ids)-aset)
                if missing: out.append(QCFinding(code='UNKNOWN_REACTION_TARGET',severity=Severity.ERROR,message=f'reaction references unknown target actors {missing}',shot_id=shot.shot_id))
            for g in shot.gaze:
                if g.actor_id not in aset: out.append(QCFinding(code='UNKNOWN_GAZE_ACTOR',severity=Severity.ERROR,message=f'gaze references unknown actor {g.actor_id}',shot_id=shot.shot_id))
                if g.target_actor_id and g.target_actor_id not in aset: out.append(QCFinding(code='UNKNOWN_GAZE_TARGET',severity=Severity.ERROR,message=f'gaze references unknown target actor {g.target_actor_id}',shot_id=shot.shot_id))
            missing=sorted(set(shot.camera.targets)-aset)
            if missing: out.append(QCFinding(code='UNKNOWN_CAMERA_TARGET',severity=Severity.ERROR,message=f'camera references unknown actors {missing}',shot_id=shot.shot_id))
        return out
