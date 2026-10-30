# CINE Slow English A2 v1.1 — FIXED 10S / Asset Bridge R2

This package is **not** a set of 1,239 generated photos. It is a verified, source-backed preparation bridge between the user's eight A2 production skills and their permanent Bell & Leaf visual libraries.

## Verified evidence

- Registry: 12 sites / 69 spaces / 108 recurring props; exact location manifest 483 requested plates, exact prop manifest 756 requested plates.
- Current **actual generated and human-approved plates in these manifests: 0**. All manifest rows remain `PENDING_NOT_GENERATED` and must not be silently changed.
- 12 composite location concept sheets exist. They are drafts and contain design conflicts with the registry. The 12 exterior samples are crops of original panels, NOT new camera-angle renders, and contain low-resolution/text artifacts. They are NOT approved and must not be used as the definitive topology.
- 10 source character concept sheets + 90 pixel-provenance source crops (10 masters, 40 angle/outfit crops, 40 expressions); hash-verified, no new 270 genuine Muse renders. Bubu spiral tail sparkle detail must be attached as identity anchor; avoid changing facial proportions or age.
- No approved WAV found within this package, no actual continuous Muse I2V 10.0 s render and voice sync proven. Any 10s spec is a planned timeline constraint until real provider QC.

## 8 skills that must enforce this bridge

1. `cine-a2-orchestrator`: before production, require validated source images, approved location/character refs, voice registry; fail closed instead of inventing refs.
2. `cine-a2-script-director`: annotate each scene with site_id / space_id and visible character tags, with A2 dialogue timing.
3. `cine-a2-shot-director`: every clip EXACT planned 10.0 seconds; camera and reverse angle follow approved topology with real physical positions.
4. `cine-character-continuity`: use exact original face/body sources and approved standalone view/expression refs. `bangoai` is a 10th conditional character; do not silently drop her or force her in every episode.
5. `cine-voice-performance`: require fixed speaker IDs, approved WAV/transcript with usage rights, believable expression and dialogue, no unverified 'fixed voice' from text instructions.
6. `cine-muse-image`: output one standalone 16:9 image; no collage, title, watermark, caption, or subtitle; D55 neutral color science and no yellow cast. One complete prompt on one line; exactly one empty line between prompts in TXT.
7. `cine-muse-video`: take approved image as first frame, visible character action (not camera-only zoom), sync to approved WAV only if actual provider allows this. Verify video using ffprobe and manual frames. If provider does not deliver 10.0 s, block; never fake duration with frozen frames.
8. `cine-a2-production-qc`: verify independent source hashes, 16:9 minimum 1280x720, true perspective, identity/architecture/prop consistency, no embedded text or multi-panel, human visual review, approved voice, exact 10 s final video.

## Use today (no provider API/credits required)

```bash
python scripts/build_asset_queue.py
python scripts/audit_and_import.py
python scripts/run_queue_sequential.py --start 0 --limit 1
python -m unittest discover -s tests -v
```

For live image generation, set a **legitimately installed provider CLI** with an explicit account and a command accepting `{prompt_file}` and `{output_file}`. No API endpoint/provider entitlement is invented here:

```bash
python scripts/run_queue_sequential.py --execute --start 0 --limit 1 --command-template 'your-authorized-provider --prompt-file {prompt_file} --output-file {output_file}'
```

This does NOT automatically attach approved source media IDs, because the actual approved scene/location images and Meta Muse IDs don't exist yet. Where the provider supports references, its adapter must supply the exact approved media IDs separately and must not send all 10 characters to every shot. **Never run 1239 paid calls before approving first master, true reverse, and single-image QC.**

## Location blockers to resolve

- `BELL`: draft sheet's attic workshop is inconsistent with registry's workshop east annex and secret chamber BELOW it.
- `BRIDGE`: draft image may show multiple arches, registry calls for ONE stone arch.
- `POST`: draft renders an overly grand 2-storey building, registry specifies smaller single-storey + attic with BLUE entrance.
- `LAKE`: draft labeled *Moonwater* and looks like larger waterside complex; registry locates simple Bellfern lake, small single-storey gray boathouse, one rowboat, stable dock.
- `SCHOOL`: some concept render is larger/fancier than an ordinary Earth community school. Keep 11yo Lia and 13yo Juno in separate age appropriate wings.
- Other locations also require topology review; a concept sheet never substitutes measured floorplan or physically true reverse shot.

## Production readiness gates

- ST05: approve topology, orientation and immutable set props.
- ST10: generate each independent plate, visual QC and record canonical SHA-256 before APPROVED.
- ST12: compile Flow first-frame only from approved character/location/prop refs; Muse I2V 10.0s only after real verification.
- ST15: independent QC; no green PASS from mock tests or green UI labels without actual images/WAV/video evidence.

## Install to CINE desktop (when the machine is ONLINE)

Keep original zip copies in external private storage, or import into project asset storage intentionally; do not add 87MB of binary references to GitHub without review. Pull reviewed GitHub skill changes, unpack this package, run audit, then use this bridge as a first-class dependency in `cine-a2-orchestrator`. Do not override existing Canon/current pointers with the 12 draft sheets or candidate generated faces. New images and voice artifacts require separate human approvals. The currently connected `DESKTOP-HJE6A6D` was offline at this inspection, so a live CINE install is **unverified**.