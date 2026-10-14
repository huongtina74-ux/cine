from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from cinefactory.domain.enums import ExecutorKind, NetworkScope, RightsStatus
from cinefactory.domain.models import AssetRecord


class PolicyViolation(RuntimeError):
    pass


@dataclass(frozen=True)
class ExecutorDescriptor:
    executor_id: str
    kind: ExecutorKind
    category: str
    network_scope: NetworkScope = NetworkScope.NONE
    notes: str = ""


class FactoryPolicy:
    def __init__(self, raw: dict):
        self.raw = raw

    @classmethod
    def from_yaml(cls, path: str | Path) -> "FactoryPolicy":
        with open(path, "r", encoding="utf-8") as f:
            return cls(yaml.safe_load(f))

    @property
    def zero_metered_api(self) -> bool:
        return self.raw.get("mode") == "ZERO_METERED_API"

    def check_executor(self, descriptor: ExecutorDescriptor) -> None:
        if descriptor.kind is ExecutorKind.PAID_METERED:
            raise PolicyViolation(f"Blocked metered executor: {descriptor.executor_id}")
        if descriptor.kind is ExecutorKind.UNKNOWN:
            raise PolicyViolation(f"Blocked unknown executor: {descriptor.executor_id}")
        if descriptor.kind is ExecutorKind.FREE_NON_METERED and not self.raw["production"].get(
            "allow_free_non_metered_services", False
        ):
            raise PolicyViolation(f"External non-metered service not approved: {descriptor.executor_id}")

        network = self.raw.get("network", {})
        if descriptor.network_scope is NetworkScope.PUBLIC_INTERNET and not network.get(
            "production_worker_public_internet", False
        ):
            raise PolicyViolation(f"Public-Internet production executor is blocked: {descriptor.executor_id}")
        if descriptor.network_scope is NetworkScope.LOOPBACK_LAN and not network.get(
            "allow_loopback_lan", True
        ):
            raise PolicyViolation(f"Local/LAN executor is blocked: {descriptor.executor_id}")

    def check_asset(self, asset: AssetRecord) -> None:
        if asset.rights_status is not RightsStatus.GREEN:
            raise PolicyViolation(
                f"Asset {asset.asset_id} is {asset.rights_status}; production requires GREEN rights status"
            )
        if asset.rights.commercial_use is False:
            raise PolicyViolation(f"Asset {asset.asset_id} is not cleared for commercial use")

    def assert_project_cost_policy(self, paid_generation_api_allowed: bool, cloud_fallback: bool) -> None:
        if not self.zero_metered_api:
            raise PolicyViolation("Factory policy must run in ZERO_METERED_API mode")
        if paid_generation_api_allowed:
            raise PolicyViolation("Project tries to enable paid generation APIs")
        if cloud_fallback:
            raise PolicyViolation("Cloud generation fallback is forbidden")
