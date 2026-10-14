# CineFactory OS v1.6.22 — Multi-Character Identity + Semantic/Dialogue Performance

Updated: 2026-10-09
Repository: CineFactory OS (existing working tree, not a clean baseline)
Status: **IMPLEMENTED WITH QUALIFICATION LIMITATIONS** — not blanket production certification

## Scope delivered

- Persistent per-character identity and actor-bound reference metadata from v1.6.21 CharacterFactory.
- Actor-appearance comparison on rendered Blender/Wan media, and frame-level actor tracking at head, middle and tail of video.
- Fail-closed multi-character tracking when an actor has no global-character binding, reference ID or usable reference pack.
- Explicit failure when distinct actor tracks collapse onto the same apparent screen region (IoU >= 0.70 on a sampled frame).
- DialoguePerformanceEngine compiles speaker/listener roles, objectives, action verbs, subtext, expression cues, gestures, eyelines and event-driven listener reactions.
- Semantic directives are preserved through ShotPerformanceSpec, EpisodeAssembler, CompiledShot and BlockExecutionPlanner.
- Per-line speech timing contract accepts supplied word or phoneme time intervals with provenance (manual or forced_alignment).
- Rejects missing/overlapping/out-of-shot speech timing where alignment is required; rejects duplicate dialogue line IDs, unknown actors and invalid shot timing.
- Invalid dialogue compilation cannot be applied to a shot; shot-ID/actor mismatches also block.
- **No invented phoneme timings or unsupported A/V synchronization claims.** The field `audio_lipsync_measured` remains false; annotations alone are not proof of actual synchronization.
- The Wan video method remains **blocked for semantic-performance-critical production** by `SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED`, even when actor identity QC passes.

## Real render evidence already present (v1.6.22 sample)

Evidence root: `data/verification/v182_multi_character_dialogue/`

- Blender dialogue shot: `blender/renders/block_animation/shots/0000_S01.mp4` (12,560 bytes in the captured sample). Blender reported performance QC pass and score 1.0 under its specified 3D cue-conformance metric, **not a human aesthetic score**.
- Real Wan two-character sample: `wan/S01.wan.multi_identity.mp4` (12,830 bytes in the captured sample), `state=SUCCESS`.
- Wan identity sample scores: actor A 0.9510; actor B 0.9258; sampled tracking minimum 0.9258. Head/mid/tail tracking passed in that captured sample.
- A/B tracks were spatially separated in the sample. It does not validate heavily occluded, fast moving, or nearly identical characters.
- Three-character dialogue behavior has deterministic test coverage and a **single successful real Blender→Wan three-character sample** (details below). Multi-seed/occlusion/camera-angle production qualification is **not yet established**.
- The sample does **not** qualify lip-sync, long-form performance quality or a multi-seed camera-angle benchmark. Inspect the recorded evidence before any production signoff.

## Changed/added code (2026-10-09 pass)

- `cinefactory/studio/dialogue_performance.py` — alignment annotations, validation, duplicate-line detection and fail-closed application.
- `cinefactory/studio/character_factory.py` — no silent pass for missing actor references; actor box-collision gate.
- `tests/test_dialogue_safety_v182.py` — targeted regressions for the failure paths above.
- Existing v1.6.22 implementation and evidence: `tests/test_dialogue_performance_v182.py`, `scripts/verify_multi_character_dialogue_v182.py`, `data/verification/v182_multi_character_dialogue/multi_character_dialogue_verification.json`.

## Test and verification commands

```powershell
python -m compileall -q cinefactory scripts tests
python -m pytest -q tests/test_dialogue_safety_v182.py tests/test_dialogue_performance_v182.py tests/test_character_factory_v181.py
python -m pytest -q
```

Recorded sample real-render evidence predates the 2026-10-09 safety hardening. New hardening is software-verified; **do not claim a new real Wan render without rerunning the full verification script.**

## Acceptance gate definitions

1. Source/canonical actor identity is stable; all expected actors have valid reference packs.
2. All requested actor tracks have measured head/mid/tail evidence.
3. Every track clears the calibrated identity floor and no two distinct actors collapse onto the same tracked region.
4. Dialogue speaker and listeners are resolvable; intervals are in range; no duplicate line ID; speaker/listener semantics are explicit.
5. Speaker speech timing is supplied, ordered and valid whenever the downstream lip-sync pipeline requires alignment.
6. Audio/video lip-sync is **unqualified** until independently measured against actual generated voice/audio and mouth animation.
7. Generative backend must retain its semantic video blocker until multiple real performance tests clear a defined production gate.

## Next qualification requirements

- Verify **three-or-more-character** real renders with distinct identities, reference crops and cross-backend transitions.
- Run multiple seeds and camera configurations; measure occlusion/re-identification and identity switches.
- Add speaker attribution from actual audio (with permission/rights) and forced alignment to generated clips; measure phoneme-to-viseme error, actual A/V offset, missing words and reaction timing.
- Introduce objective/subtext-driven motion/acting evaluation across long scenes and test it on production scene sequences.
- Calibrate identity cutoffs with false-positive/false-negative data; sample head/mid/tail alone is insufficient for moving or crowded scenes.
- Preserve the existing blocker unless real semantic performance QC qualifies the specific backend/mode.

**Release note:** Working tree already had substantial pre-existing tracked changes and untracked modules. This milestone does not stage, reset, overwrite unrelated files, or commit the entire dirty working tree.


## 2026-10-09: Real THREE-actor render qualification sample

Runner: `scripts/verify_three_actor_dialogue_v182.py`

Evidence: `data/verification/v182_three_actor_dialogue/three_actor_verification.json`

- Actors: A / CHAR_MC_A, B / CHAR_MC_B, C / CHAR_MC_C.
- Source Blender: `blender/renders/block_animation/shots/0000_S_ABC.mp4`, 160x90, 24 fps, 115 frames, 4.8 seconds, 17,544 bytes.
- 3-actor Blender camera geometry QC: PASS; 3-actor performance cue-conformance QC: PASS, score 1.0; frame evidence has all three actors.
- Wan: `wan/S_ABC.wan.mp4`, 320x176, 16 fps, 17 frames, 1.0625 seconds, 17,120 bytes; worker state SUCCESS.
- Actor A identity/tracking minimum: **0.8646** (three frame samples).
- Actor B identity/tracking minimum: **0.9165** (three frame samples).
- Actor C identity/tracking minimum: **0.7114** (three frame samples).
- Per-actor character identity assessment and sampled actor tracking reported PASS, no sampled box collision.
- The configured identity floor is **0.70**. Actor C exceeds this by only **0.0114**; therefore the result is borderline and **not sufficient for unattended long-form deployment or general quality certification**.
- This is one low-resolution, single-seed proof clip, **not** multi-angle, multi-seed, human-viewed production QA, nor proof of speaking mouth synchronization.

### Engineering blockers caught and corrected during real verification

1. Blender camera ray casting initially labeled character C's own `C_hairSide` accessory as an external occluder (`C:TARGET_OCCLUDED`). Fixed in `scripts/blender_animation_worker.py` using object-parent ownership (including attached hair/accessories) rather than suppressing real external occlusions. Final camera geometry QC PASS.
2. A three-way listening graph demanded an approximately 111-degree B→C eyeline with B oriented toward A. Performance QC correctly blocked it. Restaged/redirected the listening beat while keeping all three characters present; final measured performance QC PASS.
3. The Wan-specific `SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED` gate **remains enabled**.

### Final software verification recorded

- Final full repository regression after Blender worker ownership fix: **600 passed**, 0 failed (`pytest -q`, 204.76 seconds).
- Specialized v1.6.22/CharacterFactory tests after multi-character tracking hardening: **27 passed**, 0 failed.
- `compileall`: PASS. The Blender worker fix was also compiled and exercised by the real three-character Blender render.
- The final real three-character Blender/Wan workflow completed with `QUALIFIED_IDENTITY_ONLY` (sample-specific identity result; not a production release certification).

This step remains **PARTIALLY QUALIFIED** for production: identity sampling succeeds on two/three actors, while rigorous multi-seed, temporal/re-id, lip-sync and generated-dialogue semantic performance gates remain open.
