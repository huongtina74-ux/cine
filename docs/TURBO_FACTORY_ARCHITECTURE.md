# CineFactory Turbo Factory Architecture — 1.4

## Goal

Keep production moving continuously: planning can run ahead, GPU work is durable and model-aware, accepted shots enter the rough cut immediately, logic errors are caught before diffusion, and repeat failures learn a preferred repair strategy.

## Patterns audited from strong open-source systems

CineFactory does not copy whole factories into production. It adopts the patterns below behind CineFactory-owned state/contracts.

- **OpenClaw**: separate queue lanes, bounded sub-agent concurrency, restart/recovery behavior, and Gateway-owned queued work. CineFactory mirrors the idea that the supervisor should not block while a long tool run is active.
- **Wintercom/ai-short-drama**: checkpoint/resume and reuse of completed artifacts after interruption. CineFactory's durable work queue, immutable artifacts and idempotent JobLedger follow the same production principle.
- **ComfyUI-Distributed**: worker dispatch and least-busy/load-balanced execution. CineFactory keeps this below its own JobLedger; distributed ComfyUI transport never becomes project truth. Its lack of auth is why CineFactory still requires loopback/LAN isolation.
- **VideoClaw**: OpenClaw as a high-level production employee/supervisor while the video service runs locally behind an API. CineFactory exposes only thin supervisor endpoints to OpenClaw.
- **FireRed-OpenStoryline**: editing is an executable workflow, not a final concat step; rough-cut operations can be incremental and tool-driven. CineFactory now journals accepted shots into an incremental timeline before the full batch finishes.
- **LTX-Video distilled families**: a fast/distilled lane can be materially different from a master-quality lane. CineFactory therefore supports FAST / STANDARD / MASTER workflow IDs rather than forcing every shot through one heavy graph.

## 1. Always-on control plane

`TurboStore` is a durable SQLite/WAL control plane with:

- factory events
- cross-project work items
- worker heartbeats
- model affinity
- retry/dead-letter state
- repair statistics
- measured throughput

Creative/project truth remains in CineFactory Core. Turbo state is execution state only.

## 2. Event-driven work

Representative events:

- `PRODUCTION_STARTED`
- `SHOT_RENDER_QUEUED`
- `SHOT_ACCEPTED`
- `SHOT_FAILED`
- `PILOT_PASSED`
- `PRODUCTION_FINISHED`
- `WORK_SUCCEEDED`
- `WORK_FAILED`

OpenClaw should react to these events instead of busy-polling ComfyUI.

## 3. Cross-project scheduler

Ready work from all projects competes in one queue. A work item declares:

- resource class: CPU / GPU / IO / AGENT
- dependencies
- priority
- handler capability
- model affinity

Dependencies are hard gates. Among ready jobs, the scheduler gives a hot-model bonus to jobs matching the worker's current model affinity. This reduces expensive model swaps on a single 12 GB GPU.

## 4. Shared GPU dispatch

With `--turbo-dispatch`, ComfyUI video takes are submitted as durable `comfy.execute` GPU work instead of being invoked directly by the project process. This allows multiple project/planning processes to share one GPU queue safely. The daemon records the result back into the work item and the waiting production stage resumes from that result.

This makes model-affinity scheduling effective across projects, not only inside one batch.

## 5. Speed lanes

Video shots can use three independently pinned workflows:

- FAST — simple GREEN shots / proof lane
- STANDARD — YELLOW/RED controlled I2V
- MASTER — HERO shots only

When lane-specific workflows are configured, CineFactory renders remaining shots grouped by lane/workflow while preserving original editorial order.

## 6. Pre-render logic simulator

Before video generation, `PreRenderLogicGate`:

- fills only missing continuity state from the previous shot
- validates shot links
- validates action timing
- blocks explicit costume/prop/location contradictions
- surfaces position/facing/eyeline changes as review warnings rather than rewriting explicit intent

It never overwrites an explicit creative decision. Expensive generation should not be used to discover deterministic continuity mistakes.

## 7. Incremental editor

As soon as a shot passes Dailies, it is journaled into `post/incremental_timeline.json` in editorial order. The rough cut can therefore be assembled progressively instead of waiting for the last shot to render.

## 8. Repair memory

Failure Router still owns failure classification. Repair Memory records which constrained repair strategy worked for a specific:

`failure_code + workflow + shot complexity`

Future retries prefer the strongest observed strategy rather than relearning the same fix every time.

## 9. Throughput learning

Every video take and daemon work item records elapsed time and output units. `turbo-status` reports learned `seconds_per_unit`. Hardware ETA should be derived from measured local samples, not generic internet benchmarks.

## 10. Blender headless worker

CineFactory includes a restricted Blender previs contract and bundled headless scene worker. It creates deterministic whitebox geometry/camera previews from structured transforms. It is for spatial/camera proofing, not a second source of story truth.

## 11. OpenClaw role

OpenClaw is the supervisor:

- inspect factory status / GPU / workers / failures
- submit high-level work
- request targeted repair
- continue planning future projects while GPU workers render

OpenClaw must not directly mutate the DB, install random models/nodes, or own ComfyUI state.

## Remaining architectural gap

The legacy `AutopilotRunner` is still a synchronous vertical slice. 1.4 adds the durable always-on control plane and integrates events, logic-gating, repair memory, lane routing and incremental editing into real production, but not every creative stage has yet been decomposed into an independently schedulable DAG node. Full stage-level eventization is the next major throughput milestone.
