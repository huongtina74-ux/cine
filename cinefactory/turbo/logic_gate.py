from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field

from cinefactory.core.continuity import ContinuityValidator
from cinefactory.domain.models import ShotSpec


@dataclass
class LogicGateResult:
    passed: bool
    shots: list[ShotSpec]
    repaired_fields: list[str]=field(default_factory=list)
    findings: list[str]=field(default_factory=list)
    warnings: list[str]=field(default_factory=list)


class PreRenderLogicGate:
    """Cheap deterministic checks before any GPU video generation.

    It may fill only *missing* continuity values from the previous exit state. It never
    overwrites an explicit creative decision. Explicit contradictions are returned to the
    owning creative layer instead of burning GPU on an impossible transition.
    """
    def __init__(self)->None:
        self.continuity=ContinuityValidator()

    def _fill_missing(self,prev:ShotSpec,curr:ShotSpec,repaired:list[str])->None:
        a=prev.exit_state; b=curr.entry_state
        for field in ("location_id","time_of_day","weather","light_state","camera_side","motion_axis"):
            if getattr(b,field) is None and getattr(a,field) is not None:
                setattr(b,field,getattr(a,field)); repaired.append(f"{curr.shot_id}.entry_state.{field}")
        for cid,prev_state in a.characters.items():
            if cid not in b.characters: continue
            cur=b.characters[cid]
            for field in ("costume_id","position","facing","eyeline"):
                if getattr(cur,field) is None and getattr(prev_state,field) is not None:
                    setattr(cur,field,getattr(prev_state,field)); repaired.append(f"{curr.shot_id}.{cid}.{field}")
        for prop,state in a.props.items():
            if prop not in b.props:
                b.props[prop]=state; repaired.append(f"{curr.shot_id}.prop.{prop}")

    def validate(self,shots:list[ShotSpec],auto_fill_missing:bool=True)->LogicGateResult:
        shots=deepcopy(shots); repaired=[]; findings=[]; warnings=[]
        for i,shot in enumerate(shots):
            for j,beat in enumerate(shot.action_beats):
                if beat.start_second is not None and beat.start_second>shot.duration_seconds:
                    findings.append(f"ACTION_AFTER_SHOT:{shot.shot_id}:{j}")
                if beat.end_second is not None and beat.end_second>shot.duration_seconds:
                    findings.append(f"ACTION_END_AFTER_SHOT:{shot.shot_id}:{j}")
                if beat.start_second is not None and beat.end_second is not None and beat.end_second<=beat.start_second:
                    findings.append(f"ACTION_TIMING_INVALID:{shot.shot_id}:{j}")
            if i==0: continue
            prev=shots[i-1]
            if shot.previous_shot_id and shot.previous_shot_id!=prev.shot_id:
                findings.append(f"PREVIOUS_SHOT_LINK_MISMATCH:{shot.shot_id}:{shot.previous_shot_id}!={prev.shot_id}")
            if prev.next_shot_id and prev.next_shot_id!=shot.shot_id:
                findings.append(f"NEXT_SHOT_LINK_MISMATCH:{prev.shot_id}:{prev.next_shot_id}!={shot.shot_id}")
            # A scene boundary is an explicit discontinuity boundary; do not force state carry-over.
            if prev.scene_id != shot.scene_id:
                continue
            if auto_fill_missing: self._fill_missing(prev,shot,repaired)
            for issue in self.continuity.validate_adjacent(prev,shot):
                text=f"{issue.code}:{issue.field}:{issue.previous_value}->{issue.next_value}"
                # Position/facing/eyeline changes can be legitimate omitted movement or coverage changes.
                # They are surfaced for review but do not waste GPU by hard-blocking the whole batch.
                if any(issue.field.endswith(sfx) for sfx in ('.position','.facing','.eyeline')):
                    warnings.append(text)
                else:
                    findings.append(text)
        return LogicGateResult(passed=not findings,shots=shots,repaired_fields=repaired,findings=findings,warnings=warnings)
