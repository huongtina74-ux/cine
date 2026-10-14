from pathlib import Path

from cinefactory.domain.enums import JobState
from cinefactory.domain.models import AuditEvent, ProjectRecord, ProjectSpec, RenderJob
from cinefactory.storage.database import AuditLogRepository, Database, JobLedgerRepository, SqlProjectRepository


def make_db(tmp_path: Path) -> Database:
    db = Database(f"sqlite:///{tmp_path / 'test.db'}")
    db.create_schema()
    return db


def test_sql_project_repository_round_trip(tmp_path):
    db = make_db(tmp_path)
    repo = SqlProjectRepository(db)
    record = ProjectRecord(spec=ProjectSpec(prompt="A quiet family drama"))
    repo.save(record)
    loaded = repo.get(record.spec.project_id)
    assert loaded.spec.prompt == "A quiet family drama"
    assert loaded.state == record.state


def test_audit_is_append_only_api(tmp_path):
    db = make_db(tmp_path)
    audit = AuditLogRepository(db)
    audit.append(AuditEvent(project_id="P1", event_type="X", actor="test", entity_type="project", entity_id="P1"))
    audit.append(AuditEvent(project_id="P1", event_type="Y", actor="test", entity_type="project", entity_id="P1"))
    events = audit.list_for_project("P1")
    assert [e.event_type for e in events] == ["X", "Y"]
    assert not hasattr(audit, "delete")


def test_job_idempotency(tmp_path):
    db = make_db(tmp_path)
    ledger = JobLedgerRepository(db)
    job = RenderJob(
        project_id="P1",
        shot_id="S1",
        job_type="VIDEO",
        executor_id="local.mock",
        workflow_id="mock",
        workflow_version="1",
        dependency_hash="abc",
    )
    first, created1 = ledger.create_or_get(job)
    duplicate = RenderJob(
        project_id="P1",
        shot_id="S1",
        job_type="VIDEO",
        executor_id="local.mock",
        workflow_id="mock",
        workflow_version="1",
        dependency_hash="abc",
    )
    second, created2 = ledger.create_or_get(duplicate)
    assert created1 is True
    assert created2 is False
    assert first.job_id == second.job_id
    assert second.state == JobState.QUEUED


def test_asset_repository_round_trip(tmp_path):
    from cinefactory.domain.enums import RightsStatus
    from cinefactory.domain.models import AssetRecord, RightsEnvelope
    from cinefactory.storage.database import AssetRepository

    db = make_db(tmp_path)
    assets = AssetRepository(db)
    asset = AssetRecord(
        asset_id="CHAR_C01_REF_V1",
        asset_type="character_reference",
        origin="self_generated_local",
        rights_status=RightsStatus.GREEN,
        rights=RightsEnvelope(commercial_use=True),
        content_hash="deadbeef",
    )
    assets.save("P1", asset)
    loaded = assets.get(asset.asset_id)
    assert loaded.rights_status == RightsStatus.GREEN
    assert loaded.rights.commercial_use is True
