"""Whole-YouTube faceless niche ranking (2026-11-12). Input: output of cf_youtube_wide_scan.py (official API only, ~9K units):
per niche 2x search order=viewCount last 30 d (long>20m / medium 4-20m) and 2x search order=date last 48 h (long / medium);
videos.list + channels.list for every id. Universe: English, >= 8 min, not live. All counts OBSERVED (one reading) unless
labelled. RPM ranges: MEASURED class medians (AIR Media-Tech 2026, 300 channels) or practitioner/INFERRED (see RPM_NOTE).
Usage: python wide_scan.py <folder with hits.json videos.json channels.json meta.json>
"""
import json
import math
import os
import re
import statistics as st
import sys
from datetime import datetime, timezone

D = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/Downloads/cine_niche_survey/out/2026-11-12_wide_scan/'
HERE = os.path.dirname(os.path.abspath(__file__))
H = json.load(open(os.path.join(D, 'hits.json')))
V = json.load(open(os.path.join(D, 'videos.json'), encoding='utf-8'))
C = json.load(open(os.path.join(D, 'channels.json'), encoding='utf-8'))
META = json.load(open(os.path.join(D, 'meta.json')))
NOW = datetime.fromisoformat(META['fetched_at'])
# (low, base, high) USD per 1,000 views and evidence label
RPM = {
    'history_doc': (4, 10, 19.5, 'MEASURED class Education $10.22 (P25-P75 2.31-19.50)'),
    'history_sleep': (8, 15, 35, 'Education class + practitioner multi-hour sleep $30-40'),
    'senior_family_drama': (3, 8, 13, 'Entertainment $2.43 MEASURED class; revenge narration $8-13 AGG-EST'),
    'senior_western_heartwarming': (8, 16, 28, 'practitioner: romance older women $16-28, western $16-22'),
    'sleep_fiction': (8, 20, 40, 'practitioner: sleep stories ~$20, multi-hour $30-40'),
    'bible_stories': (4, 8, 18, 'AGG-EST $8-18 (Fluxnote), seasonal +50-100%'),
    'slow_english': (0.5, 1.5, 3, 'INFERRED from learner geography (Tier-3 countries $0.3-1.5)'),
    'disaster_doc': (2, 4, 10, 'News $2.60 / Education class (INFERRED mapping)'),
    'true_crime': (2, 4, 8, 'Entertainment class (INFERRED)'),
    'space_science': (4, 10, 19.5, 'Education class MEASURED'),
    'geopolitics': (2.5, 6, 12, 'News/Education (INFERRED)'),
    'business_doc': (2, 5, 10, 'Business $2.01 MEASURED n=3; AGG-EST higher'),
    'personal_finance': (2, 8, 20, 'Business $2.01 MEASURED n=3; AGG-EST $8-22'),
    'psychology_stoic': (2, 4, 8, 'Education/Lifestyle (INFERRED)'),
    'tech_ai': (2.3, 4, 8, 'Tech $2.33 MEASURED class'),
    'ww2_military': (4, 8, 15, 'Education/history, older male audience (INFERRED)'),
    'nature_wildlife': (3, 6, 10, 'Education-like, global audience (INFERRED)'),
    'transport_doc': (3, 5.69, 10, 'Transport $5.69 MEASURED (small n)'),
    'reddit_stories': (1.5, 3, 6, 'Entertainment (INFERRED); reused-content risk'),
    'minecraft_horror': (1, 2.05, 3.5, 'Gaming $2.05 MEASURED'),
    'kids_animation': (0.2, 0.33, 1, 'Kids & Teens $0.33 MEASURED'),
    'ambient_music': (1, 2.28, 4, 'Music $2.28 MEASURED'),
}
NONEN = re.compile(r'[^\x00-\x7F‐-‧‰-⁞€™←-⇿⌀-➿⬀-⯿️\U0001F000-\U0001FFFF]')
FOREIGN = re.compile(r'\b(de|que|con|para|em|uma|und|der|die|das|il|di|na|sa|ng|dan|yang|ve|bir|nie|jak|het|een|mundo|historia|'
                     r'geschichte|histoire|storia|hindi|tamil|telugu|urdu|bangla|kahani|kahaniya)\b', re.I)


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


def wilson(k, n, z=1.96):
    if not n:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0, c - h), min(1, c + h))


def english(v):
    sn = v['snippet']
    lang = (sn.get('defaultAudioLanguage') or sn.get('defaultLanguage') or '').lower()
    if lang and not lang.startswith('en'):
        return False
    t = sn.get('title', '')
    return not NONEN.search(t) and not FOREIGN.search(t)


def row(vid):
    v = V.get(vid)
    if not v:
        return None
    sn, s = v['snippet'], v.get('statistics', {})
    if sn.get('liveBroadcastContent') not in (None, 'none'):
        return None
    secs = dur(v['contentDetails'].get('duration'))
    cid = sn['channelId']
    c = C.get(cid, {})
    cs = c.get('statistics', {})
    cage = (NOW - ts(c['snippet']['publishedAt'])).days if c else None
    subs = None if cs.get('hiddenSubscriberCount') or 'subscriberCount' not in cs else int(cs['subscriberCount'])
    return dict(id=vid, title=sn.get('title', ''), cid=cid, ch=sn.get('channelTitle', ''), views=int(s.get('viewCount', 0)),
                secs=secs, pub=sn['publishedAt'], age_h=(NOW - ts(sn['publishedAt'])).total_seconds() / 3600,
                mfk=bool(v.get('status', {}).get('madeForKids')), en=english(v), cage=cage, subs=subs,
                cviews=int(cs.get('viewCount', 0)), cvc=int(cs.get('videoCount', 0)), country=c.get('snippet', {}).get('country') if c else None,
                created=c['snippet']['publishedAt'][:10] if c else None)


out = dict(meta=META, niches={})
L = ['# Whole-YouTube faceless niche scan (wide_scan.py, 2026-11-12)', '',
     f"Official YouTube Data API v3 only ({META['units']} units, {META['fetched_at'][:16]}Z). 22 niches x 4 searches "
     "(top by views last 30 d: one long >20 min + one medium 4-20 min query; newest uploads last 48 h: long + medium). "
     f"{META['videos']} videos, {META['channels']} channels. Universe: English (language tag/title heuristic), >= 8 min, not live. "
     "Views/subs = one reading. RPM: MEASURED class medians or practitioner/INFERRED (column 'RPM evidence').", '']
rows_all = []
for n, h in H.items():
    month = [r for r in (row(x) for x in h.get('month_long', []) + h.get('month_medium', [])) if r and r['en'] and r['secs'] >= 480]
    fresh = [r for r in (row(x) for x in h.get('fresh_long', []) + h.get('fresh_medium', [])) if r and r['en'] and r['secs'] >= 480]
    month = list({r['id']: r for r in month}.values())
    fresh = list({r['id']: r for r in fresh}.values())
    mv = [r['views'] for r in month]
    newm = {r['cid'] for r in month if r['cage'] is not None and r['cage'] <= 365 and r['views'] >= 100_000}
    newm1 = {r['cid'] for r in month if r['cage'] is not None and r['cage'] <= 365 and r['views'] >= 1_000_000}
    small_med = pct([r['views'] for r in month if r['subs'] is not None and r['subs'] < 100_000], .5)
    # fresh uploaders = everyone posting a long video in the last 48 h (failures included)
    fch = {}
    for r in fresh:
        if r['subs'] is not None and r['cage'] is not None:
            fch[r['cid']] = r
    fc = list(fch.values())
    young = [r for r in fc if r['cage'] <= 365]
    yk1 = sum(r['subs'] >= 1_000 for r in young)
    yk10 = sum(r['subs'] >= 10_000 for r in young)
    yk100 = sum(r['subs'] >= 100_000 for r in young)
    # monthly channel views (lifetime views / age) for young channels -> money with RPM base; <1K subs earns 0 (not in YPP)
    lo, base, hi, note = RPM[n]
    vmo = [r['cviews'] / max(r['cage'], 1) * 30 for r in young]
    paid = [r['cviews'] / max(r['cage'], 1) * 30 if r['subs'] >= 1_000 else 0 for r in young]
    exp_base = st.mean(paid) / 1000 * base if paid else 0
    p75_ch = pct([x for x, r in zip(vmo, young) if r['subs'] >= 1_000], .75) if yk1 else 0
    res = dict(month_n=len(month), month_median=pct(mv, .5), month_p75=pct(mv, .75), month_1m=sum(x >= 1e6 for x in mv),
               month_sum=sum(mv), small_median=small_med, new_ch_100k=len(newm), new_ch_1m=len(newm1),
               median_len_min=pct([r['secs'] / 60 for r in month + fresh], .5), mfk_share=(sum(r['mfk'] for r in month + fresh) /
                                                                                        max(1, len(month + fresh))),
               fresh_videos=len(fresh), fresh_channels=len(fc), fresh_lt1k=sum(r['subs'] < 1_000 for r in fc), young=len(young),
               young_1k=yk1, young_10k=yk10, young_100k=yk100, young_10k_ci=wilson(yk10, len(young)),
               young_median_vmo=pct(vmo, .5), paid_p75_vmo=p75_ch, rpm=(lo, base, hi), rpm_note=note,
               exp_month_usd_base=exp_base, exp_month_usd_range=(exp_base / base * lo if base else 0, exp_base / base * hi if base else 0),
               fresh_median_views=pct([r['views'] for r in fresh], .5), fresh_median_age_h=pct([r['age_h'] for r in fresh], .5))
    res['examples_new'] = sorted([dict(ch=r['ch'], created=r['created'], subs=r['subs'], views=r['views'], min=round(r['secs'] / 60),
                                       title=r['title'][:70]) for r in month if r['cage'] is not None and r['cage'] <= 365],
                                 key=lambda x: -x['views'])[:5]
    out['niches'][n] = res
    rows_all.append((n, res))

L += ['## Ranking table (sorted by expected $/month for a NEW channel, base RPM, INFERRED)', '',
      '| Niche | Top-30d median views | <100K-sub median | Top-30d videos >=1M | New ch (<=365 d) w/ video >=100K / >=1M | Median min | MFK share | '
      'Uploaders 48 h: ch / <1K subs | Young ch: n / >=1K / >=10K | Young paid ch P75 views/mo | RPM low-base-high | Exp. $/mo per new ch (base, range) |',
      '|' + '---|' * 12]
for n, r in sorted(rows_all, key=lambda x: -x[1]['exp_month_usd_base']):
    L.append(f"| {n} | {r['month_median'] / 1e3:,.0f}K | {r['small_median'] / 1e3:,.0f}K | {r['month_1m']}/{r['month_n']} | "
             f"{r['new_ch_100k']} / {r['new_ch_1m']} | {r['median_len_min']:.0f} | {100 * r['mfk_share']:.0f}% | {r['fresh_channels']} / "
             f"{r['fresh_lt1k']} | {r['young']} / {r['young_1k']} / {r['young_10k']} | {r['paid_p75_vmo'] / 1e3:,.0f}K | "
             f"${r['rpm'][0]}-{r['rpm'][1]}-{r['rpm'][2]} | ${r['exp_month_usd_base']:,.0f} (${r['exp_month_usd_range'][0]:,.0f}-"
             f"{r['exp_month_usd_range'][1]:,.0f}) |")
L += ['', 'Exp. $/mo = mean over channels created <= 365 d that uploaded a long video in the last 48 h of (lifetime views / age x 30, '
      'counted only if >= 1K subs) x RPM. It mixes failures (0) and winners, so it is an average outcome, not a typical one.', '',
      '## RPM evidence per niche', ''] + [f"- {n}: {RPM[n][3]}" for n in RPM] + ['', '## Newest-channel winners per niche (top 30 d, channel <= 365 d)', '']
for n, r in rows_all:
    if r['examples_new']:
        L.append(f"- **{n}**: " + '; '.join(f"{e['ch']} ({e['created']}, {(e['subs'] or 0) / 1e3:,.1f}K subs) {e['views'] / 1e3:,.0f}K views, "
                                             f"{e['min']} min - {e['title']}" for e in r['examples_new']))
open(os.path.join(HERE, 'wide_scan.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
json.dump(out, open(os.path.join(HERE, 'wide_scan.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=str)
print('\n'.join(L))
