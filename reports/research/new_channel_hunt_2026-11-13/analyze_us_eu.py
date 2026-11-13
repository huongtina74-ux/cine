"""US/EU new channels (<=30d, >=1M views): consistency from their own uploads."""
import json, re, statistics as st, datetime as dt
d=json.load(open('us_eu_deep.json',encoding='utf-8'))
print('units',d['units_est'],'log',d['log'][:12],'new rows',d['n_new_rows'])
def secs(s):
    m=re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',s or '')
    return sum(int(x or 0)*k for x,k in zip(m.groups(),(86400,3600,60,1))) if m else 0
out=[]
for c in d['candidates']:
    up=c.get('uploads',[])
    vs=sorted([u['views'] for u in up]) or [0]
    med=st.median(vs); top=max(up,key=lambda u:u['views']) if up else {}
    likes=sum(u['likes'] for u in up); views=sum(u['views'] for u in up) or 1
    durs=[secs(u['duration']) for u in up]
    c2=dict(c); c2.update(n_up=len(up), med=med, share_1m=sum(v>=1e6 for v in vs)/len(vs), top=top.get('views',0), top_title=top.get('title',''),
        like_rate=likes/views, top_share=(top.get('views',0)/views), med_dur=st.median(durs) if durs else 0,
        titles=[u['title'] for u in sorted(up,key=lambda u:-u['views'])[:4]])
    out.append(c2)
for c in sorted(out,key=lambda c:-c['chV']):
    print(f"\n{c['age']:.0f}d|{c['channel']}|{c['country']}|feeds {c['feeds']}|langs {c['langs']}|subs {c['subs']}|chV {c['chV']/1e6:.1f}M|uploads {c['n_up']}/{c['vids']}|median {c['med']/1e3:.0f}K|>=1M {c['share_1m']:.0%}|top share {c['top_share']:.0%}|like {c['like_rate']:.2%}|dur {c['med_dur']:.0f}s")
    for t in c['titles']: print('   -',t[:90])
json.dump(out,open('us_eu_channels.json','w',encoding='utf-8'),ensure_ascii=False,indent=1,default=list)
