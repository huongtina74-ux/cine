# Changelog

## 1.6.0

- Added RTX 3060 local render-quality profiles with zero metered production API use.
- Added BlockExecutionPlanner between EpisodeAssembler and Blender.
- Executed scene templates through external `.blend` collections or procedural room/classroom/street/arena sets.
- Executed prop socket lifecycle, crowd actions/expressions, camera motion/DOF, and local VFX events.
- Added three-point lighting, AgX/high-contrast color management, local materials/bevels and higher-quality encoding defaults.
- Added actor facing and basic ground-contact safety.
- Added zero-API FFmpeg black/freeze visual QC and semantic event sidecars for later audio/edit stages.
- Kept the persistent hot Blender worker and collection/action caches from v1.5.
- Verification: compileall PASS, pytest 66 passed. Real Blender/RTX rendering remains target-machine acceptance.

## 1.5.0

- Added Block Animation Factory while retaining v1.4 Turbo/diffusion paths.
- Added CharacterRigRegistry, AnimationClipLibrary, ExpressionEngine, ReactionEngine and PropSocketSystem.
- Added SceneTemplateLibrary, CameraCoverageEngine, CrowdBehaviorEngine and semantic VFX/Sound events.
- Added EpisodeAssembler with deterministic QC and safe timing repair.
- Added reference-token originality boundary for production episode contracts.
- Added persistent Blender JSONL worker, hot collection/action caching, external `.blend` hooks and procedural block fallback.
- Added reusable camera takes through `camera_take_id`.
- Added full-episode GPU queue prefill and concurrent GPU + IO factory lanes.
- Added FFprobe render QC and FFmpeg episode assembly.
- Added recursive dependency failure propagation to `BLOCKED`.
- Added `block-compile`, `block-enqueue`, and `block-factory` CLI commands.
- Added target-machine Blender acceptance and RTX 3060 benchmark scripts.
- Verification: compileall PASS, pytest 60 passed, persistent same-PID protocol PASS, FFmpeg diagnostic assembly PASS.
- Real Blender/RTX performance is not claimed in the packaging environment because Blender and `nvidia-smi` are unavailable there.

## 1.4.0

- Added `cinefactory.turbo` always-on control plane.
- Added durable SQLite/WAL factory events and work items.
- Added dependency-aware, cross-project work scheduling.
- Added model-affinity scheduling to reduce GPU model swapping.
- Added optional `--turbo-dispatch` path so ComfyUI video takes use the shared durable GPU queue instead of direct inline provider calls.
- Added worker heartbeat/capability/resource registry.
- Added `factory-daemon`, `turbo-status`, `turbo-enqueue`, `turbo-job`, and `logic-check` CLI commands.
- Added Turbo Control Room API endpoints and live local UI status.
- Added local GPU telemetry through `nvidia-smi` when present.
- Added throughput measurement and seconds-per-unit learning.
- Added FAST / STANDARD / MASTER video workflow lanes.
- Added lane/workflow grouped render order after pilot approval while preserving editorial order.
- Added pre-render deterministic logic gate and safe missing-state reconciliation.
- Added incremental timeline journal updated as each shot is accepted.
- Added persistent repair memory keyed by failure/workflow/shot class.
- Integrated Repair Memory with VideoFactory retries.
- Added production event emission for queue/accept/fail/pilot/finish events.
- Added restricted Blender headless previs worker and bundled whitebox renderer.
- Updated OpenClaw supervisor contract for event/status/worker interfaces.
- Added RTX 3060 12 GB scheduling profile (policy only; no fabricated performance claim).
- Added Turbo architecture documentation.
- Test suite increased to 52 passing tests.

## 1.3.0

- Canonical Asset Factory.
- Storyboard/keyframe hard gate.
- Pilot-before-batch.
- Multi-take Dailies selection and early stop.
- Local VLM QC integration points.
- Typed Failure Router.
- Workflow/API-node safety scanning.
- Exact model revision production approval.
- Whole-film QA and improved post bridges.
