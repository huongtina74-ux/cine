from cinefactory.block_animation.contracts import ResolvedReactionCue
from cinefactory.block_animation.utils import bounded,choose,unit_float
class ReactionEngine:
    def __init__(self,rules): self.rules=rules
    def compile(self,trigger,*,shot_id,candidate_actor_ids,duration_seconds):
        rules=self.rules.for_trigger(trigger.trigger)
        if not rules:return []
        targets=trigger.target_actor_ids or [x for x in candidate_actor_ids if x!=trigger.source_actor_id]; out=[]
        for actor_id in targets:
            seed=f'{shot_id}:{trigger.trigger}:{trigger.source_actor_id}:{actor_id}'; rule=rules[min(int(unit_float(seed+':rule')*len(rules)),len(rules)-1)]
            if unit_float(seed+':prob')>rule.probability: continue
            at=min(duration_seconds,trigger.at_seconds+bounded(seed+':delay',rule.min_delay_ms,rule.max_delay_ms)/1000)
            out.append(ResolvedReactionCue(actor_id=actor_id,trigger=trigger.trigger,source_actor_id=trigger.source_actor_id,start_seconds=at,clip_id=choose(seed+':clip',rule.clip_ids),expression_id=choose(seed+':expr',rule.expression_ids),intensity=bounded(seed+':intensity',rule.min_intensity,rule.max_intensity)))
        return out
