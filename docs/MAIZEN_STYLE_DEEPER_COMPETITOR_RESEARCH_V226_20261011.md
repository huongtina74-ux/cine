# CineFactory v226: Deep research correction of Maizen-style production

CHECKPOINT 2026-10-11. User correctly challenged the v225 assumption that Maizen-style MUST be raw, unscripted two-player Minecraft recording. The corrected focus is DIRECTED SCRIPTED MINECRAFT STORYTELLING, with source-of-truth decided per shot, not by a single game-install rule.

## Original official evidence

- Official Maizen Video Recording Team: https://maizen.com/video-recording-team/ — hiring people to record Minecraft game videos. Questions test survival, building, and **command** skills. Supports intentional in-game movie staging, but NOT a universal claim that all videos use gameplay instead of offline CGI.
- Official Maizencraft Slime Caverns launch, March 2026: https://maizen.com/news/maizen-comes-to-the-minecraft-marketplace/ — playable authored adventure shows deliberate story/level/quest creation and production abilities, not a specific YouTube episode render implementation.
- Maizen's official JJ/Mikey model downloads: https://maizen.com/downloads/ — .obj + textures exist; proves model asset existence, not Blender or Mine-imator were used for any video.
- Official fan guidelines: https://maizen.com/usage-guidelines/ — original cast/scenes strongly preferred; no Maizen branding/characters/footage copied without compliance.
- 2022 unofficial Reddit community FAQ: https://www.reddit.com/r/Maizen/comments/s9o53x/what_is_maizen_origin_and_faq/ — describes scripted plot, voiced Japanese original and English localization; plausible but not a verified production record for 2026.

## Real video-access limits

v224 directly verified public metadata of 7 long-form videos and inspected three sparse YouTube thumbnail preview groups, not moving footage/audio. Attempted yt-dlp/FFmpeg fetch of Maizen Bed 01:45–01:55 returned HTTP 403. TubeAlfred transcript returned insufficient credits HTTP 402 (zero credits spent). Thus full-video review, camera cut density, audio sound design, exact production engine and whether any given shot is Minecraft game runtime vs rendered CGI remain UNKNOWN, not OBSERVED.

## Technical hypotheses CineFactory should compare on ACTUAL original shots

1. GAME_ENGINE_STAGED: Minecraft legally installed; constructed private world; commands/mods/NPC/block placement/replay + director camera/audio. This is movie production IN a game engine, not playing spontaneously. Only this path needs an actual Minecraft licensed runtime.
2. BLENDER_AUTHORED: CineFactory's existing Blender 4.5 voxel character rig/scene/camera/render; original first-person POV or 3rd person coverage; original skin/props/acting; post production captions/music. This path DOES NOT require Minecraft game installation. It MUST NOT be represented as captured authentic game footage, and v197 showed 12 hard artistic QC blockers.
3. SCENE_HYBRID: combination of staged game and Blender hero/reaction shots with explicit source labels, character continuity and matched lighting; not a default before side-by-side benchmark.

Maizen's own careers give compelling evidence for game staging, but no primary source identifies their 2026 exact backend. Official OBJ downloads similarly do not prove rendered CGI. Do not replace one unverified universal theory with another.

## MAI01 original pilot R&D

Keep original Nova/Pip and waterfall mystery 45-second 9-shot storyboard from v225. v226 creates two alternate engine candidates for each shot and requires 10-second method proof before any scene qualification. For P02 first-person walk, for example, test if director-authored Blender camera and props meet aesthetic/readability and compare against real in-game capture only if licensed runtime is available. P03 actor dialogue may use Blender full rig or game NPC paths. P05 and P07 Minecraft mechanic visuals can be real game interactions or authored CGI, with truthful provenance and QC.

## Company corrections

- Script/DIRECTION: original dialogue, story beat, emotional payoff FIRST; render/capture is a downstream execution choice.
- Technical Direction: do not block 3D CGI exploration just because Minecraft launcher/Java missing; preserve conditional game rights for true game stage.
- Assets/Performance: original 64x64 voxel skins, deterministic Nova/Pip identity, animated eyes/mouth, props and acting.
- Production/QC: compare two 10-second pilots on 3060, moving footage plus audio, stable continuity, actor rig, camera, GPU cost and accepted seconds/hour; neither pilot is yet produced.
- Rights: own original IP, never copy JJ/Mikey textures and clips.
- All 26 v225 historic desk receipts and SHA manifest remain immutable for audit; v226 overlays a versioned correction rather than modifying audited receipts.

## New tools and commands

python -m cinefactory.cli maizen-method-audit
python -m cinefactory.cli maizen-method-audit --shot-id P03
python -m cinefactory.cli minecraft-company-roadmap --lane SCRIPTED_MINECRAFT_GAMEPLAY

Read-only project MCP: maizen_production_method_audit, maizen_shot_method_options, pending user's Claude Code project approval.

VERDICT: Maizen-style is scripted authored Minecraft-world entertainment, NOT equivalent to spontaneous gamer recording. Evidence supports some in-game movie filming and custom storyworld production; whether individual source shots use Minecraft, external 3D software, or both remains unknown until actual moving frames/audio or first-party detailed methodology are verified.
