"""Fail-closed interpretation of untrusted visual-review command responses.

A claim that "passed" is true without all four numeric submetrics is NOT
a completed independent assessment. The reviewer identity/truth is still
unverified: output supports a PILOT ONLY, never final cinematic certification.
"""
from __future__ import annotations
import math

METRICS=("identity_score","continuity_score","performance_score","camera_score")


def normalized_visual_review(review, *, min_score:float=0.72):
    values={key:getattr(review,key,None) for key in METRICS}
    invalid=[
        key for key,value in values.items()
        if (not isinstance(value,(int,float)) or isinstance(value,bool)
            or not math.isfinite(value) or value<0 or value>1)
    ]
    if invalid:
        return False,dict.fromkeys(("identity","continuity","performance","camera"),0.0),[
            "UNSUBSTANTIATED_VISUAL_VERDICT:"+",".join(invalid)]
    scores={key.removesuffix("_score"):float(value) for key,value in values.items()}
    overall=sum(scores.values())/len(scores)
    if not review.passed:
        return False,scores,list(review.findings) or ["EXTERNAL_VISUAL_REVIEW_REJECTED"]
    if overall<min_score:
        return False,scores,list(review.findings)+["VISUAL_SCORE_BELOW_MINIMUM"]
    return True,scores,list(review.findings)
