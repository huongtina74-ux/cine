"""Audit 2026-11-11 step 3b: dedicated sample for independent survival-story animation (A3), so A3 is not judged only on
videos that leaked into Minecraft searches. 7 queries x {this month by views, this month by relevance} read in the owner's
browser 2026-11-11 ~16:00Z, enriched with cf_mc_niche_enrich.py (82 API units). Data: .../out/2026-11-11_audit_z/.
Prints per-channel best video, long-upload count and median for survival-story channels (name/title pattern, see STICK).
"""
import json
import re
import statistics as st
import sys
from datetime import datetime, timezone

D = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Downloads/cine_niche_survey/out/2026-11-11_audit_z/'
V = json.load(open(D + 'videos.json'))
C = json.load(open(D + 'channels.json'))
U = json.load(open(D + 'uploads.json'))
NOW = datetime(2026, 11, 11, 16, 0, tzinfo=timezone.utc)


def ts(s):
    return datetime.fromisoformat(re.sub(r'\.\d+', '', s.replace('Z', '+00:00')))


def dur(d):
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d or '')
    a = [int(x or 0) for x in m.groups()]
    return a[0] * 86400 + a[1] * 3600 + a[2] * 60 + a[3]


STICK = re.compile(r'stick|zombie outbreak|bunker survival|apocalypse survival|survives|survival log|outlast|one more day|doomsday|nobody gets in|'
                   r'kit vs|whythat|wild instinct|marrow|wanderer|headlamp|melvin|thirty nights|stickcalypse|ash holdout|survival simplified|'
                   r'zsurvive|day by day|archival|doomstick|galactic highway|one year inside|your other life|beany|zombie days|undead survived|'
                   r'twisted|nevermund|bunker days', re.I)
res = []
for cid, c in C.items():
    t = c['snippet']['title']
    if not STICK.search(t):
        continue
    age = (NOW - ts(c['snippet']['publishedAt'])).days
    ups = [u for u in U.get(cid, []) if dur(u['dur']) >= 480]
    best = max([u['views'] for u in ups] + [int(v['statistics'].get('viewCount', 0)) for v in V.values() if v['snippet']['channelId'] == cid])
    res.append(dict(age=age, channel=t, subs=int(c['statistics'].get('subscriberCount', 0)), videos=int(c['statistics'].get('videoCount', 0)),
                    best=best, long_uploads=len(ups), median_long=st.median([u['views'] for u in ups]) if ups else None))
res.sort(key=lambda r: r['age'])
for a in (30, 60, 90, 365):
    s = [r for r in res if r['age'] <= a]
    print(f"<= {a} d: {len(s)} channels; best>=100K {sum(r['best'] >= 1e5 for r in s)}; best>=1M {sum(r['best'] >= 1e6 for r in s)}; "
          f"median best {st.median([r['best'] for r in s]) / 1e3 if s else 0:.0f}K; median of channel long medians "
          f"{st.median([r['median_long'] for r in s if r['median_long'] is not None]) / 1e3 if s else 0:.0f}K")
json.dump(res, open(__file__.replace('.py', '.json'), 'w'), indent=1, ensure_ascii=False)
