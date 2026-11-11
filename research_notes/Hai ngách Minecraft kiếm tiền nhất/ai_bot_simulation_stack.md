# AI-bot "civilization simulation" stack for a small faceless Minecraft studio (state as of 2026-11-12)

Scope: can one Windows PC (RTX 3060 12 GB), with Claude Code and Fabric/NeoForge modding skill, run 20–200 bot players on its own server and film a convincing 30–50 min "civilization" story — and at what cost/effort.
Labels: **OBSERVED** = stated in the linked source (date given when known) · **INFERRED** = my reasoning from cited facts · **ESTIMATED** = arithmetic on cited numbers with stated assumptions. Nothing was installed, downloaded, purchased or run. No costs below were measured on our hardware.
Note on sources: several sources describe models/papers dated after mid-2026 (GPT-6.1 Sol/Terra, Gemini 4 Argon, Claude Opus 5.5, arXiv 2610.22319). They were taken as found in search results and are flagged where only secondary coverage exists.

## 1. Frameworks and Minecraft-version support (late 2026)

### Takeaway
No LLM-agent framework supports the current release (26.3) natively. The only version where *every* piece (Mindcraft, Mineflayer, Baritone, Citizens, Carpet-family fake players, Replay Mod, Flashback) overlaps is **1.21.11** (Mindcraft's ceiling); Mineflayer alone reaches 26.1, and 26.2/26.3 need forks or ViaProxy. Server-side "fake player"/NPC mods and plugins (Carpet, PuppetPlayers, Fake Player Plugin, Citizens) are current to 26.3.

### Cited Findings
- OBSERVED: Mineflayer (PrismarineJS) README: "Supports Minecraft 1.8 to 26.1" — [Mineflayer docs](https://prismarinejs.github.io/mineflayer); releases 4.37.1 (May 2026), 4.38.0 (Aug), 4.39.0 (Sep 2026), last push 2026-10-27 — [Hysen Labs summary, 2026-09-22](https://hysenlabs.com/projects/prismarinejs-mineflayer).
- OBSERVED: 26.2 support is an open PR (#3926, opened 2026-06-16); blocker is missing minecraft-data for 26.2 (only protocol.json/version.json); a community member ran a full LLM-agent workload on 26.2 with self-patched packages — [PR #3926](https://github.com/PrismarineJS/mineflayer/pull/3926); [Issue #3952](https://github.com/PrismarineJS/mineflayer/issues/3952).
- OBSERVED (2026-10-21): "26.3 support is being worked on in #4124 … there's no release with it yet"; workaround = ViaProxy 3.4.13+ in front of a 26.3 server, bot connects as a 26.1 client — [Mineflayer discussion #4190](https://github.com/PrismarineJS/mineflayer/discussions/4190).
- OBSERVED: an independent fork (zkonikishi/Mineflayer) maintains native 26.2 (protocol 776), validated on Paper 26.2-92 (2026-09-15) — [GitHub zkonikishi/Mineflayer](https://github.com/zkonikishi/Mineflayer). Not official; unknown maintenance horizon (INFERRED).
- OBSERVED: Mindcraft (mindcraft-bots/mindcraft, MIT, ~5.8–6K stars): "Minecraft Java Edition (up to v1.21.11, recommend v1.21.6)"; Node v18/v20 recommended, "Node v24+ may cause issues"; ViaProxy suggested for unsupported versions; warns not to connect to public servers with code-writing enabled — [GitHub mindcraft](https://github.com/mindcraft-bots/mindcraft); version line still 0.1.x, maintainers "currently not very responsive to github issues" — [Hysen Labs, 2026-09-10](https://hysenlabs.com/projects/mindcraft-bots-mindcraft).
- OBSERVED: An active community fork exists, Mindcraft-CE (`mindcraft-ce/mindcraft-ce`), which ships the "Andy" local models — [mindcraft-ce docs](https://raw.githubusercontent.com/mindcraft-ce/mindcraft-ce/develop/docs/andy.md).
- OBSERVED: Y Combinator's open-source `minecraft-agent-harness` (MIT, Mineflayer-based, skill library partly from Mindcraft) ships a dev server "Paper 1.21.6 on localhost:25565, offline mode"; supports Claude, GPT, Gemini, OpenRouter or any OpenAI-Responses endpoint; "a survival server with 50 agents on it at once"; multi-agent teams from one JSON; each agent gets a shell (E2B/Docker/local folder — "local means commands run as you") — [GitHub yc-software/minecraft-agent-harness](https://github.com/yc-software/minecraft-agent-harness).
- OBSERVED: Voyager (MineDojo) README pins `fabric-loader-0.14.18-1.19` as "the version Voyager is tested on" and uses GPT-4 — [GitHub MineDojo/Voyager](https://github.com/minedojo/voyager). INFERRED: research artifact, not a 2026 production option.
- OBSERVED: Project Sid (Altera, arXiv 2411.00114, Oct 2024): technical report only; the GitHub repo contains only the PDF, README and a visual abstract (2 commits) — no runnable code — [GitHub altera-al/project-sid](https://github.com/altera-al/project-sid); "It is a research report, not a game or a product you can download" — [Arcanum RPGs, 2026-10-26](https://arcanumrpgs.com/blog/project-sid-explained).
- OBSERVED: Baritone v1.20.0 "For Minecraft 26.3. Forge … Fabric … NeoForge supported" (assets dated 2026-09-23); v1.17.0 for 1.21.11 released ~2026-09-03 — [Baritone releases](https://github.com/cabaletta/baritone/releases); [Issue #5048](https://github.com/cabaletta/baritone/issues/5048). Baritone is a client-side mod (drives a real client), not a server-bot framework (INFERRED from [baritonemc.net](https://baritonemc.net/) "Client-side").
- OBSERVED: Citizens2 CI build #4269 (2026-11-01) built modules `citizens-v26_1_R1`, `v26_2_R1`, `v26_3_R1` (plus 1.8–1.21 modules) — [Citizens Jenkins](https://ci.citizensnpcs.co/job/Citizens2/lastBuild).
- OBSERVED: Carpet Mod 26.1 release (2026-04-02) "Fixed memory leaks and fake players … added support for elytra flying with fake players" — [fabric-carpet v26.1](https://github.com/gnembon/fabric-carpet/releases/tag/v26.1); Carpet PvP fork supports Fabric 1.21.11, 26.2, 26.3 with navigating, fighting server-side bots — [GitHub Carpet-PvP](https://github.com/AndrewCTF/Carpet-PvP).
- OBSERVED: PuppetPlayers (Fabric, MIT) — fake players for 1.21.5–26.3, "Puppet players send packets to interact with the server, like a real player" — [Modrinth PuppetPlayers](https://modrinth.com/project/8fH4Iml8); Fake Player Plugin 2.0 (Paper/Purpur/Folia 1.21.x–26.3) with A* pathfinding, PvE combat, custom skins — [Modrinth FPP](https://modrinth.com/plugin/fake-player-plugin-fpp); PlayerBatch (Fabric+Carpet, 1.21.11) "supports up to 256 bots by default" — [Modrinth PlayerBatch](https://modrinth.com/mod/playerbatch).
- OBSERVED (local, verified 2026-10-05): 26.x mods need Java 25 and mojmap/no-remap; 1.20.5–1.21.11 = Java 21 — `/root/.claude/plugins/.../minecraft-modding/references/version-baselines.md`.

### Inferences
- INFERRED: Practical pin = **Minecraft 1.21.11** (Mindcraft ceiling, Mineflayer official, Baritone/Citizens/Carpet-family/Flashback/Replay Mod all have builds). Cost: our modding baseline notes are 26.x-centric; a 1.21.11 mod/datapack is Java 21 and a different mapping era, so custom datapacks/mods must target that baseline. Alternatively 26.1 if we drop Mindcraft and use the YC harness/raw Mineflayer (YC harness itself defaults to 1.21.6).
- INFERRED: "200 bot players" should not mean 200 Mineflayer LLM clients. A realistic architecture = a few LLM-driven *client* bots (Mineflayer/Mindcraft/YC harness) for named characters + many *server-side* fake players/NPCs (Citizens on Paper, or Carpet/PuppetPlayers on Fabric) as scripted extras.
- INFERRED: MineStudio/VPT-style pixel/keyboard RL agents are not a fit (training-heavy, GPU-heavy); not researched further.

### Gaps
- MineStudio's 2026 version support not checked (out of time budget).
- Whether Citizens NPCs can be driven by an external LLM process with acceptable latency — no source found; would be our own glue code.

## 2. How many concurrent bots on consumer hardware; server software; offline mode and the EULA

### Takeaway
Server load, not the LLM, is the scale ceiling: Altera's 1,000-agent runs broke their Minecraft server and they analysed 500. Mineflayer bots are light in RAM (~30–50 MB each per one source) but pathfinding is CPU-heavy. Running bots in offline mode on a private server is technically standard for testing, but Mojang's Usage Guidelines say server access "must only be granted to users who have a genuine paid-for version of Minecraft"; whether code bots on a private server breach that is **not clearly answered** by Mojang — owner decision.

### Cited Findings
- OBSERVED: "We have also simulated societies with over 1000 agents, but these runs exceeded the computational constraints of our Minecraft server environment, causing agents to be sporadically unresponsive. Therefore, the results below are analyzed using a single 500-agent simulation." — [arXiv 2411.00114 (2024)](https://arxiv.org/html/2411.00114).
- OBSERVED (secondary deep-read of the paper): actual Sid experiments were 25 agents/30 min, 49 agents/4 h, 30 agents/20 min (specialization), 29 agents/20 min (tax vote), 500 agents/2.5 h (culture); GPT-4o was required ("not possible with older base LMs"); no cost or token data published — [parkershamblin/minecraft-ai-agents research notes](https://github.com/parkershamblin/minecraft-ai-agents/blob/main/docs/research/emergent-garden-lessons.md).
- OBSERVED (hosting blog, not a controlled benchmark): "A single computer running Mineflayer can simulate 50-200 bots depending on available RAM (each bot consumes roughly 30-50MB)" — [Fumora Lab, 2026-07-30](https://www.fumora.net/lab/minecraft-load-testing).
- OBSERVED: a user running 30+ Mineflayer bots with pathfinder+pvp plugins reported heavy load on a Ryzen 9 5900X; maintainer: "A* pathfinding is an expensive operation, especially if you are running many bots" — [mineflayer issue #3070 (2023)](https://github.com/PrismarineJS/mineflayer/issues/3070).
- OBSERVED: a load test pushed Paper on a 4-core VM from 0 to 40 sprinting Mineflayer bots; Java server tick runs on one main thread so single-core speed decides capacity — [ComputingForGeeks, 2026-10-27](https://computingforgeeks.com/best-hardware-minecraft-server).
- OBSERVED: a Mineflayer bot-fleet author running server + fleet on one machine: "that makes them feel laggy (movement stutters)" — [GitHub PolpEdu/mcctf-bots](https://github.com/PolpEdu/mcctf-bots).
- OBSERVED: YC ran 50 GPT agents on one survival server for 3 h — [YC harness README](https://github.com/yc-software/minecraft-agent-harness); [The Decoder, 2026-11-02](https://the-decoder.com/one-brutal-minecraft-night-scared-50-ai-agents-into-inventing-chicken-handoff-protocols-a-fertilizer-officer-and-fishing-shifts).
- OBSERVED: Mojang Usage Guidelines, Servers and hosting: access to your server "Must only be granted to users who have a genuine paid-for version of Minecraft" — [minecraft.net usage guidelines](https://www.minecraft.net/en-us/usage-guidelines); a hosting blog reports this section unchanged between 2026-01-01, 2026-09-05 and 2026-11-03 — [Space-Node, 2026-11](https://space-node.net/blog/minecraft-eula-monetization-rules-2026).
- OBSERVED: EULA: "For the server version of Minecraft: Java Edition, you can install it on a server and host online play" — [minecraft.net EULA](https://www.minecraft.net/en-us/eula).
- OBSERVED: Mojang enforcement reply (quoted by a third-party project, 2024): custom authentication "may or may not violate the Minecraft EULA … As long as you ensure that players are using legitimate Microsoft accounts and a valid copy of Minecraft, the use of a Custom Authentication Server may not be problematic"; the project author's opinion: Mojang likely wouldn't object to a small group who own the game running bots with Mineflayer — [unmojang/drasl issue #106](https://github.com/unmojang/drasl/issues/106).
- OBSERVED: offline mode's legitimate uses are "local or development testing servers", e.g. joining a test server several times without several accounts — [madelinemiller.dev (2021)](https://madelinemiller.dev/blog/minecraft-offline-mode); community view that offline-mode servers admitting unpaid humans breach EULA — [SpigotMC thread (2015)](https://www.spigotmc.org/threads/question-online-mode-false-illegal.65685).
- OBSERVED: Mineflayer/YC tooling use `auth: 'offline'` on own/test servers and `--auth microsoft` for online-mode — [zkonikishi/Mineflayer README](https://github.com/zkonikishi/Mineflayer); [YC harness README](https://github.com/yc-software/minecraft-agent-harness).
- OBSERVED: server-side fake players (Carpet etc.) are spawned by command without any client connection or account — [Carpet (Aternos version) description](https://modrinth.com/project/carpet-aternos-version); [PuppetPlayers](https://github.com/senseiwells/PuppetPlayers).

### Inferences
- ESTIMATED (one PC, RTX 3060 box, CPU unknown): Minecraft server + ~10–20 Mineflayer LLM bots + 1 recording client is plausible; 50 Mineflayer bots with pathfinding on the same PC as the server and recorder is likely to stutter (cf. Ryzen 9 5900X at 30 bots; mcctf-bots lag). 100–200 *server-side* fake players/NPCs mostly idling or doing scripted tasks is more plausible than 100–200 client bots, but not measured — must be benchmarked with `tools/cf_status`-style measurement before any promise.
- INFERRED (EULA): lowest-risk options, in order: (1) extras as server-side NPCs/fake players (no "user" connects); (2) LLM bots in offline mode on a LAN-only/firewalled server that only the licensed owner joins, never public; (3) one purchased account per LLM bot with online-mode (cost per account not researched). Option 2 is the industry norm for testing but Mojang has not explicitly blessed it — record as an OWNER decision via `cf_decision.py`.

### Gaps
- No controlled benchmark of N Mineflayer bots vs TPS on a desktop CPU comparable to ours; CPU model of the CINE PC not in this research.
- No official Mojang statement specifically on offline-mode bots on a private server used to produce monetized videos.
- Price of extra Java accounts not researched (instructed not to create accounts).

## 3. LLM cost per agent-hour and per video (20 / 50 / 200 agents); local models on 12 GB

### Takeaway
Published runs give roughly **$0.9 to ~$25 per agent-hour** depending on model tier and how much code/reasoning the agent produces; the best-documented multi-agent number is ~$9.55/agent-hour (Gemini 4 Argon, standard price). A fully LLM-driven 50-agent, 4-hour shoot would cost roughly $170–$1,900 in API at those rates; 200 fully-LLM agents is $700–$7,600+ per shoot and probably unrunnable on one PC anyway. A local 8–9B model on a 12 GB card can drive *one or a few* agents through simple survival steps, not a 20+ agent society, and competes with Minecraft for the same GPU.

### Cited Findings
- OBSERVED: Gemini 4 Argon team (4 Mineflayer agents) beat Minecraft in 27 h 14 min; "processed about 1.35 billion input tokens, 91% of them served from the context cache, and generated about 16 million output tokens … over roughly 24,000 model calls … about $520 ($1,040 at the standard price). The whole session … came to about $810 ($1,620)." — [arXiv 2610.22319 (2026-10-15)](https://arxiv.org/html/2610.22319).
- OBSERVED: same run re-priced at "$4 per million input tokens, $0.20 per million cached input tokens, and $20 per million output tokens", giving ~$38–59 per hour of the 4-agent session — [PhantomByte, 2026-10-20](https://articles.phantom-byte.com/gemini-4-argon-minecraft-agent-run-cost.html).
- OBSERVED: MineTrials (Sept 2026, single agent, 1-hour runs, 53 runs): cost–performance frontier "from Luna at $0.86 and 14 mean advancements to Astra at $24.53 and 22.4" per one-hour run (list-price estimates) — [MineTrials](https://massiminoe.github.io/minetrials).
- OBSERVED (secondary, from Emergent Garden's "The Chaos of AI Agents", mid-2025): "a few hours of Claude Opus agents ≈ $34; a full day of several parallel Sonnet instances ≈ $20; Gemini nearly free (rate-limited)" — [parkershamblin research notes](https://github.com/parkershamblin/minecraft-ai-agents/blob/main/docs/research/emergent-garden-lessons.md).
- OBSERVED: YC Civ50 (50 GPT-6.1 Sol agents, 3 h, ~5,900 messages) — "token use and compute costs went unmeasured" / cost not in README or post — [AI Miracle, 2026-11-02](https://www.aimiracle.ai/ai-news/ai-agent-swarms-minecraft-study); [poko-everyday, 2026-10-31](https://poko-everyday.com/ai-news-20261031-2-yc-minecraft-agent-swarms).
- OBSERVED: a multi-agent Minecraft paper found per-step tokens grow roughly linearly with agent count when each agent reads the latest N chat entries (5–50 agents) — [arXiv 2503.03505](https://arxiv.org/html/2503.03505v2).
- OBSERVED: Generative Agents (25 agents, 2 game days) cost "thousands of dollars in token credits" — quoted in [parkershamblin research notes](https://github.com/parkershamblin/minecraft-ai-agents/blob/main/docs/research/emergent-garden-lessons.md).
- OBSERVED: market context, 2026-11-06: median API price across 216 models $0.75/M input, $3.00/M output; open-weight median blended price 78% lower than proprietary — [BenchLM](https://benchlm.ai/stats/llm-pricing).
- OBSERVED: Andy-4 (8B, Llama-3.1 base, Mindcraft-tuned) VRAM: Q8_0 12 GB+, Q5_K_M 8 GB+, Q4_K_M 8 GB; Andy-4-micro 1.5B ~2–6 GB — [Mindcraft-CE Andy docs](https://raw.githubusercontent.com/mindcraft-ce/mindcraft-ce/develop/docs/andy.md); Andy-4.2 (9B, Qwen3.5) "run on a single RTX 3090 … at 8-bit", "first local model capable of getting a full set of diamond armour", but "one domain where it does not perform well: Building" (produces thousands of tokens, does nothing) — [HF Andy-4.2](https://huggingface.co/Mindcraft-CE/Andy-4.2).
- OBSERVED: hands-on guide (2026-07-28): local agent models are "capable of steps, not of plans"; Ollama chat-template mismatch silently breaks Andy-4; Mindcraft-CE advises LM Studio over Ollama — [Aillex guide](https://askaillex.com/guides/local-ai-plays-minecraft).
- OBSERVED (local CLAUDE.md): RTX 3060 12 GB — "one heavy job at a time".

### Inferences
- ESTIMATED per-agent-hour reference points: low $0.86 (MineTrials cheapest frontier point), mid $9.55 (= $1,040 / (4 agents × 27.23 h)), high $24.53 (MineTrials top). Token intensity of the Gemini run ≈ 12.4 M input (91% cached) + ~0.15 M output tokens per agent-hour — these are coding agents that write programs; a dialogue-only "villager" agent should use far fewer (INFERRED, not measured).
- ESTIMATED shoot budget, assuming a 30–50 min edit needs ~4 h of simulated play (Sid runs were 20 min–4 h; Civ50 3 h) and one retake (×2 = 8 h):
  - 20 agents × 8 h = 160 agent-h → ~$140 (low) / ~$1,530 (mid) / ~$3,900 (high).
  - 50 agents × 8 h = 400 agent-h → ~$340 / ~$3,800 / ~$9,800.
  - 200 agents × 8 h = 1,600 agent-h → ~$1,400 / ~$15,300 / ~$39,200 (and the server likely cannot host it — §2).
  - Hybrid (8 LLM "lead" agents + scripted extras) × 8 h = 64 agent-h → ~$55 / ~$610 / ~$1,570.
  These are list-price arithmetic, not quotes; actual cost depends on call cadence, caching and model. Any metered run needs owner approval (CLAUDE.md hard rule).
- INFERRED (local 12 GB): Andy-4 Q4/Q5 (8 GB) fits, Andy-4.2 9B at 8-bit does not (needs ~3090-class); a 4-bit 9B likely fits but not verified. One local model serves requests serially, so 20 agents ≈ 20× the per-call latency; and the GPU is also needed by the Minecraft recording client and Flashback/Replay render → run LLM sessions and rendering at different times. Local = viable for 1–5 "lead" agents doing simple tasks, not for building or planning-heavy scenes.
- INFERRED: Claude via the Claude Code subscription is not an API bot backend for 20+ continuously-running agents; the harnesses call provider APIs with API keys (MineTrials notes it used subscriptions for single-agent runs and valued tokens at list price).

### Gaps
- No published tokens/agent-hour for a *dialogue-centric* villager agent (Mindcraft default profile) — must be measured on 1–2 agents for 1 hour before budgeting.
- Current Claude/GPT per-token prices were not verified from provider pricing pages in this pass.
- No measured local-model throughput (tokens/s, concurrent agents) on an RTX 3060.

## 4. Hybrid approach: scripted "director" + LLM only for decisions/dialogue/narration

### Takeaway
Every working system already is hybrid: Mindcraft's competence comes from 47 hand-written parameterized tools plus a non-LLM "modes" layer; PIANO has a fast non-LLM reflex path; practitioners recommend scripts for fast actions and the LLM only for plans. Nobody published a "how much was staged" breakdown for an AI-civilization video; the human-player civ genre (ish, 52M views) itself mixes organic play with admitted interference.

### Cited Findings
- OBSERVED: MineCollab/Mindcraft paper: "Exceptional effort has gone into developing a library of useful actions and queries so that the agent is not handicapped by low-level challenges"; competence is hand-engineered into 47 parameterized tools plus an automatic "modes" layer (reactive behaviours between LLM calls); optional `!newAction` lets the LLM write JS — [parkershamblin research notes summarising the paper](https://github.com/parkershamblin/minecraft-ai-agents/blob/main/docs/research/emergent-garden-lessons.md).
- OBSERVED: "performance drops dramatically from up to 90% down to less than 30% moving between the two- to five-agent settings" (cooking/crafting tasks) — same source quoting MineCollab.
- OBSERVED: PIANO = ~10 concurrent modules incl. "a fast non-LLM reflex path"; specialization emerged from one prompt ingredient ("Here's what other people are doing"); one `community_goal` string can steer a village — same source.
- OBSERVED: Hacker News commenters on YC's study: failures were often the harness, not the model; suggestion to give fast operations to fixed scripts and let the LLM only plan — [poko-everyday summary, 2026-10-31](https://poko-everyday.com/ai-news-20261031-2-yc-minecraft-agent-swarms).
- OBSERVED: Civ50 agents "didn't figure out how to systematically feed themselves" but built "an elaborate bureaucracy with permits, ledgers, and distinct roles"; 22 deaths in the first night, leader = first name in the directory — [YC on X, 2026-10-29](https://x.com/ycombinator/status/2115904914526548472); [poko-everyday](https://poko-everyday.com/ai-news-20261031-2-yc-minecraft-agent-swarms).
- OBSERVED: Emergent Garden on Project Sid: "a paper is not particularly strong evidence. I'd prefer to see long uncut footage of this emerging civilization." — [parkershamblin research notes](https://github.com/parkershamblin/minecraft-ai-agents/blob/main/docs/research/emergent-garden-lessons.md).
- OBSERVED: ish's "1000 Players Simulate Civilization" — viewers debate staging; creator says "almost entirely real with only a few moments of interference" (forum relay, 2024) — [NullForums relay of Reddit post](https://nullforums.net/threads/is-ishs-1-000-players-simulate-civilization-video-scripted-or-organic.67920); his July 2025 video description points viewers to a livestream about "what was real and not" — [YouTube ish](https://www.youtube.com/watch?v=ef568d0CrRY).
- OBSERVED: server-side bot tools offer deterministic behaviours usable as "extras": Carpet `/player` action packs, PuppetPlayers action chains (`/puppet <player> actions chain add …`), FPP A* pathfinding/combat, Baritone `#goto/#mine/#build schematic` — [PuppetPlayers](https://github.com/senseiwells/PuppetPlayers); [FPP](https://modrinth.com/plugin/fake-player-plugin-fpp); [baritonemc.net](https://baritonemc.net/).

### Inferences
- INFERRED architecture for us: (a) 5–10 named LLM characters (Mineflayer/YC harness or Mindcraft) whose *decisions and dialogue* are the story; (b) 20–200 extras as server-side fake players/NPCs running scripted jobs (farm, mine, patrol, build from schematic) assigned by a deterministic "director" process (datapack/mod or Node script) that turns LLM decisions into tasks; (c) builds placed from schematics rather than LLM-built (LLMs fail at building: Sid limitations, Andy-4.2); (d) narration written afterwards from the event log (fits the existing Director Cut → auto-edit pipeline).
- INFERRED honesty rule: if extras/builds are scripted, the title/narration must not claim "200 AIs built this on their own"; describe it as "AI-led simulation" and keep an event log as evidence (aligns with `policy-check` "metadata vs content").

### Gaps
- No creator found who documents a Citizens/Carpet-extras + LLM-leads pipeline for YouTube; no measured share of staging in any AI-civ video.

## 5. Filming: replay tools, many entities, skins/nametags, render time

### Takeaway
Filming is the most mature part: Flashback and Replay Mod both support 26.3 and 1.21.11, keyframed camera paths, nametag/skin overrides, and a server-side recorder (ServerReplay) can record the whole bot world without a client. RTX 3060 render time is not measured; a third-party add-on reports ~14–159 ms per 1080p frame depending on settings.

### Cited Findings
- OBSERVED: Replay Mod 2.6.28 "Update to 26.3" (26.1 in 2.6.26, 26.2 in 2.6.27, 1.21.11 in 2.6.25; 2.6.25 also "Fix nametags of players still being visible with Render Name Tags option disabled on 1.21.9+") — [Replay Mod changelog](https://www.replaymod.com/changelog.txt).
- OBSERVED: Replay Mod builds lagged Mojang releases by 7, 21, 26 and 33 days for 1.21.11, 26.1, 26.2, 26.3; Flashback's 26.3 build came 4 days after release (2026-09-19); ServerReplay (server-side Fabric, records replays for Replay Mod or Flashback) 3.6.0 for 26.3 on 2026-10-30, not for Paper/Spigot; "untick Render Name Tags"; Ctrl+Render = High Performance Rendering; Iris shaders supported — [Space-Node Replay Mod guide](https://space-node.net/blog/replay-mod-guide-minecraft-2026).
- OBSERVED: Flashback changelog: 0.41.1 (2026-06-24) 26.2 + Vulkan; 0.42.0 (2026-07-28) "Hide All Spectators"; 0.43.3 AMD AMF encoder, depth-map/EXR export; earlier: "Include NPCs, Show All and Hide All in the Player List" (0.16.0), "Load Skin from File" (0.17.0), skin/cape/name overrides (0.9.0), Render Filter per entity type (0.18.0) — [Flashback changelog](https://flashback-mod.com/changelog/).
- OBSERVED: FlashbackTurbo (Fabric add-on, 1.21.9–26.3): 1080p 10-s slice (603 frames) — vanilla 159 ms/frame vs Turbo 14 ms/frame; median "~8.5 s (60 fps)" export on Windows NVENC for ~1080p clips; note it sends opt-out telemetry — [Modrinth FlashbackTurbo](https://modrinth.com/project/6o9zaNB9).
- OBSERVED: MultiView merges several Flashback POV recordings into one "omniscient" replay; FlashBatch queues all scenes for export — [Modrinth MultiView](https://modrinth.com/mod/multiview); [Modrinth Flashbatch](https://modrinth.com/mod/flashbatch).
- OBSERVED: Replay Mod keyframe timeline with cubic/linear camera paths and time keyframes — [minecrafthub ReplayMod page](https://minecrafthub.io/mods/replay-mod).
- OBSERVED: Fake Player Plugin supports "custom skins" for bots — [Modrinth FPP](https://modrinth.com/plugin/fake-player-plugin-fpp).

### Inferences
- INFERRED: ServerReplay on a Fabric server records every bot without a spectator client competing for the GPU during the simulation; camera work and rendering happen afterwards → fits "one heavy GPU job at a time". Paper-only stacks (Citizens/FPP) would instead need a recording client (Flashback/Replay Mod) attached, plus MultiView if several viewpoints are needed.
- INFERRED: Original-IP skins can be applied at render time with Flashback skin-from-file overrides, so bots on the server can use generic names/skins; nametags can be hidden or replaced for clean shots.
- ESTIMATED: a 45-min final cut at 30 fps = 81,000 frames → ~19 min at 14 ms/frame to ~3.6 h at 159 ms/frame of pure export, on the add-on author's hardware (not ours); real cost is dominated by searching hours of replay for good moments and setting camera paths (not measured).

### Gaps
- No RTX 3060 render benchmark for Flashback/Replay Mod with 50–200 visible player entities; no data on replay file size / playback FPS with that many entities.

## 6. Known AI-agent Minecraft creators, audience reaction, and YouTube policy (July-2026 inauthentic content; AI disclosure)

### Takeaway
AI-agent Minecraft video is a proven but narrow niche: Emergent Garden (292K subs) peaked at 1.8M views with 4 agents, while the best-known "1000 AIs" video (5.1M) is a commentary on Altera's paper, not original footage; human-player civ videos (ish, MARCUSK) are an order of magnitude bigger. YouTube does not require the "altered/synthetic" label for non-realistic Minecraft footage, but the July 2026 clarification makes templated, repetitive AI series a monetization risk.

### Cited Findings
- OBSERVED: Emergent Garden (292K subscribers): "4 AIs Survive 10 Days in Minecraft" 1.8M views (1:27:36), "AI Plays Minecraft Forever (and dies)" 657K, "AI Builds Stuff in Minecraft | Mindcraft" ~585K, "AI for War (in minecraft)" 64K (2026-03-21) with the note "I'm feeling burned out on mindcraft"; recent non-Minecraft AI videos 361K–741K — [YouTube channel](https://www.youtube.com/channel/UCwBhBDsqiQflTMLy2epbQVw); [AI for War](https://www.youtube.com/watch?v=Ipcr5heLOJ8).
- OBSERVED: related videos: "Scientists Left 1000 AIs Alone in Minecraft. They Created A Civilization." (Species | Documenting AGI) 5.1M; "AI Simulates Civilization in Minecraft" (Wifies) 3.8M (~2 years old); "10 AIs Play Minecraft" (Turing Games, stream) 80K — [YouTube watch-page sidebar](https://www.youtube.com/watch?v=Ipcr5heLOJ8).
- OBSERVED: human-player civ comparators: ish "1000 Players Simulate Civilization: Rich & Poor" 52M views (2:28 long, July 2025), "1000 Players Build MASSIVE Civilization" 46M; MARCUSK "1500 Players Simulate Civilization" 3.7M — [YouTube ish](https://www.youtube.com/watch?v=ef568d0CrRY).
- OBSERVED (local study 2026-11-12): "Mac & Ollie" is effectively "Minecraft X Civilization: The Movie" — a multi-player simulation channel — `/home/claude/cine/docs/niches/minecraft_success_failure_2026-11-12.md`.
- OBSERVED: AI disclosure required only for realistic content ("Makes a real person appear…", "Alters footage of a real event or place", "Generates a realistic scene that didn't actually occur", AI music as main focus); labels for non-photorealistic/animated AI content appear in the expanded description; "Disclosing AI content alone won't limit a video's audience or impact its eligibility to earn money" — [YouTube Help 14328491](https://support.google.com/youtube/answer/14328491).
- OBSERVED (2026-05-27): "Non-realistic content, such as animations or fantastical scenes, also doesn't require a disclosure"; AI scripts/outlines need no disclosure — [TeamYouTube: Updates to AI content disclosure](https://support.google.com/youtube/thread/424874071/updates-to-ai-content-disclosure-and-labels?hl=en).
- OBSERVED: YouTube may auto-label via its systems/C2PA; creators can correct in Studio — [YouTube Help 15447836](https://support.google.com/youtube/answer/15447836?hl=en).
- OBSERVED: July 2025 rename "repetitious" → "inauthentic content" (mass-produced/repetitive; "regardless of how the content was made"; examples: "narrated stories with only superficial differences") — [YouTube monetization policies](https://support.google.com/youtube/answer/1311392?hl=en-EN); [TeamYouTube FAQ](https://support.google.com/youtube/thread/356734251/response-to-creator-questions-about-ypp-policies-july-2025?hl=en).
- OBSERVED: July 16, 2026 clarification splits inauthentic content into (1) generic, repetitive or template-based content (incl. content "easily made with AI, CGI, or templates, with little variation from video to video"), (2) off-putting/distressing content, (3) AI personas discussing sensitive topics; channels with too much of these can't monetize — [TechCrunch, 2026-07-20](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/?eicker.news).

### Inferences
- INFERRED: Minecraft bot footage is non-realistic → the "altered or synthetic" label is not required; the AI angle is usually disclosed in the title anyway ("AIs", "AI agents") — and it is the hook. If TTS narration impersonates nobody, no disclosure duty arises from it either (per the listed triggers).
- INFERRED: The real policy risk is category (1): weekly "N AIs simulate X" episodes with the same template, same narration style and auto-generated edit could be read as template-based. Mitigation = each episode a distinct experiment/question with visible human authorship (chosen rules, commentary, analysis of what the agents did).
- INFERRED: Audience demand appears driven by *personality + honesty about the experiment* (Emergent Garden's on-camera reasoning, failures shown) and by spectacle scale (ish). A faceless AI-civ channel lacks the first; it must compete on story and spectacle.

### Gaps
- No retention/RPM data for AI-agent Minecraft videos; no data on audience reaction specifically to *undisclosed* scripting in AI-civ videos.
- Whether Wifies' 3.8M video used LLM agents or scripted NPCs was not verified.

## 7. Risks: bot instability, griefing loops, compute limits, maintenance across updates

### Takeaway
The dominant risks are operational: Mineflayer desync and version churn (the leading creator burned out on it), coordination collapse as agent count rises, agents failing at survival basics (food, building), and a one-PC compute ceiling. Each Minecraft update costs weeks-to-months of waiting for the bot stack, so the studio must pin a version.

### Cited Findings
- OBSERVED (Emergent Garden, 2026-03): "Mineflayer desync is the deep enemy … it gets out of sync with the game constantly and it causes all kinds of weird race conditioning issues that change in different settings and different versions"; a pathfinder infinite-jump bug regressed on a version bump — [parkershamblin research notes](https://github.com/parkershamblin/minecraft-ai-agents/blob/main/docs/research/emergent-garden-lessons.md); creator: "I'm feeling burned out on mindcraft" — [YouTube AI for War](https://www.youtube.com/watch?v=Ipcr5heLOJ8).
- OBSERVED: in Emergent Garden's war video Gemini agents exploited console commands ("kill-them-with-console-commands") — [parkershamblin research notes](https://github.com/parkershamblin/minecraft-ai-agents/blob/main/docs/research/emergent-garden-lessons.md).
- OBSERVED: Civ50: 34 deaths in 3 h (22 on the first night), chronic food shortage, bureaucratic loops (4 agents spent 11 minutes appointing a fertilizer officer for one bone meal), a harness bug made some Claude agents believe they could not break beds — [poko-everyday](https://poko-everyday.com/ai-news-20261031-2-yc-minecraft-agent-swarms); [The Decoder](https://the-decoder.com/one-brutal-minecraft-night-scared-50-ai-agents-into-inventing-chicken-handoff-protocols-a-fertilizer-officer-and-fishing-shifts).
- OBSERVED: Gemini 4 Argon run: 605 deaths and six restarts of the world server over the session — [arXiv 2610.22319](https://arxiv.org/html/2610.22319); [PhantomByte](https://articles.phantom-byte.com/gemini-4-argon-minecraft-agent-run-cost.html).
- OBSERVED: Project Sid: "The primary challenge lies in agents' lack of vision and spatial reasoning … particularly in spatial navigation and collaborative skills, such as building structures"; 1000+ agents made agents "sporadically unresponsive" — [arXiv 2411.00114](https://arxiv.org/html/2411.00114).
- OBSERVED: Mindcraft code-writing is "sandboxed, but still vulnerable to injection attacks"; YC harness local shell "means commands run as you" — [Mindcraft README](https://github.com/mindcraft-bots/mindcraft); [YC harness](https://github.com/yc-software/minecraft-agent-harness).
- OBSERVED: Mineflayer had no 26.2/26.3 release as of 2026-10-21 (26.2 released by Mojang 2026-06-16) — [discussion #4190](https://github.com/PrismarineJS/mineflayer/discussions/4190); [Space-Node release table](https://space-node.net/blog/replay-mod-guide-minecraft-2026). Fabric's 26.1 announcement: "no mods from 1.21.11 or before will work" on 26.1+ without at least a recompile — [Space-Node](https://space-node.net/blog/replay-mod-guide-minecraft-2026).
- OBSERVED: Carpet fake players crash Polymer-based Fabric servers (missing login-phase context) — [GitHub NonDevBuilds/idlemate](https://github.com/NonDevBuilds/idlemate).

### Inferences
- INFERRED: Freeze the whole stack (MC 1.21.11, Paper or Fabric build, Mineflayer/Mindcraft commit SHAs, Node 20, model version) per season; never follow Mojang updates mid-series. Budget a "smoke scene" after any model or library change (behavioural regression).
- INFERRED: Expect most raw sim hours to be unusable (deaths, loops, stuck pathfinding); the edit is a highlight reel + narrated causality. Safety rails needed: no op/console permissions for agents, chat/command allow-list, watchdog to restart stuck bots, per-run token budget cap.
- INFERRED: Effort is the binding constraint, not money: building a director/glue layer, tuning prompts, babysitting runs and finding story in logs is multi-week engineering before episode 1 (consistent with a solo creator burning out). This competes with the owner's current PROPOSED niche (survival-horror films, local doc §6), which needs none of this stack.

### Gaps
- No public post-mortem quantifying hours of human supervision per hour of usable AI-civ footage.
- Griefing-loop frequency for Mindcraft-style agents (e.g., tearing down each other's builds) not quantified in any source found.
