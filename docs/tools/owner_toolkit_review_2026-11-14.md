# Owner's tool list: what CINE uses for fast, good-looking Minecraft videos (14/11/2026)

Source: the list the owner sent (software, characters, maps, repos, MCP, music, voices, the "6-step workflow"). Labels: OBSERVED (seen on the PC or measured) / INFERRED.

## Use now: already on the PC, no download needed
| Tool | Role in CINE | Notes |
|---|---|---|
| **Mine-imator 2.0.2** | **Main engine for character Shorts (MC-S1)** and short animated episodes | OBSERVED: installed. Measured 1.35 s/frame on the RTX 3060, about 10–12 min render for an 18 s Short. Code already writes the `.miproject` (`tools/mineimator`). |
| **Minecraft Java 26.3** (owner's licence) | Gameplay, tips (MC-S3), sets for long-form | OBSERVED: the BinBoZu_Studio world plus datapack. Recording works without mods (`tools/mc_java`). |
| **Blender 5.2 + MCP** (ahujasid-style bridge) + **MCprep** (zip in Downloads) | Physics Shorts (MC-S2), VFX shots that Minecraft and Mine-imator can't do | OBSERVED: installed. EEVEE runs 2.2–6.3 s/frame. |
| **Blockbench 5.2.2** (installer in Downloads) | Original monsters/creatures for MC-L2 horror, custom models | Install when MC-L2 starts. |
| **FFmpeg / MoviePy** | Cutting, mixing, subtitles, -14 LUFS (`tools/cf_auto_edit.py`) | Already the CINE pipeline. Replaces CapCut. |
| **Audio-first** ("record the voice first") from the 6 steps | Already the blockfilm rule: TTS first, picture follows the voice | Keep it. |

## Good, but needs the owner's OK to download or install (free)
| Tool | What it gives | Why we ask first |
|---|---|---|
| **Fabric loader + Iris + Complementary Shaders** | Shader lighting like the big channels when recording in Minecraft | Install rule (downloads/installs need the owner's approval). |
| **Flashback** (instead of Replay Mod) | Records the 3D world, then frees the camera for a cinematic export | Replay Mod lags behind new Minecraft versions; Flashback targets the latest (INFERRED). |
| **Incompetech** (Kevin MacLeod) | Familiar music, CC-BY: needs a credit line in the description | Download. CINE's own synthesised music already works. |
| **BBS mod (McHorse)** | One person plays every role, camera on paths | Needs a compatibility check with 26.x first. |
| **Mineflayer bots** | Characters act by script, no player needed | 26.3 needs ViaProxy plus an offline server: heavy, do it later. |

## Not using (and why)
- **NameMC / minecraftskins / Planet Minecraft skins:** other people's skins and well-known characters (JJ/Mikey…). CINE rule: original IP only. **NovaSkin editor** is fine for editing our own skins.
- **Downloaded maps (Planet Minecraft / minecraft-maps):** many are All Rights Reserved. Only use a map whose licence allows commercial use, with credit. Otherwise build our own with datapacks/code.
- **NovaSkin Wallpapers for thumbnails:** the scene art belongs to the site; commercial-use terms unclear. Thumbnails come from our own Mine-imator/Blender renders.
- **Mixamo:** needs an Adobe account (the owner must create it). Block characters have no elbows, so the gain is small.
- **CapCut:** licence limits on some assets; CINE already edits automatically with FFmpeg.
- **Freesound:** licence differs per file (CC0/BY/NC). CINE uses `sfxkit.py` (sounds made in code).
- **TTSMaker:** check the commercial terms before use. CINE already has local TTS (Kokoro/Piper).
- **Audacity "Mikey voice":** imitating the voice of a Maizen character is off-limits. Pitch shifting for our own original voices is fine.
- **"3 seconds to hold kids":** the hook principle is right, but targeting kids risks Made for Kids (RPM $0.33). CINE aims at family/teen viewers.

## Decision (INFERRED, following the OWNER instruction "use whatever is fast and good-looking")
1. MC-S1 Shorts: **Mine-imator** (fast and good-looking). The cloud engine is only for reviewing the script.
2. MC-S2 physics Shorts: **Blender EEVEE** (light settings).
3. MC-S3 tips, MC-L1/L2 long-form: **Minecraft Java** recording, plus Iris/Complementary/Flashback once the owner allows the install.
