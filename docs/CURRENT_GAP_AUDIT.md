# Current Gap Audit — CineFactory OS 1.6

## Closed or materially improved

- Durable always-on Turbo runtime, event bus, queue, dependency blocking, model affinity: **implemented**.
- Persistent Blender process with collection/action cache: **implemented**.
- Rig/clip/expression/reaction/prop/scene/camera/crowd/event registries: **implemented**.
- EpisodeAssembler deterministic compilation + safe timing repair: **implemented**.
- Renderer execution bridge (`BlockExecutionPlanner`): **implemented**.
- Scene execution: external `.blend` collection or procedural room/classroom/street/arena: **implemented**.
- Prop timed socket attachment: **implemented**.
- Crowd cue execution through action/expression streams: **implemented**.
- Camera DOF and static/push/pull/track/orbit/snap motion: **implemented**.
- Local VFX event execution + semantic event sidecars: **implemented**.
- RTX 3060 quality/fast/preview render profiles: **implemented as policy/settings; target-machine beauty benchmark still required**.
- Local black/freeze render QC: **implemented**.
- Zero-metered-production-API policy: **retained**.

## Critical remaining gaps

1. **Real target-machine Blender acceptance** — image quality, Blender-version compatibility, VRAM, seconds/frame and stability still require the actual RTX 3060 PC.
2. **Geometry-aware IK/contact** — v1.6 has deterministic facing/basic ground safety and bone/socket prop attachment, but full foot lock, hand IK, seat/contact solving and self/inter-object penetration repair are not complete.
3. **Semantic local visual QC** — black/freeze QC is real; identity, hand-contact, foot-slide, clipping, framing and expression-quality judgments still need geometry checks and/or a local VLM bridge.
4. **Dialogue Performance Engine** — per-line voice takes, forced alignment, visemes/lipsync, speech gesture and emotion timing are not complete for Block Animation.
5. **Audio Director** — semantic sound events are preserved, but automatic local Foley/SFX/music selection, ducking and final mix decisions are not complete.
6. **Minecraft/Voxel gameplay backend** — world interactions, structure generation, NPC/mob control, state checkpoints and replay cameras are not implemented yet.
7. **Roblox Studio backend** — R6/R15 adapters, Studio scene runtime, pathfinding, facial performance and capture bridge remain future work.
8. **Hybrid Shot Router** — automatic per-shot choice among Blender, Minecraft/Voxel, Roblox Studio and local AI is not implemented yet.
9. **CharacterFactory / cross-backend identity** — one prompt/image → stable Minecraft skin + Roblox avatar spec + Blender rig + voice/facial profile remains future work.
10. **Full autonomous edit/audio/master/publish-readiness loop** — existing post core is real, but the Block Universe vertical still needs tighter semantic integration and repair routing.

## Next build order

`RTX3060 beauty acceptance → IK/contact + semantic visual QC → Minecraft/Voxel runtime → dialogue/audio → Roblox Studio runtime → Hybrid Shot Router → CharacterFactory → v2.0 prompt+characters-to-finished-episode acceptance`.
