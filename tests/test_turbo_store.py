from pathlib import Path

from cinefactory.turbo.contracts import ResourceClass, WorkerSpec, WorkItem, WorkState
from cinefactory.turbo.store import TurboStore


def test_model_affinity_and_dependencies(tmp_path: Path):
    store=TurboStore(tmp_path/'turbo.db')
    a=WorkItem(project_id='P',kind='video',handler='noop',resource=ResourceClass.GPU,priority=50,model_affinity='LTX')
    b=WorkItem(project_id='P',kind='video',handler='noop',resource=ResourceClass.GPU,priority=50,model_affinity='WAN')
    c=WorkItem(project_id='P',kind='video',handler='noop',resource=ResourceClass.GPU,priority=99,model_affinity='WAN',dependencies=[b.work_id])
    for x in (a,b,c): store.enqueue_work(x)
    worker=WorkerSpec(worker_id='gpu0',resources={ResourceClass.GPU},capabilities={'noop'},active_model_affinity='LTX')
    got=store.claim_work(worker)
    assert got and got.work_id==a.work_id
    store.mark_running(got.work_id); store.finish_work(got.work_id,True)
    got2=store.claim_work(worker)
    assert got2 and got2.work_id==b.work_id
    store.mark_running(got2.work_id); store.finish_work(got2.work_id,True)
    got3=store.claim_work(worker)
    assert got3 and got3.work_id==c.work_id


def test_retry_is_durable(tmp_path: Path):
    store=TurboStore(tmp_path/'turbo.db')
    item=WorkItem(project_id='P',kind='x',handler='noop',resource=ResourceClass.CPU,max_attempts=2)
    store.enqueue_work(item)
    worker=WorkerSpec(worker_id='cpu0',resources={ResourceClass.CPU},capabilities={'noop'})
    got=store.claim_work(worker); assert got
    store.mark_running(got.work_id)
    assert store.finish_work(got.work_id,False,'boom') is WorkState.RETRY
    got=store.claim_work(worker); assert got
    store.mark_running(got.work_id)
    assert store.finish_work(got.work_id,False,'boom2') is WorkState.DEAD_LETTER


def test_runtime_managed_vram_uses_total_capacity_and_incremental_headroom(
    tmp_path: Path,
):
    gpu_meta = {
        "gpu": {
            "gpus": [
                {
                    "vram_mb": 12288.0,
                    "vram_used_mb": 10752.0,
                }
            ]
        }
    }
    worker = WorkerSpec(
        worker_id="gpu-runtime",
        resources={ResourceClass.GPU},
        capabilities={"block.video.comfy"},
        active_model_affinity="BLENDER:CYCLES",
        metadata=gpu_meta,
    )

    managed_store = TurboStore(
        tmp_path / "managed.db"
    )
    managed = WorkItem(
        project_id="P",
        kind="video",
        handler="block.video.comfy",
        resource=ResourceClass.GPU,
        model_affinity="COMFYUI:WAN",
        payload={
            "required_vram_gb": 8.0,
            "runtime_managed_vram": True,
            "hot_model_incremental_vram_gb": 0.75,
        },
    )
    managed_store.enqueue_work(managed)
    claimed = managed_store.claim_work(worker)
    assert claimed is not None
    assert claimed.work_id == managed.work_id

    unmanaged_store = TurboStore(
        tmp_path / "unmanaged.db"
    )
    unmanaged = WorkItem(
        project_id="P",
        kind="video",
        handler="block.video.comfy",
        resource=ResourceClass.GPU,
        model_affinity="COMFYUI:WAN",
        payload={
            "required_vram_gb": 8.0,
            "hot_model_incremental_vram_gb": 0.75,
        },
    )
    unmanaged_store.enqueue_work(unmanaged)
    assert unmanaged_store.claim_work(worker) is None


def test_runtime_managed_vram_still_rejects_device_too_small(
    tmp_path: Path,
):
    store = TurboStore(tmp_path / "small.db")
    item = WorkItem(
        project_id="P",
        kind="video",
        handler="block.video.comfy",
        resource=ResourceClass.GPU,
        payload={
            "required_vram_gb": 16.0,
            "runtime_managed_vram": True,
            "hot_model_incremental_vram_gb": 0.5,
        },
    )
    store.enqueue_work(item)
    worker = WorkerSpec(
        worker_id="gpu-small",
        resources={ResourceClass.GPU},
        capabilities={"block.video.comfy"},
        metadata={
            "gpu": {
                "gpus": [
                    {
                        "vram_mb": 12288.0,
                        "vram_used_mb": 2048.0,
                    }
                ]
            }
        },
    )
    assert store.claim_work(worker) is None
