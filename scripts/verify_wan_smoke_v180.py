from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.turbo.contracts import ResourceClass,WorkerSpec
from cinefactory.turbo.daemon import FactoryDaemon
from cinefactory.turbo.store import TurboStore

def main():
    out=ROOT/"data"/"verification"/"v180_cross_backend"/"wan_smoke"
    out.mkdir(parents=True,exist_ok=True)
    db=out/"turbo.db"
    if db.exists(): db.unlink()
    ctx=build_context(ROOT)
    ctx.turbo_store=TurboStore(db)

    ns=runpy.run_path(str(ROOT/"tests"/"test_block_auto_repair_v173.py"))
    ep=ns["_episode"]().model_copy(
        deep=True,
        update={"project_id":"V180_WAN_SMOKE","episode_id":"V180_WAN_SMOKE"},
    )
    comp=EpisodeAssembler.from_root(ROOT).compile(ep,output_dir=out)
    shot=comp.shots[0]
    ref=ROOT/"data"/"verification"/"v179_candidate_promotion"/"cycles_matrix"/"S01.cycles.golden.mp4"
    item=ctx.cross_backend_video.build_work_item(
        compiled=comp,
        shot=shot,
        output_path=out/"S01.wan13b.mp4",
        render_preview=True,
        switch_round=1,
        switch_of_work_id="REFERENCE_CYCLES",
        reference_frame_path=ref,
        recurring_identity_required=True,
        semantic_performance_required=False,
        precise_camera_required=False,
    )
    ctx.turbo_store.enqueue_work(item)
    worker=FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v180-wan-gpu",
            resources={ResourceClass.GPU},
            capabilities={"block.video.comfy"},
            active_model_affinity=item.model_affinity,
        ),
        poll_seconds=.05,
    )
    try:
        claimed=worker.tick()
    finally:
        worker.close()
    result=ctx.turbo_store.get_work(item.work_id)
    payload={
        "claimed":claimed,
        "work_id":item.work_id,
        "state":result.state.value,
        "last_error":result.last_error,
        "result":result.result,
        "payload_contract":item.payload["video_request"],
    }
    (out/"wan_smoke_verification.json").write_text(
        json.dumps(payload,indent=2),encoding="utf-8"
    )
    print(json.dumps(payload,indent=2))

if __name__=="__main__":
    main()
