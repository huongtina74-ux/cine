"""CINE input handoff must remain pending until a real source is reviewed."""
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("cf_audio_handoff_v1",ROOT/"tools/cf_audio_handoff.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class CINEHandoffTests(unittest.TestCase):
    def test_wrong_explicit_afanta_path_cannot_be_silently_accepted(self):
        with tempfile.TemporaryDirectory() as t:
            with mock.patch.dict(os.environ,{"AFANTA_AUDIO_ROOT":t}):
                with self.assertRaisesRegex(FileNotFoundError,"EXPLICIT_PATH_INVALID"):
                    mod.locate_afanta_root()

    def test_no_duplicate_data_or_fake_verification_on_template(self):
        with tempfile.TemporaryDirectory() as t:
            cine=Path(t)/"cine"
            (cine/"config/audio").mkdir(parents=True)
            (cine/"config/audio/branch_registry_v1.json").write_bytes(
                (ROOT/"config/audio/branch_registry_v1.json").read_bytes())
            slug="afanta_history_sleep_pilot"
            doc=mod.run("template",slug,cine_root=cine)
            self.assertIn("PENDING",doc["status"])
            self.assertTrue(Path(doc["manifest_path"]).is_file())
            self.assertFalse(Path(doc["expected_source_path"]).is_file())
            self.assertFalse(Path(doc["expected_review_evidence_path"]).is_file())
            with self.assertRaises(FileExistsError):
                mod.run("template",slug,cine_root=cine)

    def test_unreviewed_cine_handoff_cannot_be_called_approved(self):
        with tempfile.TemporaryDirectory() as t:
            cine=Path(t)/"cine"
            (cine/"config/audio").mkdir(parents=True)
            (cine/"config/audio/branch_registry_v1.json").write_bytes(
                (ROOT/"config/audio/branch_registry_v1.json").read_bytes())
            slug="afanta_cosmos_sleep_pilot"
            mod.run("template",slug,cine_root=cine)
            audit=mod.run("check",slug,cine_root=cine)
            self.assertIn("HOLD",audit["status"])
            self.assertTrue(audit["issues"])
            self.assertTrue(audit["not_youtube_or_copyright_certification"])

if __name__=="__main__":
    unittest.main()
