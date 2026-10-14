# Milestones

## M0 — Core integrity ✅

- ZERO_METERED_API hard policy
- project state machine
- core schemas
- dependency graph
- deterministic continuity validator
- executor contract/registry
- API + CLI project creation

## M1 — Persistent production core ✅ foundation complete

Implemented in v0.2:

- SQLAlchemy project persistence
- SQLite dev database / PostgreSQL-compatible URL
- append-only audit events
- JobLedger
- idempotency keys
- attempts + typed retry rules + dead-letter state
- persistent asset/right records
- content-addressed artifact storage

Still to add before production deployment:

- Alembic migrations
- PostgreSQL integration tests
- Redis/Celery worker process
- asset/creative indexes optimized for large projects
- WORM/off-machine evidence backup

## M2 — Creative vertical slice ✅ contract layer complete

Implemented in v0.2:

- StorySpec
- ScriptSpec
- AssetBibleSpec
- DirectorPlan
- BlockingMap
- performance/camera structured output
- ShotSpecBatch
- stage authority contracts
- immutable versioned creative artifacts
- cross-stage validators
- golden family-drama scenario
- OpenClaw high-level tool contract draft

Next M2 work:

- actual OpenClaw adapter/tool registration
- Director prompt compiler/skill pack
- camera grammar test corpus
- sequence-level shot grammar validator
- dependency indexing from creative artifacts to generated media

## M3 — Local image path (next build target)

- pin ComfyUI version/custom-node allowlist
- WorkflowRegistry enforcement
- approved Qwen-Image/local image workflow
- canonical character sheet workflow
- scene/prop reference workflows
- deterministic image technical QC
- local VLM identity/composition QC
- canonical-asset approval gate

## M4 — Local video path

- pinned Wan workflow
- keyframe/I2V/first-last routing
- shot complexity -> candidate count
- pilot-before-batch
- local shot QC
- Failure Router + targeted repair
- selective dependency invalidation

## M5 — Audio path

- local TTS adapter
- voice direction + pronunciation dictionary
- local ASR timing verification
- optional local lipsync
- dialogue/ambience/SFX/music stems

## M6 — Auto edit

- OpenChatCut adapter
- EditIntent -> timeline operations
- captions/audio stems
- sequence QC

## M7 — 4K finishing

- local upscale benchmark
- temporal QC
- color normalization
- sound mastering
- FFmpeg master profiles
- 3840x2160 final validation

## M8 — Autopilot

- prompt -> complete master
- exception-only paid reasoning
- human release gate
- production memory / controlled learning
