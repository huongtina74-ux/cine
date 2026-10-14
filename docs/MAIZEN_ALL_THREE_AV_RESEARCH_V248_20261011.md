# CineFactory v248 — Complete browser timeline + original audio ASR study for two remaining Maizen references

Date: 2026-10-11. Source research cases required by `config/niches/minecraft/maizen_full_video_policy_v227.json`:
1. `ZmT0ITUGUII`, *Mikey and JJ Choose the Right Hole in Minecraft*, 28:04 — previously captured/ASR under v237/v242.
2. `zhPBXzHsLuo`, *Built a House inside BED in Minecraft*, native video duration **1116.601s (18:36.6)** — **new independent Chrome study**.
3. `oX6Azwe5QLg`, *Minecraft, But Item Drops Are Multiplied Every Time!!*, native video duration **1030.741s (17:10.7)** — **new independent Chrome study**.

## Source acquisition / meaning of "watched and heard"

Using the authorized Windows Desktop Commander connection to CineFactory, Chrome via Playwright opened **each ORIGINAL YouTube video** (not a transcript or third-party AI generated walkthrough), played every source timeline interval from start to end in consecutive 38-second overlapping pieces and used the browser's real `HTMLMediaElement.captureStream()` sound track plus `MediaRecorder` Opus, without direct YouTube stream downloads or paid provider credits.

- **House inside BED:** 30/30 browser segments, 30/30 recorded original audio segments and 30/30 local `openai/whisper-tiny.en` (CPU) transcription segments, 142 source frame snapshots from sampled real browser playback, about 2,977 imperfect English words recognized.
- **Item Drops:** 28/28 browser segments, 28/28 recorded original audio segments and 28/28 local Whisper transcription segments, 128 browser source frame snapshots, about 3,004 imperfect English words recognized.
- Source IDs and source durations verified from the actual browser media/player metadata. All retry failures were explicitly recorded and repaired; the final AV timeline checks found no uncovered seam intervals. Independent additional 0–5s original audio recordings were made for **both** videos to cover Chrome startup pre-roll offsets.
- Original audio, screenshots, timecode receipts and raw ASR transcripts are kept privately in machine-local, Git-ignored `.tools/maizen_two_full_av_v244/{video_id}/`; *source audio/video not redistributed or committed*. Screenshots are sampled ~8s apart **not all video frames**.
- Native audio was captured and automatically recognized, NOT independently heard/verified word-for-word by a separate reviewer. **Whisper tiny often makes transcription errors, repeats or hallucinates phrases in music or noise**. Precise music/SFX identity, source licenses, audio levels and lip sync still require separate full audio QC. **Strict independent G02 v227 remains BLOCKED 0/3** and technical backend method promotion G03–G28 is BLOCKED. Browser playback evidence is not identical to a signed source-file SHA/whole native AV decode workflow.

## Source 2 — Built a House inside BED (18:37)

Grounded in original screenshots at 0–18:36 and locally captured English speech, **paraphrased only**.

| Episode clock | Verified story action/visual continuity | Speech/narrative purpose and lessons |
|---|---|---|
| 00:00–01:10 | JJ/Mikey-like avatars stand outside tall wooden house; shrink device activates; characters become tiny; follow to an improvised small hole at exterior wall | Opens with a consequence (their mean friend Buu stole their savings), explicit plan to prank/freeload unnoticed, rapid visual payoff of tiny-body premise |
| 01:10–03:10 | Tiny POV explores the full-size bedroom, giant beds/windows/shelves; characters slip into enlarged red internal bed-space | Clear scale change with stable first-person HUD, custom-sized sets, both external and inside-bed establishing shots |
| 03:10–05:50 | Take furniture/items from rest of house; arrange living room, bathroom and enclosed secret structure inside bed | Serialized construction, object reuse and actor-to-actor task division instead of static tutorial |
| 05:50–07:50 | Complete kitchen/counter/fridge/dining set; visit outdoor farm; transfer crops into a small irrigated indoor garden | A new resource need (food) justifies leaving/returning to secret base; reveals spatially connected locations |
| 07:50–11:25 | Install ice/cooling fans, arrow/security machines, green-cased reflector and observation window within bed | **Set up future payoffs:** dialogue explicitly predicts fire and projectile/explosive attacks; multiple defenses have intended functions |
| 11:25–14:05 | Black NIGHT title card; homeowner returns, enters bedroom, mentions hidden diamonds behind bookshelves; tiny intruders navigate bookshelf passage and recover large diamond stash | New discovery tied back to original stolen savings, turning frivolous "freeloading" into earned recovery objective |
| 14:05–15:50 | Owner notices unusual activity/bed-window, places lava/fire near/into bed, defense starts, visuals show heating/thermometer overlays | Threat anticipated earlier is now actually triggered; SFX/music specific identification not yet independently completed |
| 15:50–18:23 | Ice and fans cool the red bed interior; arrow defense fires toward owner; owner appears with rocket launcher; large blast around living room/roof and reflector operation; tiny protagonists survive in fortified base | Three-layer escalation makes early construction meaningful. Exact 3D model/mod/physics pipeline for missile/reflector unproven |
| 18:23–18:36.6 | Separate green 2D Maizen end-card, channel handles/next-video box | Outro is editorial artwork, a distinct production subsystem from voxel sets |

**Important verified inference:** This *specific episode* has intentional visual stage/scale planning and planted-defenses-then-payoff. A 3D shrink visual alone does not prove any named mod, Mine-imator, Blender, replay tool or source code. Script/characters/trademarks of Maizen and Buu cannot be lifted for original CineFactory production.

## Source 3 — Minecraft, But Item Drops Are Multiplied Every Time!! (17:11)

| Episode clock | Verified story action/visual continuity | Speech/narrative purpose and lessons |
|---|---|---|
| 00:00–02:00 | In a desert-village farm two actors introduce green item multiplier; one wheat/block gives many drops; actual hotbar and inventory fill; craft bread, multiply sand and other basic resources | High-concept mechanic demonstrated in seconds with visible measurable proof, not long exposition |
| 02:00–05:00 | Find desert pyramid, descend to pressure-plate/TNT basement, recover valuable TNT and loot chests, craft gold and iron; use extra resources for hazards | The traditional trap becomes *profitable resource* because it is a block; player logic is explained verbally and visibly |
| 05:00–07:45 | Zombie fight/raid stone rooms, TNT/obsidian protection and lava/cave layers, exploration for diamond ore | Abundance accelerates exploration but does not remove environmental risk |
| 07:45–10:00 | Diamond ore yields multiple dropped diamond items, crafting GUI visibly fills; gear and armor are made and improved | Viewer sees progress by real changes in inventory and equipment, not only dialogue |
| 10:00–12:45 | Portal to Nether; blaze rod/Enderman/ender pearl objectives, diamond armor, dangerous terrain | Important asymmetry: mechanism seems to target **block drops**; some non-block drops are not multiplied automatically; ordinary quest progression still necessary |
| 12:45–14:30 | Enter the End, Ender Dragon health bar appears, summon/build multiple Iron Golems to challenge dragon in arena | Earlier iron abundance becomes a tactical resource during late boss fight |
| 14:30–16:20 | Build obsidian bed/land zone and multiple TNT explosives near dragon landing spot, repeat bombing after defenses suffer | Multiple attempts and tactical improvement extend last conflict rather than an instant overpowered victory |
| 16:20–17:10.7 | Ender Dragon defeated, dragon egg appears then seems to vanish when acted on; final summary graphic about special duplicator and branded 2D end-card | Boss gives explicit end-goal payoff, not a vague extension of farming; egg outcome needs native sound/logic confirmation |

**Important verified inference:** A single simple rule ("many drops") serves as the engine for ~17min because it changes resource flows all the way to the Ender Dragon. The text/VO explains expected gains and limitations. This does not prove the exact item-mod/datapack/game version/plugin; later shots may include staging/editing effects.

## Comparison across the three actually viewed Maizen videos

| Variable | Choice pipes (v242) | Secret bed (v248) | Multiplier (v248) |
|---|---|---|---|
| First 30s | One right / one wrong challenge | Revenge + shrink in visible world | Multiplier on wheat yields piles immediately |
| Central curiosity | Which path hides reward or trap? | Can tiny intruders build and defend a home inside another's bed? | How far can exponentially large block resources carry a survival run? |
| Escalation | ~6 small reversals then final 10-minute base defense | Access/rooms -> farm -> preinstalled defenses -> invasion and counterfire | Farm -> TNT/pyramid -> cave diamonds -> Nether -> End dragon |
| Speech | Contrast choices, reactions and false predictions | Collaborative tutorial, early defense forecast and dramatic alarm when payoff arrives | Demonstrates rule and game resource tradeoffs, narrates survival goals |
| Camera/world | HUD POV + third-person intro, repeated adjacent challenge stages | Extreme tiny/giant scale and edited transition between outer house and inner bed | HUD, inventory/crafting, survival and boss bar across successive worlds |
| Last payoff | Boss is stopped by previously shown defense mechanics | Fire/cooling + arrow/rocket reflector foreshadowed earlier | Dragon finally defeated using extra resources |

**The reusable foundation is NOT "seven choice rounds always."** There are at least THREE distinct narrative architectures, each developed under a common studio language: legible hook, two contrasting characters with original voices, purpose-built/controlled voxel environments, camera coverage for causality, bold colored subtitles, visible item/state change, extended escalating payoff, original licensed sounds and consistent 2D outro.

**Do not conclude** all Maizen output uses Minecraft Java runtime, Forge, Fabric, Mine-imator, Blender, Minecraft NPC bots, external keyframe CGI, ReplayMod or particular add-on based on frames alone. Those are candidate production approaches that CineFactory Technical Director can later benchmark on an **original** scene once G02 quality/source rights are approved.

## CineFactory handoff

1. Research/Evidence: Browser-first real source captures and local ASR can be integrated as repeatable research tools for *other competitors*, with private media retention, retry, same-source ID checks, first-second audio patch, per-30s original visual+sound notes, independent reviewer and source rights. **This v248 observation is provisional, NOT a v227 G02 override.**
2. Creative Strategy & Script Room: Choose among choice-loop-with-finale, stealth-base-revenge, escalating-economy survival, **not one compulsory Maizen recipe**. Write new original situation/characters/assets. Every introduced item must pay off in later conflict.
3. Production Design & Assets: Build original modular voxel worlds, persistent scene graph and actor/prop inventory. Document smallest-to-giant-world scale, house/interior spatial continuity and original effect rigs. Keep character identity stable.
4. Character, Cinematography, Technical Director: Define actor blocking/eyelines and 1st/3rd-person camera transitions per story beat; compare staged licensed game world and Blender-authored CG with first-party quality pilots after gated research. Prove via video, not test counts.
5. Audio & Editorial: Two clear original English speakers and dialogue ahead of important actions, visible caption timing and Foley/music aligned to cinematic rhythm; include future SFX/music/commercial license audit before publish.
6. QC, Rights & Release: Independent observer verifies **all 3 original source films** every <=30s picture/native audio window (v227 expects 130 windows), then independent *actual* pilot full video+audio, art, actor, source/asset rights, no source character likeness and human director release. Existing v243 MAI01 original Waterfall 21-beat desk prepro still DRAFT; no Minecraft game or CGI source method was approved by v248.

Files:
- Grounded structured summary: `config/niches/minecraft/maizen_three_reference_av_study_v248.json`.
- Live audit: `cinefactory/studio/maizen_three_source_study_v248.py`.
- Machine-only original source research evidence: `.tools/maizen_two_full_av_v244/` (browser screenshot contact sheets and audio/ASR, private and Git-ignored).
- Third party videos/audio are NOT copied to repo.
