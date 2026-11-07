# Bell & Leaf / Slow English A2 — verified readiness checkpoint (2026-11-07)

## Scope and provenance
- Active Windows repo: C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6, branch integration/cine-a2-source-voice-qc-20261106.
- GitHub main checked at 0e335bf5eca1ee04b13e26b1a2aac06025f0c56b. This documentation-only branch does not merge the many uncommitted local changes.
- This is an evidence checkpoint, not approval to publish or proof of a completed Muse production.

## Executed checks on active local tree
- pytest: test_bell_leaf_story_sync_20261107.py, test_bell_leaf_visual_canon_20261107.py, test_slow_english_a2_voice_casting.py, test_cine_a2_local_assets_media.py: **26 passed, 0 failed**, plus one pytest cache permission warning.
- tools/cf_niche.py audit slow_english_a2 --verbose: **55% NOT READY**. Package 100%, identity 43%, research 17%, format 0%, KPI 0%, policy 25%, art 78%, direction 33%, tools 0%, learning 100%, owner 0%. Generic niche readiness does not equal a Bell & Leaf media QC score.
- tools/cf_completion_status.py --project slow_english_a2: BLOCKED because the script_factory project manifest is absent for this project ID. Do not equate this generic five-pillar status with Bell & Leaf E2E readiness.

## Prior local evidence (receipt dated 2026-11-06; not rerendered today)
- 10/10 source character images and 90/90 original source crops: independently verified by exact RGBA digest locally.
- 10 generated VoxCPM2 voice candidates and 10 A2 auditions; **0/10 human-approved master voices**. Audition file: data/slow_english_a2/voice_cast_round1/VOICE_AUDITION_COMPARE_NOT_APPROVED.html.
- **0/483** independent room plates and **0/756** independent prop plates approved.
- Actual 10-second Muse I2V shot with real movement, source-bound voice/lip-sync, independent QA and provider receipt: NOT VERIFIED.
- No private original PNGs, candidate WAVs, audio, image assets, or generated media should be published through this checkpoint.

## Priority execution sequence
1. Reconcile Bell & Leaf-specific niche identity, format, policy and research bindings with authoritative series contracts, without adopting foreign generic A2 metrics.
2. Gather dated competitor video observations, original audience insights and source evidence; no fabricated observations.
3. Human listening and licensed-voice approval before permanent master Voice ID/SHA lock; regenerate mouth cues for the selected paced WAV.
4. Approve real location multi-view plates and reverse angles for one pilot shot; preserve user character Canon, Bubu sparkle, and Bix without bell.
5. Run one real Muse 10.0s/240-frame/24fps/16:9 I2V shot, then independent motion, identity, lip-sync and source verification before scaling.
6. Integrate local code with small tested PRs after review; do not bulk-stage, clean/reset, or overwrite the active Windows tree.

Production authorization remains HOLD until the required evidence and owner approvals exist.
