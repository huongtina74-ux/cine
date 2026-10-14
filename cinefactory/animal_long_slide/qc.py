from __future__ import annotations

from .compatibility import SceneCompatibilityGate
from .contracts import (
    AssetManifest,
    LongSlideEpisodeSpec,
    LongSlideQCFinding,
    LongSlideQCReport,
)


class LongSlideAssetGate:
    @staticmethod
    def blockers(assets: list[AssetManifest]) -> list[str]:
        return [
            f"{asset.asset_id}: asset not production-safe"
            for asset in assets
            if asset.production_blocked
        ]


class LongSlideQC:
    MAX_CAMERA_HOLD_SECONDS = 12.0
    MAX_EVENT_GAP_SECONDS = 16.0

    def review(self, episode: LongSlideEpisodeSpec) -> LongSlideQCReport:
        findings: list[LongSlideQCFinding] = []
        tolerance = max(2.0, episode.target_duration_seconds * .01)
        if abs(episode.planned_duration_seconds - episode.target_duration_seconds) > tolerance:
            findings.append(LongSlideQCFinding(
                code="DURATION_DRIFT",
                severity="ERROR",
                message="planned duration exceeds tolerance",
            ))

        previous = None
        for module in episode.modules:
            for code in SceneCompatibilityGate.findings(module):
                findings.append(LongSlideQCFinding(
                    code="SCENE_OBSTACLE_INCOMPATIBLE",
                    severity="ERROR",
                    message=code,
                    module_id=module.module_id,
                ))
            pair = (module.animal_id, module.scene_kind.value)
            if pair == previous:
                findings.append(LongSlideQCFinding(
                    code="ADJACENT_REPETITION",
                    severity="ERROR",
                    message="adjacent modules repeat the same animal and scene",
                    module_id=module.module_id,
                ))
            previous = pair

            for beat in module.camera_beats:
                if beat.end_seconds - beat.start_seconds > self.MAX_CAMERA_HOLD_SECONDS:
                    findings.append(LongSlideQCFinding(
                        code="CAMERA_HOLD_TOO_LONG",
                        severity="WARN",
                        message="camera beat exceeds pacing limit",
                        module_id=module.module_id,
                    ))

            times = sorted(event.at_seconds for event in module.events)
            boundaries = [0.0, *times, module.duration_seconds]
            if any(b - a > self.MAX_EVENT_GAP_SECONDS for a, b in zip(boundaries, boundaries[1:])):
                findings.append(LongSlideQCFinding(
                    code="EVENT_DEAD_AIR",
                    severity="WARN",
                    message="module contains a long interval without a reaction/event",
                    module_id=module.module_id,
                ))

            if module.physics_phase_seconds > module.duration_seconds * .35:
                findings.append(LongSlideQCFinding(
                    code="PHYSICS_OVERUSE",
                    severity="WARN",
                    message="physics phase is too large; prefer controlled motion for repeatability",
                    module_id=module.module_id,
                ))

        if not episode.originality_signature:
            findings.append(LongSlideQCFinding(
                code="MISSING_ORIGINALITY_SIGNATURE",
                severity="ERROR",
                message="episode must carry a deterministic variation signature",
            ))

        return LongSlideQCReport(
            passed=not any(item.severity == "ERROR" for item in findings),
            findings=findings,
        )
