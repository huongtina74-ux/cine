from cinefactory.block_animation.contracts import ResolvedEventCue
class VFXSoundEventEngine:
    def __init__(self,library): self.library=library
    def compile(self,cue,*,duration_seconds):
        d=self.library.get(cue.event_id); return ResolvedEventCue(event_id=cue.event_id,event_type=d.event_type,at_seconds=min(cue.at_seconds,duration_seconds),renderer_event=d.renderer_event,sound_asset=d.sound_asset,source_actor_id=cue.source_actor_id,target_id=cue.target_id,intensity=cue.intensity)
