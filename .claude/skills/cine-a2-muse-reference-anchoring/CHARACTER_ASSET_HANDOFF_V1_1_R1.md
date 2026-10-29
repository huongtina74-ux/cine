# CINE Slow English A2 v1.1 — Character reference asset handoff r1

**Source pack in the user's private persistent ChatGPT Library:** `/CINE/Slow_English_A2/Character_Reference_Packs/CINE_A2_CHARACTER_REFERENCE_LIBRARY_V1_1_R1.zip`.

**SHA-256 ZIP:** `fb5def14f694479a80090819d818e09553cdebae4a3633f70caf975e5960f3ec`

## Real asset inventory

- 10 original user-provided character reference sheets stored byte-for-byte.
- 90 PNG individual `SOURCE_CROP_UNREVIEWED` images taken from the user's sheets (1 master candidate + 4 angle/wardrobe candidates + 4 expression crops for each tag).
- 90 1152×1152 padded JPEG previews. These are resize/padding conveniences, not newly generated perspectives.
- 270 new target render slots (27 per character: master + alternate angles + facial emotions + lip shapes + action poses + costume/detail); **ALL PENDING_NEW_RENDER**.
- Hash-backed JSON registry and CSV, 270 one-line English Muse prompts with exactly one blank line between prompts.
- Import script with integrity checks, no overwrite, no auto approval.

**Do not make false claims:** no live Meta Muse API render or native CINE desktop installation has been completed by this PR; the user's computer is offline. The one newly generated Lia reference sheet is a composite/contact sheet and is NOT an approved standalone 3D angle. Source crop images do not prove model identity across unseen camera views.

## Install assets into actual CINE worktree

Download the named ZIP from the user's Library (or the matching conversation artifact). On the CINE device after it is online, run:

```bash
python .claude/skills/cine-a2-muse-reference-anchoring/scripts/install_character_reference_pack.py /path/to/cine /path/to/CINE_A2_CHARACTER_REFERENCE_LIBRARY_V1_1_R1.zip
```

The importer verifies hashes and copies all assets to `assets/canon/character_refs/slow_english_a2/v1_1_r1`. It does not modify any approved `CURRENT` pointer, store a fake Muse media ID, alter user source images, or mark images approved.

## Muse and shot pipeline gates

**Required next operations**: independently generate the 270 target images with actual approved Muse Image access (no unapproved charges), reject ID drift and artifacts, record generated file/hash and original response ID, and approve views one-by-one. CINE's reference resolver must use structured visible `activeCharacterTags`, approved independent view IDs and matching approved location plates, never regex over the full prompt or all ten family images. Voice identity comes from WAV/voice registry, not image prompts. One shot image = one clean native 16:9 CGI frame, no subtitle/contact sheet.

## Known canon warnings

- `bix` original reference sheets may show an extra bell; canon forbids Bix having one.
- `bubu` owns a collar bell; `ongngoai` has an independent travel bell; Bell House has one home bell.
- `me` refers to Mara; do not redirect to reserved personal `@me` reference.
- `bangoai` should not be depicted in currently unresolved Veylora story beats without approved scene logic.
- Generated extra props/wardrobe on reference concept sheets are not inherently approved.

**Location Lock:** the separate `cine-bellfern-location-multiview-lock` skill remains authoritative for buildings and interiors. The purpose is eventually 10 human-approved robust multi-angle character packs, not merely the 10 uploaded concept boards.
