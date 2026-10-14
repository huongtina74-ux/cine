from __future__ import annotations

import json
from pathlib import Path

from cinefactory.block_animation.visual_qc import BlockVisualQC
from cinefactory.block_animation.rendered_frame_qc import RenderedFrameAnalyzer
from cinefactory.media.ffmpeg import FFmpegToolchain


class RenderQualityRejected(RuntimeError):
    """A media file rendered successfully but failed deterministic QC."""

    def __init__(
        self,
        findings: list[str],
        *,
        result: dict | None = None,
    ) -> None:
        self.findings = list(findings)
        self.result = dict(result or {})
        super().__init__(
            "render combined QC failed: "
            + ",".join(self.findings)
        )


class BlockAnimationRuntime:
    def __init__(self, root, *, ffmpeg=None, visual_qc=None):
        self.root = Path(root).resolve()
        self.ffmpeg = ffmpeg or FFmpegToolchain()
        self.visual_qc = visual_qc or BlockVisualQC(self.ffmpeg)
        self.frame_qc = RenderedFrameAnalyzer(self.ffmpeg)

    def render_and_qc(self, worker, job):
        path = Path(
            worker.execute_animation(job)
        ).resolve()
        worker_result = (
            getattr(worker, "last_result", None)
            or {}
        )
        geometry_qc = (
            worker_result.get("geometry_qc") or {}
        )
        identity_qc = (
            worker_result.get("identity_qc") or {}
        )
        performance_qc = (
            worker_result.get("performance_qc") or {}
        )

        # Worker-side geometry/identity/performance blockers are upstream
        # of media validation. Preserve their root cause even when a broken
        # test/output file also exists.
        if geometry_qc and not geometry_qc.get("passed", False):
            raise RuntimeError(
                "render geometry QC failed: "
                + ",".join(geometry_qc.get("blockers", []))
            )
        if identity_qc and not identity_qc.get("passed", False):
            raise RuntimeError(
                "render identity QC failed: "
                + ",".join(identity_qc.get("blockers", []))
            )
        if performance_qc and not performance_qc.get("passed", False):
            raise RuntimeError(
                "render performance QC failed: "
                + ",".join(performance_qc.get("blockers", []))
            )

        # After worker-side hard gates pass, validate the encoded media.
        p = self.ffmpeg.probe(path)
        expected = job.shot.duration_seconds
        tol = max(.30, 3 / job.shot.fps)
        if p.duration <= 0:
            raise RuntimeError(
                f"render QC: zero duration for {path}"
            )
        if abs(p.duration - expected) > tol:
            raise RuntimeError(
                "render QC: duration "
                f"{p.duration:.3f}s != expected "
                f"{expected:.3f}s ± {tol:.3f}s"
            )
        profile_pct = (
            job.shot.render_quality.render_percentage
        )
        expected_pct = (
            50
            if job.render_preview
            else profile_pct
        )
        ew = round(
            job.shot.width * expected_pct / 100
        )
        eh = round(
            job.shot.height * expected_pct / 100
        )
        if p.width != ew or p.height != eh:
            raise RuntimeError(
                "render QC: resolution "
                f"{p.width}x{p.height} != "
                f"expected {ew}x{eh}"
            )

        visual = self.visual_qc.review(path)
        frame_qc = self.frame_qc.analyze(
            path,
            render_state=(
                worker_result.get("render_state")
                or {}
            ),
        )

        findings: list[str] = []
        findings.extend(
            "GEOMETRY_QC_BLOCKER:" + str(item)
            for item in geometry_qc.get(
                "blockers", []
            )
        )
        findings.extend(
            "IDENTITY_STRUCTURE_BLOCKER:"
            + str(item)
            for item in identity_qc.get(
                "blockers", []
            )
        )
        findings.extend(
            "PERFORMANCE_QC_BLOCKER:"
            + str(item)
            for item in performance_qc.get(
                "blockers", []
            )
        )

        frame_findings = list(
            frame_qc.findings
        )
        findings.extend(frame_findings)
        underexposed = any(
            "UNDEREXPOSED" in item.upper()
            for item in frame_findings
        )
        overexposed = any(
            "OVEREXPOSED" in item.upper()
            for item in frame_findings
        )
        for item in visual.findings:
            upper = item.upper()
            if (
                upper == "EXCESSIVE_BLACK_FRAMES"
                and (
                    underexposed
                    or overexposed
                )
            ):
                # Pixel evidence explains the dark image as
                # lookdev/exposure, not renderer failure.
                continue
            findings.append(str(item))

        result = {
            "path": str(path),
            "duration": p.duration,
            "width": p.width,
            "height": p.height,
            "fps": p.fps,
            "video_codec": p.video_codec,
            "worker_pid": worker.pid,
            "quality_profile": (
                job.shot.render_quality.profile_id
            ),
            "visual_qc": {
                "passed": visual.passed,
                "findings": visual.findings,
                "black_seconds": (
                    visual.black_seconds
                ),
                "freeze_seconds": (
                    visual.freeze_seconds
                ),
            },
            "rendered_frame_qc": (
                frame_qc.model_dump(
                    mode="json"
                )
            ),
            "geometry_qc": geometry_qc,
            "identity_qc": identity_qc,
            "performance_qc": performance_qc,
            "render_state": (
                worker_result.get("render_state")
                or {}
            ),
            "geometry_qc_sidecar": (
                worker_result.get(
                    "geometry_qc_sidecar"
                )
            ),
            "gaze_debug": (
                worker_result.get(
                    "gaze_debug", []
                )
            ),
            "lighting_debug": (
                worker_result.get(
                    "lighting_debug", {}
                )
            ),
            "creative_intent_bound": bool(
                worker_result.get(
                    "creative_intent_bound",
                    False,
                )
            ),
            "performance_directive_count": int(
                worker_result.get(
                    "performance_directive_count",
                    0,
                )
            ),
            "qc_passed": not findings,
            "qc_findings": findings,
        }
        if findings:
            raise RenderQualityRejected(
                findings,
                result=result,
            )
        return result

    def assemble_episode(self, payload):
        shots = sorted(payload.get("shots", []), key=lambda x: int(x.get("order", 0)))
        clips = [Path(x["path"]).resolve() for x in shots]
        if not clips:
            raise ValueError("episode assembly requires at least one shot")
        missing = [str(p) for p in clips if not p.exists()]
        if missing:
            raise FileNotFoundError(f"episode assembly missing rendered shots: {missing}")
        out = Path(payload["output_path"]).resolve()
        if out != self.root and self.root not in out.parents:
            raise ValueError("episode output must stay inside CineFactory root")
        result = self.ffmpeg.concat(clips, out)
        p = self.ffmpeg.probe(result)

        # Preserve semantic sound/VFX events for the audio/editor stage. The Blender
        # worker emits one local sidecar per shot; missing sidecars are tolerated for
        # legacy renders.
        event_rows = []
        for shot, clip in zip(shots, clips):
            sidecar = clip.with_suffix(clip.suffix + ".events.json")
            if not sidecar.exists():
                continue
            try:
                data = json.loads(sidecar.read_text(encoding="utf-8"))
                for event in data.get("events", []):
                    event_rows.append({"shot_id": shot.get("shot_id"), **event})
            except Exception:
                continue
        event_manifest = out.with_suffix(out.suffix + ".events.json")
        event_manifest.write_text(json.dumps({"episode_id": payload.get("episode_id"), "events": event_rows}, indent=2), encoding="utf-8")

        return {
            "path": str(result),
            "duration": p.duration,
            "width": p.width,
            "height": p.height,
            "fps": p.fps,
            "event_manifest": str(event_manifest),
            "event_count": len(event_rows),
            "qc_passed": p.duration > 0 and p.width is not None and p.height is not None,
        }
