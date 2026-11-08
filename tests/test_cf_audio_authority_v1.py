"""CINE Audio sources are canonical; Afanta retains release/QC control."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
def load(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class SourceOfTruthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.branches=load("cf_audio_branches_authority_test","tools/cf_audio_branches.py")
        cls.wrapper=load("cf_audio_authority_test","tools/cf_audio_authority.py")

    def test_wrong_explicit_afanta_path_cannot_be_silently_accepted(self):
        with tempfile.TemporaryDirectory() as t:
            with mock.patch.dict(os.environ,{"AFANTA_AUDIO_ROOT":t}):
                with self.assertRaisesRegex(FileNotFoundError,"EXPLICIT_PATH_INVALID"):
                    self.wrapper.locate_afanta_root()

    def test_branch_strategy_has_one_canonical_json_source(self):
        src=json.loads((ROOT/"config/audio/branch_registry_v1.json").read_text(encoding="utf8"))
        self.assertEqual(self.branches.portfolio(),src)
        self.assertEqual(self.branches.BRANCHES,src["branches"])
        self.assertEqual(self.branches.STAGES,src["common_stage_ids"])
        self.assertEqual(self.branches.canonical(src),
                         (ROOT/"config/audio/branch_registry_v1.json").read_bytes())

    def test_all_scope_identifiers_have_one_owner_only(self):
        index=json.loads((ROOT/"config/audio/authority_index_v1.json").read_text(encoding="utf8"))
        self.assertEqual(index["schema"],"cine-afanta-audio-rule-authority-v1")
        rows=index["canonical_rules"]
        self.assertEqual(len({x["scope_id"] for x in rows}),len(rows))
        self.assertEqual(len({x["rule_id"] for x in rows}),len(rows))
        self.assertEqual(len({x["owner"] for x in rows}),2)
        self.assertFalse(index["allow_unapproved_auto_publication"])
        self.assertFalse(index["copy_rule_text_to_other_repository"])

    def test_thin_cine_wrapper_cannot_claim_a_missing_afanta_qc(self):
        with tempfile.TemporaryDirectory() as t:
            out=self.wrapper.audit(cine_root=ROOT,afanta_root=t,require_lock=True)
            self.assertEqual(out["status"],"AUDIO_RULE_AUTHORITY_HOLD")
            self.assertIn("AFANTA_QC_CANONICAL_VERIFIER_MISSING",out["issues"])
            self.assertFalse(out["can_route_production"])

    def test_runtime_reloads_single_canonical_strategy_on_each_read(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"registry.json"
            original=self.branches.portfolio()
            p.write_text(json.dumps(original),encoding="utf8")
            with mock.patch.object(self.branches,"PORTFOLIO_SOURCE",p):
                self.assertEqual(self.branches.portfolio(),original)
                updated=json.loads(p.read_text(encoding="utf8"))
                updated["branches"][0]["audience"]="Changed only in canonical registry"
                p.write_text(json.dumps(updated),encoding="utf8")
                self.assertEqual(self.branches.portfolio()["branches"][0]["audience"],
                                 "Changed only in canonical registry")

if __name__=="__main__":unittest.main()
