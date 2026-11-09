# Bell & Leaf EP001 / HaoHao prompt batch

Full prompt files have exactly one physical line per shot, with exactly one blank line between shots.
NEVER PASTE ALL_270 into the live queue before reviewing EP001_QC_MANIFEST.json; many named scene and Aila reference assets are not registered. Render source first frame before final video.

IMPORTANT: HaoHao automatically attaches references on ANY bare registered character name, not just @ tags. Each prompt is checked against intended on-camera cast. A missing scene location is an explicit _PENDING placeholder, not owner-approved artwork.

HaoHao fixed TTS only parses a voice line as an isolated line formatted @Juno [happy]: double-quoted English text. The strict one-line source prompt does NOT by itself activate fixed voice. A pilot submission converts the one-line file into a runtime prompt with separate voice line, then checks saved voicePlan. The native voice replacement mode is NOT proven accurate lipsync; for two speakers in one shot the current engine is blocked. Never claim native 4K just because the prompt requests it. Initial HaoHao videos measured 1248x704 24fps for 10s.

Run proof-of-concept only for approved pilot-eligible shots and actual owner assets. All full-batch media and artistic approval flags remain false.
