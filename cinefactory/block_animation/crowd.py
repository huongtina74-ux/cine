from cinefactory.block_animation.contracts import ResolvedCrowdActor
from cinefactory.block_animation.utils import bounded,choose
class CrowdBehaviorEngine:
    def __init__(self,library,expression_library=None): self.library=library; self.expression_library=expression_library
    def compile(self,cue,*,shot_id,duration_seconds):
        b=self.library.get(cue.behavior_id); end=duration_seconds if cue.end_seconds is None else min(cue.end_seconds,duration_seconds); out=[]
        for actor_id in cue.actor_ids:
            seed=f'{shot_id}:{cue.group_id}:{actor_id}:{cue.behavior_id}'; phase=bounded(seed+':phase',0,b.phase_jitter_seconds); expression_id=choose(seed+':expr',b.expression_ids); channels={}
            if expression_id and self.expression_library is not None: channels={k:float(v) for k,v in self.expression_library.get(expression_id).channels.items()}
            out.append(ResolvedCrowdActor(actor_id=actor_id,behavior_id=cue.behavior_id,clip_id=choose(seed+':clip',b.clip_ids) or b.clip_ids[0],expression_id=expression_id,expression_channels=channels,phase_seconds=phase,intensity=bounded(seed+':intensity',b.intensity_min,b.intensity_max),start_seconds=min(duration_seconds,cue.start_seconds+phase),end_seconds=max(min(end,duration_seconds),min(duration_seconds,cue.start_seconds+phase+1e-3))))
        return out
