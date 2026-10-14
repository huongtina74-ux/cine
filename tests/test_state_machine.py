import pytest

from cinefactory.core.state_machine import InvalidTransition, require_transition
from cinefactory.domain.enums import ProjectState


def test_valid_transition():
    require_transition(ProjectState.PROJECT_CREATED, ProjectState.POLICY_CHECKED)


def test_invalid_transition_is_blocked():
    with pytest.raises(InvalidTransition):
        require_transition(ProjectState.PROJECT_CREATED, ProjectState.BATCH_PRODUCTION)
