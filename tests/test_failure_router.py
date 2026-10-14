from cinefactory.domain.enums import FailureCode
from cinefactory.production.failure_router import FailureRouter


def test_failure_router_routes_identity_to_asset_engine():
    r=FailureRouter().classify('S01_SH01',['FACE_IDENTITY_DRIFT'])
    assert r.failure_code is FailureCode.IDENTITY_DRIFT
    assert r.owner=='ASSET_ENGINE'
    assert r.retryable


def test_failure_router_does_not_rerender_story_failures():
    r=FailureRouter().classify('S01_SH01',['STORY_BEAT_FAIL'])
    assert r.owner=='DIRECTOR_ENGINE'
    assert not r.retryable
    assert 'SHOT_SPEC' in r.invalidates


def test_failure_router_multi_owner_returns_distinct_repairs():
    router = FailureRouter()
    directives = router.classify_all(
        "S01_SH02",
        [
            "CAMERA_GEOMETRY_WARNING:TARGET_NEAR_SAFE_EDGE",
            "PERFORMANCE_QC_BLOCKER:C01:GAZE_ACCURACY",
        ],
    )
    owners = {item.owner for item in directives}
    assert "CINEMATOGRAPHY_ENGINE" in owners
    assert "PERFORMANCE_ENGINE" in owners


def test_failure_router_suppresses_asset_repair_when_appearance_drift_is_explained_by_lookdev():
    router = FailureRouter()
    directives = router.classify_all(
        "S01_SH02",
        [
            "RENDERED_IDENTITY_DRIFT:C01:score=0.40",
            "CUT_APPEARANCE_DRIFT:luma=0.35:rgb=0.42",
        ],
    )
    owners = {item.owner for item in directives}
    assert "LIGHTING_COLOR_ENGINE" in owners
    assert "ASSET_ENGINE" not in owners


def test_failure_router_keeps_asset_repair_for_structural_identity_failure():
    router = FailureRouter()
    directives = router.classify_all(
        "S01_SH02",
        [
            "IDENTITY_STRUCTURE_BLOCKER:C01:RIG_STYLE_MISMATCH",
            "RENDERED_IDENTITY_DRIFT:C01:score=0.40",
            "CUT_APPEARANCE_DRIFT:luma=0.35:rgb=0.42",
        ],
    )
    owners = {item.owner for item in directives}
    assert "ASSET_ENGINE" in owners
    assert "LIGHTING_COLOR_ENGINE" in owners
