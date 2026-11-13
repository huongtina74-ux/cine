"""Analyse a Tube Atlas v1.0.6.7 Videos-grid CSV export (Shorts keyword scan, 2026-11-13).
OBSERVED numbers come straight from the export; derived ratios are INFERRED."""
import csv, io, re, json, statistics as st, sys, pathlib
from collections import defaultdict
HERE = pathlib.Path(__file__).parent
rows = list(csv.DictReader(io.StringIO((HERE/'raw_tubeatlas_export.csv').read_bytes().decode('utf-8-sig', 'replace'))))

def num(s):
    s = (s or '').strip().replace(',', '').replace('+', '')
    try: return float(s)
    except ValueError: return None
def subs(s):
    s = (s or '').lower().strip()
    m = re.match(r'([\d.]+)\s*(thousand|million|billion)?', s)
    if not m: return None
    v = float(m.group(1)); mult = {'thousand':1e3,'million':1e6,'billion':1e9}.get(m.group(2),1)
    return v*mult
IP = re.compile(r'skibidi|maizen|\bjj\b|mikey|roblox|sonic|pokemon|pok[eé]mon|spider|poppy|huggy|sprunki|fnaf|freddy|among us|mario|garten|digital circus|bluey|peppa|minion|marvel|dc |batman|naruto|goku|godzilla|kong', re.I)
seen=set(); data=[]
for r in rows:
    vid=r['Video ID']
    if vid in seen: continue
    seen.add(vid)
    v=num(r['Views']); age=num(r['Published Age (Days)']); ln=num(r['Length Seconds']); sb=subs(r['Subscribers'])
    if v is None or age is None: continue
    data.append(dict(id=vid, kw=r['Search Phrase'].replace(' #shorts','').strip(), title=r['Title'], views=v, likes=num(r['Likes']),
        comments=num(r['Comments']), comments_raw=r['Comments'], length=ln, age=max(age,1), vpd=v/max(age,1), short=(r['Is Shorts'].upper()=='YES'),
        cat=r['Category'], channel=r['Channel'], chlink=r['Channel Link'], subs=sb, published=r['Published'], ip=bool(IP.search(r['Title']+' '+r['Tags']))))
shorts=[d for d in data if d['short']]
MC=lambda k:k.startswith('minecraft')
def summ(ds):
    if not ds: return {}
    vs=sorted(d['views'] for d in ds)
    rec=[d for d in ds if d['age']<=30]
    eng=[(d['likes'] or 0)/d['views'] for d in ds if d['views'] and d['likes'] is not None]
    nocom=sum(1 for d in ds if d['comments_raw'] in ('not-given','') )
    ch_1m=len({d['channel'] for d in ds if d['views']>=1e6})
    small_ch_1m=len({d['channel'] for d in ds if d['views']>=1e6 and d['subs'] is not None and d['subs']<100e3})
    vsub=[d['views']/d['subs'] for d in ds if d['subs']]
    return dict(n=len(ds), channels=len({d['channel'] for d in ds}), median_views=st.median(vs), p75_views=vs[int(.75*(len(vs)-1))],
        share_ge1m=sum(v>=1e6 for v in vs)/len(vs), channels_with_1m=ch_1m, small_channels_lt100k_with_1m=small_ch_1m,
        recent_le30d=len(rec), recent_median_vpd=st.median([d['vpd'] for d in rec]) if rec else None,
        median_age_days=st.median(d['age'] for d in ds), median_like_rate=st.median(eng) if eng else None,
        median_views_per_sub=st.median(vsub) if vsub else None, comments_hidden_share=nocom/len(ds), ip_share=sum(d['ip'] for d in ds)/len(ds))
by=defaultdict(list)
for d in shorts: by[d['kw']].append(d)
table={k:summ(v) for k,v in by.items()}
out=dict(rows_exported=len(rows), unique_videos=len(data), shorts=len(shorts), by_keyword=table)
# exploding: recent shorts (<=30d) by views/day
expl=sorted([d for d in shorts if d['age']<=30], key=lambda d:-d['vpd'])[:40]
out['exploding_recent']=[{k:d[k] for k in ('kw','title','views','age','vpd','channel','subs','chlink','ip','comments_raw')} for d in expl]
# outliers vs channel size
outl=sorted([d for d in shorts if d['subs'] and d['subs']>=1000], key=lambda d:-(d['views']/d['subs']))[:40]
out['views_per_sub_top']=[{k:d[k] for k in ('kw','title','views','age','channel','subs','chlink','ip')} for d in outl]
json.dump(out, open(HERE/'analysis.json','w'), ensure_ascii=False, indent=1, default=str)
# print compact
print('rows',len(rows),'unique',len(data),'shorts',len(shorts))
hdr='kw|n|ch|medV|p75V|>=1M|ch1M|smallch1M|rec30|recMedVPD|medAge|like%|V/sub|hidCom|IP'
print(hdr)
for k,s in sorted(table.items(), key=lambda kv:-kv[1]['median_views']):
    print(f"{k}|{s['n']}|{s['channels']}|{s['median_views']:.0f}|{s['p75_views']:.0f}|{s['share_ge1m']:.0%}|{s['channels_with_1m']}|{s['small_channels_lt100k_with_1m']}|{s['recent_le30d']}|{(s['recent_median_vpd'] or 0):.0f}|{s['median_age_days']:.0f}|{(s['median_like_rate'] or 0):.2%}|{(s['median_views_per_sub'] or 0):.2f}|{s['comments_hidden_share']:.0%}|{s['ip_share']:.0%}")
print('\nEXPLODING (<=30d, by views/day)')
for d in expl[:30]:
    print(f"{d['kw'][:22]}|{d['vpd']:.0f}/d|{d['views']:.0f}|{d['age']:.0f}d|{d['channel'][:22]}|{d['subs']}|{d['title'][:60]}|ip={d['ip']}")
print('\nTOP views/sub (subs>=1K)')
for d in outl[:25]:
    print(f"{d['kw'][:22]}|{d['views']/d['subs']:.0f}x|{d['views']:.0f}|{d['age']:.0f}d|{d['channel'][:22]}|{d['subs']}|{d['title'][:55]}")
