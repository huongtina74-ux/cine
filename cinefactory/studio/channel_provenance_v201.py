"""Optional official YouTube channel-creation source for 0-30 day hard gate.

No key? 100% safe: return NO_API_KEY without inferring channel age.
User can add their own Google Cloud YouTube Data API key in the OS
environment; no vidIQ subscription necessary. No unapproved secrets printed.
Requests are read-only channels.list part=snippet,statistics bounded to <=30.
Free daily quota is limited. Never say quota/cost guaranteed; actual Google
Cloud billing/account conditions are controlled by user.
"""
from __future__ import annotations
import datetime as dt
import json
import os
import urllib.parse
import urllib.request
from typing import Callable
from .two_track_research_v201 import ChannelEvidence,DualResearchStore
from .daily_youtube_breakout_v199 import CHANNEL_RE,UTC

def parse_official_channel(row:dict,requested:set[str])->ChannelEvidence:
    if row.get("id") not in requested:
        raise ValueError("CHANNEL_ID_API_RESPONSE_MISMATCH")
    published=(row.get("snippet") or {}).get("publishedAt")
    if not isinstance(published,str):raise ValueError("NO_CHANNEL_CREATION_SOURCE")
    try:
        when=dt.datetime.fromisoformat(published.replace("Z","+00:00"))
        if when.tzinfo is None:raise ValueError("CREATION_TIME_NO_TIMEZONE")
        created=when.astimezone(UTC).date().isoformat()
    except (ValueError,TypeError) as exc:
        raise ValueError("CHANNEL_CREATION_SOURCE_INVALID") from exc
    stats=row.get("statistics") or {}
    count=None
    if not stats.get("hiddenSubscriberCount"):
        raw=stats.get("subscriberCount")
        if isinstance(raw,str) and raw.isdecimal():count=int(raw)
    return ChannelEvidence(
        channel_id=row["id"],
        channel_name=str((row.get("snippet") or {}).get("title") or "")[:200],
        created_utc_day=created,
        creation_provenance="YOUTUBE_DATA_API_CHANNELS_SNIPPET_PUBLISHED_AT",
        subscriber_count=count,
        subscribers_observed_at=dt.datetime.now(UTC).isoformat() if count is not None else None)

def official_channel_refresh(store:DualResearchStore,channel_ids:list[str],
                             *,api_key:str|None=None,fetch_json:Callable|None=None)->dict:
    unique=list(dict.fromkeys(channel_ids))
    if not unique:
        return {"status":"NO_CHANNELS_TO_VERIFY","channels_updated":0,"channel_ids":[]}
    if len(unique)>30 or any(not CHANNEL_RE.fullmatch(cid) for cid in unique):
        raise ValueError("CHANNEL_SOURCE_QUOTA_OR_ID_INVALID")
    key=api_key if api_key is not None else os.getenv("YOUTUBE_DATA_API_KEY")
    if not key:
        return {"status":"NO_API_KEY_AGES_REMAIN_UNKNOWN","channels_updated":0,
                "channel_ids":unique,"official_age_verified":False}
    if fetch_json is None:
        def fetch_json(u):
            if not u.startswith("https://www.googleapis.com/youtube/v3/channels?"):
                raise ValueError("BLOCKED_SOURCE_HOST")
            with urllib.request.urlopen(u,timeout=15) as response:
                if int(response.status)!=200:raise RuntimeError("API_STATUS_NOT_OK")
                return json.loads(response.read(1_000_000).decode("utf-8"))
    query=urllib.parse.urlencode({
        "part":"snippet,statistics",
        "id":",".join(unique),
        "key":key,
        "maxResults":min(30,len(unique)),
    })
    uri="https://www.googleapis.com/youtube/v3/channels?"+query
    response=fetch_json(uri)
    updated=[]
    errors=[]
    for raw in response.get("items",[]):
        try:
            ch=parse_official_channel(raw,set(unique))
            store.save_channel(ch,dt.datetime.now(UTC).isoformat())
            updated.append(ch.channel_id)
        except (ValueError,TypeError) as exc:
            errors.append({"channel_id":str(raw.get("id"))[:24],"error":str(exc)[:80]})
    return {
        "status":"OFFICIAL_CHANNEL_AGE_OBSERVED" if updated else "CHANNEL_AGE_UNAVAILABLE",
        "channels_updated":len(updated),"channel_ids":updated,"errors":errors,
        "official_age_verified":bool(updated),
        "source":"YouTube Data API channels.list snippet.publishedAt",
        "user_owned_key_required":True,
        "api_key_redacted":True,
    }
