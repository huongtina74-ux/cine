"""CINE audio portfolio: regression against cross-niche leak and overwrite."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("cf_audio_branches_v1",ROOT/"tools/cf_audio_branches.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class AudioBranchContracts(unittest.TestCase):
    def make_dirs(self,root,afanta):
        research=root/"config/research/per_niche/niches.json"
        research.parent.mkdir(parents=True)
        research.write_text(json.dumps({"niches":[{"id":b["id"]} for b in mod.BRANCHES]}),encoding="utf-8")
        (afanta/"studio_os").mkdir(parents=True)
        (afanta/"studio_os/core.py").write_text("# fixture\n",encoding="utf-8")
        for b in mod.BRANCHES:
            dest=afanta/"output/audio_studio"/b["afanta_slug"]
            dest.mkdir(parents=True)
            (dest/"studio_state.json").write_text(json.dumps({
                "slug":b["afanta_slug"],"niche":b["afanta_niche"],"phase":"RELEASE_HOLD",
                "evidence":{},"release":{"privacy":"private","remote_upload_enabled":False}}),encoding="utf-8")
            (dest/"channel_plan.json").write_text(json.dumps({
                "channel_key":b["key"],"niche":b["afanta_niche"]}),encoding="utf-8")

    def test_three_distinct_branches_and_13_ordered_stages(self):
        p=mod.portfolio()
        self.assertEqual(p["parent_niche_id"],"audio")
        self.assertEqual(len(p["branches"]),3)
        self.assertEqual(len(p["common_stage_ids"]),13)
        self.assertEqual(len({x["afanta_slug"] for x in p["branches"]}),3)
        self.assertNotEqual(p["branches"][0]["mode"],p["branches"][1]["mode"])
        self.assertFalse(p["publish_authorized"])
        self.assertNotIn("business", " ".join(b["id"] for b in p["branches"]))

    def test_install_is_create_only_and_tamper_fails_before_writes(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/"cine";afanta=Path(t)/"afanta"
            self.make_dirs(root,afanta)
            got=mod.install(root,afanta)
            self.assertEqual(len(got["files_created"]),23)
            self.assertEqual(mod.audit(root,afanta)["issues"],[])
            self.assertEqual(mod.install(root,afanta)["files_created"],[])
            contract=afanta/"studio_os/audio_portfolio_contract_v1.json"
            contract.write_text("tampered",encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError,"DIFFERENT_CONTENT"):
                mod.install(root,afanta)
            self.assertEqual(contract.read_text(encoding="utf-8"),"tampered")

    def test_mixed_afanta_niche_preflight_fails_closed(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/"cine";afanta=Path(t)/"afanta"
            self.make_dirs(root,afanta)
            bad=mod.BRANCHES[0]
            state=afanta/"output/audio_studio"/bad["afanta_slug"]/"studio_state.json"
            row=json.loads(state.read_text(encoding="utf-8"))
            row["niche"]="senior_daytime_audio_en"
            state.write_text(json.dumps(row),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"AFANTA_NICHE_SCOPE_MISMATCH"):
                mod.install(root,afanta)
            self.assertFalse((root/"config/audio/branch_registry_v1.json").exists())

if __name__=="__main__":unittest.main()
