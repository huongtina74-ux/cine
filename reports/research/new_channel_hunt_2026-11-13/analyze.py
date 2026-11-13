"""Find channels created within N days that already have big videos (from hunt_15d.json)."""
import json, re, statistics as st, datetime as dt, sys
from collections import defaultdict
d=json.load(open('hunt_15d.json',encoding='utf-8'))
T=dt.datetime(2026,11,13,12,tzinfo=dt.timezone.utc)
def age(s): return (T-dt.datetime.fromisoformat(s.replace('Z','+00:00'))).total_seconds()/86400
def dur(s):
    m=re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',s or '');
    if not m: return None
    dd,h,mi,se=[int(x or 0) for x in m.groups()]; return dd*86400+h*3600+mi*60+se
print('window',d['window_days'],'after',d['published_after'],'units~',d['units_est'],'videos',d['n_videos'],'channels',d['n_channels'])
print('search errors',[l for l in d['search_log'] if 'error' in l][:3])
ch=defaultdict(list)
for r in d['rows']:
    if r['channel_created']: ch[r['channel_id']].append(r)
IP=re.compile(r'maizen|\bjj\b|mikey|skibidi|roblox|sprunki|poppy|fnaf|sonic|pokemon|digital circus|garten|bluey|minion|spider',re.I)
out=[]
for cid,rs in ch.items():
    a=age(rs[0]['channel_created'])
    top=max(rs,key=lambda r:r['views'])
    out.append(dict(channel=rs[0]['channel'],cid=cid,ch_age=a,created=rs[0]['channel_created'][:10],subs=rs[0]['subs'],ch_views=rs[0]['channel_views'],ch_videos=rs[0]['channel_videos'],
        country=rs[0]['channel_country'],top_views=top['views'],top_title=top['title'],top_dur=dur(top['duration']),top_age=age(top['video_published']),
        query=top['query'],src=top['src'],lang=top['lang'],ip=bool(IP.search(' '.join(r['title'] for r in rs)))))
for lim in (15,30):
    sel=sorted([o for o in out if o['ch_age']<=lim and o['ch_views']>=100_000],key=lambda o:-o['ch_views'])
    print(f'\n== channels created <= {lim} days with >=100K channel views: {len(sel)} (of {sum(o["ch_age"]<=lim for o in out)} new channels seen)')
    for o in sel[:45]:
        print(f"{o['ch_age']:.0f}d|{o['created']}|{o['channel'][:24]}|subs {o['subs']}|chV {o['ch_views']:,}|vids {o['ch_videos']}|top {o['top_views']:,} {o['top_dur']}s|{o['country']}|{o['lang']}|q={o['query'][:18]}|ip={o['ip']}|{o['top_title'][:60]}")
json.dump(out,open('channels.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
