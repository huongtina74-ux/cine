# Production setup

CineFactory's orchestration code is self-contained. Real AI footage still needs **local model weights and an approved local ComfyUI API workflow**. The project intentionally does not bundle multi-gigabyte model weights or unreviewed custom nodes.

## 1. Install CineFactory

Linux/macOS:

```bash
./scripts/bootstrap.sh
```

Windows PowerShell:

```powershell
.\scripts\bootstrap.ps1
```

## 2. Start local ComfyUI

Run ComfyUI on loopback/LAN only. For the strict zero-metered path, disable optional paid API nodes in ComfyUI and avoid custom nodes that call generation SaaS endpoints.

Default CineFactory target:

```text
http://127.0.0.1:8188
```

## 3. Create/export a ComfyUI API-format workflow

The workflow can be any local generation graph. CineFactory templates support these tokens:

```text
${PROMPT}
${NEGATIVE}
${SEED}
${WIDTH}
${HEIGHT}
${DURATION}
${INPUT_IMAGE}
${SHOT_ID}
```

Whole-string tokens preserve numeric values, so `${SEED}` becomes an integer rather than a string.

## 4. Import it

```bash
cinefactory import-workflow \
  --file /path/to/workflow.api.json \
  --id wan_local_shot \
  --version 1 \
  --media-type video \
  --model-id wan-local \
  --model-revision EXACT_REVISION
```

## 5. Record the exact model/license decision

Edit `models/registry.yaml`. Production promotion should only happen after the exact checkpoint's commercial/output terms have been reviewed.

## 6. Check the machine

```bash
cinefactory doctor
```

FFmpeg/FFprobe and the database must pass. ComfyUI is optional for slate acceptance mode and required for real AI footage.

## 7. Run the complete local acceptance pipeline

This creates a real MP4 from diagnostic slates and validates the whole A→Z state machine without any generation API:

```bash
cinefactory run \
  --prompt "Create a realistic family drama about a hidden sacrifice" \
  --profile family_drama \
  --language en \
  --production-mode slate \
  --tts-mode espeak \
  --no-master-4k
```

## 8. Run with local ComfyUI footage

```bash
cinefactory run \
  --prompt "Create a realistic family drama about a hidden sacrifice" \
  --profile family_drama \
  --language en \
  --production-mode comfyui \
  --workflow-id wan_local_shot \
  --workflow-version 1 \
  --render-width 1280 \
  --render-height 720 \
  --tts-mode command \
  --tts-command "python local_tts_wrapper.py --out {output} --lang {language}"
```

For high-quality creative decisions, replace `--reasoning-mode scaffold` with your own OpenClaw/Codex command bridge:

```bash
--reasoning-mode command --reasoning-command "python my_openclaw_bridge.py"
```

The bridge reads one JSON request on stdin and emits schema-valid JSON on stdout. No generation SaaS credential is required or stored by CineFactory.

## Production boundaries

- `Factory Core` owns semantic/project state.
- `ComfyUI` executes render graphs only.
- `OpenChatCut` may own the final editable editorial timeline when connected through its local bridge.
- Redis/ComfyUI queues are never the project source of truth.
- paid/metered generation fallback is not implemented.
