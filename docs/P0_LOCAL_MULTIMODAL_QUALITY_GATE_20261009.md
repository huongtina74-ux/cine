# CineFactory P0 — Local Multimodal Vision Gate
October 9, 2026 | State: FUNCTIONAL PIXEL EVIDENCE + MODEL ADAPTER TESTED; VLM SEMANTICS NOT PRODUCTION VALIDATED

## Why this exists

Previous canonical Company Youtube research → evidence-live → public image triage → single CineCouncil issue and the local video observation were working, but scene observations were not yet formalized as machine-reproducible pixel measurements, and no local model vision reviewer was operational.

This upgrade implements a source-verified, no-cloud, zero-paid-API model adapter plus strict manual Quality handoff. **It does not claim that a vision LLM viewed or understood the three MSToons videos.**

## Reused modules and new code

- Existing `core.py / smart.py`: timestamped frame JPEG extraction and audio measurements from authorized local footage. No third-party video download.
- New `scene_measurement.py`: SHA256-replay of observed frames, RGB/luminance, edge variance, frame sample-to-sample pixel difference. Stores `scene_measurements.json` in local deep-video run. These are sparse sampling proxies, never verified story, movement, music, editing pace or causal retention.
- New `local_vision_adapter.py`: only accepts a *validated* `deep_review.json` (public thumbnail images) or `scene_measurement.v1` (authorized local frame samples). Strict bounded ≤4 images, each ≤3MB and source-hash checked. Only allowlisted loopback HTTP `http://127.0.0.1:<port>/v1/chat/completions`; no internet/cloud API, paid model, GPU download or secrets. Blocks redirects, caps response, requires explicit `--execute --model MODEL_ID`. Verifies model findings cite the correct visible image ID and timestamp and stores all as `MODEL_HYPOTHESIS_PENDING_QA`, not ground truth.
- New `vision_quality.py`: checks claims against original image hashes/time and same CineCouncil issue. Outputs `INDEPENDENT_IMAGE_REVIEW_PENDING`, never self-approved.
- `deep_video_intelligence.py` now automatically computes reproducible pixel measurements when sampling any authorized local video.
- `__main__.py` exposes `scene-measure`, `vision-local-review`, `vision-quality-packet`.

## Live evidence from this Windows machine

Machine: `DESKTOP-HJE6A6D`; RTX 3060 ~12 GiB VRAM, approximately **8.8 GiB reported in use** during readiness probe. No running local vision API responded at 127.0.0.1:11434 / 1234 / 8000. Avoided loading any large model into current GPU and affecting users' workflows.

1. Existing authorized synthetic MP4 source (testsrc + audio sine) was observed in **8 actual frame JPEGs** using ffmpeg; then `scene-measure` produced `HASH_VERIFIED_OBJECTIVE_FRAME_FACTS`. Mean sampled pixel change proxy ~0.0493/1. This is test footage, not downloaded competitor video.
2. Existing real public metadata and exact MSToons thumbnail review from `evidence_live_04/deep_intelligence/deep_review.json` was passed to `vision-local-review` WITHOUT `--execute` and safely produced `BLOCKED_NO_LOCAL_VISION_MODEL` with 0 invented claims, production false.
3. `vision-quality-packet` created `INDEPENDENT_IMAGE_REVIEW_PENDING` for the same original council issue; still no human review or model output.
4. Re-ran `deep-video-local` on owned synthetic MP4 (8 frames, audio measurement) and confirmed the newly integrated per-frame statistics file and unchanged department tasks.
5. In unit/integration tests a deliberately stubbed local model response citing a real frame/timestamp was accepted only as a **hypothesis**, while fabricated frame IDs, unauthorized endpoint URLs, changed JPEG evidence, invalid full-video interpretation scope, inflated production approval, and stale original hashes were rejected.

On-disk replay files:
`C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\synthetic_observed_v2\scene_measurements.json`
`C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_04\deep_intelligence\vision_readiness.json`
`C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\evidence_live_04\deep_intelligence\vision_quality_pending.json`

## Execution (PowerShell in CineFactory repo)

```powershell
python -m cinefactory.research_intelligence deep-video-local --source "C:\path\to\authorized.mp4" --output-dir "C:\CineResearch\unique_new_run" --niche "Minecraft animation" --video-id "XXXXXXXXXXX" --authorization OWNED --max-frames 12
# For local scene evidence, this command now also writes scene_measurements.json

python -m cinefactory.research_intelligence vision-local-review --source "C:\CineResearch\unique_new_run\scene_measurements.json" --output "C:\CineResearch\unique_new_run\model_readiness.json" --role visual

# ONLY once a tested local VLM server exists with adequate free VRAM and explicit intent:
python -m cinefactory.research_intelligence vision-local-review --source "C:\CineResearch\unique_new_run\scene_measurements.json" --output "C:\CineResearch\unique_new_run\vision_model_new_run.json" --role visual --model "actual-local-vision-model-id" --endpoint "http://127.0.0.1:1234/v1/chat/completions" --max-images 2 --execute

python -m cinefactory.research_intelligence vision-quality-packet --model-review "C:\CineResearch\unique_new_run\vision_model_new_run.json" --output "C:\CineResearch\unique_new_run\quality_new_run.json"
```

- No `--execute` = create a blocked readiness report, never imply inference.
- `--execute` and unreachable model = `MODEL_RUN_FAILED` with nonzero CLI exit (failure doesn't allow misleading success).
- A working local model response must follow structured JSON, exact image ID/time and visible image scope; any string response unsupported by the contract fails.
- Model claims are not independent source corroboration even if multiple roles use the same model. Independent inspection is essential for Quality; no approval is generated automatically.
- Do not copy or reconstruct copyrighted scripts or footage. Competitor media research must respect rights and licensing.

## Next technical acceptance targets

- Connect a **verified** appropriately quantized local VLM to the existing loopback API *when* GPU memory is actually available; measure VRAM peak, inference latency, output parse success rate, and grounded visual precision on labeled sample frames. Do not choose a model from advertisement/spec alone.
- Expand objective audio/timeline diagnostics where authorized media exists and compare scene descriptions against independent human annotations.
- Build a data-backed multimodal review benchmark with multi-frame and missing-transcript samples, English/high-RPM languages and explicit uncertainty, then provide CineCouncil actual reviewed opinions and real Quality rebuttal.
- Later integrate authenticated owner approval for niche promotion and dedicated Research Pod; never automatically publish because a model agrees with itself.
