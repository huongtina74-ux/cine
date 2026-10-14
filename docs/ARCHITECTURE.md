# CineFactory OS v0.2 Architecture

## Mission

One prompt should eventually produce a reviewed 4K master through a local-first production line. Agent reasoning may be paid; media generation must not use metered generation APIs.

## Non-negotiable invariants

1. **One owner per decision domain.**
2. Factory Core is the source of truth for project state, jobs, rights and dependency lineage.
3. Prompts are compiled artifacts, never canonical creative truth.
4. Agent thinks; deterministic services execute repeatable work.
5. Storyboard/keyframe validation happens before expensive video generation.
6. Failed shots are selectively repaired; the whole project is not blindly regenerated.
7. An upstream change invalidates only dependency descendants.
8. No production executor may silently fall back to a paid metered API.
9. Final 4K is a mastering contract, not a prompt adjective.
10. Local/LAN media workers may be reachable by the Factory; public-Internet generation workers are blocked.
11. Creative revisions are versioned and immutable; downstream stages cite upstream hashes.
12. Queue state is execution state, not project truth.

## Authority hierarchy

```text
StorySpec
  -> ScriptSpec
  -> AssetBibleSpec
  -> DirectorPlan
  -> ShotSpecBatch
  -> RenderSpec / Workflow manifest
  -> GeneratedArtifact
  -> QCReport
  -> Editorial Timeline
  -> MasterSpec
```

A downstream layer may request repair upstream, but it may not silently rewrite upstream meaning.

## Creative ownership

- Story Engine owns premise, causality, turns and ending.
- Script Engine owns scene execution/dialogue within approved story meaning.
- Asset Engine owns persistent character/scene/prop identities and variants.
- Director Engine owns audience endpoint, performance, blocking, sound and edit intent.
- Cinematography Engine owns motivated shot execution and camera choices.
- Editor Engine owns final editorial timing/order, not story meaning.

## Runtime responsibilities

- **OpenClaw:** executive reasoning/orchestration only.
- **CineFactory Core:** policy, state, rights, continuity, dependencies, jobs, audit, memory.
- **Creative skills:** story/directing/performance/blocking/camera decisions via structured contracts.
- **ComfyUI:** local rendering only.
- **Local models:** image/video/TTS/VLM/ASR/lipsync/upscale workers.
- **OpenChatCut:** canonical editorial timeline only.
- **FFmpeg/local finishing:** deterministic delivery/mastering.

## Persistence

Development defaults to SQLite for zero-friction testing. The repository layer is SQLAlchemy-based and accepts a PostgreSQL URL for production. Canonical accepted media is stored content-addressed by SHA-256 and is never overwritten.

## Job lifecycle

```text
QUEUED -> RUNNING -> SUCCESS
                  -> RETRY -> RUNNING
                  -> BLOCKED      (rights/security/cost hard stop)
                  -> DEAD_LETTER  (retry budget exhausted)
```

Jobs carry deterministic idempotency keys based on project, shot, job type, executor, workflow version and dependency hash.

## Planned production stages

```text
PROMPT
-> POLICY
-> STORY
-> SCRIPT
-> ASSET BIBLE
-> DIRECTOR
-> SHOTS
-> PILOT
-> BATCH
-> SHOT QC
-> SEQUENCE QC
-> EDIT
-> AUDIO
-> COLOR
-> 4K MASTER
-> RIGHTS
-> HUMAN RELEASE
```
