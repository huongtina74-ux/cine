# Local / open-source production stack for long-form YouTube on ONE Windows PC (RTX 3060 12 GB, 32 GB RAM) — state as of 2026-11-12

Scope: what a small studio can make largely by code, Blender, open repos, local AI models and AI agents (Claude Code + MCP) on one RTX 3060 12 GB / 32 GB RAM Windows machine, with Blender 4.5/5.2, Python and an existing in-house TTS/script app.
Labels: **OBSERVED** = stated in the linked source (date given where the source gives one) · **INFERRED** = my reasoning from cited facts · **ESTIMATED** = a number I worked out, not measured on this PC.
Local context read first (not redone): `research_notes/Hai ngách Minecraft kiếm tiền nhất/horror_production_stack.md` and `ai_bot_simulation_stack.md`. They cover Minecraft capture (Flashback/Iris/Distant Horizons), Minecraft mods and local LLM bots (Andy-4 on 12 GB). They do not cover TTS, image/video models, code animation or music. Both note the CineFactory rule "one heavy GPU job at a time" on the RTX 3060. **OBSERVED locally:** this Linux checkout has no `data/production_ledger.jsonl`, so CineFactory's own render/edit times are **not measured** here; read them on the Windows machine.
Note: this session already exposes a Blender MCP whose tool names (`get_blendfile_summary_*`, `*_for_cli`, `search_api_docs`, `search_manual_docs`, screenshots, `execute_blender_code`) match the Blender Lab server's tool set described by agentmods (below). **INFERRED** that the owner's machine already has the official Blender Lab MCP connected.

---

## 1. Code-driven animation, Blender automation, maps and data-viz: which tools, licences and maintenance state?

### Takeaway
For a company of more than 3 people, Remotion costs money ($25/seat/month for manual creators or $0.01/render with a $100/month minimum for automation). Manim CE (MIT, actively released, v0.22.0 on 2026-10-08) and the MIT Motion Canvas forks (Revideo, Canvas Commons) cost nothing. Blender's Python API plus the official Blender Lab MCP (needs Blender 5.1+) or the community mcp-for-blender gives Claude Code full scene control. OSM-based maps are commercially usable with on-screen or description attribution.

### Cited Findings
- **Remotion licence (OBSERVED):** "Remotion is free to use for individuals and companies up to three people." The Company License has two options. "Remotion for Creators" costs $25/month per seat, for "low volume manual video creations… (including using AI agents and Remotion Studio)". "Remotion for Automators" costs "$0.01 per render, $100/mo minimum" and covers batch rendering and automated products. — [remotion.pro/license](https://www.remotion.pro/license); FAQ: "$25/month per person who writes Remotion code themselves or using agentic coding tools" — [remotion.pro/faq](https://www.remotion.pro/faq)
- **Remotion activity (OBSERVED, 2026-11-03):** 70.3k stars, latest release v4.0.540 on 2026-11-02 — [dev.to/reelmint, Motion Canvas vs Remotion](https://dev.to/reelmint/motion-canvas-vs-remotion-which-one-should-you-build-video-with-48f4)
- **Manim Community (OBSERVED):** MIT licence. v0.22.0 was released 2026-10-08 and reworks output format selection and video encoding. Releases run roughly every 1–2 months: 0.19.1 Dec 2025, 0.20.0 Feb 2026, 0.21.0 Aug 2026, 0.22.0 Oct 2026. Needs Python ≥3.11. — [Manim changelog 0.22.0](https://docs.manim.community/en/stable/changelog/0.22.0-changelog.html); [PyPI manim](https://pypi.org/project/manim); [GitHub ManimCommunity/manim](https://github.com/manimCommunity/manim)
- **Motion Canvas (OBSERVED):** MIT licence; describes itself as "a specialized tool designed to create informative vector animations and synchronize them with voice-overs." The last stable release is v3.17.2 (2024-12-14); 3.18.0-alpha followed 2025-02-16; the last commit was 2026-07-02. One sourced article calls the core "effectively dormant" as of Oct 2026. — [GitHub motion-canvas](https://github.com/motion-canvas/motion-canvas); [metavert.io/motion-canvas](https://metavert.io/motion-canvas) (2026-10-24)
- **Revideo (OBSERVED):** MIT licence; moved to `midrender/revideo`. v0.11.0 (2026-07-10) adds headless rendering, a render CLI and parallel rendering. The README says "A scene is plain TypeScript, so Claude or Codex can produce one from a prompt"; telemetry can be turned off with `DISABLE_TELEMETRY=true`. **Canvas Commons** is a community MIT fork; 0.4.0 shipped 2026-09-24. — [GitHub midrender/revideo](https://github.com/midrender/revideo); [metavert.io](https://metavert.io/motion-canvas)
- **Other code-video options (OBSERVED, 2026-11-03):** Editly (MIT, JSON5 spec on ffmpeg; last commit May 2025). Theatre.js (Apache-2.0) is a browser motion editor, not a video encoder; last commit Aug 2024. Lottie is a playback format, not a renderer for narrated explainers. — [dev.to/reelmint, Remotion alternatives](https://dev.to/reelmint/remotion-alternatives-what-to-use-instead-depending-on-why-youre-leaving-3de3)
- **Official Blender MCP (OBSERVED):** Blender Lab "MCP Server" requires Blender 5.1 or newer. It has a security warning: it "will execute LLM generated code in Blender without any guards". It is GPL-3.0, and its docs and manual are bundled for lookups. — [blender.org/lab/mcp-server](https://www.blender.org/lab/mcp-server/); [projects.blender.org/lab/blender_mcp](https://projects.blender.org/lab/blender_mcp). Version 1.0.3 shipped 2026-09-11. "Blender itself has no built-in LLM connection and the Foundation has said none is planned." — [voyager.so](https://voyager.so/blog/blender-mcp) (2026-09-17)
- **Community Blender MCP (OBSERVED):** `ahujasid/blender-mcp` was renamed `mcp-for-blender` (v2.0.0, 2026-09-16); old configs keep working. Setup is `claude mcp add blender uvx mcp-for-blender`. It needs Blender 3.0+ (so it works on 4.5). It runs arbitrary Python and imports assets from Poly Haven (CC0, no key), Sketchfab and Poly Pizza (keys), with Hyper3D/Hunyuan3D options. — [issue #366](https://github.com/ahujasid/mcp-for-blender/issues/366); [mcp.so listing](https://mcp.so:8443/servers/blender-mcp). The Lab server has 26 tools, mostly read/navigate plus `_for_cli` headless variants; mcp-for-blender has 9 tools; both default to port 9876 — [agentmods.dev](https://agentmods.dev/compare/blender-mcp-compared) (2026-11-06)
- **Skipping MCP (OBSERVED):** "If your agent has a shell, it can skip MCP: ask Claude Code… for a bpy script, then run it in a background Blender." — [voyager.so](https://voyager.so/blog/blender-mcp)
- **OSM data for maps (OBSERVED):** ODbL; free to use commercially with attribution. For video, "attribution may be given on the map, in end credits, or… within the description"; the text is "Map data from OpenStreetMap" or "©OpenStreetMap" plus `openstreetmap.org/copyright`. OSM's own map tiles "are not free and not intended for commercial use". — [OSMF Licence FAQ](https://osmfoundation.org/wiki/Licence/Licence_and_Legal_FAQ); [OSMF Attribution Guidelines](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines)
- **Data-viz (OBSERVED):** `dexplo/bar_chart_race` (MIT) makes bar/line chart races with matplotlib or plotly — [GitHub](https://github.com/dexplo/bar_chart_race). Flourish needs a paid plan for video export, and free-plan videos must link back to Flourish — [Flourish help](https://helpcenter.flourish.studio/hc/en-us/articles/8761566757647-Bar-chart-race-an-overview)

### Inferences
- INFERRED: At CineFactory's size, Remotion is free only while the company has ≤3 people. Revideo (MIT, TypeScript, headless CLI) and Manim CE (Python, fits the existing Python tooling) cover the same "LLM writes the scene file → render → MP4" loop at zero licence risk. Motion Canvas core should not be the base for a new pipeline because releases have stalled; use Revideo or Canvas Commons instead.
- INFERRED: The owner runs Blender 4.5 and 5.2. The official Lab MCP (5.1+) works only with 5.2; mcp-for-blender works with both. The most reproducible production path is Claude Code writing `bpy` scripts run by `blender.exe --background`. CLAUDE.md already uses the 4.5 portable build this way. Use MCP for interactive scene inspection and debugging, not for batch renders. Both servers run unguarded Python: keep them away from folders that hold `.env` or receipts, as the cf_guard hooks already require.
- INFERRED: Maps: render your own tiles or vectors from OSM extracts (or Natural Earth, public domain) in Blender or matplotlib. Never screen-grab tile.openstreetmap.org. Put "Map data from OpenStreetMap + openstreetmap.org/copyright" in the description template that `cf_policy_check.py` validates.
- INFERRED: Data-viz: pandas → matplotlib/plotly (bar_chart_race) or Manim graphs → PNG/MP4 → ffmpeg. This is fully local, deterministic and commercial-safe. Flourish's free tier is unsuitable because of its attribution rule and lack of video export.

### Gaps
- BlenderGIS and Blosm (blender-osm) compatibility with Blender 4.5/5.x and Blosm's free-versus-premium split: not verified (search returned nothing reliable).
- No measured render speeds for Manim, Revideo or Blender EEVEE/Cycles on an RTX 3060. CineFactory's own ledger is not in this checkout: **not measured**.
- No public benchmark (beyond the bpy-dev fork's "BlenderBench" mention) of how reliably LLMs build production-quality Blender scenes.

---

## 2. Local AI image and video models (Nov 2026): licence, VRAM fit on 12 GB, speed, quality

### Takeaway
**Images:** commercial-safe local options are Z-Image / Z-Image-Turbo, FLUX.2 [klein] 4B, Qwen-Image-2512 (Apache-2.0) and FLUX.1 schnell. FLUX.1/FLUX.2 [dev], FLUX.2 klein 9B and Qwen-Image-2.1 are non-commercial *for using the model* in revenue-generating work, even though their [dev] outputs may be used commercially.
**Video:** Wan 2.2 (Apache-2.0) is the only top-tier open video model with a clean licence. It runs on 12 GB only through GGUF + block-swap + 4-step LoRAs, at about 5–20 min per 5-second clip. LTX-2.x is free under $10M revenue and runs on 12 GB only at Q3 with offloading. HunyuanVideo 1.5's licence excludes the EU, UK and South Korea. Wan 2.5+ has no open weights. Local AI video is B-roll, not the backbone of a long-form video.

### Cited Findings
- **FLUX [dev] licence (OBSERVED):** It permits only "non-commercial and non-production use". "use (a) for revenue-generating activity… is not a Non-Commercial Purpose." Yet "You may use Output for any purpose (including for commercial purposes), except as expressly prohibited herein". v2.0 (updated 2025-11-25) covers FLUX.1 [dev], Kontext [dev], Krea [dev] and FLUX.2 [dev]. — [BFL Non-Commercial License v2.0](https://bfl.ai/legal/non-commercial-license-terms); [HF FLUX.1-dev LICENSE](https://huggingface.co/black-forest-labs/FLUX.1-dev/blob/main/LICENSE.md)
- **FLUX.2 [klein] (OBSERVED):** 4B and 4B Base are Apache 2.0 (8.4 / 9.2 GB VRAM; about 1.2 s per image on an RTX 5090). 9B and 9B Base use the FLUX Non-Commercial License (19.6 / 21.7 GB). — [bfl.ai/models/flux-2-klein](https://bfl.ai/models/flux-2-klein)
- **Image licence roundup (OBSERVED, 2026-10-14):** Commercial: Z-Image and Z-Image-Turbo, FLUX.2 [klein] 4B, Qwen-Image-2512 (20B; 20.43 GB at FP8), ERNIE-Image, LongCat-Image. Non-commercial: Qwen-Image-2.1/Turbo (the "Qwen Research License", a switch away from Apache), FLUX.2 [dev]/klein 9B, Ideogram 4. HunyuanImage-3.0's licence "does not apply in the EU, UK or South Korea". — [vdf.ai](https://vdf.ai/blog/best-local-image-generation-models/). The original Qwen-Image is Apache-2.0 — [HF Qwen-Image LICENSE](https://huggingface.co/Qwen/Qwen-Image/blob/main/LICENSE)
- **Z-Image-Turbo on a 3060:** About 36 s per 1024² image at 8-bit, 8 steps, 7.0 GB VRAM. This was *calculated from specs, not benchmarked* — [gpupartner validation PDF](https://gpupartner.com/tools/vram-calculator/z-image-turbo/report-rtx-3060-12gb.pdf) (2026-11-05). It conflicts with a repo claim of "~3 seconds per image with 8-step distilled model" on an RTX 3060 12GB — [binkiewka/z-image-turbo-local](https://github.com/binkiewka/z-image-turbo-local). Treat this as unresolved; measure it.
- **Wan 2.2 licence and releases (OBSERVED):** Apache 2.0 per its repo — [localaimaster](https://localaimaster.com/blog/best-gpu-for-video-generation) citing [Wan2.2 repo](https://github.com/Wan-Video/Wan2.2). Wan 2.2 weights were released 2025-07-28, S2V-14B 2025-08-26 and Animate-14B 2025-09-19. **Wan 2.5 has no published weights** and is API-only (about $0.05–0.15 per second of output). — [genvidkit](https://www.genvidkit.com/blog/wan-2-5-open-source) (checked 2026-10-09)
- **Wan 2.2 on an RTX 3060 (OBSERVED community measurements):**
  - About 15–20 min per 5 s clip at 848×480 with 14B I2V Q4_K_M GGUF, 4-step Lightning LoRA and wanBlockSwap, using ~10–11 GB VRAM — [binkiewka repo](https://github.com/binkiewka/z-image-turbo-local)
  - "t2v: around 10–12 minutes, i2v: around 15 minutes" for 5 s at 1440×960/60 fps after upscaling and RIFE frame interpolation, on 3060 + 32 GB RAM with LightX2V + BlockSwap — [Civitai workflow](https://civitai.com/articles/17955/wan-22-workflow-optimized-for-rtx-3060-12-gb-vram-gpu) (2025-08, updated 2026-10)
  - About 5 min for a 640×640 clip on a 3060 with lightx2v + SageAttention (Reddit user) — [r/comfyui](https://www.reddit.com/r/comfyui/comments/1ozh1uz/whats_the_generation_speed_of_wan22_videos/)
  - Wan 2.2 TI2V-5B at BF16, 50 steps: about 54 min per clip (calculated, not benchmarked) — [gpupartner](https://gpupartner.com/tools/vram-calculator/wan-2-2-ti2v-5b/report-rtx-3060-12gb.pdf)
- **System RAM limit (OBSERVED):** One 3060 test peaked at 11,649 MiB VRAM but about 43.6–43.9 GB *system* RAM. Another run, using the Turbo LoRA, "took 6 to 7 minutes per clip on a machine with 64 GB of RAM" and named system RAM, not VRAM, as the binding limit. — [genvidkit RTX 3060 page](https://www.genvidkit.com/blog/rtx-3060-12gb-ai-video-models) (2026-10-09). NVIDIA's LTX-2 guide lists 16 GB VRAM + **64 GB system RAM** — [localaimaster](https://localaimaster.com/blog/best-gpu-for-video-generation) citing NVIDIA
- **LTX-2.x (OBSERVED):** LTX-2.3 (22B, Mar 2026) generates synced video and audio in one pass. Its community floor is a 12 GB card running a Q3_K_M GGUF with CPU offload; Q4 is recommended for 16 GB. — [localaimaster](https://localaimaster.com/blog/local-ai-video-generation). Licence: "Entities with annual revenues of at least $10,000,000… are required to obtain a paid license"; use-based restrictions apply; this covers LTX-2.5 versions since 2026-08-11 — [LTX-2 LICENSE](https://github.com/Lightricks/LTX-2/blob/main/LICENSE.md); [ltx.io/model/license](https://ltx.io/model/license). The older LTX-Video 0.9.5 takes about 7 min per 5 s 768×512 clip on a 3060 — [localaimaster](https://localaimaster.com/blog/local-ai-video-generation)
- **HunyuanVideo 1.5 (OBSERVED):** 8.3B parameters; 14 GB minimum with offloading; native ComfyUI support; built-in 1080p super-resolution. Licence "Territory" means worldwide *excluding the EU, UK and South Korea*, and outputs must not be used outside the Territory. — [Tencent LICENSE](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5/blob/main/LICENSE); [localaimaster](https://localaimaster.com/blog/local-ai-video-generation)
- **Other video models (OBSERVED):** CogVideoX-5B "runs on 12GB VRAM but the output quality is now clearly behind" — [localaimaster](https://localaimaster.com/blog/local-ai-video-generation). FramePack has a 6 GB floor; on a 4090 it takes 1.5–2.5 s per frame, so one minute of 30 fps video is a 45–75 min job — [localaimaster GPU guide](https://localaimaster.com/blog/best-gpu-for-video-generation). All models "degrade hard past their training length" (~5 s) — [localaimaster](https://localaimaster.com/blog/local-ai-video-generation)
- **ComfyUI (OBSERVED):** v0.28.0 (2026-07-15) added native SeedVR2 image/video upscaling — [localaimaster](https://localaimaster.com/blog/local-ai-video-generation)

### Inferences
- INFERRED (licence): A monetized YouTube channel is "revenue-generating activity". Running FLUX.1/FLUX.2 [dev] or klein 9B locally for the channel is outside the licence, even though BFL claims no ownership of outputs. Default the image model to **Z-Image-Turbo or FLUX.2 klein 4B**, with Qwen-Image-2512 as a quality step-up. It is 20B; on 12 GB it needs GGUF/offload, which is ESTIMATED and not verified. SDXL-family finetunes need a per-checkpoint licence check; not researched here.
- INFERRED (licence): HunyuanVideo 1.5 and HunyuanImage 3.0 are risky for a channel with EU or UK viewers, because the licence forbids displaying outputs outside the Territory. Avoid them for public uploads.
- ESTIMATED throughput, Wan 2.2 on this PC: about 10 min per usable 5 s 480p→upscaled clip. Over a 20 h GPU day that is about 120 clips, roughly 10 min of raw footage. After a 30–50% reject rate (warped faces, wrong motion), that leaves **about 5–7 min of usable AI B-roll per day**, with the GPU unavailable for anything else. 32 GB RAM is at or below what the community reports for 14B GGUF runs, so expect swapping or OOM. A 64 GB RAM upgrade is the cheapest fix; this is INFERRED from genvidkit's RAM peaks.
- INFERRED: Image-to-video (generate a still with Z-Image, then animate with Wan I2V) gives more control than text-to-video and keeps character or style consistency manageable. Without trained LoRAs, recurring characters still drift across shots.

### Gaps
- No independent, measured 3060 benchmark for LTX-2.3 Q3, Qwen-Image-2512 GGUF or FLUX.2 klein 4B.
- Wan 2.6/2.7 status: API IDs exist, but no open weights were found (genvidkit could not confirm dates).
- The SD3.5 Community License (the "$1M revenue" threshold) was not re-verified this session; the Stability Community Licence's $1M rule was verified only for Stable Audio (§4).

---

## 3. TTS and voice for long narration: commercial licence, quality, cloning consent

### Takeaway
Weights whose licence allows commercial use: **Kokoro-82M (Apache-2.0), Chatterbox / Chatterbox Multilingual / Turbo (MIT, watermarked), VoxCPM2 (Apache-2.0), Qwen3-TTS (Apache-2.0), Orpheus 3B (Apache-2.0 card, Llama-3.2 base caveat), Dia, CosyVoice 2, Zonos, Magpie (NVIDIA Open Model License)**.
Non-commercial: **XTTS-v2 (CPML; Coqui has shut down, so no licence can be bought), F5-TTS and OmniVoice (CC-BY-NC weights), Fish S2-Pro (research licence), OpenAudio S1-mini (CC-BY-NC-SA), Voxtral TTS, Breeze TTS 2, Higgs Audio V3 (creator grant only), VibeVoice (research only)**.
The highest-rated open voices are mostly non-commercial.

### Cited Findings
- **Licence matrix (OBSERVED, checked 2026-11-07):** "Commercial use allowed: Kokoro-82M, Qwen3-TTS, VoxCPM2, Phonon 31M, Dia2 and Sesame CSM-1B (Apache 2.0); Ming-3.0-tts and Chatterbox (MIT); Kyutai Pocket TTS and Kyutai TTS 1.6B (CC-BY 4.0)". Non-commercial: Voxtral 4B, Fish S2 Pro, OpenAudio S1-mini, Breeze TTS 2, Higgs Audio V3, XTTS v2, F5-TTS and OmniVoice ("code is MIT or Apache but… weights are CC-BY-NC because of the Emilia training data"). "Orpheus 3B is tagged Apache 2.0 but is a fine-tune of Llama-3.2-3B-Instruct, so check whether Meta's terms carry over." "Higgs Audio V3 lets creators monetize podcasts and videos with credit." The top open-weight model on Artificial Analysis was "Fish Audio Drama 3". Arena Elo: Kokoro 1064, Chatterbox 1023, XTTS v2 915. — [gpuwerk.com](https://gpuwerk.com/blog/open-source-tts-models) (2026-11-07)
- **Coqui / XTTS (OBSERVED):** The CPML "allows only non-commercial use of a machine learning model and its outputs." "Coqui has shut down." — [Cartesia](http://www.cartesia.ai/learn/open-source-tts) (2026-10-09). Chatterbox family: 500M English, Multilingual V3 (23+ languages), Turbo 350M, all MIT — same source.
- **Chatterbox watermark (OBSERVED):** "every clip it makes carries an inaudible Perth watermark." VibeVoice-Realtime is "intended for research and development only". — [Dograh](https://www.dograh.com/hub/blogs/open-source-tts-models) (2026-11-05)
- **VoxCPM2 (OBSERVED):** Apache-2.0 code and weights; 30 languages; 48 kHz output; voice design and cloning; RTF as low as 0.13 on an RTX 4090 with NanoVLLM. "we do not recommend its use in production… without rigorous testing". — [VoxCPM docs](https://voxcpm.readthedocs.io/); [LICENSE](https://github.com/OpenBMB/VoxCPM/blob/main/LICENSE)
- **Fish Audio (OBSERVED):** The new "Fish Audio Community License" v1.0 (2026-10-13) allows limited commercial use. "The S2-Pro weights remain under the Fish Audio Research License." S1-mini is CC-BY-NC-SA-4.0. — [fish-speech LICENSE](https://github.com/fishaudio/fish-speech/blob/main/LICENSE); [README](https://github.com/fishaudio/fish-speech); [HF s1-mini](https://huggingface.co/fishaudio/s1-mini)
- **Kokoro speed (OBSERVED):** On CPU only (M3 Pro), "A 22-second paragraph of narration rendered in 3.5 seconds — a real-time factor around 0.16×"; 54 voices in 9 language groups; it does not clone; known espeak-ng path pitfalls. — [VisionStory review](https://www.visionstory.ai/open-source/kokoro-tts) (2026-07-06)
- **Hardware (OBSERVED):** Chatterbox needs about an 8 GB GPU. Fish S2 Pro and Higgs V3 need 16–24 GB ("server GPU (rent)"). Voxtral needs ≥16 GB. — [llmconfigurator](https://llmconfigurator.com/en/voice/text-to-speech) (2026-10-25)
- **Supertonic v3 (OBSERVED):** OpenRAIL-M (allows commercial use, with use-based restrictions) — [Local-TTS-Demo LICENSING.md](https://github.com/yapweijun1996/Local-TTS-Demo/blob/main/docs/LICENSING.md)
- **Disclosure (OBSERVED):** YouTube: "creators are required to disclose when their realistic content is altered or synthetic" — [YouTube Community, July 2025 YPP Q&A](https://support.google.com/youtube/blog/356734251/response-to-creator-questions-about-ypp-policies-july-2025?hl=en-FO)

### Inferences
- INFERRED: For long English narration on a 3060, **Kokoro** is the safe workhorse: fast on CPU, Apache-2.0, frees the GPU for renders. Its fixed voices and flatter emotion limit drama formats. **Chatterbox (MIT)** or **VoxCPM2 / Qwen3-TTS (Apache)** are the step-up for expressive or cloned voices and fit 8–12 GB. Fish S2-Pro, Higgs V3, XTTS and F5 must be rejected at the licence gate whatever they sound like. The existing in-house TTS app should record which engine and which weights licence produced each file.
- INFERRED (cloning consent): Clone only (a) a voice actor under a signed release that covers AI synthesis and monetized YouTube, or (b) a synthetic or designed voice (VoxCPM2 voice design, Kokoro presets). Never clone a real person without written consent. A cloned voice of a real person is "realistic altered/synthetic" content and triggers YouTube's disclosure label.
- ESTIMATED: A 20-min narration at Kokoro RTF ~0.16 takes about 3–4 min of CPU time. Splitting into sentences, retakes and loudness passes dominate, not synthesis.

### Gaps
- No measured RTF on an RTX 3060 for Chatterbox, VoxCPM2 or Qwen3-TTS.
- The exact commercial clauses of the new Fish Audio Community License §III (revenue caps?) were truncated in the source.
- No blind listening test of hour-long narration (fatigue, prosody drift) for any open model was found.

---

## 4. Music and SFX: local models, licences, royalty-free sources

### Takeaway
**ACE-Step 1.5 (MIT code; weights described as MIT/Apache)** is the only open full-song model with clean commercial terms.
- **YuE2** weights are CC BY-NC 4.0 plus a 2026-09-16 "individual creator" grant. Companies need a commercial licence, so CineFactory as a company should not rely on it.
- **MusicGen/AudioGen** weights are non-commercial.
- **Stable Audio Open** is free only under the Stability Community License: registration required, and under $1M in annual revenue.
- For SFX and beds, curated royalty-free libraries remain the low-risk path.

### Cited Findings
- **Matrix (OBSERVED, 2026-09-12):** ACE-Step is Apache-2.0 for code and weights: "the only Apache-2.0 model that does full songs with vocals". Commercially usable: Magenta RealTime (CC-BY-4.0 weights), Bark (MIT), Demucs/Spleeter (stem tools). Non-commercial weights: MusicGen, AudioGen and MAGNeT (CC-BY-NC 4.0), YuE2 (CC BY-NC 4.0), AudioLDM 2 and Tango (CC BY-NC-SA). Stable Audio Open is "Conditional — revenue threshold" and gated on HF. ACE-Step's own disclaimer: "output stylistically close to an existing artist can create problems no permissive licence resolves." — [clintjohnson.cloud Patchbay](https://clintjohnson.cloud/patchbay/ai-music/ai-music-model-licenses)
- **ACE-Step 1.5 (OBSERVED):** The repo LICENSE is MIT (Copyright 2026 ACEStep) — [GitHub LICENSE](https://github.com/ace-step/ACE-Step-1.5/blob/main/LICENSE). "Its model card says generated music can be used commercially." — [boppy.me](https://boppy.me/blog/open-source-ai-music-model-licenses) (2026-10-26). The hosted acestep.io service says "Content ID, YouTube Rights Manager… require separate approval or an Enterprise Rights license". That applies to the hosted service, not local weights. — [acestep.io/terms](https://acestep.io/terms)
- **YuE2 (OBSERVED):** Code Apache-2.0; weights "CC BY-NC 4.0 with additional creator permission". Personal users, content creators and musicians "acting in an individual capacity" may monetize outputs; "The individual creator permission does not authorize commercial use of the model weights by companies." — [YuE MODEL_LICENSE](https://github.com/multimodal-art-projection/YuE/blob/main/MODEL_LICENSE); [README](https://github.com/multimodal-art-projection/YuE). Conflict: Promptus (2026-10-27) says "Monetising a video that uses YuE2-generated audio" falls inside the NC restriction — [promptus.ai](http://www.promptus.ai/blog/yue2-commercial-licence-explained). It appears to have missed the creator grant; the HF discussion shows users still asking for clarification — [HF discussion #5](https://huggingface.co/m-a-p/YuE2-3B/discussions/5)
- **Stable Audio (OBSERVED):** Self-hosted open models fall under the Community License: "permits qualifying commercial use without a license fee for users below its revenue threshold, but requires commercial users to register"; above $1M annual revenue a separate licence is required. — [Stability KB](https://kb.stability.ai/knowledge-base/stable-audio-commerical-and-usage-licensing); [HF stable-audio-open-small LICENSE](https://huggingface.co/stabilityai/stable-audio-open-small/blob/main/LICENSE)

### Inferences
- INFERRED: Music beds: ACE-Step 1.5 (instrumental, prompted per episode mood) or a curated royalty-free library. Keep a per-track provenance row (model, seed, prompt, licence). Do not register AI tracks in Content ID: a claim on your own or others' uploads creates disputes, and ACE-Step's own disclaimer warns about artist-similar outputs.
- INFERRED: SFX: Stable Audio Open Small (under $1M, registered) or CC0 libraries (e.g. Freesound CC0 items). Prefer CC0 over CC-BY, because CC-BY needs per-sound credit tracking.

### Gaps
- YouTube Audio Library terms, Freesound/Sonniss licence details and Pixabay music terms were **not researched this session** (out of tool budget). Verify before use.
- No measured ACE-Step 1.5 VRAM or speed on an RTX 3060 was found (the Patchbay page has a VRAM section I did not open).

---

## 5. Subtitles, editing/assembly and QC

### Takeaway
Subtitles and alignment are solved locally: faster-whisper (MIT, CTranslate2) or WhisperX (BSD-2, word timestamps, about 70× real-time batched) runs on a 4–12 GB GPU. Assembly is best done as code: ffmpeg plus the existing `cf_auto_edit.py`, Revideo/Manim for graphics, Blender for 3D. QC is ffmpeg filters plus the existing `cf_qc.py`. The human remains the judge of story, pacing and visual errors.

### Cited Findings
- WhisperX: BSD-2-Clause; "Automatic Speech Recognition with Word-level Timestamps (& Diarization)"; "70x speed-up… batched whisper with faster-whisper backend"; 2026 adds context-aware batching — [GitHub m-bain/whisperX](https://github.com/m-bain/whisperX). A tested 2026 stack (WhisperX 3.8.5, faster-whisper 1.2.1, ffmpeg 8.1.1 via winget on Windows) runs large-v3 "on a 4 GB GPU" — [long-video-transcripts](https://github.com/undisputedP/long-video-transcripts). WhisperX is "a permissive licence that allows commercial use" — [speechtotext.dev](https://speechtotext.dev/model/whisperx/)
- ComfyUI v0.28.0 has native SeedVR2 upscaling for "generate at 720p, upscale for delivery" — [localaimaster](https://localaimaster.com/blog/local-ai-video-generation)

### Inferences
- INFERRED: Because the script and TTS text are known, use **forced alignment** (WhisperX align) against the script rather than free transcription. This gives exact SRTs, which `cf_auto_edit.py` already emits. Whisper doubles as a QC check: re-transcribe the final mix and diff it against the locked script to catch TTS mispronunciations or dropped words.
- INFERRED: Assembly stays in ffmpeg: concat, xfade, sidechain ducking, `loudnorm` to -14 LUFS (already in CineFactory). Avoid GUI NLEs in the automated loop. An NLE such as DaVinci Resolve (free) is still the fastest place for the human "approve the draft" pass, but it is not researched here.
- INFERRED: Automated QC can catch technical faults: loudness, black or frozen frames, silence, resolution, subtitle sync. It cannot judge "is this boring / wrong / uncanny"; that remains the qc-reviewer and owner gate.

### Gaps
- Measured faster-whisper large-v3 speed on an RTX 3060 was not found in this session.
- auto-editor and MoviePy 2 status and licences were not checked.

---

## 6. AI agents for production, "faceless video" repos, and why they produce demonetizable slop

### Takeaway
Open-source "faceless" generators (ShortGPT, MoneyPrinterTurbo, MoneyPrinter variants) chain LLM script → TTS → stock or AI images → captions → render, and some auto-upload. That is exactly the template-driven, interchangeable output YouTube's "inauthentic content" policy (renamed 2025-07-15, clarified July 2026) excludes from monetization. Claude Code + MCP is valuable as a *production coordinator and coder*, not as a substitute for original concept, research and human review.

### Cited Findings
- **Policy (OBSERVED):** 2025-07-15: "repetitious content" was renamed "inauthentic content" to clarify that it "includes content that is repetitive or mass-produced". — [YouTube monetization policies](https://support.google.com/youtube/answer/1311392?hl=en). YouTube's examples of mass-produced content: "A channel that uploads narrated stories with only superficial differences between them; A channel that uploads slideshows that all have the same narration"; "channels that use AI in their content remain eligible to monetize." — [YouTube Community Q&A](https://support.google.com/youtube/blog/356734251/response-to-creator-questions-about-ypp-policies-july-2025?hl=en-FO)
- **July 2026 clarification (OBSERVED):** There are three non-monetizable categories. The first, "generic or repetitive content", is "content that looks like it's made with a template… image slideshows and templated storylines, and AI-generated content made with generic or unoriginal templates giving the impression of mass production"; it also covers "videos that stitch together unrelated or inconsistent AI clips". — [Tubefilter](https://www.tubefilter.com/2026/07/13/youtube-inauthentic-content-monetization-policy-update) (2026-07-13). YouTube's Matt Halprin says channels dedicated to this "will be removed from YPP, regardless of whether the content is AI-generated or not" — [TechCrunch](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/) (2026-07-20)
- **ShortGPT (OBSERVED):** MIT; "Experimental AI framework for youtube shorts / tiktok channel automation". ContentVideoEngine does "generating audio, automatically sourcing background video footage, timing captions"; it sources footage from Pexels and Bing Image. — [GitHub RayVentura/ShortGPT](https://github.com/RayVentura/ShortGPT). Last push 2025-02-10; about 8.1k stars — [dev.to/reelmint](https://dev.to/reelmint/open-source-ai-shorts-generators-the-repos-worth-running-in-2026-2kcp) (2026-11-06)
- **MoneyPrinter-family (OBSERVED):** MoneyPrinterTurbo is MIT and MoneyPrinterV2 is AGPL-3.0 — [dev.to/reelmint](https://dev.to/reelmint/open-source-ai-shorts-generators-the-repos-worth-running-in-2026-2kcp). A 2026 fork advertises "Selenium for automated uploads" to YouTube Studio, TikTok "via web automation", and thumbnails titled "How I Made $10K in 30 Days" — [s106062228/moneyprinter](https://github.com/s106062228/moneyprinter)
- **Claude Code + Blender (OBSERVED):** A 2026-04 tutorial (42k views) shows Claude Code + Blender MCP on Blender 4.5 and says a custom skill was needed "to improve geometry quality and make Claude much more reliable" — [YouTube](https://www.youtube.com/watch?v=fsLkJNEtsTw)

### Inferences
- INFERRED: The faceless repos fail for four structural reasons, not technical ones:
  1. One prompt produces a generic script with no research or point of view.
  2. Visuals are stock or AI clips matched to keywords, so they are "unrelated or inconsistent AI clips".
  3. Every video shares the same template, voice and caption style, so videos are interchangeable.
  4. Volume is the goal, with auto-upload and no human review.
  Each maps directly to YouTube's named examples. Their scripted uploads (Selenium/web automation) also conflict with CineFactory's hard rule "never upload/publish" and with platform terms.
- INFERRED: n8n was not researched. CineFactory already has an orchestrator (Claude Code skills + `produce_long_slide_episode.py`), so adding n8n would duplicate it; consistent with the CLAUDE.md "do not spawn a new project" rule.
- INFERRED: The defensible pattern is the one CineFactory already encodes: original IP; research → plan → human greenlight; code-built visuals with a designed look; maker ≠ checker; human approval of the draft; private upload. AI speeds up the crafts but does not replace the editorial decisions.

### Gaps
- No public data on what share of channels built with these repos were demonetized. The evidence is policy text, not enforcement statistics.
- n8n's licence (Sustainable Use License) and fit were not verified this session.

---

## 7. Capability map, realistic throughput, and which formats reach broadcast quality vs "slop"

### Takeaway
On this one PC, the strongest outputs are **code- and Blender-built visuals with TTS narration**: explainers, data-viz, maps and history, stylized 3D, and kids 3D with original rigs. These can reach broadcast-grade polish because every frame is deterministic and art-directed. **Photoreal AI-video-led formats** (fake documentary footage, AI "movies", realistic humans) can reach only short B-roll quality locally. Done at volume, they land exactly in YouTube's "inconsistent AI clips / templated" categories.

### Cited Findings
- 12 GB-tier video generation is "batch work, not chat": a Wan 2.2 TI2V-5B 5 s 720p clip takes "under 9 minutes on a single consumer GPU" per the repo, on a far faster card than a 3060 — [localaimaster GPU guide](https://localaimaster.com/blog/best-gpu-for-video-generation)
- "Use Wan 2.2 not LTX for face-heavy shots… keep clips at exactly 5 seconds or less… do not request fast head movement. Faces are the hardest thing for any video model." — [localaimaster](https://localaimaster.com/blog/local-ai-video-generation)
- Everything else in this section rests on the cited findings in §1–§6.

### Inferences

**Capability map (licence column = commercial use OK for a small company with <$1M revenue).** Quality and speed figures are INFERRED/ESTIMATED from §1–§6 unless they carry a link there.

| Block | Best local options (Nov 2026) | Licence (commercial?) | Quality 2026 | Fits 3060 12 GB / 32 GB? | Speed (ESTIMATED unless §-cited) | Still needs a human |
|---|---|---|---|---|---|---|
| Script / research agent | Claude Code (+ CineFactory Script Factory skills); local 7–14B LLM only for bulk drafting | Claude: paid service; local Qwen/Llama: per model | High with sourced research; local LLMs weaker | Claude: cloud; 14B Q4 at about 30 tok/s on a 3060 (third-party estimate, [modelfit](https://modelfit.io/gpu/rtx-3060/)) | Minutes per draft | Topic choice, angle, fact-check, final script lock |
| TTS / voice | Kokoro (narration), Chatterbox / VoxCPM2 / Qwen3-TTS (expressive or clone) | Yes (Apache/MIT); XTTS/F5/Fish S2 = **No** | Kokoro good but plain; Chatterbox ~ElevenLabs-lite | Yes (Kokoro on CPU; others ~8 GB) | Kokoro ~0.16 RTF on CPU (§3) | Pronunciation fixes, emotion direction, consent for cloned voices |
| Image gen | Z-Image-Turbo, FLUX.2 klein 4B, Qwen-Image-2512 | Yes (Apache); FLUX dev/klein 9B/Qwen-Image-2.1 = **No** for revenue use | Near-commercial stills; text in image is OK-ish | Yes (Z-Image ~7 GB at 8-bit) | 3–36 s per image (conflicting, §2) | Art direction, consistency, artifact rejection |
| Video gen | Wan 2.2 14B I2V GGUF + lightx2v; LTX-2.3 Q3 | Wan: Apache; LTX: free <$10M; Hunyuan 1.5: excludes EU/UK/KR | Good 5 s shots; faces and hands fail; no long takes | Barely (block-swap; 32 GB RAM is tight) | ~5–20 min per 5 s clip (§2) → ~5–7 usable min per GPU-day | Shot selection, rejecting ~30–50%, continuity |
| 2D motion graphics | Manim CE, Revideo / Canvas Commons; Remotion if ≤3 people or paying | MIT; Remotion paid >3 people | Broadcast-grade when designed | Yes (CPU/browser) | Minutes per scene, not measured | Visual design system, timing taste |
| 3D / Blender | bpy scripts + `blender --background`; Geometry Nodes; Blender Lab MCP (5.1+) or mcp-for-blender | Blender GPL (outputs free); MCPs GPL/MIT | Broadcast-grade if assets and rigs are good | Yes (EEVEE fast; Cycles slow) | Not measured (ledger absent here) | Character design, rigging, animation acting, lighting taste |
| Maps | OSM / Natural Earth → Blender or matplotlib | ODbL with attribution / public domain | High | Yes | Fast once templated | Cartographic accuracy, attribution |
| Data-viz animation | pandas + matplotlib/plotly (bar_chart_race), Manim graphs | MIT | High | Yes | Seconds to minutes | Data sourcing and verification |
| Music | ACE-Step 1.5; royalty-free libraries | MIT / per library; YuE2 creator grant excludes companies; MusicGen = **No** | Usable beds; vocals hit-or-miss | Not measured | Not measured | Taste, avoiding artist-like outputs, provenance log |
| SFX | Stable Audio Open Small (<$1M, registered), CC0 libraries | Conditional / CC0 | Good for foley-ish | Yes | Seconds | Placement and mix |
| Subtitles | WhisperX / faster-whisper (forced alignment to the script) | BSD-2 / MIT | Near-perfect with known text | Yes (runs on 4 GB) | Minutes per hour of audio | Spot-check names and terms |
| Edit / assembly | ffmpeg + `cf_auto_edit.py` (DC-driven), Revideo for overlays | LGPL/GPL builds / MIT | High for structured formats | Yes | Minutes | Pacing, cut choice, approve draft |
| QC | `cf_qc.py`, ffmpeg ebur128 / blackdetect / freezedetect, Whisper re-transcribe diff | Free | Technical only | Yes | Minutes | Story, visual errors, policy, final approval |

**ESTIMATED throughput of finished long-form minutes per day on this one PC** (one heavy GPU job at a time; 8 h human day; INFERRED from §1–§6, not measured):
- *Code/graphics-led explainer* (Manim/Revideo + data-viz + maps + Kokoro + code edit): once a reusable design system exists, about **10–20 finished minutes/day**. The bottleneck is research, script and human review, not compute.
- *Templated Blender 3D with existing rigs and sets* (CineFactory long-slide style): roughly **10–30 min/day**, depending on EEVEE vs Cycles and shot count. **Not measured** here; use the Windows `production_ledger.jsonl`.
- *Illustrated narration* (Z-Image stills + Ken Burns/parallax + Kokoro): **20–40 min/day** of compute capacity. This is exactly the "slideshow with narration" pattern YouTube names, so it needs strong original writing and variety to stay monetizable.
- *AI-video-led* (Wan 2.2 for most shots): **~5–7 usable min/day** of footage at 480p→upscaled, before editing. Not viable for daily long-form; use as accent B-roll (≤10–20% of runtime).

**Broadcast-quality vs slop by format (INFERRED):**
- **Can reach broadcast/premium quality with this stack:**
  - math/science/tech explainers (Manim/Revideo)
  - data stories and bar-chart races with real analysis
  - map-driven history and geography
  - stylized 3D kids/edu content with original characters (Blender)
  - "sleep" history or science audio with designed, slow visuals
  - language-learning dialogue animation with a consistent style (the A2 niche)
  
  These succeed when each episode has original research and a designed look.
- **Hard to make non-slop locally:**
  - photoreal AI "documentaries" and AI "short films" (face and continuity failures, 5 s limits)
  - AI-avatar talking heads (not researched; licences vary)
  - realistic historical reenactment
  - anything that needs lip-synced realistic humans
- **Slop by construction (avoid):**
  - Reddit-story or "fact list" narrations over stock or AI clips
  - templated slideshows with the same voice
  - AI animal-in-peril or rescue loops (explicitly named in the July 2026 clarification)
  - auto-generated Shorts farms
  
  All match YouTube's named "inauthentic content" examples.

**What still needs a human, everywhere (INFERRED):** niche and angle choice, fact verification, story structure, art direction and character design, rejecting bad AI shots, pacing approval, licence/provenance sign-off, AI-disclosure decision, and the upload itself (CineFactory rule).

### Gaps
- None of the throughput figures above are measured on this PC. Measure first with `studio-shot-benchmark` and `production_ledger.jsonl`: one Manim scene, one Revideo scene, one EEVEE shot, one Z-Image batch, one Wan clip, one Kokoro and one Chatterbox 10-min narration.
- AI avatar / lip-sync models (e.g. talking-head generators), RVC voice conversion, 3D-generation models (Hunyuan3D, TRELLIS) and image upscaler licences were not researched in this pass.
- No data on the RPM or retention differences between "code-animated" and "AI-video" long-form channels; that belongs to the market-research notes, not this stack note.
