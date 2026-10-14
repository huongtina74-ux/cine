from types import SimpleNamespace
import math
import pytest

from cinefactory.qc.visual_policy import normalized_visual_review


def res(**kw):
    defaults={"passed":True,"identity_score":0.9,"continuity_score":0.9,
              "performance_score":0.9,"camera_score":0.9,"findings":[]}
    return SimpleNamespace(**{**defaults,**kw})


def test_all_four_real_scores_are_required():
    passed,scores,findings=normalized_visual_review(res(camera_score=None))
    assert not passed
    assert scores["camera"]==0
    assert findings[0].startswith("UNSUBSTANTIATED_VISUAL_VERDICT:")


def test_bare_true_is_not_visual_quality():
    obj=SimpleNamespace(passed=True,findings=[])
    passed,scores,findings=normalized_visual_review(obj)
    assert not passed
    assert scores["identity"]==0


@pytest.mark.parametrize("invalid",[-1,1.01,float("nan"),float("inf"),True])
def test_invalid_quality_scores_are_rejected(invalid):
    passed,_,findings=normalized_visual_review(res(performance_score=invalid))
    assert not passed
    assert findings[0].startswith("UNSUBSTANTIATED")


def test_explicit_failure_overrides_good_scores():
    passed,scores,findings=normalized_visual_review(res(passed=False))
    assert not passed
    assert findings[0]=="EXTERNAL_VISUAL_REVIEW_REJECTED"


def test_threshold_applies_to_actual_four_scores():
    passed,scores,findings=normalized_visual_review(res(identity_score=0.4,continuity_score=0.4,
                                                       performance_score=0.4,camera_score=0.4))
    assert not passed
    assert findings[-1]=="VISUAL_SCORE_BELOW_MINIMUM"


def test_valid_four_submetrics_mean_review_advisory_only():
    passed,scores,findings=normalized_visual_review(res())
    assert passed
    assert scores["identity"]==0.9
    # This unit only interprets a declared score, not authenticate model/human identity.
