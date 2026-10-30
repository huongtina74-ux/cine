# Legacy A2 FIXED 10S 8-skill pack → CINE company integration
The owner's ZIP skillpack contained eight specialist specifications, NOT eight fully installed production workers. Do not duplicate shared departments or call them READY until operational evidence exists.

1. A2 Script Director → existing CINE Writers Room and niche story bible.
2. Automatic Shot Director → CINE Direction/DOP with exactly 10.0s per shot.
3. Character Continuity → immutable user-source character registry and SHA preflight; unapproved generated views blocked.
4. Voice Performance → CINE Audio + niche voice_registry.json; WAV/license/lip-sync unverified.
5. Muse Image → generation via approved character/location anchors only; one 16:9 full frame, no text panels.
6. Muse Video → 10.0s image-to-video acting and fixed voice, requires provider contract + actual video QC.
7. A2 Production QC → stage gates and human art approval in main CINE QC department.
8. CINE Orchestrator → existing Studio Kernel/Company Runner; optional CLI in scripts/slow_english_a2_preflight.py.

This PR integrates data definitions and an actual **read-only preflight** into one repo. The legacy full prompt compiler from the separate ZIP must still be imported and reconciled with the real CINE company runner before claiming one-click auto-production. The Desktop Commander device was offline at the audit. No new standalone CINE OS is authorized.

## The single authoritative Master Skill

Use only `.claude/skills/cine-script-factory/SKILL.md` as the public Bell & Leaf entrypoint. The 21 original A2 specialist skills are internal professional roles in `config/story_factory/a2_bell_leaf_skill_graph.json`. `tools/cf_a2_master_skill.py` dispatches them and records SHA-bound output receipts in the existing episode directory, while `tools/cf_script_factory.py` retains real stage gates and `tools/cf_a2_director_bridge.py` retains 10-second director intake. Status/PASS on file contracts never substitutes independent human A2/creative/Canon approval.
