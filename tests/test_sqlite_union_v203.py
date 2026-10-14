"""Verify lossless legacy SQLite union does not overwrite canonical evidence."""
import sqlite3
import pytest
from scripts.migrate_legacy_sqlite_once import build_merged, assert_union


def db(rows, schema="CREATE TABLE events (event_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"):
    connection = sqlite3.connect(":memory:")
    connection.execute(schema)
    if rows:
        connection.executemany("INSERT INTO events (event_id, payload) VALUES (?,?)", rows)
    connection.commit()
    return connection


def test_union_adds_missing_primary_keys_without_overwriting():
    canonical = db([("A", "canonical")])
    legacy = db([("A", "canonical"), ("B", "legacy")])
    stage = db([("A", "canonical")])
    try:
        stage.execute("BEGIN IMMEDIATE")
        report = build_merged(canonical, legacy, stage, insert=True)
        stage.commit()
        assert report["events"]["insert_missing"] == 1
        assert report["events"]["existing_identical"] == 1
        assert_union(stage, canonical, legacy, report)
        assert stage.execute("SELECT payload FROM events WHERE event_id='A'").fetchone()[0] == "canonical"
        assert canonical.execute("SELECT count(*) FROM events").fetchone()[0] == 1
    finally:
        canonical.close()
        legacy.close()
        stage.close()


def test_union_rejects_same_primary_key_with_different_data():
    canonical = db([("A", "original")])
    legacy = db([("A", "changed")])
    stage = db([("A", "original")])
    try:
        with pytest.raises(RuntimeError, match="CONFLICTING_PRIMARY_KEY_VALUES"):
            build_merged(canonical, legacy, stage, insert=True)
        assert stage.execute("SELECT payload FROM events WHERE event_id='A'").fetchone()[0] == "original"
    finally:
        canonical.close()
        legacy.close()
        stage.close()


def test_union_rejects_schema_drift():
    canonical = db([("A", "original")])
    legacy = db([("A", "original")], schema="CREATE TABLE events (event_id TEXT PRIMARY KEY, payload TEXT NOT NULL, extra TEXT)")
    stage = db([("A", "original")])
    try:
        with pytest.raises(RuntimeError, match="TABLE_SCHEMA_DIFFERENCE"):
            build_merged(canonical, legacy, stage, insert=True)
    finally:
        canonical.close()
        legacy.close()
        stage.close()
