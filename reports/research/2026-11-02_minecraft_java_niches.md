# Minecraft Java & Bedrock: which YouTube niches need it, demand, money, and fit (research 2026-11-02)

Scope: web research only, about 30 minutes. Goal: help the owner decide whether to buy **Minecraft: Java & Bedrock Edition for PC** for a monetised, US-market, original-character YouTube channel.
Labels: **OBSERVED** = read on the linked page (page dates given where shown) · **INFERRED** = my reasoning, not measured.
Subscriber and view counts move every day. Each one is the value printed on the source on the date shown.

---

## 0. Short answer (INFERRED, based on the sections below)

- **Buy it. It is cheap and it opens the formats that get the most views.** The PC purchase is a single $29.99 bundle that includes both Java and Bedrock ([tech-insider, 2026-06-22](https://tech-insider.org/minecraft-java-vs-bedrock-2026/); [minecrafthub, 2026-08-28](https://minecrafthub.io/articles/minecraft-java-vs-bedrock)). OBSERVED. Every machinima tool that matters (Replay Mod, Flashback, BBS/Blockbuster, Iris shaders, Fabric/Forge horror mods) is **Java-only**. Bedrock cannot load Java mods ([flashback-mod.com](https://flashback-mod.com/flashback-vs-replay-mod/); [minecraft.net store page](https://www.minecraft.net/en-us/store/minecraft-java-bedrock-edition-pc)). OBSERVED.
- **The most useful format for this studio is "scripted gameplay" with original characters.** It looks like gameplay but is scripted, voiced and keyframed. **Spawnpoint Media (Milo & Chip, EYstreem)** makes this format in Java with McHorse's Blockbuster/BBS mod plus Replay Mod. Its own job ads say so (section 2.3). OBSERVED. It is the clearest proof that the format can be produced on a pipeline, and the IP is fully original.
- **The catch is money.** Kids-directed Minecraft content will probably be set "made for kids". Median Kids & Teens RPM is **$0.33**, against **$2.05** for Gaming ([AIR Media-Tech, 300 channels, May 2025–May 2026](https://air.io/en/youtube-glossary/what-does-made-for-kids-mean-on-youtube)). OBSERVED. The tone you choose (kids or general audience) affects revenue more than the tool you choose. INFERRED.
- **New YPP entry bar from 2027-02-01: 8,000 watch hours/year or 20M Shorts views in 90 days** ([YouTube Help](https://support.google.com/youtube/answer/12843009?hl=en); [YouTube Blog 2026-08-10](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn)). OBSERVED. A new channel should therefore plan around long-form watch time, not Shorts. INFERRED.

---

## 1. Which niches REQUIRE owning Minecraft, and what each one needs

General facts:
- Java runs only on Windows/macOS/Linux and is the edition for mods (Fabric, Forge, NeoForge) and shaders (Iris/OptiFine). Bedrock uses add-ons and the Marketplace instead. Java mods and Bedrock add-ons are not interchangeable. OBSERVED ([minecrafthub](https://minecrafthub.io/articles/minecraft-java-vs-bedrock); [minecraft.net store](https://www.minecraft.net/en-us/store/minecraft-java-bedrock-edition-pc); [tech-insider](https://tech-insider.org/minecraft-java-vs-bedrock-2026/)).
- Java PC minimum since 2026-07-21: 8 GB RAM, 4-core CPU, Vulkan 1.3 GPU with 2 GB VRAM ([minecrafthub system requirements, 2026-10-10](https://minecrafthub.io/articles/minecraft-system-requirements)). OBSERVED. The studio's RTX 3060 12 GB should be more than enough for vanilla play. Heavy shaders plus Replay Mod rendering were not measured. INFERRED.
- Monetisation is allowed. Minecraft's Usage Guidelines say you may "create, use, and share videos… of you playing or using Minecraft" and earn ad revenue, as long as videos are free to watch and you "add enough of your own unique content". Sponsors must be suitable for children ([minecraft.net/usage-guidelines](https://www.minecraft.net/en-us/usage-guidelines)). OBSERVED. Mojang's "Creator-Safe" music playlist may be used in monetised Minecraft content ([minecraft.net music article, 2023-12-06](https://www.minecraft.net/en-us/article/can-i-use-minecraft-music-)). OBSERVED.

| Niche / format | Needs Java? | Key requirements | Evidence |
|---|---|---|---|
| **Replay Mod cinematics / machinima** | **Yes (Java only)** | Fabric (Forge only up to 1.12.2). Client-side. Records network packets (<10 MB/hour), free camera, keyframe camera paths, built-in renderer, OpenEXR depth export. Shaders through Iris on Fabric. | OBSERVED: [replaymod.com](https://www.replaymod.com/), [Modrinth: 19.6M downloads, MC up to 26.3](https://modrinth.com/mod/replaymod), [minecrafthub](https://minecrafthub.io/mods/replay-mod), [CurseForge docs](https://www.curseforge.com/minecraft/mc-mods/replay-mod-fabric-and-forge) |
| **Flashback** (newer Replay alternative) | **Yes** | Fabric, MC 1.21+ only. More keyframe types, scene switcher, audio track on the timeline. Files do not convert from Replay Mod. | OBSERVED: [flashback-mod.com](https://flashback-mod.com/flashback-vs-replay-mod/) |
| **BBS mod machinima / cutscenes** | **Yes** | Fabric 1.20.1 / 1.20.4 / 1.21.1 (alpha for 26.3). Forge/NeoForge only through Sinytra Connector. Records actor actions, keyframe replay editor, clip-based camera editor, **Blockbench models with animations**, Snowstorm particles. 384.6K downloads. "Versions 2.0 and above are primarily developed with LLMs." Forks: BBS Reforge, BBS FS. | OBSERVED: [Modrinth BBS](https://modrinth.com/mod/bbs-mod), [CurseForge BBS, 2.3.3 dated 2026-10-14](https://www.curseforge.com/minecraft/mc-mods/bbs-mod), [GitHub mchorse/bbs-mod](https://github.com/mchorse/bbs-mod), [BBS Reforge](https://modrinth.com/mod/mod-bbsreforge) |
| (older) Blockbuster mod | Yes | Forge 1.12.2. Multiple actors, director blocks, camera paths, OBJ/MagicaVoxel models, Minema for frame-exact output. Not advised on public servers. | OBSERVED: [mchorse.github.io/blockbuster](https://mchorse.github.io/blockbuster), [GitHub](https://github.com/mchorse/blockbuster) |
| **Scripted roleplay "gameplay"** (Maizen / Milo & Chip style) | **Yes in practice** | Spawnpoint hires "Minecraft Blockbuster Animators" (BBS/Blockbuster Studio on 1.20.1–1.21.1, Blockbench face rigs, Replay Mod, NPC/motion-capture mods, shader-pack editing), a "Minecraft Replay Mod Filmer", "Java Mod Developer", "Minecraft 3D & 2D Modeller", and "Minecraft / Roblox Role-play Body Actor". Actors record VO in a studio; the team builds digital sets in Minecraft and scripts every video. | OBSERVED: [Spawnpoint careers](https://spawnpointmedia.com/careers), [Blockbuster Animator job](https://spawnpointmedia-1677622320.teamtailor.com/jobs/2661298-minecraft-blockbuster-animator), [Tubefilter 2026-06-10](https://www.tubefilter.com/2026/06/10/eystreem-spawnpoint-media-spotter-global-brands-milo-chip) |
| Let's play / survival series | Either edition | Game plus screen recorder (e.g. OBS). Live play and commentary. | INFERRED (common practice; not sourced) |
| **100 Days Hardcore** | Usually Java (modded variants) | Long recorded play. Forge Labs' horror-mod 100-day video is a "3:11:16"-class long upload. Bedrock versions exist (BowsMC, 1M views). | OBSERVED: [Forge Labs](https://www.youtube.com/watch?v=OF4Sw5RMppY), [BowsMC Bedrock 100 days](https://www.youtube.com/watch?v=TJjMK3dpmxw) |
| **"Minecraft but…" challenges** | Yes (datapacks/mods/plugins) | Custom mechanics, usually from custom code or datapacks. YouTube's own history says the format grew from 2019–2020 and needs "manipulating the game". | OBSERVED: [YouTube Trends "One Trillion"](https://youtube.com/trends/articles/minecraft-trillion) |
| SMP series | Yes (servers mostly Java) | A server (Paper/Spigot or modded) and a cast of real creators. Hermitcraft and 2b2t run on Java. | OBSERVED: [tech-insider](https://tech-insider.org/minecraft-java-vs-bedrock-2026/), [Flux Java vs Bedrock servers](https://runonflux.com/games/minecraft/java-vs-bedrock) |
| **Horror (mods/maps)** | **Yes** | Fabric/Forge horror mods (The Broken Script, Man From The Fog, Cave Dweller, Verity, etc.) plus a survival play-through. Bedrock horror add-ons exist (Evident "Bedrock's scariest mod" 1.1M views). | OBSERVED: [Forge Labs Broken Script, 6.9M views](https://www.youtube.com/watch?v=OF4Sw5RMppY), [Pandeh tier list page](https://www.youtube.com/watch?v=bgLf6lmK6MI) |
| Speedrun | Yes (MCSR ranked etc. are Java) | High live skill. | OBSERVED (Java ranked scene): [FrizzClips MCSR Ranked](https://www.youtube.com/watch?v=00nvw4Vxp54); skill requirement INFERRED |
| Building / timelapse / tutorials | Either; Java for Axiom, Replay/Flashback timelapses | Build skill. Xisumavoid quoted using Replay Mod for timelapses. | OBSERVED: [replaymod.com quotes](https://www.replaymod.com/), [minecrafthub Axiom guide listing](https://minecrafthub.io/mods/replay-mod) |
| Redstone | Either (Java mechanics differ) | Deep technical skill. | INFERRED |
| Mod / add-on showcases | Java (mods) or Bedrock (add-ons) | Fabric/Forge. Low production cost. AsianHalfSquat "Ultimate Cinematic Experience" (Fabric 1.21.4) got 1.03M views. | OBSERVED: [AsianHalfSquat video](https://www.youtube.com/watch?v=kxfhfZ0lMEA) |
| Shader / cinematic trailers | Yes | Iris + shader packs + Replay/Flashback. | OBSERVED: [minecrafthub Replay Mod](https://minecrafthub.io/mods/replay-mod), [Opticality Flashback guide 358K views](https://www.youtube.com/watch?v=KVqOTtCLff8) |
| Parkour Shorts backgrounds | **No** (free "no copyright" parkour footage exists) | Footage channels offer free parkour loops (Orbital: 4.1M views on one loop). Monetisation risk: see section 3. | OBSERVED: [Orbital NCG](https://www.youtube.com/watch?v=u7kdVe8q5zs) |
| Bedrock Marketplace / add-ons | **Bedrock** (included in the bundle) | Partner Program application (selective), 70% revenue share, quarterly payout, $200 minimum (third-party guide). The Marketplace is Bedrock-only and holds about 36,719 pages of content from 326 creators (2026-06-25). Spawnpoint's first Milo & Chip skin pack "outsold Star Wars on Minecraft Marketplace". | OBSERVED: [generalistprogrammer guide 2026-03](https://generalistprogrammer.com/tutorials/how-to-become-minecraft-marketplace-partner-guide), [Minecraft Wiki Marketplace](https://minecraft.wiki/w/Marketplace), [CB Insights quoting Tubefilter](https://www.cbinsights.com/company/spawnpoint-media) |

### 1b. Where owning Minecraft also helps the current Blender / Mine-imator animation pipeline
- **Mineways** exports worlds from **Java Edition** saves (up to 26.3) to OBJ/USD for Blender. Bedrock worlds must be converted first. It "normally need[s] your Minecraft world to be saved on your computer". OBSERVED ([Mineways](https://www.realtimerendering.com/erich/minecraft/public/mineways/), [Mineways downloads](https://www.realtimerendering.com/erich/minecraft/public/mineways/downloads.html)).
- **MCprep** (Blender add-on) is built around worlds exported by jmc2obj/Mineways. It provides mob/item rigs, material prep and animated textures. OBSERVED ([GitHub MCprep](https://github.com/Moo-Ack-Productions/MCprep)).
- **Chunky** path-traces Java Edition worlds (1.2.1 and up). OBSERVED ([Chunky docs](https://chunky-dev.github.io/docs)). Its README notes that missing textures show as red crosses and need a texture pack for the right version ([Chunky README](https://github.com/chunky-dev/chunky/blob/master/README.md?plain=1)). OBSERVED.
- **Mine-imator** says it animates "blocks, items and the lovable characters from Minecraft" and is not affiliated with Mojang ([mineimator.com](https://www.mineimator.com/)). OBSERVED.
- INFERRED: owning Java gives the studio (a) a legitimate licence and its own vanilla texture/asset source, (b) the ability to build sets quickly in-game (or with Axiom) and export them through Mineways into the existing Blender + MCprep pipeline, and (c) a BBS/Replay previs or "gameplay-look" layer. The Usage Guidelines also say all rights in Minecraft "assets, and any derivatives" stay with Mojang/Microsoft and that permission can be revoked ([usage guidelines](https://www.minecraft.net/en-us/usage-guidelines)). OBSERVED. So vanilla assets in videos are used under Mojang's permissions, not owned. INFERRED; the owner should read that page once.

---

## 2. Demand evidence 2025–2026

### 2.1 Size of Minecraft on YouTube
- 1 trillion views in 2021 (35,000+ creator channels in 150 countries). In 2021 "Minecraft, But…" was the top category at over 5B views, with animations close behind at 4.9B. OBSERVED, **stale (2021)** ([TechSpot 2021-12-15](https://www.techspot.com/news/92644-minecraft-youtube-videos-have-collectively-gained-over-one.html); [YouTube Trends](https://youtube.com/trends/articles/minecraft-trillion)).
- 1.5T views by May 2024 ([YouTube Blog 2024-05-28](https://blog.youtube/culture-and-trends/minecraft-15/)). OBSERVED.
- **"Now at 2T"** in YouTube's 20th-anniversary Culture & Trends report (data to April 2025) ([Google PDF](https://services.google.com/fh/files/misc/trends-20th-birthday.pdf)). OBSERVED. INFERRED: roughly 1T new views in about 3.5 years, so on the order of 250–300B views/year.
- In the US, Minecraft is called "one of the largest gaming communities on YouTube" ([Think with Google 2025-02-03](https://business.google.com/us/think/search-and-video/2025-youtube-trends/)). OBSERVED. In the 2025 year-end report, "A Minecraft Movie" is a trending topic ([2025 Global Culture & Trends report](https://kstatic.googleusercontent.com/files/566d8945f160e9ca0d48ff1cdd9dbde2da073192f893e99f3d81c045b82f30c8b1fef85317d5ebe937217e18efd25def312f71bd745f43d9a3a9629e20a68686)). OBSERVED.
- The official Minecraft channel had 543.7M views in one week (Tubefilter top 50, July 2026), driven by Shorts ([Northeast Times 2026-07-14](https://northeasttimes.com/2026/07/14/world-cup-and-minecraft-are-reshaping-youtube-s-global-charts)). OBSERVED, secondary source.
- In May 2026, "minecraft challenge" had the best views per video of any gaming topic in hype.ad's 30-day sample: 595,666 average over 13 videos ([hype.ad May 2026](https://hype.ad/blog/trending-topics/gaming/may-2026)). OBSERVED. The sample is small.

### 2.2 Which formats lead, with notable channels (ThoughtLeaders data as of October 2026, [source](https://www.thoughtleaders.io/blog/best-minecraft-youtubers), OBSERVED)
"Typical views per new video" is ThoughtLeaders' projection.
- **Challenge / kids** ("where the highest view counts on Minecraft YouTube are right now"): Farzy 3.2M subs / ~4.78M per video; EYstreem 13.9M / ~2.28M; PrestonPlayz 17.9M / ~2.01M; Cash 11.7M / ~1.52M; Bionic 8.9M / ~1.44M; Wisp 5.9M / ~774K; SSundee 25.5M / ~623K; Johnny Minecraft 5.0M / ~289K.
- **Roleplay & animation** ("fastest growing corner… young audience"): Maizen 17.8M / ~1.64M; GameToons 12.8M / ~1.57M; MSToons 1.7M / ~1.38M; **Milo and Chip 4.8M / ~1.26M (started 2023)**; Aphmau 25.3M / ~1.15M; Doni Bobes 4.6M / ~894K.
- **Building / survival**: Grian 8.9M / ~1.25M; LDShadowLady 7.6M / ~1.05M; GeminiTay 2.2M / ~583K.
- **SMP**: Dream 34.8M / ~4.59M (rare uploads); SmallishBeans 4.1M / ~518K. Separately, Unstable SMP episodes reached 5.6M–7.3M views (Spoke 2.85M subs; Wemmbu 4.75M subs) ([Spoke](https://www.youtube.com/watch?v=8_Au10osdEo), [Wemmbu](https://www.youtube.com/watch?v=_hyFGrcVv5U)).
- **Technical**: Mumbo Jumbo 9.8M / ~1.25M; Skip the Tutorial 10.6M / ~661K.
- Audience split: "building, SMP and technical channels skew older… roleplay, animation and challenge channels reach kids and young teens at very high volume". OBSERVED (same source).
- **Horror** (single videos, OBSERVED on the video pages): Forge Labs (6.23M subs) "Surviving Minecraft's Best Horror Mod", 6.9M views ([link](https://www.youtube.com/watch?v=OF4Sw5RMppY)); Chiefxd (795K) horror one-chunk, 3.9M ([link](https://www.youtube.com/watch?v=BJiFY7vJvLo)); **Liskia with 21.2K subs got 1.5M views** on a horror-mod ranking ([link](https://www.youtube.com/watch?v=2XXWYMBwg1k)). That last one is an outlier, but it shows small channels can break out. YouTube's 2025 report says Minecraft-first creators "dialled up the horror in 2025" (regional, India) ([2025 report](https://kstatic.googleusercontent.com/files/566d8945f160e9ca0d48ff1cdd9dbde2da073192f893e99f3d81c045b82f30c8b1fef85317d5ebe937217e18efd25def312f71bd745f43d9a3a9629e20a68686)).
- **Speedrun/cinematic hybrids**: Evbo (4.15M) "SPEEDRUN ACADEMY" 5.9M views. It is voiced by actors, i.e. a scripted "civilization movie" format ([link](https://www.youtube.com/watch?v=N4zqNUGdLSk)). OBSERVED.
- **Animation (Blender etc.)**: Rainimator 2.45M subs (vidIQ 2026-10-24) ([vidIQ](https://vidiq.com/youtube-stats/channel/@rainimator)). The Minecraft Animation wiki lists Black Plasma Studios (now Squared Media) at 8.21M as the most-subscribed Blender user ([fandom](https://minecraftanimation.fandom.com/wiki/List_of_commonly_used_Minecraft_animation_programs_and_their_foremost_users)). OBSERVED; the wiki number may be stale.

### 2.3 Are there successful channels BUILT on Replay Mod or BBS?
- **As a production tool inside a big format: yes.** Spawnpoint Media (EYstreem 13.9M, Milo & Chip 4.8M, Firelight 4.6M on its site) has a department called "Animation (Blockbuster & Replay)". It hires Blockbuster/BBS animators and Replay Mod filmers. It says it produces "10+ episodes each week in-house" and has 100+ staff ([spawnpointmedia.com](https://spawnpointmedia.com/), [careers](https://spawnpointmedia.com/careers), [Tubefilter 2024-06-05](https://www.tubefilter.com/2024/06/05/eystreem-spawnpoint-media-spotter-investment)). Milo & Chip produced "16 billion watch minutes from May–October 2025" ([Tubefilter 2026-06-10](https://www.tubefilter.com/2026/06/10/eystreem-spawnpoint-media-spotter-global-brands-milo-chip)). OBSERVED.
- **As a standalone "Replay/BBS cinematics" genre: no large channel found.** The BBS wiki names series (e.g. "Flashman", "Deltacraft") and says "several machinima channels and production groups have since adopted BBS" ([BBS wiki](https://bbsmod.miraheze.org/wiki/BlockBuster_Studio_(BBS))). McHorse keeps a playlist of 1,000+ Blockbuster community videos ([GitHub](https://github.com/mchorse/blockbuster)). Channel sizes: **not measured**. The visible "cinematic" videos are mostly tutorials (Opticality 4.38K subs, 358K views; Laynce "How to Make Movies in Minecraft" 217K) ([link](https://www.youtube.com/watch?v=KVqOTtCLff8)). OBSERVED. INFERRED: viewers come for the story and characters, not the tool. A Replay/BBS showcase channel is a weak niche on its own, but the tools are strong inside the scripted-roleplay or challenge format.
- **Maizen's own toolchain: not measured.** Maizen started in Japan. The English version is dubbed by professional voice actors ([r/Maizen FAQ](https://www.reddit.com/r/Maizen/comments/s9o53x/what_is_maizen_origin_and_faq); [Maizen fandom wiki](https://fanmaizen.fandom.com/wiki/Maizen)). OBSERVED, fan sources. Maizen's fan-content guidelines allow monetised fan videos ([maizen.com/usage-guidelines](https://www.maizen.com/usage-guidelines)). OBSERVED. Hundreds of JJ/Mikey fan channels exist, e.g. "Funny Maizen" 136K and "Mikey & JJ – Minecraft" 648K. They state they are made by ">20 specialists" ([example](https://www.youtube.com/watch?v=29HV5HxKNLU)). OBSERVED. **Our rule forbids using JJ/Mikey even though Maizen permits it.** These channels show the format is saturated with derivative copies. INFERRED.

---

## 3. Monetisation: gaming vs made-for-kids, Shorts vs long-form

- **Gaming RPM:**
  - AIR median $2.05; middle 50% $0.70–$3.62 (May 2025–May 2026) ([overseeros quoting AIR](https://www.overseeros.com/blog/youtube-rpm-by-niche)). OBSERVED.
  - vidIQ's 2026 sub-niche estimate: "Minecraft and Roblox: around $3–$5", Let's Plays $2–4 (same page). OBSERVED, secondary.
  - Gyre: median **US** gaming RPM about $3.50 ([Gyre 2026-05-20](https://gyre.pro/blog/youtube-gaming-channel-ways-to-increase-the-number-of-subscribers-in-)). OBSERVED.
  - Hypertube: Minecraft RPM $1–3 typical, CPM $2–6, higher for US/UK/AU audiences ([Hypertube 2026-07-13](https://hypertube.io/blog/how-much-do-minecraft-youtubers-really-make-2026-data)). OBSERVED.
  - The sources disagree. Treat **$1–4 long-form RPM for a US-skewed, general-audience Minecraft channel** as the planning band. INFERRED.
- **Made for kids (COPPA):**
  - Personalised ads are off, along with comments and notifications.
  - Kids & Teens median RPM $0.33 (middle half $0.16–$0.88). Kids CPM $1.59. Only 32% of kids' views carried an ad ([AIR](https://air.io/en/youtube-glossary/what-does-made-for-kids-mean-on-youtube); [MilX 2026-10-12](https://milx.app/en/guidelines/guide-to-monetize-videos-in-youtube-kids-niche)). OBSERVED.
  - Other estimates: $1–3 ([Gyre](https://gyre.pro/blog/how-to-monetize-a-youtube-kids-channel)). Industry estimates put the drop at 50–90%+, and YouTube does not publish a figure ([makeinfluence](https://www.makeinfluence.com/en/academy/youtubes-made-for-kids-coppa-classification-what-it-does-to-ad-revenue)). OBSERVED.
  - Penalty up to $53,088 per violation. The FTC updated the COPPA Rule in January 2025 ([MilX](https://milx.app/en/guidelines/guide-to-monetize-videos-in-youtube-kids-niche); [AIR](https://air.io/en/youtube-glossary/what-does-made-for-kids-mean-on-youtube)). OBSERVED.
  - vidIQ warns that Minecraft/Roblox content can be classified as made for kids even when aimed at adults. Commentary style and language are the main signal ([vidIQ](https://vidiq.com/blog/post/get-full-youtube-monetization-gaming-videos)). OBSERVED.
  - INFERRED: Maizen/Milo & Chip-style animation and roleplay, with cartoon characters and simple stories, will very likely be treated as made for kids. Honest labelling is required. Horror, SMP, technical and building formats skew older (section 2.2) and stay in gaming RPM ranges. **The same original cast pitched at a teen/general audience (horror-lite, mystery, challenge) could earn about 3–10x more per view than a kids pitch.** INFERRED from the RPM medians above. Our own numbers: not measured.
  - How big kids brands earn: Spawnpoint relies on brand deals aimed at parents, syndication (Roku, Prime, Apple TV), toys and Marketplace skin packs ([Tubefilter 2026](https://www.tubefilter.com/2026/06/10/eystreem-spawnpoint-media-spotter-global-brands-milo-chip)). OBSERVED.
- **Shorts vs long-form:**
  - AIR (274 channels): Shorts RPM is about 3–14% of long-form in most niches. Gaming example: $1.79 long-form vs $0.17 Shorts. US Shorts RPM about $0.328 ([AIR Shorts study 2026-09-16](https://air.io/en/air-data-findings/youtube-shorts-rpm-vs-long-form-how-much-do-shorts-earn-in-2026); [overseeros](https://www.overseeros.com/blog/youtube-rpm-by-niche)). OBSERVED. Gyre cites $0.03–0.08 for gaming Shorts. OBSERVED.
  - From 2027-02-01, Shorts revenue share needs **10M qualified Shorts views per 90 days** even for channels already in YPP ([YouTube Blog](https://blog.youtube/news-and-events/youtube-partner-program-updates-2027-new-opportunities-earn)). OBSERVED. Use Shorts for discovery only. INFERRED.
- **Policy risk for automation:**
  - On 2025-07-15, YouTube renamed "repetitious" to **"inauthentic content"** (mass-produced or repetitive). Examples given: "narrated stories with only superficial differences", "slideshows that all have the same narration". Using AI is fine if the content is original and authentic ([YouTube monetization policies](https://support.google.com/youtube/answer/1311392?hl=en); [TeamYouTube FAQ](https://support.google.com/youtube/thread/356734251?hl=en&msgid=357121869)). OBSERVED.
  - Parkour-background story Shorts are the textbook case of this risk ([Longform Studio](https://longformstudio.app/articles/reddit-stories-youtube-channel); [Digiday 2025-07-18](https://digiday.com/media/youtubes-ai-slop-crackdown-has-creators-concerned-marketers-cheering)). OBSERVED.

---

## 4. Difficulty and cost for a small automated studio

| Niche | Live play skill? | How much can be pipelined (INFERRED) | Time per video |
|---|---|---|---|
| Scripted roleplay with original cast (BBS + Replay/Flashback + Blockbench rigs) | Low to medium: "body actors" perform once, then keyframe edits | **High.** Script → VO → record actor takes on a private world → BBS keyframes/camera → Replay/Flashback render → our auto-edit/QC. BBS saves editable keyframe data. | Spawnpoint: 30+ videos/month with ~80 staff (2024) ([Tubefilter 2024](https://www.tubefilter.com/2024/06/05/eystreem-spawnpoint-media-spotter-investment)). OBSERVED. Ours: not measured. Needs a pilot. |
| Blender/MCprep original animation (current) | None | High (already in CineFactory) | Ours is in `data/production_ledger.jsonl`; not re-read for this note |
| Horror-mod survival / 100 days | **High**: real play and a commentary persona | Low to medium: mod setup can be scripted; the play cannot | Forge Labs uploads run 3–4 hours; play time is far longer (INFERRED) |
| "Minecraft but" / challenge | Medium; needs datapack/mod dev plus a voiced host character | Medium: custom datapacks are reusable; the host can be an original voiced character (Evbo uses voice actors) | not measured |
| SMP | Needs a cast of real players and a community | Low | not measured |
| Speedrun / redstone | **High** skill | Low | not measured |
| Building / timelapse / tutorial | Medium build skill (Axiom/WorldEdit speed it up) | Medium: Replay/Flashback timelapse plus narration | not measured |
| Mod showcase / shader cinematics | Low | Medium to high, but thin originality (inauthentic-content risk if templated) | not measured |
| Parkour backgrounds | None | Very high, but that is exactly what the policy targets | n/a |
| Marketplace skin/world packs | None (Blockbench art) | Medium. Partner approval needed. A good later merch path for original IP. | not measured |

Cost (OBSERVED unless noted): game $29.99 one-time. Replay Mod, Flashback, BBS, Fabric, Iris, Mineways, Chunky and MCprep are free. BBS is ARR-licensed; Replay Mod is GPL ([Modrinth BBS](https://modrinth.com/mod/bbs-mod); [Modrinth ReplayMod](https://modrinth.com/mod/replaymod)). A private server is optional; single-player or a LAN world is enough for actor recording (INFERRED). Hardware: the existing RTX 3060 12 GB box. One heavy job at a time per CLAUDE.md, so Replay/BBS renders queue with Blender renders (INFERRED).

---

## 5. Stale or weak data flags
- Category totals by format (5B "Minecraft But", 4.9B animation) are **2021**. No newer per-format totals were found.
- Black Plasma/Squared Media 8.21M comes from a fan wiki; the date is unclear.
- "Typical views" are ThoughtLeaders **projections**, not medians of our own pull. Our own `tools/cf_research_stats.py` medians were **not run** for this note.
- RPM sources are mostly vendor blogs (AIR/MilX share one dataset; Gyre, Hypertube, vidIQ). They disagree by about 2x.
- Maizen's production tools and made-for-kids status: **not measured**.
- No search covered the sizes of standalone BBS/Replay channels; this is **not measured**, not proven absent.

---

## 6. Ranked table (fit for an automated ORIGINAL-character studio, US market)

| Rank | Niche | Needs Java? | Demand evidence | Competition | Fit for automated original-character studio |
|---|---|---|---|---|---|
| 1 | **Scripted "gameplay-look" roleplay/story with our original cast** (BBS + Replay/Flashback, Blockbench rigs) | **Yes** | Very high: Milo & Chip 4.8M subs, ~1.26M views/video, started 2023; Maizen 17.8M / ~1.64M | Very high (Maizen + hundreds of JJ/Mikey copies, Spawnpoint) | **High.** Proven to be pipeline-able (Spawnpoint). Original IP is required anyway. Risk: made for kids → ~$0.33 RPM unless the tone targets teens. |
| 2 | **Original Blender/MCprep animation** (current pipeline; Java used for world export and textures) | Helps (Mineways needs Java saves) | High: MSToons 1.7M / ~1.38M per video; GameToons 12.8M; Rainimator 2.45M | High | **High** (already built). Java mainly speeds up set building. Same made-for-kids caveat. |
| 3 | **Story-driven horror/mystery with original characters** (horror-mod look, scripted rather than live) | **Yes** | Very high: Forge Labs 6.9M, Chiefxd 3.9M, 21K-sub Liskia 1.5M | High | **Medium-high.** Older audience → gaming RPM, not kids RPM. Must stay scripted to avoid needing live play skill. Use our own entities, not third-party mod mobs, for IP safety (INFERRED). |
| 4 | "Minecraft but…" challenges hosted by a voiced original character | **Yes** (datapacks/mods) | Very high: challenge is the top-views corner; 595K avg/video in May 2026 sample | Very high | **Medium.** Needs datapack dev and a strong host persona. Evbo shows voice-acted scripted variants work. |
| 5 | Building / timelapse / tutorial | Either | Medium-high: Grian ~1.25M; adult audience | High | Medium. Skill-bound. Better RPM, not kids. |
| 6 | Mod showcase / shader cinematics | Yes | Medium: AsianHalfSquat 1.0M on one video | Medium | Medium-low. Low originality per video; inauthentic-content risk if templated. Better used as B-roll and technique. |
| 7 | Bedrock Marketplace skins/worlds of our cast | Bedrock (bundle) | Indirect: Milo & Chip pack "outsold Star Wars" | Medium (326 partner creators) | **Later-stage merch** once the IP has fans. Partner approval needed. |
| 8 | 100 Days Hardcore / let's play | Usually Java | High (Forge Labs, EYstreem) | Very high | Low. Needs long live play and a personality. |
| 9 | SMP series | Yes | High (Unstable SMP 5–7M) | Very high, cast-dependent | Low. Needs real creator collaborators. |
| 10 | Speedrun / redstone | Yes / Either | Medium (Evbo hybrids high) | High | Low. Pure skill. |
| 11 | Parkour Shorts backgrounds | No | High raw Shorts views | Saturated | **Avoid.** Inauthentic/reused-content risk; Shorts RPM about $0.03–0.33; the 10M/90-day Shorts bar from Feb 2027. |

Suggested next step (INFERRED; owner decides): buy the $29.99 bundle, then run **one measured pilot**: a 60–90 s scene of our original cast made with BBS (Fabric 1.21.1) and Flashback, timed end to end and logged with `tools/cf_decision.py`. Compare quality and minutes per finished minute against the current Blender/MCprep scene before committing a channel format. Decide the audience (kids/made for kids vs teen/general) **before** scripting, because that choice moves RPM about 3–10x.
