"""Minecraft Shorts sub-niche scan (2026-11-13, owner: 1-2 long-form + 1-4 Shorts niches "kiếm nhiều tiền và nhanh").
Discovery: owner browser YouTube search with the Shorts type filter (relevance order, 3 queries x 2 pages per sub-niche),
2026-11-13 ~04:45Z. Enrichment: cf_mc_niche_enrich.py (official API videos.list + channels.list, <=120 units).
Relevance search favours successful Shorts, so this measures winners and channel ages, not failure rates. One reading.
Usage: python mc_shorts.py <folder with videos.json channels.json>
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

D = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Downloads/cine_niche_survey/out/2026-11-13_mc_shorts/'
HERE = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(D, 'videos.json'), encoding='utf-8'))
C = json.load(open(os.path.join(D, 'channels.json'), encoding='utf-8'))
IDS = json.load(open(os.path.join(D, 'ids.json')))
NOW = datetime(2026, 11, 13, 4, 45, tzinfo=timezone.utc)
IP = re.compile(r"\bjj\b|mikey|maizen|verity|sprunki|skibidi|labubu|poppy|huggy|siren head|cartoon cat|fnaf|freddy|sonic|pokemon|"
                r"spongebob|mario|garten|banban|dandy|doors|rainbow friends|smiling critters|catnap|brainrot|tralalero|tung tung", re.I)
NONEN = re.compile(r'[^\x00-\x7F‐-‧‰-⁞€™←-⇿⌀-➿⬀-⯿️\U0001F000-\U0001FFFF#]')
NAMES = dict(horror='Horror / scary', build='Build hacks / tips', redstone='Redstone / farms', battle='Mob battle / experiment',
             noobpro='Noob vs Pro / troll / "Minecraft but"', anim='Animation story', facts='Facts / myths / secrets',
             parkour='Parkour / satisfying / ASMR')


def ts(s):
    return datetime.fromisoformat(re.sub(r'\.\d+', '', s.replace('Z', '+00:00')))


def dur(d):
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d or '')
    if not m:
        return 0
    a = [int(x or 0) for x in m.groups()]
    return a[0] * 86400 + a[1] * 3600 + a[2] * 60 + a[3]


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return 0
    k = (len(xs) - 1) * q
    f = int(k)
    return xs[f] + (xs[min(f + 1, len(xs) - 1)] - xs[f]) * (k - f)


out = {}
L = ['# Minecraft Shorts sub-niches (mc_shorts.py, 2026-11-13)', '',
     'Shorts found by YouTube search (Shorts filter, relevance), exact numbers from videos.list/channels.list. English titles, <= 180 s. '
     'Relevance search over-samples winners: read as "what wins and who wins", not as failure rates.', '',
     '| Sub-niche | Shorts | Median views | >=1M | Posted <= 30 d: n / median | Channels | Channel age <= 365 d (share) | '
     'New ch (<=365 d) with a Short >=1M | Made for Kids | Third-party IP in title | Median channel subs |', '|' + '---|' * 11]
for code, name in NAMES.items():
    rows = []
    for x in IDS[code].split():
        v = V.get(x[:-1])
        if not v:
            continue
        sn = v['snippet']
        s = dur(v['contentDetails'].get('duration'))
        lang = (sn.get('defaultAudioLanguage') or sn.get('defaultLanguage') or '').lower()
        if s == 0 or s > 180 or (lang and not lang.startswith('en')) or NONEN.search(sn.get('title', '')):
            continue
        c = C.get(sn['channelId'], {})
        cs = c.get('statistics', {})
        rows.append(dict(views=int(v.get('statistics', {}).get('viewCount', 0)), age_d=(NOW - ts(sn['publishedAt'])).days,
                         mfk=bool(v.get('status', {}).get('madeForKids')), ip=bool(IP.search(sn.get('title', '') + ' ' + sn.get('channelTitle', ''))),
                         cid=sn['channelId'], ch=sn.get('channelTitle', ''), title=sn.get('title', '')[:60],
                         cage=(NOW - ts(c['snippet']['publishedAt'])).days if c else None,
                         subs=None if cs.get('hiddenSubscriberCount') else int(cs.get('subscriberCount', 0)),
                         cvid=int(cs.get('videoCount', 0)), cviews=int(cs.get('viewCount', 0))))
    if not rows:
        continue
    vs = [r['views'] for r in rows]
    rec = [r['views'] for r in rows if r['age_d'] <= 30]
    chs = {r['cid']: r for r in rows}
    young = [r for r in chs.values() if r['cage'] is not None and r['cage'] <= 365]
    new1m = {r['cid'] for r in rows if r['cage'] is not None and r['cage'] <= 365 and r['views'] >= 1e6}
    res = dict(n=len(rows), median=pct(vs, .5), m1=sum(x >= 1e6 for x in vs), recent_n=len(rec), recent_median=pct(rec, .5),
               channels=len(chs), young=len(young), new1m=len(new1m), mfk=sum(r['mfk'] for r in rows) / len(rows),
               ip=sum(r['ip'] for r in rows) / len(rows), med_subs=pct([r['subs'] or 0 for r in chs.values()], .5),
               young_examples=sorted([dict(ch=r['ch'], age=r['cage'], subs=r['subs'], videos=r['cvid'], ch_views=r['cviews'],
                                           best=max(x['views'] for x in rows if x['cid'] == r['cid'])) for r in young],
                                     key=lambda e: -e['best'])[:6])
    out[name] = res
    L.append(f"| {name} | {res['n']} | {res['median'] / 1e3:,.0f}K | {res['m1']} | {res['recent_n']} / {res['recent_median'] / 1e3:,.0f}K | "
             f"{res['channels']} | {res['young']} ({100 * res['young'] / res['channels']:.0f}%) | {res['new1m']} | {100 * res['mfk']:.0f}% | "
             f"{100 * res['ip']:.0f}% | {res['med_subs'] / 1e3:,.0f}K |")
L += ['', '## Young channels (created <= 365 d) in each sub-niche (best Short in sample)', '']
for name, r in out.items():
    L.append(f"- **{name}**: " + ('; '.join(f"{e['ch']} ({e['age']} d, {(e['subs'] or 0) / 1e3:,.0f}K subs, {e['videos']} videos, "
                                           f"{e['ch_views'] / 1e6:,.1f}M channel views, best {e['best'] / 1e6:,.2f}M)" for e in r['young_examples'])
                                 or 'none'))
open(os.path.join(HERE, 'mc_shorts.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
json.dump(out, open(os.path.join(HERE, 'mc_shorts.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('\n'.join(L))
