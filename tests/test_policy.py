from pathlib import Path

import pytest

from cinefactory.core.policy import ExecutorDescriptor, FactoryPolicy, PolicyViolation
from cinefactory.domain.enums import ExecutorKind, NetworkScope

ROOT = Path(__file__).resolve().parents[1]


def test_local_executor_allowed():
    policy = FactoryPolicy.from_yaml(ROOT / "config" / "factory_policy.yaml")
    policy.check_executor(ExecutorDescriptor("wan.local", ExecutorKind.LOCAL, "video"))


def test_paid_metered_executor_blocked():
    policy = FactoryPolicy.from_yaml(ROOT / "config" / "factory_policy.yaml")
    with pytest.raises(PolicyViolation):
        policy.check_executor(ExecutorDescriptor("cloud.video", ExecutorKind.PAID_METERED, "video", NetworkScope.PUBLIC_INTERNET))
