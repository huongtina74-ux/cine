"""Success vs failure of Minecraft creators per sub-niche (2026-11-12, owner: "xem các kênh thành công và các kênh thất bại").

Sample (survivorship-light): YouTube search in the owner's browser 2026-11-11 ~17:20Z, 7 sub-niches x 6 'minecraft ...' queries,
filters 'today' (2 pages) + 'this week' (1 page). 'Today' uploads include channels with 0-50 views, so failing creators are in.
Per-channel row (cr1.txt + cr2.txt, built in the browser, deduped by niche+video):
  idx, niches (h horror, s survival, a machinima/animation, c challenge, y mystery, e engineering, l lore), sample videos,
  English-title videos, Minecraft-word videos, long (>=8 min) videos, median views, max views, median long views, median length s.
Channel stats: channels.list (17 API units, enrich_meta.json). No other API calls. Views/subs are one reading.
Usage: python sf_study.py <folder with channels.json channels.txt cr1.txt cr2.txt fresh_stats.json>
"""
import json
import math
import os
import re
import statistics as st
import sys
from datetime import datetime, timezone

D = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Downloads/cine_niche_survey/out/2026-11-12_failure_sample/'
HERE = os.path.dirname(os.path.abspath(__file__))
NOW = datetime(2026, 11, 11, 17, 36, tzinfo=timezone.utc)
C = json.load(open(os.path.join(D, 'channels.json'), encoding='utf-8'))
IDS = ['UC' + x for x in open(os.path.join(D, 'channels.txt'), encoding='utf-8').read().split()]
FRESH = json.load(open(os.path.join(D, 'fresh_stats.json'), encoding='utf-8'))
NAMES = dict(h='HORROR', s='SURVIVAL_100DAYS', a='MACHINIMA', c='CHALLENGE', y='MYSTERY', e='ENGINEERING', l='LORE')
FRESH_KEY = dict(h='horror', s='survival', a='machinima', c='challenge', y='mystery', e='engineering', l='lore')
# AGG-EST per-1,000-views revenue ranges (research_notes/.../rpm_economics.md; gaming median $2.05 MEASURED, kids $0.33 MEASURED).
RPM = dict(h=(1.5, 3.5), s=(2.0, 4.0), a=(0.5, 2.0), c=(2.0, 4.0), y=(0.7, 3.6), e=(2.0, 5.0), l=(3.0, 6.0))
NONEN = re.compile(r'[^\x00-\x7F‐-‧‰-⁞€™←-⇿⌀-➿⬀-⯿️\U0001F000-\U0001FFFF]')
FOREIGN = re.compile(r'\b(de|que|con|para|em|uma|und|der|die|das|il|di|na|sa|ng|dan|yang|ve|bir|nie|jak|het|een|cu|mundo|dias|días|'
                     r'hari|gün|dni|tage|jours|giorni|ngày|español|brasil|türkçe|indonesia|tiếng|русск)\b', re.I)

rows = []
for part in ('cr1.txt', 'cr2.txt'):
    for r in open(os.path.join(D, part), encoding='utf-8').read().strip().strip(';').split(';'):
        a = r.split(',')
        rows.append(dict(i=int(a[0]), niches=a[1], k=int(a[2]), en=int(a[3]), mc=int(a[4]), nlong=int(a[5]),
                         med=int(a[6] or 0), mx=int(a[7] or 0), medlong=int(a[8]) if a[8] else None, medlen=int(a[9] or 0)))


def ts(s):
    return datetime.fromisoformat(re.sub(r'\.\d+', '', s.replace('Z', '+00:00')))


def wilson(k, n, z=1.96):
    if not n:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * q
    f = int(k)
    return xs[f] + (xs[min(f + 1, len(xs) - 1)] - xs[f]) * (k - f)


chan = []
for r in rows:
    cid = IDS[r['i']]
    c = C.get(cid)
    if not c:
        continue
    sn, s = c['snippet'], c['statistics']
    desc = (sn.get('title', '') + ' ' + sn.get('description', ''))
    age = max(1, (NOW - ts(sn['publishedAt'])).days)
    subs = int(s['subscriberCount']) if not s.get('hiddenSubscriberCount') and 'subscriberCount' in s else None
    vc, vv = int(s.get('videoCount', 0)), int(s.get('viewCount', 0))
    en_ok = r['en'] >= max(1, math.ceil(r['k'] / 2)) and not FOREIGN.search(sn.get('title', '')) and \
        (sn.get('country') in (None, 'US', 'GB', 'CA', 'AU', 'NZ', 'IE') or r['en'] == r['k'])
    mc_ok = r['mc'] >= 1 or 'minecraft' in desc.lower()
    chan.append(dict(r, cid=cid, title=sn.get('title', ''), country=sn.get('country'), age=age, subs=subs, vc=vc, vv=vv,
                     avg=vv / vc if vc else 0, vpd=vv / age, upw=vc / (age / 7), en_ok=en_ok, mc_ok=mc_ok,
                     longform=r['nlong'] >= 1, created=sn['publishedAt'][:10]))

# Spin-offs of established creators (OBSERVED from channel names) and localized re-uploads are not new entrants.
SPINOFF = re.compile(r'top videos|craftee too|omz plays|cashclips|mrdru lab', re.I)
for c in chan:
    c['spinoff'] = bool(SPINOFF.search(c['title']))
U = [c for c in chan if c['en_ok'] and c['mc_ok'] and c['subs'] is not None and not c['spinoff']]
out = dict(meta=dict(channels_in_sample=len(rows), channels_with_api=len(chan), english_minecraft=len(U),
                     hidden_subs=sum(1 for c in chan if c['subs'] is None)), niches={})
L = ['# Success vs failure of Minecraft creators by sub-niche (sf_study.py, 2026-11-12)', '',
     f"Sample: {len(rows)} channels uploading in 7 Minecraft sub-niches (YouTube search 'today' + 'this week', 2026-11-11 ~17:20Z); "
     f"{len(chan)} returned by channels.list (17 units); {len(U)} English + Minecraft + public subs, excluding "
     f"{sum(c['spinoff'] for c in chan)} spin-off/localized channels of established creators. A channel can sit in several "
     'sub-niches. All numbers OBSERVED (one reading) unless marked INFERRED/AGG-EST. Channel age = channel creation date, '
     'which can predate the niche (repurposed channels).', '']
TIERS = [(1_000, '>=1K'), (10_000, '>=10K'), (100_000, '>=100K'), (1_000_000, '>=1M')]


def block(code, g, label):
    n = len(g)
    res = dict(n=n)
    if not n:
        return res, f'| {label} | 0 |' + ' |' * 9
    for t, name in TIERS:
        k = sum(c['subs'] >= t for c in g)
        res[name] = k
    res['lt1k'] = n - res['>=1K']
    res['med_subs'] = pct([c['subs'] for c in g], .5)
    res['med_avg_views'] = pct([c['avg'] for c in g], .5)
    res['med_vpd'] = pct([c['vpd'] for c in g], .5)
    lo, hi = wilson(res['>=10K'], n)
    return res, (f"| {label} | {n} | {res['lt1k']} ({100 * res['lt1k'] / n:.0f}%) | {res['>=1K']} | {res['>=10K']} "
                 f"({100 * res['>=10K'] / n:.0f}%, CI {100 * lo:.0f}-{100 * hi:.0f}%) | {res['>=100K']} | {res['>=1M']} | "
                 f"{res['med_subs']:,.0f} | {res['med_avg_views']:,.0f} | {res['med_vpd']:,.0f} |")


for code, name in NAMES.items():
    g_all = [c for c in U if code in c['niches']]
    g_long = [c for c in g_all if c['longform']]
    young = [c for c in g_long if c['age'] <= 365]
    mid = [c for c in g_long if 365 < c['age'] <= 1095]
    old = [c for c in g_long if c['age'] > 1095]
    L += [f'## {name}', '', '| Cohort (long-form uploaders) | Channels | <1K subs (fail) | >=1K | >=10K | >=100K | >=1M | '
          'Median subs | Median lifetime views/video | Median views/day of channel life |', '|' + '---|' * 10]
    res = {}
    for lab, g in (('all long-form', g_long), ('channel <=365 d', young), ('1-3 y', mid), ('>3 y', old)):
        r_, line = block(code, g, lab)
        res[lab] = r_
        L.append(line)
    # winners vs losers among long-form channels <= 3 y old
    yg = [c for c in g_long if c['age'] <= 1095]
    win = [c for c in yg if c['subs'] >= 10_000]
    lose = [c for c in yg if c['subs'] < 1_000]

    def prof(g):
        if not g:
            return dict(n=0)
        return dict(n=len(g), med_videos=pct([c['vc'] for c in g], .5), med_uploads_week=pct([c['upw'] for c in g], .5),
                    med_len_min=pct([c['medlen'] / 60 for c in g], .5), med_age_d=pct([c['age'] for c in g], .5),
                    med_sample_views=pct([c['med'] for c in g], .5))
    pw, pl = prof(win), prof(lose)
    res['winners_<=3y'] = pw
    res['losers_<=3y'] = pl
    L += ['', f'Winners (>=10K subs) vs losers (<1K) among long-form channels <= 3 y: '
          f"winners n={pw['n']}" + (f", median {pw['med_videos']:.0f} videos, {pw['med_uploads_week']:.1f} uploads/week, "
                                    f"{pw['med_len_min']:.0f} min, age {pw['med_age_d']:.0f} d, sample-video median "
                                    f"{pw['med_sample_views']:,.0f} views" if pw['n'] else '') +
          f"; losers n={pl['n']}" + (f", median {pl['med_videos']:.0f} videos, {pl['med_uploads_week']:.1f} uploads/week, "
                                     f"{pl['med_len_min']:.0f} min, age {pl['med_age_d']:.0f} d, sample-video median "
                                     f"{pl['med_sample_views']:,.0f} views" if pl['n'] else '') + '.']
    # expected money (INFERRED): probability tiers from long-form channels <= 3 y; monthly views per tier from same channels
    base = [c for c in g_long if c['age'] <= 1095]
    bands = [(0, 1_000), (1_000, 10_000), (10_000, 100_000), (100_000, 1e12)]
    ev_lo = ev_hi = 0
    parts = []
    for lo_, hi_ in bands:
        g = [c for c in base if lo_ <= c['subs'] < hi_]
        p = len(g) / len(base) if base else 0
        mv = pct([c['vpd'] * 30 for c in g], .5) or 0
        paid = lo_ >= 1_000  # YPP needs >= 1K subs (+ watch hours); INFERRED that >=1K long-form channels qualify
        if paid:
            ev_lo += p * mv / 1000 * RPM[code][0]
            ev_hi += p * mv / 1000 * RPM[code][1]
        parts.append(dict(band=f'{lo_:,.0f}-{hi_:,.0f}', n=len(g), p=round(p, 3), median_monthly_views=round(mv)))
    res['money'] = dict(rpm_range=RPM[code], bands=parts, expected_monthly_usd=(round(ev_lo), round(ev_hi)), base_n=len(base))
    L += ['', f"Expected money for a long-form channel <= 3 y (INFERRED = share of channels in each subscriber band x that band's "
          f"median monthly views x AGG-EST RPM ${RPM[code][0]}-{RPM[code][1]}; <1K band earns $0): n={len(base)}; bands " +
          '; '.join(f"{b['band']}: {b['n']} ch, {100 * b['p']:.0f}%, {b['median_monthly_views']:,.0f} views/mo" for b in parts) +
          f" -> **${ev_lo:,.0f}-{ev_hi:,.0f} per month per channel** (mean, dominated by the few winners).", '']
    f = FRESH.get(FRESH_KEY[code], {})
    res['fresh'] = f
    if f:
        L += [f"New uploads <= 48 h (English, >= 8 min, search-ranked): n={f['n']}, median {f['medViews']:,} views, P75 {f['p75']:,}, "
              f"P90 {f['p90']:,}, median {f['medVph']} views/hour, {f['ge1k']}/{f['n']} >= 1K, {f['lt100']}/{f['n']} < 100, "
              f"median {f['medLenMin']} min.", '']
    # named examples
    ex_w = sorted([c for c in young if c['subs'] >= 10_000], key=lambda c: -c['subs'])[:6]
    ex_l = sorted([c for c in young if c['subs'] < 1_000], key=lambda c: -c['vc'])[:4]
    if ex_w:
        L.append('Young winners: ' + '; '.join(f"{c['title'].strip()} ({c['created']}, {c['subs'] / 1e3:,.1f}K subs, {c['vc']} videos, "
                                              f"{c['avg'] / 1e3:,.1f}K views/video)" for c in ex_w) + '.')
    if ex_l:
        L.append('Young strugglers (most uploads, still <1K subs): ' + '; '.join(
            f"{c['title'].strip()} ({c['created']}, {c['subs']} subs, {c['vc']} videos, {c['avg']:,.0f} views/video)" for c in ex_l) + '.')
    L.append('')
    out['niches'][name] = res

# cross-niche summary
L += ['## Summary (long-form channels, English, Minecraft)', '',
      '| Sub-niche | Channels | Fail <1K | >=10K | <=365 d: n / >=10K | Exp. $/month (<=3 y, INFERRED) | Fresh upload median views (48 h) |',
      '|---|---|---|---|---|---|---|']
for code, name in NAMES.items():
    r = out['niches'][name]
    a, y = r['all long-form'], r['channel <=365 d']
    if not a.get('n'):
        continue
    L.append(f"| {name} | {a['n']} | {100 * a['lt1k'] / a['n']:.0f}% | {100 * a['>=10K'] / a['n']:.0f}% | {y.get('n', 0)} / "
             f"{y.get('>=10K', 0)} | ${r['money']['expected_monthly_usd'][0]:,}-{r['money']['expected_monthly_usd'][1]:,} "
             f"(n={r['money']['base_n']}) | {r['fresh'].get('medViews', 0):,} |")
# cross-niche winner/loser profile (long-form, <= 3 y)
LOWPROD = {'IN', 'PH', 'VN', 'BD', 'PK', 'ID', 'BR', 'NP'}
pool = {c['cid']: c for c in U if c['longform'] and c['age'] <= 1095}.values()
W = [c for c in pool if c['subs'] >= 10_000]
Lz = [c for c in pool if c['subs'] < 1_000]
M = [c for c in pool if 1_000 <= c['subs'] < 10_000]


def prof2(g):
    return (f"n={len(g)}, median {pct([c['vc'] for c in g], .5):.0f} videos, {pct([c['upw'] for c in g], .5):.1f} uploads/week, "
            f"sample-video median length {pct([c['medlen'] / 60 for c in g], .5):.0f} min, "
            f"{sum(c['medlen'] >= 3600 for c in g)} with >= 60-min videos, "
            f"{sum((c['country'] or '') in LOWPROD for c in g)} registered in IN/PH/VN/BD/PK/ID/BR/NP, "
            f"{sum(c['country'] is None for c in g)} no country, median lifetime views/video {pct([c['avg'] for c in g], .5):,.0f}")


young_all = [c for c in pool if c['age'] <= 365]
L += ['', '## Cross-niche: what separates winners from losers (long-form, channel <= 3 y, unique channels)', '',
      f'- Winners >= 10K subs: {prof2(W)}.', f'- Middle 1K-10K: {prof2(M)}.', f'- Losers < 1K: {prof2(Lz)}.',
      f"- New entrants (channel <= 365 d, any niche): {len(young_all)} channels; >= 1K subs {sum(c['subs'] >= 1_000 for c in young_all)}, "
      f">= 10K {sum(c['subs'] >= 10_000 for c in young_all)}, >= 100K {sum(c['subs'] >= 100_000 for c in young_all)} "
      f"(Wilson 95% CI for >= 10K: {100 * wilson(sum(c['subs'] >= 10_000 for c in young_all), len(young_all))[0]:.0f}-"
      f"{100 * wilson(sum(c['subs'] >= 10_000 for c in young_all), len(young_all))[1]:.0f}%).", '']
out['cross'] = dict(winners=len(W), middle=len(M), losers=len(Lz), young=len(young_all))
open(os.path.join(HERE, 'sf_study.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
json.dump(out, open(os.path.join(HERE, 'sf_study.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=str)
json.dump([{k: c[k] for k in ('cid', 'title', 'spinoff', 'niches', 'created', 'age', 'subs', 'vc', 'vv', 'country', 'nlong', 'med', 'medlen',
                               'en_ok', 'mc_ok')} for c in chan], open(os.path.join(HERE, 'sf_channels.json'), 'w', encoding='utf-8'),
          indent=0, ensure_ascii=False)
print('\n'.join(L))
