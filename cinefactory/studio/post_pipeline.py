from __future__ import annotations

from pydantic import BaseModel, Field

from cinefactory.post.timeline import TimelineSpec

from .audio_department import AudioPlan, AudioQC
from .color_department import ColorPlan, ColorQC
from .editorial import EditDecisionGraph, EditorialCompiler
from .qc_department import QCLayer, StudioQCFinding


class PostProductionBundle(BaseModel):
    project_id: str
    editorial: EditDecisionGraph
    audio: AudioPlan
    color: ColorPlan
    media_paths: dict[str, str] = Field(default_factory=dict)


class PostProductionPreflight(BaseModel):
    project_id: str
    executable: bool
    timeline: TimelineSpec | None = None
    findings: list[StudioQCFinding] = Field(default_factory=list)


class PostProductionCoordinator:
    """Runs semantic post gates before expensive rendering/mastering begins."""

    def __init__(self) -> None:
        self.editorial = EditorialCompiler()
        self.audio_qc = AudioQC()
        self.color_qc = ColorQC()

    def _project_findings(
        self,
        bundle: PostProductionBundle,
    ) -> list[StudioQCFinding]:
        findings: list[StudioQCFinding] = []
        components = {
            "editorial": bundle.editorial.project_id,
            "audio": bundle.audio.project_id,
            "color": bundle.color.project_id,
        }
        for name, project_id in components.items():
            if project_id != bundle.project_id:
                findings.append(
                    StudioQCFinding(
                        code=f"POST_PROJECT_MISMATCH_{name.upper()}",
                        layer=QCLayer.TECHNICAL,
                        message=f"{name} project_id does not match post bundle",
                    )
                )
        return findings

    def preflight(self, bundle: PostProductionBundle) -> PostProductionPreflight:
        findings = self._project_findings(bundle)
        timeline: TimelineSpec | None = None

        if not findings:
            try:
                timeline = self.editorial.to_timeline(
                    bundle.editorial,
                    bundle.media_paths,
                )
            except (KeyError, ValueError) as exc:
                findings.append(
                    StudioQCFinding(
                        code="EDITORIAL_COMPILE_FAILED",
                        layer=QCLayer.EDITORIAL,
                        message=str(exc),
                    )
                )

        for code in self.audio_qc.validate(bundle.audio):
            findings.append(
                StudioQCFinding(
                    code=code.replace(":", "_"),
                    layer=QCLayer.AUDIO,
                    message=code,
                )
            )

        for code in self.color_qc.validate(bundle.color):
            findings.append(
                StudioQCFinding(
                    code=code.replace(":", "_"),
                    layer=QCLayer.COLOR,
                    message=code,
                )
            )

        return PostProductionPreflight(
            project_id=bundle.project_id,
            executable=not findings and timeline is not None,
            timeline=timeline,
            findings=findings,
        )
