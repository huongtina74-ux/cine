"""Lossless, fail-closed one-time reconciliation of the two CineFactory SQLite ledgers.

Run without --apply to validate a staged union and immutable before snapshots.
Only --apply can insert; never updates or deletes existing source rows.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / ".tools" / "cleanup_audit"
BACKUPS = ROOT.parent / ".tools" / "cleanup_archive"


def open_db(path: Path, readonly: bool = True):
    if readonly:
        con = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=20)
    else:
        con = sqlite3.connect(str(path), timeout=20)
    con.execute("PRAGMA busy_timeout=20000")
    return con


def snapshot(source: Path, dest: Path) -> None:
    if dest.exists():
        raise RuntimeError(f"REFUSE_TO_OVERWRITE_SNAPSHOT:{dest}")
    source_con = open_db(source)
    dest_con = open_db(dest, readonly=False)
    try:
        source_con.backup(dest_con)
    finally:
        source_con.close()
        dest_con.close()


def tables(con: sqlite3.Connection) -> list[str]:
    return [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name"
    )]


def table_info(con: sqlite3.Connection, table: str):
    return con.execute(f'PRAGMA table_info("{table}")').fetchall()


def data(con: sqlite3.Connection, table: str):
    meta = table_info(con, table)
    pk = [x[1] for x in sorted(meta, key=lambda x: x[5]) if x[5]]
    cols = [x[1] for x in meta]
    if not pk:
        raise RuntimeError(f"TABLE_WITHOUT_EXPLICIT_PRIMARY_KEY:{table}")
    out = {}
    for row in con.execute(f'SELECT * FROM "{table}"'):
        fields = dict(zip(cols, row))
        key = tuple(fields[c] for c in pk)
        if key in out:
            raise RuntimeError(f"DUPLICATE_PRIMARY_KEY:{table}")
        out[key] = tuple(row)
    return cols, pk, out


def build_merged(source_con, legacy_con, dest_con, *, insert: bool):
    if tables(source_con) != tables(legacy_con):
        raise RuntimeError("SCHEMA_TABLE_MISMATCH")
    summaries = {}
    for table in tables(source_con):
        if table_info(source_con, table) != table_info(legacy_con, table):
            raise RuntimeError(f"TABLE_SCHEMA_DIFFERENCE:{table}")
        cols, pk, primary = data(source_con, table)
        _, _, legacy = data(legacy_con, table)
        overlap = primary.keys() & legacy.keys()
        conflicting = [k for k in overlap if primary[k] != legacy[k]]
        if conflicting:
            raise RuntimeError(f"CONFLICTING_PRIMARY_KEY_VALUES:{table}:{len(conflicting)}")
        missing = set(legacy) - set(primary)
        if insert:
            column_sql = ", ".join('"' + c.replace('"', '""') + '"' for c in cols)
            markers = ",".join("?" for _ in cols)
            sql = f'INSERT INTO "{table}" ({column_sql}) VALUES ({markers})'
            for k in sorted(missing, key=repr):
                dest_con.execute(sql, legacy[k])
        summaries[table] = {
            "canonical": len(primary), "legacy": len(legacy),
            "existing_identical": len(overlap), "insert_missing": len(missing),
            "expected_total": len(primary) + len(missing),
            "pk": pk,
        }
    return summaries


def assert_union(stage_con, primary_con, legacy_con, summaries):
    if stage_con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise RuntimeError("SQLITE_INTEGRITY_CHECK_FAILED")
    if stage_con.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise RuntimeError("FOREIGN_KEY_VIOLATIONS")
    for table, summary in summaries.items():
        _, _, stage = data(stage_con, table)
        _, _, primary = data(primary_con, table)
        _, _, legacy = data(legacy_con, table)
        assert len(stage) == summary["expected_total"], table
        assert all(stage[k] == v for k, v in primary.items()), table
        assert all(stage[k] == v for k, v in legacy.items()), table


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Insert into canonical ledgers after staged proof")
    args = parser.parse_args()
    AUDIT.mkdir(parents=True, exist_ok=True)
    BACKUPS.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    outcome = {}
    for name in ("cinefactory.db", "turbo.db"):
        live_path = ROOT / "data" / name
        legacy_path = ROOT / ".tools" / "legacy_conflicts_20261010" / "data" / name
        assert live_path.is_file() and legacy_path.is_file()
        canon_backup = BACKUPS / f"{stamp}_{name}.before_union.sqlite"
        legacy_backup = BACKUPS / f"{stamp}_{name}.legacy_snapshot.sqlite"
        staged = AUDIT / f"{stamp}_{name}.proposed_union.sqlite"
        snapshot(live_path, canon_backup)
        snapshot(legacy_path, legacy_backup)
        shutil.copy2(canon_backup, staged)
        canonical = open_db(canon_backup)
        legacy = open_db(legacy_backup)
        stage = open_db(staged, readonly=False)
        try:
            stage.execute("BEGIN IMMEDIATE")
            summaries = build_merged(canonical, legacy, stage, insert=True)
            stage.commit()
            assert_union(stage, canonical, legacy, summaries)
        finally:
            stage.close()
        status = "DRY_RUN_VERIFIED"
        if args.apply:
            current = open_db(live_path, readonly=False)
            try:
                current.execute("BEGIN IMMEDIATE")
                # Require live data to be identical to the freshly backed up state.
                for table in tables(canonical):
                    _, _, before = data(canonical, table)
                    _, _, now = data(current, table)
                    if before != now:
                        raise RuntimeError(f"LIVE_DATABASE_CHANGED_DURING_MIGRATION:{name}:{table}")
                build_merged(canonical, legacy, current, insert=True)
                assert_union(current, canonical, legacy, summaries)
                current.commit()
                status = "APPLIED_UNION_VERIFIED"
            except Exception:
                current.rollback()
                raise
            finally:
                current.close()
        outcome[name] = {
            "status": status, "tables": summaries,
            "canonical_snapshot": str(canon_backup),
            "legacy_snapshot": str(legacy_backup),
            "candidate": str(staged),
        }
        canonical.close()
        legacy.close()
        print(f"{name}: {status}; "
              + ", ".join(f"{t}: +{v['insert_missing']}" for t, v in summaries.items()), flush=True)
    output = AUDIT / f"{stamp}_db_union_report.json"
    output.write_text(json.dumps(outcome, ensure_ascii=False, indent=2), encoding="utf8")
    print("MIGRATION_REPORT", output, flush=True)


if __name__ == "__main__":
    main()
