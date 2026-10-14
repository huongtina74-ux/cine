from __future__ import annotations
from dataclasses import dataclass, field
from cinefactory.domain.models import ShotSpec


@dataclass
class CinematicQCResult:
    passed: bool
    findings: list[str]=field(default_factory=list)


class CinematicQC:
    def shot(self,shot:ShotSpec)->CinematicQCResult:
        f=[]
        if len(shot.camera.narrative_purpose.strip())<8: f.append('CAMERA_PURPOSE_WEAK')
        if shot.camera.movement.kind!='static' and len(shot.camera.movement.purpose.strip())<8: f.append('CAMERA_MOVE_UNMOTIVATED')
        if shot.performance and not shot.camera.focus_target: f.append('PERFORMANCE_NO_FOCUS_TARGET')
        if len(shot.action_beats)>4 and shot.duration_seconds<8: f.append('ACTION_OVERLOADED')
        return CinematicQCResult(not f,f)

    def sequence(self,shots:list[ShotSpec])->CinematicQCResult:
        f=[]
        if not shots:return CinematicQCResult(False,['NO_SHOTS'])
        sizes=[s.camera.shot_size.lower() for s in shots]
        run=1
        for i in range(1,len(sizes)):
            run=run+1 if sizes[i]==sizes[i-1] else 1
            if run>=4:f.append(f'REPETITIVE_SHOT_SIZE:{sizes[i]}:{run}')
        moving=sum(1 for s in shots if s.camera.movement.kind!='static')
        if len(shots)>=4 and moving==len(shots): f.append('EVERY_SHOT_MOVES_CAMERA')
        for a,b in zip(shots,shots[1:]):
            if a.scene_id==b.scene_id and a.exit_state.camera_side and b.entry_state.camera_side and a.exit_state.camera_side!=b.entry_state.camera_side:
                f.append(f'AXIS_SIDE_CHANGE:{a.shot_id}->{b.shot_id}')
        return CinematicQCResult(not f,f)
