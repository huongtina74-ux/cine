# CINE Slow English A2 / Bell & Leaf — Canon Lock Integration v1.1

## Product requirement
CINE must reuse the **exact existing** Bell & Leaf character identities, physical location layouts, props and 10-second shot grammar across episodes. It must not invent an approved asset because the filename exists or a generation returned an image.

## Truthful delivery state — 2026-10-29
- 10 original source sheets and 90 source crops are stored separately in `CINE_A2_CHARACTER_REFERENCE_LIBRARY_V1_1_R1.zip`, with SHA-256 and original provenance. Those **are not 90 newly rendered camera angles**.
- `RENDER_TARGETS_270_SLOTS.csv`: all 270 targets remain `PENDING_NEW_RENDER` until a real Muse result is received and individually reviewed.
- **One newly generated Bubu front/3/4 full-body candidate** is included here as `DRAFT_GENERATED`, not approved and not rendered through Meta Muse.
- All 12 location registries and 69 spaces exist as DRAFT, but no location master can be declared `APPROVED_FOR_REFERENCE` just from a prompt/plan.
- No Meta Model API key is available here; the connected Windows CINE workstation is offline. No live Muse 270-image generation, no real first-frame video test and no local CINE asset installation has been claimed.

## Files
1. `schemas/CHARACTER_REGISTRY.schema.json` validates **real** character reference pointer format; no imaginary `APPROVED` filenames.
2. `schemas/LOCATION_REGISTRY.schema.json` validates site/space/view registry, inherited from the existing 12-site CINE registry.
3. `schemas/SHOT.schema.json` validates structured per-shot metadata, with exact visible character tags.
4. `config/CHARACTER_CURRENT.json` pins sources to real checksums, leaves `approved_assets: []`, and records 27 remaining new-render slots per character.
5. `config/LOCATION_CURRENT.json` creates **draft pointers only** for 12 locations, 69 spaces, and no fake approved plates.
6. `config/slow_english_a2_bell_leaf_project_profile.json` enables strict production rejection of unapproved references, 16:9 and 10-second I2V.
7. `src/bellLeafCanonResolver.ts` provides `resolveCharacterRefs()`, `resolveLocationRefs()`, `buildBellLeafPrompt()`, `runBellLeafQC()`, `resolveShot()`, `verifyReferenceFiles()`.
8. `examples/` contain two approved-fixture-independent real shot metadata examples. `EP001_S001` is zero-character yet still has mandatory location ID. `EP001_S010` requires exactly Lia+Bubu and an atelier location.
9. `scripts/muse_reference_render_queue.py` is a strictly opt-in and dry-run-by-default Muse image job generator and audit writer.
10. `assets/CANDIDATE_bubu_FRONT_FULL_BODY_NOT_APPROVED.png` contains one newly generated single-frame candidate, separately from originals.

## Canon approval state machine
`USER_UPLOADED_SOURCE` -> `SOURCE_CROP_UNREVIEWED` -> `DRAFT_GENERATED` -> `REVIEW_REQUIRED` -> (human reviewer accepts + original SHA validated) -> `APPROVED_FOR_REFERENCE`.

**No direct transition from PENDING or DRAFT to production READY** without individual human approval and check. Store approval *per rendered angle*, outfit and face expression; source sheets remain immutable.

## Muse reference-anchoring procedure (official Meta behavior)
- Model: `muse-image-1.0`; Meta Responses API via `client.responses.create()`.
- Upload the user-approved master as `input_image` along with a concise English single-view instruction. Every generated image should be one independent view (front, 3/4, profile, reverse, smile, surprise, mouth shape, action).
- If using a saved compatible Muse conversation, `previous_response_id` can chain from the approved master. Avoid blindly chaining all 10 character conversations together, which risks blended faces.
- Output appears in the response `image_generation_call.result`. Verify completed status and save the original returned bytes plus hashes. Never let the generator set `APPROVED_FOR_REFERENCE` on its own.
- Rendering and API billing require explicit `--execute` and environment variable `MODEL_API_KEY`; **do not upload secrets to GitHub**.
- Source: https://dev.meta.ai/docs/cookbook/anchored-image-series and https://dev.meta.ai/docs/cookbook/image-generation-basics

## Command sequence when the CINE device is online

```sh
# A. Install the SOURCE asset library into your real checked-out CINE repository.
python .claude/skills/cine-a2-muse-reference-anchoring/scripts/install_character_reference_pack.py /path/to/cine /path/to/CINE_A2_CHARACTER_REFERENCE_LIBRARY_V1_1_R1.zip

# B. Run local resolver tests without spending credits.
node --experimental-strip-types --test tests/bellLeafCanonResolver.test.mjs

# C. Validate the first render (dry-run, no API call).
python scripts/muse_reference_render_queue.py --source-pack /path/to/unpacked/source_pack --stage masters --tag Lia --max-jobs 1 --destination /path/to/output

# D. After explicit authorization + pricing confirmation only:
# MODEL_API_KEY=... python scripts/muse_reference_render_queue.py --source-pack ... --stage masters --tag Lia --execute --max-jobs 1 --destination ...
```

Next: human QC of the 10 independent master images, mark approved with actual file hash and reviewer; only then generate 260 remaining views, expressions, mouth and motion/pose references. For group shots, only add approved family group anchors after individual character identities are correct. First-frame output for Flow and Muse should always be a single full 16:9 image, not a 3x3 sheet; generated text/subtitles are forbidden and added later in editorial.

## Quality checks for each image
Exact face, silhouette, eye color, age, body proportions, outfit and signature details; no Bix bell; Bubu exactly one collar bell; Orin has distinct travel bell; no live-action recast; no global warm/yellow/orange cast; physically plausible D55; clean whites; no excessive decorative bells; original location topology; no text, watermark, grid or blurry sidebars. Automated quality tests cannot alone certify human visual identity.

## Epistemic guard
Do not claim that Photoshop cropping creates new unseen camera angles. Do not claim 12 locations are APPROVED when their 1,239 planned plates are still ungenerated. A green backend job is not evidence of correct face geometry. The 270 render slots are tasks, not outputs. Each successful AI-generated file is still a QC candidate until reviewed.