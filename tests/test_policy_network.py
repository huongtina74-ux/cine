from pathlib import Path

import pytest

from cinefactory.core.policy import ExecutorDescriptor, FactoryPolicy, PolicyViolation
from cinefactory.domain.enums import ExecutorKind, NetworkScope

ROOT = Path(__file__).resolve().parents[1]


def test_loopback_lan_is_allowed():
    policy = FactoryPolicy.from_yaml(ROOT / "config" / "factory_policy.yaml")
    policy.check_executor(ExecutorDescriptor("local.comfy", ExecutorKind.LOCAL, "video", NetworkScope.LOOPBACK_LAN))


def test_public_internet_generation_is_blocked_even_if_free():
    policy = FactoryPolicy.from_yaml(ROOT / "config" / "factory_policy.yaml")
    with pytest.raises(PolicyViolation):
        policy.check_executor(ExecutorDescriptor("public.service", ExecutorKind.LOCAL, "video", NetworkScope.PUBLIC_INTERNET))
