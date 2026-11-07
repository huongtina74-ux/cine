---
name: cine-per-niche-creative-risk
description: Required across CINE niches before producing any new research-driven YouTube video or original screenplay. Isolates each niche's competitors and creativity contracts, then checks originality, sources, rights, audience and AI disclosures.
---
# CINE — Per-Niche Creative & YouTube Risk Gate

Scope: all creator niches. This is NOT Bell & Leaf-only and NOT a replacement for existing company stages or specific Canon skills.

## Before assigning research or scripts
1. Read docs/CINE_PER_NICHE_A_B_C_D_OWNER_STANDARD_20261028.md and docs/CINE_PER_NICHE_RESEARCH_CREATIVE_YOUTUBE_GATES_20261107.md.
2. Read config/research/per_niche/niches.json and config/research/per_niche/creative_youtube_risk_profiles_v1.json; run: python tools/cf_creative_youtube_gate.py inventory.
3. Select EXACT niche_id and genre/format. Do not mix generic Slow English with magical_witch_family_stories/Bell & Leaf; do not inherit finance/history or audio-story baselines for gaming or ASMR. Local package unregistered in the research roster => BLOCK_OWNER_NICHE_ROUTING. Do not autonomously activate.
4. Route competitor research A/B/C/D by exact niche/cohort; store real URL/video/channel IDs with dated observations in the existing canonical SQLite registry. A direct video of a DIFFERENT niche counts only as adjacent background, never a direct comparable baseline.
5. Deep inspection must identify what was truly inspected: metadata-only, transcript with timecodes or actual audio/video. Never invent personal competitor CTR, RPM, retention, copyrighted scripts or verified outlier evidence.
6. Carry **abstract** mechanisms to an ORIGINAL episode: audience need, hook mechanism, stakes, pacing, emotional payoff, hypothesis, creative difference, rights and three independent axes of originality. Never transfer competitor scene-by-scene scripts, characters, twists, faces or dialogue.
7. For long-running series, run the specific dedup/continuity gate (e.g., Bell & Leaf 1000-card registry) and review all released episodes, not just titles.
8. Draft a per-video research/creative brief with six YouTube policy decisions, each grounded in the actual video: made-for-kids designation; altered/synthetic disclosure; reused-content originality; inauthentic/mass-production risk; rights; advertiser suitability. Children's audience is NOT a revenue optimisation toggle. Animated family-safe videos might or might not be directed to children. Do not assert a policy exemption from a title or prompt.
9. Run: python tools/cf_creative_youtube_gate.py preflight --brief data/your_niche/your_episode.json --out data/your_niche/creative_youtube_preflight.json. BLOCKED => reject handoff and research missing evidence. INDEPENDENT_EDITORIAL_REVIEW_REQUIRED => proceed only with independent expert/owner review, never automatic release.
10. After publishing with owner's permission, use OWN verified Analytics and timestamps to test hypothesis; promote insight/skill changes only with evidence, independent review, owner-approved version change and rollback. Never claim success from a synthetic test or competitor public metadata alone.

## Hard prohibitions
- No cross-niche benchmark/retention/metadata contamination or generic "viral formula" disguised as niche research.
- No sourced transcript adaptation masquerading as original writing.
- No repetitive mass-produced AI templates with identical scenarios and endings.
- No fabricated metrics, fake reviewer signoffs, rights clearance or "zero YouTube risk" claims.
- No owner Canon mutations; Bell & Leaf remains locked to its four originals and special actor/portal/voice/visual rules.
- No automatic Made-for-Kids opt-out based on preferred RPM, no automatic upload/publication.
- Do not rewrite CineFactory stable modules or overwrite a dirty local tree for integration.

## Acceptance
A factual research receipt is not approval of art; a structurally valid brief is only a candidate for independent editorial review. Preflight never returns release_authorized=true. Tools/tests prove deterministic checks, not that every Windows EXE agent is wired to run them.
