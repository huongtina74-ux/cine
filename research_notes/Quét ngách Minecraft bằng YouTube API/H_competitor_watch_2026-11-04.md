# Competitor watch – survival lane (2026-11-04, owner request after trial ep03)

Viewing method: YouTube in the built-in browser on the owner's PC, no download. Picture sampled from continuous playback. **Audio not heard** (muted; transcript read instead).
Coverage labels per CLAUDE.md research policy. None of these reaches the v228 "complete" bar (no source SHA, no heard audio, no second reviewer). Read conclusions as OBSERVED picture + transcript only.

| Video | Format seen | Coverage |
|---|---|---|
| [Day Zero – I Survived 100 Days in a REALISTIC APOCALYPSE in Minecraft](https://www.youtube.com/watch?v=crnpqkov3ps) 52:00, 1.9M | **Minecraft Java, modded, first-person gameplay + creator's own live voice** | Played 0:00→52:00 at 3–6×, ~60 frames sampled; full transcript (414 segments); description read |
| [Nobody Gets In – Zombie Outbreak: 30 Days Locked Inside a Supermarket](https://www.youtube.com/watch?v=oXj7bWgRX_I) 10:41, 3.3M | **2D stick figure, illustrated backgrounds, narrated in 2nd person** | ~12 frames; full transcript (82 segments); chapters |
| [Kit vs The End – Zombie Outbreak: 100 Days Trapped On A Zombie Cruise Ship (Full Movie)](https://www.youtube.com/watch?v=xdj5PL0t61k) 73:02, 0.7M | **2D stick figure, detailed illustrated scenes** | PARTIAL: ~8 frames, transcript did not load |

## Correction to earlier research (S7)
The two "Zombie Outbreak + day counter" leaders (Nobody Gets In, Kit vs The End) are **not Minecraft**. They are 2D stick-figure narrated stories that surfaced in our Minecraft keyword scans. Only Day Zero is Minecraft.
- The S7 formula still stands: zombie outbreak, a sealed place, a day counter, "One sound and they find you".
- What sells in those two is **script + narration**, not 3D detail.

## Day Zero: how the Minecraft look is made (OBSERVED from the creator's description and frames)
- **Map:** "Beautiful map by heyitskad (customized and detailed by me)", downloaded from PlanetMinecraft and credited.
  - The streets, signals, power lines, a mall, a church, a gas station and furnished interiors (kitchens, warehouse racks, crates) all come from the map, not built per video.
- **Mods listed by the creator:**
  - The Hordes (zombie hordes)
  - TaCZ (guns)
  - Immersive Vehicles/MTS (cars with interiors, helicopters)
  - Legendary Survival Overhaul (thirst, injuries)
  - Ready-made alternative he suggests: the "Cursed Walking" pack.
- **Shaders (INFERRED, not named):** soft sun shadows, volumetric sky, aurora/night sky, depth-of-field blur, bloom on lamps.
- **Voice:** the creator's own live reactions ("No, no, no", "Let's go"). Not TTS. He says the "planned events" are staged, but the gameplay is real.
- **Structure:**
  - 35 s cold open: place, goal "escape this town", rules of realism (injury, bleeding, smell tracking, hordes).
  - Then a chain of goals: shelter → weapon → food/water → infection → vaccine → fuel.
  - Night as the threat beat.
  - Ends at 50:50 by driving out.
- **Blocking:** zombies and player obey game collision. Nothing passes through anything, because the game engine handles it.

## Nobody Gets In: why a simple 2D video gets 3.3M (OBSERVED from the transcript)
- **Hook:** "Automatic doors open for anything... They do not check for a pulse."
- **Voice:** second-person "you".
- **Structure:** a "First problem / Second problem / Third problem / Fourth problem" spine.
- **Recurring motif:** "New store policy: Nobody gets in", amended as the story turns.
- **Concrete numbers** everywhere: 9,000 cans, 40 seconds, 300 heads, a ton per pallet.
- **Story turns:**
  - Twist: the zombies "don't hunt, they repeat".
  - The living humans become the fourth problem.
  - The ending is emotional: Dana keeps starting her shift. "Alone, you would not have seen day 23."
- **Picture:** one word of on-screen text at a time, flat illustrated store sets, a stick figure.

## What this means for Bin Bo Zu (INFERRED; the owner decides)
1. **Detail of picture:** use Minecraft Java with
   - (a) a detailed, credited map, or our own set built by datapack;
   - (b) shaders (Iris + Complementary or BSL; needs owner approval to download);
   - (c) furniture/vehicle mods only if the look needs them.

   Our code engine cannot match that level of world detail at a sensible cost.
2. **Collision:** in the game, physics handles it. In the code engine we must add a minimum-distance check, and QC must fail any overlap.
3. **Voice:** the leaders use either a real human voice (Day Zero) or a strong narrator (the 2D channels).
   - Local Kokoro (already installed) is the free upgrade to test next.
   - Owner voice or ElevenLabs need the owner's choice.
4. **Script:** adopt the narrated-survival script DNA as a formula, not text: problem spine, policy motif, numbers, twist, emotional close. Our trial script had the hook but no "problems" spine and no numbers.
