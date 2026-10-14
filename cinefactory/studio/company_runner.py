from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from pydantic import BaseModel, Field

from .company import CompanyBlueprint, CompanyStage
from .execution import (
    CompanyExecutionEngine,
    CompanyExecutionLedger,
    ExecutionLedgerStore,
    RepairTicket,
    StageState,
)
from .qc_department import StudioQCFinding


class StageHandlerResult(BaseModel):
    ok: bool
    produced_artifacts: list[str] = Field(default_factory=list)
    checkpoint_ref: str | None = None
    qc_findings: list[StudioQCFinding] = Field(default_factory=list)
    detail: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class StageExecutionContext:
    blueprint: CompanyBlueprint
    stage: CompanyStage
    kernel: Any | None = None
    project_root: Path | None = None


StageHandler = Callable[[StageExecutionContext], StageHandlerResult]


class StageHandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, StageHandler] = {}

    def register(self, stage_id: str, handler: StageHandler) -> None:
        if stage_id in self._handlers:
            raise ValueError(f"duplicate stage handler: {stage_id}")
        self._handlers[stage_id] = handler

    def get(self, stage_id: str) -> StageHandler | None:
        return self._handlers.get(stage_id)

    def ids(self) -> list[str]:
        return sorted(self._handlers)


class CompanyTickResult(BaseModel):
    ran_stage_ids: list[str] = Field(default_factory=list)
    skipped_stage_ids: list[str] = Field(default_factory=list)
    blocked_stage_ids: list[str] = Field(default_factory=list)
    repair_tickets: list[RepairTicket] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class CompanyRunReport(BaseModel):
    project_id: str
    complete: bool
    cycles: int
    ledger: CompanyExecutionLedger
    repair_tickets: list[RepairTicket] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class AutonomousCompanyRunner:
    """Executes company stages through registered handlers with durable resume semantics."""

    def __init__(
        self,
        blueprint: CompanyBlueprint,
        handlers: StageHandlerRegistry,
        *,
        store: ExecutionLedgerStore,
        kernel: Any | None = None,
        project_root: str | Path | None = None,
        ledger: CompanyExecutionLedger | None = None,
        retry_limit: int = 2,
    ) -> None:
        if blueprint.strict_stage_receipts:
            from .contract_integrity import audit_company_wiring
            wiring = audit_company_wiring(blueprint.stages)
            if not wiring.valid:
                raise ValueError(
                    "COMPANY_STAGE_WIRING_BLOCKED:"
                    + ",".join(wiring.blocker_codes())
                )
        self.blueprint = blueprint
        self.handlers = handlers
        self.store = store
        self.kernel = kernel
        self.project_root = Path(project_root) if project_root is not None else None
        self.engine = CompanyExecutionEngine(
            blueprint,
            ledger=ledger,
            retry_limit=retry_limit,
        )

        self.store.save(self.engine.ledger)

    @classmethod
    def resume(
        cls,
        blueprint: CompanyBlueprint,
        handlers: StageHandlerRegistry,
        *,
        store: ExecutionLedgerStore,
        kernel: Any | None = None,
        project_root: str | Path | None = None,
        retry_limit: int = 2,
    ) -> "AutonomousCompanyRunner":
        ledger = store.load(blueprint.project.studio_project_id)
        return cls(
            blueprint,
            handlers,
            store=store,
            kernel=kernel,
            project_root=project_root,
            ledger=ledger,
            retry_limit=retry_limit,
        )

    def _persist(self) -> None:
        self.store.save(self.engine.ledger)

    def _context(self, stage: CompanyStage) -> StageExecutionContext:
        return StageExecutionContext(
            blueprint=self.blueprint,
            stage=stage,
            kernel=self.kernel,
            project_root=self.project_root,
        )

    def tick(self) -> CompanyTickResult:
        decision = self.engine.schedule()
        result = CompanyTickResult(
            blocked_stage_ids=list(decision.blocked_stage_ids),
            errors=list(decision.reasons),
        )

        for stage_id in decision.ready_stage_ids:
            stage = self.engine.stage_map[stage_id]
            handler = self.handlers.get(stage_id)
            if handler is None:
                if not stage.required:
                    self.engine.skip_optional(stage_id)
                    result.skipped_stage_ids.append(stage_id)
                    self._persist()
                    continue
                record = self.engine.ledger.get(stage_id)
                record.state = StageState.BLOCKED
                record.error = "STAGE_HANDLER_MISSING"
                result.blocked_stage_ids.append(stage_id)
                result.errors.append(f"{stage_id}:STAGE_HANDLER_MISSING")
                self._persist()
                continue

            self.engine.start(stage_id)
            result.ran_stage_ids.append(stage_id)
            self._persist()

            try:
                handler_result = handler(self._context(stage))
            except Exception as exc:
                self.engine.fail(stage_id, f"{type(exc).__name__}:{exc}")
                result.errors.append(f"{stage_id}:{type(exc).__name__}:{exc}")
                self._persist()
                continue

            if handler_result.qc_findings:
                tickets = self.engine.route_qc_findings(
                    stage_id,
                    handler_result.qc_findings,
                )
                result.repair_tickets.extend(tickets)
                record = self.engine.ledger.get(stage_id)
                record.error = handler_result.error or "QC_REPAIR_REQUIRED"
                self._persist()
                continue

            if not handler_result.ok:
                self.engine.fail(
                    stage_id,
                    handler_result.error or "STAGE_HANDLER_FAILED",
                )
                result.errors.append(
                    f"{stage_id}:{handler_result.error or 'STAGE_HANDLER_FAILED'}"
                )
                self._persist()
                continue

            if self.blueprint.strict_stage_receipts:
                from .artifact_receipts import verify_persisted_outputs
                studio = (
                    self.kernel.studio
                    if hasattr(self.kernel, "studio")
                    else self.kernel
                )
                blackboard = getattr(studio, "blackboard", None)
                if blackboard is None:
                    receipt_error = "STAGE_BLACKBOARD_UNAVAILABLE"
                else:
                    problems = verify_persisted_outputs(
                        blackboard,
                        self.blueprint.project.studio_project_id,
                        stage,
                        handler_result.produced_artifacts,
                    )
                    receipt_error = (
                        ",".join(problem.code + ":" + problem.artifact
                                 for problem in problems)
                        if problems else None
                    )
                if receipt_error:
                    self.engine.fail(
                        stage_id, "STAGE_RECEIPTS_UNVERIFIED:" + receipt_error,
                    )
                    result.errors.append(
                        f"{stage_id}:STAGE_RECEIPTS_UNVERIFIED:{receipt_error}"
                    )
                    self._persist()
                    continue

            self.engine.succeed(
                stage_id,
                handler_result.produced_artifacts,
                checkpoint_ref=handler_result.checkpoint_ref,
            )
            self._persist()

        return result

    def run_until_blocked_or_complete(
        self,
        *,
        max_cycles: int = 100,
    ) -> CompanyRunReport:
        all_repairs: list[RepairTicket] = []
        all_errors: list[str] = []

        for cycle in range(1, max_cycles + 1):
            if self.engine.is_complete():
                return CompanyRunReport(
                    project_id=self.blueprint.project.studio_project_id,
                    complete=True,
                    cycles=cycle - 1,
                    ledger=self.engine.ledger,
                    repair_tickets=all_repairs,
                    errors=all_errors,
                )

            tick = self.tick()
            all_repairs.extend(tick.repair_tickets)
            all_errors.extend(tick.errors)
            progressed = bool(tick.ran_stage_ids or tick.skipped_stage_ids)
            if tick.repair_tickets or tick.blocked_stage_ids or not progressed:
                return CompanyRunReport(
                    project_id=self.blueprint.project.studio_project_id,
                    complete=False,
                    cycles=cycle,
                    ledger=self.engine.ledger,
                    repair_tickets=all_repairs,
                    errors=all_errors,
                )

        return CompanyRunReport(
            project_id=self.blueprint.project.studio_project_id,
            complete=self.engine.is_complete(),
            cycles=max_cycles,
            ledger=self.engine.ledger,
            repair_tickets=all_repairs,
            errors=all_errors + ["MAX_CYCLES_REACHED"],
        )
