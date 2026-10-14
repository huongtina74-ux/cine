from pathlib import Path
import shutil

from cinefactory.appctx import build_context
from cinefactory.turbo import FactoryDaemon, ResourceClass, WorkerSpec, WorkItem


def make_root(tmp_path: Path)->Path:
    src=Path(__file__).resolve().parents[1]
    for name in ('config','models','workflows','knowledge'):
        if (src/name).is_dir(): shutil.copytree(src/name,tmp_path/name)
    return tmp_path


def test_daemon_executes_noop_and_records_throughput(tmp_path: Path):
    root=make_root(tmp_path)
    ctx=build_context(root)
    item=WorkItem(project_id='P',kind='noop',handler='noop',resource=ResourceClass.CPU)
    ctx.turbo_store.enqueue_work(item)
    d=FactoryDaemon(ctx,WorkerSpec(worker_id='cpu0',resources={ResourceClass.CPU},capabilities={'noop'}))
    assert d.tick() is True
    assert ctx.turbo_store.get_work(item.work_id).state.value=='SUCCESS'
    summary=ctx.turbo_store.throughput_summary()
    assert summary and summary[0]['samples']==1

def test_turbo_comfy_dispatch_roundtrip_without_provider(tmp_path: Path):
    import threading, time
    from cinefactory.turbo.comfy_dispatch import TurboComfyDispatcher
    root=make_root(tmp_path)
    ctx=build_context(root)
    daemon=FactoryDaemon(ctx,WorkerSpec(worker_id='gpu0',resources={ResourceClass.GPU},capabilities={'comfy.execute'}))
    daemon.register('comfy.execute', lambda item: {'ok':True,'artifacts':['fake.mp4'],'metadata':{'model':'hot'}})
    def worker():
        deadline=time.time()+2
        while time.time()<deadline:
            if daemon.tick(): return
            time.sleep(.01)
    t=threading.Thread(target=worker); t.start()
    result=TurboComfyDispatcher(ctx,poll_seconds=.01).execute(project_id='P',workflow={'1':{'class_type':'Fake'}},output_dir=str(root/'out'),model_affinity='FAST@1',timeout_seconds=2)
    t.join(timeout=2)
    assert result.ok
    assert result.artifacts==['fake.mp4']
