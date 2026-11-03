"""Minecraft US/English YouTube Data API v3 dataset collector (stdlib only, read-only, official API).

Phases (all quota-guarded, hard cap MAX_UNITS):
  1. search.list (type=video, US, en, order=viewCount, maxResults=50) for SEED keywords, last 7 days
  2. videos.list for all hits -> expand EXPAND related keywords from top titles -> search them (7 days)
  3. search.list for CORE keywords, last 15 days
  4. videos.list (snippet,statistics,contentDetails,status) + channels.list for every result/channel
  5. uploads (playlistItems.list + videos.list, last 50) for leaders, new<=12mo with 100K+ result, new<=30d
  6. derived fields; write CSV/JSON

The API key is read from the .env file inside this process only; it is never printed, logged or written.
"""
import csv
import json
import os
import re
import statistics
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = r"C:\Users\ADMIN\Downloads\cine_niche_survey"
ENV = os.path.join(BASE, ".env")
NOW = datetime.now(timezone.utc).replace(microsecond=0)
OUT = os.path.join(BASE, "out", NOW.strftime("%Y-%m-%d") + "_api_dataset")
LOG = os.path.join(OUT, "progress.log")
MAX_UNITS = 9300
UPLOAD_RESERVE = 0  # uploads use whatever is left after search+lists
EXPAND = 10
SHORT_S = 180
API = "https://www.googleapis.com/youtube/v3/"
COST = {"search": 100, "videos": 1, "channels": 1, "playlistItems": 1}
DUR = re.compile(r"^P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")

SEEDS_SHORT = """minecraft
minecraft animation
minecraft horror
minecraft 100 days
minecraft shorts
minecraft funny
minecraft movie
minecraft challenge
minecraft mod
minecraft survival
minecraft hardcore
minecraft smp
minecraft manhunt
minecraft roleplay
minecraft build
minecraft redstone
minecraft speedrun
minecraft pvp
minecraft update
minecraft prank
minecraft lore
minecraft story
minecraft but
minecraft mystery
minecraft parkour""".splitlines()
SEEDS_LONG = """minecraft but every time
baby zombie tries food for the first time minecraft
minecraft poor vs rich animation
minecraft found footage
minecraft analog horror
minecraft survival movie full
minecraft lore explained
minecraft build hacks
minecraft monster school
minecraft noob vs pro
minecraft noob vs pro vs hacker vs god
i survived 100 days in minecraft hardcore
minecraft 1000 players simulate civilization
minecraft but i can shapeshift
minecraft but every block is random
minecraft arg
minecraft creepypasta
minecraft herobrine
minecraft scary seed
minecraft horror mod
minecraft zombie apocalypse
minecraft villager life
minecraft parody song
minecraft house tutorial
minecraft speedrunner vs hunter
minecraft hide and seek
minecraft trolling friends
minecraft lucky block
minecraft one block
minecraft animation sad story
minecraft family roleplay""".splitlines()
CORE15 = """minecraft
minecraft animation
minecraft horror
minecraft 100 days
minecraft shorts
minecraft movie
minecraft challenge
minecraft but
minecraft smp
minecraft manhunt
minecraft roleplay
minecraft noob vs pro
minecraft poor vs rich animation
minecraft found footage
minecraft mod
minecraft survival
minecraft build
minecraft lore explained""".splitlines()

STOP = set("minecraft the a an and or of to in on for with is are i my me we you your it this that vs but at by from as be was "
           "it's i'm part shorts short minecraftshorts video videos episode ep official live ft feat new got how what who why "
           "when can will just get all one not his her our they them so do does did has have had into out up".split())

os.makedirs(OUT, exist_ok=True)
STATE = {"units": 0, "calls": Counter(), "errors": [], "quota_stop": None, "phase": "", "started": NOW.isoformat()}


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(datetime.now(timezone.utc).strftime("%H:%M:%S") + " " + msg + "\n")


def read_key():
    with open(ENV, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.match(r"\s*(YOUTUBE_DATA_API_KEY|YOUTUBE_API_KEY|GOOGLE_API_KEY)\s*=\s*['\"]?([^'\"\s#]+)", line)
            if m:
                return m.group(2)
    return None


KEY = read_key()


class QuotaStop(Exception):
    pass


def api(endpoint, **params):
    cost = COST[endpoint]
    params["key"] = KEY
    url = API + endpoint + "?" + urlencode(params)
    for attempt in range(3):
        if STATE["units"] + cost > MAX_UNITS:
            raise QuotaStop("budget cap %d reached" % MAX_UNITS)
        STATE["units"] += cost  # counted per attempt (conservative)
        STATE["calls"][endpoint] += 1
        try:
            with urlopen(url, timeout=30) as s:
                return json.load(s)
        except HTTPError as e:
            reason = ""
            try:
                body = json.loads(e.read().decode("utf-8", "ignore"))
                reason = ((body.get("error") or {}).get("errors") or [{}])[0].get("reason", "")
            except Exception:
                pass
            if reason in ("quotaExceeded", "dailyLimitExceeded", "rateLimitExceeded", "userRateLimitExceeded") or (e.code == 403 and not reason):
                STATE["quota_stop"] = "HTTP %d %s" % (e.code, reason)
                raise QuotaStop(STATE["quota_stop"]) from None
            if e.code >= 500 and attempt < 2:
                time.sleep(2 + attempt * 3)
                continue
            safe = {k: v for k, v in params.items() if k != "key"}
            STATE["errors"].append({"endpoint": endpoint, "code": e.code, "reason": reason,
                                    "params": {k: str(v)[:120] for k, v in safe.items()}})
            return {"items": [], "_error": e.code}
        except Exception as e:  # network; never include the URL
            if attempt < 2:
                time.sleep(2 + attempt * 3)
                continue
            STATE["errors"].append({"endpoint": endpoint, "code": "network", "reason": type(e).__name__})
            return {"items": [], "_error": "network"}
    return {"items": []}


def iso(dt):
    return dt.isoformat().replace("+00:00", "Z")


def utc(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def seconds(d):
    m = DUR.fullmatch(d or "")
    if not m:
        return None
    a, b, c, e = (int(x or 0) for x in m.groups())
    return a * 86400 + b * 3600 + c * 60 + e


# ---------------- collected state ----------------
SEARCH = []          # {keyword, window_days, published_after, fetched_at, rank, video_id, channel_id, title}
RAW_SEARCH = {}      # "kw|7" -> response items (snippet) + meta
VIDEOS = {}          # id -> item (trimmed) + _fetched_at
CHANNELS = {}        # id -> item + _fetched_at
UPLOADS = {}         # channel_id -> {"group": [...], "fetched_at":..., "items": [video ids in playlist order], "playlist_items": [...]}
UPVIDEOS = {}        # id -> item (from uploads)
KEYWORDS = []        # (keyword, type, windows)


def trim(item):
    sn = item.get("snippet", {})
    sn.pop("thumbnails", None)
    sn.pop("localized", None)
    if "description" in sn:
        sn["description"] = sn["description"][:1000]
    return item


def search(q, days):
    after = NOW - timedelta(days=days)
    fetched = iso(datetime.now(timezone.utc).replace(microsecond=0))
    data = api("search", part="snippet", q=q, type="video", order="viewCount", maxResults=50,
               publishedAfter=iso(after), regionCode="US", relevanceLanguage="en")
    items = data.get("items", [])
    RAW_SEARCH["%s|%d" % (q, days)] = {"keyword": q, "window_days": days, "published_after": iso(after), "fetched_at": fetched,
                                       "totalResults": (data.get("pageInfo") or {}).get("totalResults"),
                                       "error": data.get("_error"), "items": [trim(i) for i in items]}
    ids = []
    for rank, it in enumerate(items, 1):
        vid = (it.get("id") or {}).get("videoId")
        if not vid:
            continue
        ids.append(vid)
        SEARCH.append({"keyword": q, "window_days": days, "published_after": iso(after), "fetched_at": fetched, "rank": rank,
                       "video_id": vid, "channel_id": it["snippet"].get("channelId", ""), "title": it["snippet"].get("title", "")})
    log("search %dd %-55s -> %d (units %d)" % (days, q[:55], len(ids), STATE["units"]))
    return ids


def fetch_videos(ids, store):
    ids = [i for i in dict.fromkeys(ids) if i not in store]
    for i in range(0, len(ids), 50):
        fetched = iso(datetime.now(timezone.utc).replace(microsecond=0))
        data = api("videos", part="snippet,statistics,contentDetails,status", id=",".join(ids[i:i + 50]))
        for it in data.get("items", []):
            it["_fetched_at"] = fetched
            store[it["id"]] = trim(it)


def fetch_channels(ids):
    ids = [i for i in dict.fromkeys(ids) if i and i not in CHANNELS]
    for i in range(0, len(ids), 50):
        fetched = iso(datetime.now(timezone.utc).replace(microsecond=0))
        data = api("channels", part="snippet,statistics,contentDetails,status", id=",".join(ids[i:i + 50]))
        for it in data.get("items", []):
            it["_fetched_at"] = fetched
            CHANNELS[it["id"]] = trim(it)


def related(titles, seen, n):
    grams = Counter()
    for t in titles:
        w = [x for x in re.findall(r"[a-z0-9']+", t.lower()) if x not in STOP and len(x) > 2 and not x.isdigit()]
        for i in range(len(w)):
            grams[w[i]] += 1
            if i + 1 < len(w) and w[i] != w[i + 1]:
                grams[w[i] + " " + w[i + 1]] += 2
    out = []
    for g, _ in grams.most_common(300):
        q = "minecraft " + g
        if q in seen or any(q in o or o in q for o in out) or any(q == s for s in seen):
            continue
        out.append(q)
        if len(out) >= n:
            break
    return out


def ch_age_days(ch):
    try:
        return (NOW - utc(ch["snippet"]["publishedAt"])).total_seconds() / 86400
    except Exception:
        return None


def vrow(v):
    sn, st, cd, ss = v.get("snippet", {}), v.get("statistics", {}), v.get("contentDetails", {}), v.get("status", {})
    pub = utc(sn["publishedAt"])
    fa = utc(v["_fetched_at"])
    age = (fa - pub).total_seconds() / 86400
    views = int(st["viewCount"]) if "viewCount" in st else None
    dur = seconds(cd.get("duration"))
    return {
        "video_id": v["id"], "url": "https://www.youtube.com/watch?v=" + v["id"], "title": sn.get("title", ""),
        "channel_id": sn.get("channelId", ""), "channel_title": sn.get("channelTitle", ""),
        "published_at": sn.get("publishedAt", ""), "fetched_at": v["_fetched_at"], "age_days": round(age, 3),
        "views": views, "likes": int(st["likeCount"]) if "likeCount" in st else None,
        "comments": int(st["commentCount"]) if "commentCount" in st else None,
        "duration_s": dur, "is_short_candidate": (dur is not None and 0 < dur <= SHORT_S),
        "made_for_kids": ss.get("madeForKids"), "category_id": sn.get("categoryId", ""),
        "live_broadcast_content": sn.get("liveBroadcastContent", ""),
        "default_language": sn.get("defaultLanguage", ""), "default_audio_language": sn.get("defaultAudioLanguage", ""),
        "tags": "|".join(sn.get("tags", []) or []),
        "views_per_day": round(views / max(age, 1.0), 1) if views is not None else None,
    }


def median_for(rows, fmt=None):
    rs = [r for r in rows if r["views"] is not None and (fmt is None or r["is_short_candidate"] == fmt)]
    old = [r for r in rs if r["age_days"] >= 3]
    use, basis = (old, "age>=3d") if len(old) >= 3 else (rs, "all")
    if not use:
        return None, "none", 0
    return statistics.median(r["views"] for r in use), basis, len(use)


def write_csv(path, rows, fields):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


def save(final=False):
    STATE["phase_at_save"] = STATE["phase"]
    STATE["saved_at"] = iso(datetime.now(timezone.utc).replace(microsecond=0))
    # keywords
    with open(os.path.join(OUT, "keywords.txt"), "w", encoding="utf-8") as f:
        f.write("# keyword\ttype\twindows_days  (generated %s; type: seed_short / seed_longtail / expanded_from_titles)\n" % iso(NOW))
        for k, t, w in KEYWORDS:
            f.write("%s\t%s\t%s\n" % (k, t, ",".join(str(x) for x in w)))
    json.dump(RAW_SEARCH, open(os.path.join(OUT, "raw_search.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(VIDEOS, open(os.path.join(OUT, "raw_videos.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump(CHANNELS, open(os.path.join(OUT, "raw_channels.json"), "w", encoding="utf-8"), ensure_ascii=False)
    json.dump({"uploads": UPLOADS, "videos": UPVIDEOS}, open(os.path.join(OUT, "raw_uploads.json"), "w", encoding="utf-8"), ensure_ascii=False)
    write_csv(os.path.join(OUT, "search_hits.csv"), SEARCH,
              ["keyword", "window_days", "published_after", "fetched_at", "rank", "video_id", "channel_id", "title"])
    if not final:
        json.dump(dict(STATE, calls=dict(STATE["calls"])), open(os.path.join(OUT, "run_meta.json"), "w", encoding="utf-8"), indent=1)
        return
    # ---------- derived tables ----------
    hits = {}
    for s in SEARCH:
        h = hits.setdefault(s["video_id"], {"k7": set(), "k15": set(), "best_rank": 999})
        (h["k7"] if s["window_days"] == 7 else h["k15"]).add(s["keyword"])
        h["best_rank"] = min(h["best_rank"], s["rank"])
    # channel uploads rows + medians
    up_rows, ch_med = [], {}
    for cid, u in UPLOADS.items():
        rows = []
        for pos, vid in enumerate(u["items"], 1):
            v = UPVIDEOS.get(vid) or VIDEOS.get(vid)
            if not v or "publishedAt" not in v.get("snippet", {}):
                continue
            r = vrow(v)
            r["upload_position"] = pos
            r["fetch_groups"] = "|".join(u["groups"])
            rows.append(r)
        m_all = median_for(rows)
        m_long = median_for(rows, False)
        m_short = median_for(rows, True)
        ch_med[cid] = {"all": m_all, "long": m_long, "short": m_short, "rows": rows}
        for r in rows:
            m = m_short if r["is_short_candidate"] else m_long
            r["channel_median_views"] = m_all[0]
            r["channel_median_views_same_format"] = m[0]
            r["views_div_channel_median"] = round(r["views"] / m_all[0], 3) if m_all[0] and r["views"] is not None else None
            r["views_div_channel_median_same_format"] = round(r["views"] / m[0], 3) if m[0] and r["views"] is not None else None
        up_rows += rows
    # videos table
    vrows = []
    for vid, v in VIDEOS.items():
        if vid not in hits or "publishedAt" not in v.get("snippet", {}):
            continue
        r = vrow(v)
        h = hits[vid]
        r["keywords_7d"] = "|".join(sorted(h["k7"]))
        r["keywords_15d"] = "|".join(sorted(h["k15"]))
        r["n_keywords"] = len(h["k7"] | h["k15"])
        r["best_search_rank"] = h["best_rank"]
        ch = CHANNELS.get(r["channel_id"])
        if ch:
            cs = ch.get("statistics", {})
            hidden = cs.get("hiddenSubscriberCount", False)
            subs = int(cs["subscriberCount"]) if ("subscriberCount" in cs and not hidden) else None
            r["channel_subs"] = subs
            r["channel_subs_hidden"] = hidden
            r["channel_created_at"] = ch["snippet"].get("publishedAt", "")
            a = ch_age_days(ch)
            r["channel_age_days"] = round(a, 1) if a is not None else None
            r["channel_country"] = ch["snippet"].get("country", "")
            r["views_div_subs"] = round(r["views"] / subs, 3) if subs and r["views"] is not None else None
        cm = ch_med.get(r["channel_id"])
        if cm:
            m = cm["short"] if r["is_short_candidate"] else cm["long"]
            r["channel_median_views"] = cm["all"][0]
            r["channel_median_basis"] = "%s,n=%d" % (cm["all"][1], cm["all"][2])
            r["channel_median_views_same_format"] = m[0]
            r["views_div_channel_median"] = round(r["views"] / cm["all"][0], 3) if cm["all"][0] and r["views"] is not None else None
            r["views_div_channel_median_same_format"] = round(r["views"] / m[0], 3) if m[0] and r["views"] is not None else None
        vrows.append(r)
    vrows.sort(key=lambda r: -(r["views"] or 0))
    vf = ["video_id", "url", "title", "channel_id", "channel_title", "published_at", "fetched_at", "age_days", "views", "likes",
          "comments", "duration_s", "is_short_candidate", "made_for_kids", "category_id", "live_broadcast_content",
          "default_language", "default_audio_language", "keywords_7d", "keywords_15d", "n_keywords", "best_search_rank",
          "views_per_day", "channel_subs", "channel_subs_hidden", "channel_created_at", "channel_age_days", "channel_country",
          "views_div_subs", "channel_median_views", "channel_median_basis", "channel_median_views_same_format",
          "views_div_channel_median", "views_div_channel_median_same_format", "tags"]
    write_csv(os.path.join(OUT, "videos.csv"), vrows, vf)
    uf = ["channel_id", "channel_title", "fetch_groups", "upload_position", "video_id", "url", "title", "published_at", "fetched_at",
          "age_days", "views", "likes", "comments", "duration_s", "is_short_candidate", "made_for_kids", "category_id",
          "live_broadcast_content", "views_per_day", "channel_median_views", "channel_median_views_same_format",
          "views_div_channel_median", "views_div_channel_median_same_format", "tags"]
    write_csv(os.path.join(OUT, "uploads.csv"), up_rows, uf)
    # channels table
    by_ch = {}
    for r in vrows:
        by_ch.setdefault(r["channel_id"], []).append(r)
    crows = []
    for cid, ch in CHANNELS.items():
        sn, cs = ch.get("snippet", {}), ch.get("statistics", {})
        hidden = cs.get("hiddenSubscriberCount", False)
        a = ch_age_days(ch)
        sv = by_ch.get(cid, [])
        r = {"channel_id": cid, "title": sn.get("title", ""), "custom_url": sn.get("customUrl", ""),
             "created_at": sn.get("publishedAt", ""), "age_days": round(a, 1) if a is not None else None,
             "country": sn.get("country", ""), "subscribers": int(cs["subscriberCount"]) if ("subscriberCount" in cs and not hidden) else None,
             "hidden_subscriber_count": hidden, "video_count": int(cs.get("videoCount", 0)), "total_views": int(cs.get("viewCount", 0)),
             "made_for_kids": ch.get("status", {}).get("madeForKids"), "fetched_at": ch.get("_fetched_at"),
             "uploads_playlist": (ch.get("contentDetails", {}).get("relatedPlaylists") or {}).get("uploads", ""),
             "sample_videos": len(sv), "sample_views_sum": sum(x["views"] or 0 for x in sv),
             "sample_max_views": max((x["views"] or 0 for x in sv), default=0),
             "sample_shorts": sum(1 for x in sv if x["is_short_candidate"]),
             "groups": "|".join(GROUPS.get(cid, [])), "uploads_fetched": cid in UPLOADS}
        cm = ch_med.get(cid)
        if cm:
            rows = cm["rows"]
            r.update({"uploads_n": len(rows), "uploads_long": sum(1 for x in rows if not x["is_short_candidate"]),
                      "uploads_shorts": sum(1 for x in rows if x["is_short_candidate"]),
                      "median_views_all": cm["all"][0], "median_basis": "%s,n=%d" % (cm["all"][1], cm["all"][2]),
                      "median_views_long": cm["long"][0], "median_views_shorts": cm["short"][0],
                      "uploads_last_30d": sum(1 for x in rows if x["age_days"] <= 30),
                      "newest_upload": max((x["published_at"] for x in rows), default=""),
                      "oldest_upload_in_sample": min((x["published_at"] for x in rows), default=""),
                      "outliers_3x_same_format": sum(1 for x in rows if (x["views_div_channel_median_same_format"] or 0) >= 3)})
        crows.append(r)
    crows.sort(key=lambda r: -r["sample_views_sum"])
    cf = ["channel_id", "title", "custom_url", "created_at", "age_days", "country", "subscribers", "hidden_subscriber_count",
          "video_count", "total_views", "made_for_kids", "fetched_at", "uploads_playlist", "sample_videos", "sample_views_sum",
          "sample_max_views", "sample_shorts", "groups", "uploads_fetched", "uploads_n", "uploads_long", "uploads_shorts",
          "median_views_all", "median_basis", "median_views_long", "median_views_shorts", "uploads_last_30d", "newest_upload",
          "oldest_upload_in_sample", "outliers_3x_same_format"]
    write_csv(os.path.join(OUT, "channels.csv"), crows, cf)
    # summary counts for the notes
    v15 = [r for r in vrows if r["age_days"] <= 15]
    summ = {
        "videos_unique": len(vrows), "channels": len(crows), "uploads_channels": len(UPLOADS), "uploads_rows": len(up_rows),
        "search_calls": sum(1 for _ in RAW_SEARCH), "search_hits": len(SEARCH),
        "videos_1m_plus_age_le_15d": sum(1 for r in v15 if (r["views"] or 0) >= 1_000_000),
        "videos_1m_plus_age_le_7d": sum(1 for r in vrows if r["age_days"] <= 7 and (r["views"] or 0) >= 1_000_000),
        "videos_views_div_subs_ge_10": sum(1 for r in vrows if (r.get("views_div_subs") or 0) >= 10),
        "videos_shorts": sum(1 for r in vrows if r["is_short_candidate"]),
        "videos_mfk_true": sum(1 for r in vrows if r["made_for_kids"] is True),
        "channels_new_30d": sum(1 for r in crows if r["age_days"] is not None and r["age_days"] <= 30),
        "channels_new_365d": sum(1 for r in crows if r["age_days"] is not None and r["age_days"] <= 365),
        "channels_hidden_subs": sum(1 for r in crows if r["hidden_subscriber_count"]),
        "groups": {g: sum(1 for x in GROUPS.values() if g in x) for g in ("leader_top30", "new_le_365d_100k", "new_le_30d")},
        "groups_skipped_for_budget": SKIPPED,
        "videos_missing_from_videos_list": len(set(hits) - set(VIDEOS)),
    }
    STATE["summary"] = summ
    json.dump(dict(STATE, calls=dict(STATE["calls"])), open(os.path.join(OUT, "run_meta.json"), "w", encoding="utf-8"), indent=1)
    log("SUMMARY " + json.dumps(summ))


GROUPS = {}
SKIPPED = []


def main():
    if not KEY:
        log("NO_API_KEY")
        return
    log("start now=%s out=%s" % (iso(NOW), OUT))
    STATE["phase"] = "search_seed_7d"
    for k in SEEDS_SHORT:
        KEYWORDS.append((k, "seed_short", [7] + ([15] if k in CORE15 else [])))
    for k in SEEDS_LONG:
        KEYWORDS.append((k, "seed_longtail", [7] + ([15] if k in CORE15 else [])))
    for k, _, _ in list(KEYWORDS):
        search(k, 7)
    STATE["phase"] = "videos_seed"
    fetch_videos([s["video_id"] for s in SEARCH], VIDEOS)
    top = sorted(VIDEOS.values(), key=lambda v: -int(v.get("statistics", {}).get("viewCount", 0)))[:300]
    seen = set(k for k, _, _ in KEYWORDS)
    extra = related([v["snippet"]["title"] for v in top], seen, EXPAND)
    log("expanded: " + " ; ".join(extra))
    STATE["phase"] = "search_expanded_7d"
    for k in extra:
        KEYWORDS.append((k, "expanded_from_titles", [7]))
        search(k, 7)
    save()
    STATE["phase"] = "search_core_15d"
    for k in CORE15:
        search(k, 15)
    STATE["phase"] = "videos_channels"
    fetch_videos([s["video_id"] for s in SEARCH], VIDEOS)
    fetch_channels(sorted({v["snippet"]["channelId"] for v in VIDEOS.values()}))
    save()
    # ---------- uploads groups ----------
    STATE["phase"] = "uploads"
    sums, mx = Counter(), Counter()
    for v in VIDEOS.values():
        cid, views = v["snippet"]["channelId"], int(v.get("statistics", {}).get("viewCount", 0))
        sums[cid] += views
        mx[cid] = max(mx[cid], views)
    leaders = [c for c, _ in sums.most_common(30)]
    new365 = sorted([c for c in CHANNELS if (ch_age_days(CHANNELS[c]) or 1e9) <= 365 and mx[c] >= 100_000], key=lambda c: -mx[c])
    new30 = sorted([c for c in CHANNELS if (ch_age_days(CHANNELS[c]) or 1e9) <= 30], key=lambda c: -mx[c])
    for g, lst in (("leader_top30", leaders), ("new_le_365d_100k", new365), ("new_le_30d", new30)):
        for c in lst:
            GROUPS.setdefault(c, [])
            if g not in GROUPS[c]:
                GROUPS[c].append(g)
    order = list(dict.fromkeys(leaders + new30 + new365))
    log("uploads: leaders=%d new365_100k=%d new30=%d unique=%d units_now=%d" % (len(leaders), len(new365), len(new30), len(order), STATE["units"]))
    for n, cid in enumerate(order):
        if STATE["units"] + 2 > MAX_UNITS:
            SKIPPED.extend(order[n:])
            log("budget: skipped %d channels" % len(order[n:]))
            break
        pl = (CHANNELS[cid].get("contentDetails", {}).get("relatedPlaylists") or {}).get("uploads")
        if not pl:
            continue
        fetched = iso(datetime.now(timezone.utc).replace(microsecond=0))
        data = api("playlistItems", part="contentDetails,snippet", playlistId=pl, maxResults=50)
        pitems = data.get("items", [])
        ids = [it["contentDetails"]["videoId"] for it in pitems if it.get("contentDetails", {}).get("videoId")]
        UPLOADS[cid] = {"groups": GROUPS[cid], "fetched_at": fetched, "playlist_id": pl, "error": data.get("_error"),
                        "items": ids, "playlist_total": (data.get("pageInfo") or {}).get("totalResults")}
        need = [i for i in ids if i not in VIDEOS and i not in UPVIDEOS]
        if need:
            fetch_videos(need, UPVIDEOS)
        if n % 20 == 0:
            log("uploads %d/%d units %d" % (n, len(order), STATE["units"]))


if __name__ == "__main__":
    try:
        main()
    except QuotaStop as e:
        log("QUOTA_STOP " + str(e))
        STATE["quota_stop"] = STATE["quota_stop"] or str(e)
    except Exception:
        tb = traceback.format_exc()
        if KEY:
            tb = tb.replace(KEY, "***")
        log("ERROR " + tb)
        STATE["errors"].append({"fatal": tb[-2000:]})
    finally:
        STATE["phase"] = STATE["phase"] + "|final"
        try:
            save(final=True)
        except Exception:
            tb = traceback.format_exc()
            if KEY:
                tb = tb.replace(KEY, "***")
            log("SAVE_ERROR " + tb)
        log("DONE units=%d calls=%s" % (STATE["units"], dict(STATE["calls"])))
