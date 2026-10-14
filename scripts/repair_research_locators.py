from __future__ import annotations
import argparse
import json
from hashlib import sha256
from pathlib import Path


def audit_current_locator(state_root: Path) -> dict:
    state = Path(state_root).resolve()
    index = state / "latest_health.json"
    if not index.is_file():
        return {"status": "NO_LATEST_INDEX"}
    record = json.loads(index.read_text(encoding="utf-8"))
    day = str(record.get("day") or "")
    attempt = int(record.get("latest_attempt") or 0)
    if not day or attempt < 1:
        return {"status": "INDEX_NOT_RELOCATABLE", "index": str(index)}
    relative = f"daily/{day}/attempt_{attempt:03d}/daily_report.json"
    candidate = (state / relative).resolve()
    if not candidate.is_relative_to(state) or not candidate.is_file():
        return {"status": "CANONICAL_REPORT_MISSING", "candidate": str(candidate)}
    report = json.loads(candidate.read_text(encoding="utf-8"))
    if report.get("day") != day or report.get("state") != record.get("state"):
        raise ValueError("CANONICAL_RESEARCH_REPORT_STATE_MISMATCH")
    canonical = str(candidate)
    changed = (record.get("report") != canonical or
               record.get("report_relative") != relative)
    return {
        "status": "REBASE_REQUIRED" if changed else "CURRENT",
        "index": str(index), "canonical": canonical, "relative": relative,
        "historical_locator": record.get("report"),
        "report_sha256": sha256(candidate.read_bytes()).hexdigest(),
    }


def rebase_current_locator(state_root: Path, backup_root: Path) -> dict:
    status = audit_current_locator(state_root)
    if status.get("status") != "REBASE_REQUIRED":
        return status
    index = Path(status["index"])
    current = json.loads(index.read_text(encoding="utf-8"))
    backup = Path(backup_root) / ("latest_health_before_rebase_" +
                                 sha256(index.read_bytes()).hexdigest()[:16] + ".json")
    backup.parent.mkdir(parents=True, exist_ok=True)
    if not backup.exists():
        backup.write_bytes(index.read_bytes())
    else:
        assert backup.read_bytes() == index.read_bytes()
    current["report"] = status["canonical"]
    current["report_relative"] = status["relative"]
    current["historical_report_path"] = status["historical_locator"]
    tmp = index.with_suffix(".tmp")
    if tmp.exists():
        raise FileExistsError(tmp)
    tmp.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    tmp.replace(index)
    if audit_current_locator(state_root)["status"] != "CURRENT":
        raise RuntimeError("REBASE_POSTCONDITION_FAILED")
    status["status"] = "REBASED_CURRENT_WITH_HISTORICAL_BACKUP"
    status["backup"] = str(backup)
    return status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-root", type=Path, required=True)
    ap.add_argument("--backup-root", type=Path)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    if args.apply and args.backup_root is None:
        ap.error("--apply requires --backup-root for immutable evidence preservation")
    status = (
        rebase_current_locator(args.state_root, args.backup_root)
        if args.apply else audit_current_locator(args.state_root)
    )
    print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
