# CineFactory OS 1.6

> **Current engineering readiness (2026-10-10): PARTIAL — not commercially film-qualified.**
> The v1.6 description below documents baseline capabilities, not completion
> of the autonomous media-company objective. For validated v205 cross-department
> wiring, original-media lanes, owner authorization, test evidence and remaining
> release blockers see [v205 integration & acceptance](docs/CINEFACTORY_V205_INTEGRATION_ACCEPTANCE.md).
> The long-term original-channel, series and episode layer is documented in
> [Channel and Franchise OS v206](docs/CINEFACTORY_CHANNEL_LONG_TERM_V206.md).
> [Minecraft subniche, media routing and optional character reuse v207](docs/CINEFACTORY_MINECRAFT_SUBNICHES_V207.md).
> [Channel-first niche classification and precise competitor research v208](docs/CINEFACTORY_CHANNEL_FORENSICS_V208.md).
> [Production governance, script continuity, independent film QC and health v209](docs/CINEFACTORY_PRODUCTION_GATES_V209.md).
> [AI image/video/3D/audio/software/SaaS technology radar v210](docs/CINEFACTORY_AI_MEDIA_TECH_RADAR_V210_20261010.md) — 96 structured candidates, commercial-license gates, read-only CLI.
> [Automatic niche and competitor technology research v211](docs/CINEFACTORY_TECHNOLOGY_DISCOVERY_V211.md) — format-matched recommendations, bounded public GitHub/HF discovery, immutable pending R&D receipts, no automatic installs.
> [Whole-company niche/scene technology council and Claude/MCP/SaaS source watch v212](docs/CINEFACTORY_WHOLE_COMPANY_TECHNOLOGY_V212.md) — daily fixed-source watch, 26 department advisories and production qualification boundaries.
> For a repeatable live snapshot run `python scripts/company_architecture_doctor_v204.py`.

**Local-first AI video production operating system** for:

> **One prompt → research → writing → directing → assets → storyboard → local generation → QC/repair → incremental edit → audio/finish → final video.**

Production rule:

> **Paid agent reasoning may be used. Metered image/video/TTS/ASR/VLM/upscale generation APIs are blocked from the production path.**

## What changed in 1.6

1.6 keeps the dedicated **Block Animation Factory** from 1.5 and closes the biggest renderer gap: scene/prop/crowd/camera/event contracts now reach the persistent Blender execution path. The default `rtx3060_quality` profile is local-first and beauty-oriented while the hard `ZERO_METERED_API` production policy remains unchanged.

### Block Animation Factory

- persistent Blender process with hot collection/action caches
- CharacterRigRegistry + AnimationClipLibrary + Expression/Reaction engines
- executable SceneTemplate runtime: external `.blend` collection or procedural room/classroom/street/arena
- executable PropSocket bindings with timed attach/detach visibility
- crowd cues normalized into real action/expression streams
- camera coverage with DOF and static/push/pull/track/orbit/snap motion
- local VFX execution plus shot/episode semantic event manifests
- `rtx3060_quality`, `rtx3060_fast`, and `preview` quality profiles
- AgX/high-contrast color management, three-point lighting, local materials/bevels, motion-blur hooks
- local FFmpeg black/freeze visual QC in addition to technical probe QC
- deterministic actor facing + basic ground-contact safety
- full-episode GPU queue prefill and concurrent GPU/IO lanes
- originality/reference-token guard retained

Compile and enqueue the included original demo:

```bash
cinefactory block-enqueue \
  --file examples/block_animation/original_episode.json \
  --output-dir data/projects/P_BLOCK_DEMO/block/EP_DEMO_001
```

Run the continuous factory:

```bash
cinefactory block-factory
```

Run target-machine acceptance and RTX 3060 measurement:

```bash
python scripts/acceptance_block_v16.py
python scripts/benchmark_block_rtx3060_v16.py
```

The build environment used to package v1.6 has FFmpeg but does not have Blender or `nvidia-smi`, so real Blender/RTX image quality and performance are deliberately not fabricated.

### Turbo Factory Runtime retained from v1.4

- durable SQLite/WAL Event Bus and cross-project queue
- CPU/GPU/IO/AGENT resource classes
- model-affinity scheduling
- retry/dead-letter and repair memory
- incremental timeline
- FAST/STANDARD/MASTER diffusion lanes
- local GPU telemetry when `nvidia-smi` exists

## Existing production core

- strict project state machine
- SQLAlchemy project/asset/JobLedger storage
- immutable creative artifacts
- Asset Bible / canonical references
- motivated camera and performance contracts
- continuity validation
- originality/authenticity quarantine and competitor-collision checks
- ComfyUI local/LAN adapter
- workflow/model revision registry
- cloud/API workflow safety scanner
- Asset Factory
- keyframe/storyboard gate
- pilot-before-batch
- adaptive multi-take Dailies
- local technical/VLM QC bridges
- Failure Router
- OpenChatCut bridge + FFmpeg fallback
- local TTS/subtitles/audio mux
- local upscale bridge + deterministic 4K mastering
- whole-film QA

## Start

```bash
python -m pip install -e '.[dev]'
cinefactory doctor
```

Start API/Control Room:

```bash
uvicorn cinefactory.api.app:app --host 127.0.0.1 --port 8765
```

Open:

```text
http://127.0.0.1:8765/
```

## Start the always-on daemon

Single-machine example:

```bash
cinefactory factory-daemon \
  --worker-id gpu-0 \
  --resources GPU,CPU,IO \
  --capabilities job.execute,comfy.execute,timeline.accept,blender.previs,blender.animation.render,block.episode.assemble,noop
```

Inspect it:

```bash
cinefactory turbo-status
```

To make real ComfyUI video takes use the durable shared GPU queue instead of calling ComfyUI inline, start the daemon above and add:

```bash
--turbo-dispatch
```

Multiple CineFactory project processes can then submit GPU renders into the same model-affinity queue. The planner/editor can continue on CPU/agent lanes while the GPU daemon drains render work.

OpenClaw should call the Turbo status/events interfaces and supervise by exception; it should not busy-poll ComfyUI or write CineFactory's database directly.

## RTX 3060 12 GB

A scheduling profile is included at:

```text
profiles/hardware/rtx3060_12gb.yaml
```

It intentionally does **not** claim a generic render time. CineFactory records actual local throughput and should choose ETA/lane policy from measured runs on the target PC.

## Complete zero-API software-path acceptance

```bash
cinefactory run \
  --prompt "An original fictional story about a difficult family choice" \
  --profile cinematic_story \
  --production-mode slate \
  --tts-mode none \
  --allow-no-visual-qc \
  --no-master-4k
```

`slate` mode proves the production software path with diagnostic media. It is not evidence of AI footage quality.

## Turbo API

Important supervisor endpoints:

- `GET /turbo/status`
- `GET /turbo/gpu`
- `GET /turbo/work`
- `POST /turbo/work`
- `GET /turbo/events`
- `POST /turbo/events`
- `GET /turbo/workers`

See `integrations/openclaw/tool-contract.yaml`.

## Verification

Current build verification:

```text
compileall: PASS
pytest: 66 passed
block v1.6 acceptance: compile/plan, queue prefill, persistent-protocol, zero-API visual QC and FFmpeg assembly PASS
real Blender/RTX acceptance: not run in build environment (Blender/nvidia-smi unavailable)
Turbo daemon durable-work smoke test: PASS
```

## Important limitation

1.6 retains the real durable Turbo runtime and integrates event emission, lane routing, logic gating, repair memory and incremental editing into production. However, **the entire legacy Autopilot creative chain is not yet split into independent DAG work nodes**. That is the next major step required for true multi-project stage overlap at all times.

Read:

- `docs/TURBO_FACTORY_ARCHITECTURE.md`
- `docs/CURRENT_GAP_AUDIT.md`
- `docs/ORIGINALITY_AUTHENTICITY.md`
- `docs/PRODUCTION_SETUP.md`
