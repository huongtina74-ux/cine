"""Read-only public YouTube storyboard snapshots for a scored shortlist.

This is not video playback, audio inspection or transcription. Read only
official i.ytimg.com/i9.ytimg.com JPEG storyboard endpoints discovered by
yt-dlp (not arbitrary user-supplied URLs). Copyrighted stills are ONLY stored
in quarantined research evidence, never training or production assets.
"""
from __future__ import annotations
import hashlib
import io
import json
import urllib.parse
import urllib.request
from pathlib import Path
from PIL import Image,ImageDraw
from typing import Callable
from .daily_youtube_breakout_v199 import VIDEO_RE

ALLOWED_STORYBOARD_HOSTS={"i.ytimg.com","i9.ytimg.com"}
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        raise ValueError("STORYBOARD_REDIRECT_NOT_ALLOWED")

def _pull_jpg(url:str,max_bytes:int=2000000)->bytes:
    target=urllib.parse.urlsplit(url)
    if target.scheme!="https" or target.hostname not in ALLOWED_STORYBOARD_HOSTS:
        raise ValueError("UNTRUSTED_STORYBOARD_URL")
    if not target.path.startswith("/sb/"):
        raise ValueError("STORYBOARD_NOT_ORIGINAL_YOUTUBE_STORYBOARD")
    opener=urllib.request.build_opener(_NoRedirect)
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"},method="GET")
    with opener.open(req,timeout=12) as rsp:
        blob=rsp.read(max_bytes+1)
    if not 30<len(blob)<=max_bytes:
        raise ValueError("STORYBOARD_BAD_LENGTH")
    # PIL decode verifies actual readable image, not an HTML block page.
    with Image.open(io.BytesIO(blob)) as img:
        img.verify()
    return blob

def inspect_sparse_storyboards(video_id:str,root:Path,
                                *,max_pages:int=3,
                                extractor:Callable|None=None)->dict:
    if not VIDEO_RE.fullmatch(video_id):
        raise ValueError("MALFORMED_VIDEO_ID")
    if max_pages<1 or max_pages>5:
        raise ValueError("STORYBOARD_PAGE_BUDGET")
    folder=Path(root).resolve()/"data/research/youtube_breakout/storyboards"/video_id
    summary={
        "video_id":video_id,
        "source_level":"OFFICIAL_LOW_RES_YOUTUBE_STORYBOARD_ONLY",
        "public_storyboard_actually_fetched":False,
        "fully_played_or_decoded_video":False,
        "audio_or_dialogue_heard":False,
        "motion_acting_or_cut_timing_proven":False,
        "production_reuse_or_training_permitted":False,
        "shots":[],"source_page_hashes":[],
        "status":"NO_ACCESSIBLE_PUBLIC_STORYBOARD",
        "errors":[],
    }
    try:
        if extractor is None:
            import yt_dlp
            with yt_dlp.YoutubeDL({"quiet":True,"no_warnings":True,
                                   "skip_download":True,"noplaylist":True,
                                   "socket_timeout":12}) as y:
                item=y.extract_info("https://www.youtube.com/watch?v="+video_id,download=False)
        else:
            item=extractor(video_id)
        if item.get("id")!=video_id:
            raise ValueError("VIDEO_ID_MISMATCH")
        formats=[x for x in item.get("formats",[]) if str(x.get("format_id","")).startswith("sb")
                 and x.get("fragments") and int(x.get("rows") or 0)>0
                 and int(x.get("columns") or 0)>0]
        if not formats:
            raise ValueError("NO_PUBLIC_STORYBOARD_FORMAT")
        # Prefer 320x180 frames, as used in v198; low-res, bounded.
        chosen=sorted(formats,key=lambda x:(int(x.get("width") or 0),
                                            int(x.get("height") or 0)),reverse=True)[0]
        fragments=chosen["fragments"]
        indices=sorted({round(i*(len(fragments)-1)/max(1,max_pages-1))
                       for i in range(max_pages)})
        tile_w=int(chosen.get("width") or 0)
        tile_h=int(chosen.get("height") or 0)
        columns=int(chosen.get("columns") or 0)
        rows=int(chosen.get("rows") or 0)
        if tile_w<60 or tile_w>400 or tile_h<40 or tile_h>240 or columns*rows>30:
            raise ValueError("STORYBOARD_LAYOUT_REJECTED")
        output=Image.new("RGB",(tile_w*3,(tile_h+24)*len(indices)),"white")
        drawer=ImageDraw.Draw(output)
        for k,page in enumerate(indices):
            fragment=fragments[page]
            try:
                blob=_pull_jpg(fragment["url"])
                with Image.open(io.BytesIO(blob)) as image:
                    frame=image.convert("RGB")
                if frame.width<tile_w*columns or frame.height<tile_h*rows:
                    raise ValueError("INVALID_THUMBNAIL_SHEET_SIZE")
                page_sha=hashlib.sha256(blob).hexdigest()
                folder.mkdir(parents=True,exist_ok=True)
                page_file=folder/f"page_{page:03d}_{page_sha[:12]}.jpg"
                if page_file.exists() and hashlib.sha256(page_file.read_bytes()).hexdigest()!=page_sha:
                    raise ValueError("EXISTING_PAGE_TAMPERED")
                if not page_file.exists():
                    page_file.write_bytes(blob)
                summary["source_page_hashes"].append({"file":str(page_file),
                                                      "sha256":page_sha,
                                                      "page_index":page})
                approx_page_start=sum(float(f.get("duration") or 0)
                                      for f in fragments[:page])
                samples=sorted({0,(columns*rows)//2,columns*rows-1})
                for col,idx in enumerate(samples):
                    idx=min(idx,columns*rows-1)
                    crop=frame.crop(((idx%columns)*tile_w,(idx//columns)*tile_h,
                                     (idx%columns+1)*tile_w,(idx//columns+1)*tile_h))
                    output.paste(crop,(col*tile_w,k*(tile_h+24)+24))
                    seconds=approx_page_start+(idx+.5)*float(fragment.get("duration") or 0)/(columns*rows)
                    drawer.text((col*tile_w+5,k*(tile_h+24)+5),
                                f"Approx {seconds/60:.1f}m p{page} t{idx}",fill="black")
                    summary["shots"].append({
                        "approx_time_seconds":round(seconds,1),
                        "page_index":page,"tile_index":idx,
                        "source_page_sha256":page_sha,
                        "confidence":"PUBLIC_SPARSE_STORYBOARD_FRAME_NOT_MOTION",
                    })
            except Exception as e:
                summary["errors"].append(type(e).__name__+":"+str(e)[:150])
        if summary["shots"]:
            folder.mkdir(parents=True,exist_ok=True)
            contact=folder/"public_sparse_storyboard_research.jpg"
            output.save(contact,quality=88)
            summary["public_storyboard_actually_fetched"]=True
            summary["status"]="PARTIAL_PUBLIC_STORYBOARD_FRAMES_VIEWABLE"
            summary["review_sheet_file"]=str(contact)
            summary["review_sheet_sha256"]=hashlib.sha256(contact.read_bytes()).hexdigest()
    except Exception as exc:
        summary["errors"].append(type(exc).__name__+":"+str(exc)[:150])
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"storyboard_provenance.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    return summary
