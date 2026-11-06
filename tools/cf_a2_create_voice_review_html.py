#!/usr/bin/env python3
"""Generate offline audition page for 10 Bell & Leaf voices (no auto-approval)."""
import html,json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/"data/slow_english_a2/voice_cast_round1"
OUT=BASE/"VOICE_AUDITION_COMPARE_NOT_APPROVED.html"
def esc(x):return html.escape(str(x),quote=True)
def make():
 report=json.loads((BASE/"A2_AUDITION_REPORT.json").read_text(encoding="utf-8"))
 registry=json.loads((ROOT/"config/niches/slow_english_a2/voice_registry.json").read_text(encoding="utf-8"))["voices"]
 rows=[]
 for row in report["voices"]:
  tag=row["tag"];src=BASE/(tag+"_CANDIDATE_NOT_APPROVED.wav")
  paced=BASE/"a2_paced"/(tag+"_A2_PACE_PREVIEW_NOT_APPROVED.wav")
  if not src.is_file() or not paced.is_file():raise FileNotFoundError(tag)
  if hashlib.sha256(src.read_bytes()).hexdigest()!=row["source_sha256"]:raise ValueError("Voice changed: "+tag)
  who=registry[tag]["display_name"]
  rows.append(f"""<section class="voice"><div class="title"><h2>{esc(who)}</h2><small>{esc(tag)} · suggested {row['a2_target_wpm_proposed']} WPM · original {row['raw_wpm']} WPM</small></div>
   <p class="line">{esc(row['transcript'])}</p><div class="grid">
   <div><b>Original VoxCPM2</b><audio controls preload="none" src="{esc(src.name)}"></audio></div>
   <div><b>A2 listening preview</b><audio controls preload="none" src="{esc('a2_paced/'+paced.name)}"></audio></div>
   </div><div class="note"><b>Suggested review:</b> age fit · American English pronunciation · believable emotion · same-character identity · A2 clarity · voice distinctness
   <textarea placeholder="Your notes for this character (copy into your review message, no automatic storage)" rows="2"></textarea></div></section>""")
 doc=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
 <title>Bell &amp; Leaf – A2 Voice Casting Review</title>
 <style>body{{font:16px/1.55 system-ui,-apple-system,sans-serif;background:#111720;color:#eef3f9;margin:auto;max-width:980px;padding:30px 18px}}
 h1{{font-size:1.6rem}}h2{{margin:0;font-size:1.22rem}}small,p{{color:#b9c6d6}}.voice{{margin:16px 0;padding:20px;border:1px solid #3f4a59;border-radius:14px;background:#1b2430}}
 .title{{display:flex;gap:18px;align-items:baseline;flex-wrap:wrap}}.line{{font-style:italic;font-size:1.06rem}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}
 audio{{display:block;width:100%;margin:8px 0 12px}}.note{{margin-top:12px;color:#afbac7}}textarea{{margin-top:8px;width:100%;box-sizing:border-box;min-height:70px;background:#101721;color:#eee;border:1px solid #526273;border-radius:6px;padding:8px}}
 @media(max-width:650px){{.grid{{grid-template-columns:1fr}}}}.warning{{border-left:4px solid #d4a34b;padding:12px 16px;background:#2b261d}}</style></head><body>
 <h1>Bell &amp; Leaf — 10-character Voice Casting</h1>
 <div class="warning"><strong>CANDIDATES ONLY — 0/10 voices approved.</strong> These WAVs were synthesized on the RTX 3060. A2 previews are time-stretched for listening, not independent performances.
 Do not approve based only on duration; listen for wording, pauses, age/character fit and emotional authenticity. Master voice ID and SHA are locked only after owner approval.</div>
 {''.join(rows)}
 <p>Audio stays on your Windows computer. This page does not upload media, transmit reviews or change Voice Registry.</p></body></html>"""
 OUT.write_text(doc,encoding="utf-8")
 print(json.dumps({"html":str(OUT),"voices":len(rows),"voice_approved":0},ensure_ascii=False))
if __name__=="__main__":make()
