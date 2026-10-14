from __future__ import annotations

from pydantic import BaseModel, Field

from .contracts import DepartmentId, MediaFormat


class PodRole(BaseModel):
    role_id: str
    department: DepartmentId
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)


class ProjectPod(BaseModel):
    project_id: str
    media_format: MediaFormat
    roles: list[PodRole] = Field(default_factory=list)

    @property
    def departments(self) -> set[DepartmentId]:
        return {r.department for r in self.roles}


class ProjectPodBuilder:
    """Forms a temporary delivery team from permanent craft departments."""

    CORE = [
        PodRole(
            role_id="producer",
            department=DepartmentId.STUDIO_MANAGEMENT,
            responsibilities=["scope", "gates", "schedule", "cross-department coordination"],
        ),
        PodRole(
            role_id="research",
            department=DepartmentId.INTELLIGENCE,
            responsibilities=["market", "audience", "competitors", "production methods"],
        ),
        PodRole(
            role_id="creative",
            department=DepartmentId.CREATIVE_STRATEGY,
            responsibilities=["creative brief", "differentiation", "project DNA"],
        ),
        PodRole(
            role_id="technical_director",
            department=DepartmentId.TECHNICAL_DIRECTION,
            responsibilities=["capability routing", "preflight", "resource plan"],
        ),
        PodRole(
            role_id="editor",
            department=DepartmentId.EDITORIAL,
            responsibilities=["edit decision graph", "timeline", "pacing"],
        ),
        PodRole(
            role_id="sound",
            department=DepartmentId.AUDIO,
            responsibilities=["voice", "SFX", "music", "mix"],
        ),
        PodRole(
            role_id="qc",
            department=DepartmentId.QC,
            responsibilities=["independent review", "repair routing"],
        ),
    ]
    def build(self, project_id: str, media_format: MediaFormat) -> ProjectPod:
        roles = [r.model_copy(deep=True) for r in self.CORE]

        evidence_formats = {
            MediaFormat.DOCUMENTARY,
            MediaFormat.TUTORIAL,
            MediaFormat.EXPLAINER,
            MediaFormat.REVIEW,
            MediaFormat.DATA_VISUALIZATION,
        }
        direction_formats = {
            MediaFormat.NARRATIVE,
            MediaFormat.NARRATIVE_FILM,
            MediaFormat.ANIMATION,
            MediaFormat.COMMERCIAL,
            MediaFormat.MUSIC_VIDEO,
            MediaFormat.GAMEPLAY,
        }

        if media_format in evidence_formats:
            roles.append(
                PodRole(
                    role_id="evidence",
                    department=DepartmentId.EVIDENCE,
                    responsibilities=["claim graph", "fact checking", "source integrity"],
                )
            )
        roles.append(
            PodRole(
                role_id="writer",
                department=DepartmentId.WRITERS_ROOM,
                responsibilities=["format grammar", "script", "revision"],
            )
        )
        if media_format in direction_formats:
            roles.extend([
                PodRole(
                    role_id="director",
                    department=DepartmentId.DIRECTION,
                    responsibilities=["audience experience", "blocking", "performance intent", "coverage"],
                ),
                PodRole(
                    role_id="dop",
                    department=DepartmentId.CINEMATOGRAPHY,
                    responsibilities=["camera", "lighting", "screen direction"],
                ),
            ])
        if media_format in {
            MediaFormat.NARRATIVE,
            MediaFormat.NARRATIVE_FILM,
            MediaFormat.ANIMATION,
            MediaFormat.COMMERCIAL,
            MediaFormat.MUSIC_VIDEO,
        }:
            roles.append(
                PodRole(
                    role_id="production_design",
                    department=DepartmentId.PRODUCTION_DESIGN,
                    responsibilities=["world", "characters", "sets", "props", "lookdev"],
                )
            )
        if media_format is MediaFormat.GAMEPLAY:
            roles.append(
                PodRole(
                    role_id="runtime_operator",
                    department=DepartmentId.PRODUCTION,
                    responsibilities=["runtime control", "capture", "checkpoint/recovery"],
                )
            )

        return ProjectPod(project_id=project_id, media_format=media_format, roles=roles)
