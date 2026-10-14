# ZERO_API_QUALITY operating mode

CineFactory keeps `ZERO_METERED_API` as the enforceable policy name. `ZERO_API_QUALITY` is the production intent:

- Paid reasoning agent: allowed if the operator chooses (for example Codex/OpenClaw model access).
- Paid image/video/TTS/music/upscale/VLM APIs: forbidden.
- Cloud GPU fallback: forbidden.
- Local Blender, Roblox Studio, ComfyUI/local models, FFmpeg, local TTS and future local voxel/Minecraft adapters: allowed.

Quality is pursued by deterministic assets, reusable rigs, lighting, camera, performance, local rerender and QC—not by silently falling back to paid generation.
