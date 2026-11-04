# Parrot "10,000 Player Minecraft War": scale of the first 8 minutes (2026-11-05, owner request)

Source: https://www.youtube.com/watch?v=bHxLy6Qza3M (4:00:00).
Viewing:
- Built-in browser on the owner's PC, muted, no download. **Audio not heard.**
- 27 frames sampled 0:02–8:00, at about every 10 s in the cold open and every 15–25 s after it.
- The owner also sent 5 frames of his own (snow arena crowd, skyscraper city, desert walled city, night plaza, 1:20 plaza).
- Contact sheet: `J_parrot_first8min_sheet.jpg`. Frames are grouped by time range; their order inside a range is not exact.
- Coverage: PARTIAL. This does not meet the v228 "complete" bar.

## What is on screen (OBSERVED)
- **0:00–0:55, cold open:** no HUD, cinematic camera. About 6 different hero locations in under a minute:
  - a white marble throne hall with a crowd of a few hundred players;
  - a Nether fortress-cathedral with lava falls;
  - a giant winged statue about 60+ blocks tall;
  - a Nether plain covered by a crowd of thousands, with the villain on a wall;
  - a portal room full of armoured players;
  - a sky town with a lighthouse tower and hot-air balloons.
- **1:00–2:30:**
  - First-person survival play with a full HUD and **vanilla lighting, no shader**.
  - A futuristic city of about 60 white skyscrapers in a jungle basin, with lagoons and islands. Next to it, terraced red mesas.
  - Plus night shots: a palace plaza with thousands of armoured players standing in formation.
- **3:00–8:00:**
  - The POV rides a blimp, whose design is credited in the description to another creator's tutorial.
  - **View distance reaches the horizon:** oceans, coastlines, several walled kingdoms, a red Nether sky dome over one region, a 40-block-high orange border wall. That is far beyond vanilla's 32-chunk limit, so (INFERRED) a level-of-detail mod such as Distant Horizons, or a pre-rendered flyover.
  - Aurora at night (INFERRED: shader or custom sky only in the cinematic shots).
- **Owner's frames:**
  - snow castle arena packed with players;
  - desert walled city of about 150 houses beside layered mesa cliffs;
  - skyscraper city with atmospheric haze.

  The haze and soft fog in his frames (INFERRED) come from shaders plus far-distance LOD in the cinematic shots.

## What the scale is made of (INFERRED from the frames, not confirmed by the creator)
1. **The world:**
   - One continent-size map with many kingdoms, built and terraformed by a build team over months.
   - Much of the backdrop is ordinary Minecraft terrain (forests, rivers, oceans, mesas). Only the hero areas are hand-built.
2. **The crowds:** real players (thousands of name tags), not NPCs. This is the one part we cannot copy with entities in a single client.
3. **Two looks:**
   - cinematic shots: no HUD, shader-like light and haze, far LOD;
   - plain vanilla first-person gameplay.
4. **Credits:**
   - The description credits original music, the blimp design, and 8 creators who appear.
   - There is no builder credit and no shader or mod list.

## What this means for Bin Bo Zu (INFERRED; the owner decides)
- **Do not try to match the continent.** Match the *shot list*: 6–10 hero locations, each dressed only where the camera looks, plus real terrain around them.
- **Real terrain for free:**
  - Move the city out of the superflat world into a normal-terrain world (vanilla worldgen: mountains, rivers, snow).
  - Flatten only the plot.
- **Mass production of buildings:**
  - Make 20–30 detailed modules once (houses, towers, skyscrapers).
  - Save them with vanilla structure blocks.
  - Place them hundreds of times with `/place template` and rotation.
- **Crowds:**
  - In game: up to about 1–2k mannequins per shot. Needs a measured performance check (not measured yet).
  - For "10,000" wide shots: render the same world in Blender with instanced crowd figures (our own skins), which also gives fog and DOF.
- **Look:**
  - Iris + Complementary for cinematic shots.
  - Distant Horizons for the horizon.

  Both are free mods, but each download needs owner approval.

## Correction: are the crowds real players? (2026-11-05, owner question)
OBSERVED: the name tags in the owner's frame of the night plaza army fall into two kinds.
- **Combinator patterns:** "xX_Hunter_Xx", "xX_Knight_Xx", "LuckyHunter", "LuckySniper", "LuckyGhost", "Cyber_Viper", "CyberBlade", "CyberReaper", "Epic_Viper", "EpicReaper1993", "Iron_Raven", "IronGhost91", "TheMiner3", "TheRider2013", "TheWolf7", "SwiftWolf", "GhostMiner2000", "Neon_Bear".
- **Pronounceable nonsense:** "Plastclaertung", "Shexmaichpack", "Measwiextrax", "Skoulglish".

The soldiers wear identical armour and shields and stand in exact rows.

INFERRED: a large share of the "10,000 players" in the army shots are generated NPC or bot players, not fans. Our earlier notes said "thousands of real fan players". That is now unproven: real fans may be present at some moments, but the formation armies are most likely NPCs.

What is real:
- the game (Minecraft Java on a multiplayer server; first-person HUD with hearts, hunger and hotbar, item tooltips);
- the creators who play;
- the PvP.

What is staged:
- the story (the description: "a staged Minecraft server where ... tell stories");
- the cinematic shots.

For us: NPC armies are the same trick as our mannequins. A title must not claim "players" for NPCs (policy-check: misleading metadata).
