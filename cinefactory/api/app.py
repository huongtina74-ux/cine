from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from cinefactory.appctx import build_context
from cinefactory.autopilot import AutopilotRequest, AutopilotRunner
from cinefactory.doctor import Doctor
from cinefactory.creative.contracts import CreativeContractError
from cinefactory.domain.enums import CreativeStage, ProjectState
from cinefactory.domain.models import AssetBibleSpec, AssetRecord, DirectorPlan, ProjectRecord, ProjectSpec, RenderJob, ScriptSpec, ShotSpec, StorySpec
from cinefactory.originality import OriginalityGuard, ReferenceRecord, prior_project_references
from cinefactory.turbo import FactoryEvent, WorkItem
from cinefactory.turbo.metrics import gpu_snapshot

ctx = build_context()
app = FastAPI(title="CineFactory OS", version="1.4.0")


class ShotBatch(BaseModel):
    shots: list[ShotSpec]


@app.get("/", response_class=HTMLResponse)
def control_room():
    return """<!doctype html><html><head><meta charset='utf-8'><title>CineFactory OS</title>
<style>body{font-family:system-ui;background:#0d0f12;color:#eef;max-width:1100px;margin:30px auto;padding:0 18px}textarea,input,select,button{width:100%;box-sizing:border-box;margin:8px 0;padding:12px;background:#171a20;color:#eee;border:1px solid #3a414b;border-radius:8px}button{cursor:pointer;background:#e7edf6;color:#111;font-weight:700}pre{white-space:pre-wrap;background:#151920;padding:14px;border-radius:8px;min-height:160px}.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.card{background:#151920;border:1px solid #2c333d;padding:14px;border-radius:10px}h1,h2{margin-bottom:8px}</style></head>
<body><h1>CineFactory OS 1.4 — Turbo Control Room</h1><p>One prompt + always-on production control plane.</p>
<div class='cards'><div class='card'><b>Factory</b><pre id='factory'>loading...</pre></div><div class='card'><b>GPU</b><pre id='gpu'>loading...</pre></div><div class='card'><b>Workers</b><pre id='workers'>loading...</pre></div></div>
<h2>One Prompt</h2><textarea id='prompt' rows='5' placeholder='Describe the video you want...'></textarea>
<div class='row'><input id='profile' value='cinematic_story'><select id='mode'><option value='slate'>Slate acceptance mode</option><option value='comfyui'>Local ComfyUI production</option></select></div>
<button onclick='run()'>CREATE VIDEO</button><pre id='out'>Ready.</pre>
<script>async function refresh(){try{let s=await (await fetch('/turbo/status')).json();factory.textContent=JSON.stringify({work:s.work,events:s.events,throughput:s.throughput},null,2);workers.textContent=JSON.stringify(s.workers,null,2);gpu.textContent=JSON.stringify(await (await fetch('/turbo/gpu')).json(),null,2)}catch(e){factory.textContent=String(e)}};setInterval(refresh,3000);refresh();async function run(){let out=document.getElementById('out');out.textContent='Running...';let body={prompt:document.getElementById('prompt').value,profile:document.getElementById('profile').value,language:'vi',reasoning_mode:'scaffold',production_mode:document.getElementById('mode').value,master_4k:true};try{let r=await fetch('/autopilot',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});let j=await r.json();out.textContent=JSON.stringify(j,null,2)}catch(e){out.textContent=String(e)}};</script></body></html>"""


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "mode": ctx.policy.raw.get("mode"),
        "version": "1.4.0",
        "executors": ctx.executors.ids(),
    }


@app.get("/policy")
def get_policy() -> dict:
    return ctx.policy.raw


@app.post("/projects", response_model=ProjectRecord)
def create_project(spec: ProjectSpec) -> ProjectRecord:
    try:
        return ctx.orchestrator.create_project(spec)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/projects/{project_id}", response_model=ProjectRecord)
def get_project(project_id: str) -> ProjectRecord:
    try:
        return ctx.projects.get(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@app.get("/projects/{project_id}/audit")
def get_audit(project_id: str):
    return ctx.audit.list_for_project(project_id)


@app.post("/projects/{project_id}/policy-check", response_model=ProjectRecord)
def policy_check(project_id: str) -> ProjectRecord:
    try:
        return ctx.orchestrator.policy_check(project_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc


@app.post("/projects/{project_id}/transition/{target}", response_model=ProjectRecord)
def transition(project_id: str, target: ProjectState) -> ProjectRecord:
    try:
        return ctx.orchestrator.transition(project_id, target)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Project not found") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/projects/{project_id}/creative/story")
def submit_story(project_id: str, story: StorySpec):
    try:
        return ctx.creative.submit_story(project_id, story)
    except (KeyError, CreativeContractError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/projects/{project_id}/creative/script")
def submit_script(project_id: str, script: ScriptSpec):
    try:
        return ctx.creative.submit_script(project_id, script)
    except (KeyError, CreativeContractError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/projects/{project_id}/creative/assets")
def submit_assets(project_id: str, bible: AssetBibleSpec):
    try:
        return ctx.creative.submit_asset_bible(project_id, bible)
    except (KeyError, CreativeContractError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/projects/{project_id}/creative/director")
def submit_director(project_id: str, director: DirectorPlan):
    try:
        return ctx.creative.submit_director_plan(project_id, director)
    except (KeyError, CreativeContractError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/projects/{project_id}/creative/shots")
def submit_shots(project_id: str, batch: ShotBatch):
    try:
        return ctx.creative.submit_shots(project_id, batch.shots)
    except (KeyError, CreativeContractError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc




@app.post("/projects/{project_id}/assets", response_model=AssetRecord)
def register_asset(project_id: str, asset: AssetRecord):
    try:
        ctx.projects.get(project_id)
        ctx.assets.save(project_id, asset)
        return asset
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/projects/{project_id}/assets", response_model=list[AssetRecord])
def list_assets(project_id: str):
    return ctx.assets.list_project(project_id)


@app.post("/jobs")
def enqueue_job(job: RenderJob):
    try:
        result, created = ctx.job_service.enqueue(job)
        return {"created": created, "job": result}
    except (KeyError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/jobs/{job_id}", response_model=RenderJob)
def get_job(job_id: str):
    try:
        return ctx.jobs.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


@app.get("/projects/{project_id}/jobs", response_model=list[RenderJob])
def list_project_jobs(project_id: str):
    return ctx.jobs.list_project(project_id)


@app.post("/jobs/{job_id}/execute", response_model=RenderJob)
def execute_job(job_id: str):
    try:
        return ctx.job_service.execute_now(job_id)
    except (KeyError, RuntimeError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/references", response_model=ReferenceRecord)
def add_reference(record: ReferenceRecord):
    try:
        ctx.references.add(record)
        return record
    except FileExistsError as exc:
        raise HTTPException(status_code=409, detail="Reference already exists") from exc


@app.get("/references", response_model=list[ReferenceRecord])
def list_references():
    return ctx.references.list()


@app.get("/projects/{project_id}/originality")
def project_originality(project_id: str):
    refs=ctx.references.list()+prior_project_references(ctx.root/"data"/"projects", exclude_project_id=project_id)
    guard=OriginalityGuard()
    out={}
    try:
        story,_=ctx.creative.store.get_latest(project_id, CreativeStage.STORY, StorySpec)
        out["story"]=guard.check_story(story,refs).model_dump(mode="json")
    except KeyError:
        out["story"]={"status":"MISSING"}
    try:
        script,_=ctx.creative.store.get_latest(project_id, CreativeStage.SCRIPT, ScriptSpec)
        out["script"]=guard.check_script(script,refs).model_dump(mode="json")
    except KeyError:
        out["script"]={"status":"MISSING"}
    return out


@app.get("/doctor")
def doctor_report():
    return Doctor(ctx).run()


@app.post("/autopilot")
def autopilot(req: AutopilotRequest):
    result = AutopilotRunner(ctx).run(req)
    if not result.success:
        raise HTTPException(status_code=409, detail=result.model_dump(mode="json"))
    return result


@app.get("/turbo/status")
def turbo_status():
    return ctx.turbo_store.status()

@app.get("/turbo/gpu")
def turbo_gpu():
    return gpu_snapshot()

@app.get("/turbo/work")
def turbo_work():
    return [x.model_dump(mode="json") for x in ctx.turbo_store.list_work()]

@app.post("/turbo/work")
def turbo_enqueue(item: WorkItem):
    result,created=ctx.turbo_store.enqueue_work(item)
    return {"created":created,"work":result.model_dump(mode="json")}

@app.get("/turbo/events")
def turbo_events(limit:int=100):
    return ctx.turbo_store.list_events(limit=max(1,min(limit,500)))

@app.post("/turbo/events")
def turbo_publish(event: FactoryEvent):
    return ctx.turbo_store.publish_event(event).model_dump(mode="json")

@app.get("/turbo/workers")
def turbo_workers():
    return ctx.turbo_store.list_workers()
