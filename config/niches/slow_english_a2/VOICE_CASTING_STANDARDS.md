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

## HaoHao age-perception casting audition — 2026-11-09

This section supplements the ten-role story Canon. The local HaoHao Studio has been updated with **audition candidates only**, not production signoff.

| Character | Story role | EmoVoice trial ID | Voice label | A2 speed | Trial WPM |
|---|---|---|---|---:|---:|
| Juno | 13-year-old boy | 1182 | Brett Condron | 0.70 | 140 |
| Lia | 11-year-old girl | 1851 | Kehinde | 0.86 | 125 |
| Mara | adult mother | 7525 | Jeannie Tirado | 0.70 | 128 |
| Evan | adult father, ~40 | 7553 | BDSEmpire | 0.84 | 132 |
| Orin | senior magical grandfather | 594 | KentF | 0.70 | 130 |
| Arthur | senior Earth grandfather | 6499 | dave7 | 0.70 | 130 |
| Rose | senior Earth grandmother | 8300 | Judith Parker | 0.72 | 128 |
| Elara | senior magical grandmother | 1066 | Laurie Anne Walden | 0.72 | 127 |
| Bubu | purple spirit cat | 5029 | Courtney Sandhu | 0.88 | 133 |
| Bix | friendly small robot | 1335 | Clarica | 0.82 | 134 |

**Evidence and limitations.** Voice IDs were checked against the DreamVoiceDB perceptual-age/timbre annotations (Interspeech 2024): https://huggingface.co/datasets/carankt/DreamVoiceDB . These labels are the age a voice **sounds like** to annotators, not the real age of the human reader. The closest available label for Lia aged 11 is Teenager, so do not claim an authentic 11-year-old voice.

All ten trial WAVs were rendered with the actual installed HaoHao EmotiVoice engine, with one English A2 scripted sentence per role. Automatic ASR matched the scripted words in this controlled test, and pacing measured 125–140 WPM. These metrics do **not** establish human-approved accents, emotional acting, child realism, or voice rights.

**Critical local speed bug repaired:** in the installed EmotiVoice file models/prompt_tts_modified/model_open_source.py, the inference branch called self.length_regulator(x, d_outs, None, ~src_mask), without passing alpha. The installed local copy now passes alpha=alpha. Before the patch, different speed values produced byte-identical WAVs; after patch, 0.70x yielded a ~1.43x-longer WAV than 1.0x for the same text and speaker. Backup stored in supervisor-evidence/HaoHao_VoiceCasting_20261109/runtime_backups.

**Muse limitation:** HaoHao Muse→OpenVoice V2 voice conversion preserves the original video bitstream and native speech timing. The corrected local EmoVoice speaking-speed control applies to the WAV synthesis engine, NOT automatically to video speech that Muse has already produced. Video lip-sync and the commercial rights for individual voices remain separate approval gates.

Before release, the owner must listen to the local matched-text old-versus-new audition clips using BellLeaf_Voice_Audition_Review.html, approve distinctive ages/accent/emotion/identity, check voice rights and actual video lip-sync, and then explicitly approve all 10 Canon master WAVs. No private WAV or personal source artwork is committed to GitHub.
