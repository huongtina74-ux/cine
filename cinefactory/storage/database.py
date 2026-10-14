from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from cinefactory.domain.enums import JobState, ProjectState
from cinefactory.domain.models import AssetRecord, AuditEvent, JobAttempt, ProjectRecord, ProjectSpec, RenderJob


class Base(DeclarativeBase):
    pass


class ProjectRow(Base):
    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    state: Mapped[str] = mapped_column(String(64), nullable=False)
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    blocked_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    spec_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AuditEventRow(Base):
    __tablename__ = "audit_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    actor: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class AssetRow(Base):
    __tablename__ = "assets"

    asset_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    asset_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    rights_status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    content_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    record_json: Mapped[str] = mapped_column(Text, nullable=False)


class JobRow(Base):
    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    shot_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    job_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    executor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    workflow_id: Mapped[str] = mapped_column(String(128), nullable=False)
    workflow_version: Mapped[str] = mapped_column(String(64), nullable=False)
    dependency_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    state: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    output_artifact_ids_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    payload_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class JobAttemptRow(Base):
    __tablename__ = "job_attempts"

    attempt_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(64), nullable=False)
    worker_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    failure_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")


class Database:
    """SQLAlchemy database facade.

    SQLite is used for local development. The same repositories work with PostgreSQL by
    changing the SQLAlchemy URL (e.g. postgresql+psycopg://...).
    """

    def __init__(self, url: str = "sqlite:///./data/cinefactory.db") -> None:
        if url.startswith("sqlite:///"):
            path = Path(url.removeprefix("sqlite:///"))
            path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(url, future=True)
        self.Session = sessionmaker(self.engine, expire_on_commit=False, class_=Session)

    def create_schema(self) -> None:
        Base.metadata.create_all(self.engine)


class SqlProjectRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def save(self, record: ProjectRecord) -> None:
        with self.db.Session.begin() as session:
            row = session.get(ProjectRow, record.spec.project_id)
            if row is None:
                row = ProjectRow(project_id=record.spec.project_id)
                session.add(row)
            row.state = record.state.value
            row.current_version = record.current_version
            row.blocked_reason = record.blocked_reason
            row.spec_json = record.spec.model_dump_json()
            row.created_at = record.created_at
            row.updated_at = record.updated_at

    def get(self, project_id: str) -> ProjectRecord:
        with self.db.Session() as session:
            row = session.get(ProjectRow, project_id)
            if row is None:
                raise KeyError(project_id)
            return ProjectRecord(
                spec=ProjectSpec.model_validate_json(row.spec_json),
                state=ProjectState(row.state),
                current_version=row.current_version,
                blocked_reason=row.blocked_reason,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )

    def list_ids(self) -> list[str]:
        with self.db.Session() as session:
            return list(session.scalars(select(ProjectRow.project_id).order_by(ProjectRow.project_id)))


class AuditLogRepository:
    """Append-only audit log. No update/delete API is intentionally provided."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def append(self, event: AuditEvent) -> None:
        with self.db.Session.begin() as session:
            session.add(
                AuditEventRow(
                    event_id=event.event_id,
                    project_id=event.project_id,
                    event_type=event.event_type,
                    actor=event.actor,
                    entity_type=event.entity_type,
                    entity_id=event.entity_id,
                    payload_json=json.dumps(event.payload, ensure_ascii=False, sort_keys=True),
                    created_at=event.created_at,
                )
            )

    def list_for_project(self, project_id: str) -> list[AuditEvent]:
        with self.db.Session() as session:
            rows = session.scalars(
                select(AuditEventRow)
                .where(AuditEventRow.project_id == project_id)
                .order_by(AuditEventRow.created_at, AuditEventRow.event_id)
            ).all()
            return [
                AuditEvent(
                    event_id=r.event_id,
                    project_id=r.project_id,
                    event_type=r.event_type,
                    actor=r.actor,
                    entity_type=r.entity_type,
                    entity_id=r.entity_id,
                    payload=json.loads(r.payload_json),
                    created_at=r.created_at,
                )
                for r in rows
            ]


class JobLedgerRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    @staticmethod
    def _to_job(row: JobRow) -> RenderJob:
        return RenderJob(
            job_id=row.job_id,
            project_id=row.project_id,
            shot_id=row.shot_id,
            job_type=row.job_type,
            executor_id=row.executor_id,
            workflow_id=row.workflow_id,
            workflow_version=row.workflow_version,
            dependency_hash=row.dependency_hash,
            idempotency_key=row.idempotency_key,
            state=JobState(row.state),
            attempt=row.attempt,
            max_attempts=row.max_attempts,
            failure_code=row.failure_code,
            error_detail=row.error_detail,
            queued_at=row.queued_at,
            started_at=row.started_at,
            finished_at=row.finished_at,
            output_artifact_ids=json.loads(row.output_artifact_ids_json),
            payload=json.loads(row.payload_json),
        )

    def create_or_get(self, job: RenderJob) -> tuple[RenderJob, bool]:
        with self.db.Session.begin() as session:
            existing = session.scalar(select(JobRow).where(JobRow.idempotency_key == job.idempotency_key))
            if existing is not None:
                return self._to_job(existing), False
            row = JobRow(
                job_id=job.job_id,
                project_id=job.project_id,
                shot_id=job.shot_id,
                job_type=job.job_type,
                executor_id=job.executor_id,
                workflow_id=job.workflow_id,
                workflow_version=job.workflow_version,
                dependency_hash=job.dependency_hash,
                idempotency_key=job.idempotency_key or "",
                state=job.state.value,
                attempt=job.attempt,
                max_attempts=job.max_attempts,
                failure_code=job.failure_code.value if job.failure_code else None,
                error_detail=job.error_detail,
                queued_at=job.queued_at,
                started_at=job.started_at,
                finished_at=job.finished_at,
                output_artifact_ids_json=json.dumps(job.output_artifact_ids),
                payload_json=json.dumps(job.payload, ensure_ascii=False),
            )
            session.add(row)
            return job, True

    def save(self, job: RenderJob) -> None:
        with self.db.Session.begin() as session:
            row = session.get(JobRow, job.job_id)
            if row is None:
                raise KeyError(job.job_id)
            row.state = job.state.value
            row.attempt = job.attempt
            row.max_attempts = job.max_attempts
            row.failure_code = job.failure_code.value if job.failure_code else None
            row.error_detail = job.error_detail
            row.started_at = job.started_at
            row.finished_at = job.finished_at
            row.output_artifact_ids_json = json.dumps(job.output_artifact_ids)
            row.payload_json = json.dumps(job.payload, ensure_ascii=False)

    def get(self, job_id: str) -> RenderJob:
        with self.db.Session() as session:
            row = session.get(JobRow, job_id)
            if row is None:
                raise KeyError(job_id)
            return self._to_job(row)

    def list_project(self, project_id: str) -> list[RenderJob]:
        with self.db.Session() as session:
            rows = session.scalars(
                select(JobRow).where(JobRow.project_id == project_id).order_by(JobRow.queued_at)
            ).all()
            return [self._to_job(r) for r in rows]

    def append_attempt(self, attempt: JobAttempt) -> None:
        with self.db.Session.begin() as session:
            session.add(
                JobAttemptRow(
                    attempt_id=attempt.attempt_id,
                    job_id=attempt.job_id,
                    attempt_number=attempt.attempt_number,
                    state=attempt.state.value,
                    worker_id=attempt.worker_id,
                    failure_code=attempt.failure_code.value if attempt.failure_code else None,
                    error_detail=attempt.error_detail,
                    started_at=attempt.started_at,
                    finished_at=attempt.finished_at,
                    metadata_json=json.dumps(attempt.metadata, ensure_ascii=False),
                )
            )


class AssetRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def save(self, project_id: str, asset: AssetRecord) -> None:
        with self.db.Session.begin() as session:
            row = session.get(AssetRow, asset.asset_id)
            if row is None:
                row = AssetRow(asset_id=asset.asset_id, project_id=project_id)
                session.add(row)
            elif row.project_id != project_id:
                raise ValueError(f"Asset {asset.asset_id} belongs to another project")
            row.asset_type = asset.asset_type
            row.version = asset.version
            row.rights_status = asset.rights_status.value
            row.content_hash = asset.content_hash
            row.record_json = asset.model_dump_json()

    def get(self, asset_id: str) -> AssetRecord:
        with self.db.Session() as session:
            row = session.get(AssetRow, asset_id)
            if row is None:
                raise KeyError(asset_id)
            return AssetRecord.model_validate_json(row.record_json)

    def list_project(self, project_id: str) -> list[AssetRecord]:
        with self.db.Session() as session:
            rows = session.scalars(
                select(AssetRow).where(AssetRow.project_id == project_id).order_by(AssetRow.asset_type, AssetRow.asset_id)
            ).all()
            return [AssetRecord.model_validate_json(r.record_json) for r in rows]
