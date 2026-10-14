from cinefactory.block_animation.contracts import ResolvedExpressionCue
from cinefactory.block_animation.utils import bounded
class ExpressionEngine:
    def __init__(self,library): self.library=library
    def compile(self,cue,*,shot_id,duration_seconds):
        d=self.library.get(cue.expression_id); end=cue.end_seconds
        if end is None:end=min(duration_seconds,cue.start_seconds+d.attack_seconds+.45+d.release_seconds)
        start=max(0,min(cue.start_seconds,duration_seconds)); end=max(start+1e-3,min(end,duration_seconds))
        intensity=max(0,min(1.5,cue.intensity*bounded(f'{shot_id}:{cue.actor_id}:{cue.expression_id}',.96,1.04)))
        channels={k:max(-1,min(1,float(v)*intensity)) for k,v in d.channels.items()}
        return ResolvedExpressionCue(actor_id=cue.actor_id,expression_id=cue.expression_id,start_seconds=start,end_seconds=end,intensity=intensity,channels=channels)
