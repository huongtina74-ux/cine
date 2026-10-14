# CineFactory v1.6.1 RTX3060 Validation

Date: 2026-09-26  
Host: Windows 10 Pro 22H2, build 22621  
Scope: v1.6.1 Block Animation baseline only

## Decision

Status: READY for the validated v1.6.1 Block Animation baseline.

This is a bounded acceptance decision: the real render completed on the available RTX3060, the persistent worker behaved correctly during full passes, the final master passed technical QC, the before/after frames were inspected, and the regression suite is green. It does not claim that dialogue/audio, Minecraft/Roblox execution, hybrid routing, geometry-aware IK, semantic VLM QC, or true hand-to-hand prop transfer are complete.

## Host and toolchain

- GPU: NVIDIA GeForce RTX 3060, 12,288 MB VRAM, compute capability 8.6, driver 610.47.
- CPU: 20 logical processors, Intel64 Family 6 Model 151 Stepping 2.
- Memory: 31.85 GiB total; observed available sample 15.7–16.0 GiB.
- Python: 3.11.15; pip 26.1.2.
- Blender: 4.5.14 LTS portable executable under .tools; the PATH lookup was initially unavailable, so the validation scripts used CINEFACTORY_BLENDER_EXECUTABLE explicitly.
- FFmpeg: 7.1 essentials build; ffprobe was available.
- Python torch was 2.13.0+cpu with CUDA unavailable. This is recorded separately from the successful Blender GPU render, which was corroborated with nvidia-smi snapshots.
- No paid or metered API was used.

Full machine evidence is in data/validation/v1.6.1/system_report.json.

## Code integrity

The source and required architecture were reviewed before edits. A Git baseline was created at commit 2ae6809:

    CineFactory v1.6 baseline before RTX3060 validation

Final verification:

- pytest: 67 passed, 0 failed, 0 skipped.
- compileall: PASS.
- Existing acceptance harness: PASS for its zero-API, planning, queue, persistent mock-worker, QC, and FFmpeg checks.
- The existing acceptance harness still reports its internal real_blender_render check as SKIP because it searches PATH. The dedicated real-Blender validation path passed with the explicit portable executable.

See data/validation/v1.6.1/baseline_test_report.json.

## Real RTX3060 benchmark

The original v1.6 block benchmark rendered with the real Blender worker:

- 2 shots, 640x360, 108 total frames.
- Total selected render time: 41.890 seconds.
- Average: 0.3879 seconds/frame, approximately 2.578 frames/second.
- Worker PID 33880 persisted across both shots.
- Peak observed VRAM: 710 MB.
- Peak observed GPU utilization snapshot: 92%.
- Both H.264 outputs passed technical visual QC.

Evidence: data/validation/v1.6.1/rtx3060_raw_benchmark.json.

## Beauty benchmark

The required beauty benchmark rendered a 49.5-second target episode at 1920x1080 and 24 fps. The assembled master measured 49.639333 seconds.

Before fixes:

- 12 shots, one persistent worker PID 35588.
- Selected shot render total: 912.221 seconds, about 15.20 minutes.
- Average: 0.7679 seconds/frame, about 1.302 frames/second.
- Median shot: 0.7879 seconds/frame.
- Peak observed VRAM: 736 MB.
- Peak observed GPU utilization snapshot: 98%.

After fixes, selected final shots:

- 12 shots, full initial after pass persisted on PID 40648.
- Selected shot render total: 991.093 seconds, about 16.52 minutes.
- Average: 0.8343 seconds/frame, about 1.199 frames/second.
- Median shot: 0.8631 seconds/frame.
- Peak observed VRAM: 704 MB.
- Peak observed GPU utilization snapshot: 97%.
- BEAT08 was intentionally retaken in a second worker (PID 37196) after human review; its replacement render is included in the final selected aggregate. Therefore the final assembled artifact contains outputs from two worker PIDs, while each complete before/after pass itself demonstrated same-PID persistence.

GPU numbers are sparse nvidia-smi before/after snapshots, not continuous traces. Cache hit/miss rates and idle periods were not instrumented and are reported as NOT_AVAILABLE.

## Visual review

The before review found three actionable P1 issues:

1. The procedural face direction was reversed in close shots.
2. Prop sockets attached to the actor root rather than the visible arm geometry.
3. Prop-targeted framing ignored the prop and made the presentation beat too tight.

The fixes corrected face yaw, mapped hand sockets to the procedural arms, preserved prop_id through camera planning, and made the Blender worker target the prop object. The presentation camera was then retaken with both principal actors and the book readable in the same frame.

The final spot review found no black, frozen, corrupt, or obviously unrendered frames. Remaining limitations are documented: some stylized group/orbit edge cropping and occlusion, no geometry-aware IK/contact, no true hand-to-hand transfer, and no semantic visual QC beyond technical checks plus human inspection.

See data/validation/v1.6.1/visual_findings.md, data/validation/v1.6.1/fixes_applied.md, and data/validation/v1.6.1/remaining_gaps.md.

## Artifacts

- Final master: data/validation/v1.6.1/beauty_benchmark_001_after.mp4
- Before master: data/validation/v1.6.1/beauty_benchmark_001_before.mp4
- Final copied master: data/validation/v1.6.1/beauty_benchmark_001/master.mp4
- Performance report: data/validation/v1.6.1/performance_report.json
- Acceptance report: data/validation/v1.6.1/final_acceptance_report.json

Recommended next milestone: add semantic camera/composition checks and geometry-aware contact/prop-transfer primitives, then repeat this real-render protocol before expanding runtime scope.
