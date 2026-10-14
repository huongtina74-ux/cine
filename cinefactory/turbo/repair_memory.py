from __future__ import annotations

import hashlib

from cinefactory.turbo.store import TurboStore


class RepairMemory:
    def __init__(self,store:TurboStore)->None:
        self.store=store

    @staticmethod
    def key(failure_code:str,workflow_id:str|None,shot_class:str|None,strategy:str)->str:
        raw="|".join([failure_code,workflow_id or "*",shot_class or "*",strategy])
        return hashlib.sha256(raw.encode()).hexdigest()[:24]

    def suggest(self,failure_code:str,workflow_id:str|None,shot_class:str|None):
        return self.store.best_repair(failure_code=failure_code,workflow_id=workflow_id,shot_class=shot_class)

    def record(self,*,failure_code:str,workflow_id:str|None,shot_class:str|None,strategy:str,prompt_directive:str|None,success:bool,score:float=0.0)->None:
        self.store.record_repair(key=self.key(failure_code,workflow_id,shot_class,strategy),failure_code=failure_code,workflow_id=workflow_id,shot_class=shot_class,strategy=strategy,prompt_directive=prompt_directive,success=success,score=score)
