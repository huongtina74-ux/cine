# Bell & Leaf — Voice Casting v1.0 (integrated into the existing CINE niche)

**Canonical data:** [voice_registry.json](voice_registry.json) in this same folder. **No narrator.** Keep exactly ten character tags; `bangoai` (maternal grandmother) is conditional on the Veylora story arc. The casting description comes from the owner's requested character/voice directions; it is NOT an approved WAV, a real VoxCPM2 voice ID, or proof of deployed voice synthesis.

## Workflow: design → listen → approve → lock → perform

1. Use `voice_casting_prompts.txt` to produce multiple **licensed/consented** character voice candidates. Child roles must use licensed age-appropriate synthetic voices or performers with appropriate consent, not unconsented minor cloning. The user requested **VoxCPM2 as a candidate engine**, but actual CLI/API availability and settings are not verified in CINE.
2. Evaluate each candidate in neutral, joyful, worried and reassuring lines for stable pitch/timbre, US pronunciation, emotional range and clarity for English A2.
3. Compare confusing pairs side by side: Lia ≠ Mara, Bubu ≠ Bix, Orin ≠ paternal Grandfather, maternal ≠ paternal Grandmother. Reject voices that sound interchangeable.
4. Approve and archive actual `sample_wav`, `sample_sha256`, `transcript`, `voice_id`, `voice_provider`, `voice_model_version`, license/consent record, engine/config and human decision. All these remain **null/pending** until actual audio has been auditioned. Do not substitute `voice_profile_key` for a provider's `voice_id`.
5. Every shot: resolve structured `speaker_tag`, never full-prompt regex. Reuse the same approved master and provider voice identity for every episode; vary only delivery/emotion. Generate dialogue WAV with exact approved script text.
6. Measure real WAV duration; align words/visemes to actual dialogue before lip-sync. If dialogue lasts 4 seconds in a 10-second shot, use the remaining six for meaningful movement/reaction/ambience. **Never stretch speech to fill the whole shot**.
7. QC pronunciation, voice drift, timbre consistency, noise, clipping, emotional congruence, timing, voice rights, character identification, lipsync and audio-SFX/music balance. Fail closed if audio asset is missing or different.
8. Keep archived approved WAV+SHA, engine/model settings and cast decision version; never silently change cast over 1000+ episodes. Any re-cast needs explicit review.

## Status
Casting **design metadata 10/10**, prepared English prompts **10/10**; audio masters **0/10 approved**, real VoxCPM2 10-voice synthesis **not verified**, lip-sync **not verified**, production release **BLOCKED**.

## Speaker ID mapping
Evan `bo`, Mara `me`, Juno `juno`, Lia `Lia`, Bubu `bubu`, Bix `bix`, Orin `ongngoai`, maternal grandmother `bangoai` (conditional), paternal grandfather `ongnoi`, paternal grandmother `banoi`. The older source Voice Bible's `NARRATOR` slot is **excluded**.
