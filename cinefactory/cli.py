from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import typer

from cinefactory.appctx import build_context
from cinefactory.autopilot import AutopilotRequest, AutopilotRunner
from cinefactory.doctor import Doctor
from cinefactory.workflows.importer import WorkflowImporter
from cinefactory.workflows.registry import WorkflowManifest
from cinefactory.domain.enums import CreativeStage, ProjectState
from cinefactory.domain.models import AssetBibleSpec, DirectorPlan, ProjectSpec, RenderJob, ScriptSpec, ShotSpec, StorySpec
from cinefactory.originality import ConceptFingerprint, OriginalityGuard, ReferenceKind, prior_project_references
from cinefactory.turbo import FactoryDaemon, ResourceClass, WorkerSpec, WorkItem
from cinefactory.turbo.logic_gate import PreRenderLogicGate
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import EpisodeSpec
from cinefactory.block_animation.factory import ContinuousBlockFactory
from cinefactory.production import intent as production_intent
from cinefactory.studio.company import (
    CompanyBlueprint,
    CompanyOrchestrator,
)
from cinefactory.studio.company_handlers import (
    FilmCompanyHandlers,
    FilmHandlerConfig,
)
from cinefactory.studio.company_runner import AutonomousCompanyRunner
from cinefactory.studio.contracts import (
    PlanningInputKind,
    PlanningInputRef,
    StudioProjectSpec,
)
from cinefactory.studio.execution_mastery import ExecutionMasteryRunner
from cinefactory.studio.tool_knowledge import audit_tool_mastery
from cinefactory.studio.production_qualification import (
    AttestationKind,
    ProductionQualificationBoard,
    QualificationAttestation,
)
from cinefactory.studio.production import ProductionCompiler
from cinefactory.studio.reference_intelligence import (
    ReferenceAcquisitionPolicy,
    ReferenceIntelligenceEngine,
    ReferenceVideoDecomposer,
)
from cinefactory.studio.script_intelligence import ScriptInputCompiler

app = typer.Typer(help="CineFactory OS CLI")
ROOT = Path(__file__).resolve().parents[1]


def context():
    return build_context(ROOT)


def load_model(path: Path, model_type):
    return model_type.model_validate_json(path.read_text(encoding="utf-8"))


def _planning_inputs_from_cli(
    *,
    script_file: Path | None = None,
    outline_file: Path | None = None,
    reference_script_file: list[Path] | None = None,
) -> list[PlanningInputRef]:
    inputs: list[PlanningInputRef] = []
    if script_file is not None and outline_file is not None:
        raise typer.BadParameter(
            "Use either --script-file or --outline-file as the primary script source, not both."
        )
    if script_file is not None:
        inputs.append(
            PlanningInputRef(
                kind=PlanningInputKind.SCRIPT,
                uri=str(script_file.resolve()),
                metadata={
                    "primary": True,
                    "revision_policy": "LOCK",
                },
            )
        )
    if outline_file is not None:
        inputs.append(
            PlanningInputRef(
                kind=PlanningInputKind.SCRIPT_OUTLINE,
                uri=str(outline_file.resolve()),
                metadata={"primary": script_file is None},
            )
        )
    for path in reference_script_file or []:
        inputs.append(
            PlanningInputRef(
                kind=PlanningInputKind.REFERENCE_SCRIPT,
                uri=str(path.resolve()),
            )
        )
    return inputs


@app.command()
def create(
    prompt: str = typer.Option(..., "--prompt"),
    profile: str = typer.Option("cinematic_story", "--profile"),
    language: str = typer.Option("vi", "--language"),
    duration: int | None = typer.Option(None, "--duration"),
) -> None:
    ctx = context()
    record = ctx.orchestrator.create_project(
        ProjectSpec(prompt=prompt, profile=profile, language=language, duration_seconds=duration)
    )
    typer.echo(record.model_dump_json(indent=2))


@app.command("policy-check")
def policy_check(project_id: str) -> None:
    record = context().orchestrator.policy_check(project_id)
    typer.echo(record.model_dump_json(indent=2))


@app.command("transition")
def transition(project_id: str, target: ProjectState) -> None:
    record = context().orchestrator.transition(project_id, target)
    typer.echo(record.model_dump_json(indent=2))


@app.command("submit-story")
def submit_story(project_id: str, file: Path) -> None:
    artifact = context().creative.submit_story(project_id, load_model(file, StorySpec))
    typer.echo(artifact.model_dump_json(indent=2))


@app.command("submit-script")
def submit_script(project_id: str, file: Path) -> None:
    artifact = context().creative.submit_script(project_id, load_model(file, ScriptSpec))
    typer.echo(artifact.model_dump_json(indent=2))


@app.command("submit-assets")
def submit_assets(project_id: str, file: Path) -> None:
    artifact = context().creative.submit_asset_bible(project_id, load_model(file, AssetBibleSpec))
    typer.echo(artifact.model_dump_json(indent=2))


@app.command("submit-director")
def submit_director(project_id: str, file: Path) -> None:
    artifact = context().creative.submit_director_plan(project_id, load_model(file, DirectorPlan))
    typer.echo(artifact.model_dump_json(indent=2))


@app.command("submit-shots")
def submit_shots(project_id: str, file: Path) -> None:
    raw = json.loads(file.read_text(encoding="utf-8"))
    shots = [ShotSpec.model_validate(item) for item in raw]
    artifact = context().creative.submit_shots(project_id, shots)
    typer.echo(artifact.model_dump_json(indent=2))


@app.command("enqueue-job")
def enqueue_job(file: Path) -> None:
    job = load_model(file, RenderJob)
    result, created = context().job_service.enqueue(job)
    typer.echo(json.dumps({"created": created, "job": result.model_dump(mode="json")}, ensure_ascii=False, indent=2, default=str))


@app.command("execute-job")
def execute_job(job_id: str) -> None:
    job = context().job_service.execute_now(job_id)
    typer.echo(job.model_dump_json(indent=2))


@app.command("audit")
def audit(project_id: str) -> None:
    events = context().audit.list_for_project(project_id)
    typer.echo(json.dumps([e.model_dump(mode="json") for e in events], ensure_ascii=False, indent=2, default=str))


@app.command("workflows")
def list_workflows() -> None:
    items = context().workflows.list()
    typer.echo(json.dumps([x.model_dump(mode="json") for x in items], ensure_ascii=False, indent=2))


@app.command("import-workflow")
def import_workflow(
    file: Path = typer.Option(..., "--file", exists=True, readable=True),
    workflow_id: str = typer.Option(..., "--id"),
    version: str = typer.Option("1", "--version"),
    media_type: str = typer.Option("video", "--media-type"),
    model_id: str = typer.Option(..., "--model-id"),
    model_revision: str | None = typer.Option(None, "--model-revision"),
    executor_id: str = typer.Option("local.comfyui", "--executor"),
) -> None:
    ctx=context()
    manifest=WorkflowManifest(
        workflow_id=workflow_id, version=version, executor_id=executor_id, media_type=media_type,
        model_id=model_id, model_revision=model_revision, workflow_file="workflow.api.json", local_only=True,
    )
    workflow_path, manifest_path = WorkflowImporter(ctx.root / "workflows").import_api_json(file, manifest)
    typer.echo(json.dumps({"workflow":str(workflow_path),"manifest":str(manifest_path)},indent=2))


@app.command("route")
def route_production(
    prompt: str = typer.Option(..., "--prompt"),
    workflow_family: str | None = typer.Option(None, "--workflow-family"),
    world_target: str | None = typer.Option(None, "--world"),
    backend: str | None = typer.Option(None, "--backend"),
) -> None:
    router = production_intent.ProductionIntentRouter()
    result = router.route(
        prompt,
        workflow_family=production_intent.WorkflowFamily(workflow_family) if workflow_family else None,
        world=production_intent.WorldTarget(world_target) if world_target else None,
        backend=production_intent.BackendKind(backend) if backend else None,
    )
    typer.echo(result.model_dump_json(indent=2))


@app.command("backend-capabilities")
def show_backend_capabilities() -> None:
    values = [item.model_dump(mode="json") for item in production_intent.backend_capabilities()]
    typer.echo(json.dumps(values, ensure_ascii=False, indent=2))


@app.command("studio-plan")
def studio_plan(
    prompt: str = typer.Option(..., "--prompt"),
    language: str = typer.Option("vi", "--language"),
    duration: int | None = typer.Option(None, "--duration"),
    script_file: Path | None = typer.Option(
        None,
        "--script-file",
        exists=True,
        readable=True,
    ),
    outline_file: Path | None = typer.Option(
        None,
        "--outline-file",
        exists=True,
        readable=True,
    ),
    reference_script_file: list[Path] = typer.Option(
        [],
        "--reference-script-file",
        exists=True,
        readable=True,
    ),
) -> None:
    ctx = context()
    project = StudioProjectSpec(
        prompt=prompt,
        language=language,
        duration_seconds=duration,
        planning_inputs=_planning_inputs_from_cli(
            script_file=script_file,
            outline_file=outline_file,
            reference_script_file=reference_script_file,
        ),
    )
    plan = ctx.studio.control_plane.plan(project)
    route_map = {
        item.segment.segment_id: item.routes
        for item in plan.segments
    }
    recipe = ProductionCompiler().compile(
        project.studio_project_id,
        [item.segment for item in plan.segments],
        route_map,
    )
    typer.echo(json.dumps({
        "project": project.model_dump(mode="json"),
        "product": plan.product.model_dump(mode="json"),
        "plan": plan.model_dump(mode="json"),
        "recipe": recipe.model_dump(mode="json"),
    }, ensure_ascii=False, indent=2, default=str))


@app.command("research-to-studio")
def research_to_studio(
    project_id: str = typer.Option(..., "--project-id"),
    pod: Path = typer.Option(..., "--approved-pod", exists=True, readable=True),
    evidence: Path = typer.Option(..., "--verified-evidence", exists=True, readable=True),
    owner_event: Path = typer.Option(..., "--owner-event", exists=True, readable=True),
    trusted_owner_key: Path = typer.Option(..., "--trusted-owner-key", exists=True, readable=True),
) -> None:
    """Create one signed original-pilot-only work order in the canonical project."""
    import re
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{1,99}", project_id):
        raise typer.BadParameter("Project ID must be a safe local identifier.")
    from cinefactory.studio.research_studio_handoff_v205 import create_studio_work_order
    destination = (
        ROOT / "data" / "projects" / project_id / "inputs"
        / "approved_studio_work_order.json"
    )
    result = create_studio_work_order(
        pod, evidence, owner_event, trusted_owner_key, destination,
        expected_project_id=project_id,
    )
    typer.echo(json.dumps({
        "state": result["state"], "project_id": result["project_id"],
        "niche": result["niche"], "scope": result["scope"],
        "work_order_path": str(destination), "auto_published": False,
    }, indent=2, ensure_ascii=False))


@app.command("channel-init")
def channel_init(
    brand_id: str = typer.Option(..., "--brand-id"),
    working_name: str = typer.Option("Lantern Vale Stories", "--working-name"),
) -> None:
    """Create a DRAFT original Minecraft channel and 3 long-term series."""
    from cinefactory.studio.channel_franchise_v206 import (
        ChannelLibrary, minecraft_original_starter, evaluate_evergreen_slate,
    )
    bible = minecraft_original_starter(brand_id, working_name)
    library = ChannelLibrary(ROOT)
    path = library.register_draft(bible)
    typer.echo(json.dumps({
        "state": "DRAFT_REQUIRES_OWNER_IP_AND_BRAND_REVIEW",
        "source": str(path),
        "channel_brand_id": bible.channel_brand_id,
        "series": [s.series_id for s in bible.series],
        "episodes": evaluate_evergreen_slate(bible)["episodes_planned"],
        "created_youtube_channel": False,
        "production_or_upload_authorized": False,
    }, ensure_ascii=False, indent=2))


@app.command("channel-slate")
def channel_slate(
    brand_id: str = typer.Option(..., "--brand-id"),
    weeks: int = typer.Option(12, "--weeks", min=1, max=52),
) -> None:
    """Preview a sustainable editorial slate (never schedules uploads)."""
    from cinefactory.studio.channel_franchise_v206 import ChannelLibrary, draft_editorial_slate
    bible, _ = ChannelLibrary(ROOT).load(brand_id)
    typer.echo(json.dumps(draft_editorial_slate(bible, weeks), ensure_ascii=False, indent=2))


@app.command("channel-episode")
def channel_episode(
    brand_id: str = typer.Option(..., "--brand-id"),
    series_id: str = typer.Option(..., "--series-id"),
    episode_id: str = typer.Option(..., "--episode-id"),
) -> None:
    """Preview a source-hash-locked original episode before company-plan."""
    from cinefactory.studio.channel_franchise_v206 import ChannelLibrary
    episode = ChannelLibrary(ROOT).resolve_episode(brand_id,series_id,episode_id)
    typer.echo(episode.model_dump_json(indent=2))


@app.command("channel-observe")
def channel_observe(
    brand_id: str = typer.Option(..., "--brand-id"),
    series_id: str = typer.Option(..., "--series-id"),
    episode_id: str = typer.Option(..., "--episode-id"),
    verified_private_receipt: Path = typer.Option(
        ..., "--verified-private-receipt", exists=True, readable=True,
    ),
    owner_analytics_oauth_file: Path = typer.Option(
        ..., "--owner-analytics-oauth-file", exists=True, readable=True,
    ),
) -> None:
    """Read real authorized owner metrics; never auto-promote channel rules."""
    from cinefactory.studio.channel_franchise_v206 import ChannelLibrary
    from cinefactory.studio.youtube_oauth_transport_v205 import GoogleYouTubeOwnedAnalyticsTransport
    from cinefactory.studio.channel_growth_v206 import ChannelOwnedGrowthLedger
    bible, _ = ChannelLibrary(ROOT).load(brand_id)
    if not bible.verified_youtube_channel_id:
        raise typer.BadParameter(
            "Channel bible has no independently verified owned YouTube channel ID."
        )
    provider = GoogleYouTubeOwnedAnalyticsTransport(
        owner_analytics_oauth_file,
        verified_channel_id=bible.verified_youtube_channel_id,
    )
    receipt = json.loads(verified_private_receipt.read_text(encoding="utf8"))
    result = ChannelOwnedGrowthLedger(ROOT).record_verified_episode(
        brand_id=brand_id,series_id=series_id,episode_id=episode_id,
        release_receipt=receipt,transport=provider,
    )
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command("minecraft-format-map")
def minecraft_format_map() -> None:
    """Show technical Minecraft subniches without claiming a viral winner."""
    from cinefactory.studio.minecraft_subniche_v207 import CATALOG
    typer.echo(json.dumps({
        "market": "minecraft",
        "ranked_winner_automatically": False,
        "formats": [
            entry.model_dump(mode="json")
            for entry in CATALOG.values()
        ],
    }, ensure_ascii=False, indent=2))


@app.command("minecraft-research-candidates")
def minecraft_research_candidates(
    records_file: Path = typer.Option(
        ..., "--records-file", exists=True, readable=True,
    ),
) -> None:
    """Filter source-declared observations, pending actual source authentication."""
    from cinefactory.studio.minecraft_subniche_v207 import rank_subniche_research
    raw = json.loads(records_file.read_text(encoding="utf8"))
    if not isinstance(raw, list):
        raise typer.BadParameter("Supply a list of independently documented candidate records.")
    typer.echo(json.dumps(
        rank_subniche_research(raw),ensure_ascii=False,indent=2,
    ))


@app.command("channel-forensics")
def channel_forensics(
    channel_url: str = typer.Option(...,"--channel-url"),
    snapshot_json: Path | None = typer.Option(
        None,"--snapshot-json",exists=True,readable=True,
        help="Offline user-supplied public catalogue; does NOT independently prove external facts.",
    ),
    search_peers: bool = typer.Option(False,"--search-peers"),
    max_videos: int = typer.Option(10,"--max-videos",min=2,max=16),
    discover_public_repos: bool = typer.Option(
        True,"--discover-public-repos/--no-discover-public-repos",
        help="Auto-search public GitHub/Hugging Face on live channel research. Offline supplied snapshots never make network calls.",
    ),
    output_file: Path | None = typer.Option(None,"--output-file"),
) -> None:
    """Channel URL -> per-video niche taxonomy -> same-format query/peer plan.

    Uses the existing public yt-dlp scanner, no paid API credits. Competitor
    searches are optional and bounded. Never certifies unwatched media.
    """
    from datetime import datetime,timezone
    from hashlib import sha256
    from cinefactory.studio.channel_forensics_v208 import ChannelSample
    from cinefactory.research_intelligence.channel_forensics_runner_v208 import (
        run_forensics,store_dossier,
    )
    snapshot=(
        ChannelSample.model_validate_json(snapshot_json.read_text(encoding="utf8"))
        if snapshot_json else None
    )
    report=run_forensics(
        channel_url,sample=snapshot,search=search_peers,max_videos=max_videos,
    )
    if output_file is None:
        cid=report["classification"]["source_channel_id"] or "unknown_channel"
        timestamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        output_file=(
            ROOT/"data"/"research"/"channel_forensics"/cid
            /(timestamp+"_"+sha256(channel_url.encode()).hexdigest()[:8]+".json")
        )
    # Existing 96-v210 recommendations are always included in the dossier.
    # Optional public GitHub scan adds only immutable PENDING receipts.
    from cinefactory.studio.technology_discovery_v211 import (
        run_technology_discovery,
    )
    tech_scan=[]
    if discover_public_repos and snapshot_json is None:
        for fmt,tech in list(
            report["technology_advisory"]["by_metadata_format_candidate"].items()
        )[:2]:
            tech_scan.append(run_technology_discovery(
                ROOT,minor_niche=fmt,major_niche=report["classification"]["market_major_niche"],
                discover_public=True,max_queries=1,
            ))
    report["technology_public_discovery"]=tech_scan
    stored=store_dossier(report,output_file)
    typer.echo(json.dumps({
        "state":report["classification"]["status"],
        "source_channel_id":report["classification"]["source_channel_id"],
        "major_niche":report["classification"]["market_major_niche"],
        "dominant_minor_niche":report["classification"]["dominant_minor_niche"],
        "video_sample_size":report["classification"]["sample_size"],
        "peer_status":report["competitor_discovery"]["status"],
        "technology_formats_considered":list(
            report["technology_advisory"]["by_metadata_format_candidate"]
        ),
        "new_technology_pending_receipts":sum(
            len(x["pending_queue"]["pending_additions"])+
            len(x["model_pending_queue"]["pending_additions"])
            for x in report["technology_public_discovery"]
        ),
        "technology_search_errors":sum(
            len(x["source_errors"]) for x in report["technology_public_discovery"]
        ),
        "research_dossier_path":str(stored),
        "video_visual_analysis_performed":False,
        "competitors_verified":False,
        "production_approved":False,
    },ensure_ascii=False,indent=2))


@app.command("technology-watch")
def technology_watch(
    public_sources: bool = typer.Option(
        False,"--public-sources",help="Read 4 fixed public Claude/MCP/AI/SaaS sources; no paid API."),
    source_id: list[str] = typer.Option([],"--source-id"),
) -> None:
    """Survey public source versions; never install, execute or choose a backend."""
    from cinefactory.studio.technology_watch_v212 import (
        watch_public_sources, latest_watch_status,
    )
    if public_sources:
        report=watch_public_sources(
            ROOT,source_ids=source_id or None,max_sources=6 if source_id else 4,
        )
    else:
        if source_id:
            raise typer.BadParameter("Source IDs require --public-sources.")
        report=latest_watch_status(ROOT)
    typer.echo(json.dumps(report,ensure_ascii=False,indent=2))


@app.command("technology-match")
def technology_match(
    minor_niche: str = typer.Option(...,"--minor-niche"),
    major_niche: str | None = typer.Option(None,"--major-niche"),
    scene_intent: str | None = typer.Option(None,"--scene-intent"),
    department: str | None = typer.Option(None,"--department"),
) -> None:
    """Read-only format, scene and company department technology matching."""
    from cinefactory.studio.technology_council_v212 import counsel_for_all_departments
    report=counsel_for_all_departments(
        minor_niche,major_niche,scene_intent=scene_intent,
    )
    if department:
        if department not in report["all_departments"]:
            raise typer.BadParameter("Unknown company department.")
        report["all_departments"]={
            department:report["all_departments"][department],
        }
    typer.echo(json.dumps(report,ensure_ascii=False,indent=2))


@app.command("technology-backlog")
def technology_backlog(
    limit: int = typer.Option(60, "--limit", min=1, max=300),
) -> None:
    """Read-only newly discovered R&D queue, verify source evidence hashes."""
    from cinefactory.studio.technology_discovery_v211 import (
        inspect_pending_technologies,
    )
    typer.echo(json.dumps(
        inspect_pending_technologies(ROOT,limit=limit),
        ensure_ascii=False,indent=2,
    ))


@app.command("technology-discover")
def technology_discover(
    minor_niche: str = typer.Option(..., "--minor-niche"),
    major_niche: str | None = typer.Option(None, "--major-niche"),
    public_sources: bool = typer.Option(
        False, "--public-sources",
        help="Query one public GitHub and Hugging Face search; zero paid APIs.",
    ),
) -> None:
    """Original-format R&D candidates; never clone, install or qualify models."""
    from cinefactory.studio.technology_discovery_v211 import (
        run_technology_discovery,
    )
    report=run_technology_discovery(
        ROOT,minor_niche=minor_niche,major_niche=major_niche,
        discover_public=public_sources,max_queries=1,
    )
    typer.echo(json.dumps(report,ensure_ascii=False,indent=2))


@app.command("niche-technology-plan")
def niche_technology_plan(
    minor_niche: str = typer.Option(..., "--minor-niche"),
    major_niche: str | None = typer.Option(None, "--major-niche"),
    conference: Path | None = typer.Option(None, "--conference"),
    bakeoff: Path | None = typer.Option(None, "--bakeoff"),
) -> None:
    """Cross-company 96-tool niche research plan; no unreviewed execution."""
    from cinefactory.studio.niche_technology_strategy_v213 import (
        prepare_niche_technology_strategy,
    )
    report = prepare_niche_technology_strategy(
        minor_niche,
        major_niche=major_niche,
        conference_file=conference,
        bakeoff_file=bakeoff,
        company_root=ROOT,
    )
    typer.echo(json.dumps(report, ensure_ascii=False, indent=2))


@app.command("technology-knowledge")
def technology_knowledge(
    query: str = typer.Option("", "--query"),
    minor_niche: str | None = typer.Option(None, "--minor-niche"),
    department: str | None = typer.Option(None, "--department"),
    kind: str | None = typer.Option(None, "--kind"),
    limit: int = typer.Option(15, "--limit", min=1, max=100),
) -> None:
    """Search complete 18-section studio library; advisory only, no installation."""
    from cinefactory.studio.technology_knowledge_v215 import query_company_knowledge
    result = query_company_knowledge(
        query=query, minor_niche=minor_niche,
        department=department, kind=kind, limit=limit,
    )
    typer.echo(json.dumps(result, ensure_ascii=True, indent=2))


@app.command("technology-knowledge-summary")
def technology_knowledge_summary(
    minor_niche: str = typer.Option(..., "--minor-niche"),
    top_k: int = typer.Option(5, "--top-k", min=1, max=20),
) -> None:
    """Read-only access map for all 26 company departments."""
    from cinefactory.studio.technology_knowledge_v215 import (
        department_knowledge_index, load_company_knowledge,
    )
    kb = load_company_knowledge()
    report = department_knowledge_index(minor_niche, top_k=top_k)
    report["base_registry_count"] = kb["baseline_count"]
    report["user_study_rows"] = kb["user_source_row_count"]
    report["research_v214_count"] = kb["research_v214_count"]
    report["reference_workflows"] = kb["workflow_count"]
    typer.echo(json.dumps(report, ensure_ascii=True, indent=2))


@app.command("agentic-technology-review")
def agentic_technology_review(
    minor_niche: str = typer.Option(..., "--minor-niche"),
    department: str | None = typer.Option(None, "--department"),
    limit: int = typer.Option(10, "--limit", min=1, max=25),
) -> None:
    """Safe October 2026 Claude/MCP/model research, no backend execution."""
    from cinefactory.studio.agentic_research_v216 import advise_agentic_tools
    report=advise_agentic_tools(minor_niche,department=department,limit=limit)
    typer.echo(json.dumps(report,ensure_ascii=True,indent=2))


@app.command("creator-tool-research")
def creator_tool_research(
    minor_niche: str = typer.Option(...,"--minor-niche"),
    department: str | None = typer.Option(None,"--department"),
    limit: int = typer.Option(12,"--limit",min=1,max=50),
) -> None:
    """Evidence-reviewed creative SaaS/MCP/Claude candidates, with zero spend."""
    from cinefactory.studio.creator_technology_v217 import suggest_creator_technologies
    data=suggest_creator_technologies(minor_niche,department=department,limit=limit)
    typer.echo(json.dumps(data,ensure_ascii=True,indent=2))


@app.command("ai-connector-status")
def ai_connector_status(
    probe_local: bool = typer.Option(False, "--probe-local"),
    node_query: str = typer.Option("Checkpoint", "--node-query"),
) -> None:
    """Actual local AI/MCP readiness plus reviewed vendor enablement gates."""
    from cinefactory.studio.local_ai_connector_v219 import (
        claude_external_connector_plan, comfyui_local_status,
        comfyui_local_capabilities, comfyui_local_queue,
    )
    report=claude_external_connector_plan()
    if probe_local:
        report["local_comfyui"] = comfyui_local_status()
        report["matching_nodes"] = comfyui_local_capabilities(node_query,limit=12)
        report["local_queue"] = comfyui_local_queue()
    typer.echo(json.dumps(report,ensure_ascii=True,indent=2))


@app.command("creative-mcp-landscape")
def creative_mcp_landscape(
    minor_niche: str = typer.Option(...,"--minor-niche"),
    department: str | None = typer.Option(None,"--department"),
    limit: int = typer.Option(15,"--limit",min=1,max=27),
) -> None:
    """Official and community creative MCP options; R&D-only with no paid calls."""
    from cinefactory.studio.creative_mcp_landscape_v220 import plan_creative_mcp_for_niche
    result=plan_creative_mcp_for_niche(minor_niche,department=department,limit=limit)
    typer.echo(json.dumps(result,ensure_ascii=True,indent=2))


@app.command("company-connectors")
def company_connectors(
    minor_niche: str = typer.Option("minecraft_story_adventure","--minor-niche"),
    department: str | None = typer.Option(None,"--department"),
    limit: int = typer.Option(12,"--limit",min=1,max=27),
    inventory: bool = typer.Option(False,"--inventory"),
    probe_local: bool = typer.Option(False,"--probe-local"),
) -> None:
    """All 27 creative/MCPs integrated into department/shot plans; fail closed."""
    from cinefactory.studio.company_connector_registry_v221 import (
        company_connector_inventory, company_scene_connector_plan,
    )
    result=(company_connector_inventory(local_probe=probe_local)
            if inventory else
            company_scene_connector_plan(minor_niche,department=department,
                                         limit=limit,local_probe=probe_local))
    typer.echo(json.dumps(result,ensure_ascii=True,indent=2))


@app.command("minecraft-production-research")
def minecraft_production_research(
    storyboard: bool = typer.Option(False,"--storyboard"),
) -> None:
    """Verified local Minecraft pilot and pending original animation R&D."""
    from cinefactory.studio.minecraft_production_research_v222 import (
        minecraft_research_conference, original_minecraft_pilot_storyboard,
    )
    report=(original_minecraft_pilot_storyboard() if storyboard
            else minecraft_research_conference())
    typer.echo(json.dumps(report,ensure_ascii=True,indent=2))


@app.command("minecraft-company-roadmap")
def minecraft_company_roadmap_command(
    lane: str | None = typer.Option(None,"--lane"),
    phase: str | None = typer.Option(None,"--phase"),
    blockers_only: bool = typer.Option(False,"--blockers-only"),
) -> None:
    """Original Maizen-style / BigSchool-style complete studio 28-step roadmap."""
    from cinefactory.studio.minecraft_company_roadmap_v223 import (
        minecraft_company_roadmap, minecraft_next_approved_step,
    )
    if blockers_only:
        if lane is None:
            raise typer.BadParameter("--blockers-only requires --lane")
        result=minecraft_next_approved_step(lane)
    else:
        result=minecraft_company_roadmap(lane=lane,phase=phase)
    typer.echo(json.dumps(result,ensure_ascii=True,indent=2))


@app.command("minecraft-source-evidence")
def minecraft_source_evidence(
    video_id: str | None = typer.Option(None, "--video-id"),
) -> None:
    """G01 direct YouTube page metadata and G02 sparse public preview evidence."""
    from cinefactory.studio.minecraft_source_evidence_v224 import (
        minecraft_g01_g02_evidence,
    )
    report=minecraft_g01_g02_evidence(video_id=video_id)
    typer.echo(json.dumps(report,ensure_ascii=True,indent=2))


@app.command("maizen-studio")
def maizen_studio(
    department: str | None = typer.Option(None,"--department"),
    start: bool = typer.Option(False,"--start"),
    output_dir: Path | None = typer.Option(None,"--output-dir",
        help="New isolated versioned desk-receipt folder; never overwrites previous handoffs."),
) -> None:
    """Operate Maizen Studio A: 26 actual desk-work handoffs, no gameplay or paid jobs."""
    from cinefactory.studio.maizen_studio_kickoff_v225 import (
        maizen_department_work, maizen_studio_status,
        materialize_maizen_desk_receipts,
    )
    if department is not None and start:
        raise typer.BadParameter("Use either --start or --department, not both")
    if output_dir is not None and not start:
        raise typer.BadParameter("--output-dir requires --start")
    if output_dir is not None:
        repo_root=context().root.resolve()
        destination=output_dir.resolve()
        if not destination.is_relative_to(repo_root/"data"/"verification"):
            raise typer.BadParameter("--output-dir must stay inside data/verification")
    if department is not None:
        result=maizen_department_work(department)
    elif start:
        result=materialize_maizen_desk_receipts(output_dir=output_dir)
    else:
        result=maizen_studio_status()
    typer.echo(json.dumps(result,ensure_ascii=False,indent=2))


@app.command("maizen-runtime")
def maizen_runtime() -> None:
    """Probe installed Java/Minecraft/OBS/FFmpeg without launching anything."""
    from cinefactory.studio.maizen_runtime_preflight_v225 import maizen_runtime_readiness
    typer.echo(json.dumps(maizen_runtime_readiness(), ensure_ascii=False,indent=2))


@app.command("maizen-method-audit")
def maizen_method_audit(
    shot_id: str | None = typer.Option(None,"--shot-id"),
) -> None:
    """v226: verify staged Minecraft vs authored CGI instead of forcing raw gameplay."""
    from cinefactory.studio.maizen_method_review_v226 import (
        maizen_production_method_audit, maizen_shot_method_options,
    )
    result=(maizen_shot_method_options(shot_id) if shot_id is not None
            else maizen_production_method_audit())
    typer.echo(json.dumps(result,ensure_ascii=False,indent=2))


@app.command("maizen-full-video-review")
def maizen_full_video_review(
    video_id: str | None = typer.Option(None,"--video-id"),
    prepare_templates: bool = typer.Option(False,"--prepare-templates"),
    verify_local_media: bool = typer.Option(False,"--verify-local-media"),
) -> None:
    """Strict Maizen full visual/audio gate, with optional local full decoding."""
    from cinefactory.studio.maizen_full_video_gate_v227 import (
        draft_full_review_template, maizen_full_video_review_gate,
        prepare_full_watch_templates,
    )
    if sum(bool(x) for x in (video_id,prepare_templates,verify_local_media))>1 and (
        prepare_templates or (verify_local_media and video_id is None)
    ):
        raise typer.BadParameter("Use --prepare-templates alone or --verify-local-media with --video-id")
    if prepare_templates:
        result=prepare_full_watch_templates()
    elif verify_local_media:
        if video_id is None:
            raise typer.BadParameter("--verify-local-media requires --video-id")
        from cinefactory.studio.maizen_media_decode_v227 import verify_reference_media
        result=verify_reference_media(video_id)
    elif video_id is not None:
        result=draft_full_review_template(video_id)
    else:
        result=maizen_full_video_review_gate()
    typer.echo(json.dumps(result,ensure_ascii=False,indent=2))


@app.command("maizen-research-stage")
def maizen_research_stage(
    stage_id: str = typer.Option(..., "--stage-id"),
    enforce: bool = typer.Option(False,"--enforce"),
) -> None:
    """Hard fail if a Maizen downstream stage tries to skip full movie+audio review."""
    from cinefactory.studio.maizen_full_video_gate_v227 import (
        maizen_research_stage_gate,
        require_maizen_full_video_review_for_stage,
    )
    if enforce:
        require_maizen_full_video_review_for_stage(stage_id)
    result=maizen_research_stage_gate(stage_id)
    typer.echo(json.dumps(result,ensure_ascii=False,indent=2))


@app.command("competitor-full-review")
def competitor_full_review(
    niche: str = typer.Option(...,"--niche"),
    video_ids: list[str] | None = typer.Option(None,"--video-id"),
    department: str | None = typer.Option(None,"--department"),
) -> None:
    """Universal full competitor A/V research evidence gate (all niche families)."""
    from cinefactory.studio.universal_competitor_review_v228 import (
        competitor_full_review_gate, competitor_study_department_gate,
    )
    result=(competitor_study_department_gate(niche,department,video_ids)
            if department else competitor_full_review_gate(niche,video_ids))
    typer.echo(json.dumps(result,ensure_ascii=False,indent=2))


@app.command("film-expert-adoption")
def film_expert_adoption(
    department: str | None = typer.Option(None,"--department"),
) -> None:
    """Audit user's cinema expert playbook vs validated CineFactory production."""
    from cinefactory.studio.film_expert_adoption_v229 import film_expert_adoption_audit
    typer.echo(json.dumps(film_expert_adoption_audit(department),ensure_ascii=True,indent=2))


@app.command("maizen-vidiq-evidence")
def maizen_vidiq_evidence() -> None:
    """Read provider 28:04 walkthrough; keep G02 full original media gate blocked."""
    from cinefactory.studio.maizen_vidiq_provider_v230 import maizen_vidiq_provider_evidence
    typer.echo(json.dumps(maizen_vidiq_provider_evidence(),ensure_ascii=True,indent=2))


@app.command("maizen-browser-source")
def maizen_browser_source() -> None:
    """v237: direct original Chrome playback and honest independent QC limitations."""
    from cinefactory.studio.maizen_browser_source_review_v237 import maizen_browser_source_study
    typer.echo(json.dumps(maizen_browser_source_study(),ensure_ascii=True,indent=2))


@app.command("maizen-company-next")
def maizen_company_next(
    materialize: bool = typer.Option(False,"--materialize"),
) -> None:
    """v243: write auditable original MAI01 preproduction handoffs, never render or bypass G02."""
    from cinefactory.studio.maizen_company_next_v243 import (
        maizen_next_company_stage,materialize_original_preproduction,
    )
    result=maizen_next_company_stage()
    if materialize:
        result["materialization"]=materialize_original_preproduction()
    typer.echo(json.dumps(result,ensure_ascii=True,indent=2))


@app.command("maizen-three-source-study")
def maizen_three_source_study() -> None:
    """v248: original browser picture and audio research, no G02 override."""
    from cinefactory.studio.maizen_three_source_study_v248 import maizen_three_source_video_study
    typer.echo(json.dumps(maizen_three_source_video_study(),ensure_ascii=True,indent=2))


@app.command("maizen-independent-av")
def maizen_independent_av() -> None:
    """v251: second-source mechanical AV QC; never human native G02 approval."""
    from cinefactory.studio.maizen_second_pass_av_v251 import maizen_second_pass_av_evidence
    typer.echo(json.dumps(maizen_second_pass_av_evidence(),ensure_ascii=True,indent=2))


@app.command("technology-radar")
def technology_radar(
    category: str | None = typer.Option(None, "--category"),
    priority: str | None = typer.Option(None, "--priority"),
    show_items: bool = typer.Option(False, "--show-items"),
) -> None:
    """Read-only media technology inventory, licensing and local-readiness flags."""
    from cinefactory.studio.technology_radar_v210 import (
        load_technology_radar, summarize_technology_radar,
    )
    report = summarize_technology_radar(
        load_technology_radar(),
        category=category, priority=priority, include_items=show_items,
    )
    typer.echo(json.dumps(report, ensure_ascii=False, indent=2))


@app.command("company-readiness")
def company_readiness(
    output_file: Path | None = typer.Option(None,"--output-file"),
) -> None:
    """Read-only operational health; never self-certifies cinematic quality."""
    from cinefactory.studio.operational_readiness_v209 import audit_company_readiness
    report=audit_company_readiness(ROOT)
    if output_file is not None:
        target=output_file.resolve()
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    typer.echo(json.dumps(report,ensure_ascii=False,indent=2))


@app.command("company-plan")
def company_plan(
    prompt: str = typer.Option(..., "--prompt"),
    language: str = typer.Option("vi", "--language"),
    niche: str | None = typer.Option(None, "--niche", help="Explicit approved niche id."),
    domain: str = typer.Option("generic", "--domain"),
    channel_brand_id: str | None = typer.Option(None, "--channel-brand-id"),
    series_id: str | None = typer.Option(None, "--series-id"),
    episode_id: str | None = typer.Option(None, "--episode-id"),
    duration: int | None = typer.Option(None, "--duration"),
    project_id: str | None = typer.Option(None, "--project-id"),
    minecraft_subniche: str | None = typer.Option(None, "--minecraft-subniche"),
    reuse_series_characters: bool = typer.Option(False, "--reuse-series-characters"),
    script_file: Path | None = typer.Option(
        None,
        "--script-file",
        exists=True,
        readable=True,
    ),
    outline_file: Path | None = typer.Option(
        None,
        "--outline-file",
        exists=True,
        readable=True,
    ),
    reference_script_file: list[Path] = typer.Option(
        [],
        "--reference-script-file",
        exists=True,
        readable=True,
    ),
) -> None:
    import re
    if project_id and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{1,99}", project_id):
        raise typer.BadParameter("Project ID must be a safe canonical local identifier.")
    ctx = context()
    project = StudioProjectSpec(
        prompt=prompt,
        language=language,
        niche=niche,
        domain=domain,
        channel_brand_id=channel_brand_id,
        series_id=series_id,
        episode_id=episode_id,
        minecraft_subniche=minecraft_subniche,
        reuse_series_characters=reuse_series_characters,
        studio_project_id=project_id or f"STU_{uuid4().hex[:12]}",
        duration_seconds=duration,
        planning_inputs=_planning_inputs_from_cli(
            script_file=script_file,
            outline_file=outline_file,
            reference_script_file=reference_script_file,
        ),
    )
    blueprint = CompanyOrchestrator(ctx.studio).build_blueprint(
        project, professional_governance=True
    )
    typer.echo(blueprint.model_dump_json(indent=2))


def _require_required_company_handlers(
    blueprint: CompanyBlueprint, handlers,
) -> None:
    """Never start a strict project whose required stage has no executable handler.

    Optional EVIDENCE and unconfigured optional voice remain legitimate;
    mandatory voice must be either configured or explicitly rejected.
    """
    if not blueprint.strict_stage_receipts:
        return
    missing = sorted(s.stage_id for s in blueprint.stages
                     if s.required and handlers.get(s.stage_id) is None)
    if missing:
        typer.echo(json.dumps({
            "state": "BLOCKED_REQUIRED_HANDLER",
            "project_id": blueprint.project.studio_project_id,
            "missing_handlers": missing,
            "resolution": ("Configure approved TTS or voice source when VOICE_PREP "
                           "is mandatory; otherwise fix the responsible executor."),
            "production_permission": False,
        }, ensure_ascii=False, indent=2))
        raise typer.Exit(code=2)


def _require_valid_company_wiring(blueprint: CompanyBlueprint) -> None:
    """Fail before scheduling a production DAG with missing departments."""
    from cinefactory.studio.contract_integrity import audit_company_wiring

    result = audit_company_wiring(blueprint.stages)
    if result.valid:
        return
    typer.echo(json.dumps({
        "state": "BLOCKED_STAGE_CONTRACT",
        "project_id": blueprint.project.studio_project_id,
        "issues": [problem.model_dump(mode="json") for problem in result.issues],
    }, ensure_ascii=False, indent=2))
    raise typer.Exit(code=2)


@app.command("company-run")
def company_run(
    prompt: str = typer.Option(
        "Continue the saved company project",
        "--prompt",
    ),
    language: str = typer.Option("vi", "--language"),
    niche: str | None = typer.Option(None, "--niche"),
    domain: str = typer.Option("generic", "--domain"),
    channel_brand_id: str | None = typer.Option(None, "--channel-brand-id"),
    series_id: str | None = typer.Option(None, "--series-id"),
    episode_id: str | None = typer.Option(None, "--episode-id"),
    duration: int | None = typer.Option(None, "--duration"),
    project_id: str | None = typer.Option(
        None,
        "--project-id",
        help="Stable project id. Required with --resume.",
    ),
    import_maizen_research: bool = typer.Option(
        False, "--import-maizen-research",
        help="Bind cached Maizen sources to this new Minecraft project, without self-approving G02.",
    ),
    script_file: Path | None = typer.Option(
        None,
        "--script-file",
        exists=True,
        readable=True,
    ),
    outline_file: Path | None = typer.Option(
        None,
        "--outline-file",
        exists=True,
        readable=True,
    ),
    reference_script_file: list[Path] = typer.Option(
        [],
        "--reference-script-file",
        exists=True,
        readable=True,
    ),
    production_mode: str = typer.Option(
        "slate",
        "--production-mode",
    ),
    tts_mode: str = typer.Option("none", "--tts-mode"),
    tts_command: str | None = typer.Option(
        None,
        "--tts-command",
    ),
    voice: str | None = typer.Option(None, "--voice"),
    turbo_dispatch: bool = typer.Option(
        False,
        "--turbo-dispatch/--inline-dispatch",
    ),
    render_width: int = typer.Option(
        1280,
        "--render-width",
        min=64,
    ),
    render_height: int = typer.Option(
        720,
        "--render-height",
        min=64,
    ),
    max_cycles: int = typer.Option(
        60,
        "--max-cycles",
        min=1,
        max=500,
    ),
    resume: bool = typer.Option(
        False,
        "--resume/--new-run",
    ),
    minecraft_subniche: str | None = typer.Option(None, "--minecraft-subniche"),
    reuse_series_characters: bool = typer.Option(False, "--reuse-series-characters"),
    allow_private_upload: bool = typer.Option(False, "--allow-private-upload"),
    owner_youtube_oauth_file: Path | None = typer.Option(
        None, "--owner-youtube-oauth-file", exists=True, readable=True,
    ),
    owner_youtube_analytics_oauth_file: Path | None = typer.Option(
        None, "--owner-youtube-analytics-oauth-file", exists=True, readable=True,
    ),
    owner_channel_id: str | None = typer.Option(None, "--owner-channel-id"),
) -> None:
    import re
    if project_id and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{1,99}", project_id):
        raise typer.BadParameter("Project ID must be a safe canonical local identifier.")
    ctx = context()
    if allow_private_upload and (owner_youtube_oauth_file is None or not owner_channel_id):
        raise typer.BadParameter(
            "Private upload requires explicit --owner-youtube-oauth-file "
            "and --owner-channel-id and a signed per-video approval."
        )
    if owner_youtube_oauth_file is not None and not allow_private_upload:
        raise typer.BadParameter("OAuth upload token provided without --allow-private-upload.")
    if owner_youtube_analytics_oauth_file is not None and not owner_channel_id:
        raise typer.BadParameter("Analytics OAuth requires --owner-channel-id.")
    if resume and not project_id:
        raise typer.BadParameter(
            "--resume requires --project-id"
        )
    if resume and import_maizen_research:
        raise typer.BadParameter(
            "Saved research handoff is immutable for resume; omit --import-maizen-research."
        )
    if import_maizen_research and (not project_id or niche != "minecraft"):
        raise typer.BadParameter("--import-maizen-research requires a stable --project-id and --niche minecraft.")

    inputs = _planning_inputs_from_cli(
        script_file=script_file,
        outline_file=outline_file,
        reference_script_file=reference_script_file,
    )
    if resume and inputs:
        raise typer.BadParameter(
            "Do not supply script inputs with --resume; the saved sanitized blueprint is authoritative."
        )
    if resume and (
        niche is not None or domain != "generic"
        or any((channel_brand_id, series_id, episode_id))
        or minecraft_subniche is not None or reuse_series_characters
    ):
        raise typer.BadParameter(
            "Resume uses the saved niche/domain/channel/series/episode. Do not override it."
        )

    if project_id:
        project_root = (
            ctx.root / "data" / "projects" / project_id
        )
    else:
        project_root = None

    if resume:
        assert project_root is not None
        blueprint_path = (
            project_root / "company" / "blueprint.json"
        )
        if not blueprint_path.is_file():
            raise typer.BadParameter(
                f"saved company blueprint not found: {blueprint_path}"
            )
        blueprint = CompanyBlueprint.model_validate_json(
            blueprint_path.read_text(encoding="utf-8")
        )
        _require_valid_company_wiring(blueprint)
        handlers = FilmCompanyHandlers(
            ctx,
            config=FilmHandlerConfig(
                production_mode=production_mode,
                tts_mode=tts_mode,
                tts_command=tts_command,
                voice=voice,
                turbo_dispatch=turbo_dispatch,
                render_width=render_width,
                render_height=render_height,
                require_human_final_approval=True,
                enable_research_handoff=(
                    (ctx.root / "data" / "projects" / blueprint.project.studio_project_id
                     / "company" / "research_handoff.json").is_file()
                ),
            ),
        ).registry(niche=(
            blueprint.project.niche
            if blueprint.stages and blueprint.stages[0].stage_id == "NICHE_PROJECT_INTAKE"
            else None
        ), production_route=blueprint.minecraft_route)
        _require_required_company_handlers(blueprint, handlers)
        runner = AutonomousCompanyRunner.resume(
            blueprint,
            handlers,
            store=ctx.studio.execution_ledgers,
            kernel=ctx,
            project_root=project_root,
        )
    else:
        project_kwargs = {
            "prompt": prompt,
            "language": language,
            "niche": niche,
            "domain": domain,
            "channel_brand_id": channel_brand_id,
            "series_id": series_id,
            "episode_id": episode_id,
            "minecraft_subniche": minecraft_subniche,
            "reuse_series_characters": reuse_series_characters,
            "duration_seconds": duration,
            "planning_inputs": inputs,
        }
        if project_id:
            project_kwargs["studio_project_id"] = project_id
        project = StudioProjectSpec(**project_kwargs)
        blueprint = CompanyOrchestrator(
            ctx.studio
        ).build_blueprint(project, professional_governance=True)
        if import_maizen_research:
            from cinefactory.studio.research_evidence_bridge_v266 import build
            build(ctx.root, project.studio_project_id, write=True)
            blueprint = blueprint.model_copy(update={
                "stages": [
                    stage.model_copy(update={"required": True})
                    if stage.stage_id == "EVIDENCE" else stage
                    for stage in blueprint.stages
                ]
            })
        project_root = (
            ctx.root
            / "data"
            / "projects"
            / blueprint.project.studio_project_id
        )
        company_dir = project_root / "company"
        company_dir.mkdir(parents=True, exist_ok=True)
        blueprint_path = company_dir / "blueprint.json"
        blueprint_path.write_text(
            blueprint.model_dump_json(indent=2),
            encoding="utf-8",
        )
        _require_valid_company_wiring(blueprint)
        handlers = FilmCompanyHandlers(
            ctx,
            config=FilmHandlerConfig(
                production_mode=production_mode,
                tts_mode=tts_mode,
                tts_command=tts_command,
                voice=voice,
                turbo_dispatch=turbo_dispatch,
                render_width=render_width,
                render_height=render_height,
                require_human_final_approval=True,
                enable_research_handoff=(
                    (ctx.root / "data" / "projects" / blueprint.project.studio_project_id
                     / "company" / "research_handoff.json").is_file()
                ),
            ),
        ).registry(niche=(
            blueprint.project.niche
            if blueprint.stages and blueprint.stages[0].stage_id == "NICHE_PROJECT_INTAKE"
            else None
        ), production_route=blueprint.minecraft_route)
        _require_required_company_handlers(blueprint, handlers)
        runner = AutonomousCompanyRunner(
            blueprint,
            handlers,
            store=ctx.studio.execution_ledgers,
            kernel=ctx,
            project_root=project_root,
        )

    if allow_private_upload or owner_youtube_analytics_oauth_file is not None:
        if not (
            blueprint.stages
            and blueprint.stages[0].stage_id == "NICHE_PROJECT_INTAKE"
        ):
            raise typer.BadParameter(
                "v205 owned YouTube transport is only qualified for "
                "native-media specialist projects."
            )
        from cinefactory.studio.youtube_oauth_transport_v205 import (
            GoogleYouTubePrivateTransport,
            GoogleYouTubeOwnedAnalyticsTransport,
        )
        if allow_private_upload:
            live = GoogleYouTubePrivateTransport(owner_youtube_oauth_file)
            if live.owned_channel_id != owner_channel_id:
                raise typer.BadParameter(
                    "Authenticated YouTube channel differs from --owner-channel-id."
                )
            ctx.youtube_oauth_transport = live
        if owner_youtube_analytics_oauth_file is not None:
            ctx.youtube_analytics_transport = GoogleYouTubeOwnedAnalyticsTransport(
                owner_youtube_analytics_oauth_file,
                verified_channel_id=owner_channel_id,
            )

    report = runner.run_until_blocked_or_complete(
        max_cycles=max_cycles
    )
    typer.echo(
        json.dumps(
            {
                "project_id": report.project_id,
                "complete": report.complete,
                "cycles": report.cycles,
                "errors": report.errors,
                "repair_tickets": [
                    item.model_dump(mode="json")
                    for item in report.repair_tickets
                ],
                "ledger": report.ledger.model_dump(mode="json"),
                "blueprint_path": str(
                    project_root / "company" / "blueprint.json"
                ),
            },
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )
    raise typer.Exit(code=0 if report.complete else 2)


@app.command("script-inspect")
def script_inspect(
    script_file: Path | None = typer.Option(
        None,
        "--script-file",
        exists=True,
        readable=True,
    ),
    outline_file: Path | None = typer.Option(
        None,
        "--outline-file",
        exists=True,
        readable=True,
    ),
    reference_script_file: list[Path] = typer.Option(
        [],
        "--reference-script-file",
        exists=True,
        readable=True,
    ),
) -> None:
    ctx = context()
    inputs = _planning_inputs_from_cli(
        script_file=script_file,
        outline_file=outline_file,
        reference_script_file=reference_script_file,
    )
    if not inputs:
        raise typer.BadParameter(
            "Provide --script-file, --outline-file, or --reference-script-file."
        )
    pack = ScriptInputCompiler(ctx.root).compile(inputs)
    typer.echo(pack.model_dump_json(indent=2))


@app.command("tool-doctor")
def tool_doctor(
    tool: list[str] = typer.Option(
        ["blender", "ffmpeg", "premiere", "aftereffects", "photoshop", "resolve", "unreal", "canva"],
        "--tool",
    ),
) -> None:
    ctx = context()
    result = [ctx.studio.tool_doctor.inspect(name).model_dump(mode="json") for name in tool]
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command("tool-skills")
def tool_skills(tool: str | None = typer.Option(None, "--tool")) -> None:
    ctx = context()
    result = [item.model_dump(mode="json") for item in ctx.studio.tool_skills.list(tool)]
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command("tool-mastery")
def tool_mastery(
    run: bool = typer.Option(
        False,
        "--run/--report-only",
        help="Run available local execution evaluators before reporting.",
    ),
) -> None:
    ctx = context()
    runner = ExecutionMasteryRunner(ctx.studio)
    if run:
        runner.evaluate_installed()
    knowledge = audit_tool_mastery(ctx.studio)
    execution = {
        report.tool_id: report.model_dump(mode="json")
        for report in ctx.studio.execution_mastery.list()
    }
    typer.echo(
        json.dumps(
            {
                "knowledge_mastery": knowledge.model_dump(mode="json"),
                "execution_mastery": execution,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@app.command("tool-validate")
def tool_validate(
    tool: list[str] = typer.Option(
        ["blender", "ffmpeg"],
        "--tool",
        help="Tool(s) with implemented deterministic local mastery evaluator.",
    ),
) -> None:
    ctx = context()
    runner = ExecutionMasteryRunner(ctx.studio)
    reports = [runner.evaluate(name).model_dump(mode="json") for name in tool]
    typer.echo(json.dumps(reports, ensure_ascii=False, indent=2))


@app.command("tool-adapters")
def tool_adapters() -> None:
    ctx = context()
    result = []
    for item in ctx.studio.tool_adapters.list():
        probe = ctx.studio.tool_adapters.probe(ctx.studio, item.tool_id)
        result.append(
            {
                "spec": item.model_dump(mode="json"),
                "probe": probe.model_dump(mode="json"),
            }
        )
    typer.echo(json.dumps(result, ensure_ascii=False, indent=2))


@app.command("tool-attest")
def tool_attest(
    tool: str = typer.Option(..., "--tool"),
    kind: AttestationKind = typer.Option(..., "--kind"),
    reviewer: str = typer.Option(..., "--reviewer"),
    rationale: str = typer.Option(..., "--rationale"),
    approve: bool = typer.Option(
        False,
        "--approve/--reject",
    ),
    evidence: list[str] = typer.Option([], "--evidence"),
    tool_version: str | None = typer.Option(None, "--tool-version"),
) -> None:
    ctx = context()
    now_id = f"ATT_{tool}_{kind.value}_{len(ctx.studio.production_qualification.attestations(tool)) + 1:04d}"
    attestation = QualificationAttestation(
        attestation_id=now_id,
        tool_id=tool,
        kind=kind,
        approved=approve,
        reviewer=reviewer,
        rationale=rationale,
        evidence_refs=evidence,
        tool_version=tool_version,
    )
    ctx.studio.production_qualification.add_attestation(attestation)
    typer.echo(attestation.model_dump_json(indent=2))


@app.command("tool-qualification")
def tool_qualification(
    tool: list[str] = typer.Option(
        ["blender", "ffmpeg"],
        "--tool",
    ),
    promote: bool = typer.Option(
        False,
        "--promote/--report-only",
        help="Promote only tools that pass all fail-closed qualification checks.",
    ),
) -> None:
    ctx = context()
    board = ProductionQualificationBoard(ctx.studio)
    decisions = []
    for name in tool:
        decision = (
            board.promote_if_qualified(name)
            if promote
            else board.evaluate(name)
        )
        decisions.append(decision.model_dump(mode="json"))
    typer.echo(json.dumps(decisions, ensure_ascii=False, indent=2))


@app.command("doctor")
def doctor() -> None:
    report = Doctor(context()).run()
    typer.echo(json.dumps(report, ensure_ascii=False, indent=2))


@app.command("run")
def run_autopilot(
    prompt: str = typer.Option(..., "--prompt"),
    profile: str = typer.Option("cinematic_story", "--profile"),
    language: str = typer.Option("vi", "--language"),
    duration: int | None = typer.Option(None, "--duration"),
    reasoning_mode: str = typer.Option("scaffold", "--reasoning-mode"),
    reasoning_command: str | None = typer.Option(None, "--reasoning-command"),
    production_mode: str = typer.Option("slate", "--production-mode"),
    workflow_id: str | None = typer.Option(None, "--workflow-id"),
    workflow_version: str = typer.Option("1", "--workflow-version"),
    asset_workflow_id: str | None = typer.Option(None, "--asset-workflow-id"),
    asset_workflow_version: str = typer.Option("1", "--asset-workflow-version"),
    keyframe_workflow_id: str | None = typer.Option(None, "--keyframe-workflow-id"),
    keyframe_workflow_version: str = typer.Option("1", "--keyframe-workflow-version"),
    video_workflow_id: str | None = typer.Option(None, "--video-workflow-id"),
    video_workflow_version: str = typer.Option("1", "--video-workflow-version"),
    video_fast_workflow_id: str | None = typer.Option(None, "--video-fast-workflow-id"),
    video_fast_workflow_version: str = typer.Option("1", "--video-fast-workflow-version"),
    video_standard_workflow_id: str | None = typer.Option(None, "--video-standard-workflow-id"),
    video_standard_workflow_version: str = typer.Option("1", "--video-standard-workflow-version"),
    video_master_workflow_id: str | None = typer.Option(None, "--video-master-workflow-id"),
    video_master_workflow_version: str = typer.Option("1", "--video-master-workflow-version"),
    asset_candidates: int = typer.Option(2, "--asset-candidates", min=1, max=6),
    keyframe_candidates: int = typer.Option(2, "--keyframe-candidates", min=1, max=6),
    pilot_count: int = typer.Option(2, "--pilot-count", min=1, max=6),
    visual_qc_command: str | None = typer.Option(None, "--visual-qc-command"),
    require_visual_qc: bool = typer.Option(True, "--require-visual-qc/--allow-no-visual-qc"),
    turbo_dispatch: bool = typer.Option(False, "--turbo-dispatch/--inline-dispatch"),
    turbo_timeout_seconds: int = typer.Option(1800, "--turbo-timeout-seconds", min=30, max=21600),
    min_visual_score: float = typer.Option(0.72, "--min-visual-score", min=0.0, max=1.0),
    early_accept_score: float = typer.Option(0.88, "--early-accept-score", min=0.0, max=1.0),
    max_repair_rounds: int = typer.Option(2, "--max-repair-rounds", min=0, max=5),
    openchatcut_command: str | None = typer.Option(None, "--openchatcut-command"),
    upscale_command: str | None = typer.Option(None, "--upscale-command"),
    render_width: int = typer.Option(1280, "--render-width"),
    render_height: int = typer.Option(720, "--render-height"),
    tts_mode: str = typer.Option("none", "--tts-mode"),
    tts_command: str | None = typer.Option(None, "--tts-command"),
    voice: str | None = typer.Option(None, "--voice"),
    master_4k: bool = typer.Option(True, "--master-4k/--no-master-4k"),
    originality_strict: bool = typer.Option(True, "--originality-strict/--no-originality-strict"),
    originality_retries: int = typer.Option(2, "--originality-retries", min=0, max=5),
    include_prior_projects: bool = typer.Option(True, "--include-prior-projects/--no-prior-projects"),
    workflow_family: str | None = typer.Option(None, "--workflow-family"),
    world_target: str | None = typer.Option(None, "--world"),
    backend: str | None = typer.Option(None, "--backend"),
) -> None:
    ctx = context()
    result = AutopilotRunner(ctx).run(AutopilotRequest(
        prompt=prompt, profile=profile, language=language, duration_seconds=duration,
        reasoning_mode=reasoning_mode, reasoning_command=reasoning_command,
        production_mode=production_mode, workflow_id=workflow_id, workflow_version=workflow_version,
        asset_workflow_id=asset_workflow_id, asset_workflow_version=asset_workflow_version,
        keyframe_workflow_id=keyframe_workflow_id, keyframe_workflow_version=keyframe_workflow_version,
        video_workflow_id=video_workflow_id, video_workflow_version=video_workflow_version,
        video_fast_workflow_id=video_fast_workflow_id, video_fast_workflow_version=video_fast_workflow_version,
        video_standard_workflow_id=video_standard_workflow_id, video_standard_workflow_version=video_standard_workflow_version,
        video_master_workflow_id=video_master_workflow_id, video_master_workflow_version=video_master_workflow_version,
        asset_candidates=asset_candidates, keyframe_candidates=keyframe_candidates, pilot_count=pilot_count,
        visual_qc_command=visual_qc_command, require_visual_qc=require_visual_qc, turbo_dispatch=turbo_dispatch, turbo_timeout_seconds=turbo_timeout_seconds, min_visual_score=min_visual_score,
        early_accept_score=early_accept_score, max_repair_rounds=max_repair_rounds,
        openchatcut_command=openchatcut_command, upscale_command=upscale_command,
        render_width=render_width, render_height=render_height, tts_mode=tts_mode, tts_command=tts_command, voice=voice, master_4k=master_4k,
        originality_strict=originality_strict, originality_retries=originality_retries, include_prior_projects=include_prior_projects,
        workflow_family=workflow_family, world_target=world_target, backend=backend,
    ))
    typer.echo(result.model_dump_json(indent=2))
    raise typer.Exit(code=0 if result.success else 2)


@app.command("reference-doctor")
def reference_doctor() -> None:
    typer.echo(
        ReferenceIntelligenceEngine.health().model_dump_json(
            indent=2
        )
    )


@app.command("reference-analyze")
def reference_analyze(
    source: str = typer.Option(..., "--source", "--url"),
    max_duration: int = typer.Option(
        2400,
        "--max-duration",
        min=30,
    ),
    max_height: int = typer.Option(
        720,
        "--max-height",
        min=144,
        max=2160,
    ),
    retain_media: bool = typer.Option(
        False,
        "--retain-media/--discard-media",
    ),
) -> None:
    ctx = context()
    engine = ReferenceIntelligenceEngine(
        ctx.root,
        policy=ReferenceAcquisitionPolicy(
            max_duration_seconds=max_duration,
            max_height=max_height,
            retain_downloaded_media=retain_media,
        ),
    )
    report = engine.video(source)
    typer.echo(
        json.dumps(
            {
                "video_id": report.source.video_id,
                "planning_profile": report.planning_profile(),
                "findings": report.findings,
                "quarantine_dir": report.quarantine_dir,
                "transcript_available": report.transcript.available,
                "media_sha256": report.media_sha256,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@app.command("channel-analyze")
def channel_analyze(
    url: str = typer.Option(..., "--url"),
    niche: str = typer.Option("generic", "--niche"),
    max_videos: int = typer.Option(
        5,
        "--max-videos",
        min=1,
        max=20,
    ),
    max_duration: int = typer.Option(
        2400,
        "--max-duration",
        min=30,
    ),
    max_height: int = typer.Option(
        720,
        "--max-height",
        min=144,
        max=2160,
    ),
) -> None:
    ctx = context()
    decomposer = ReferenceVideoDecomposer(
        ctx.root,
        policy=ReferenceAcquisitionPolicy(
            max_duration_seconds=max_duration,
            max_height=max_height,
            max_channel_videos=max_videos,
        ),
    )
    report = decomposer.analyze_channel(
        url,
        niche=niche,
        limit=max_videos,
    )
    typer.echo(
        json.dumps(
            {
                "sample_count": len(report.profiles),
                "planning_profile": report.planning_profile(),
                "patterns": [
                    item.model_dump(mode="json")
                    for item in report.patterns
                ],
                "playbook": report.playbook.model_dump(mode="json"),
                "findings": report.findings,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


@app.command("reference-add")
def reference_add(
    file: Path = typer.Option(..., "--file", exists=True, readable=True),
    kind: ReferenceKind = typer.Option(ReferenceKind.COMPETITOR, "--kind"),
    title: str | None = typer.Option(None, "--title"),
    source_url: str | None = typer.Option(None, "--url"),
    idea_summary: str | None = typer.Option(None, "--idea-summary"),
    hook_summary: str | None = typer.Option(None, "--hook-summary"),
    structure_beat: list[str] = typer.Option([], "--structure-beat"),
    collision_tag: list[str] = typer.Option([], "--collision-tag"),
    fingerprint_file: Path | None = typer.Option(None, "--fingerprint-file", exists=True, readable=True),
) -> None:
    ctx=context()
    fingerprint = ConceptFingerprint.model_validate_json(fingerprint_file.read_text(encoding="utf-8")) if fingerprint_file else None
    record=ctx.references.import_text(
        file, kind=kind, title=title, source_url=source_url, idea_summary=idea_summary,
        hook_summary=hook_summary, structure_beats=structure_beat, concept_fingerprint=fingerprint,
        collision_tags=collision_tag,
    )
    typer.echo(record.model_dump_json(indent=2))


@app.command("references")
def list_references() -> None:
    typer.echo(json.dumps([r.safe_metadata() for r in context().references.list()], ensure_ascii=False, indent=2))


@app.command("originality-audit")
def originality_audit(project_id: str) -> None:
    ctx=context()
    refs=ctx.references.list()+prior_project_references(ctx.root/"data"/"projects", exclude_project_id=project_id)
    guard=OriginalityGuard()
    out={}
    try:
        story,_=ctx.creative.store.get_latest(project_id, CreativeStage.STORY, StorySpec)
        expression=guard.check_story(story,refs)
        from cinefactory.originality import fingerprint_from_project
        fp=fingerprint_from_project(story)
        auth=guard.authenticity_report(expression_report=expression,fingerprint=fp,references=refs)
        out["story"]=expression.model_dump(mode="json")
        out["authenticity"]=auth.model_dump(mode="json")
    except KeyError:
        out["story"]={"status":"MISSING"}
    try:
        script,_=ctx.creative.store.get_latest(project_id, CreativeStage.SCRIPT, ScriptSpec)
        out["script"]=guard.check_script(script,refs).model_dump(mode="json")
    except KeyError:
        out["script"]={"status":"MISSING"}
    typer.echo(json.dumps(out,ensure_ascii=False,indent=2))


@app.command("turbo-status")
def turbo_status() -> None:
    typer.echo(json.dumps(context().turbo_store.status(), ensure_ascii=False, indent=2, default=str))


@app.command("turbo-enqueue")
def turbo_enqueue(
    file: Path = typer.Option(..., "--file", exists=True, readable=True),
) -> None:
    ctx=context(); item=WorkItem.model_validate_json(file.read_text(encoding="utf-8")); out,created=ctx.turbo_store.enqueue_work(item)
    typer.echo(json.dumps({"created":created,"work":out.model_dump(mode="json")},ensure_ascii=False,indent=2,default=str))


@app.command("turbo-job")
def turbo_job(
    job_id: str,
    priority: int = typer.Option(50, "--priority", min=0, max=100),
    model_affinity: str | None = typer.Option(None, "--model-affinity"),
) -> None:
    ctx=context(); job=ctx.jobs.get(job_id)
    item=WorkItem(project_id=job.project_id,kind=job.job_type,handler="job.execute",resource=ResourceClass.GPU,priority=priority,model_affinity=model_affinity or f"{job.workflow_id}@{job.workflow_version}",payload={"job_id":job_id})
    out,created=ctx.turbo_store.enqueue_work(item); typer.echo(json.dumps({"created":created,"work":out.model_dump(mode="json")},indent=2,default=str))


@app.command("factory-daemon")
def factory_daemon(
    worker_id: str = typer.Option("gpu-0", "--worker-id"),
    resources: str = typer.Option("GPU,CPU,IO", "--resources"),
    capabilities: str = typer.Option("job.execute,comfy.execute,timeline.accept,blender.previs,blender.animation.render,block.episode.assemble,noop", "--capabilities"),
    active_model: str | None = typer.Option(None, "--active-model"),
    poll_seconds: float = typer.Option(0.25, "--poll-seconds", min=0.05, max=10.0),
    once: bool = typer.Option(False, "--once"),
) -> None:
    ctx=context(); rs={ResourceClass(x.strip().upper()) for x in resources.split(',') if x.strip()}; caps={x.strip() for x in capabilities.split(',') if x.strip()}
    worker=WorkerSpec(worker_id=worker_id,resources=rs,capabilities=caps,active_model_affinity=active_model)
    daemon=FactoryDaemon(ctx,worker,poll_seconds=poll_seconds)
    if once:
        worked=daemon.tick(); typer.echo(json.dumps({"worked":worked,"status":ctx.turbo_store.status()},indent=2,default=str)); return
    typer.echo(f"CineFactory daemon {worker_id} started. Ctrl+C to stop.")
    daemon.run_forever()


@app.command("block-compile")
def block_compile(file: Path=typer.Option(...,"--file",exists=True,readable=True), output_dir: Path=typer.Option(...,"--output-dir")) -> None:
    ctx=context(); ep=EpisodeSpec.model_validate_json(file.read_text(encoding="utf-8")); asm=EpisodeAssembler.from_root(ctx.root); c=asm.compile(ep,output_dir=output_dir); target=Path(output_dir)/f"{ep.episode_id}.compiled.json"; asm.write_compiled(c,target); typer.echo(json.dumps({"compiled":str(target.resolve()),"shots":len(c.shots),"qc":c.qc.model_dump(mode="json"),"library_fingerprint":c.library_fingerprint},indent=2,default=str))

@app.command("block-enqueue")
def block_enqueue(file: Path=typer.Option(...,"--file",exists=True,readable=True), output_dir: Path=typer.Option(...,"--output-dir")) -> None:
    ctx=context(); ep=EpisodeSpec.model_validate_json(file.read_text(encoding="utf-8")); asm=EpisodeAssembler.from_root(ctx.root); c=asm.compile(ep,output_dir=output_dir); asm.write_compiled(c,Path(output_dir)/f"{ep.episode_id}.compiled.json"); typer.echo(asm.enqueue(c,ctx.turbo_store,output_dir=output_dir).model_dump_json(indent=2))

@app.command("block-factory")
def block_factory(poll_seconds:float=typer.Option(.05,"--poll-seconds",min=.02,max=2.0), once:bool=typer.Option(False,"--once")) -> None:
    f=ContinuousBlockFactory(context(),poll_seconds=poll_seconds)
    if once:
        try:typer.echo(json.dumps(f.tick(),indent=2))
        finally:f.gpu.daemon.close(); f.io.daemon.close()
        return
    typer.echo("CineFactory Block Animation Factory started. Ctrl+C to stop."); f.run_forever()


@app.command("logic-check")
def logic_check(file: Path = typer.Option(..., "--file", exists=True, readable=True), auto_fill_missing: bool = typer.Option(True, "--auto-fill/--no-auto-fill")) -> None:
    raw=json.loads(file.read_text(encoding="utf-8")); shots=[ShotSpec.model_validate(x) for x in raw]
    result=PreRenderLogicGate().validate(shots,auto_fill_missing=auto_fill_missing)
    typer.echo(json.dumps({"passed":result.passed,"repaired_fields":result.repaired_fields,"findings":result.findings,"shots":[x.model_dump(mode="json") for x in result.shots]},ensure_ascii=False,indent=2,default=str))
    if not result.passed: raise typer.Exit(code=2)


if __name__ == "__main__":
    app()
