from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, Field

from .company_runner import AutonomousCompanyRunner
from .execution import RepairTicket, StageState


class RepairResult(BaseModel):
    repaired: bool
    detail: str | None = None
    evidence: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class RepairContext:
    ticket: RepairTicket
    runner: AutonomousCompanyRunner
    kernel: Any | None = None


RepairHandler = Callable[[RepairContext], RepairResult]


class RepairHandlerRegistry:
    def __init__(self) -> None:
        self._by_code: dict[str, RepairHandler] = {}
        self._by_owner: dict[str, RepairHandler] = {}

    def register_code(self, finding_code: str, handler: RepairHandler) -> None:
        if finding_code in self._by_code:
            raise ValueError(f"duplicate repair handler: {finding_code}")
        self._by_code[finding_code] = handler

    def register_owner(self, owner: str, handler: RepairHandler) -> None:
        if owner in self._by_owner:
            raise ValueError(f"duplicate repair owner handler: {owner}")
        self._by_owner[owner] = handler

    def get(self, ticket: RepairTicket) -> RepairHandler | None:
        return self._by_code.get(ticket.finding_code) or self._by_owner.get(
            ticket.owner.value
        )



class RepairCycleReport(BaseModel):
    attempted: int = 0
    repaired: int = 0
    unresolved: list[str] = Field(default_factory=list)
    details: list[str] = Field(default_factory=list)


class AutonomousRepairSupervisor:
    """Applies only registered bounded repairs; unknown problems remain blocked."""

    def __init__(
        self,
        registry: RepairHandlerRegistry,
        *,
        max_rounds_per_stage: int = 2,
    ) -> None:
        self.registry = registry
        self.max_rounds_per_stage = max_rounds_per_stage
        self._attempts: dict[tuple[str, str], int] = {}

    def repair(
        self,
        runner: AutonomousCompanyRunner,
        tickets: list[RepairTicket],
    ) -> RepairCycleReport:
        report = RepairCycleReport()
        repaired_stages: set[str] = set()
        for ticket in tickets:
            key = (ticket.stage_id, ticket.finding_code)
            attempts = self._attempts.get(key, 0)
            if attempts >= self.max_rounds_per_stage:
                report.unresolved.append(
                    f"{ticket.stage_id}:{ticket.finding_code}:REPAIR_LIMIT"
                )
                continue
            handler = self.registry.get(ticket)
            if handler is None:
                report.unresolved.append(
                    f"{ticket.stage_id}:{ticket.finding_code}:NO_REPAIR_HANDLER"
                )
                continue

            self._attempts[key] = attempts + 1
            report.attempted += 1
            try:
                result = handler(
                    RepairContext(
                        ticket=ticket,
                        runner=runner,
                        kernel=runner.kernel,
                    )
                )
            except Exception as exc:
                report.unresolved.append(
                    f"{ticket.stage_id}:{ticket.finding_code}:"
                    f"{type(exc).__name__}:{exc}"
                )
                continue

            if not result.repaired:
                report.unresolved.append(
                    f"{ticket.stage_id}:{ticket.finding_code}:REPAIR_DECLINED"
                )
                if result.detail:
                    report.details.append(result.detail)
                continue
            report.repaired += 1
            repaired_stages.add(ticket.stage_id)
            if result.detail:
                report.details.append(result.detail)

        for stage_id in sorted(repaired_stages):
            record = runner.engine.ledger.get(stage_id)
            if record.state is StageState.NEEDS_REPAIR:
                runner.engine.repair_complete(stage_id)
        if repaired_stages:
            runner.store.save(runner.engine.ledger)
        return report


class SupervisedRunReport(BaseModel):
    complete: bool
    repair_rounds: int
    unresolved: list[str] = Field(default_factory=list)
    run_errors: list[str] = Field(default_factory=list)


    @classmethod
    def from_state(
        cls,
        *,
        complete: bool,
        repair_rounds: int,
        unresolved: list[str],
        run_errors: list[str],
    ) -> "SupervisedRunReport":
        return cls(
            complete=complete,
            repair_rounds=repair_rounds,
            unresolved=unresolved,
            run_errors=run_errors,
        )


def run_with_repairs(
    supervisor: AutonomousRepairSupervisor,
    runner: AutonomousCompanyRunner,
    *,
    max_supervisor_rounds: int = 6,
    max_cycles_per_run: int = 100,
) -> SupervisedRunReport:
    errors: list[str] = []
    unresolved: list[str] = []
    for repair_round in range(max_supervisor_rounds + 1):
        report = runner.run_until_blocked_or_complete(
            max_cycles=max_cycles_per_run,
        )
        errors.extend(report.errors)
        if report.complete:
            return SupervisedRunReport.from_state(
                complete=True,
                repair_rounds=repair_round,
                unresolved=unresolved,
                run_errors=errors,
            )
        if not report.repair_tickets:
            unresolved.append("RUN_BLOCKED_WITHOUT_REPAIR_TICKETS")
            return SupervisedRunReport.from_state(
                complete=False,
                repair_rounds=repair_round,
                unresolved=unresolved,
                run_errors=errors,
            )
        repair_report = supervisor.repair(runner, report.repair_tickets)
        unresolved.extend(repair_report.unresolved)
        if repair_report.repaired == 0:
            return SupervisedRunReport.from_state(
                complete=False,
                repair_rounds=repair_round,
                unresolved=unresolved,
                run_errors=errors,
            )
    unresolved.append("SUPERVISOR_ROUND_LIMIT")
    return SupervisedRunReport.from_state(
        complete=False,
        repair_rounds=max_supervisor_rounds,
        unresolved=unresolved,
        run_errors=errors,
    )
