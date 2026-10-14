from __future__ import annotations

import pytest
from pydantic import ValidationError

from cinefactory.studio.authority import AuthorityMatrix, DecisionDomain
from cinefactory.studio.corporate import CompanyFunctionId, CompanyFunctionRegistry
from cinefactory.studio.handoffs import HandoffContract, HandoffRegistry, HandoffState
from cinefactory.studio.hierarchy import (
    ContentNode,
    ContentNodeKind,
    CreativeIntentHierarchy,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.maturity import (
    CompanyMaturityAudit,
    DepartmentMaturity,
    MaturityLevel,
)
from cinefactory.studio.niche_os import NicheRegistry
from cinefactory.studio.review_board import (
    DailiesReviewBoard,
    ReviewNote,
    ReviewSeverity,
)
from cinefactory.studio.seo import EvidenceKind, NicheSEOBrain, SearchObservation


def test_company_functions_are_complete():
    registry = CompanyFunctionRegistry()
    assert registry.validate() == []
    ids = {item.function_id for item in registry.list()}
    assert CompanyFunctionId.FINANCE_INVESTMENT in ids
    assert CompanyFunctionId.YOUTUBE_GROWTH_SEO in ids
    assert CompanyFunctionId.BUSINESS_AFFAIRS_LEGAL in ids


def test_seven_core_niches_have_independent_ontologies():
    niches = NicheRegistry()
    assert len(niches.active()) == 7
    assert niches.get("minecraft").content_unit_ontology == [
        "sequence", "scene", "beat", "shot"
    ]
    assert niches.get("long_slices_game").content_unit_ontology[0] == "run"
    assert niches.get("asmr_sleep_hands_objects").content_unit_ontology[1] == "trigger_block"
    assert niches.get("rain_sleep_white_noise").content_unit_ontology[-1] == "loop_variation_block"


def test_competitor_private_metrics_cannot_be_public_facts():
    with pytest.raises(ValidationError):
        SearchObservation(
            query="minecraft story",
            intent="entertainment",
            evidence_kind=EvidenceKind.PUBLIC_FACT,
            metadata={"ctr": 0.12},
        )


def test_niche_seo_brain_detects_new_channel_breakout():
    brain = NicheSEOBrain(niche_id="minecraft")
    brain.add_observation(
        "minecraft_story",
        SearchObservation(
            query="minecraft story",
            intent="entertainment",
            channel_id="C1",
            channel_age_days=10,
            views=1_200_000,
            observed_views_per_day=120_000,
        ),
    )
    results = brain.new_channel_breakouts(max_channel_age_days=30, min_views=1_000_000)
    assert [item.channel_id for item in results] == ["C1"]


def test_authority_matrix_has_single_camera_owner():
    matrix = AuthorityMatrix()
    assert matrix.validate() == []
    assert matrix.can_decide(DecisionDomain.CAMERA, "CINEMATOGRAPHY")
    assert not matrix.can_decide(DecisionDomain.CAMERA, "ANIMATION")


def test_handoff_is_structured_and_versioned():
    registry = HandoffRegistry()
    item = registry.create(
        HandoffContract(
            project_id="P1",
            source_department="DIRECTION",
            destination_department="CINEMATOGRAPHY",
            object_versions={"SC_01": 3},
            intent={"purpose": "reveal threat"},
            dependencies=["SCRIPT:v5"],
            acceptance_criteria=["camera plan preserves reveal timing"],
        )
    )
    assert item.state is HandoffState.OPEN
    registry.accept(item.handoff_id)
    assert registry.get(item.handoff_id).state is HandoffState.ACCEPTED


def test_high_severity_dailies_review_must_be_independent():
    with pytest.raises(ValidationError):
        ReviewNote(
            project_id="P1",
            object_id="SH_01",
            reviewer_department="ANIMATION",
            reviewer_id="animator_2",
            owner_department="ANIMATION",
            problem="foot slide",
            evidence="frames 42-55",
            impact="breaks weight and contact",
            acceptance_criteria="foot remains locked during planted phase",
            severity=ReviewSeverity.HIGH,
        )

    board = DailiesReviewBoard()
    note = board.add(
        ReviewNote(
            project_id="P1",
            object_id="SH_01",
            reviewer_department="DIRECTION",
            reviewer_id="director",
            owner_department="ANIMATION",
            problem="fear does not read",
            evidence="brows and gaze remain neutral in frames 60-72",
            impact="reveal loses emotional payoff",
            acceptance_criteria="fear reads in silent playback",
            severity=ReviewSeverity.HIGH,
        )
    )
    assert board.blockers("P1") == [note]
    board.resolve(note.note_id, "v4 approved in silent playback")
    assert board.blockers("P1") == []


def test_creative_intent_requires_explicit_override():
    hierarchy = CreativeIntentHierarchy()
    hierarchy.add(
        ContentNode(
            node_id="P",
            kind=ContentNodeKind.PROJECT,
            title="Project",
            intent={"mood": "cold", "theme": "trust"},
        )
    )
    hierarchy.add(
        ContentNode(
            node_id="SQ",
            kind=ContentNodeKind.SEQUENCE,
            title="Sequence",
            parent_id="P",
        )
    )
    hierarchy.add(
        ContentNode(
            node_id="SC",
            kind=ContentNodeKind.SCENE,
            title="Scene",
            parent_id="SQ",
            intent={"mood": "warm"},
        )
    )
    assert hierarchy.effective_intent("SC")["mood"] == "cold"
    hierarchy.get("SC").override_fields.add("mood")
    assert hierarchy.effective_intent("SC")["mood"] == "warm"


def test_maturity_cannot_claim_benchmark_leading_without_evidence():
    audit = CompanyMaturityAudit()
    item = audit.assess(
        DepartmentMaturity(
            department_id="DIRECTION",
            documented=True,
            contracts_defined=True,
            tests_passed=True,
            production_evidence=True,
        )
    )
    assert item.level is MaturityLevel.PRODUCTION_READY
    assert not audit.benchmark_leading_claim_allowed(["DIRECTION"])

    item.benchmark_evidence.append("competitor_pairwise_test:PASS")
    audit.assess(item)
    assert audit.benchmark_leading_claim_allowed(["DIRECTION"])


def test_kernel_exposes_professional_company_layer(tmp_path):
    kernel = build_studio_kernel(tmp_path)
    company = kernel.professional_company
    assert len(company.niches.active()) == 7
    assert company.company_functions.validate() == []
    assert company.authority.validate() == []
    assert company.seo_for("roblox_animation").niche_id == "roblox_animation"


def test_professional_company_exposes_production_economics(tmp_path):
    from cinefactory.studio.production_economics import ProductionShotClass

    kernel = build_studio_kernel(tmp_path)
    company = kernel.professional_company
    hero = company.economics.budget_for(
        type(
            "Shot",
            (),
            {
                "shot_id": "H1",
                "duration_seconds": 2.0,
                "creative_intent": {"production_class": "HERO"},
            },
        )(),
        global_max_repair_rounds=10,
    )
    assert hero.shot_class is ProductionShotClass.HERO
    assert hero.max_local_repairs == 4
