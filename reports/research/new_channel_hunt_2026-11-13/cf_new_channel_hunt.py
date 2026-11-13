"""CineFactory: hunt for very new channels (<=N days) that already have big videos.
Inputs: Tube Atlas CSV exports (Video ID column) in this folder + YouTube Data API search.list
(publishedAfter window, order=viewCount, Shorts and any length). Output: out/<date>_new_channel_hunt/.
Key is read from .env (YOUTUBE_DATA_API_KEY) and never printed."""
import csv, glob, io, json, os, sys, time, urllib.parse, urllib.request, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
KEY = [l.split('=',1)[1].strip().strip('"') for l in open(os.path.join(HERE,'.env'),encoding='utf-8') if l.startswith('YOUTUBE_DATA_API_KEY=')][0]
TODAY = dt.datetime(2026,11,13,tzinfo=dt.timezone.utc)
WINDOW = int(sys.argv[1]) if len(sys.argv)>1 else 15
AFTER = (TODAY - dt.timedelta(days=WINDOW)).strftime('%Y-%m-%dT00:00:00Z')
OUT = os.path.join(HERE,'out','2026-11-13_new_channel_hunt'); os.makedirs(OUT, exist_ok=True)
units = 0
def api(ep, **p):
    global units
    p['key']=KEY
    url='https://www.googleapis.com/youtube/v3/'+ep+'?'+urllib.parse.urlencode(p)
    for i in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                units += 100 if ep=='search' else 1
                return json.load(r)
        except Exception as e:
            err=str(e); time.sleep(2)
    return {'error': err.replace(KEY,'***')}
QUERIES = [l.strip() for l in open(os.path.join(HERE,'hunt_queries.txt'),encoding='utf-8') if l.strip()]
vids = {}
# 1) Tube Atlas exports
for f in glob.glob(os.path.join(HERE,'tubeatlas_*.csv')):
    for r in csv.DictReader(io.StringIO(open(f,'rb').read().decode('utf-8-sig','replace'))):
        if r.get('Video ID'): vids.setdefault(r['Video ID'], {'src':'tubeatlas:'+os.path.basename(f), 'q':r.get('Search Phrase','')})
# 2) API search, newest window, by views
log=[]
for q in QUERIES:
    for dur in ('short','any'):
        res = api('search', part='snippet', q=q, type='video', order='viewCount', publishedAfter=AFTER, maxResults=50, videoDuration=dur, relevanceLanguage='en')
        if 'error' in res: log.append({'q':q,'dur':dur,'error':res['error']}); continue
        for it in res.get('items',[]):
            vids.setdefault(it['id']['videoId'], {'src':'api_search_'+dur, 'q':q})
        log.append({'q':q,'dur':dur,'n':len(res.get('items',[]))})
# 3) videos.list
ids=list(vids); vinfo={}
for i in range(0,len(ids),50):
    res=api('videos', part='snippet,statistics,contentDetails', id=','.join(ids[i:i+50]), maxResults=50)
    for it in res.get('items',[]): vinfo[it['id']]=it
# 4) channels.list
chids=sorted({v['snippet']['channelId'] for v in vinfo.values()}); cinfo={}
for i in range(0,len(chids),50):
    res=api('channels', part='snippet,statistics', id=','.join(chids[i:i+50]), maxResults=50)
    for it in res.get('items',[]): cinfo[it['id']]=it
rows=[]
for vid,meta in vids.items():
    v=vinfo.get(vid)
    if not v: continue
    c=cinfo.get(v['snippet']['channelId'],{})
    cs=c.get('snippet',{}); st=c.get('statistics',{})
    rows.append(dict(video_id=vid, src=meta['src'], query=meta['q'], title=v['snippet']['title'], video_published=v['snippet']['publishedAt'],
        duration=v['contentDetails'].get('duration'), views=int(v['statistics'].get('viewCount',0)), likes=int(v['statistics'].get('likeCount',0) or 0),
        comments=v['statistics'].get('commentCount'), category=v['snippet'].get('categoryId'), lang=v['snippet'].get('defaultAudioLanguage') or v['snippet'].get('defaultLanguage'),
        channel_id=v['snippet']['channelId'], channel=v['snippet']['channelTitle'], channel_created=cs.get('publishedAt'), channel_country=cs.get('country'),
        subs=None if st.get('hiddenSubscriberCount') else int(st.get('subscriberCount',0) or 0), channel_views=int(st.get('viewCount',0) or 0), channel_videos=int(st.get('videoCount',0) or 0)))
json.dump(dict(window_days=WINDOW, published_after=AFTER, units_est=units, search_log=log, n_videos=len(rows), n_channels=len(cinfo), rows=rows),
          open(os.path.join(OUT,'hunt_%dd.json'%WINDOW),'w',encoding='utf-8'), ensure_ascii=False)
open(os.path.join(OUT,'DONE_%dd.txt'%WINDOW),'w').write('videos=%d channels=%d units~%d'%(len(rows),len(cinfo),units))
print('DONE', len(rows), len(cinfo), units)
