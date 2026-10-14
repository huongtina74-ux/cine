from __future__ import annotations

from enum import IntEnum
from pydantic import BaseModel, Field


class MaturityLevel(IntEnum):
    UNSPECIFIED = 0
    DOCUMENTED = 1
    CONTRACTED = 2
    TESTED = 3
    PRODUCTION_READY = 4
    BENCHMARK_LEADING = 5


class DepartmentMaturity(BaseModel):
    department_id: str
    level: MaturityLevel = MaturityLevel.UNSPECIFIED
    documented: bool = False
    contracts_defined: bool = False
    tests_passed: bool = False
    production_evidence: bool = False
    benchmark_evidence: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)

    def inferred_level(self) -> MaturityLevel:
        if not self.documented:
            return MaturityLevel.UNSPECIFIED
        if not self.contracts_defined:
            return MaturityLevel.DOCUMENTED
        if not self.tests_passed:
            return MaturityLevel.CONTRACTED
        if not self.production_evidence:
            return MaturityLevel.TESTED
        if not self.benchmark_evidence:
            return MaturityLevel.PRODUCTION_READY
        return MaturityLevel.BENCHMARK_LEADING


class CompanyMaturityAudit:
    def __init__(self) -> None:
        self._items: dict[str, DepartmentMaturity] = {}

    def assess(self, item: DepartmentMaturity) -> DepartmentMaturity:
        item.level = item.inferred_level()
        self._items[item.department_id] = item
        return item

    def get(self, department_id: str) -> DepartmentMaturity:
        return self._items[department_id]

    def minimum_level(self) -> MaturityLevel:
        if not self._items:
            return MaturityLevel.UNSPECIFIED
        return min((item.level for item in self._items.values()), default=MaturityLevel.UNSPECIFIED)

    def benchmark_leading_claim_allowed(self, critical_departments: list[str]) -> bool:
        if not critical_departments:
            return False
        for department_id in critical_departments:
            item = self._items.get(department_id)
            if item is None or item.level is not MaturityLevel.BENCHMARK_LEADING:
                return False
        return True
