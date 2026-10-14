"""Operating charter for specialist departments. Specs describe duty, NOT runtime certification."""
from __future__ import annotations
from .contracts import DepartmentId, DepartmentSpec, KnowledgeScope

CHARTERS = {
    "STUDIO_MANAGEMENT": (
        "Own portfolio decisions, budgets, risk authority, greenlights and independent escalation.",
        ["studio governance","slate strategy","resource economics","copyright governance"],
        ["intake triage","portfolio scoring","spend signoff","escalation"],
        ["CompanyOrchestrator","PortfolioGreenlight","CompanyExecutionLedger"],
        ["project_brief","niche_evidence","rights_clearance","production_budget"],
        ["project_intake","portfolio_greenlight","corporate_preflight","owner_release_decision"],
        ["No production on research-only approval","no inferred owner signatures","separate technical and artistic approval"],
        ["PORTFOLIO_AUTHORITY","FINANCE_CHECK","RIGHTS_HOLD","ESCALATION_TRACE"],
    ),
    "ASSETS": (
        "Acquire, license, validate and version persistent models, character rigs, scene and sound assets.",
        ["asset identity","3D rigging","license evidence","packaging","scene reuse"],
        ["canonical asset registration","rig socket tests","asset hashing","provenance QA"],
        ["CharacterRigRegistry","Blender","asset_manifest","license ledger"],
        ["asset_bible","design_bible","licenses","character_ids"],
        ["assets","asset_manifest","canonical_references"],
        ["Do not import unlicensed models","preserve identity and content hashes","reject placeholder as final asset"],
        ["ASSET_INTEGRITY","RIG_COMPATIBILITY","LICENSE_EVIDENCE","STYLE_IDENTITY"],
    ),
    "PRODUCTION": (
        "Execute approved original media shots with repeatable scene safety, continuity and resource tracking.",
        ["shot assembly","GPU scheduling","runtime capture","render economics","scene state"],
        ["render orchestration","retry/recovery","take review","continuity verification"],
        ["Blender","ComfyUI qualified workflows","FFmpeg","Turbo worker"],
        ["production_handoff","production_recipe","assets","keyframes","spend_gate"],
        ["dailies","production_backend","adaptive_production_report"],
        ["Hard gate on portfolio, rights and budget","never promote a diagnostic slate","record real accepted seconds"],
        ["RENDER_VALIDITY","DURATION","CONTINUITY","ART_QC","PROVENANCE"],
    ),
    "GENERATIVE_MEDIA": (
        "Evaluate and use only explicitly permitted local generation models per scene under provenance and cost gates.",
        ["diffusion","video generation","model VRAM","commercial licensing","consistency"],
        ["model qualification","workflow fingerprinting","scene test","quality benchmark"],
        ["ComfyUI","model registry","visual model conference"],
        ["scene_tool_plan","model_hash","license_attestation","workflow_hash"],
        ["generated_shot","model_qualification","generation_cost_report"],
        ["Service availability is not model qualification","no metered cloud fallback","rights and scene QC are mandatory"],
        ["MODEL_HASH","WORKFLOW_HASH","LICENSE_SCOPE","SCENE_QC","VRAM_LIMIT"],
    ),
    "VFX": (
        "Deliver readable and physically coherent compositing/effects aligned with the approved look.",
        ["compositing","particles","physics","keying","depth","temporal consistency"],
        ["VFX breakdown","render-layer assembly","artifact QC","before/after review"],
        ["Blender compositor","FFmpeg","qualified ComfyUI workflow"],
        ["shot_book","render_layers","creative_intent_graph"],
        ["vfx_plan","vfx_comp","vfx_qc"],
        ["No unmotivated effects","do not alter character identity","verify frame continuity"],
        ["VFX_CONTINUITY","EDGE_QUALITY","COLORSPACE","TEMPORAL_ARTIFACTS"],
    ),
    "COLOR": (
        "Own exposure, look continuity, safe color pipeline, delivery mastering and color review.",
        ["color science","exposure","tone mapping","grading","HDR/SDR"],
        ["shot matching","grade QC","technical mastering","delivery verification"],
        ["Blender","FFmpeg","DaVinci Resolve candidate"],
        ["timeline","lighting_color_intent","audio_master"],
        ["color_plan","master_candidate","color_qc"],
        ["Look stays consistent across shots","do not claim native 4K from upscaling","validate color space"],
        ["EXPOSURE","SHOT_MATCH","GAMUT","RESOLUTION","DELIVERY_QC"],
    ),
    "RIGHTS": (
        "Independently verify origin, commercial rights, permissions and license scope for every release asset.",
        ["copyright","originality","license compatibility","privacy","platform policy"],
        ["source verification","license ledger","chain of title","release review"],
        ["license manifest","asset registry","source evidence"],
        ["source_assets","license_attestations","publication_intent"],
        ["rights_clearance","asset_rights_report","release_risk_decision"],
        ["Unknown license blocks commercial release","reference patterns cannot copy expression","owner attestation is separate"],
        ["CHAIN_OF_TITLE","LICENSE_SCOPE","CONSENT","PLATFORM_POLICY"],
    ),
    "PACKAGING": (
        "Package truthful title/thumbnail/audience promise and final delivery metadata after film QC.",
        ["audience positioning","thumbnail storytelling","SEO","brand integrity"],
        ["title ideation","thumbnail QA","metadata QA","promise/payoff audit"],
        ["FFmpeg","creative brief","packaging hypotheses"],
        ["approved_master","qc_report","human_final_gate","project_dna"],
        ["release_package","thumbnail_brief","metadata_manifest"],
        ["Never publish a diagnostic master","no misleading clickbait","owner final approval required"],
        ["PROMISE_ALIGNMENT","THUMBNAIL_RIGHTS","METADATA_INTEGRITY"],
    ),
    "ANALYTICS": (
        "Collect authorized owned-channel metrics, distinguish observations from hypotheses and promote only validated improvements.",
        ["CTR","audience retention","RPM","statistical inference","cohort analysis"],
        ["owned-metric ingestion","window normalization","causal review","experiment tracking"],
        ["YouTube Analytics authorized export","learning store"],
        ["publication_receipt","owned_metrics","experiment_plan"],
        ["observations","hypotheses","learning_candidates","promotion_review"],
        ["No invented private competitor metrics","WAITING_DATA is not learning complete","no auto-promote on one sample"],
        ["CHANNEL_OWNERSHIP","METRIC_PROVENANCE","FRESHNESS","EVIDENCE_THRESHOLD"],
    ),
    "RD_KNOWLEDGE": (
        "Convert documented problems and evaluated experiments into versioned reusable professional skills.",
        ["knowledge engineering","eval science","benchmarking","lineage","root-cause"],
        ["evidence intake","test authoring","controlled rollout","rollback"],
        ["SkillRegistry","KnowledgeRegistry","Git"],
        ["problem_records","trusted_docs","experiment_reports"],
        ["skill_candidates","benchmark_reports","promotion_decisions"],
        ["No autonomous core edits without review","new rules require reproducible eval","all promotions reversible"],
        ["SOURCE_TRUST","EVAL_REPEATABILITY","REGRESSION","ROLLBACK"],
    ),
    "OPERATIONS": (
        "Keep company services, workers, schedules, backups and incident response reliable and auditable.",
        ["worker orchestration","health checks","backup recovery","security","observability"],
        ["lease verification","runbook execution","recovery drill","capacity alerts"],
        ["Task Scheduler","ComfyUI","Blender workers","Git","health monitor"],
        ["system_inventory","worker_heartbeats","scheduled_runs","failure_reports"],
        ["service_health","incident_ticket","recovery_receipt","capacity_plan"],
        ["Historical worker healthy flags are not live heartbeat","never destroy immutable evidence","fail closed on stale service"],
        ["FRESH_HEARTBEAT","BACKUP_RESTORE","SCHEDULER_RESULT","RESOURCE_PRESSURE"],
    ),
}


def specialist_department_specs():
    from .departments import _d
    result = {}
    for name, args in CHARTERS.items():
        role = DepartmentId(name)
        result[role] = _d(role, *args)
    return result


def specialist_operational_readiness(executable_roles: set[DepartmentId],
                                     verified_quality_roles: set[DepartmentId]) -> dict:
    """A written charter alone cannot claim a department has working experts."""
    return {role.value: {
        "charter": "SPECIFIED",
        "executable": role in executable_roles,
        "independent_quality_verified": role in verified_quality_roles,
        "status": ("QUALIFIED" if role in executable_roles and role in verified_quality_roles
                   else "IMPLEMENTED_UNQUALIFIED" if role in executable_roles else "CHARTER_ONLY"),
    } for role in specialist_department_specs()}
