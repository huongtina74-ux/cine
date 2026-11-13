"""CineFactory: hunt for MEGA new channels: created <=15 days, huge Shorts views. Any niche, any country.
search.list (order=viewCount, publishedAfter, videoDuration=short) by region with no query + generic queries,
then videos.list + channels.list. Key from .env, never printed. Output out/2026-11-13_new_channel_hunt/mega_15d.json"""
import json, os, sys, time, urllib.parse, urllib.request, datetime as dt
HERE=os.path.dirname(os.path.abspath(__file__))
KEY=[l.split('=',1)[1].strip().strip('"') for l in open(os.path.join(HERE,'.env'),encoding='utf-8') if l.startswith('YOUTUBE_DATA_API_KEY=')][0]
AFTER='2026-10-29T00:00:00Z'
OUT=os.path.join(HERE,'out','2026-11-13_new_channel_hunt'); os.makedirs(OUT,exist_ok=True)
units=0; log=[]
def api(ep,**p):
    global units
    p['key']=KEY; url='https://www.googleapis.com/youtube/v3/'+ep+'?'+urllib.parse.urlencode(p)
    err=''
    for i in range(3):
        try:
            with urllib.request.urlopen(url,timeout=30) as r:
                units+=100 if ep=='search' else 1; return json.load(r)
        except Exception as e:
            err=str(e); 
            try: err+=' '+e.read().decode()[:300]
            except Exception: pass
            time.sleep(2)
    return {'error':err.replace(KEY,'***')}
REGIONS=['US','IN','BR','ID','MX','PH','GB','DE','JP','KR','VN','TH','EG','PK']
EXTRA_PAGE={'US','IN','BR','ID'}
QUERIES=['#shorts','funny','ai','animation','challenge','cat','prank','satisfying','cartoon','story','roblox','football','song','dance','asmr','magic','life hack','car','baby','minecraft']
jobs=[dict(regionCode=r) for r in REGIONS]+[dict(q=q) for q in QUERIES]
vids={}
for j in jobs:
    tok=None
    pages=2 if j.get('regionCode') in EXTRA_PAGE else 1
    for pg in range(pages):
        p=dict(part='snippet',type='video',order='viewCount',publishedAfter=AFTER,maxResults=50,videoDuration='short',**j)
        if tok: p['pageToken']=tok
        res=api('search',**p)
        if 'error' in res: log.append(dict(j,error=res['error'][:300])); break
        for it in res.get('items',[]): vids.setdefault(it['id']['videoId'],json.dumps(j))
        log.append(dict(j,page=pg,n=len(res.get('items',[]))))
        tok=res.get('nextPageToken')
        if not tok: break
ids=list(vids); vinfo={}
for i in range(0,len(ids),50):
    res=api('videos',part='snippet,statistics,contentDetails',id=','.join(ids[i:i+50]))
    for it in res.get('items',[]): vinfo[it['id']]=it
chids=sorted({v['snippet']['channelId'] for v in vinfo.values()}); cinfo={}
for i in range(0,len(chids),50):
    res=api('channels',part='snippet,statistics',id=','.join(chids[i:i+50]))
    for it in res.get('items',[]): cinfo[it['id']]=it
rows=[]
for vid,job in vids.items():
    v=vinfo.get(vid)
    if not v: continue
    c=cinfo.get(v['snippet']['channelId'],{}); cs=c.get('snippet',{}); st=c.get('statistics',{})
    rows.append(dict(video_id=vid,job=job,title=v['snippet']['title'],video_published=v['snippet']['publishedAt'],duration=v['contentDetails'].get('duration'),
        views=int(v['statistics'].get('viewCount',0)),likes=int(v['statistics'].get('likeCount',0) or 0),comments=v['statistics'].get('commentCount'),
        category=v['snippet'].get('categoryId'),lang=v['snippet'].get('defaultAudioLanguage') or v['snippet'].get('defaultLanguage'),
        channel_id=v['snippet']['channelId'],channel=v['snippet']['channelTitle'],channel_created=cs.get('publishedAt'),channel_country=cs.get('country'),
        subs=None if st.get('hiddenSubscriberCount') else int(st.get('subscriberCount',0) or 0),channel_views=int(st.get('viewCount',0) or 0),channel_videos=int(st.get('videoCount',0) or 0)))
json.dump(dict(published_after=AFTER,units_est=units,search_log=log,n_videos=len(rows),n_channels=len(cinfo),rows=rows),open(os.path.join(OUT,'mega_15d.json'),'w',encoding='utf-8'),ensure_ascii=False)
open(os.path.join(OUT,'DONE_mega.txt'),'w').write('videos=%d channels=%d units~%d'%(len(rows),len(cinfo),units))
print('DONE',len(rows),len(cinfo),units)
