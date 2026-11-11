# Production stack for original Minecraft horror-survival videos with a custom entity and scripted events (as of 2026-11-12)

Scope: the cheapest reliable toolchain for a small faceless studio (Windows, RTX 3060 12 GB, Blender 4.5, Claude Code with the minecraft-modding skill) to make ORIGINAL Minecraft horror-survival videos with its own stalker entity and scripted events. Covers game version/loader, datapack vs mod, entity modelling/animation, scripted events, cinematic capture, shaders, set building, effort per video, and EULA/Usage Guidelines limits.

Labels used: **OBSERVED** = read in the cited page or file during this session (2026-11-12). **INFERRED** = my reasoning from observed facts. **ESTIMATED** = a planning number with no direct source; it must be measured before anyone relies on it.

Method note: I tried to re-verify live version numbers directly (Mojang piston-meta, Fabric meta, Modrinth API, NeoForge maven) with curl from this container. Every request was blocked by the egress proxy (HTTP 403 CONNECT). So the loader, API and GeckoLib numbers come from the modding skill's reference file, which was "Verified 2026-10-05", and from Modrinth/CurseForge pages fetched through the search tool. They have not been re-checked against the live endpoints today.

---

## 1. Datapack-only vs real mod (Fabric/NeoForge + GeckoLib): which is faster to build and safer to maintain on 26.x, and what are the current versions?

### Takeaway
Build the hero entity as a **Fabric mod on Minecraft Java 26.3, using GeckoLib 5 for the animated model**. Use datapack functions only for one-off scripted scenes. Three reasons:
- On 26.3, everything needed for capture and building (Flashback, Axiom, Iris, Distant Horizons, the shader packs) is available on Fabric.
- NeoForge for 26.3 was still beta-only at the last verification.
- A real mod gives native pathfinding, line-of-sight checks and client-side jumpscare/fog effects. A datapack has to fake all of these with commands.

Datapack plus Animated Java is a proven, faster route to a *good-looking animated rig*. Its AI is borrowed from an invisible vanilla mob, and every bone costs one entity. It works as a prototype or fallback, not as the long-term base.

### Cited Findings

**Version baselines (OBSERVED, skill reference file, verified 2026-10-05)** — [version-baselines.md](file:///root/.claude/plugins/synced/f23e4b95-3cd9-4302-8764-2cdced09b7f9_a38d4e54-0fc1-4cfb-b1ec-f1b6d2f2c4a0/47ed4289-e8f3-4ac0-8507-cceb0bf92082/skills/minecraft-modding/references/version-baselines.md)
- 26.1: Java 25. Resource pack 84, data pack 101. Fabric loader 0.19.5, Fabric API 0.155.3+26.1.2. NeoForge 26.1.0.19-beta. GeckoLib 5.5.
- 26.1.2: NeoForge **26.1.2.114**, the first stable NeoForge in the 26.x line. GeckoLib 5.5.2.
- 26.2: resource pack 88, data pack 107. Fabric API 0.161.0+26.2. NeoForge **26.2.0.88** (stable). Forge 26.2-65.1.3. GeckoLib 5.5.5.
- 26.3: resource pack 97, data pack 121. Fabric loader 0.19.5, Fabric API 0.161.0+26.3. NeoForge **26.3.0.51-beta** (no stable yet). Forge 26.3-66.0.9. Loom 1.17.491. GeckoLib 5.5.7.
- "26.4 is snapshots-only as of 2026-10-05."
- Every 26.x version uses mojmap with no remapping and needs JDK 25 and Gradle ≥ 9.1. Ship a shadow (fat) jar.
- The ` 34` pack_format trap: 34 is the old 1.21 resource format and must never appear in a 26.x pack.
- **"5.5.5 is the last GeckoLib with a Fabric jar for 26.2 (5.5.6 for 26.2 is forge+neoforge only)."**
- Official Forge docs stop at 1.21.x; the 26.x Forge numbers are unofficial.

**Official release facts**
- Minecraft Java 26.3 "Wilderness Bound" was released 2026-09-15: data pack 121.0, resource pack 97.1, minimum Java SE 25 — [Minecraft Wiki: Java Edition 26.3](https://minecraft.wiki/w/Java_Edition_26.3); [minecraft.net 26.3 article](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3).
- 26.4 Snapshot 2 shipped 2026-09-29 (data pack 122.1, resource pack 99.0) — [minecraft.net](https://www.minecraft.net/en-us/article/minecraft-26-4-snapshot-2).
- 26.4 Snapshot 1 made Vulkan the default renderer, and Iris has no build for any 26.4 snapshot — [mcreference, 2026-09-27](https://mcreference.com/guides/shaders-minecraft-26-3).

**Writing the mod (OBSERVED, skill reference file)** — [writing-from-scratch.md](file:///root/.claude/plugins/synced/f23e4b95-3cd9-4302-8764-2cdced09b7f9_a38d4e54-0fc1-4cfb-b1ec-f1b6d2f2c4a0/47ed4289-e8f3-4ac0-8507-cceb0bf92082/skills/minecraft-modding/references/writing-from-scratch.md)
- "Animated models: GeckoLib is the standard."
- The pieces are `GeoEntity` + `GeoModel` (Bedrock `.geo.json` + `.animation.json`) + `GeoEntityRenderer`.
- 26.2+ renderers use the new extract → submit pipeline. Wrap `submit` and `extractRenderState` in try/catch, because a throw there is a hard crash.
- Registration traps on 26.x: each object needs its id set on `Properties` (`setId`), or you get "Item id not set". Building an ItemStack in a class initialiser gives "Components not bound yet".

**GeckoLib** — on Modrinth: MIT licence, Forge/Fabric/NeoForge, supports 26.3, 26.2, 26.1.2 and 26.1. The library offers keyframe animation, 30+ easings, concurrent animations, and sound, particle and event keyframes — [Modrinth: GeckoLib](https://modrinth.com/mod/geckolib).

**Animated Java (datapack route)**
- Blockbench plugin. Latest release **v1.11.0, dated 2026-10-09** — [GitHub](https://animated-java.dev/source).
- Supports "Minecraft: Java Edition 1.20.4 and newer, up to 26.3" — [AJ FAQ](https://animated-java.dev/docs/resources/faq).
- The Blueprint's Target Minecraft Version "like 26.2 (the default)" — [AJ Blueprints docs](https://animated-java.dev/docs/core-concepts/blueprints).
- Rigs are built from display entities (item, block and text displays). Exports are either Resource Pack + Data Pack, or a "Plugin" JSON for a server plugin — [AJ Blueprints docs](https://animated-java.dev/docs/core-concepts/blueprints).
- Features: Function API, Locators that run commands through function keyframes, tweening, Molang, and "Camera Support – Install the Official Camera Plugin to create cinematic camera paths" — [AJ GitHub README](https://github.com/Animated-Java/animated-java).
- Performance limit: "Every bone is an entity that has to be updated each frame". The FAQ advises using as few bones as possible and not playing animations on rigs nobody can see — [AJ FAQ](https://animated-java.dev/docs/resources/faq).
- To make a bone look at a player you must split it into its own rig and mount it on a Locator — [AJ FAQ](https://animated-java.dev/docs/resources/faq).

**Custom Entity API (datapack)** — uses "an invisible mob of their choice as the AI for walking, targetting, etc, and Animated Java as a custom model". Supports 26.2, 26.1.x and 1.21.9–1.21.11. Apache-2.0. Only 41 downloads, published a month before the page snapshot — [Modrinth](https://modrinth.com/datapack/custom-entity-api).

**Hybrid option: blockbench-import-library** — a Fabric/NeoForge mod that renders Blockbench and Animated Java models server-side through item-display entities, "eliminating the need for players to install additional mods". Its 26.3 build (2.2.0+26.3-rc-3) is dated 2026-10-01 — [CurseForge](https://www.curseforge.com/minecraft/mc-mods/blockbench-import-library).

**Datapack precedent at scale: From The Fog** (Herobrine horror)
- Published as a Data Pack and also as Fabric/Forge jars. 6.1M downloads on Modrinth. Licence CC-BY-NC-SA-4.0.
- v1.10 was a full rewrite. It added a "Dwelling" sighting type that "watches the player from just out of view when they are in caves", a "Sneaky Strike", and "developer tools for mapmakers".
- Source: [Modrinth From The Fog 1.10](https://modrinth.com/datapack/from-the-fog/version/WOL5vQ2V).

**Vanilla 26.x atmosphere is now data-driven**
- 26.1 made the light model data-driven through environment attributes (`visual/block_light_tint`, `visual/ambient_light_color`, `visual/night_vision_color`) and added Timelines — [minecraft.net 26.1](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-1).
- Fog attributes include `visual/fog_color` and `visual/fog_end_distance`. They are set by dimension types, biomes, timelines and weather, in that order of priority — [Minecraft Wiki: Environment attribute](https://minecraft.wiki/w/Environment_attribute).
- 26.3 moved mob spawns into the environment attribute `gameplay/natural_mob_spawns` — [minecraft.net 26.3](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3).

### Inferences
- **INFERRED — which version and loader to pick:**
  - **Minecraft 26.3 + Fabric loader 0.19.5 + Fabric API 0.161.0+26.3 + GeckoLib 5.5.x (Fabric jar).** This is the one combination where the whole capture stack (Flashback, Axiom, Iris, Distant Horizons, Complementary, BSL) is published for the same version, as section 3 shows.
  - Do not target 26.4 snapshots: the Vulkan default breaks Iris shaders.
  - Do not use NeoForge as the primary loader. 26.3 NeoForge is beta, and Flashback and Axiom are Fabric-only anyway.
  - The skill's Architectury layout (common + fabric + neoforge) costs little and keeps a NeoForge build possible later.
- **INFERRED — fallback:** if a GeckoLib Fabric jar for 26.3 turns out not to exist, drop to **26.2 with GeckoLib 5.5.5 (Fabric)**. The baseline notes that 5.5.6 on 26.2 has no Fabric jar, so the same gap could recur on 26.3. Check the GeckoLib versions page before scaffolding.
- **INFERRED — mod vs datapack:**
  - **Mod strengths:** real `Goal`/`Brain` AI and `PathNavigation`; per-tick look-detection on the server; client packets for jumpscare overlays, screen shake, fog pushes and sanity shaders; config files; one jar that also works as a public release. Claude Code's modding skill covers exactly this stack (GeckoLib, the 26.x registration traps, extract/submit rendering), which lowers the build risk.
  - **Datapack strengths:** no Java build, quicker iteration on model and animation, and nothing to install client-side beyond the resource pack.
  - **Datapack weaknesses:** AI is borrowed from a vanilla mob; each bone is an entity; look-at-player needs rig stacking; jumpscares and fog changes must be faked (title/particle tricks, or a custom biome/timeline per dimension).
- **INFERRED — maintenance:** both routes break on each Minecraft drop. Datapack breakage is mostly data/command format changes (pack formats change every release; command and component syntax drifts). Mod breakage is Java API drift (mojmap now, with `javap` diffing per the skill). Modrinth/Curse histories show horror mods mostly stuck on Forge 1.19–1.20.1, which suggests most authors do not keep up with Mojang's quarterly drops. So pick one version per season and freeze it.
- **INFERRED — storytelling shortcut:** for a *video* (not a released game), much of the "event system" does not need in-game code. Flashback can override fog, fog colour, time of day, weather and camera shake in post (section 3). Only player-reactive behaviour (stalk, flee when seen, chase, break torches) has to be real AI.

### Gaps
- I could not confirm that GeckoLib 5.5.7 for 26.3 ships a **Fabric** jar; the Modrinth API fetch was blocked. Indirect evidence: "Hollow Steve" ships Fabric 26.3 builds that constrain GeckoLib to major version 5 ([CurseForge](https://www.curseforge.com/minecraft/mc-mods/hollowsteve/files/8750810)).
- I did not re-check whether a stable NeoForge for 26.3 was released after 2026-10-05.
- Animated Java's licence type was not captured (the repo has a LICENSE file, but its terms were not read).
- I have no hard data on how often horror datapacks break across 26.x drops.

---

## 2. How do known horror-mod creators build entities that stalk the player, what are their licences, and is showcasing them commercially allowed?

### Takeaway
The successful stalker mods (The Man From The Fog, Cave Dweller and its forks, From The Fog, The Knocker, Cryptid, In The Corners) share one pattern:
- a **state machine** (spawn out of sight → watch at distance → approach when ignored → flee or vanish when looked at → chase/kill);
- a **timer/cooldown spawn director**;
- **proximity-escalating sound** (whispers, cave noise);
- **screen effects** (Darkness effect, jumpscare overlay, sanity shader).

Almost all of them are Forge 1.19–1.20.1 with GeckoLib, and most are All Rights Reserved. We should build our own original creature, name and lore. The "reimagined" forks explicitly disclaim ownership of Gargin's Cave Dweller concept, which shows the community treats named creatures as their creators' property.

### Cited Findings

**The Man From The Fog (M_Productions)**
- Forge 1.19.2–1.20.1. Modrinth lists ARR; CurseForge lists "Custom License". About 5.2M Modrinth downloads and 18.5M CurseForge downloads. Requires GeckoLib — [Modrinth](https://modrinth.com/mod/the-man-from-the-fog); [CurseForge](https://www.curseforge.com/minecraft/mc-mods/the-man-from-the-fog).
- Config options: `spawn_rate`, `jumpscare`, `max_chase_duration` 1000 ticks, `min_chase_duration` 400 ticks, `climbing`, `vanish_distance` 30, `spawn_at_day`, `darkness_effect`, `all_dimensions`, `break_blocks` — [Modrinth](https://modrinth.com/mod/the-man-from-the-fog).
- Behaviour: "watches the player from a far distance and comes closer after being ignored. When looked at, it either vanishes or goes aggressive" — [CurseForge](https://www.curseforge.com/minecraft/mc-mods/the-man-from-the-fog).
- CurseForge tags it in the "MCreator" category — [CurseForge](https://www.curseforge.com/minecraft/mc-mods/the-man-from-the-fog).
- v1.2.0 (2024-02) added a sanity system, a shader when sanity drops below 250, whisper sounds, a "fake man", a parallel dimension, ritual blocks/structures, and "improved man watching you every tick" — [Modrinth v1.2.0](https://modrinth.com/mod/the-man-from-the-fog/version/1.2.0).
- v1.1.0 (2023-12) added a "new stalking mechanic", staged spawn rates and lightning — [Modrinth v1.1.0](https://modrinth.com/mod/the-man-from-the-fog/version/1.1.0).
- The official Fabric port is **MIT** (1.19–1.20.1) — [Modrinth Fabric port](https://modrinth.com/project/118OmVLd).
- The official site says the mod "has been free since launch and will stay that way" and that Fabric is not planned for the main line — [themanfromthefog.com](https://themanfromthefog.com/).

**Cave Dweller (Gargin)**
- Forge 1.19.3, **All Rights Reserved**, about 460K downloads, requires GeckoLib 4.0.4+ — [CurseForge](https://www.curseforge.com/minecraft/mc-mods/cave-dweller).
- "As you explore caves, you will be stalked by this monster. As he gets closer, the cave sounds will get more intense" — [CurseForge](https://www.curseforge.com/minecraft/mc-mods/cave-dweller).
- When looked at, it chooses to either run away or chase. It can crouch through 2-block gaps. It ignores boats ("a common tactic to counter other Dweller mods") — [Minecraft Horror Wiki (fan wiki)](https://minecraft-horror.fandom.com/wiki/Cave_Dweller).
- Gargin's 2023-07-11 announcement video "has 5.4 million views" (fan-wiki figure) — [same wiki](https://minecraft-horror.fandom.com/wiki/Cave_Dweller).
- Per the CurseForge blog: spawns deep underground at light level 0, uses a cooldown after each sighting, has about 60 HP, and follows to the surface once enraged — [CurseForge blog, 2026-04-06](https://blog.curseforge.com/cave-dweller-minecraft-mod-frequently-asked-questions).

**Cave Dweller forks and licences**
- *Cave Dweller Reimagined* (idk_someguy): MIT, 15.9M downloads, last updated 2023-10. It states it "was never mine to begin with and is just a combination of models/sounds" from SiverDX's *Cave Dweller Evolved* and Schpalrbo's texture — [CurseForge](https://www.curseforge.com/minecraft/mc-mods/cave-dweller-reimagined).
- *Reimagined cave dweller* (Valk & Naz, 2026, Forge 1.20.1): ARR on Modrinth. Disclaimer: "We do not claim ownership of the 'Cave Dweller' entity, its design, or its associated lore, which remain the property of Gargin" — [Modrinth](https://modrinth.com/mod/reimagined-cave-dweller).
- That fork describes the pattern: it stares first and plays a sound ("That's your warning"), then uses a cooldown and proximity check so it doesn't spam — [Modrinth](https://modrinth.com/project/Ai4qOy4o).

**From The Fog (Lunar Eclipse Studios)** — Herobrine. CC BY-NC-SA 4.0 ("non-commercial purposes only"). Ships as Fabric, Forge, NeoForge and a plain datapack; last listed versions 1.19–1.21.10 (checked 2026-09-25) — [minecrafthub](https://minecrafthub.io/mods/from-the-fog); [Modrinth](https://modrinth.com/datapack/from-the-fog/version/1.10).

**Other stalker designs found**
- *Twixxel's Stalker*: invincible. Never moves while watched and advances only by teleporting when your back is turned (weeping-angel). Four timed events: stalk every 15 min at a 50% roll; "behind scare" every 25 min, spawning a jumpscare image directly behind the player; chase every 36 min, smashing through walls; sound-only "break event" every 10 min — [minecraft-guides (2026-06)](https://www.minecraft-guides.com/mod/twixxels-stalker).
- *The Stalker* (custom-entity), Fabric 26.2/26.3, ARR, with a paid "Premium Edition":
  - states IDLE / STALKING / WATCHING / CHASING; weeping-angel freeze;
  - spawns "out of the player's direct line of sight, with a per-player cooldown";
  - camera shake and lightning;
  - requires Fabric loader 0.19.5+, Fabric API 0.160.0+26.2 and Java 25.
  - Source: [Modrinth](https://modrinth.com/project/custom-entity-the-stalker).
- *Hollow Steve*: Fabric/Forge/NeoForge 26.1–26.3. Changelog notes: "Losing sight of a player no longer gives Hollow Steve unfair real-time tracking", stalking/teleport cooldowns, sprinting/items revealing the player's location, a sleep trap, and GeckoLib constrained to major version 5 — [CurseForge](https://www.curseforge.com/minecraft/mc-mods/hollowsteve/files/8750810).
- *The Cryptid*: MIT, built in MCreator. Paces, stalks or watches; when looked at it may vanish or do a "random event". Ambient sounds may or may not come from it. Its intent escalates from scaring to killing over time — [CurseForge](https://www.curseforge.com/minecraft/mc-mods/the-cryptid).
- *It Follows*: MIT, with source. Slow, relentless and invincible. Opens doors, breaks soft blocks, climbs, respawns closer if outrun — [Modrinth](https://modrinth.com/mod/it-follows).
- *In The Corners*: 43 entities in tiers (stalkers → bosses). Spawn delay is configurable (default "every 4000 ticks"). Includes jumpscare-on-contact and kick-from-world — [Modrinth](https://modrinth.com/mod/in-the-corners).

### Inferences
- **INFERRED — reusable technical blueprint** (reconstructed from the behaviour descriptions above; I read no source code):
  1. **Director:** a server-side per-player timer plus a cooldown, which picks an event type (sighting, behind-scare, sound-only, chase).
  2. **Spawn placement:** behind or outside the player's FOV, 20–40 blocks away, in darkness, with a valid floor.
  3. **Look detection:** each tick, take the dot product of the player's look vector with the vector to the entity, plus a block raycast for line of sight (the vanilla Enderman stare check is the template).
  4. **State machine:** WATCH → APPROACH when ignored → VANISH or CHASE when seen.
  5. **Chase:** ground navigation with sprint speed, door opening, soft-block breaking, and a crouch hitbox for 2-high tunnels.
  6. **Feedback:** positional sounds with volume or variety scaled by distance; Darkness/Blindness effects; a client HUD jumpscare (texture + sting) sent by packet; an optional "sanity" post-shader.
  7. **Fairness:** stop omniscient tracking once line of sight is lost.

  All of this maps onto vanilla `Goal` classes plus a custom `ServerTickEvent` director, which the modding skill can scaffold.
- **INFERRED — "MCreator" precedent:** several hit mods (TMFTF, Cryptid) were built in MCreator. The bar for a *viral* entity is design, sound and pacing, not code sophistication.
- **INFERRED — IP risk:** named creatures (Cave Dweller, Man From The Fog, Herobrine variants) are tied to their creators. Our creature needs an original silhouette, name, lore and sound set; do not borrow the "Dweller" or "From the Fog" naming. This matches CineFactory's original-IP hard rule.
- **INFERRED — commercial showcase precedent:** this whole genre depends on monetized YouTube videos of these mods. Gargin's own reveal video and the "Found Footage" YouTuber skin section in From The Fog show that authors expect and welcome video coverage. ARR and CC-BY-NC-SA licences, as written, restrict redistribution and commercial reuse of the *mod files and assets*. I found no licence that explicitly forbids filming. This is not legal advice, and it is moot if we build our own.

### Gaps
- I read no horror-mod source code (no GitHub source link was surfaced for TMFTF or Gargin's Cave Dweller), so the implementation blueprint above is reconstructed from feature descriptions.
- I found no explicit statement from any of these authors granting or denying the use of their mod in monetized videos.
- The SiverDX "Cave Dweller Evolved" licence and source were not checked.

---

## 3. Cinematic capture, shaders, Distant Horizons, set building, and recording settings on an RTX 3060

### Takeaway
**Flashback (Fabric, ARR, free) is the primary capture tool on 26.3.** It records packets in the background, has a keyframe timeline, overrides fog/time/weather/camera shake, exports offline at any resolution and fps, and integrates with Distant Horizons. Replay Mod (GPL-3.0) also supports 26.3 and is the fallback.

Shaders: Complementary (Reimagined/Unbound, plus the horror edit "Spooklementary"), Photon and BSL all ship 26.3 builds, and their licences allow content creation and videos. They run through Iris (LGPL-3.0), which needs the OpenGL renderer.

Set building: **Axiom's free tier forbids "Commercial Use … for profit, directly or indirectly"**, so a monetized studio should either buy the commercial licence or use WorldEdit.

### Cited Findings

**Flashback**
- Fabric only, client-side, **Licensed ARR**. Compatible with 26.3, 26.2, 26.1.x and 1.21–1.21.11. 12.7–13.5M downloads. Author Moulberry — [Modrinth](https://modrinth.com/mod/flashback).
- Changelog: 0.43.4 "Updated to 26.3" (2026-09-19); 0.43.5 "Fixed various 26.3 issues" (2026-09-20); 0.43.6 dated 2026-09-25 — [Modrinth changelog](https://modrinth.com/mod/flashback/changelog).
- Conflict: the third-party documentation site flashback-mod.com still lists 0.43.3 (2026-08-28) for 1.21–26.2 — [flashback-mod.com](https://flashback-mod.com/). It is a fan documentation site, not the author's, so Modrinth is authoritative.
- Records the packet stream, not the screen, so "A computer that plays at 40 FPS can export 4K at 60" — [flashback-mod.com/about](https://flashback-mod.com/about/).
- Timeline tracks: camera, entity tracking, speed, timelapse, freeze, time of day, audio. Overrides: "FOV, fog and fog colour, weather, time of day, night vision, camera shake and camera roll". Output: MP4/WebM/WebP/GIF/PNG/EXR, depth maps and 360° projections — [flashback-mod.com/about](https://flashback-mod.com/about/).
- Camera keyframes support smooth, linear and Hermite interpolation. In/out points are set with I/O. "Set Audio Source" re-places the microphone on an entity. Stereo audio export — [flashback-mod.com camera keyframes](https://flashback-mod.com/camera-keyframes); [export page](https://flashback-mod.com/export-video/).
- Export renders frame by frame. "Render time roughly follows pixel count — 4K is four times the work of 1080p before supersampling". SSAA offers 2× or 4× — [flashback-mod.com export](https://flashback-mod.com/export-video/).
- "A shot that renders in ten minutes without a shader pack can take an hour with one at the same settings, and adding supersampling multiplies it again." Exporting from fullscreen has been blocked since 0.42.2. Iris first-person hand rendering compatibility was removed (shaders still render) — [flashback-mod.com troubleshooting](https://flashback-mod.com/troubleshooting/).
- Distant Horizons integration since 0.10.0 (needs DH 2.3.0+). Markers via `/flashback mark` (0.4.0). 0.41.1 added 26.2 and Vulkan support — [flashback-mod.com changelog](https://flashback-mod.com/changelog/).
- Replay Mod files cannot be imported into Flashback — [flashback-mod.com](https://flashback-mod.com/).

**Replay Mod**
- Fabric (Forge for legacy versions). **GPL-3.0-or-later**. Compatible with 26.3, 26.2, 26.1.x and every version back to 1.8 — [Modrinth](https://modrinth.com/project/Nv2fQJo5).
- Render modes: default, stereoscopic, cubic, equirectangular. Uses FFmpeg (installed separately, otherwise it outputs PNG/EXR sequences). Supports camera path export and depth maps — [Replay Mod docs](https://www.replaymod.com/docs/); [changelog](https://www.replaymod.com/changelog.txt); [minecrafthub guide](https://minecrafthub.io/guides/how-to-use-replay-mod).

**Editing guidance** (third-party, 2026-10-19): render above upload resolution (1440p for a 1080p upload); use PNG sequence or lossless for shots you will colour-grade; transcode to ProRes/DNxHR; add motion blur by frame blending; run one test shot end to end before rendering forty — [Umbrella Creators](https://umbrellacreators.com/blog/how-to-edit-minecraft-cinematics-replay-mod-shaders).

**Iris and the shader packs**
- **Iris:** LGPL-3.0, Fabric/NeoForge/Quilt, supports 26.3 — [Modrinth](https://modrinth.com/mod/iris). "Optifine, Canvas, or Vulkan mods: Incompatible"; Distant Horizons and Voxy work only with packs that explicitly support them — [irisshaders.dev](https://irisshaders.dev/).
- The 26.2 DH+Iris modpack notes "Vulkan is NOT currently compatible with Iris Shaders" and mentions a future Vulkan shader mod, "Aperture" — [Modrinth modpack](https://modrinth.com/modpack/distant-horizons-iris-shaders/version/0.4.2+26.2.fabric).
- **Shader packs on 26.3:** 123 packs declare 26.3 versus 424 for 26.2. Ready on 26.3: Complementary Reimagined/Unbound, BSL, MakeUp, Sildur's, Bliss, Mellow, and **Spooklementary** ("a dark, moody edit of Complementary"). OptiFine is not available for 26.3 — [mcreference (2026-09-27)](https://mcreference.com/guides/shaders-minecraft-26-3).
- **Complementary License Agreement 1.7**, clause 1.1: "All Users are free to use This Pack for Normal Usage … includes: a. Using The Pack for gameplay b. Using The Pack for content creation". Redistribution only through Modrinth/CurseForge modpack systems — [GitHub License.txt](https://raw.githubusercontent.com/ComplementaryDevelopment/ComplementaryReimagined/main/License.txt). Both Complementary editions list 26.3 — [Modrinth Reimagined](https://modrinth.com/shader/complementary-reimagined); [Unbound](https://modrinth.com/shader/complementary-unbound).
- **Photon:** "Use Photon Shaders, including for commercially published screenshots and videos" — [Photon LICENSE](https://raw.githubusercontent.com/sixthsurge/photon/main/LICENSE).
- **BSL** (CaptTatsu, ARR): "You're allowed to … Use this shaderpack for taking screenshots and videos". Files listed for 26.3 dated 2026-09-21 — [mirror page quoting BSL agreement](https://millida.net/en/shaders/bsl-shaders-dlya-minecraft). The official bitslablab.com page returned HTTP 526 during this session.

**Distant Horizons**
- LGPL-3.0, Fabric/NeoForge in one jar (1.20.6+). Works with Iris 1.7+ only on shaders built for DH. Renders with OpenGL or Vulkan — [Modrinth](https://modrinth.com/mod/distanthorizons).
- Release 3.3.0 "Add MC 26.3 support", plus anti-aliasing and TAA, and fixes for Iris shadow maps — [GitLab release 3.3.0](https://gitlab.com/distant-horizons-team/distant-horizons/-/releases/3.3.0).

**Axiom** (Moulberry)
- Fabric only, ARR. Supports 26.3, 26.2 and 26.1.x. Version 6.0.5 dated 2026-09-03 for 26.1–26.2 — [Modrinth](https://modrinth.com/mod/axiom); [modpacks.ch listing](https://modpacks.ch/mods/minecraft/N6n5dqoA/axiom).
- EULA: "'Commercial Use' is using the Product for profit, directly or indirectly". Users without a commercial licence "must not … make Commercial Use of the Product" — [Axiom EULA](https://axiom.moulberry.com/eula).
- The Modrinth page asks "people who make money through building in Minecraft" to buy the Commercial Licence — [Modrinth](https://modrinth.com/mod/axiom).

**WorldEdit** is listed as available for Fabric, NeoForge and Bukkit/Paper — [minecrafthub Axiom page "More Java Mods"](https://minecrafthub.io/mods/axiom).

### Inferences
- **INFERRED — capture modpack** (all Fabric, 26.3): Fabric API, Flashback, Sodium + Iris, Complementary Unbound / Spooklementary / Photon (pick one look per series and lock it), Distant Horizons only for wide establishing shots, and our own mod + GeckoLib. Optionally Replay Mod in a *separate* instance as fallback (Flashback blocks Replay Mod from recording a Flashback replay, per its 0.2.0 changelog).
- **INFERRED — horror atmosphere is mostly a capture-time decision:** Flashback's fog, fog-colour, time-of-day, weather and camera-shake overrides let the editor dial dread per shot without touching mod code. In-game code is only needed where the *player character* must react on camera (the POV gameplay take).
- **INFERRED — two kinds of shot:**
  1. First-person "survival POV" footage. Take it from the Flashback replay of the gameplay session, so it can be re-rendered at higher quality. Flashback forces first-person while editing, and Spectate on the player entity gives the POV.
  2. Third-person cinematic shots: keyframed camera paths, entity tracking, dolly/crane moves.
- **ESTIMATED — RTX 3060 12 GB render settings:**
  - Gameplay session at 1080p with shaders on a medium profile, aiming for ≥ 40 fps (it only has to be playable, since Flashback re-renders).
  - Flashback export at 1920×1080, 60 fps (24 or 30 for slow dread shots), shaders on, SSAA 1× for drafts and 2× for hero shots. Use PNG or high-bitrate MP4 (NVENC) for the edit.
  - Using the source's "10 min → ~1 h with shaders" ratio: plan for **roughly 5–20 minutes of render per finished minute at 1080p60 with shaders** on a 3060, and about 4× that for 4K. Not measured; benchmark one 30-second shot first.
  - CineFactory's rule "one heavy job at a time" applies: do not render while Blender or ComfyUI jobs run.
- **INFERRED — Axiom licence:** a monetized YouTube studio arguably falls under "for profit, directly or indirectly". Either buy the commercial licence or build sets with WorldEdit plus vanilla structure blocks. This needs an OWNER decision.
- **INFERRED — Distant Horizons cost:** DH helps only with surface or skyline establishing shots. Horror is mostly caves, forests and night fog, so DH adds VRAM and render cost for little gain. Turn it off by default.

### Gaps
- Axiom Commercial Licence price was not found on the fetched pages.
- WorldEdit's exact 26.3 build and licence were not verified this session.
- Replay Mod's Iris/shader stability on 26.3 specifically was not verified.
- Flashback's ARR licence page was not read. It is a free mod and video use is its purpose, but the text was not checked.
- There are no measured render times for any of these tools on an RTX 3060.

---

## 4. Effort model: hours to build one reusable entity + event system, and hours per 15–25 min episode and per 40–55 min "100 days" movie; what can be automated

### Takeaway
No reliable published production logs exist for this niche. The best public anchors are general YouTube editing rates of about **1–2 hours of editing per finished minute** for scripted or story-driven gaming videos, and raw-footage ratios like "2 h 30 min of footage → 20–60 min" for a horror survival video.

ESTIMATED planning numbers:
- About **40–90 h** to build a v1 reusable entity + director mod with Claude Code.
- About **30–60 h** per 15–25 min episode.
- About **80–150 h** per 40–55 min "100 days" movie.

Editing dominates. Scripted events, Flashback markers, offline batch renders and auto-subtitles are the main levers to reduce it.

### Cited Findings
- r/NewTubers creator anecdotes:
  - "it usually takes me 1-2 hours of editing … per minute of finished video. A 20-minute video typically takes me 30-40 hours of editing from conception to rendering" — [Reddit r/NewTubers](https://www.reddit.com/r/NewTubers/comments/1ibr3rc/am_i_taking_too_long_when_it_comes_to_editing/).
  - Game-documentary creators: "between an hour or two per minute"; a ~800K-subscriber peer takes "about an hour per minute" — [Reddit r/NewTubers](https://www.reddit.com/r/NewTubers/comments/1omlxre/spending_8_hours_editing_every_week_and_im).
  - A Minecraft horror-survival creator: "2 hours and 30 min of footage which could easily be cut to anywhere within 20 minutes- 1 hour", citing "the goofy gang (cheap pickle, tinymacdude, wallibear…)" as plot-centric horror-mod examples — [Reddit r/NewTubers (Aug 2025)](https://www.reddit.com/r/NewTubers/comments/1n4ph1k/how_long_should_my_minecraft_horror_survival).
  - A creator survey: "20-min videos taking 8–40 hours"; "Gaming essay creators editing 40+ hours" — [Reddit r/NewTubers](https://www.reddit.com/r/NewTubers/comments/1oyowru/how_long_does_it_really_take_you_to_create_a/np6rgf4?sort=new).
- Big-creator extreme: GeorgeNotFound's 35-minute "150 days" video had "over 50 hours of footage" and took "over 2 years" to finish editing — [YouTube description (2024-01-02)](https://www.youtube.com/watch?v=8lwMYnpqg2c).
- Render cost: shaders can turn a 10-minute render into about 1 hour; supersampling multiplies it again — [flashback-mod.com troubleshooting](https://flashback-mod.com/troubleshooting/).
- Automation hooks that exist:
  - Flashback markers via `/flashback mark` — [flashback-mod.com changelog](https://flashback-mod.com/changelog/).
  - Animated Java function keyframes and Locators that run commands from animations — [AJ README](https://github.com/Animated-Java/animated-java).
  - TMFTF-style config switches (spawn rate, chase durations, jumpscare on/off) — [Modrinth](https://modrinth.com/mod/the-man-from-the-fog).
  - Twixxel's Stalker shows timer-driven event scheduling (15/25/36/10-minute cycles) — [minecraft-guides](https://www.minecraft-guides.com/mod/twixxels-stalker).

### Inferences
- **ESTIMATED — v1 entity + director system (mod route, Claude Code doing most of the Java):**

  | Task | Hours |
  |---|---|
  | Concept + silhouette | 4–8 |
  | Blockbench model + texture | 6–12 |
  | GeckoLib animations (idle, walk, run, stare, crawl, attack, vanish, jumpscare) | 8–16 |
  | AI goals + director + look-detection | 10–25 |
  | Client jumpscare overlay / fog push / sanity shader | 6–12 |
  | Sound design (original or licensed SFX, layered whispers) | 4–10 |
  | Test + tuning in a real client | 6–12 |
  | **Total** | **≈ 44–95 h** |

  Datapack + Animated Java route: modelling and animation take the same time. Logic is about 10–20 h, but tuning AI-faking hacks takes longer, so the total is similar. The datapack route is faster only for a static or scripted "appearance" creature with no real chase AI.
- **ESTIMATED — 15–25 min episode, once the system exists:**

  | Task | Hours |
  |---|---|
  | Outline/script and beat sheet | 3–6 |
  | Set dressing with WorldEdit/Axiom | 2–6 |
  | Gameplay recording (2–4× runtime of raw play, scripted triggers, retakes) | 2–6 |
  | Flashback cinematic shots (20–40 keyframed shots) | 3–8 |
  | Unattended renders | 2–8 |
  | Edit (at ~1–1.5 h per finished minute) | 15–35 |
  | VO/sound mix + subtitles + thumbnail | 4–8 |
  | **Total** | **≈ 30–70 h** (about 25–60 h hands-on) |

- **ESTIMATED — 40–55 min "100 days" movie:**

  | Task | Hours |
  |---|---|
  | Gameplay (compressed, scripted world progression; not literal 100 in-game days) | 15–30 |
  | Cinematic shots | 8–16 |
  | Renders | 6–20 |
  | Edit | 40–80 |
  | Writing/VO/sound | 10–20 |
  | **Total** | **≈ 80–150 h** |

- **INFERRED — what can be automated or templated:**
  1. A scripted event director in our mod with `/director trigger <event>` commands and a deterministic "story mode" config, so recording sessions hit beats on cue instead of waiting for random spawns.
  2. A Flashback marker dropped automatically by the mod at each event (if Flashback exposes a command hook; otherwise the operator types `/flashback mark`). This turns markers into an edit decision list.
  3. Batch overnight renders, one at a time on the GPU.
  4. Auto-subtitles from the VO track (CineFactory already has SRT generation in `tools/cf_auto_edit.py`).
  5. A reusable shot library: establishing fog pans, "entity in treeline" inserts, and jumpscare stings that recur across episodes.
  6. Background extras (villagers/NPC players): fake-player tools such as the Carpet mod's `/player` exist in the ecosystem but were not verified for 26.3 in this session. Using our own scripted NPC entities is safer.
- **INFERRED — biggest risk to the KPI:** editing hours. Scripting events in-engine (deterministic beats) cuts raw footage, and raw footage drives editing time. The "2.5 h footage → 20 min" ratio above suggests targeting ≤ 3:1 raw-to-final for scripted episodes, against roughly 8–60:1 for unscripted survival.

### Gaps
- I found no first-hand production log from a faceless Minecraft horror channel with hours per episode.
- I found no measured render throughput for Flashback + Iris + Complementary on an RTX 3060.
- The Carpet / fake-player status on 26.3 was not checked.
- All hour figures above are ESTIMATED and must be replaced by `data/production_ledger.jsonl` measurements after the first pilot.

---

## 5. Minecraft EULA / Usage Guidelines: can we distribute or monetize our custom mod (free on Modrinth/CurseForge as a growth loop? sell it?) and monetize videos?

### Takeaway
- **Releasing the mod free on Modrinth/CurseForge is allowed.** Distribute the mod only (not a modded game), with no play-to-earn mechanics and no out-of-game ownership checks.
- **Selling the mod, or "trying to make money from" it, is not allowed** under the Java EULA.
- Monetized YouTube videos are explicitly allowed if every video is free to watch in full and adds "enough of your own unique content" such as commentary/narration.
- Do not put "Minecraft" as the dominant part of a channel, mod or product name.

### Cited Findings

**EULA**
- "Any Mods you create for Minecraft: Java Edition from scratch belong to you … and you can do whatever you want with them, as long as you don't sell them for money / try to make money from them and so long as you don't distribute Modded Versions of the game." — [Minecraft EULA](https://www.minecraft.net/en-us/eula).
- "The Minecraft Usage Guidelines often change, and we have the right to withdraw the permissions given in them at any time without notice." — [Minecraft EULA](https://www.minecraft.net/en-us/eula).

**Usage Guidelines — mods**
- "You may create, use, or distribute a mod if: You distribute the mod only and not a modded version of Minecraft; The mod doesn't create a play-to-earn function …; The mod cannot be used to directly or indirectly verify whether a player owns or has access to out-of-game content" — [Minecraft Usage Guidelines](https://www.minecraft.net/en-us/usage-guidelines).
- Sharing your creation with the community counts as "commercial use" under the guidelines "whether you plan to make money off it or not", so the Commercial Use rules apply to a free mod release too — [Usage Guidelines](https://www.minecraft.net/en-us/usage-guidelines).

**Usage Guidelines — videos**
- Monetization is allowed "so long as: All videos (in their entirety) are free to view … You add enough of your own unique content … for example: You can add your own audio commentary … You can't just include your logo, web address, or overlays on top of our or someone else's gameplay – we reserve our right to decide on if your content is unique enough". Sponsor callouts must sit outside the game content and be child-suitable. "You don't sell copies of the videos or streams" — [Usage Guidelines](https://www.minecraft.net/en-us/usage-guidelines).
- Mojang's help article: "You are allowed to create videos of Mojang games, upload or stream from YouTube or other video sites, and monetize those videos." In-game Minecraft music is allowed in monetized gameplay videos; music use outside normal gameplay may be restricted (C418's policy) — [Minecraft Help (2021)](https://help.minecraft.net/hc/en-us/articles/4408934440589-Content-Creation-and-Broadcasting-Terms-of-Use-and-Guidelines).

**Usage Guidelines — naming**
- "You may not use the Minecraft name as the primary or dominant name or title". It may appear in a secondary title or description when necessary to describe the work honestly — [Usage Guidelines](https://www.minecraft.net/en-us/usage-guidelines).

**Usage Guidelines — brand promotion**
- Brand/sponsor promotions built *inside* gameplay are not allowed without approval. Example: "A mod created to allow players to play in a world with branded automobiles" — [Usage Guidelines](https://www.minecraft.net/en-us/usage-guidelines).

**Secondary readings**
- A plain-language reading (checked 2026-10-06) concludes "Sell Java Edition mods or plugins | Not allowed" and "Put videos behind a paywall or sell copies | Not allowed" — [Drate guide](https://drate.app/guides/can-you-sell-minecraft-builds).
- A server-hosting knowledge base found "no Mojang or Microsoft text permitting the sale of Java Edition mods or plugins" — [GameServerKings (checked 2026-08-19)](https://www.gameserverkings.com/knowledge-base/minecraft/monetising-your-server/).

**Market precedent (tension)** — "The Stalker" horror mod advertises a paid "Premium Edition" — [Modrinth](https://modrinth.com/project/custom-entity-the-stalker). This conflicts with the plain EULA text; a third party doing it does not make it compliant.

### Inferences
- **INFERRED — growth loop is allowed:**
  - Publish the creature mod free on Modrinth and CurseForge under our own licence (ARR or a restrictive custom licence protects the creature IP; MIT would let anyone reuse the model).
  - Link it from video descriptions, and have the mod's page link back to the channel.
  - Do not sell it, paywall it, early-access it for money, or tie it to channel memberships. "Members-only early download" would very likely count as "try to make money from" the mod.
- **INFERRED — platform payouts are a grey zone:** CurseForge's author-rewards and Modrinth's creator-monetization programs pay mod authors from ad revenue. The EULA's "try to make money from them" wording arguably covers that. Many authors take part and Mojang has not publicly objected, but I found no Mojang text endorsing it. Conservative default: opt out of payouts, or ask the OWNER to decide.
- **INFERRED — content compliance:** faceless narration and storytelling over our own gameplay counts as "unique content". Do not use in-game licensed music outside gameplay context (C418/Lena Raine policies) or third-party music without licences. CineFactory's policy-check should flag "Minecraft" in a dominant title position and any sponsor overlay inside gameplay.
- **INFERRED — shader and tool licences are compatible with monetized video:** Complementary ("content creation"), Photon ("commercially published … videos") and BSL ("screenshots and videos") all allow it. Axiom is the exception (section 3).

### Gaps
- I found no official Mojang statement on mod-platform revenue-share programs (CurseForge rewards, Modrinth payouts).
- I did not check YouTube's own policies on "repetitious / mass-produced" content and AI disclosure for faceless gameplay channels (out of scope here, but relevant to the channel).
- C418 and Lena Raine music policy pages were not fetched.
