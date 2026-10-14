"""Seed user-selected competitors from verified public video metadata.

No full video download, credentials, account subscriptions, uploads or
production changes. This is a single initial seed, future channel uploads
are monitored by CineFactory daily scanner independently.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from cinefactory.studio.daily_youtube_breakout_v199 import (
    BreakoutLedger,PublicYoutubeClient,
)
SEEDS=[
    ("t5wy_OsuMvM","minecraft_gameplay"),
    ("L3mZVFZRJ8E","minecraft_animation"),
]
def main():
    ledger=BreakoutLedger(ROOT/"data/research/youtube_breakout/cinefactory_breakout.sqlite3")
    client=PublicYoutubeClient()
    results=[]
    for vid,lane in SEEDS:
        try:
            record=client.video(vid,lane=lane)
            if not record.channel_id:
                results.append({"video_id":vid,"status":"CHANNEL_ID_NOT_AVAILABLE"})
                continue
            ledger.follow_channel(record,datetime.now(timezone.utc).isoformat(),
                                  "USER_PROVIDED_REFERENCED_COMPETITOR")
            results.append({
                "video_id":record.video_id,"channel_id":record.channel_id,
                "name":record.channel_name,"status":"VERIFIED_CHANNEL_FOLLOWED",
                "channel_created_at":None,"channel_new_channel_status":"UNKNOWN",
                "video_full_content_seen":False,
            })
        except Exception as e:
            results.append({"video_id":vid,
                            "status":"SEED_METADATA_UNAVAILABLE",
                            "error":type(e).__name__+":"+str(e)[:150]})
    output=ROOT/"data/research/youtube_breakout/seed_competitors_v199.json"
    output.write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding="utf-8")
    print("COMPETITOR_TRACKER_ACTUAL_SEEDS",json.dumps(results,ensure_ascii=False),
          "CHANNEL_COUNT",ledger.stats()["followed_competitor_channels"])
if __name__=="__main__":main()
