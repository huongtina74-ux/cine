from __future__ import annotations
"""Build department-by-department professional SOP and an original nursery demo plan.

The generated handbook consists of verified *research instructions* and test
gates, NOT a certification of the listed candidate tools or a content asset.
"""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.niche_research_conference_v192 import (
    DEPARTMENT_PLAYBOOK,OFFICIAL_SOURCE_SNAPSHOT,NicheResearchConference,
)

def main():
    target=ROOT/"docs"/"CINEFACTORY_DEPARTMENT_PRODUCTION_RESEARCH_V1632.md"
    research=ROOT/"data"/"verification"/"v192_department_research"
    research.mkdir(parents=True,exist_ok=True)
    lines=[
        "# CineFactory v1.6.32 — Departmental Production R&D Handbook",
        "",
        "**2026-10-09.** Status: source-backed expert SOPs and controlled local A/B experiment. This document does not certify a new production tool and is not autonomous live web research.",
        "",
        "## Operating rules",
        "",
        "1. Receive niche, original script, approved media/rights, audience and quality bar; route to specialists before selecting engines.",
        "2. Source research must distinguish official technical manuals, license/rights, active code/adapter status, hardware suitability and actual generated-video evidence.",
        "3. All new tools are candidates. Demonstrate exact version, executable smoke, safe license, scoped reference shot, GPU/VRAM budget and accepted-minute cost before automatic production.",
        "4. Produce original creative content; never download/recreate competing characters/songs without necessary rights. For preschool music require curriculum expert and original lyric/music/voice clearance.",
        "5. Present quality-best, fastest-viable, cheapest-viable and Pareto candidates. Do not invent perceptual quality from SSIM, use blind human creative review on final output.",
        "6. Fail closed: unfinished QA, noncleared music/footage/voice/AI model, unsupported engine or expensive API require an explicit R&D request and separate authorization.",
        "",
        "## Department operating procedures (22)",
        "",
    ]
    for i,(id,dp) in enumerate(DEPARTMENT_PLAYBOOK.items(),1):
        lines.extend([
            f"### {i:02d}. {id}",
            "",
            f"**Mission:** {dp.responsibility}",
            "",
            "**Must receive:** "+ "; ".join(dp.inputs)+".",
            "",
            "**Research questions:** "+ "; ".join(dp.research_questions)+".",
            "",
            "**Candidate tool families:** "+ "; ".join(dp.candidate_tool_families)+".",
            "",
            "**Handoff artifacts:** "+ "; ".join(dp.deliverables)+".",
            "",
            "**Objective QA:** "+ "; ".join(dp.objective_qc)+".",
            "",
            "**Expert/human review:** "+ ("; ".join(dp.human_qc) if dp.human_qc else "Required for risky or artistically ambiguous output")+".",
            "",
            "**Technical source anchors:** "+ (
                "; ".join(f"[{k}]({OFFICIAL_SOURCE_SNAPSHOT[k].url})" for k in dp.source_ids)
                if dp.source_ids else "Source evidence must be acquired for this project"
            )+".",
            "",
            "**Release condition:** All rights, functionality, acceptance, cost and quality evidence must be signed off before an automated production route may rely on this department.",
            "",
        ])
    lines.extend([
        "## Niche-specific production lanes",
        "",
        "| Niche | Initial method options to benchmark | Non-negotiable domain evaluation |",
        "|---|---|---|",
        "| Original preschool 3D musicals | Blender organic rig + original song and vocal timing; alternative licensed real-time animation engine | curriculum, original IP/music rights, singing visemes, choreography, child-safe behaviour and human audience review |",
        "| Minecraft | Blender voxel rig/camera + reusable actor clips; original game runtime where actual gameplay necessary | actor persistence, occlusion, movement, editing and originality |",
        "| Roblox | Blender R6 animation vs Roblox Studio genuine gameplay | R6 body and wardrobe, camera, safe ownership of assets |",
        "| Animal animation | Blender animal rig/physics vs game physics after runnable proof | anatomy, motion, emotional behaviour, object collisions |",
        "| Long Slide | Godot candidate runtime vs Blender physics | deterministic obstacles, trajectory, stable capture, speed |",
        "| GTA | genuine licensed game runtime with capture, not claimed Blender recreation | game/publisher licence, authentic footage, stable recording |",
        "| AI drama | locally qualified ComfyUI model vs Blender hybrid | face/body consistency, style, no IP copying, rights on checkpoints/LoRAs |",
        "| 2D cartoons/English | OpenToonz Xsheet candidate, 2D compositing and Remotion if company licence allows | legibility, graphics timing, audio-to-caption synchronization |",
        "| ASMR | actual microphone/camera + audio editor, not default synthetic substitutes | authentic soft transients, noise floor and relaxed pacing |",
        "| Long audio stories | original scripts, consented human narrator vs tested local TTS | pronunciation, no loop/reused text, intonation and accessibility |",
        "| Rain and sleep | licensed audio originals, mastering and low-flicker imagery | click-free loops, level stability, non-disturbing sound |",
        "| Silent fishing | original first-party field recording and sound capture | authentic capture, property rights and safety |",
        "",
        "## Accurate cost formula",
        "",
        "**True total cost per ACCEPTED video minute** = (measured electricity + GPU rental if any + applicable API/subscription charges + incremental human labor + licensed assets/music amortization + storage/bandwidth + rejected-shot and re-render cost) / final accepted minutes.",
        "",
        "The measured SSIM, bitrate, video size and wall-time from an encoding A/B experiment do not provide the total dollar cost; these items remain UNKNOWN until measured. Quality floors are defined per niche and stage. A tool meeting no quality gate must not be ranked as cheapest viable.",
        "",
        "## Engineering gaps with priority",
        "",
        "| Priority | Capability gap | First real acceptance test |",
        "|---|---|---|",
        "| P0 | Autonomous authorized web/repo/document ingestion with cited source verification | tool candidates carry source snapshot, licence checks and independent benchmark evidence |",
        "| P0 | Original preschool songwriting/vocals/organic characters | 30–60s original song with human curriculum/music/IP review |",
        "| P0 | Real scene-based performance A/B beyond video encoding | same geometry/camera/asset seed via Blender Workbench, Eevee, allowed alternatives; reviewer scoring |",
        "| P0 | Actual game runtime engine availability | Godot executable, original course, deterministic physics video + render timing |",
        "| P0 | AI video local GPU qualification | ComfyUI pinned workflow & model licence; 12GB GPU and multi-shot identity review |",
        "| P1 | True cost and bottleneck telemetry | real GPU W, render retries, VRAM, CPU, human touch time; accepted-minute cost |",
        "| P1 | Independent video QA and creative/artistic blind review | annotated 3-genre pilot clips + repair loop, no automatic approval based on compressed PSNR |",
        "",
        "## Audit ledger",
        "",
        "Source files: cinefactory/studio/niche_research_conference_v192.py; research_brief_parser_v192.py; codec_ab_experiment_v192.py. Script creates reports at data/verification/v192_department_research/.",
        "",
        "Known limitations: source links are curated from the current research session, and the local conference does not itself browse current websites. All methods need actual cross-backend and independent human benchmark before any release.",
        "",
    ])
    target.write_text("\n".join(lines),encoding="utf-8")
    sample={
        "project_brief":"An original 3D preschool song teaching the English alphabet through friendly original characters; educational, not copied from another IP.",
        "script_text":"Scene 1: Original preschool character sings the ABC song in a colourful classroom and dances in rhythm.\nScene 2: The child character says each letter while colourful letters appear as 2D typography.\nScene 3: Two characters dance together and sing a final chorus.",
        "target_language":"en","intended_audience":"preschool",
        "target_duration_minutes":1.0,
        "reference_video_urls":[],
        "source_media_rights_confirmed":False,
    }
    report=NicheResearchConference(ROOT).convene(
        "preschool_3d_musical",project_id="ORIGINAL_PRESCHOOL_MUSIC_PILOT",
        context=sample,
    )
    (research/"example_preschool_song_research_v192.json").write_text(
        report.model_dump_json(indent=2),encoding="utf-8")
    print("DEPARTMENT_RND_HANDBOOK_WRITTEN",target,
          "sops",len(DEPARTMENT_PLAYBOOK),"preschool_scene_hypotheses",
          report.input_analysis.script_segments if report.input_analysis else 0)
if __name__=="__main__":main()
