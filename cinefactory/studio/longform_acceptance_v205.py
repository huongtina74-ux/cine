"""Evidence-based long-form film acceptance; media probe != film artistry."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


def sha256_stream(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        while chunk:=f.read(1024*1024):
            h.update(chunk)
    return h.hexdigest()


def probe_film(path, *, min_seconds=480, max_seconds=720,
               min_width=1920,min_height=1080):
    movie=Path(path).resolve(strict=True)
    proc=subprocess.run(
        ["ffprobe","-v","error","-show_entries",
         "format=duration,format_name:stream=index,codec_type,codec_name,width,height,avg_frame_rate,channels",
         "-of","json",str(movie)],
        capture_output=True,text=True,timeout=30,
    )
    if proc.returncode!=0:
        raise RuntimeError("FFPROBE_FAILED:" + proc.stderr[-180:])
    media=json.loads(proc.stdout)
    streams=media.get("streams",[])
    video=next((s for s in streams if s.get("codec_type")=="video"),{})
    audio=next((s for s in streams if s.get("codec_type")=="audio"),{})
    seconds=float(media.get("format",{}).get("duration") or 0)
    findings=[]
    if seconds<min_seconds:findings.append("LONG_FORM_TOO_SHORT")
    if seconds>max_seconds:findings.append("LONG_FORM_EXCEEDS_ASSIGNED_SCOPE")
    if int(video.get("width") or 0)<min_width or int(video.get("height") or 0)<min_height:
        findings.append("MASTER_NOT_AT_LEAST_1080P")
    if not audio:findings.append("FINAL_AUDIO_STREAM_MISSING")
    rate=video.get("avg_frame_rate") or "0/1"
    try:
        nom,den=(int(v) for v in rate.split("/"))
        fps=nom/den
    except (ValueError,ZeroDivisionError):
        fps=0
    if fps<23.0:findings.append("FRAME_RATE_BELOW_ACCEPTANCE")
    if movie.stat().st_size<1024:findings.append("FILE_INVALID_OR_EMPTY")
    return {
        "schema":"cine.film.longform_technical_evidence.v205",
        "movie":str(movie),"sha256":sha256_stream(movie),
        "duration_seconds":round(seconds,3),"width":video.get("width"),
        "height":video.get("height"),"fps":round(fps,3),
        "audio_channels":audio.get("channels"),
        "technical_findings":findings,
        "technical_pass":not findings,
        "independent_story_qc":"NOT_OBSERVED",
        "independent_art_qc":"NOT_OBSERVED",
        "actor_identity_and_expression_qc":"NOT_OBSERVED",
        "sound_design_and_listening_qc":"NOT_OBSERVED",
        "rights_qc":"NOT_OBSERVED",
        "commercial_release_accepted":False,
    }


def independent_film_acceptance(media_evidence, reviews, trusted_reviewer_keys):
    """Verify six distinct external Ed25519-signed film reviews, one per gate.

    trusted_reviewer_keys is a trusted mapping provided by the studio operator
    outside the media project. Project JSON cannot nominate its own reviewer.
    """
    if media_evidence.get("technical_pass") is not True:
        return {"status":"REJECTED_TECHNICAL","release_permission":False,
                "findings":media_evidence.get("technical_findings",[])}
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    import base64
    required=("story","acting_identity","camera_edit","sound","rights","originality")
    missing=[]
    approved_people=set()
    for gate in required:
        item=reviews.get(gate,{})
        person=item.get("reviewer_id")
        payload=item.get("payload",{})
        if (not person or person not in trusted_reviewer_keys
                or person in approved_people
                or payload.get("gate")!=gate
                or payload.get("master_sha256")!=media_evidence.get("sha256")
                or payload.get("decision")!="ACCEPT"
                or payload.get("schema")!="cine.film.signed_review.v205"):
            missing.append(gate)
            continue
        try:
            pem=Path(trusted_reviewer_keys[person]).read_bytes()
            pub=serialization.load_pem_public_key(pem)
            if not isinstance(pub,Ed25519PublicKey):
                raise TypeError("UNSUPPORTED_REVIEW_SIGNATURE")
            pub.verify(
                base64.b64decode(item["signature_b64"],validate=True),
                json.dumps(payload,sort_keys=True,separators=(",",":"),
                           ensure_ascii=False).encode("utf8"),
            )
            approved_people.add(person)
        except (KeyError, ValueError, TypeError, InvalidSignature):
            missing.append(gate)
    if missing:
        return {"status":"PENDING_AUTHENTICATED_REVIEW","release_permission":False,
                "missing_review_gates":missing}
    return {"status":"FILM_ACCEPTED_BY_SIGNED_INDEPENDENT_REVIEWERS",
            "release_permission":True,
            "master_sha256":media_evidence["sha256"],
            "technical_evidence":media_evidence["schema"],
            "reviewed_gates":list(required),
            "reviewer_count":len(approved_people),
            "published":False}
