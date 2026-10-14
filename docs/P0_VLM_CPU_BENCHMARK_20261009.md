# P0 — First REAL Local Vision Model Benchmark (9 October 2026)

Status: EXECUTED. This candidate/configuration is **REJECTED FOR DEPLOYMENT**, not a validated AI video analyst.

## Objective and machine constraints

The owner's intent is a zero-paid-API AI media company with dependable multimodal competitor research. Reuse CineFactory's immutable YouTube evidence chain, Deep Video source hashes, and CineCouncil; avoid new duplicate scanners.

- PC: DESKTOP-HJE6A6D, NVIDIA RTX 3060 (12288 MiB). At probe GPU usage was **8820 MiB** and available VRAM **3294 MiB**. Other user's GPU processes remain active; no forced resource reclamation.
- CineFactory's current Python uses `torch 2.13.0+cpu` (`torch.cuda.is_available() == False`), transformers 5.16.1; NVIDIA GPU acceleration is NOT available in this Python runtime. System had ~12.8 GiB free RAM.
- No local Ollama/vLLM/LMStudio server was responsive; the earlier `vision-local-review` runs correctly blocked when model missing.
- Source selected for *experimental benchmark only*: `HuggingFaceTB/SmolVLM2-256M-Video-Instruct` (official Hugging Face repo, Apache-2.0), pinned source snapshot revision `067788b187b95ebe7b2e040b3e4299e342e5b8fd`. Local weights ~1.026 GB. Code uses offline local files, no cloud model inference.
- `num2words 0.5.14` and `docopt 0.6.2` were installed in isolated directory `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\vlm_cpu_deps`; original base Python environment was not modified.

## Real measurements, no fabricated video description

First run `vlm_cpu_smol256_run01` failed during model load: missing `num2words`. This is preserved as a factual failure.

Second run: `vlm_cpu_smol256_run02` (3 controlled synthetic 256×256 images):

| Case | Ground truth | Model answer | Outcome | CPU inference |
| --- | --- | --- | --- | --- |
| red image with blue square; ask whether background mostly red | YES | NO | WRONG | 20.687 s |
| green image with yellow circle; same question | NO | NO | RIGHT | 20.250 s |
| white image with black text; ask whether blue square present | NO | NO | RIGHT | 20.250 s |

- Accuracy **2/3 (66.7%)**, only 3 elementary synthetic tests — insufficient to estimate broad real-world accuracy.
- Model repeatedly answered NO: diagnostic `CONSTANT_ANSWER_POSSIBLE_MODEL_OR_PROCESSOR_BIAS`; the underlying cause could involve limited model capability or library/model compatibility, not established yet.
- Load time **0.438 s**, resident Python memory after loading **440.5 MiB**, by completion **1445.5 MiB**, 3 test inference time total about **61.2 s**. No RTX/CUDA speed has been benchmarked.
- Verified `AutoProcessor.apply_chat_template` genuinely returned DIFFERENT `pixel_values` tensors for red/green inputs, each shape `(1,17,3,512,512)`. Thus image data were present, though this does not establish the model used them correctly.
- Transformer's library warned about model pad_token_id (128002 above declared vocabulary 31999) and processor_kwargs handling; these are compatibility concerns to investigate before any model endorsement.
- **No competitor videos, full frames, audio, screenplay, narrative analysis or agent debate were inferred by this CPU benchmark.**

## Automated Quality Gate

Module: `cinefactory/research_intelligence/vlm_benchmark_gate.py`
CLI: `vlm-smoke-audit --report ... --output ...`.

The gate **reopens the actual images** and validates known pixel geometry, reference answers, model revision, bounded test count, inference timings, and rejects forged “correct” fields. It flags constant answers, slow CPU inference and a too-small synthetic sample.

Real outcome: `SMOKE_REJECT_POOR_CONTROLLED_ACCURACY` and `model_deploy_approved=false`, `production_permission=false`. Even a hypothetical 100% pass in 3 tests can ONLY yield `CPU_SMOKE_PASS_NOT_GENERALIZED`, never deployment approval.

- Source report: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\vlm_cpu_smol256_run02\report.json`.
- Audit gate: `C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\vlm_cpu_smol256_run02\quality_gate_v2.json`.
- Test assets: `redblue.png`, `green.png`, `white.png` in same run directory.
- `scripts/benchmark_small_vlm_cpu.py` runs CPU only with 2 Torch threads and refuses less than 5 GiB free RAM; no GPU allocation or installation in system Python.

## Repeat the actual (isolated) CPU benchmark

Run in `C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6`:

```powershell
python -u scripts/benchmark_small_vlm_cpu.py --output-dir "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\NEW_UNIQUE_VLM_CPU_RUN" --max-samples 3 --deps-dir "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\20261009\vlm_cpu_deps"
python -m cinefactory.research_intelligence vlm-smoke-audit --report "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\NEW_UNIQUE_VLM_CPU_RUN\report.json" --output "C:\Users\ADMIN\Downloads\CineResearch_DailyState\verification\NEW_UNIQUE_VLM_CPU_RUN\quality_gate.json"
```

Outputs are immutable per unique run. Never assume model performance is validated because the code runs.

## Engineering acceptance next

1. Create a **separate tested CUDA model environment** without changing the existing Hermes/CineFactory Python interpreter. Only when available VRAM has a measured safe margin; protect ongoing user processes.
2. Verify a more capable candidate with pinned version and compatible inference stack rather than judging its abilities from marketing. Candidate family SmolVLM2-500M/2.2B or other strong small VLM; license and actual throughput must be rechecked.
3. Build a human-labeled 30+ frame/thumbnail benchmark for actual animation, object identity, text, composition and ambiguous/unanswerable images. Include temporal sequences, spoofed frames and cross-topic negatives.
4. Measure image/frame caption factual precision, hallucinations, refusal/unknown behavior, retrieval quality, VRAM/CPU/latency budgets and issue-to-issue consistency. Distinguish thumbnail observations from full-video scene/audio analysis.
5. Have Quality independently validate model descriptions, then permit *advisory* CineCouncil debate. Owner approval to produce remains a separate authenticated decision.

**Decision: DO NOT ROUTE AUTOMATIC DEEP VIDEO SEMANTIC ANALYSIS TO THIS CANDIDATE/CONFIGURATION.**
