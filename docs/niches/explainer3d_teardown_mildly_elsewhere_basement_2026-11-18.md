# Teardown: "He Flooded His Own Basement Before the River Could" (Mildly Elsewhere) — lane X-S1, 2026-11-18

Source: https://www.youtube.com/shorts/rMmG7s-IIMQ — watched in the browser (owner's request), sampled every 1.5–3 s, 0–71 s, captions read on frame. No download. Audio NOT heard (captions only).

## Numbers (OBSERVED 2026-11-18 from the public page)
- 71 s, 1080x1920, Science & Technology, published 2026-11-14 → **27.5M views in ~4 days**, 479K likes, 1,777 comments.
- Channel: joined 2026-09-09 (70 d), 72.9K subs, 158 videos (~2.3/day), 130.7M channel views. Already on `config/research/watchlists/explainer3d_shorts.txt` (leader).
- Last 48 Shorts (MEASURED from the shorts tab): median **203.5K**; "How a Hole … Becomes …" series n=10 median **3.0M**; everything else n=38 median 132K; 12/48 ≥ 1M. This video = ~135× channel median.

## Beat sheet (OBSERVED captions; times approximate)
| t (s) | beat | picture |
|---|---|---|
| 0–3 | HOOK, counter-intuitive act: "He flooded his own basement, the day before the river could." | aerial of one house, river behind |
| 3–10 | setup: neighbours stack sandbags; he runs a hose into his basement; "His neighbor has three pumps." | street, hose, two houses side by side |
| 12 | conflict line (quote caption): "Flood's not till tomorrow, pal." | neighbour leaning on picket fence |
| 15–21 | escalation: water fills to the top step; neighbour "is calling it the indoor pool" | stairwell POV, water rising |
| 24–30 | flood arrives, both houses end up in water; "Next door, the pumps…"; neighbour yells "How's the pool?" | flooded street, low water-level camera |
| 33–42 | EXPLANATION with **cutaway section**: crack in the wall "wide enough for a finger", soaked ground "leans on a basement wall", "the wall is bending in" | wall close-up, cross-section of house + soil |
| 45–51 | everyday ANALOGY: empty can crushed vs full can; water inside "pushes back just as hard" | workbench, gloved hand squeezes can |
| 54–57 | rule: "…to let the water in" | aerial of both houses |
| 60–71 | PAYOFF: "A week later." pumps out slowly ("nice and slow"); "Next door, the neighbor('s basement wall collapsed)… except his kitchen is down there with it." | pump hose; neighbour's basement full of rubble, kitchen fallen in |

## Why it works (INFERRED)
1. Title = an action that sounds stupid ("flooded his own basement") → curiosity gap that only the payoff closes.
2. Two-character conflict (smug neighbour with 3 pumps vs quiet hero) → comedy + someone to root for/against; the twist punishes the mocker.
3. Real physics (hydrostatic pressure on basement walls; FEMA really says pump out slowly, ~1/3 per day) shown with a **cutaway** + a **can analogy** anyone gets in 2 s.
4. Payoff line lands in the last 3 s ("his kitchen is down there with it") → rewatch/loop and comments.
5. Honesty: description states it is a made-up 3D story and what the real guidance is (protects against "misleading" strikes).
6. Fast pacing: new shot roughly every 1.5–3 s; big centred 2–5-word captions; narrator VO + short quoted character lines; channel watermark top-right.

## How it is made (INFERRED from frames)
- Real-time-looking 3D (not AI video): the same street/two houses stay consistent across 0–71 s, true cross-section cutaways, stable geometry → a 3D scene (Unreal Engine 5 or Blender with stock asset kits: suburban houses, trees, picket fence, generic realistic people).
- Simple character animation (lean, walk, point), mostly camera motion + props (hose, water plane rising, crumpled can) carry the story.
- TTS-style narrator + caption track; light SFX.

## CINE version (original, our pipeline)
Template "X-S1 counter-intuitive fix": hook act → mocker → it gets worse → cutaway physics + 2-s analogy → "A week later" reversal.
Production path on our machine: script+beat sheet (showrunner) → Blender 5.2 EEVEE on the RTX 3060 (CC0 assets from Poly Haven, boolean cutaway, rising water plane, one rigged character pair) → local TTS narrator → `cf_auto_edit` (captions 2–5 words, -14 LUFS) → `cf_qc` + qc-reviewer. Flow images (0 credits) for concept/thumbnail only.
Three original ideas (not copies):
1. "He Opened Every Window Before the Hurricane" — pressure equalization myth vs reality (needs fact-check; it is mostly a MYTH → the twist can be that the smug one is wrong for a different reason).
2. "She Parked Her Car in the Lake on Purpose" — no; replace: "He Left His Pipes Dripping All Night" (freezing pipes; moving water freezes later; neighbour's pipe bursts).
3. "He Filled His Pool to the Brim Before the Storm" — hydrostatic uplift: empty pools float out of the ground (channel already has 'Why a Pool Can Float' 101K → our angle must differ; drop if too close).
Every physics claim needs a source before script lock (studio rule).
Cheapest pilot: idea 2, ~40 s, 1 street set, 2 characters, 12–15 shots; measure Blender render time per shot before committing to the lane.
