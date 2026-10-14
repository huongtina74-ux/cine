"""v214: a verified reference document is not a deployable technology."""
import json
from pathlib import Path

from cinefactory.studio.technology_radar_v210 import load_technology_radar

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "config" / "technology" / "professional_studio_research_v214.json"


def test_professional_studio_rnd_backlog_preserves_96_registry():
    document = json.loads(FILE.read_text(encoding="utf-8"))
    base = load_technology_radar()
    assert document["schema"] == "cine.technology.professional_studio_research.v214"
    assert document["baseline_registry_preserved"] is True
    assert document["baseline_registry_count"] == len(base["items"]) == 96
    assert document["items_count"] == len(document["items"]) >= 12
    assert document["research_only"] is True
    assert document["automatic_install"] is False
    assert document["paid_api_calls"] is False
    assert document["license_or_runtime_certification"] is False
    ids = [item["id"] for item in document["items"]]
    assert len(ids) == len(set(ids))
    assert set(ids) & {item["id"] for item in base["items"]} == set()
    for item in document["items"]:
        assert item["priority"] in {"P0", "P1", "RND", "HOLD"}
        assert item["url"].startswith("https://")
        assert item["status"] != "PRODUCTION_APPROVED"
        assert len(item["caveat"]) >= 20


def test_licensed_depth_weights_not_promoted():
    data = json.loads(FILE.read_text(encoding="utf-8"))
    items = {row["id"]: row for row in data["items"]}
    assert items["depth_anything_v2_base_large"]["priority"] == "HOLD"
    assert items["depth_anything_v2_base_large"]["status"] == "SOURCE_VERIFIED_LICENSE_RESTRICTED"
    assert "CC-BY-NC" in items["depth_anything_v2_base_large"]["caveat"]
