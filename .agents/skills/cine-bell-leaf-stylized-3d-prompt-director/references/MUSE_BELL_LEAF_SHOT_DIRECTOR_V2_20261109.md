# Bell & Leaf: Muse × HaoHao cinematic shot director v2.0

Date: 2026-11-09. Durable companion to MUSE_HAOHAO_OPERATING_STANDARD_20261109.md in the SAME existing CINE skill. It does not supersede the story, character, location, or voice Canon. Read both documents for every Muse/HaoHao shot prompt. Scope: Slow English A2, Bell & Leaf only.

## 1. Screenwriter-first production contract

The screenplay, story timeline and asset IDs are the source of truth, never a memorized chat or an arbitrary example prompt. Before writing, resolve the locked episode revision, adjacent shot continuity, intended narrative action, character motivations, on-screen actors, primary speaker, emotion, exact A2 text, source character references, costume, location and verified camera viewpoint. No scene or dialogue rewrite without screenplay approval.

Every shot is EXACTLY 10.0 seconds, 16:9, 24fps, one continuous take, original premium cinematic stylized 3D animated family fantasy. The user's upscale-steakhouse example supplies useful production vocabulary (materials, actor expression, camera motivation, environment and SFX) but is a multi-scene montage and MUST NOT be transplanted into Bell & Leaf Canon or crammed into one 10-second shot. Split any multi-location or multi-cut sequence at screenplay level into separate ten-second shots.

The first 15 seconds must establish a genuine Canon hook: S001 and first half of S002, without changing shot durations or making characters appear at historical events where they do not belong. No time-travel edits, unapproved extra actors or causal discontinuities.

## 2. Mandatory @character AND @location

Use the exact registered HaoHao actor tags for visible cast, e.g. @Juno @BIX, AND the exact registered location tag from the same shot's approved source location, e.g. EXACT SOURCE LOCATION @BellKitchen_Day. A tag is not a model-level identity lock: HaoHao's attachment resolver finds registered names and attaches the matching images; some tags may be stripped before text reaches Muse. Verify the attachment list and reference SHAs before queueing.

Mandatory in both first-frame and video prompt: shot revision + ID; ACTIVE TAGS FOR THIS SHOT: [juno,bix] (or [] when nobody visible); @actor tags; @registered_location; site/time-of-day/view/orientation; selected approved outfit; acting/camera/lighting. Do NOT invent registered names such as @WizardCastle when the actual Tư liệu contains only BellKitchen_Day. If location has no registered approved source plate or view, mark HOLD_LOCATION and do not generate an alternative location by text alone.

Set continuity is as critical as face continuity. Describe only OWNER-VERIFIED architecture: direction of daylight, table, doors, windows, counter, furniture, props, exits and walk paths. If the source provides a front view only, do not pretend a reverse-angle plate exists; use a camera angle defensibly grounded by the available source or HOLD and collect the missing owner reference.

Source order: approved original face anchor → source-verified body/angle/outfit → owner location plate → approved single 16:9 first-frame → textual acting prompt. The multi-panel 1122×1402 character sheets stored in HaoHao must not be interpreted as a single ready-to-animate face image. Crop one source-verifiable hero, inspect identity and provenance, and do not fabricate a face/age/outfit variant. All images should remain private in the owner environment.

Actor guardrails: Juno youthful boy, 13; Lia young girl, 11; Mara warm adult mother; Evan supportive father; Orin elder wizard. BUBU keeps purple cat body, gold collar bell and sparkling spiral tail. BIX remains a compact teal/gold mechanical turtle-pangolin robot without a bell. Never add Evan to the image merely because Juno says "Dad"; dialogue mentions are not visible-cast directives.

## 3. Reusable premium animation style, without false promises

Series baseline for every shot:

    Original premium cinematic stylized 3D family-fantasy animation, high-end animated feature-film craftsmanship, expressive original character faces matching approved owner references, realistic-in-animation material textures where relevant, polished composition, readable eye and hand acting, physically grounded contact shadows, tasteful subtle depth of field, motivated smooth camera movement, consistent character silhouette and hairstyle, refined original production design, stable lighting, no live-action or photorealistic faces.

Add shot-appropriate texture vocabulary only when the story needs it: crusty bread, ceramic glaze, soft steam from a cup, copper cookware, bell glints, magic dust motes. Dynamic fire/flames, frantic action or restaurant props from the user's unrelated example are NOT defaults. D55 (~5500K) for approved daylight scenes, use warm/volumetric accents only when justified by the source and the beat. Avoid turning every scene uniformly orange or making the background excessively blurry.

The phrase "4K look" is an aspiration for richness, not a native 3840×2160 guarantee. Inspect the actual MP4; older Muse outputs were around 1280×720. Only describe 4K delivery as separately upscaled/mastered if the pipeline actually performs it and tests sharpness.

## 4. Cinema grammar and ten-second performance

Choose the shot for its narrative purpose, not a random lens number:
- Geography/reveal: wide, 28–35mm-equivalent, deliberate short dolly, unobstructed set geography, minimal dialogue.
- Emotional conversation: medium two-shot or medium-close 50mm-equivalent, speaker eye level, visible face/mouth and hands, gentle nearly-locked camera.
- Realization/fear/wonder: close-up 65–85mm-equivalent, minimal camera move, micro-expression and a real acting pause.
- Object and mechanical prop: close/insert 70–100mm-equivalent, believable articulated finger/claw-object contact and coherent background.
- Exploration: medium-wide 35–50mm-equivalent, controlled lateral tracking and correct foot-ground motion.
- Over-shoulder: screen-direction and 180-degree axis must match previous shot, no mystery extra character.

Default acting timeline (adapt, don't repeat mechanically): 0–2s pose, eye line and motivation; 2–7s one meaningful action and/or brief dialogue; 7–10s emotional reaction/end pose leading into next shot. One shot = one main action and one coherent emotion. No edits/cuts, camera teleport, 360-degree spin, random montage, slideshow zoom, unnatural prop transformations or unmotivated fake zoom.

A shot can look spectacular without being chaotic: clear staging, silhouette, foreground/midground/background, storytelling contrast, subtle hand acting, carefully designed SFX and expressive but not exaggerated faces. In dialogue shots avoid camera changes that hide lips and make lip-sync impossible to inspect.

## 5. Acting, vocal identity and Slow English A2

Load the CURRENT voice_registry.json from CINE and the audition status. No automatic claim that a selected local EmoVoice voice is owner-approved, licensed or perfectly age-matched. Juno must sound youthful instead of a mature adult; Lia clear and gentle; Mara warm; Evan reassuring; Orin grounded and wise; earth grandparents warmly distinct; Bubu playful; BIX compact and lightly robotic.

Direct one main speaker in a current HaoHao/OpenVoice conversion shot. An offscreen mention does not add a speaker or face. Spoken English should be natural A2: familiar vocabulary, short clauses, deliberate stress, emotion anchored to acting, clear proper names, natural breathing pauses, not theatrical screaming or robotic monotone. Aim for roughly 110–145 spoken words per minute verified on real final audio, not merely a written speed slider. Allocate only as many words as fit the 2–7s dialogue window and ending reaction.

For external imports preserve ONE PHYSICAL TEXT LINE per shot and EXACTLY ONE empty line separating shots. In a separate structured runtime voice plan, bind exact text, speaker, emotion and selected voice profile. HaoHao parses an INTERNAL line such as:

    @Juno [happy]: "Dad, Bix can carry the toast now. I tested him yesterday."

But the above must be its own internal voice-plan line, not another line inserted into the import TXT. The local EmotiVoice preview pacing fix does NOT rewrite Muse's original mouth animation or real audio timing. After generation compare ASR, proper names (Bix), age/timbre/emotion and lip-sync by listening and examining the video; OpenVoice V2 converts timbre without changing the native picture stream.

Use low-volume diegetic ambience appropriate to location: morning birds outside, teacup movement, quiet kitchen cloth movement, delicate magical bell sound. No noisy, cluttered soundtrack that masks the English-learning speech. Sound effects should be motivated by visually observable actions.

## 6. Subtitles REQUIRED on every final spoken shot

Deliver English subtitles for the Slow English audience whenever a character actually speaks. Preferred production path: Muse renders clean scene with no baked-in writing → speech and mouth alignment QC → post-conversion final accepted audio → SRT/VTT timed by forced alignment and human check → readable bottom-safe overlay burned into FINAL MP4 or appropriate sidecar delivery → final video/subtitle QC.

Caption only the final approved actual spoken words with correct proper names and punctuation; if audio differs from the locked script, FIX or HOLD audio rather than silently captioning words never spoken. Bottom center, white simple sans serif, thin dark outline/shadow, at most 2 lines; remain inside mobile safe area, avoid lips/hands/props, only visible during speech; preserve exactly 10.0 seconds and 16:9. Silent shot: no subtitle.

If user explicitly asks Muse to draw text IN native generation, create an EXPERIMENTAL variant and inspect spelling, jitter and timing; never treat this as the production default or assume accuracy. "No text in native Muse image/video" and "subtitles mandatory in final delivery" are compatible and intentional.

Maintain shot-local SRT timing 0–10 seconds, and offset timestamps by 10 seconds per preceding shot when assembling an episode. Don't accidentally combine 270 separate local subtitle tracks without global offsets.

## 7. Single-line example for first-frame image

This example is stylistic guidance for the previously recorded EP001 S003 beat; only use when the locked script version and owner visual references still validate it.

    EP001_V22_S003 FIRST FRAME, 16:9 single full-bleed frame, ACTIVE TAGS FOR THIS SHOT: [juno,bix]; @Juno @BIX EXACT SOURCE LOCATION @BellKitchen_Day; owner-verified youthful 13-year-old Juno face and approved outfit, compact BIX teal-and-gold turtle-pangolin robot with NO bell, actual approved kitchen topology and D55 morning light direction, medium two-shot at child eye height with 50mm-equivalent composition, Juno looks at BIX balancing toast, subtle believable hand/claw contact and focused expressions; original premium stylized 3D feature-film still, one image not grid/collage, no extra person or props, no text or watermark.

## 8. Single-line example for ten-second Muse video

    EP001_V22_S003 VIDEO, exactly 10.0 seconds, 16:9, 24fps, one continuous take, ACTIVE TAGS FOR THIS SHOT: [juno,bix]; @Juno @BIX EXACT SOURCE LOCATION @BellKitchen_Day; original premium cinematic stylized 3D family animation with original owner-canon face/age, approved Juno workshop outfit and unchanged BIX mechanical teal-and-gold shell without a bell, match the approved kitchen set topology, 4K-detail visual look only; child-eye medium two-shot with stabilized gentle 50mm-equivalent push; 0–2s Juno looks at BIX balancing toast; 2–7s Juno speaks in a youthful, clearly articulated, happy-proud A2 voice while BIX subtly adjusts its claws; 7–10s BIX lifts its head in a pleased reaction and Juno smiles; exact one-speaker dialogue: "Dad, Bix can carry the toast now. I tested him yesterday."; quiet cozy kitchen ambience and soft plate contact, actual expressive eye/hand movement and mouth animation, no photorealism, no extra speaker/character, no set changes, no jump cuts, no collage, no baked-in text or watermark; English captions mandatory in final post-QC delivery.

VIDEO TEXT + FIRST FRAME TEXT are two different output artifacts. Their shot IDs, character tags, location tag, storyboard and source SHA must match exactly. Every adjacent shot line is separated by exactly one blank line (no internal newline), as demanded by HaoHao import.

## 9. Structured runtime record / caption plan

Keep this data separate from the external import TXT. Example keys are illustrative; placeholders require owner-approved sources:

    shot_id: S003
    script_revision: EP001_V22
    duration_seconds: 10.0
    fps: 24
    aspect_ratio: 16:9
    visible_cast: [juno, bix]
    haohao_actor_tags: [@Juno, @BIX]
    location_tag: @BellKitchen_Day
    location_view_id: MUST_RESOLVE_REAL_OWNER_APPROVED_VIEW
    first_frame_sha256: MUST_FILL_AFTER_APPROVAL
    speaking_cast: [Juno]
    voice_plan: [@Juno [happy]: "Dad, Bix can carry the toast now. I tested him yesterday."]
    audio_qc: NOT_RUN
    subtitles_required: true
    subtitle_source: FINAL_ACCEPTED_AUDIO
    subtitle_format: SRT_AND_BURNED_FINAL_MP4
    subtitle_position: BOTTOM_SAFE_CENTER
    subtitle_max_lines: 2
    subtitle_qc: NOT_RUN
    release_state: HOLD_UNTIL_REFERENCES_VOICE_AND_SUBTITLE_APPROVED

A placeholder is a HARD BLOCKER, not a functional ID. The pipeline must not queue a shot for Muse if first-frame, face, location or rights approvals are unresolved.

## 10. Provenance, safety, and independent QC

Use the film's family-friendly original-fantasy aesthetic. No verified official comprehensive Muse banned-word list exists: check real semantics, child-safe content, assets, commercial image/voice rights, official policy and correct account/quotas. Non-graphic magical peril and protective acts can be narrated honestly. Do not obfuscate content to circumvent moderation or advise account rotation to evade restrictions.

For each accepted shot record screenplay revision, actor+location reference SHA, real attached images, validated single-speaker dialogue plan, actual FFprobe video dimensions/frames/audio, ASR transcript, media-level identity and room-geometry QC, continuity and lens/blocking QC, mouth sync human evaluation, SRT subtitle timing/spelling, final watermarks/visual artifacts, and clear owner approval. A HaoHao "Xong" status alone is RENDERED_UNREVIEWED. Native 720p is not native 4K even after upscaling. A passing static preflight does NOT approve production.

Persistent entry point: existing CINE cine-bell-leaf-stylized-3d-prompt-director/SKILL.md and its byte-matched .agents twin; load references from repo on every run. Git storage is durable, but models only use skills reliably when the orchestrator actually loads these files.

## 11. HaoHao automatic-asset matcher: no extra characters (2026-11-09)

A VERIFIED installed-app behavior: HaoHao's `Compose.findCharacters` attaches stored character art for every matching plain name **anywhere in the raw prompt**, as well as for `@name`. The renderer does NOT infer that text such as "BUBU's tail must stay consistent" or a spoken mention of "Mara" means OFFSCREEN ? both can silently attach unwanted portraits. Location descriptions such as "Mara's workshop" can trigger this, too.

The EP001 prompt generator now emits the BUBU/BIX visual canon clauses **only when those characters are visible**, removes unneeded offscreen names from a registered location's descriptive brief, and uses `haohao_detected_character_names` to compare predicted attachment names against `haohao_names` on BOTH the image prompt and video prompt and on internal fixed-voice lines. Unexpected character matches cause `HOLD_DO_NOT_QUEUE` with blocker `EXTRA_HAOHAO_CHARACTER_REFERENCE_MENTION` until the director can fix the actual meaning without changing Canon or exact spoken dialogue. Never bypass the gate by omitting a truly visible actor or falsifying a voice line.

On the 2026-11-09 installed owner inventory, the stricter 270-shot preflight yields 40 `PILOT_ONLY_REQUIRES_HUMAN_QC` and 230 `HOLD`, including 14 shots carrying offscreen-name/attachment mismatches. **Four specifically selected independent 10-second samples** (S002, S145, S181, S187) were sent through HaoHao after inspection, one on each of four logged-in accounts; this is not approval for unlimited/multi-account quota evasion or automatic mass-scale. The initial three completed outputs are **native 1280?720, 24fps, exactly 10s** with converted voice for speaking scenes; Muse visually baked some text despite explicit no-native-caption instruction. Therefore native 4K, face exactness, subtitle accuracy and human lip-sync QC remain UNAPPROVED.

Re-run `python tools/bell_leaf/build_haohao_ep001_director_batch_v3.py` and `muse_haohao_skill_gate.py` whenever character/location descriptions or screenplay revisions change; inspect live `assetSnapshot.bindings` for each queued shot. Keep explicit `@actor @location` tags plus strict visual continuity, but never depend on tags alone.
