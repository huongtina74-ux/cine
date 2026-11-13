"""CineFactory: US/EU new-channel deep dive (2026-11-13).
1) search.list region feeds (Shorts, order=viewCount, publishedAfter 2026-10-29) for remaining US/EU regions.
2) Merge with earlier pools; pick channels created <=30 days, >=1M channel views, US/EU (country or feed region).
3) Pull each candidate's uploads (playlistItems, latest 50) + videos.list stats -> consistency.
Key from .env, never printed."""
import json, os, time, urllib.parse, urllib.request, datetime as dt, statistics as st
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,'out','2026-11-13_new_channel_hunt')
KEY=[l.split('=',1)[1].strip().strip('"') for l in open(os.path.join(HERE,'.env'),encoding='utf-8') if l.startswith('YOUTUBE_DATA_API_KEY=')][0]
units=0; log=[]
def api(ep,**p):
    global units
    p['key']=KEY; url='https://www.googleapis.com/youtube/v3/'+ep+'?'+urllib.parse.urlencode(p); err=''
    for i in range(2):
        try:
            with urllib.request.urlopen(url,timeout=30) as r:
                units+=100 if ep=='search' else 1; return json.load(r)
        except Exception as e:
            err=str(e)
            try: err+=' '+e.read().decode()[:300]
            except Exception: pass
            time.sleep(2)
    return {'error':err.replace(KEY,'***')}
EU=['US','CA','GB','IE','AU','NZ','DE','FR','ES','IT','NL','BE','AT','CH','SE','NO','DK','FI','PL','PT','CZ','RO','HU','GR']
NEW_REGIONS=['CA','AU','FR','ES','IT','NL','PL','SE','BE']
vids={}
for rg in NEW_REGIONS:
    res=api('search',part='snippet',type='video',order='viewCount',publishedAfter='2026-10-29T00:00:00Z',maxResults=50,videoDuration='short',regionCode=rg)
    if 'error' in res: log.append(dict(region=rg,error=res['error'][:300])); break
    for it in res.get('items',[]): vids.setdefault(it['id']['videoId'],rg)
    log.append(dict(region=rg,n=len(res.get('items',[]))))
ids=list(vids); vinfo={}
for i in range(0,len(ids),50):
    res=api('videos',part='snippet,statistics,contentDetails',id=','.join(ids[i:i+50]))
    for it in res.get('items',[]): vinfo[it['id']]=it
chids=sorted({v['snippet']['channelId'] for v in vinfo.values()}); cinfo={}
for i in range(0,len(chids),50):
    res=api('channels',part='snippet,statistics,contentDetails',id=','.join(chids[i:i+50]))
    for it in res.get('items',[]): cinfo[it['id']]=it
new_rows=[]
for vid,rg in vids.items():
    v=vinfo.get(vid)
    if not v: continue
    c=cinfo.get(v['snippet']['channelId'],{}); cs=c.get('snippet',{}); stt=c.get('statistics',{})
    new_rows.append(dict(video_id=vid,job=json.dumps({'regionCode':rg}),title=v['snippet']['title'],video_published=v['snippet']['publishedAt'],duration=v['contentDetails'].get('duration'),
        views=int(v['statistics'].get('viewCount',0)),likes=int(v['statistics'].get('likeCount',0) or 0),comments=v['statistics'].get('commentCount'),category=v['snippet'].get('categoryId'),
        lang=v['snippet'].get('defaultAudioLanguage') or v['snippet'].get('defaultLanguage'),channel_id=v['snippet']['channelId'],channel=v['snippet']['channelTitle'],
        channel_created=cs.get('publishedAt'),channel_country=cs.get('country'),subs=None if stt.get('hiddenSubscriberCount') else int(stt.get('subscriberCount',0) or 0),
        channel_views=int(stt.get('viewCount',0) or 0),channel_videos=int(stt.get('videoCount',0) or 0)))
rows=list(new_rows)
for f in ('hunt_15d.json','mega_15d.json'):
    try: rows+=json.load(open(os.path.join(OUT,f),encoding='utf-8'))['rows']
    except Exception as e: log.append(dict(load=f,error=str(e)))
T=dt.datetime(2026,11,13,12,tzinfo=dt.timezone.utc)
age=lambda s:(T-dt.datetime.fromisoformat(s.replace('Z','+00:00'))).total_seconds()/86400
cand={}
for r in rows:
    if not r.get('channel_created'): continue
    a=age(r['channel_created'])
    if a>30 or r['channel_views']<1_000_000: continue
    job=r.get('job') or ''
    feed=json.loads(job).get('regionCode') if job.startswith('{') else None
    eu=(r['channel_country'] in EU) or (r['channel_country'] is None and (feed in EU or (r.get('lang') or '').split('-')[0] in ('en','de','fr','es','it','nl','pl','sv','pt')))
    if not eu: continue
    c=cand.setdefault(r['channel_id'],dict(channel=r['channel'],cid=r['channel_id'],age=a,created=r['channel_created'],country=r['channel_country'],subs=r['subs'],chV=r['channel_views'],vids=r['channel_videos'],feeds=set(),langs=set()))
    if feed: c['feeds'].add(feed)
    if r.get('lang'): c['langs'].add(r['lang'])
top=sorted(cand.values(),key=lambda c:-c['chV'])[:45]
for c in top:
    up='UU'+c['cid'][2:]
    res=api('playlistItems',part='contentDetails',playlistId=up,maxResults=50)
    vid_ids=[it['contentDetails']['videoId'] for it in res.get('items',[])]
    stats=[]
    if vid_ids:
        vr=api('videos',part='snippet,statistics,contentDetails',id=','.join(vid_ids))
        for it in vr.get('items',[]):
            stats.append(dict(id=it['id'],title=it['snippet']['title'],published=it['snippet']['publishedAt'],duration=it['contentDetails'].get('duration'),
              views=int(it['statistics'].get('viewCount',0)),likes=int(it['statistics'].get('likeCount',0) or 0),comments=int(it['statistics'].get('commentCount',0) or 0),
              lang=it['snippet'].get('defaultAudioLanguage'),tags=it['snippet'].get('tags',[])[:8],desc=it['snippet'].get('description','')[:200]))
    c['uploads']=stats; c['feeds']=sorted(c['feeds']); c['langs']=sorted(c['langs'])
json.dump(dict(units_est=units,log=log,n_new_rows=len(new_rows),candidates=top),open(os.path.join(OUT,'us_eu_deep.json'),'w',encoding='utf-8'),ensure_ascii=False)
open(os.path.join(OUT,'DONE_us_eu.txt'),'w').write('cands=%d units~%d'%(len(top),units))
print('DONE',len(top),units)
