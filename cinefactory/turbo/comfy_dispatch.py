from __future__ import annotations

import time

from cinefactory.executors.base import ExecutionResult
from cinefactory.turbo.contracts import ResourceClass, WorkItem, WorkState


class TurboComfyDispatcher:
    """Submit ComfyUI work to the durable GPU queue and wait for the daemon result.

    This is the bridge that lets multiple planning/autopilot processes share one GPU queue
    without calling ComfyUI directly. The daemon owns provider execution; CineFactory Core
    still owns project/job truth.
    """
    def __init__(self,ctx,poll_seconds:float=0.25)->None:
        self.ctx=ctx; self.poll_seconds=poll_seconds

    def execute(self,*,project_id:str,workflow:dict,output_dir:str,model_affinity:str|None,timeout_seconds:int=1800,priority:int=50,provenance:dict|None=None)->ExecutionResult:
        payload={'workflow':workflow,'output_dir':output_dir}
        if provenance:
            payload.update(provenance)
        item=WorkItem(project_id=project_id,kind='comfy.render',handler='comfy.execute',resource=ResourceClass.GPU,priority=priority,model_affinity=model_affinity,payload=payload)
        self.ctx.turbo_store.enqueue_work(item)
        deadline=time.monotonic()+timeout_seconds
        while time.monotonic()<deadline:
            cur=self.ctx.turbo_store.get_work(item.work_id)
            if cur.state is WorkState.SUCCESS:
                r=cur.result
                return ExecutionResult(bool(r.get('ok',True)),list(r.get('artifacts',[])),dict(r.get('metadata',{})),r.get('error'))
            if cur.state in {WorkState.BLOCKED,WorkState.DEAD_LETTER,WorkState.CANCELLED}:
                return ExecutionResult(False,[],{'work_id':cur.work_id},cur.last_error or cur.state.value)
            time.sleep(self.poll_seconds)
        return ExecutionResult(False,[],{'work_id':item.work_id},f'Turbo GPU queue timed out after {timeout_seconds}s')
