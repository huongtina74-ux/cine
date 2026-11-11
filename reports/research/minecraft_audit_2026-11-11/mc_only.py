"""Minecraft-only reassessment (2026-11-11, owner scope lock). Reuses classified_videos.json (classify.py) and the read-only
dataset copy; drops A3 (independent 2D animation) and A9 (non-Minecraft). Splits Minecraft into sub-niches, flags third-party IP,
runs the required sensitivity cuts and an outlier-removal check. Writes mc_only.md + mc_only.json. No API calls.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

DATA = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Downloads/cine_niche_survey/out/2026-11-11_niche_compare/'
HERE = os.path.dirname(os.path.abspath(__file__))
V = json.load(open(os.path.join(HERE, 'classified_videos.json')))
U = json.load(open(os.path.join(DATA, 'uploads.json')))
C = json.load(open(os.path.join(DATA, 'channels.json')))
NOW = datetime(2026, 11, 11, 15, 31, tzinfo=timezone.utc)

IP = re.compile(r"\bjj\b|jj's|mikey|maizen|verity|lovity|technoblade|\bdream\b|sakadung|labubu|sprunki|skibidi|poppy|huggy|jerry|godzilla|"
                r"cat in the hat|talking tom|kpop|k-pop|demon hunter|ishowspeed|ronaldo|paw patrol|spongebob|sonic|naruto|pokemon|pokémon|"
                r"freddy|fnaf|banban|thatmob|wemmbu|parrot|spoke|chocho|choo choo|charles|angela|talking", re.I)
SIM = re.compile(r"\bvs\.?\b|army|armies|battle|simulat|which .*surviv|who will|experiment|tnt|\d[\d,]* (mobs|zombies|wardens|villagers)", re.I)
MULTI = re.compile(r"players? simulate|player (minecraft )?war|\bsmp\b|manhunt|hunters|speedrun|hackers vs|murder run|qsmp|civilization", re.I)
HORROR = re.compile(r"horror|scary|terrif|creepy|haunt|curse|dark origin|hunting|alive|nightmare|entity|ghost|monster", re.I)


def sub(v):
    p, t, tags = v['primary_format'], v['title'], v['secondary_tags']
    ip = bool(IP.search(t + ' ' + v['channel']))
    if p == 'A2':
        return ('MACHINIMA_IP' if ip else ('MACHINIMA_HORROR_ORIG' if HORROR.search(t) else 'MACHINIMA_ORIG')), ip
    if p == 'A5':
        return 'HORROR_MOD', ip
    if p == 'A6':
        return 'MYSTERY_ARG', ip
    if p == 'A8':
        return 'LORE_DOC', ip
    if p in ('A1', 'A7'):
        if MULTI.search(t):
            return 'MULTIPLAYER_EVENT', ip
        if SIM.search(t) and not re.search(r"redstone|create mod|piston|door|farm", t, re.I):
            return 'SIM_BATTLE_EXPERIMENT', ip
        if p == 'A7':
            return 'ENGINEERING', ip
        if 'apocalypse_survival' in tags:
            return 'SURVIVAL_100DAYS', ip
        return 'CHALLENGE_CONCEPT', ip
    return None, ip


def ts(s):
    return datetime.fromisoformat(re.sub(r'\.\d+', '', s.replace('Z', '+00:00')))


def dur(d):
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d or '')
    a = [int(x or 0) for x in m.groups()]
    return a[0] * 86400 + a[1] * 3600 + a[2] * 60 + a[3]


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return 0
    k = (len(xs) - 1) * q
    f = int(k)
    return xs[f] + (xs[min(f + 1, len(xs) - 1)] - xs[f]) * (k - f)


def ch_age(cid):
    return (NOW - ts(C[cid]['snippet']['publishedAt'])).days


def long_hits(cid):
    vids = {v['video_id']: v['views'] for v in V if v['channel_id'] == cid and v['duration_s'] >= 480}
    for u in U.get(cid, []):
        if dur(u['dur']) >= 480:
            vids[u['id']] = u['views']
    return list(vids.values())


MC = []
for v in V:
    s, ip = sub(v)
    if s and v['english'] and v['duration_s'] >= 480:
        MC.append(dict(v, sub=s, ip=ip))
ORDER = ['SURVIVAL_100DAYS', 'CHALLENGE_CONCEPT', 'MULTIPLAYER_EVENT', 'SIM_BATTLE_EXPERIMENT', 'HORROR_MOD', 'MACHINIMA_IP',
         'MACHINIMA_ORIG', 'MACHINIMA_HORROR_ORIG', 'MYSTERY_ARG', 'ENGINEERING', 'LORE_DOC']
CUTS = [('all', lambda v: True), ('subs<1M', lambda v: v['channel_subs'] < 1_000_000), ('subs<100K', lambda v: v['channel_subs'] < 100_000),
        ('channel<=365d', lambda v: ch_age(v['channel_id']) <= 365), ('channel<=90d', lambda v: ch_age(v['channel_id']) <= 90)]
out, lines = {}, ['# Minecraft-only metrics (mc_only.py)', '',
                  'Universe: English, >= 8 min, primary_format in A1/A2/A5/A6/A7/A8 (A3 independent 2D and A9 non-Minecraft removed).',
                  f'Videos: {len(MC)}; channels: {len({v["channel_id"] for v in MC})}. Views are one reading (2026-11-11 15:31Z). '
                  'Shares are of THIS search sample, not success probabilities.', '']
for cut, f in CUTS:
    lines += [f'## Cut: {cut}', '', '| Sub-niche | Videos | Channels | Median | P75 | P90 | >=1M (n/N) | IP share | Median min | '
              'Ch <=30/90/365 d | Emerging ch >=100K | >=1M | repeat >=3x100K | >=1M from >1M-sub ch | Median w/o top channel |', '|' + '---|' * 15]
    for s in ORDER:
        g = [v for v in MC if v['sub'] == s and f(v)]
        if not g:
            lines.append(f'| {s} | 0 |' + ' |' * 13)
            continue
        vs = [v['views'] for v in g]
        chs = {v['channel_id'] for v in g}
        ages = {c: ch_age(c) for c in chs}
        emerg = [c for c in chs if ages[c] <= 365]
        h100 = [c for c in emerg if any(x >= 1e5 for x in long_hits(c))]
        h1m = [c for c in emerg if any(x >= 1e6 for x in long_hits(c))]
        rep = [c for c in emerg if sum(x >= 1e5 for x in long_hits(c)) >= 3]
        m1 = [v for v in g if v['views'] >= 1e6]
        big = sum(1 for v in m1 if v['channel_subs'] > 1_000_000)
        top = max(chs, key=lambda c: sum(v['views'] for v in g if v['channel_id'] == c))
        rest = [v['views'] for v in g if v['channel_id'] != top]
        row = dict(n=len(g), ch=len(chs), med=pct(vs, .5), p75=pct(vs, .75), p90=pct(vs, .9), m1=len(m1),
                   ip=sum(v['ip'] for v in g) / len(g), emerg100=len(h100), emerg1m=len(h1m), rep=len(rep), big=big,
                   med_wo_top=pct(rest, .5) if rest else 0, top=C[top]['snippet']['title'])
        out.setdefault(cut, {})[s] = row
        lines.append(f"| {s} | {len(g)} | {len(chs)} | {row['med'] / 1e3:,.0f}K | {row['p75'] / 1e3:,.0f}K | {row['p90'] / 1e3:,.0f}K | "
                     f"{len(m1)}/{len(g)} | {100 * row['ip']:.0f}% | {pct([v['duration_s'] for v in g], .5) / 60:.0f} | "
                     f"{sum(a <= 30 for a in ages.values())}/{sum(a <= 90 for a in ages.values())}/{len(emerg)} | {len(h100)} | {len(h1m)} | "
                     f"{len(rep)} | {big}/{len(m1)} | {row['med_wo_top'] / 1e3:,.0f}K (top: {row['top'][:18]}) |")
    lines.append('')
# emerging-creator list (channel <= 365 d, any long >= 100K), Minecraft only
lines += ['## Emerging Minecraft channels (created <= 365 d) with a >= 8-min video >= 100K (sample + uploads)', '',
          '| Channel | Sub-niche | IP | Created | Age | Subs | Videos | Long >=100K | Long >=1M | Best (views, min, published, age at publish) |',
          '|---|---|---|---|---|---|---|---|---|---|']
seen = set()
for v in sorted(MC, key=lambda v: -max(long_hits(v['channel_id']) or [0])):
    c = v['channel_id']
    if c in seen or ch_age(c) > 365:
        continue
    seen.add(c)
    hits = long_hits(c)
    if not any(x >= 1e5 for x in hits):
        continue
    best = max([x for x in V if x['channel_id'] == c], key=lambda x: x['views'])
    up = [u for u in U.get(c, []) if dur(u['dur']) >= 480]
    if up:
        bu = max(up, key=lambda u: u['views'])
        if bu['views'] > best['views']:
            best = dict(video_id=bu['id'], views=bu['views'], duration_s=dur(bu['dur']), published=bu['pub'],
                        channel_age_at_publish_days=(ts(bu['pub']) - ts(C[c]['snippet']['publishedAt'])).days)
    st = C[c]['statistics']
    lines.append(f"| [{C[c]['snippet']['title'].strip()}](https://www.youtube.com/channel/{c}) | {v['sub']} | {'yes' if v['ip'] else 'no'} | "
                 f"{C[c]['snippet']['publishedAt'][:10]} | {ch_age(c)} d | {int(st.get('subscriberCount', 0)) / 1e3:.1f}K | {st.get('videoCount')} | "
                 f"{sum(x >= 1e5 for x in hits)} | {sum(x >= 1e6 for x in hits)} | [{best['views'] / 1e3:,.0f}K](https://youtu.be/{best['video_id']}), "
                 f"{best['duration_s'] // 60} m, {best['published'][:10]}, d{int(best['channel_age_at_publish_days'])} |")
open(os.path.join(HERE, 'mc_only.md'), 'w').write('\n'.join(lines) + '\n')
json.dump(out, open(os.path.join(HERE, 'mc_only.json'), 'w'), indent=1, ensure_ascii=False)
print('\n'.join(lines))
