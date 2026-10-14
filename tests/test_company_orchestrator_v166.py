from __future__ import annotations

from pathlib import Path

from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.contracts import MediaFormat, StudioProjectSpec
from cinefactory.studio.kernel import build_studio_kernel


def test_company_blueprint_documentary_contains_evidence_stage(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    blueprint = CompanyOrchestrator(kernel).build_blueprint(
        StudioProjectSpec(prompt="Documentary about history", duration_seconds=300)
    )
    assert blueprint.studio_plan.product.format is MediaFormat.DOCUMENTARY
    evidence = next(x for x in blueprint.stages if x.stage_id == "EVIDENCE")
    assert evidence.required is True
    assert "FACT_CLAIMS" in blueprint.quality_profile.gates


def test_company_blueprint_gameplay_contains_runtime_operator_and_authenticity_pack(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    blueprint = CompanyOrchestrator(kernel).build_blueprint(
        StudioProjectSpec(prompt="Minecraft gameplay survival 100 days", duration_seconds=600)
    )
    assert blueprint.studio_plan.product.format is MediaFormat.GAMEPLAY
    assert any(r.role_id == "runtime_operator" for r in blueprint.project_pod.roles)
    assert blueprint.packs.domain_pack is not None
    assert blueprint.packs.domain_pack.pack_id == "domain.gaming"
    assert blueprint.executable is False


def test_company_blueprint_animation_has_direction_and_dop(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    blueprint = CompanyOrchestrator(kernel).build_blueprint(
        StudioProjectSpec(prompt="Create an animated cinematic short", duration_seconds=60)
    )
    stage_ids = {x.stage_id for x in blueprint.stages}
    assert "DIRECTION" in stage_ids
    assert "CINEMATOGRAPHY" in stage_ids
    role_ids = {x.role_id for x in blueprint.project_pod.roles}
    assert "director" in role_ids
    assert "dop" in role_ids
