# BigSchool "Season 3 All Episode - Minecraft Animation" — frame study 2026-11-02

Source: https://www.youtube.com/watch?v=X09yxFuKLAs, viewed (streamed, muted) in the owner's browser pane.
Nothing was downloaded. ~16 frames sampled across 0:15–1:06:40, plus 3 consecutive frames at 0.25× speed.
Audio was NOT listened to: no sound/voice claims below.

## Public metadata (OBSERVED, player response)
- Published 2020-08-18. Length 4,173 s (1:09:33). 135.96M views. Category Film & Animation. isFamilySafe=true.
- Streams: 1080p max, **30 fps** at every quality.
- Captions: English auto-generated (ASR) only; the timedtext fetch returned empty.
- Description chapters: Baby Zombie was Homeless 0:00:01 · Funny Zombie Family 0:10:48 · Poor Skeleton Girl 0:21:48 ·
  Fight Diamond Bandits 0:32:58. A pinned comment adds Rescue Baby Zo… 0:46:03.
  → about 11-minute episodes stitched into a 70-minute compilation.
- Music credits in the description, all free:
  - Audionautix: Hero In Peril, Night Runner
  - Kevin MacLeod / incompetech, CC-BY 3.0: Merry Go, Fluffing a Duck, Amazing Plan, Sneaky Snitch, Scheming Weasel, Investigations, The Builder
  - freesound.org (SFX)
- Comments are nostalgic and from kids; several state ages of 5–12 or "as a kid". Comments come in English, Portuguese, Spanish and Arabic.

## What the frames show (OBSERVED)
- **Sets:** large vanilla-texture Minecraft builds: a town with roads, crosswalks and lamp posts, a school, wooden houses, brick rooms, snow areas. They look like real Minecraft worlds imported as scenery.
- **Characters:**
  - Rigged Minecraft-proportion models: Herobrine/Steve, a baby zombie (custom outfit), a skeleton, a wither skeleton, a zombie pigman, a chicken, plus custom human skins.
  - Limbs **bend smoothly at elbows and knees** (Herobrine's knee bend, the zombie's sitting pose).
  - Baby characters get big cartoon "googly" eyes added on the face. The eyes change shape for emotion: tears at 16:50, wide eyes on the bench at 1:02.
- **Props:** custom non-voxel props (a round red football, golden bananas, a book on a lectern), plus items rendered as extruded sprites.
- **Look:**
  - Soft daylight, mild ambient occlusion, light depth of field on close-ups.
  - No motion blur, no stylised grading.
  - "BigSchool" text watermark at top right.
- **Shots:** mostly mid and close shots on characters with a slow-moving camera; emotional beats are held on faces.
- **Third-party IP in the video:**
  - a clown character resembling a famous horror-film clown (16:50)
  - Coca-Cola cans and logo (1:06:40)
  - We must not copy either.

## How it is made (INFERRED — not confirmed by the creator)
- **Most likely Mine-imator**, or a similar Minecraft-native animation tool, rather than in-game capture. Evidence:
  - smooth-bending limbs
  - imported vanilla worlds
  - flat-soft render
  - 30 fps output
  - overlay cartoon eyes
- Blender + a Minecraft rig is possible but less likely for this 2020 look. Confidence: medium. Unverified, because no credits name the software.
- **Not gameplay:** no HUD, no first-person view, and characters pose in ways the game cannot.
- **Story engine:**
  - poor/homeless baby mob plus a protector (Herobrine)
  - emotion first (crying, rescue)
  - wordless or near-wordless acting, so it works across languages; this matches the multilingual comments
- **Business:** made-for-kids audience → huge views but low RPM (our earlier estimate: kids ≈ $0.33).
- Compilations re-use existing episodes into 1-hour videos, which keeps the channel alive for 6 years.

## Implications for CineFactory (INFERRED)
- The BigSchool route can be done **without buying Minecraft Java**:
  - Mine-imator bundles its assets, and Mine-imator 2.0.2 is already installed on the owner PC.
  - Blender + MCprep needs a legal copy of the game for the textures.
- Our SAVEWALKER ARG lane is 13+ and not made for kids, the opposite audience. A BigSchool-style kids lane would be a separate, lower-RPM channel.
- Copy only structures, never characters:
  - poor → rescued
  - transformation
  - wordless emotional acting
  - compilations
  - free CC-BY music with full credits
- docs/MINECRAFT_MAIZEN_BIGSCHOOL_COMPLETE_COMPANY_MASTER_V223 says "BIGSCHOOL-STYLE = Blender". This frame study suggests Mine-imator for the 2020 seasons. Treat the tool as **unverified** either way.

## Addendum — subtitles and channel scan via Agent-Reach 1.6.1 (OBSERVED, 2026-11-02 23:4x)
Agent-Reach installed in `%USERPROFILE%\.agent-reach-venv` on the owner PC (uv, pypi.org only; no `--system`, no logins,
no cookies, no Groq/OpenAI key). Used `youtube read|search|subtitle` (yt-dlp backend, text only, no media download).
- Auto-subtitles S3 (69.5 min): 401 sound tags, of which music 292, laughter 22, bell 19, snorts 15, screaming 15,
  crying 4, cheering 5. Only **363 spoken words ≈ 5.2 words/min**, all interjections ("Huh?", "Hey", "Wow",
  "Help me", "Thank you", "Oh my god"). → confirms near-wordless acting; music almost wall-to-wall.
- 6 more BigSchool videos read (2020-08 → 2022-05): no software named in any description; every description credits
  Kevin MacLeod / Twin Musicom / Audionautix music and individual freesound.org SFX authors (cartoon eye blink,
  cute laugh, siren whistle). Episodes are 10–14 min; compilations 32 min to 3 h 08 min ("Season 9", 58.6M views).
  Top single: "BABY ZOMBIE Lv.1 - Lv.300" 37.7M (2022-04-01, 12:05).
- Software stays NOT VERIFIED (INFERRED Mine-imator, medium confidence).
- Agent-Reach limits: no frames/visual watching (that still needs the browser pane); `transcribe` needs a
  Groq/OpenAI key (not configured, owner rule: no metered APIs). yt-dlp access to YouTube is outside the official
  API; for repeatable research keep using `tools/cf_youtube_niche_survey.py` (Data API).

## Addendum 2 — full-length storyboard pass + 1080p frame inspection (OBSERVED, 2026-11-02 23:5x)
Method (no download): YouTube's own seek-preview storyboards (level 3: 320×180, one frame / 10 s, 47 sheets × 9 =
419 frames for S3). Viewed 17 sheets = 153 frames, every ~30 s across all 5 episodes, plus 4 frames drawn from the
paused 1080p player onto an on-page canvas to inspect detail (16:58, 0:20, 19:01, 19:06), plus 2 sheets of
"BABY ZOMBIE Lv.1 - Lv.300" (2022).
- Rendering evidence (all seen):
  - cast soft shadows on grass (wither skeleton at night, 19:06) — vanilla Minecraft has no such shadows
  - point light from campfire lighting characters at night (sheet M12)
  - depth of field with blurred background on close-ups (19:01)
  - ambient-occlusion dark corners (16:58)
  - emissive glowing eyes (Herobrine)
  - no HUD, no first-person view, no name tags, no motion blur
- Rig evidence:
  - one-piece limbs that bend in the middle with a continuous texture (elbows, knees, sitting and crouching poses)
  - removable cartoon eyes that pop on and off any mob as a gag (enderman, slime, creeper, baby zombie)
  - tears
- Props: non-voxel models (cylinder basket, round football, white car, TV with an animated screen texture,
  Plinko board, image planes such as "wanted posters").
- Post-production signatures:
  - full-frame TV-static noise used as a scene transition (S3 and the 2022 video)
  - speech-bubble tag "Baby Zombie"
  - chalkboard titles ("Bottle Throw")
  - floating yellow "Lvl.30" labels and a "94%" progress bar (2022)
  - "BigSchool" watermark top right
- Third-party IP spotted (do not copy):
  - a horror-film clown look-alike
  - a horror-game marionette look-alike
  - a Superman logo shirt
  - Coca-Cola cans and logo
  - SCP-096 in the Season 4 title
- Pipeline unchanged from 2020 to 2022 (same rigs, lighting, transitions).

### Conclusion (INFERRED, confidence medium-high for the category, medium for the exact tool)
- **Category:** keyframed 3D animation in a Minecraft-native animator, not gameplay capture, not a mod.
- **Pipeline:**
  - **Scene:** worlds/schematics built in Minecraft and imported as scenery.
  - **Animation:** bendable Minecraft rigs with add-on cartoon eyes, keyframed per shot at 30 fps. Shadows, a point light, DOF and AO are rendered by the animator.
  - **Edit:** a video editor adds static transitions, text bubbles and labels, plus CC-BY music (Kevin MacLeod, Twin Musicom, Audionautix) and freesound.org SFX credited by author.
  - **Distribution:** about 11-minute episodes, then 30 min–3 h season compilations.
- **Tool:** Mine-imator is the best match (free, bundled assets, bend rigs, sun shadows, point lights, DOF, 30 fps default workflows).
- Blender + a Minecraft rig would also fit visually, so the exact tool stays NOT VERIFIED.
- Next confirmation step: render the same shot types in the owner's Mine-imator 2.0.2 and compare side by side.
