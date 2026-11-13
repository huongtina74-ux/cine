"""Merge hunt_15d.json + mega_15d.json; rank channels created <=15/30 days by channel views."""
import json, re, datetime as dt
from collections import defaultdict
T=dt.datetime(2026,11,13,12,tzinfo=dt.timezone.utc)
age=lambda s:(T-dt.datetime.fromisoformat(s.replace('Z','+00:00'))).total_seconds()/86400
rows=[]
for f in ('hunt_15d.json','mega_15d.json'):
    d=json.load(open(f,encoding='utf-8')); rows+=d['rows']
    if f=='mega_15d.json': print('mega units',d['units_est'],'videos',d['n_videos'],'channels',d['n_channels'],'errors',[l for l in d['search_log'] if 'error' in l][:2])
ch=defaultdict(list)
for r in rows:
    if r.get('channel_created'): ch[r['channel_id']].append(r)
out=[]
for cid,rs in ch.items():
    r0=rs[0]; top=max(rs,key=lambda r:r['views'])
    out.append(dict(channel=r0['channel'],cid=cid,age=age(r0['channel_created']),created=r0['channel_created'][:10],subs=r0['subs'],chV=r0['channel_views'],vids=r0['channel_videos'],
       country=r0['channel_country'],lang=top['lang'],top=top['views'],title=top['title'],job=top.get('job') or top.get('query'),n_seen=len(rs)))
print('channels total',len(out))
for lim in (15,30):
    sel=sorted([o for o in out if o['age']<=lim],key=lambda o:-o['chV'])
    print(f'\n== created <= {lim}d: {len(sel)} channels; >=10M views: {sum(o["chV"]>=10e6 for o in sel)}; >=100M: {sum(o["chV"]>=100e6 for o in sel)}')
    for o in sel[:30]:
        print(f"{o['age']:.0f}d|{o['created']}|{o['channel'][:26]}|subs {o['subs']}|chV {o['chV']:,}|vids {o['vids']}|top {o['top']:,}|{o['country']}|{o['lang']}|{str(o['job'])[:28]}|{o['title'][:55]}")
# context: the biggest channels in the pool regardless of age, and age distribution of 100M+ channels
big=sorted(out,key=lambda o:-o['chV'])
print('\n== oldest/youngest among channels whose top recent Short >=50M')
for o in sorted([o for o in out if o['top']>=50e6],key=lambda o:o['age'])[:15]:
    print(f"{o['age']:.0f}d|{o['channel'][:26]}|chV {o['chV']:,}|top {o['top']:,}|{o['title'][:50]}")
json.dump(out,open('channels_merged.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
