from __future__ import annotations

from cinefactory.domain.enums import ProjectState


class InvalidTransition(RuntimeError):
    pass


TRANSITIONS: dict[ProjectState, set[ProjectState]] = {
    ProjectState.PROJECT_CREATED: {ProjectState.POLICY_CHECKED, ProjectState.BLOCKED},
    ProjectState.POLICY_CHECKED: {ProjectState.STORY_READY, ProjectState.BLOCKED},
    ProjectState.STORY_READY: {ProjectState.SCRIPT_READY, ProjectState.BLOCKED},
    ProjectState.SCRIPT_READY: {ProjectState.ASSET_BIBLE_READY, ProjectState.BLOCKED},
    ProjectState.ASSET_BIBLE_READY: {ProjectState.DIRECTOR_PLAN_READY, ProjectState.BLOCKED},
    ProjectState.DIRECTOR_PLAN_READY: {ProjectState.SHOTSPEC_VALIDATED, ProjectState.BLOCKED},
    ProjectState.SHOTSPEC_VALIDATED: {ProjectState.PILOT_GENERATED, ProjectState.BLOCKED},
    ProjectState.PILOT_GENERATED: {ProjectState.PILOT_APPROVED, ProjectState.BLOCKED},
    ProjectState.PILOT_APPROVED: {ProjectState.BATCH_PRODUCTION, ProjectState.BLOCKED},
    ProjectState.BATCH_PRODUCTION: {ProjectState.SHOT_QC_COMPLETE, ProjectState.BLOCKED},
    ProjectState.SHOT_QC_COMPLETE: {ProjectState.SEQUENCE_QC_COMPLETE, ProjectState.BLOCKED},
    ProjectState.SEQUENCE_QC_COMPLETE: {ProjectState.EDIT_LOCKED, ProjectState.BLOCKED},
    ProjectState.EDIT_LOCKED: {ProjectState.AUDIO_MASTERED, ProjectState.BLOCKED},
    ProjectState.AUDIO_MASTERED: {ProjectState.COLOR_MASTERED, ProjectState.BLOCKED},
    ProjectState.COLOR_MASTERED: {ProjectState.MASTER_4K_VALIDATED, ProjectState.BLOCKED},
    ProjectState.MASTER_4K_VALIDATED: {ProjectState.RIGHTS_FINAL_PASS, ProjectState.BLOCKED},
    ProjectState.RIGHTS_FINAL_PASS: {ProjectState.HUMAN_RELEASE_APPROVAL, ProjectState.BLOCKED},
    ProjectState.HUMAN_RELEASE_APPROVAL: {ProjectState.PUBLISHED, ProjectState.ARCHIVED, ProjectState.BLOCKED},
    ProjectState.PUBLISHED: {ProjectState.ARCHIVED},
    ProjectState.ARCHIVED: set(),
    ProjectState.BLOCKED: set(),
}


def can_transition(current: ProjectState, target: ProjectState) -> bool:
    return target in TRANSITIONS[current]


def require_transition(current: ProjectState, target: ProjectState) -> None:
    if not can_transition(current, target):
        raise InvalidTransition(f"Invalid project transition: {current} -> {target}")
