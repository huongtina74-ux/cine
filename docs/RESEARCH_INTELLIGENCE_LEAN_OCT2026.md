# CineFactory Research Intelligence — lean production policy (October 2026)

## Design principle
Minimize cost, latency, unsupported conclusions and accidental replication.
More agents and more packages do not imply better research.

## Only five stages
1. **Metadata/evidence triage** (`triage`): require new channel 0–30 days, two DISTINCT >=1M view videos >=8 minutes, recent evergreen evidence, believable business case, proof of newcomer access, distinct content format. Qualified results are **AUDIT_READY**, never automatically VERIFIED.
2. **Bounded observation** (`smart-observe`): local authorized video only, opens with FFprobe; low-resolution OpenCV heuristic samples <=180 seconds for visual changes (not semantic meaning), dense opening, bounded uniform coverage over the rest, max 24 images by default. No big vision model loaded at this stage. Metadata-only candidates do not trigger video processing.
3. **Focused review** (`dispatch`): ASMR audio-focused, animation story/visual/animation-focused, narration voice/story-focused. Claude Code runs only via an explicitly approved task, with a per-call budget. Unapproved tasks are stored, not executed.
4. **Owned-video feedback** (`studio-import`, `retention`, `compare`, `qc`): consume authorized Studio exports and observed local videos; exact channel/video and report-period provenance. Links nearest sampled frames to observed retention drops without claiming causation.
5. **Validated learning** (`review`, `learn`): mark observations VERIFIED/HYPOTHESIS/UNKNOWN; require time/path evidence for VERIFIED; produce experiments pending validation, never auto-edit production policies.

## Why NOT more default tools?
- No expensive credit-based research provider in the critical path.
- No Qwen / Whisper auto-install. Add ONLY if representative tests show better evidence accuracy for a needed niche and memory/latency pass budget.
- No PySceneDetect required initially; OpenCV already present. Try the specialized AdaptiveDetector only if shot-cut errors are observed on reference samples.
- No direct download/scraping workaround is enabled. Metadata sources and local video files require lawful/authorized access.

## CLI usage
Run from repo root:

```powershell
python -m cinefactory.research_intelligence triage .\data\research_candidates.json .\data\triage.json --max-deep 3
python -m cinefactory.research_intelligence smart-observe "D:\media\authorized_reference.mp4" "D:\research\ref" --max-frames 24
python -m cinefactory.research_intelligence dispatch "D:\research\ref\observation.json" "D:\research\tasks" --niche "Minecraft animation" --reference-id "case001"
python -m cinefactory.research_intelligence studio-import "D:\analytics\studio.csv" "D:\analytics\studio.json" --start 2026-10-01 --end 2026-10-08 --channel-id UC_ACTUAL
python -m cinefactory.research_intelligence compare "D:\research\ref\observation.json" "D:\research\owned\observation.json" "D:\research\feedback.json" --studio-report "D:\analytics\studio.json" --owned-video-id ACTUAL11ID
python -m cinefactory.research_intelligence retention "D:\analytics\retention_points.json" "D:\research\retention_review.json" --observation "D:\research\owned\observation.json"
python -m cinefactory.research_intelligence learn "D:\research\feedback.json" "D:\research\review.json" --output "D:\research\learning.json"
```

Only `--approved` dispatches can be submitted to `run-claude` manually. That command MAY spend real Claude quota/money. It was tested with mocked subprocess, not a live paid inference in this phase.

## Honest evidence boundaries
- YouTube metadata does not reveal an external channel's CTR, RPM, watch-time retention or referral source.
- A report with a link is not independently verified. AUDIT_READY requires source audit before any claim of a proven niche.
- Video samples can miss motion, voice, edit points, black frames, unsafe content or other events. A sampled frame alone proves very little about narrative.
- OpenCV visual differences are candidate changes, not an authoritative shot segmentation.
- Studio CSV is not real-time background synchronization. User-controlled export or OAuth is required.
- Owned analytics require a consistent reporting window; avoid comparing different age windows.
- Retention decreases correlated with nearby frames do not establish why people left.
- Never promote research hypotheses into production rules without a reviewed experiment; maintain editorial originality and rights.

## Current acceptance and next experiments
Unit/integration acceptance includes:
- distinct-video, channel-age, no-Shorts/no-Live gates and a strict deep-review budget;
- bounded opening/full-coverage visual sampling with actual generated MP4 files;
- focused departmental dispatch and approval enforcement;
- authorized CSV import, normalized percentage/duration and period hash;
- actual owned-video QC, feedback and retention-to-frame map;
- end-to-end synthetic local sample → task → Studio metrics → QC → learning proposal.

To qualify additional components (e.g. ASR, vision models, PySceneDetect):
1. Assemble a LEGALLY ACCESSIBLE representative validation set (e.g. Minecraft, ASMR, Long Slide), with manually-reviewed ground truth.
2. Compare precision/recall of events, temporal coverage, scene accuracy, wall time, peak GPU VRAM and per-video dollar cost.
3. Include non-winning and false-positive videos.
4. Add a component ONLY if a measurable quality gain outweighs runtime complexity and resource cost.
5. Require a separate implementation, operational health checks and launch approval for continuous autonomous collection.
