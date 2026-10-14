"""Daily P1 orchestration of Company's SINGLE canonical discovery runner.

Fail closed: blocked/partial runs never become qualified niche results.
No second collector; each run preserves manifests and hashes for audit.
"""
from __future__ import annotations
import csv
import hashlib
import json
import os
import re
import signal
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from .core import _write_json

REPORT_ITEMS = (
    "run_manifest.yaml", "artifact_index.csv", "evidence_table.csv",
    "processed/market_coverage_matrix.csv",
    "processed/owner_channel_candidate_shortlist.csv",
    "processed/company_channel_output_gate.csv",
    "processed/dual_lane_complete_register.csv",
    "processed/lane_a_keyword_channel_evidence.csv",
    "processed/lane_b_independent_channel_opportunities.csv",
    "reports/discovery_run_decision_packet.md",
    "reports/parallel_niche_discovery_master_report.md",
    "processed/channel_snapshot_official_api.csv",
    "processed/fresh_video_observations_clean_official_api.csv",
    "raw/official_api_integrated_scan.json",
    "raw/lane_b_broad_market_surface.json",
    "raw/lane_b_age_1_90_catalogs.json",
    "cine_p1_normalized/native_adapter_manifest.json",
    "cine_p1_normalized/niche_radar_channel_snapshot.csv",
    "cine_p1_normalized/niche_radar_video_snapshot.csv",
)
MAX_ARCHIVE_ITEM_BYTES = 100 * 1024 * 1024
ALLOWED_RUN_STATUSES = {"COMPLETE", "BLOCKED"}
ACCEPTABLE_VERDICTS = {"QUALIFIED_FOR_HUMAN_REVIEW", "WATCHLIST_ONLY", "NO_QUALIFIED_NICHE_FOUND"}
MANDATORY_SNAPSHOT = {
    "run_manifest.yaml", "artifact_index.csv", "evidence_table.csv",
    "processed/market_coverage_matrix.csv",
    "reports/discovery_run_decision_packet.md",
}


def _sha(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _read_yaml(path: Path) -> dict:
    import yaml
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _coverage(run_dir: Path) -> dict:
    f = run_dir / "processed/market_coverage_matrix.csv"
    if not f.is_file():
        return {"queries_due": None, "queries_complete": None, "status": "NOT_COLLECTED"}
    with f.open(encoding="utf-8-sig", newline="") as stream:
        records = list(csv.DictReader(stream))
    done = sum(row.get("coverage_status") == "COMPLETE" for row in records)
    return {"queries_due": len(records), "queries_complete": done,
            "status": "COMPLETE" if records and done == len(records) else "PARTIAL"}


def _health_snapshot(run_dir: Path, snapshot_dir: Path) -> tuple[list[dict], list[str]]:
    files, missing = [], []
    for relative in REPORT_ITEMS:
        source = run_dir / relative
        if not source.is_file():
            missing.append(relative)
            continue
        if source.stat().st_size > MAX_ARCHIVE_ITEM_BYTES:
            missing.append(f"{relative}:too_large_to_archive")
            continue
        target = snapshot_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        before = _sha(source)
        shutil.copy2(source, target)
        after = _sha(target)
        if before != after or before != _sha(source):
            target.unlink(missing_ok=True)
            missing.append(f"{relative}:changed_during_archival")
            continue
        files.append({"relative_path": relative, "sha256": after,
                      "bytes": target.stat().st_size, "source_sha256": before})
    return files, missing


def _run_with_timeout_tree(argv: list[str], cwd: Path, timeout_seconds: float) -> tuple[str, str, int, bool]:
    """Stop the whole scanner process tree, not only its parent, on timeout."""
    opts = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
    proc = subprocess.Popen(
        argv, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding="utf-8", errors="replace", **opts
    )
    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        if os.name == "nt":
            try:
                subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                               check=False, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=20)
            except (OSError, subprocess.TimeoutExpired):
                proc.kill()
        else:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except (OSError, ProcessLookupError):
                proc.kill()
        try:
            stdout, stderr = proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
        stderr = (stderr or "") + "\nCANONICAL_RUNNER_TIMEOUT_TREE_TERMINATED"
    return stdout or "", stderr or "", -1 if timed_out else proc.returncode, timed_out


def _day_string(day: str | None) -> str:
    if day is None:
        # The host-local day is used only for the job partition; the report stores UTC timestamps.
        return datetime.now().astimezone().date().isoformat()
    date.fromisoformat(day)
    return day


def daily_preflight(company_root: str | Path) -> dict:
    root = Path(company_root).resolve(strict=True)
    runner = root / "scripts" / "run_complete_niche_discovery.py"
    if not runner.is_file():
        raise FileNotFoundError("Canonical Company YouTube runner missing")
    api_key_present = any(os.getenv(k, "").strip() for k in
                          ("YOUTUBE_DATA_API_KEY", "YOUTUBE_API_KEY", "GOOGLE_API_KEY"))
    return {
        "company_root": str(root), "runner": str(runner),
        "api_key_present": api_key_present,
        "official_strict_verification_available": api_key_present,
        "mode": "auto",
        "blocked_if_no_official_proof": not api_key_present,
        "market": "US", "language": "en",
        "limitations": [
            "Canonical runner currently locked to US/en",
            "No API key means the official channel age/catalog proof is blocked",
            "Company native output does not yet guarantee niche_radar_channel/video_snapshot tables for Market Bridge",
        ],
    }


def execute_daily(company_root: str | Path, daily_root: str | Path, *, day: str | None = None,
                  retry: bool = False, dry_run: bool = False, max_seconds: int = 5400,
                  runner_extra: list[str] | None = None) -> dict:
    if not 30 <= max_seconds <= 21600:
        raise ValueError("Runner timeout must be 30..21600s")
    if runner_extra:
        switches = {"--skip-recursive-expansion", "--skip-independent-lane-b"}
        numeric = [part for part in runner_extra if part not in switches]
        if len(numeric) != len(runner_extra) - sum(item in switches for item in runner_extra):
            raise ValueError("Malformed canonical flag list")
        if len(set(item for item in runner_extra if item in switches)) != sum(item in switches for item in runner_extra):
            raise ValueError("Duplicate scan switches forbidden")
        allowed = {"--queries-per-market", "--max-queries-per-window",
                   "--max-results-per-query", "--quota-budget",
                   "--catalog-videos", "--max-catalog-channels",
                   "--dynamic-root-limit", "--dynamic-suffix-limit",
                   "--lane-b-subclusters-per-market", "--lane-b-max-results",
                   "--max-youtubejs-about-channels", "--lane-b-catalog-videos",
                   "--recursive-parent-limit", "--recursive-children-per-parent",
                   "--recursive-batch-size", "--recursive-max-catalog-channels"}
        if (len(numeric) % 2 or any(
            numeric[i] not in allowed or not numeric[i + 1].isdigit()
            for i in range(0, len(numeric), 2)
        )):
            raise ValueError("Only explicitly permitted numeric scan budget overrides")
    preflight = daily_preflight(company_root)
    root = Path(preflight["company_root"])
    state = Path(daily_root).resolve()
    period = _day_string(day)
    day_root = state / "daily" / period
    day_root.mkdir(parents=True, exist_ok=True)
    lock = day_root / "run.lock"
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise RuntimeError("A daily attempt is already running or lock recovery needs inspection") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as writer:
        writer.write(json.dumps({"started_at_utc": datetime.now(timezone.utc).isoformat(),
                                 "host_pid": os.getpid(), "day": period}))
    try:
        existing = sorted(day_root.glob("attempt_*/daily_report.json"))
        if existing and not retry:
            raise FileExistsError("Daily report already exists; use --retry to preserve an additional attempt")
        index = max((int(path.parent.name.split("_")[-1]) for path in existing), default=0) + 1
        if index > 25:
            raise RuntimeError("Too many attempts, inspect scanner failures")
        attempt = day_root / f"attempt_{index:03d}"
        if attempt.exists():
            raise FileExistsError("An earlier attempt exists without terminal report: manual recovery required")
        attempt.mkdir()
        run_slug = f"cine_p1_daily_{period.replace('-', '')}_{index:03d}"
        source_run = root / "research" / "markets" / run_slug
        if source_run.exists():
            raise FileExistsError("Canonical scanner slug already used; refusing to overwrite data")
        run_id = f"CINE-P1-{period.replace('-', '')}-{index:03d}"
        argv = [sys.executable, str(preflight["runner"]), "--mode", "auto",
                "--run-slug", run_slug, "--run-id", run_id,
                "--channel-age-min", "0", "--channel-age-max", "30",
                "--required-qualified-niches", "1", "--allow-watchlist-output"]
        if dry_run:
            argv.append("--dry-run")
        if runner_extra:
            argv.extend(runner_extra)
        start = datetime.now(timezone.utc)
        stdout, stderr, code, timed_out = _run_with_timeout_tree(argv, root, max_seconds)
        # log tails only, do not store API keys (keys are never passed in argv)
        (attempt / "runner.stdout.log").write_text(stdout[-500_000:], encoding="utf-8")
        (attempt / "runner.stderr.log").write_text(stderr[-150_000:], encoding="utf-8")
        completed_at = datetime.now(timezone.utc).isoformat()
        native = {"schema": "cine.research.native_adapter.v1", "status": "NOT_RUN"}
        native_error = None
        if source_run.exists() and not dry_run:
            from .native_adapter import normalize_company_run
            try:
                native = normalize_company_run(source_run, observed_at=completed_at)
            except (OSError, ValueError, TypeError, KeyError) as exc:
                native_error = f"Native schema adapter blocked: {type(exc).__name__}: {exc}"
                native = {"schema": "cine.research.native_adapter.v1", "status": "ADAPTER_FAILED"}
        manifest_file = source_run / "run_manifest.yaml"
        manifest = _read_yaml(manifest_file) if manifest_file.is_file() else {}
        raw_status = manifest.get("run_status", "UNKNOWN")
        raw_verdict = manifest.get("decision_packet", {}).get("final_verdict", "UNKNOWN")
        if dry_run:
            status = "DRY_RUN"
        elif (code == 0 and raw_status == "COMPLETE"
              and raw_verdict in ACCEPTABLE_VERDICTS):
            status = "COMPLETE"
        elif source_run.exists():
            status = "BLOCKED" if raw_status == "BLOCKED" else "PARTIAL"
        else:
            status = "FAILED"
        files, missing = _health_snapshot(source_run, attempt / "snapshot") if source_run.exists() else ([], list(REPORT_ITEMS))
        coverage = _coverage(source_run)
        gaps = list(manifest.get("coverage_gaps", []))
        if not preflight["api_key_present"]:
            gaps.append("Official API key is unavailable: strict public channel verification cannot be certified")
            if status == "COMPLETE":
                status = "PARTIAL"
        if timed_out:
            gaps.append("TIMEOUT: canonical scanner process tree was terminated to avoid orphan collectors")
            if status == "COMPLETE":
                status = "PARTIAL"
        if native_error:
            gaps.append(native_error)
            if status == "COMPLETE":
                status = "PARTIAL"
        if status == "COMPLETE" and native.get("status") != "SCHEMA_READY_TOPIC_REVIEW_REQUIRED":
            status = "PARTIAL"
            gaps.append("Company native channel/video snapshot is missing, so unified intelligence cannot consume this run")
        if status == "COMPLETE" and (
            not MANDATORY_SNAPSHOT.isdisjoint(set(missing)) or coverage["status"] != "COMPLETE"
        ):
            status = "PARTIAL"
            gaps.append("Mandatory snapshot or keyword coverage incomplete")
        # Audit exact official channel/video IDs only after the original scan terminates
        # and its own manifest is COMPLETE. A crashed checkpoint is never promoted.
        breakout = {"schema": "cine.research.official_breakout_audit.v1", "state": "NOT_EVALUATED"}
        official_raw = source_run / "raw" / "official_api_integrated_scan.json"
        if status == "COMPLETE" and official_raw.is_file():
            from .breakout_proof import audit_official_artifact
            try:
                breakout = audit_official_artifact(
                    official_raw, attempt / "official_breakout_audit.json"
                )
            except (ValueError, TypeError, KeyError, OSError) as exc:
                status = "PARTIAL"
                gaps.append(f"Official breakout audit failed: {type(exc).__name__}: {exc}")
                breakout = {"schema": "cine.research.official_breakout_audit.v1", "state": "AUDIT_FAILED"}
        # Reuse the canonical youtubei.js lanes. Even on a partial scan their
        # public evidence can be PRESCREENED, never promoted or called verified.
        public = {"schema":"cine.research.public_prescreen.v1", "state":"NOT_EVALUATED"}
        if source_run.exists() and not dry_run:
            from .public_prescreen import prescreen_company_public
            try:
                public = prescreen_company_public(
                    root, source_run, attempt / "public_prescreen.json",
                    as_of=completed_at, max_candidates=20)
            except (OSError, ValueError, TypeError, KeyError) as exc:
                public={"schema":"cine.research.public_prescreen.v1","state":"PRESCREEN_FAILED"}
                gaps.append("Public prescreen failed: " + type(exc).__name__)
        report = {
            "schema": "cine.research.daily_run.v1", "day": period,
            "run_id": run_id, "run_slug": run_slug,
            "attempt": index, "state": status, "dry_run": dry_run,
            "started_at": start.isoformat(),
            "completed_at": completed_at,
            "canonical_runner_exit_code": code,
            "runner_timed_out": timed_out,
            "canonical_run_dir": str(source_run), "preflight": preflight,
            "canonical_run_status": raw_status, "canonical_verdict": raw_verdict,
            "qualified_niches": None,
            "canonical_legacy_candidate_count": manifest.get("decision_packet", {}).get("candidate_count") if status == "COMPLETE" else None,
            "coverage": coverage, "gaps": gaps,
            "missing_snapshot_items": missing, "snapshot": files,
            "strict_0_30_two_1m_niche_gate": "CHANNEL_WITNESSES_ONLY_NOT_FULL_NICHE" if
                breakout["state"] == "CHANNEL_BREAKOUT_EVIDENCE_PRESENT" else "NOT_EVALUATED_WITH_FULL_PROOF",
            "public_prescreen": {
                "state":public["state"],
                "candidate_count":len(public.get("candidates",[])),
                "official_verification_queue_count":len(public.get("requests_for_official_verification",[])),
                "path":str(attempt / "public_prescreen.json") if
                    public["state"] not in ("NOT_EVALUATED","NOT_COLLECTED","PRESCREEN_FAILED")
                    else None,
                "auto_called_official_api":False,
            },
            "channel_breakout_audit": {
                "state": breakout["state"],
                "witness_count": len(breakout.get("witness_channels", [])),
                "report_path": str(attempt / "official_breakout_audit.json") if
                    breakout["state"] in ("CHANNEL_BREAKOUT_EVIDENCE_PRESENT", "NO_CONFIRMED_CHANNEL_BREAKOUT")
                    else None,
            },
            "owner_review_eligible": False,
            "canonical_owner_review_eligible": status == "COMPLETE" and raw_verdict == "QUALIFIED_FOR_HUMAN_REVIEW",
            "bridge_ready": False,
            "native_adapter": native,
            "bridge_reason": "Native schema can be imported after manual topic fit and all five strict niche gates are independently reviewed",
            "no_fabricated_niches": True,
        }
        _write_json(attempt / "daily_report.json", report)
        latest = {"schema": "cine.research.daily_index.v1", "day": period,
                  "latest_attempt": index, "report": str(attempt / "daily_report.json"),
                  "report_relative": (attempt / "daily_report.json").relative_to(state).as_posix(),
                  "state": status, "updated_at": report["completed_at"]}
        _write_json(day_root / "latest.json", latest)
        _write_json(state / "latest_health.json", latest)
        return report
    finally:
        lock.unlink(missing_ok=True)


def daily_health(daily_root: str | Path, *, max_age_hours: int = 36,
                 now: str | None = None) -> dict:
    if max_age_hours < 1:
        raise ValueError("max_age_hours must be positive")
    path = Path(daily_root) / "latest_health.json"
    if not path.is_file():
        return {"status": "ALERT_NEVER_RAN", "reason": "No daily report yet"}
    rec = json.loads(path.read_text(encoding="utf-8"))
    if rec.get("report_relative"):
        root = Path(daily_root).resolve()
        report = (root / rec["report_relative"]).resolve()
        if not report.is_relative_to(root) or not report.is_file():
            return {"status": "ALERT_MISSING_REPORT", "latest": rec}
    as_of = datetime.fromisoformat(now.replace("Z", "+00:00")) if now else datetime.now(timezone.utc)
    time = datetime.fromisoformat(rec["updated_at"].replace("Z", "+00:00"))
    if as_of.tzinfo is None or time.tzinfo is None:
        raise ValueError("Health timestamps require timezone")
    elapsed = (as_of - time).total_seconds() / 3600
    if elapsed < 0 or elapsed > max_age_hours:
        return {"status": "ALERT_STALE", "hours_since_last_report": round(elapsed, 2), "latest": rec}
    if rec["state"] != "COMPLETE":
        return {"status": "ALERT_INCOMPLETE", "latest": rec, "hours_since_last_report": round(elapsed, 2)}
    return {"status": "HEALTHY", "latest": rec, "hours_since_last_report": round(elapsed, 2)}
