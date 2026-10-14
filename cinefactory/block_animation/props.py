from cinefactory.block_animation.contracts import ResolvedPropBinding
class PropSocketSystem:
    def __init__(self,rigs,props): self.rigs=rigs; self.props=props
    def resolve(self,cue,*,rig_id,duration_seconds):
        rig=self.rigs.get(rig_id); prop=self.props.get(cue.prop_id); socket=cue.socket or prop.default_socket
        if not socket: raise ValueError(f'prop {cue.prop_id} has no socket and cue did not provide one')
        bone=rig.sockets.get(socket)
        if not bone: raise ValueError(f'rig {rig_id} does not expose socket {socket!r} for prop {cue.prop_id}')
        end=duration_seconds if cue.end_seconds is None else min(cue.end_seconds,duration_seconds)
        if end<=cue.start_seconds:end=min(duration_seconds,cue.start_seconds+1e-3)
        return ResolvedPropBinding(prop_id=cue.prop_id,actor_id=cue.actor_id,socket=socket,bone_name=bone,start_seconds=min(cue.start_seconds,duration_seconds),end_seconds=end,attach_offset=prop.attach_offset)
