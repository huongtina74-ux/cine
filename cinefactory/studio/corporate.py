from __future__ import annotations

from enum import StrEnum
from pydantic import BaseModel, Field


class CompanyFunctionId(StrEnum):
    EXECUTIVE_STRATEGY = "EXECUTIVE_STRATEGY"
    FINANCE_INVESTMENT = "FINANCE_INVESTMENT"
    BUSINESS_AFFAIRS_LEGAL = "BUSINESS_AFFAIRS_LEGAL"
    PEOPLE_TALENT_TRAINING = "PEOPLE_TALENT_TRAINING"
    MARKETING_PUBLICITY = "MARKETING_PUBLICITY"
    PROCUREMENT_VENDOR = "PROCUREMENT_VENDOR"
    RISK_INTERNAL_AUDIT = "RISK_INTERNAL_AUDIT"
    YOUTUBE_GROWTH_SEO = "YOUTUBE_GROWTH_SEO"
    DATA_ANALYTICS = "DATA_ANALYTICS"
    TECHNOLOGY_PLATFORM = "TECHNOLOGY_PLATFORM"
    KNOWLEDGE_RND = "KNOWLEDGE_RND"


class CompanyFunctionSpec(BaseModel):
    function_id: CompanyFunctionId
    mission: str
    authority: list[str] = Field(default_factory=list)
    reads: list[str] = Field(default_factory=list)
    writes: list[str] = Field(default_factory=list)
    gates: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)


def _f(function_id: CompanyFunctionId, mission: str, authority: list[str],
       reads: list[str], writes: list[str], gates: list[str], metrics: list[str]) -> CompanyFunctionSpec:
    return CompanyFunctionSpec(
        function_id=function_id,
        mission=mission,
        authority=authority,
        reads=reads,
        writes=writes,
        gates=gates,
        metrics=metrics,
    )


DEFAULT_COMPANY_FUNCTIONS: dict[CompanyFunctionId, CompanyFunctionSpec] = {
    CompanyFunctionId.EXECUTIVE_STRATEGY: _f(
        CompanyFunctionId.EXECUTIVE_STRATEGY,
        "Own company direction, portfolio priorities, capital allocation and enterprise trade-offs.",
        ["portfolio_greenlight", "company_priorities", "capital_allocation"],
        ["market_map", "niche_scores", "finance_forecast", "risk_register"],
        ["company_strategy", "portfolio_decisions", "annual_priorities"],
        ["PORTFOLIO_GREENLIGHT"],
        ["portfolio_value", "risk_adjusted_roi", "capacity_utilization"],
    ),
    CompanyFunctionId.FINANCE_INVESTMENT: _f(
        CompanyFunctionId.FINANCE_INVESTMENT,
        "Own budgets, project economics, cost controls, forecasts and investment evidence.",
        ["budget_policy", "spend_limits", "investment_recommendation"],
        ["cost_ledger", "production_plan", "revenue_observations"],
        ["budget", "forecast", "variance_report", "unit_economics"],
        ["BUDGET_AND_ECONOMICS"],
        ["cost_per_minute", "cost_per_shot", "gpu_hour_cost", "budget_variance"],
    ),
    CompanyFunctionId.BUSINESS_AFFAIRS_LEGAL: _f(
        CompanyFunctionId.BUSINESS_AFFAIRS_LEGAL,
        "Own rights, licensing, contracts, IP, commercial-use clearance and platform-policy risk.",
        ["rights_clearance", "license_policy", "contract_policy"],
        ["asset_registry", "tool_registry", "source_registry", "release_package"],
        ["rights_register", "license_decisions", "legal_blocks"],
        ["RIGHTS_POLICY_CLEARANCE"],
        ["uncleared_assets", "license_exceptions", "policy_blocks"],
    ),
    CompanyFunctionId.PEOPLE_TALENT_TRAINING: _f(
        CompanyFunctionId.PEOPLE_TALENT_TRAINING,
        "Build expert capability, role standards, curricula, staffing and performance development.",
        ["role_standards", "training_requirements", "capability_assessment"],
        ["department_specs", "skill_registry", "failure_library"],
        ["competency_matrix", "training_plans", "capability_gaps"],
        ["ROLE_AND_SKILL_READINESS"],
        ["skill_coverage", "training_completion", "review_quality"],
    ),
    CompanyFunctionId.MARKETING_PUBLICITY: _f(
        CompanyFunctionId.MARKETING_PUBLICITY,
        "Translate approved content into audience-facing channel, brand, release and publicity strategy.",
        ["brand_positioning", "release_messaging"],
        ["project_dna", "release_package", "audience_model"],
        ["campaign_brief", "channel_messaging", "publicity_plan"],
        ["BRAND_AND_RELEASE_ALIGNMENT"],
        ["reach", "brand_consistency", "launch_execution"],
    ),
    CompanyFunctionId.PROCUREMENT_VENDOR: _f(
        CompanyFunctionId.PROCUREMENT_VENDOR,
        "Control vendor, software, hardware and asset procurement with alternatives and lock-in awareness.",
        ["vendor_selection", "procurement_policy"],
        ["capability_gap", "tool_candidates", "budget"],
        ["vendor_decision", "renewal_register", "alternative_suppliers"],
        ["PROCUREMENT_CLEARANCE"],
        ["vendor_risk", "license_cost", "switching_cost"],
    ),
    CompanyFunctionId.RISK_INTERNAL_AUDIT: _f(
        CompanyFunctionId.RISK_INTERNAL_AUDIT,
        "Independently audit controls, traceability, continuity, security and business risks.",
        ["audit_scope", "control_exception"],
        ["decision_log", "rights_register", "cost_ledger", "production_trace"],
        ["audit_findings", "control_actions", "enterprise_risk_register"],
        ["INTERNAL_CONTROL"],
        ["critical_open_findings", "control_coverage", "recovery_readiness"],
    ),
    CompanyFunctionId.YOUTUBE_GROWTH_SEO: _f(
        CompanyFunctionId.YOUTUBE_GROWTH_SEO,
        "Own YouTube search/discovery intelligence, packaging, retention and growth experimentation.",
        ["seo_method", "packaging_experiments", "search_opportunity_scoring"],
        ["competitor_research", "keyword_graph", "audience_model", "performance_metrics"],
        ["seo_brief", "search_gap_map", "packaging_hypotheses", "growth_experiments"],
        ["DISCOVERY_AND_PACKAGING"],
        ["search_traffic", "browse_traffic", "suggested_traffic", "ctr", "retention"],
    ),
    CompanyFunctionId.DATA_ANALYTICS: _f(
        CompanyFunctionId.DATA_ANALYTICS,
        "Own data quality, metric definitions, attribution and decision-grade analytics.",
        ["metric_definitions", "data_quality_policy"],
        ["production_events", "audience_metrics", "costs", "experiments"],
        ["dashboards", "diagnostics", "attribution", "confidence_scoped_findings"],
        ["DATA_QUALITY"],
        ["freshness", "completeness", "lineage_coverage"],
    ),
    CompanyFunctionId.TECHNOLOGY_PLATFORM: _f(
        CompanyFunctionId.TECHNOLOGY_PLATFORM,
        "Own production technology, compute, storage, queues, observability and engineering reliability.",
        ["platform_standards", "production_technology_policy"],
        ["resource_plan", "tool_registry", "incidents"],
        ["platform_services", "capacity_plan", "slo", "recovery_plan"],
        ["PLATFORM_READINESS"],
        ["gpu_utilization", "queue_latency", "failure_rate", "recovery_time"],
    ),
    CompanyFunctionId.KNOWLEDGE_RND: _f(
        CompanyFunctionId.KNOWLEDGE_RND,
        "Convert research, incidents, experiments and external technology into validated company capability.",
        ["knowledge_promotion", "benchmark_policy", "deprecation"],
        ["problem_records", "tool_gaps", "experiments", "external_research"],
        ["validated_rules", "skills", "benchmarks", "deprecation_decisions"],
        ["KNOWLEDGE_PROMOTION"],
        ["validated_rules", "benchmark_coverage", "regression_pass_rate"],
    ),
}


class CompanyFunctionRegistry:
    def __init__(self, items: dict[CompanyFunctionId, CompanyFunctionSpec] | None = None) -> None:
        self._items = dict(items or DEFAULT_COMPANY_FUNCTIONS)

    def get(self, function_id: CompanyFunctionId) -> CompanyFunctionSpec:
        return self._items[function_id]

    def list(self) -> list[CompanyFunctionSpec]:
        return [self._items[k] for k in CompanyFunctionId]

    def validate(self) -> list[str]:
        findings: list[str] = []
        for spec in self.list():
            if not spec.authority:
                findings.append(f"{spec.function_id.value}:AUTHORITY_MISSING")
            if not spec.writes:
                findings.append(f"{spec.function_id.value}:OUTPUTS_MISSING")
            if not spec.gates:
                findings.append(f"{spec.function_id.value}:GATES_MISSING")
        return findings
