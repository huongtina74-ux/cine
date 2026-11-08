# BELL & LEAF — Muse I2V 3D identity retention, research and executable preflight (2026-11-08)

**State:** local preflight and QC tools only; NOT a real Muse API connection, paid generation, certified animated performance, approved voice or 270-shot release. Applies solely to Slow English A2 / magical_witch_family_stories / Bell & Leaf.

## Critical finding: "Muse" does not identify an engine

The current CINE workflow uses the name Muse without a verified provider URL, logged-in model version, image-reference slots, first-frame contract or real video task. Do not equate all Muse websites, Meta Muse Video, or Fawna Muse.

- **Meta Muse Video**: Meta launched a July 7, 2026 preview; public article does not prove a generally usable production endpoint for our account or 10-second exact reference/voice inputs. https://ai.meta.com/blog/introducing-muse-image-muse-video-msl/
- **Fawna Muse**: third-party engine WAN 2.7; documentation offers image-to-video, 10s, 16:9, first/last frame, no dedicated style-reference slot, and a special 9-panel composite placed in its first-frame slot for character consistency. This is **not compatible** with Bell & Leaf's mandatory SINGLE complete production scene as frame 0 unless actual capability for separate references can be verified. https://www.fawna.ai/docs/models/muse/
- **Google Flow/Veo 3.1**: separate engine with reference ingredients and start/end frames. https://support.google.com/flow/answer/16353334 and https://deepmind.google/models/veo/
- **Gemini Omni 1.2 Flash**: announced November 5, 2026; Google says 3-15s output, combined character/style/audio references and stronger character continuity. Test through an authorized Google Flow/Omni interface only if it actually supports those inputs and is affordable; it is not a Muse product and no success is guaranteed. https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-omni-1-2-flash/

Model documentation and claims are never proof of the user's actual subscription features or fidelity. First identify exact product, model, prompt/reference slots and original rendered video.

## Why 3D CGI becomes live action

This is a style and identity-drift failure: generative video synthesizes/guesses frames rather than animating a fixed skinned Blender 3D mesh. Large head turns, long camera orbits, missing reference views, photoreal model bias, multi-person occlusion, "realistic human" phrasing, or a 9-grid inserted as a scene image can cause recasting. These are credible hypotheses, not diagnosed causes of a particular Muse output without seeing its frames. Also CINE carries an unrelated generic Slow English A2 character sheet with **Mia / Grandpa Walter / Biscuit**: those names must never enter this Bell & Leaf subniche's prompts.

## The strict pipeline — source look belongs to FIRST FRAME, prompt controls MOTION

1. Resolve the correct episode and shot S001–S270. Read EP001_SHOT_VISUAL_REFERENCE_BINDINGS_v1.json, the v2 locked face/hero/tail crops and the owner location source SHA. Confirm truly visible cast per shot; do not load an entire family sheet into a one-character shot. No reference images when there are no visible characters.
2. Generate the EXACT SINGLE full-frame 16:9 stylized 3D CGI still with the correct source face/body design, neutral D55 5500K, correct location doors/windows/props and no image text/collage. The owner references do not permit arbitrary new angle/wardrobe. Aila has no approved face. The 483 missing room and 756 prop view slots remain blocked; a single-angle room reference does not establish a reverse angle.
3. Freeze the image path and SHA256. I2V first frame MUST be this finished approved standalone scene image, not a 3x3/9-grid character contact sheet. Model reference slots are separate only if the ACTUAL selected engine supports them.
4. Keep I2V prompt short and action-focused. Google's official I2V advice is **prompt for motion only**: image already defines visual identity and background. https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/best-practice . Specify ONE main action with at most simple 0-2s, 2-7s and 7-10s acting beats, gentle eye and jaw/body movement, stable or motivated camera, one take. Avoid restating skin/hair/lighting dozens of times, or "photorealistic human, live action, real actor" as positive instructions. Keep one concise positive CGI style constraint and use negative field ONLY if provider supports it.
5. If engine generates unstable voice or lip-sync, discard its speech and use the same licensed/approved immutable character WAV and external validated lip-sync. Names like VOICE_MARA in a prompt do not lock an audio identity.
6. Inspect actual MP4 at frame times 0/2/5/8/9.7 seconds AND watch the entire moving clip. Reject if the face turns into a human, age changes, Bix gains a bell, Bubu loses his spiral sparkling tail/one gold collar bell, scene changes topology, an unapproved person appears, or the clip only zooms while actors stand still. Re-render only after narrowing complexity and fixing first-frame inputs. Do not use QC screenshot contact sheet as the next video first frame.
7. Once each real shot has source/engine/receipt/video hash/visual reviewer/voice and continuity evidence, proceed to the existing CINE final media release gate. There is NO automatic human approval from prompts, metadata or hashes.

## Pilot before large batches

T01: Mara CGI medium shot — 0-2s looks at leaf, 2-7s turns her head only about 15 degrees and speaks a short A2 sentence (approved master WAV), 7-10s breathes and shows concern. No zoom-only motion.
T02: Bubu CGI full body — 0-2s blinks, 2-7s takes two small steps and curls his spiral purple tail, 7-10s holds a small curious expression. Purple tail sparkle remains visible in EVERY frame; exactly one gold collar bell.
T03: Mara + Juno two-person shot — 0-2s both glance at spoon, 2-7s Juno reaches for it while Mara reacts; 7-10s Mara smiles. First test is action-only; only add two distinct voices when approved WAV and actual lip-sync conditioning are available.

Do not test the full 270 shots, unknown Meta Muse API, expensive credits, cloning or unapproved Aila face without owner approval. If same model converts CGI to live action on several controlled test clips, swap to an authenticated image-reference-rich I2V model (e.g. an applicable Flow/Omni/Veo capability) or use locally locked Blender rig animation for deterministic model geometry.

## Executable CINE commands

Dry-run / fail-closed example (written prompt is one continuous physical line, generated even if execution is blocked):
python tools/bell_leaf/muse_i2v_preflight.py --shot S001 --provider unknown_muse --motion "The small turtle-pangolin robot slowly lifts the spoon and turns toward Mara." --out data/story_quality/S001_preflight.json --txt data/story_quality/S001_muse_prompt.txt

Registered provider IDs: unknown_muse, meta_muse_video, fawna_muse, google_flow_omni_1_2, google_flow_veo_3_1. This local script NEVER submits a task or requests paid credits. It demands shot director verification, real source assets, correct location, one approved 16:9 first frame and verified account/provider before a remote render could be approved. No provider is currently marked verified.

After a REAL rendered 10s file exists:
python tools/bell_leaf/muse_i2v_frame_qc.py --shot S001 --video data/video/S001_actual.mp4 --first-frame data/images/S001_approved.png --out-dir data/story_quality/S001_review

The second command extracts frames and creates a human review form with ALL QC fields pending. A report with no issues does NOT prove a real stable 3D animation. The existing tools/cf_a2_media_release_gate.py also requires independent audio/lipsync review and actual provider authenticity; nothing here bypasses it.

## Personal source artwork and cross-niche isolation

Character and location source 44 PNGs are in owner Windows CINE / a local Git commit. Public GitHub cine repo contains source manifests and rules, NOT image binary backup; remote backup requires private authorized storage. Don't expose original commercial artwork by pushing image binaries to public repository. Never mix Bell & Leaf with unrelated Slow English A2 character sheets or the audio-story niche. Keep 1-line prompt and exactly 1 blank line between shot prompts in an import-ready batch; never copy a 3x3 storyboard image into one video shot.
