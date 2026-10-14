"""Evidence citations for manual image-quality review."""

import hashlib
import json
from pathlib import Path

from .core import _write_json
from .local_vision_adapter import _evidence


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quality_review_packet(model_review, output):
    source=Path(model_review).resolve(strict=True)
    model=json.loads(source.read_text(encoding="utf-8"))
    if model.get("schema")!="cine.research.local_vision_review.v1":
        raise ValueError("Expected a model review")
    base=Path(model["source_path"]).resolve(strict=True)
    if _sha(base)!=model["source_sha256"]:
        raise ValueError("Vision source changed")
    facts=_evidence(base, max_images=4)
    ids={x["id"]:x for x in facts["images"]}
    for claim in model.get("findings", []):
        observed=ids.get(claim.get("evidence_id"))
        if (not observed or observed["hash"]!=claim.get("image_sha256")
            or observed["second"]!=claim.get("second")
            or claim.get("status")!="MODEL_HYPOTHESIS_PENDING_QA"):
            raise ValueError("Model claim lacks a matching original image")
    if (model.get("production_permission") is not False
        or model.get("human_quality_reviewed") is not False
        or model.get("canonical_issue_id")!=facts["issue_id"]):
        raise ValueError("Unapproved model result cannot be promoted")
    record={
        "schema":"cine.research.vision_quality_packet.v1",
        "state":"INDEPENDENT_IMAGE_REVIEW_PENDING",
        "model_path":str(source),"model_sha256":_sha(source),
        "source_sha256":_sha(base),"canonical_issue_id":facts["issue_id"],
        "items":[{"evidence_id":x["evidence_id"],
                  "model_hypothesis":x["claim"],"image_sha256":x["image_sha256"],
                  "second":x["second"],"quality_status":"NOT_INSPECTED"}
                 for x in model.get("findings",[])],
        "checks":[
            "Inspect exact original image and check every visible assertion",
            "Challenge whether model mistook a thumbnail for complete video",
            "Leave unobserved plot, motion, retention, licensing and audio unknown",
        ],
        "independent_evaluation_completed":False,
        "production_permission":False,
    }
    _write_json(Path(output),record)
    return record
