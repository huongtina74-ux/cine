import argparse,contextlib,io,json,pathlib,sys,tempfile,unittest
from types import SimpleNamespace
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import cf_script_factory as factory
import cf_a2_claude_agent as agent

class CINEClaudeAgentWindowsTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.storage=pathlib.Path(self.tmp.name)
  self.ep="bell_leaf_agent_test"
  with contextlib.redirect_stdout(io.StringIO()):
   factory.initialize(argparse.Namespace(id=self.ep,root=self.storage,
    niche="magical_witch_family_stories",mode="A2_ANIMATED_SCREENPLAY",
    minutes=40,writer="actual-test-operator",language="en-US"))
  self.base=self.storage/self.ep
  self.sample={"subniche_id":"magical_witch_family_stories","sources":[{
   "url":"https://www.youtube.com/watch?v=SampleTest1","observed_at_utc":"2026-10-22T13:12:07+00:00",
   "method":"historic_public_metadata","peer_group":"ADJACENT_SLOW_ENGLISH",
   "evidence_type":"METADATA_ONLY","channel":"Verified Example, simulated test only"}]}
 def tearDown(self):self.tmp.cleanup()
 def put_source(self):
  p=self.base/"01_research/input_sources.json"
  p.write_text(json.dumps(self.sample),encoding="utf-8")
 def payload(self,url=None):
  src=self.sample["sources"][0]
  obj={"items":[{"id":"EV1","url":url or src["url"],"observed_at_utc":src["observed_at_utc"],
        "method":"historic_public_metadata","claim":"Historical metadata listed in source records only, not watched video",
        "confidence":"SUPPORTED_HYPOTHESIS","limitations":"No direct witch-family cohort, no actual AV inspection"}]}
  return json.dumps({"artifacts":[{"path":"01_research/evidence_register.json","content":json.dumps(obj)}],
   "summary":"Metadata only; no direct cohort","limitations":["Actual external video not watched"]})
 def test_no_source_fails_closed(self):
  with self.assertRaisesRegex(ValueError,"input_sources.json"):
   agent.prepare(ROOT,self.ep,self.storage)
 def test_reject_wrong_cohort(self):
  self.sample["subniche_id"]="slow_english_a2_story";self.put_source()
  with self.assertRaisesRegex(ValueError,"Invalid research subniche"):
   agent.prepare(ROOT,self.ep,self.storage)
 def test_source_provenance_must_be_dated(self):
  self.sample["sources"][0].pop("observed_at_utc");self.put_source()
  with self.assertRaisesRegex(ValueError,"Unverified or unclassified"):
   agent.prepare(ROOT,self.ep,self.storage)
 def test_reject_invented_url(self):
  self.put_source()
  _,_,node,_,sources=agent.prepare(ROOT,self.ep,self.storage)
  with self.assertRaisesRegex(ValueError,"Invented research URL"):
   agent.parse(self.payload("https://example.org/invented"),node,sources)
 def test_real_claude_invocation_uses_stdin_and_no_tools(self):
  self.put_source()
  with mock.patch.object(agent.subprocess,"run",return_value=SimpleNamespace(
    returncode=0,stdout=self.payload(),stderr="")) as invoke:
   result=agent.run(ROOT,self.ep,"claude-code-test",self.storage,True,60)
  cmd=invoke.call_args.args[0]
  opts=invoke.call_args.kwargs
  self.assertEqual(cmd[0:2],["claude","-p"])
  self.assertEqual(cmd[cmd.index("--tools")+1],"")
  self.assertIn("ASSIGNMENT",opts["input"])
  self.assertGreater(len(opts["input"]),1000)
  self.assertNotIn("--dangerously-skip-permissions",cmd)
  self.assertEqual(result["status"],"ROLE_HANDOFF_RECORDED_NOT_APPROVED")
  self.assertFalse(result["production_authorized"])
  self.assertTrue((self.base/"01_research/evidence_register.json").is_file())
 def test_repeated_run_no_unsafe_overwrite(self):
  self.put_source()
  with mock.patch.object(agent.subprocess,"run",return_value=SimpleNamespace(
    returncode=0,stdout=self.payload(),stderr="")):
   agent.run(ROOT,self.ep,"claude-code-test",self.storage,True,60)
  second=agent.run(ROOT,self.ep,"claude-code-test",self.storage,False,60)
  self.assertEqual(second["skill_id"],"r04-competitive-outlier")
  self.assertEqual(second["status"],"PREPARED_ONLY")
 def test_output_paths_whitelist(self):
  self.put_source()
  _,_,node,_,sources=agent.prepare(ROOT,self.ep,self.storage)
  fake=json.dumps({"artifacts":[{"path":"../../CLAUDE.md","content":"tampering"}]})
  with self.assertRaisesRegex(ValueError,"wrong artifact paths"):
   agent.parse(fake,node,sources)

if __name__=="__main__":unittest.main()
