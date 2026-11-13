"""Low-quota daily Minecraft pass (read-only, official YouTube Data API v3).
Used when the day's quota was already spent by another job: NO search.list.
  1. re-snapshot (videos.list) yesterday's 1M+/outlier/explosive/small-channel lists
  2. channels.list + last-50 uploads for EVERY watchlist channel
Hard cap MAX_UNITS; stops cleanly on quotaExceeded. Key read from .env in-process only; never printed/written.
"""
import csv, json, os, re, sys, time, traceback
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import urlopen

BASE = r"C:\Users\ADMIN\Downloads\cine_niche_survey"
PREV = os.path.join(BASE, "out", "2026-11-11_api_dataset", "analysis")
NOW = datetime.now(timezone.utc).replace(microsecond=0)
OUT = os.path.join(BASE, "out", NOW.strftime("%Y-%m-%d") + "_mc_daily_lite")
os.makedirs(OUT, exist_ok=True)
LOG = os.path.join(OUT, "progress.log")
MAX_UNITS = int(os.environ.get("MC_MAX_UNITS", "190"))
WATCH = """UC-Diq5SjWZDol8C0_E_1Y7A,UCc2RL8jvY1rJPuCnJVsIQWw,UCJHBJ7F-nAIlMGolm0Hu4vg,UCToxKVrkEuAONR4rFIJ_DyQ,UCkXiYodooLCuCmPEhrz32Ig,UC8r4SVVsfj8YfPCu9I9LOAw,UCZccjtuYFXgnHJZuti2PrhQ,UCo5PIvuZMD14ij_8fQXhvSg,UCHu4LZoHcIwOT16wIjYl0Lw,UCN1IH9Yuz3WlVDJ3jDIAI5A,UCkB4kByxpTDtGDT56RZfXsg,UCyUKWmArpcU2YeJFYfqVSSw,UCkTI_fxFyWU1U-iInYnMt2A,UCU9XwWmgsDdGRHXjrE0ewmQ,UCK0DXOEQLQ_YkP2x1jddjsw,UCVFgxz89Ond56851oZHAcrg,UCDCDdtu2ldfNCJJfrLEqRWw,UC8Cp4n7CJBoY4sMOWdTSAGA,UCCQaqq9L_IaPw3FyLW1Rn5A,UC8BAM9FulzAucO3ENpk-yqA,UC9rNiDYJAsDRbYuQO2wvihQ,UCI4jqHZzPqg5aQEJSC4zn1g,UC55HQXkPybptGkfRfniM77g,UCXwHTTvZxWXmoiXsitx8iog,UCfrE3ETIQO906PeaUZoDC_w,UC6KDePyRnTj5EIUcJvCXVmQ,UCND-rtZrbxwcyz4qA5Bppkg,UCKOKtUXMTKpO9RlKfT7HwgA,UCQyDIp03A6tsck3w29gflfg,UCk2uxbWi5py_iJXaEsh2YRA,UC1jKdni3foWJbQ5R7b3-xnw,UC4Ro4ns3l_0Je2EPpE47Ryw,UCZDmrAO-bnBxU4_LiH40CjA,UCGj5HppBXUUFZ7CoyNUNu2Q,UC6KHf_WmgxTGKBAGckDUHHw,UCCqUgUPWNhUzrmGE1r4p2kA,UCZikV3UKwZZKoE0hG9YquPQ,UCoetJ6BMwV4gpCnW88fIEyw,UCgzVBte0O0Iju1ACoNbdINQ,UCktAim4t-NivVXjETAQxvaA,UCVnUc2TZocno9t2YW5x6cRA,UCRaGNwQG_rNsODhuKRZ4dlw,UCC7TZe3whbuNtlWE8WYrPmQ,UC1HrYKD5Cd3XPJvK7DsrG8A""".split(",")
EXTRA = [c for c in os.environ.get("MC_EXTRA_CH", "").split(",") if c]
DUR = re.compile(r"^P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$")
STATE = {"units": 0, "quota_stop": None, "errors": 0}


def log(m):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(datetime.now(timezone.utc).strftime("%H:%M:%S ") + m + "\n")


def key():
    for line in open(os.path.join(BASE, ".env"), encoding="utf-8", errors="ignore"):
        m = re.match(r"\s*(YOUTUBE_DATA_API_KEY|YOUTUBE_API_KEY|GOOGLE_API_KEY)\s*=\s*['\"]?([^'\"\s#]+)", line)
        if m:
            return m.group(2)


KEY = key()


class Stop(Exception):
    pass


def api(ep, **p):
    if STATE["units"] + 1 > MAX_UNITS:
        raise Stop("cap %d" % MAX_UNITS)
    STATE["units"] += 1
    p["key"] = KEY
    try:
        with urlopen("https://www.googleapis.com/youtube/v3/" + ep + "?" + urlencode(p), timeout=30) as s:
            return json.load(s)
    except HTTPError as e:
        reason = ""
        try:
            reason = (json.loads(e.read().decode("utf-8", "ignore"))["error"]["errors"][0]).get("reason", "")
        except Exception:
            pass
        if e.code == 403 and (not reason or "uota" in reason or "imit" in reason):
            STATE["quota_stop"] = "HTTP %d %s" % (e.code, reason)
            raise Stop(STATE["quota_stop"]) from None
        STATE["errors"] += 1
        return {"items": []}
    except Exception as e:
        STATE["errors"] += 1
        log("net " + type(e).__name__)
        return {"items": []}


def secs(d):
    m = DUR.fullmatch(d or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (86400, 3600, 60, 1))) if m else None


def vrow(it, fetched):
    sn, st, cd = it.get("snippet", {}), it.get("statistics", {}), it.get("contentDetails", {})
    return {"video_id": it["id"], "title": sn.get("title", ""), "channel_id": sn.get("channelId", ""),
            "channel": sn.get("channelTitle", ""), "published_at": sn.get("publishedAt", ""), "fetched_at": fetched,
            "views": st.get("viewCount", ""), "likes": st.get("likeCount", ""), "comments": st.get("commentCount", ""),
            "duration_s": secs(cd.get("duration")), "audio_lang": sn.get("defaultAudioLanguage", ""),
            "lang": sn.get("defaultLanguage", ""), "live": sn.get("liveBroadcastContent", "")}


def videos(ids):
    out = []
    for i in range(0, len(ids), 50):
        f = NOW.isoformat()
        f = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        for it in api("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).get("items", []):
            out.append(vrow(it, f))
    return out


def wcsv(name, rows):
    if not rows:
        return
    keys = list(rows[0].keys())
    with open(os.path.join(OUT, name), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    if not KEY:
        log("NO_API_KEY")
        return
    log("start %s cap=%d" % (NOW.isoformat(), MAX_UNITS))
    ids, src = [], {}
    for fn in ("C_exploding_le15d_1m.csv", "A_outliers_3x_median.csv", "A_first5d_explosive.csv", "C_small_channel_vs_subs.csv"):
        for r in csv.DictReader(open(os.path.join(PREV, fn), encoding="utf-8-sig")):
            if r["video_id"] not in src:
                ids.append(r["video_id"])
                src[r["video_id"]] = {"prev_views": r["views"], "prev_age_d": r["age_days"], "prev_list": fn.split(".")[0]}
            else:
                src[r["video_id"]]["prev_list"] += "|" + fn.split(".")[0]
    log("resnap ids %d" % len(ids))
    rs = []
    try:
        rs = videos(ids)
        for r in rs:
            r.update(src.get(r["video_id"], {}))
        wcsv("resnapshot.csv", rs)
        log("resnap rows %d units %d" % (len(rs), STATE["units"]))
        chs = []
        allc = list(dict.fromkeys(WATCH + EXTRA))
        for i in range(0, len(allc), 50):
            f = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
            for it in api("channels", part="snippet,statistics,contentDetails", id=",".join(allc[i:i + 50])).get("items", []):
                sn, st = it["snippet"], it.get("statistics", {})
                chs.append({"channel_id": it["id"], "title": sn.get("title", ""), "handle": sn.get("customUrl", ""),
                            "created": sn.get("publishedAt", ""), "country": sn.get("country", ""),
                            "subs": "" if st.get("hiddenSubscriberCount") else st.get("subscriberCount", ""),
                            "videos": st.get("videoCount", ""), "total_views": st.get("viewCount", ""), "fetched_at": f,
                            "uploads": (it.get("contentDetails", {}).get("relatedPlaylists") or {}).get("uploads", ""),
                            "is_extra": it["id"] in EXTRA and it["id"] not in WATCH})
        wcsv("watch_channels.csv", chs)
        log("channels %d units %d" % (len(chs), STATE["units"]))
        ups = []
        for n, c in enumerate(chs):
            if not c["uploads"]:
                continue
            pl = api("playlistItems", part="contentDetails", playlistId=c["uploads"], maxResults=50)
            vids = [x["contentDetails"]["videoId"] for x in pl.get("items", [])]
            for pos, r in enumerate(videos(vids), 1):
                r["upload_pos"] = pos
                ups.append(r)
            if n % 10 == 0:
                log("uploads %d/%d units %d" % (n, len(chs), STATE["units"]))
                wcsv("watch_uploads.csv", ups)
        wcsv("watch_uploads.csv", ups)
    except Stop as e:
        log("STOP " + str(e))
        wcsv("resnapshot.csv", rs) if rs else None
    finally:
        json.dump({"started": NOW.isoformat(), "units": STATE["units"], "quota_stop": STATE["quota_stop"],
                   "errors": STATE["errors"], "search_calls": 0}, open(os.path.join(OUT, "run_meta.json"), "w"), indent=1)
        log("DONE units=%d quota_stop=%s errors=%d" % (STATE["units"], STATE["quota_stop"], STATE["errors"]))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        tb = traceback.format_exc()
        log("ERROR " + (tb.replace(KEY, "***") if KEY else tb))
