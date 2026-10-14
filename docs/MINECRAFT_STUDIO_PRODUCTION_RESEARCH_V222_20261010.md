# CineFactory Minecraft Animation Production Research v222

**Research checkpoint:** 2026-10-10. **Verdict:** RESEARCH_IN_PROGRESS_NOT_PRODUCTION_READY.

This is a real assessment of the current CineFactory OS source, its own valid MP4 and SHA/FFprobe evidence, and outside first-party technical/policy references. **No claim that BigSchool/Maizen full video and audio were watched.** Their private animation program, rig library, labor, staff size and edit schedule cannot be inferred from a thumbnail or search snippet.

## 1. Distinguish the production lanes (essential before automation)

| Lane | Output truth | Best default CineFactory stack | Status |
|---|---|---|---|
| **Minecraft-style ORIGINAL scripted 3D animation** | Entirely authored 3D block actors, sets, acting, camera, light, voice, montage | Claude Code Script/Director -> first-party Blender voxel rig/animation/cameras -> FFmpeg/Remotion/audio/QC | Chosen first research and eventual film pilot; quality NOT approved |
| **Minecraft scripted in-game machinima** | Real Minecraft runtime gameplay staged with players, mods or commands | Real legal game runtime + replay/camera capture -> voice/edit/QC | Separate authentic game adapter required, NOT Blender render posing as game footage |
| **Minecraft genuine survival/gameplay/tutorial** | Real actions recorded in Minecraft game | Gameplay capture/mic/recording, optional replay camera, soundtrack, edit | Separate source provenance and QA route; do not fabricate action with generative models |

Do not group all channels with the word Minecraft into the same automation lane. BigSchool is labeled Minecraft Animation; Maizen's official Minecraft roleplay/gaming and fan-made 3D animation inspired by Maizen are different formats.

## 2. What is currently genuinely working in CineFactory

- `cinefactory/studio/block_production.py`: persistent Blender worker, compiled shots, queue, recovery, GPU policy, visual QC; there is real infrastructure, but no published professional-quality episode acceptance.
- `cinefactory/block_animation/assembler.py`, registry, animation, camera, prop, expression, reaction, scene template, crowd and QC modules exist. The YAML currently has original `mc_a/mc_b/mc_c` rigs and 14 declared animation clips. A YAML clip name is not a visually accepted working film performance.
- Machine: local Blender **4.5.14 LTS** file found at `.tools/blender-4.5.14-windows-x64/blender.exe`. Local ComfyUI **0.38.0** API responds on `127.0.0.1:8188` with RTX 3060 12GB, but Comfy MCP official beta and Blender Lab MCP 5.1+ are NOT yet validated production operators.
- The Minecraft-specific YAML state before this research remained empty: `config/niches/minecraft/production.yaml` has no approved recipes/toolchains/benchmarks; `config/niches/minecraft/competitors.yaml` and `research.yaml` have no entries. This study intentionally registers new *unverified* research separately, not false approved competitors or production recipes.

### Real local 2s baseline, decoded and inspected

- File `data/verification/v197_minecraft_art_direction/minecraft_3shot_visual_pilot_with_original_sfx.mp4` exists, size 402,011 bytes. SHA-256 matches receipt `0a880320847cfda17172618b6b7a1aadba14d27311d8529b180962297c64443e`.
- ffprobe: H.264 960x540 @24fps, AAC, 2.000s. `three_shot_real_frame_review.jpg` inspected visually (three frames 6/25/42). Scene has two original colorful voxel children against a sparse house/grass village, simple face/poses. Shots switch wide to close and reaction but the narrative/event and performance are still unclear without a proper storyboard or dialogue.
- Art-gate `recovery_gap_audit.json` has **12 independent hard blockers**: acting and emotion library, audio post QC, identity not validated, director storyboard/coverage, 1080p minimum, independent review, 30-second or longer acceptance pilot, model/SFX rights, nonexpressive generic faces, original narrative approval, production UV skins, lighting/depth/readability.
- v197 is a real 2s technical/presentation **prototype**, not Disney-level, not professional ready, not a BigSchool re-creation.

## 3. What can be credibly learned from professional technical sources

1. **Blender Studio — Minecraft Animation Workshop (Dillon Gu):** official course outline covers Mineways world import, texture/shader, Boxscape rigs/skins, props/dynamic parenting, animation/acting, lighting Cycles vs Blender Render, sound and export. We inspected course curriculum, not paid chapters or complete full video. https://studio.blender.org/training/minecraft-animation-workshop/
2. **Blockbench (official tool and Microsoft tutorials):** original per-part cuboid modeling, UV skin texture, animation bones/clip timeline. Blockbench's official export table recommends glTF/glb for Blender rendering, preserving scene hierarchy; OBJ lacks hierarchy and skeletal animation. https://blockbench.net/wiki/guides/export-formats/ ; https://learn.microsoft.com/en-us/minecraft/creator/documents/blockbench
3. **Mineways:** official project documents world exporting for Blender 3.5+ and names alternatives MiEx/jmc2obj, plus possible ReplayMod camera GLB. Ownership of world/game textures and commercial license must be checked for exact use. https://github.com/erich666/Mineways
4. **MCprep:** can prepare Minecraft world materials/texture swaps, mob/prop spawning, scene effects; README advertises older Blender compatibility (e.g. 2.8 to 4.0), not a verified Blender4.5 worker addon. HOLD as optional test instead of silently installing. https://github.com/Moo-Ack-Productions/MCprep
5. **Mine-imator:** dedicated Minecraft-themed 3D animation editor and renderer, official latest stable 2.0.2 page dated Nov 2023. Potential art-direction comparison; no public headless API or Claude Code MCP was verified, so do not assume automatic batch CLI. https://www.mineimator.com/download
6. **Blender 4.5 LTS:** maintained through July 2027; avoid unnecessary engine change while rigs/characters, acting, audio and art are weak. https://www.blender.org/releases/4-5/

## 4. Competitor evidence design (not a fabricated shot breakdown)

### BigSchool `@bigschoolminecraft`
Known publicly: Minecraft Animation brand; historical 2019 establishment, third-party services estimate ~32.4m subscribers and multi-billion lifetime views around Sep–Oct 2026. Some current-indexed reports show *heavily short* recent videos and mixed video count discrepancies. Those reports do NOT establish two 8+ minute new-channel 1M-in-14d breakouts or current long-form economics. Verify original YouTube upload date, duration, 24h/7d/14d change and real long-form catalogue before strategic scoring.
Reference: https://www.youtube.com/@bigschoolminecraft/videos and https://www.speakrj.com/audit/report/UC-Diq5SjWZDol8C0_E_1Y7A/youtube/media-stats

### Maizen Official `@maizenofficial`
Scripted gameplay and roleplay can appear cinematic but may run real in-game custom scripting. Never assume Blender animation or report fake footage as original game capture. Need direct selected full episode timestamps, game versus 3D frame semantics and voice/camera evidence. https://www.youtube.com/@maizenofficial/videos

### Kamui Animation (unofficial Maizen derivative)
Public YouTube description explicitly says unofficial / fan-made. This is a valid example that fan 3D animations may look unlike the creator's original gameplay; it is NOT proof Maizen itself animated the episode. https://www.youtube.com/watch?v=psUSgeK57t8

**Studio video-forensics form (for any future accessible authorized >=8min reference):**
- Evidence ID/source URL, source ownership, watch permission, date/time, duration, playable full-video and full-audio confirmation.
- For each time-coded shot: STORY_BEAT, tension/reveal/payoff, cast and actions, actor screen position/eye lines, camera shot scale and movement, face/brows/mouth rig, prop/hand contact, environment/light, audio/VO/SFX/music, edit transitions and pacing.
- Compare >=1 mature long-form winner, >=1 weaker original long-form upload, and >=1 comparable independent new-channel example to avoid survivorship bias.
- Label OBSERVED frame/audio vs PUBLISHER-REPORTED metadata vs INFERRED tool type vs UNKNOWN private toolchain. Never infer software solely from Minecraft voxel appearance.

## 5. Recommended original 45-second studio pilot — not yet rendered

Storyboard prepared as separate evidence-backed data in `config/niches/minecraft/research_backlog_v222.yaml`.

Title: **The Lost Lantern**. Original characters **Nova** and **Pip**, with distinct legally created outfits/skins and stable actor IDs; village/forest/cave/lantern assets authored in-house. Ten shots (4,4,4,5,5,5,5,5,4,4 seconds) make exactly 45 seconds, 1080p24. Story: lantern goes out -> find glowing trail -> cave tension/dialogue -> glowing orb lands on Pip -> funny emotional release -> second glow suggests next mystery.

Department responsibilities:
- R&D/Research: derive original shot grammar from documented sources and (later) real video review, not copy script, rigs, character colors or competitor branding.
- Creative/Script: 45s original action/dialogue, exact hook, tension, reconciliation, reaction, new mystery.
- Character Department: two **original** 64x64 pixel skins + proper articulated shoulder/elbow/hand/hip/foot rig, face expressions, brows, eyelids, phoneme mouth, contact constraints and costume/skin version registry.
- Environment/Props: original Blockbench-created voxel cave, trees, lantern/orb, light-emitting surfaces, ground, depth and accurate collision/contact; optional own legally sourced exported Minecraft world if using the authentic game.
- Direction/Cinematography: lock storyboard, shot sizes wide/medium/close, eyeline continuity, camera direction, lighting changes, parallax, color contrast and composition on phone.
- Performance: natural idle/anticipation/walk/halt/turn/recoil/laugh, footplant and hand prop sockets, procedural reusable NLA animation clips, not merely one arm swing.
- Sound: original/licensed English voice actors/TTS, Foley, original SFX/music, sync to actions/visemes, loudness and clipping checks; no random copyrighted tracks.
- Render: Blender 4.5 Eevee on 3060 as baseline; actual hero quality inspected at 1080p24; render only changed shots when repairing. Workbench for preview only. Comparisons with Cycles, Mine-imator or Unreal require same story/actors/audio and actual finished receipts.
- Editorial/Color: FFmpeg/Remotion (existing), separate audio QC and color, captions where needed, pacing and scene logic verification.
- Gate: actual accepted 30–60s media, SHA and frame/audio QC, rights ledger and independent review; never automatically publish as an episodic 8–10 minute channel.

**Why 45s and 10 shots?** Short enough for fail-fast art/rig/audio iteration on 12GB VRAM yet long enough to expose continuity and acting across cuts. If this stage fails, producing 10 minutes simply multiplies defects.

## 6. Decision matrix for Claude Code/MCP software

| Candidate | Minecraft animated film fit | Deployment decision |
|---|---|---|
| Blender 4.5 existing worker + CineFactory scene graph | Deterministic 3D rig/identity/camera/edit, repeatable local | **P0 baseline**, improve art/acting. Existing code does not mean production QC approved |
| Blockbench original assets → glTF → Blender | First-party original voxel skin/prop/world assets; consistent UV | **P0 research**, evaluate export fidelity and install rights; no automatic app install |
| Mineways / MiEx | Import original Minecraft-built environment | P1 after legal/game ownership and source verification |
| MCprep | Material swaps, mobs, props; potential quick setup | HOLD until Blender 4.5 compatibility and license audit |
| Mine-imator | Specialized Minecraft animatic/comparison | P1 optional manual pilot; unknown Claude automation support |
| ComfyUI + Claude via internal read-only MCP | Concept thumbnails, storyboard aids, selective nonidentity hero enhancement | P2 only; output continuity and rights not proven, no cloud partner spending |
| Blender Lab 5.1 MCP + Claude Code | Scene automation and bpy control | HOLD; separate environment and strict security sandbox, current 4.5 worker stable |
| Unreal 5.8 / Unity | Heavy real-time world/complex shots | Later R&D only if actual 3D clip beats Blender in QC/accepted seconds/hour |
| OpenArt/Higgsfield/Runway | Premium effect shots (optional) | PAID HOLD; do not default to cloud for every Minecraft frame |

## 7. Safety and monetization

- Minecraft's updated Usage Guidelines allow many monetized, freely viewable original player videos with meaningful unique contribution and have specific restrictions; don't treat that as blanket permission for redistributed official asset packs, branded merchandise, copied proprietary character skins or commercial use outside the guideline. https://www.minecraft.net/en-us/usage-guidelines
- Maizen's **official Fan Content Guidelines** contain conditional allowance for derivative free-view YouTube video ads but explicitly prohibit some commercial/promotional uses and confusing brand attribution. Original first-party characters are strategically and legally more robust. https://maizen.com/usage-guidelines/
- YouTube channel policy (inauthentic content, updated 2025) explicitly covers *mass-produced/repetitive* videos. Owning the Blender render or using AI doesn't automatically qualify: each episode needs original story, progression and artistic value. https://support.google.com/youtube/answer/1311392

## 8. Implementation / next acceptance

**Done now:** 3 research cases recorded with explicit NOT_WATCHED flags; 9 technology choices with real source URLs and qualified/installed distinctions; original 45s/10shot beat/camera/actor/SFX plan; code-level Minecraft research meeting; local MP4 SHA-check and comparison to known v197 QC blockers; Claude internal MCP and CLI query hooks; regression tests.

**Not done:** Full authorized BigSchool/Maizen video footage analysis; approved rights to any competitor asset; new character skin/rig upgrades; voice acting/sound mixing; genuine 45s render, benchmark; official Comfy MCP/Blender Lab install; production recipe/toolchain approval.

**First prioritized R&D sequence:**
1. Obtain lawful full sample references and have research agent mark actual timestamps; assess *original techniques only*.
2. Character art/rig proof: two fresh UV skins/rigs + 5 essential expressions + 5 acting moves, designed for repeatable episodic work.
3. Render 3 critical scenes (close dialogue, hand prop interaction, wide move/cave light), fail QC early.
4. Produce coherent 45s original real video at 1080p24 with dialogue, Foley, music and QC receipts.
5. Measure time per accepted second, rework and GPU consumption; only then extrapolate to 8–10min episodes.

## Usage on real CineFactory Windows checkout

```powershell
cd 'C:\Users\ADMIN\Downloads\cinefactory-os-v1.6\cinefactory-os-v1.6'
python -m cinefactory.cli minecraft-production-research
python -m cinefactory.cli minecraft-production-research --storyboard
python -m cinefactory.cli niche-technology-plan --minor-niche minecraft_story_adventure
```

After Claude Code's project MCP `cinefactory-studio` receives explicit human trust approval, Claude can invoke `minecraft_research_conference` and `original_minecraft_pilot_storyboard`, then involve Researcher / Technical Director / Quality Auditor, without paid credits or invisible filesystem writes.
