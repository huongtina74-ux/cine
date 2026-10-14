from __future__ import annotations

"""Two independent real Blender renders, measured actor appearance consistency.

Uses the rendered frame-QC actor bounding boxes / labels as trusted scene
annotation, but independently compares image-derived appearance summaries.
Not an unconstrained detector, blind actor re-ID or a multi-seed Wan benchmark.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
from pydantic import BaseModel, Field


class ImageIdentityMatch(BaseModel):
    actor_id: str
    correct_score: float
    nearest_rival_score: float | None = None
    score_margin: float | None = None
    passed: bool
    findings: list[str] = Field(default_factory=list)


class RealRenderReIDReport(BaseModel):
    status: str
    passed: bool
    measured: bool
    production_qualified: bool = False
    evidence_type: str = "BLENDER_TWO_SHOT_IMAGE_APPEARANCE_WITH_RIG_BOXES"
    shot_video_hashes: list[str]
    matches: list[ImageIdentityMatch] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    not_verified: list[str] = Field(default_factory=lambda:[
        "UNCONSTRAINED_ACTOR_DETECTION",
        "UNSEEN_CAMERA_AND_OCCLUSION_GENERALIZATION",
        "WAN_MULTISEED_IDENTITY",
        "HUMAN_APPROVED_GROUND_TRUTH",
    ])


class TwoShotImageIdentityVerifier:
    def __init__(
        self, *, minimum_score: float=.82,minimum_margin: float=.08,
    ) -> None:
        self.minimum_score=minimum_score
        self.minimum_margin=minimum_margin

    @staticmethod
    def score(left: dict,right: dict)->float:
        a=np.asarray(left["hsv_histogram"],dtype=float)
        b=np.asarray(right["hsv_histogram"],dtype=float)
        if a.shape!=(48,) or b.shape!=(48,) or np.any(a<0) or np.any(b<0):
            raise ValueError("RENDER_ACTOR_HIST_INVALID")
        if abs(a.sum()-1.)>.02 or abs(b.sum()-1.)>.02:
            raise ValueError("RENDER_ACTOR_HIST_NOT_NORMALIZED")
        similarity=float(np.sqrt(a*b).sum())
        rgb1=np.asarray(left["rgb_mean"],dtype=float)
        rgb2=np.asarray(right["rgb_mean"],dtype=float)
        if rgb1.shape!=(3,) or rgb2.shape!=(3,) or np.any(~np.isfinite(rgb1+rgb2)):
            raise ValueError("RENDER_ACTOR_RGB_INVALID")
        distance=float(np.linalg.norm(rgb1-rgb2))
        h1=int(left["ahash64"],16)
        h2=int(right["ahash64"],16)
        if len(left["ahash64"])!=16 or len(right["ahash64"])!=16:
            raise ValueError("RENDER_ACTOR_AHASH_INVALID")
        hamming=(h1^h2).bit_count()/64.
        return max(0.,min(1.,.65*similarity+.20*(1-min(1.,distance/.8))+.15*(1-hamming)))

    @staticmethod
    def load_scene(media_path: str|Path) -> tuple[Path,dict]:
        video=Path(media_path).resolve()
        if not video.is_file():
            raise ValueError("RENDER_VIDEO_MISSING")
        sidecar=Path(str(video)+".frame_qc.json")
        geometry=Path(str(video)+".geometry_qc.json")
        if not sidecar.is_file() or not geometry.is_file():
            raise ValueError("RENDER_IDENTITY_SIDECARS_MISSING")
        frame=json.loads(sidecar.read_text(encoding="utf-8"))
        geo=json.loads(geometry.read_text(encoding="utf-8"))
        actors=frame.get("actors",{})
        geometry_actors=geo.get("render_state",{}).get("actors",{})
        if len(actors)<2 or set(actors)!=set(geometry_actors):
            raise ValueError("RENDER_ACTOR_SET_NOT_GROUNDED")
        if not geo.get("identity_qc",{}).get("passed",False):
            raise ValueError("RIG_IDENTITY_GEOMETRY_QC_NOT_PASSED")
        return video,{"appearance":actors,"geometry":geometry_actors}

    def compare(self,*,first_video: str|Path,second_video: str|Path,
                second_override: dict|None=None)->RealRenderReIDReport:
        a,scene_a=self.load_scene(first_video)
        b,scene_b=self.load_scene(second_video)
        blockers=[]
        if a==b:
            blockers.append("TWO_DISTINCT_RENDER_FILES_REQUIRED")
        hashes=[
            hashlib.sha256(a.read_bytes()).hexdigest(),
            hashlib.sha256(b.read_bytes()).hexdigest(),
        ]
        if hashes[0]==hashes[1]:
            blockers.append("RENDER_VIDEO_BYTES_IDENTICAL")
        appearances_a=scene_a["appearance"]
        appearances_b=second_override if second_override is not None else scene_b["appearance"]
        if set(appearances_a)!=set(appearances_b):
            blockers.append("ACTOR_SETS_DIFFER")
        if not all(
            scene_a["geometry"].get(k,{}).get("rig_id") ==
            scene_b["geometry"].get(k,{}).get("rig_id")
            for k in appearances_a
        ):
            blockers.append("RIG_IDENTITY_VERSION_MISMATCH")
        results=[]
        for actor in sorted(set(appearances_a)&set(appearances_b)):
            positive=self.score(appearances_a[actor],appearances_b[actor])
            rivals=[
                self.score(appearances_a[actor],desc)
                for other,desc in appearances_b.items() if other!=actor
            ]
            rival=max(rivals,default=None)
            margin=positive-rival if rival is not None else None
            errors=[]
            if positive<self.minimum_score:
                errors.append("CROSS_SHOT_ACTOR_APPEARANCE_LOW")
            if rival is not None and margin<self.minimum_margin:
                errors.append("CROSS_SHOT_ACTOR_CONFUSION")
            results.append(ImageIdentityMatch(
                actor_id=actor,correct_score=positive,
                nearest_rival_score=rival,score_margin=margin,
                passed=not errors,findings=errors,
            ))
            blockers.extend(f"{actor}:{e}" for e in errors)
        return RealRenderReIDReport(
            status="ANNOTATED_TWO_SHOT_RENDER_APPEARANCE_PASS" if results and not blockers else "BLOCKED",
            passed=bool(results) and not blockers,measured=bool(results),
            shot_video_hashes=hashes,matches=results,blockers=sorted(set(blockers)),
        )
