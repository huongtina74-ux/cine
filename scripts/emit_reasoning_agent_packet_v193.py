from __future__ import annotations
"""Export a gated handoff packet for a future authorized reasoning-capable agent.

No LLM, internet, GitHub, video tool, paid API or external process is called.
The example response is explicitly authored for demonstrating schema contract.
"""
import hashlib,json,sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.evidence_reasoning_v193 import (
    CitedResearchSource,SourceKind,
)
from cinefactory.studio.strategic_reasoning_v193 import DecisionReasoningReport
from cinefactory.studio.reasoning_agent_bridge_v193 import (
    ReasoningAgentBridge,AgentResearchProposal,AgentHypothesis,
)

def main():
    dest=ROOT/"data"/"verification"/"v193_evidence_reasoning"
    report=DecisionReasoningReport.model_validate_json(
        (dest/"real_codec_evidence_reasoning.json").read_text(encoding="utf-8"))
    origin=ROOT/"data"/"verification"/"v192_department_research"/"codec_ab"/"codec_ab_evidence_v192.json"
    source=CitedResearchSource(
        source_id="REAL_V192_ENCODE_AB_MANIFEST",
        kind=SourceKind.LOCAL_ARTIFACT,locator=str(origin.resolve()),
        publisher_or_owner="CINEFACTORY_LOCAL_ENCODE_LAB",
        observed_on=date(2026,10,9),
        source_sha256=hashlib.sha256(origin.read_bytes()).hexdigest(),
        scope="FFmpeg x264 CRF21 original v185 90-frame 640x360 already lossy video",
        retrieved_and_inspected=True,independently_verified=False,
    )
    bridge=ReasoningAgentBridge()
    packet=bridge.make_packet(report,[source],project_brief=(
        "Evaluate what the 90-frame x264 evidence establishes, "
        "and propose a safe next 4K/long-form codec benchmark without inventing prices."
    ))
    (dest/"external_reasoning_agent_packet_v193.json").write_text(
        packet.model_dump_json(indent=2),encoding="utf-8")
    example=AgentResearchProposal(
        session_id=packet.session_id,
        hypotheses=[AgentHypothesis(
            hypothesis_id="EXAMPLE_RESEARCH_HYPOTHESIS_ONLY",
            relevant_task_id=packet.task_ids[0],
            proposed_method_id="ffmpeg.x264.veryfast",
            candidate_niche=packet.niche_id,
            claim="Existing short x264 timing may not generalize to 4K long-form encoding.",
            confidence_class="UNTESTED",
            cited_source_ids=["REAL_V192_ENCODE_AB_MANIFEST"],
            benchmark_to_run="On original 4K lossless reference, compare 3 x264 presets over >=30 seconds while measuring accepted footage fidelity, time and stream correctness.",
            risk_and_known_gaps=["ONE_90_FRAME_ALREADY_LOSSY_SOURCE","NO_LONGFORM_ENCODE_RELIABILITY","NO_ACCEPTED_MINUTE_COST_OR_HUMAN_REVIEW"],
        )],
        knowledge_gaps=["4K wall-time and user acceptance","H264 rights scope"],
        statement_of_uncertainty="This is a local illustrative structured response, NOT an executed external intelligent-agent investigation.",
    )
    admitted=bridge.review(packet,example)
    (dest/"illustrative_agent_response_v193.json").write_text(
        example.model_dump_json(indent=2),encoding="utf-8")
    (dest/"agent_response_review_v193.json").write_text(
        admitted.model_dump_json(indent=2),encoding="utf-8")
    assert admitted.status=="RESEARCH_PROPOSAL_ACCEPTED"
    assert not admitted.production_execution_approved
    print("V193_AGENT_BRIDGE_RESEARCH_PACKET_PASS",
          "task_count",len(packet.task_ids),
          "permitted_source_refs",packet.permitted_source_ids,
          "response_admission",admitted.status,
          "remote_agent_connected",packet.agent_connected,
          "production_execution_approved",admitted.production_execution_approved)

if __name__=="__main__":main()
