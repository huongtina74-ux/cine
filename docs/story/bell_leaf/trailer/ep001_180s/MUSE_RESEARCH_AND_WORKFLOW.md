# BELL & LEAF — MUSE I2V 3D CHARACTER & STYLE LOCK V2

**Date:** 2026-11-06. **Deliverable:** 18 Flow still-image prompts + 18 Muse Image-to-Video prompts, one unbroken line per prompt, exactly one blank line between shots; 18 × 10.0s = 180s, 16:9. These are production specifications, NOT rendered or verified Muse clips.

## Important platform identity research

Several unrelated websites use Muse/Muse Video. **Meta** officially previewed Muse Video on 2026-07-07, including native audio direction, but explicitly identified synchronization as an area to improve; it did not in that announcement establish a universal per-shot persistent character lock, waveform-level uploaded audio lip-sync API, duration/resolution guarantees or reproducible VOICE_ID. A 2026-09-15 Meta One announcement said more video generation in Meta AI is powered by Muse models, not that every site branding itself Muse is official or supports the exact same inputs. The old muse.ai hosting/search platform rebranded Skiv on 2026-03-03; it is not a proof of a Meta video-generation route. Third-party sites such as muse-video.app, museaivideo.com, pixmind.io, fawna.ai vary in reference counts, input modes, negative fields and target duration. **Actual generation website, account access, engine/model ID, frame controls, true voice conditioning and success must be verified in the user's real UI.**

Sources:
- https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/
- https://about.fb.com/news/2026/09/introducing-meta-one-subscription-service-more-features-ai/
- https://muse.ai/blog/muse-ai-is-now-skiv
- https://muse-video.app/user-guide (a third-party product; NOT a Meta spec)
- https://www.pixmind.io/ai-video/muse-video (a third-party integration with its own limits)

## 0. Non-negotiable art direction

This is a 3D COMPUTER-ANIMATED CGI family adventure. **Stylized 3D faces and original 3D character models must not be changed into photographic, live-action or photorealistic real people.** Reference is a locked character sculpt/model sheet and the exact single approved first-frame image for EACH shot. Realistic LIGHT and physically based MATERIALS are allowed; they do NOT imply photoreal skin or human actors. D55 ~5500K natural neutral lighting; no warm/yellow cast. 50mm look, slight DOF. Single shot; no nine-grid, split screen, text or captions.

Reference ID map (only include an actual approved image file for an active tag):
- EVAN: fixed male nonmagical Earth postman, original model and approved outfit.
- MARA: fixed adult female witch, face/hair/body and wardrobe exactly as approved.
- JUNO: fixed 13-year-old inventor, original model, no age jump.
- LIA: fixed 11-year-old animal-empathy girl, original model, no adult face.
- BIX: COMPACT turtle-pangolin robot; NO bell; same body/shell shape.
- BUBU: SMALL purple cat spirit, exactly one GOLD collar bell; purple spiral tail with visible SPARKLE on every frame including rear/3/4 views; never anthropomorphize into real human.
- ORIN: elder male wizard, face/hair/beard/body model from approved reference only.
- GRANDPA_EARTH & GRANDMA_EARTH: ordinary Earth grandparents, their own models; no magic faces or substitute strangers.

## 1. Required per-shot attachments

1. **ONE clean 16:9 approved Flow image** matching the shot composition, not a collage or nine-grid. This is the ACTUAL source frame for Muse I2V.
2. Only when supported by the actual UI, add **approved character reference portraits/turnarounds** for ACTIVE TAGS; prefer front/3-4 angle and a full body reference, no cross-character reference contamination. If the model confuses multiple references, use just the shot image and one high-priority identity reference, not a 9-grid first frame.
3. For each character use an original color/model sheet with a unique asset ID, revision and SHA-256 if possible; don't silently swap the image for a regenerated substitute. No source images for inactive tags.
4. Background/architecture plate belongs to the specific approved location, not a generic new hallway; do not use face references for unseen/occluded person.
5. If a UI asks for 'Character References', 'Style Reference' or 'First/Last Frame', use only features actually present, not assumptions imported from another Muse site. Never feed a nine-grid of character images as the INPUT VIDEO FRAME; it risks producing a grid in the output. A dedicated character-reference slot can receive a composite sheet if the specific model explicitly supports it; that is not the shot itself.

## 2. Recommended production order

**Stage A: Make/pick locked Flow 3D CGI frame → manually approve face, body, outfit, Bubu tail, location (NO photoreal actors).**
**Stage B: Muse IMAGE-TO-VIDEO, not text-to-video.** Upload one selected approved first frame. If reference inputs are supported, attach only the matching real asset(s). Paste the corresponding LINE from 18 I2V prompts; use 16:9 and 10s when available. Request 1080p / 24fps only if offered; otherwise generate native valid format and verify/upscale in post (never describe unsupported output as native).
**Stage C: Use approved WAV voice masters.** Waveform/text/speaker mapping determined BEFORE video. No evidence a text command 'VOICE_MARA' makes Muse reuse a speaker embedding across shots. If true audio-conditioned lip-sync is verified in the specific engine, provide the same WAV to that conditioning interface and review synchronized phonemes. Otherwise generate image motion without new speech, then use a separate verified lip-sync engine with the same WAV and composite original dialogue. Do not let Muse invent a new voice for each shot.
**Stage D: Audit each raw video** at 0.0s / 2.0s / 5.0s / 8.0s / last frame and compare with reference. A visually nice shot is REJECT if identity changed, became human, one cat tail disappears, Bix acquired a bell, voices shift or body transforms.
**Stage E: Assemble 18×10s in editor**, inspect cuts, frame count, audio mix, fixed speaker ID, soundtrack licensing and visual style.

## 3. When Muse turns animation into live action

Root-cause suspects: source frame was not approved CGI; prompt says 'photorealistic person', 'real human skin' or asks for feature-film 'realism' without tying it to stylized animation; reference set includes real photos; a model defaults to cinematic live action; many moving characters/faces on screen; faces occluded/turn too far; multiple cuts or hard camera moves; negative prompt unsupported.

**Fix in this order:** (1) enforce actual 3D CGI IMAGE as first frame, (2) remove any live-action/photo wording in positive prompt, (3) reduce shot to 1–2 speaking faces with medium/close framing, (4) gentle camera movement with limited head yaw and real hand/eye acting, (5) use correct refs only, (6) native negative prompt only when supported, (7) test a 10s shot with one speaking character FIRST, (8) reject any style-drift result and regenerate from the same original frame.

The words 'never transform' in a prompt **cannot guarantee** identity preservation; proof only comes from verified video. Repeated generation with same prompt may still vary. For robust 1,000 episode continuity, curate approved image bank, voice bank, model/engine versions, shot QC evidence, and reference IDs.

## 4. Audio safety

Native video generation may create dialogue and effects but it may not preserve chosen speaker voice across separate generations, and lip-sync may be inconsistent. For BELL & LEAF LOCKED audio, TTS/voice cloning/voice acting should output immutable WAV per character; match WAV to shot timeline and apply validated mouth cues in downstream process. If Muse has proven audio-conditioning, use and test it first. Avoid 'perfect lip sync' claims without finished video. The enclosed voice cue JSON is a planning sheet, NOT 9 approved WAV files.

## 5. Model and workflow qualification test (three-shot proof-of-ability gate)

- **T01 MARA talking medium close-up:** lock exact MARA stylized facial identity, mouth, eyes and hair while speaking about a flower; 10s with gentle head turn (<20 degrees).
- **T02 BUBU reacting:** original purple cat, one collar bell, animated expression, full spiral purple tail with persistent sparkles; 10s and clean body motion, no cat-to-human transformation.
- **T03 MARA + JUNO two-shot:** same canonical faces in one moving 10s shot, real action, no duplicates; if failure, split coverage to single-character shots for final trailer.

For each: compare 5 sample frames to the approved first frame, reject identity/2D-live-action drift, inspect natural motion, confirm exact output duration/aspect/native resolution, run audio/lip-sync QC independently. **Do not scale to 18 shots until this small sample passes with the actual Muse engine.**

## 6. Character-identity QA decision

- PASS: recognizably SAME approved sculpt/face across all sampled frames, no new human actor/skin, no change of ages, relative sizes and outfit; active tags exact; background matches known location; intended motion and emotion occur; voice pipeline is controlled separately.
- FAIL: humanized CGI face, enlarged/reduced eyes, altered nose/lips, age/gender drift, different clothes/hair/skin, stretched body, Bubu tail absent, Bubu given human legs, Bix with bell, random extra face, subtitle or nine-grid, no physical motion, WAV changed, uncontrolled dialogue. Regenerate from approved first frame; never approve solely because atmosphere looks good.

## 7. Short-input Muse compatibility

Some third-party sites labeled Muse/Muse Video have an approximately 2,500-character field. Also included are **18 compact Flow + 18 compact Muse I2V prompts each at most 2,490 characters, count verified**, preserving shot action, reference identity rules, no-live-action style, external voice lock and tag format. Use the compact Muse file in short text fields and the full I2V as director/QC documentation. Input limits on the actual provider must be checked in the real UI.

## 8. Format contract

- IMAGE TXT: 18 prompts, each exactly ONE physical line, **ONE blank line** between prompts. FLOW image prep only.
- I2V TXT: 18 prompts, each exactly ONE physical line, **ONE blank line** between prompts. Each begins with contract and contains exact performance timeline from source screenplay, plus external voice master policy and active-tag list.
- PDFs visually line-wrap prompts for human reading; source TXT never has line breaks inside a prompt.
- 10s is a request/target; inspect actual output duration and native frame-rate after generation.
- Trailer shot order/titles and spoken lines stay the same as the EP001 18-shot approved draft unless later officially changed.