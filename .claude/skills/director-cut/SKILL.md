---
name: director-cut
description: Write the Director Cut (director_cut.json) for an episode - every shot with section, in/out, cut, emotion, purpose, voice-over line, SFX and on-screen text - so the episode can be auto-edited. Use after render (Long Slide) or after shots exist for any niche, and whenever the owner asks to change the edit, narration or pacing.
---
# Director Cut

The Director Cut is the single source of truth for the edit. `tools/cf_auto_edit.py` builds the video from it; nobody edits by hand.

## 1. Create the skeleton
- Long Slide: `python tools/cf_director_cut.py from-long-slide --episode-dir data/animal_long_slide/episodes/<ID>`
  (one shot per rendered module, cue SFX from the `.events.json` sidecars, sections hook/race/finale).
- Any other niche: `python tools/cf_director_cut.py template --episode <ID> --shots <N> --out <folder>/director_cut.json`, then point each `source` at its clip.

## 2. Fill it (this is the creative work)
Read `episode.json`, `upload_package.json` (synopsis, cast) and the series bible. For EVERY shot write:
- `purpose`: what this shot does for the story (one line). A shot with no purpose is cut or shortened.
- `emotion`: one word the viewer should feel (excited, worried, proud...).
- `vo.text`: the narration line, or empty. Kids: short sentences, present tense, name the character, no scary words.
- `onscreen_text`: only for the hook title or a key number, <= 5 words, `{"text","at","duration","position"}`.
- `cut`: `cut` by default; `dissolve` (0.4-0.8 s) for time passing; `dip_black` (0.6-1 s) between chapters.
- `in`/`out`: trim dead frames at the start/end of a module; keep the first 5 s of the episode moving.
- Sections: rename `sections[].label` - they become YouTube chapters (need >= 3 chapters, each >= 10 s).
- `music.path`: a licensed or self-made track (keep the license file next to it). `keep_source_audio` only for clips that carry useful sound.

## 3. Prove it fits
- `python tools/cf_director_cut.py vo-fit <dc>` - every line must fit its shot at the measured speed (`wpm`; kids narration ~130). Rewrite lines that are OVER; never speed up the voice.
- `python tools/cf_director_cut.py validate <dc> --strict` must print VALID.

## 4. Record
`python tools/cf_decision.py add --kind edit --label OWNER|INFERRED --decision "DC v1 for <ID>" --why "<main pacing choice>" --evidence <dc>`
Then use the `auto-edit` skill.
