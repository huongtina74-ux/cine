# CINE Slow English A2 — Gia đình phù thủy / Bell & Leaf
## Windows Master Skill — single existing CineFactory project

**CINE root:** `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`

**Only Master Skill:** `.claude/skills/cine-script-factory/SKILL.md`

**Fixed project:** `slow_english_a2_bell_leaf` — subniche `magical_witch_family_stories` inside Slow English A2. No additional CineFactory, separate Story Bible or duplicate asset registry.

### Real Windows operation

From the CINE root (PowerShell):

```powershell
python tools/cf_script_factory.py init --id bell_leaf_ep001 --niche magical_witch_family_stories --mode A2_ANIMATED_SCREENPLAY --minutes 40 --writer YOUR_ACTUAL_WRITER_ID
python tools/cf_a2_master_skill.py next --id bell_leaf_ep001
python tools/cf_a2_claude_agent.py --id bell_leaf_ep001 --execute --actor claude-code-sonnet
python tools/cf_a2_master_skill.py status --id bell_leaf_ep001
```

Only initialize a new episode once. Every episode stays in the existing `data/script_factory/projects/` directory. Do not overwrite already developed episodes.

Before the FIRST research role, place authentic input source records at:

`data/script_factory/projects/<episode_id>/01_research/input_sources.json`

The records must include `subniche_id: magical_witch_family_stories` and a nonempty list of sources containing HTTPS URL, observed_at_utc, source method, evidence modality and peer group. Distinguish `DIRECT_MAGICAL_FAMILY` from `ADJACENT_SLOW_ENGLISH`. If no direct comparison exists, record adjacent data as context and mark direct benchmark insufficient; DO NOT invent a direct channel.

### Operating logic

One Master Skill delegates 21 specialists over eight stages:

Research → Audience Insights → Concepts → Story Canon → Causal Outline → Screenplay → Independent Review → Script Lock.

The dispatcher selects the next legal role from 38 causal dependencies. Each actual agent task receives the original skill, existing evidence, current Bell & Leaf Series Bible and voice registry. Claude CLI runs with filesystem tools **disabled**; it sends a JSON file map back to the local Python wrapper, which validates paths, source URLs, content and hashes, then records the role handoff. No permission bypass, no automatic edits outside the exact artifact list.

When `next` returns `STAGE_QC_GATE`, a genuine reviewer must inspect evidence, content and creative quality. Only then may the original CINE Script Factory `advance` stage be used; the agent wrapper NEVER does this automatically.

After final independent Story Doctor, A2 learner comprehension, actual 30–50-minute table read, Veylora Canon review and Script Lock, director preflight is:

```powershell
python tools/cf_a2_director_bridge.py --id bell_leaf_ep001 --out data/slow_english/episodes/bell_leaf_ep001/shot_preflight
```

The director checks SHA and makes 10.0s shot prompts; actual licensed voices, lip-sync, full-bleed 16:9 images, true reverse angles and rendered video remain separately gated by production QC.

### Verified local integration evidence — 2026-10-30

- Claude Code v2.1.296 authenticated via existing Pro account. The repository's Claude trust prompt has **not** been bypassed. This wrapper uses no Claude tools, so untrusted workspace permissions are not needed for these role outputs.
- One CINE repo, one Master Skill; 21 original specialist skill files, 38 dependencies, 27 declared artifacts.
- Real R01 Claude role completed with SHA-bound `evidence_register.json` in `bell_leaf_integration_pilot_20261030`; five historical 2026-10-22 Slow English metadata sources labeled **ADJACENT**, not direct magical-family research.
- Research stage **NOT APPROVED**; missing verified direct magical-family comparator evidence, actual viewing of competitor audiovisual content and human research/editorial review. No completed Bell & Leaf screenplay, approved 483 room views, approved 756 prop views, WAV, lip-sync or Muse final video asserted.
- Existing Windows git history and local unrelated modifications remain untouched; no reset, clean or forced merge. A selective prior overlay from GitHub commit `6e6e47a4` was backed up under `C:\Users\ADMIN\Documents\CINE_A2_Research_Audit_20261022\SYNC_BACKUP_20261030_6e6e47a4`.

**Safe diagnostic commands:** `python tools/cf_a2_master_skill.py status --id EPISODE_ID`; `python -m unittest discover -s tests -p test_cine_a2_claude_agent.py -v`; `python -m unittest discover -s tests -p test_cine_a2_master_skill.py -v`.

**No false readiness:** a recorded skill is a validated file handoff, NOT evidence that it was editorially approved; a successful unit test is not evidence the whole 40-minute film was produced.
