"""Research locator migration is versioned and does not forge old evidence."""
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.repair_research_locators import (
    audit_current_locator, rebase_current_locator,
)
from cinefactory.research_intelligence.daily_research import daily_health


def test_rebase_operational_index_preserves_original_source(tmp_path):
    root = tmp_path / "state"
    report = root / "daily/2026-10-10/attempt_005/daily_report.json"
    report.parent.mkdir(parents=True)
    report.write_text(json.dumps({"day": "2026-10-10", "state": "BLOCKED"}), encoding="utf8")
    before = {
        "day": "2026-10-10", "latest_attempt": 5,
        "report": "C:/deleted/legacy/research/daily_report.json",
        "state": "BLOCKED",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    index = root / "latest_health.json"
    index.write_text(json.dumps(before), encoding="utf8")
    assert audit_current_locator(root)["status"] == "REBASE_REQUIRED"
    fixed = rebase_current_locator(root, tmp_path / "immutable_backup")
    assert fixed["status"] == "REBASED_CURRENT_WITH_HISTORICAL_BACKUP"
    assert Path(fixed["backup"]).is_file()
    assert json.loads(Path(fixed["backup"]).read_text(encoding="utf8")) == before
    assert json.loads(report.read_text(encoding="utf8")) == {"day": "2026-10-10", "state": "BLOCKED"}
    after = json.loads(index.read_text(encoding="utf8"))
    assert Path(after["report"]).resolve() == report.resolve()
    assert after["historical_report_path"] == before["report"]
    assert after["report_relative"] == "daily/2026-10-10/attempt_005/daily_report.json"
    assert daily_health(root)["status"] == "ALERT_INCOMPLETE"
    assert audit_current_locator(root)["status"] == "CURRENT"


def test_health_does_not_silently_accept_missing_canonical_report(tmp_path):
    root = tmp_path / "state"
    root.mkdir()
    (root / "latest_health.json").write_text(json.dumps({
        "report_relative": "daily/missing/file.json",
        "state": "COMPLETE",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }), encoding="utf8")
    assert daily_health(root)["status"] == "ALERT_MISSING_REPORT"
