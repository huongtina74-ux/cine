"""CineFactory: US/EU mostPopular charts (videos.list chart=mostPopular, 1 unit/page) -> channel ages. Key from .env, never printed."""
import json, os, time, urllib.parse, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,'out','2026-11-13_new_channel_hunt')
KEY=[l.split('=',1)[1].strip().strip('"') for l in open(os.path.join(HERE,'.env'),encoding='utf-8') if l.startswith('YOUTUBE_DATA_API_KEY=')][0]
units=0; log=[]
def api(ep,**p):
    global units
    p['key']=KEY; url='https://www.googleapis.com/youtube/v3/'+ep+'?'+urllib.parse.urlencode(p); err=''
    for i in range(2):
        try:
            with urllib.request.urlopen(url,timeout=30) as r:
                units+=1; return json.load(r)
        except Exception as e:
            err=str(e)
            try: err+=' '+e.read().decode()[:300]
            except Exception: pass
            time.sleep(2)
    return {'error':err.replace(KEY,'***')}
REG=['US','GB','CA','AU','DE','FR','ES','IT','NL','PL','SE','IE','BE','AT']
vids={}
for rg in REG:
    tok=None
    for pg in range(4):
        p=dict(part='snippet,statistics,contentDetails',chart='mostPopular',regionCode=rg,maxResults=50)
        if tok: p['pageToken']=tok
        res=api('videos',**p)
        if 'error' in res: log.append(dict(region=rg,error=res['error'][:300])); break
        for it in res.get('items',[]):
            vids.setdefault(it['id'],dict(it=it,regions=[]))['regions'].append(rg)
        tok=res.get('nextPageToken'); log.append(dict(region=rg,page=pg,n=len(res.get('items',[]))))
        if not tok: break
chids=sorted({v['it']['snippet']['channelId'] for v in vids.values()}); cinfo={}
for i in range(0,len(chids),50):
    res=api('channels',part='snippet,statistics',id=','.join(chids[i:i+50]))
    for it in res.get('items',[]): cinfo[it['id']]=it
rows=[]
for vid,v in vids.items():
    it=v['it']; c=cinfo.get(it['snippet']['channelId'],{}); cs=c.get('snippet',{}); st=c.get('statistics',{})
    rows.append(dict(video_id=vid,regions=v['regions'],title=it['snippet']['title'],video_published=it['snippet']['publishedAt'],duration=it['contentDetails'].get('duration'),
      views=int(it['statistics'].get('viewCount',0)),likes=int(it['statistics'].get('likeCount',0) or 0),category=it['snippet'].get('categoryId'),
      channel_id=it['snippet']['channelId'],channel=it['snippet']['channelTitle'],channel_created=cs.get('publishedAt'),channel_country=cs.get('country'),
      subs=None if st.get('hiddenSubscriberCount') else int(st.get('subscriberCount',0) or 0),channel_views=int(st.get('viewCount',0) or 0),channel_videos=int(st.get('videoCount',0) or 0)))
json.dump(dict(units=units,log=log,rows=rows),open(os.path.join(OUT,'mostpopular_us_eu.json'),'w',encoding='utf-8'),ensure_ascii=False)
open(os.path.join(OUT,'DONE_mostpopular.txt'),'w').write('rows=%d units=%d'%(len(rows),units)); print('DONE',len(rows),units)
