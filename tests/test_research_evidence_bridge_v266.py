"""v266 handoff: original source hashes, project binding and G02 fail-closed."""
import json
import pytest
from cinefactory.studio.research_evidence_bridge_v266 import ROOT,build,load,SOURCES
from cinefactory.studio.company_handlers import FilmCompanyHandlers,FilmHandlerConfig
from cinefactory.cli import context

def test_v266_research_handoff_never_grants_g02_or_publish(tmp_path):
 # Use real read-only source files, isolated project dir, no production assets copied.
 for rel in SOURCES.values():
  orig=ROOT/rel
  target=tmp_path/rel
  target.parent.mkdir(parents=True,exist_ok=True)
  target.write_bytes(orig.read_bytes())
 data=build(tmp_path,"TEST_V266_SCOPE",write=True)
 assert data["production_permission"] is False
 assert data["source_approval"] is False
 assert data["g02_status"].startswith("PENDING")
 assert data["competitor_profiles_certified_count"]==0
 assert len(data["source_video_ids_pending_independent_review"])==3
 reloaded=load(tmp_path,"TEST_V266_SCOPE")
 assert reloaded["source_sha256"]==data["source_sha256"]
 assert load(tmp_path,"OTHER_PROJECT") is None
 for s in data["public_candidate_sample"]:
  assert s["is_film_semantically_verified"] is False

def test_v266_research_handoff_detects_source_drift(tmp_path):
 for rel in SOURCES.values():
  target=tmp_path/rel
  target.parent.mkdir(parents=True,exist_ok=True)
  target.write_bytes((ROOT/rel).read_bytes())
 build(tmp_path,"TEST_SCOPE",write=True)
 candidate=tmp_path/SOURCES["public_video_metadata"]
 candidate.write_text(candidate.read_text(encoding="utf8")+" ",encoding="utf8")
 with pytest.raises(ValueError,match="SOURCE_MISMATCH"):
  load(tmp_path,"TEST_SCOPE")

def test_v266_cannot_forge_g02_by_editing_handoff(tmp_path):
 for rel in SOURCES.values():
  target=tmp_path/rel
  target.parent.mkdir(parents=True,exist_ok=True)
  target.write_bytes((ROOT/rel).read_bytes())
 build(tmp_path,"TEST_SCOPE",write=True)
 p=tmp_path/"data/projects/TEST_SCOPE/company/research_handoff.json"
 o=json.loads(p.read_text(encoding="utf8"))
 o["g02_status"]="PASS"
 o["production_permission"]=True
 p.write_text(json.dumps(o),encoding="utf8")
 with pytest.raises(ValueError,match="NOT_AUTHORIZED"):
  load(tmp_path,"TEST_SCOPE")

def test_v266_only_registers_g02_handler_when_explicitly_enabled():
 ctx=context()
 default=FilmCompanyHandlers(ctx,config=FilmHandlerConfig())
 enabled=FilmCompanyHandlers(ctx,config=FilmHandlerConfig(enable_research_handoff=True))
 assert default.registry().get("EVIDENCE") is None
 assert enabled.registry().get("EVIDENCE") is not None
