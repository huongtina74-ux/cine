from pathlib import Path
from cinefactory.turbo.repair_memory import RepairMemory
from cinefactory.turbo.store import TurboStore


def test_repair_memory_prefers_successful_strategy(tmp_path: Path):
    m=RepairMemory(TurboStore(tmp_path/'t.db'))
    for ok in (True,True,False):
        m.record(failure_code='IDENTITY_DRIFT',workflow_id='wan',shot_class='RED',strategy='strong_refs',prompt_directive='lock face',success=ok,score=.9 if ok else .2)
    for ok in (False,False):
        m.record(failure_code='IDENTITY_DRIFT',workflow_id='wan',shot_class='RED',strategy='new_seed',prompt_directive='new seed',success=ok,score=.1)
    best=m.suggest('IDENTITY_DRIFT','wan','RED')
    assert best and best.strategy=='strong_refs'
    assert best.success_rate>0.6
