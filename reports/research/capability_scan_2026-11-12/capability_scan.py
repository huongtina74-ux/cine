"""Capability-based niche scan (2026-11-12, owner: "nghiên cứu kỹ các ngách bạn làm được, đâu chỉ AI").
12 extra niches the studio can make with code / Blender / CAD-CNC know-how / Minecraft modding / screen-recorded tutorials.
Sample: owner browser YouTube search 2026-11-12 ~09:15Z, 2 + 2 queries per niche, filters "this month by views" (m) and
"today" (t, includes 0-view uploads). Rows (rows.txt): niche, bucket, channel index, views, minutes, hours since upload, English
title flag (videos >= 8 min only). Channel stats: channels.list (9 API units). One reading; small samples, labelled OBSERVED.
Usage: python capability_scan.py <folder with channels.json channels.txt>
"""
import json
import os
import re
import statistics as st
import sys
from datetime import datetime, timezone

D = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Downloads/cine_niche_survey/out/2026-11-12_capability_scan/'
HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(D, 'channels.json'), encoding='utf-8'))
IDS = ['UC' + x for x in open(os.path.join(D, 'channels.txt')).read().split()]
NOW = datetime(2026, 11, 12, 9, 25, tzinfo=timezone.utc)
NAMES = dict(ts='true_scale_3d', hw='how_it_works_3d', ae='ancient_engineering_3d', bt='blender_tutorial', ca='coding_ai_tools_tutorial',
             cc='cad_cnc_cabinet', dv='data_viz_maps', mp='math_physics_explainer', mb='minecraft_build_mod', ex='excel_cad_software_tutorial',
             gd='game_devlog', wb='woodworking_build')


def age(cid):
    c = C.get(cid)
    return (NOW - datetime.fromisoformat(c['snippet']['publishedAt'].replace('Z', '+00:00')[:19] + '+00:00')).days if c else None


def subs(cid):
    s = C.get(cid, {}).get('statistics', {})
    return None if s.get('hiddenSubscriberCount') or 'subscriberCount' not in s else int(s['subscriberCount'])


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return 0
    k = (len(xs) - 1) * q
    f = int(k)
    return xs[f] + (xs[min(f + 1, len(xs) - 1)] - xs[f]) * (k - f)


rows = []
for r in open(os.path.join(HERE, 'rows.txt')).read().strip().split(';'):
    n, b, i, v, mins, h, en = r.split(',')
    cid = IDS[int(i)]
    rows.append(dict(n=n, b=b, cid=cid, views=int(v), mins=int(mins), h=int(h), en=en == '1', age=age(cid), subs=subs(cid),
                     title=C.get(cid, {}).get('snippet', {}).get('title', ''), cviews=int(C.get(cid, {}).get('statistics', {}).get('viewCount', 0)),
                     country=C.get(cid, {}).get('snippet', {}).get('country')))
out, L = {}, ['# Capability-based niche scan (capability_scan.py, 2026-11-12)', '',
              'Browser search 2026-11-12 ~09:15Z (this month by views + today), channels.list 9 units. English titles, >= 8 min. '
              'Small samples: directional only.', '',
              '| Niche | Top-month videos n | Median views | >=100K | >=1M | New ch (<=365 d) with video >=100K | Uploaders today: ch / <1K subs | '
              'Young uploaders: n / >=1K / >=10K | Median length |', '|' + '---|' * 9]
for code, name in NAMES.items():
    m = [r for r in rows if r['n'] == code and r['b'] == 'm' and r['en']]
    t = [r for r in rows if r['n'] == code and r['b'] == 't' and r['en']]
    mv = [r['views'] for r in m]
    new100 = {r['cid'] for r in m if r['age'] is not None and r['age'] <= 365 and r['views'] >= 1e5}
    tch = {r['cid']: r for r in t if r['subs'] is not None}.values()
    young = [r for r in tch if r['age'] <= 365]
    res = dict(m_n=len(m), m_median=pct(mv, .5), m_100k=sum(x >= 1e5 for x in mv), m_1m=sum(x >= 1e6 for x in mv), new_ch_100k=len(new100),
               t_ch=len(tch), t_lt1k=sum(r['subs'] < 1000 for r in tch), young=len(young), young_1k=sum(r['subs'] >= 1000 for r in young),
               young_10k=sum(r['subs'] >= 10000 for r in young), median_len=pct([r['mins'] for r in m + t], .5),
               new_examples=sorted([dict(ch=r['title'], age=r['age'], subs=r['subs'], views=r['views'], mins=r['mins']) for r in m
                                    if r['age'] is not None and r['age'] <= 365 and r['views'] >= 5e4], key=lambda x: -x['views'])[:5])
    out[name] = res
    L.append(f"| {name} | {res['m_n']} | {res['m_median'] / 1e3:,.0f}K | {res['m_100k']} | {res['m_1m']} | {res['new_ch_100k']} | {res['t_ch']} / "
             f"{res['t_lt1k']} | {res['young']} / {res['young_1k']} / {res['young_10k']} | {res['median_len']:.0f} m |")
L += ['', '## New-channel examples (created <= 365 d, video >= 50K this month)', '']
for name, r in out.items():
    if r['new_examples']:
        L.append(f"- **{name}**: " + '; '.join(f"{e['ch']} ({e['age']} d, {(e['subs'] or 0) / 1e3:,.1f}K subs) {e['views'] / 1e3:,.0f}K, {e['mins']} m"
                                              for e in r['new_examples']))
open(os.path.join(HERE, 'capability_scan.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
json.dump(out, open(os.path.join(HERE, 'capability_scan.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('\n'.join(L))
