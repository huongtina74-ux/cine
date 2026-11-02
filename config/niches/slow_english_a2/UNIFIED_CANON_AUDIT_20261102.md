# CINE Slow English A2 — unified active Bell & Leaf Canon audit (2026-11-02)

This is **one** Slow English A2 production profile inside **one** CINE repository. Historical Mia/Grandpa Walter/Biscuit episodes remain as prior artifacts, but may NOT be auto-re-rendered under the current Bell & Leaf character identity. No duplicate CineFactory or separate active canon is created.

## Source images examined
- The owner-provided private Library ZIP `CINE_BELL_LEAF_CANON_SOURCE_LOCK_V1_2_FINAL.zip` contains ten exact original user reference sheets, plus 90 SHA-confirmed source crops and detail assets. Source SHA/crops were verified against the ZIP. This archive is **not** committed to public/private GitHub code and is not yet physically installed in the Windows source path. Original sheets are identity authority; exact crops are not new approved generated camera-angle reference images.
- The 12 location concept sheets were inspected and remain **DRAFT**, multi-panel composited concepts, not individually approved independent 16:9 physical camera plates. One concept labels the lake Moonwater instead of Bellfern; registry and topology remain authoritative. No false approval.
- The canonical site/space/prop registry contains 12 sites, 69 spaces, 108 props, with 483 room plate slots and 756 prop view slots still pending. Never replace site geometry based on composites.

## Active loader correction
- `config/niches/slow_english_a2/visual_bible.yaml` now contains exact original Bell & Leaf character tags `bo me juno Lia bubu bix ongngoai bangoai ongnoi banoi`, per-tag source paths and SHA, and 12 site IDs. Identity is tied to `CHARACTER_CURRENT_SOURCE_LOCK_V1_2.json`; older Mia/Walter/Biscuit identity no longer active.
- `config/niches/slow_english_a2/toolkit.yaml` no longer routes narration, Ken Burns or 3 hero shots as if they were Bell & Leaf. Candidate source-locked image, VoxCPM2, Muse I2V, score and captions are intentionally production=false until real approved WAV, independent plates, commercial clearance and E2E QC.
- `cinefactory/slow_english_unified.py` is the shared A2 Canon check; the old but *active* CINE `cinefactory/prompt_pack.py` and `cinefactory/niche_tools.py` refuse to load a Bell & Leaf config that conflicts with actual canonical names, stage rules or 10.0-second/no-narrator policy.
- This guard makes current CINE Slow English config logically consistent; it **does not mean assets were installed** or images/videos generated.

## Skill/repo complementarity
- 21 original internal research/screenplay skills run through `cine-script-factory` Master Skill, `cf_a2_master_skill.py` and `cf_a2_claude_agent.py`, using eight stage gates and 38 DAG dependencies.
- `danjdewhurst/story-skills` (24 original skills, MIT; 18 mapped) is an *optional*, read-only verified craft source. `tools/cf_a2_external_craft.py` reads two original licensed technique excerpts appropriate to the selected role, checks checkout commit and bounds their size; the existing Claude writer then receives these in the task context. The external repo's book folder structure never overrides Bell & Leaf Canon; no CLI from the repo is executed.
- `pandich93/youtube-niche-finder` remains reference-only, not an activated tool runtime; source evidence for Bell & Leaf must be real and same-subniche.
- Script Lock -> Canon-aware fixed-10s preflight is connected but no actual approved Muse media/voice or publish/Analytics E2E is claimed.

## Windows implementation and safety
Applied **in the existing Windows CINE worktree** with a byte-for-byte backup of legacy active visual/toolkit files at `C:\Users\ADMIN\Documents\CINE_A2_Research_Audit_20261022\SLOW_ENGLISH_UNIFICATION_BACKUP_20261102`. No reset, clean, force merge, deletion of SE_0001/SE_0002 or promotion of draft frames. The local Git history is divergent and not forcibly rewritten.

Run `python -m cinefactory.slow_english_unified` for the factual result:
- A result of `logic_consistency=PASS` means same source-of-truth IDs/styles/tool routing.
- A result of `production_authorized=false` means Bell & Leaf **must not** be considered ready. Expected blockers: 0/10 original on-disk source PNGs until owner source ZIP installed, 0/10 approved voice WAVs, and 0/483+0/756 approved independent plates, actual I2V unverified.
