---
name: cine-bell-leaf-stylized-3d-prompt-director
description: Mandatory Bell & Leaf 3D CGI family-animation image and 10-second video prompt writing, preserving immutable owner Canon faces, character silhouettes and room geometry. No live-action recasts or false approvals.
---

# CINE — Bell & Leaf 3D Animation Prompt Director v1.0

## Scope and trigger
Apply whenever preparing Bell & Leaf episode/trailer images, image-to-video clips, Flow/Muse prompts, camera/acting direction or shot batches. The scoped niche is magical_witch_family_stories under slow_english_a2_story and series bell_leaf. These standards apply to EP001 onward, including future EP1000+, but EP001 currently has the only complete 270-shot visual binding; new episodes MUST establish their own verified bindings. Do not force 3D animation onto other Slow English audio and narrative niches.

## Mandatory read-only Canon sources
- config/niches/slow_english_a2/CHARACTER_VISUAL_CANON_LOCK_CURRENT.json — immutable approved character identity.
- config/niches/slow_english_a2/OWNER_VISUAL_REFERENCE_BIBLE_20261108.json — owner original assets, SHA, 9 single-view location plates and concept boards.
- .claude/skills/cine-a2-muse-reference-anchoring/integration/config/LOCATION_CURRENT.json — authoritative site/room topology; NEVER duplicate it.
- docs/story/bell_leaf/ep001_screenplay/EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json — per-shot cast/location tentative bindings.
- config/niches/slow_english_a2/stylized_3d_prompt_contract_v1.json and i2v_provider_contracts_20261108.json.
- docs/story/bell_leaf/MUSE_I2V_PROVIDER_STYLE_CONTINUITY_20261108.md, docs/story/bell_leaf/OWNER_VISUAL_REFERENCE_HANDOFF_20261108.md.

Owner original source > verified source crop > separately owner-approved new angle > prompt adjectives. Character sheets/crops are identity anchors, NOT guaranteed proof a new generated image has the same face. Never publish owner art PNG to public GitHub without express authorization. A clean GitHub clone missing PNGs must BLOCK, not hallucinate images.

## Character and setting lock
Exactly approved faces/costumes for Evan, Mara, Juno (boy 13), Lia (girl 11), Orin, Arthur, Rose, supporting Elara. BIX = small turtle-pangolin ROBOT WITHOUT bell. BUBU = small purple spirit cat with exactly ONE GOLD collar bell and continually SPARKLING PURPLE SPIRAL TAIL. No Mia, Grandpa Walter, Biscuit or other generic Slow English templates. Evan and Arthur/Rose must not learn the family's magic accidentally. Aila has NO approved owner visual/voice, so do not invent a face.
Resolve ONLY actors visibly framed in a shot; voice-only roles get no face images. If none, set ACTIVE TAGS FOR THIS SHOT: [] and attach no character refs. Location must use its existing site_id/space_id and source image SHA; one owner primary angle does not certify other angles, mirrors or overnight geometry. The monumental hall is NOT approved as the small secret recently built Earth fixed station. Never place a storyboard/collage/9-grid into a single scene image.

## IMAGE direction (Flow/Muse Image)
Write ONE full-bleed 16:9 standalone STYLIZED 3D CGI animated-family-film first frame, not a photo of a real actor. Use the attached EXACT owner character face and hero reference(s), and exact location plate. Describe single intended pose, eye line, character positions, correct camera distance and object interaction, source-faithful sculpted face, eye geometry, age, costume, body proportions, characteristic materials and environment topology. For daytime scenes use neutral D55 around 5500K, clean whites, soft CGI shadows, restrained saturation, 50mm look and mild depth of field; night scenes keep their canon lighting. One image only; no subtitle, additional person, new architectural features or panels.

Never use positive live-action/real actress/photoreal human skin pores/hyperreal people descriptions. Never substitute a generic Disney/Pixar look or a prettier but different face for owner's specific approved original.

## VIDEO direction (Muse/Flow I2V)
The real standalone approved image is the literal first frame and style authority. Video prompt describes MOTION rather than re-inventing face, eyes, hair, costume or room. Use exactly ONE continuous 10.0-second take:
- 0–2s preparation, eye focus and initial subtle movement.
- 2–7s ONE purposeful physical action: gesture, steps, hand-to-object action, gaze, lips or breathing; real visible movement rather than zoom-only.
- 7–10s a meaningful emotion/reaction and settle.
Specify locked or gently motivated camera, maintain original stylized CGI character geometry and room, no cut, montage or large orbit that requires unapproved unseen facial angles. Prefer short positive camera instructions over long negative lists; negative prompt belongs only in a proven-supported provider field. Dialogue/voice identity needs approved WAV and real lip-sync/viseme QC; a voice-name string in a prompt is NOT a voice lock. One shot cannot carry ten complex actions or lengthy two-person conversation.

## Executable compiler
For EP001, write a structured JSON shot brief using shot_id, visible_cast, image.framing, image.pose, video.setup_0_2, video.action_2_7, video.reaction_7_10, video.camera. See docs/story/bell_leaf/ep001_screenplay/EP001_3D_PROMPT_BRIEF_EXAMPLE.json.

    python tools/bell_leaf/compile_3d_animation_prompts.py --brief docs/story/bell_leaf/ep001_screenplay/EP001_3D_PROMPT_BRIEF_EXAMPLE.json --out-dir data/story_quality/ep001_3d_prompt_drafts

Outputs: FLOW_IMAGE_DRAFTS.txt and MUSE_VIDEO_DRAFTS.txt, BOTH one complete prompt per shot on exactly one line and exactly ONE empty line between successive shots. Same S### order and active tags. DRAFT_QC_RECEIPTS.json records source path and unresolved blockers; production_authorized ALWAYS false. No made-up provider media IDs, original character names, location plate or human approvals.

Next run tools/bell_leaf/muse_i2v_preflight.py with a REAL approved first frame, verified provider+model+uploads, then tools/bell_leaf/muse_i2v_frame_qc.py on a real 10-second MP4. Inspect source vs 0,2,5,8,9.7s and also watch continuous clip. Reject if CGI becomes photographic human, face/age/body, wardrobe, Bubu tail sparkle, Bix's lack of bell, site topology, lip-sync, real acting or framing fail. No automatic approval from passing static prompt checks.

## Skill QC rubric
A: correct niche and episode-only characters; B: source SHA face/hero/room validated; C: one 16:9 film frame, clear character pose, room correct and no collage; D: animated CGI rendering without real-human language; E: purposeful camera + acting, three coherent physical beats in 10 seconds, no camera-only zoom; F: emotion and A2 clear dialogue only if approved WAV available; G: five-frame+continuous video real-review and independent editor approval; H: do not overwrite source images, never silently publish source art, record evidence.

**Guarantee boundary:** The skill and text are drafting and detection aids, NOT a guarantee a generative model can keep a physical 3D face identical for 1,000 episodes. A reusable owner-approved Blender rig is more deterministic for strict geometric identity.

## Official source principles
- Meta Muse Image anchor series: https://dev.meta.ai/docs/cookbook/anchored-image-series
- Google I2V: https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/best-practice
- Runway Gen-4: https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide

## Required first-15-second hook for EVERY Bell & Leaf episode (2026-11-09)
The 0-10 second opening shot S001 MUST create a TRUE, clearly visible, episode-specific question or tension. The next 10-second shot S002 MUST connect or reinforce it by 15s. Keep every Muse source shot at exactly 10.0s (24fps/240 frames): NEVER generate a 15s shot to implement the 15s hook. No long logo/recap first, fake drama, fabricated stakes, rapid A2 exposition or automatic claim of audience retention. Vary genre: mystery, heartfelt decision, comedy trouble, urgent problem, visual surprise or disaster when truly justified. Do not re-use the Veylora disaster intro on future episodes. For EP001: S001 previews the real past Veylora event with only Mara and Orin; S002 cuts to the present Earth kitchen as Bix makes an ordinary two-note cup sound and Mara freezes. The past event is fully explained later at SC-006. No Evan, Juno, Lia, Bix, Bubu or Earth grandparents can appear in the historic teaser. No masked villain reveal. The Veylora station location plate is NOT approved; block final images. Require opening_hook in story plan, run tools/bell_leaf/opening_hook_gate.py and tools/cf_story_quality_gate.py check. A structural PASS requires separate human story/art review and real first-30s audience retention after publication.
