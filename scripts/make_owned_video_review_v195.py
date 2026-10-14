from __future__ import annotations
"""Review-only original CineFactory video frame proof (no competitor frames).

Outputs an offline contact sheet of six actual decoded owned video frames,
time/frame index, media and PNG hashes for a human review of pixel observations.
No generated/synthetic replacement frame is presented as decoded source.
"""
import hashlib,json,sys
from pathlib import Path
import cv2
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))

SOURCE_VIDEOS=[
    ("V185 original studio video",
     ROOT/"data/verification/v185_alignment_reid/two_actors_speech_audible.mp4"),
    ("V186 original studio video",
     ROOT/"data/verification/v186_multishot_second/blender/renders/block_animation/shots/0000_SPEAKERS_AB.mp4"),
]

def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    target=ROOT/"data/verification/v195_video_production_intelligence"
    target.mkdir(parents=True,exist_ok=True)
    frame_dir=target/"owned_frame_evidence"
    frame_dir.mkdir(parents=True,exist_ok=True)
    tiles=[]
    ledger=[]
    for row,(name,path) in enumerate(SOURCE_VIDEOS):
        capture=cv2.VideoCapture(str(path))
        if not capture.isOpened():raise RuntimeError("OWNED_FRAME_PROOF_NOT_DECODABLE")
        fps=float(capture.get(cv2.CAP_PROP_FPS))
        count=int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if count!=90:raise RuntimeError("ORIGINAL_VIDEO_FRAME_COUNT_CHANGED")
        for col,frameidx in enumerate((12,36,60)):
            capture.set(cv2.CAP_PROP_POS_FRAMES,frameidx)
            ok,img=capture.read()
            if not ok or img is None:raise RuntimeError("DECODER_FAILED_REQUESTED_FRAME")
            h,w=img.shape[:2]
            image=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
            frame_path=frame_dir/f"owned_video_{row+1:02d}_frame_{frameidx:04d}.png"
            image.save(frame_path)
            tile=Image.new("RGB",(w,h+46),(255,255,255))
            tile.paste(image,(0,46))
            drawer=ImageDraw.Draw(tile)
            drawer.text((8,5),f"{name} | frame {frameidx:02d}",fill=(0,0,0))
            drawer.text((8,22),f"{frameidx/fps:.3f}s | {w}x{h} | source SHA {sha(path)[:14]}",fill=(40,40,40))
            tiles.append(tile)
            ledger.append({"source":str(path.resolve()),
                           "source_sha256":sha(path),
                           "frame_index":frameidx,
                           "time_seconds":round(frameidx/fps,4),
                           "decoded_frame_png":str(frame_path.resolve()),
                           "decoded_frame_png_sha256":sha(frame_path),
                           "source_is_owned":True,
                           "human_artistic_quality_review_complete":False})
        capture.release()
    tile_width=max(x.width for x in tiles)
    tile_height=max(x.height for x in tiles)
    sheet=Image.new("RGB",(tile_width*3,tile_height*2),(235,235,235))
    for i,item in enumerate(tiles):
        sheet.paste(item,((i%3)*tile_width,(i//3)*tile_height))
    dst=target/"owned_actual_decoded_frames_review_v195.jpg"
    sheet.save(dst,quality=93)
    (target/"owned_frame_evidence_manifest_v195.json").write_text(
        json.dumps({"status":"REAL_OWNED_MEDIA_FRAME_QC_PENDING_HUMAN_REVIEW",
           "frame_evidence":ledger,"contact_sheet_path":str(dst.resolve()),
           "contact_sheet_sha256":sha(dst),
           "owned_frame_count":len(ledger),"external_copyright_media_saved":False,
           "creative_quality_passed":False},
           ensure_ascii=False,indent=2),encoding="utf-8")
    print("V195_OWNED_FRAME_PROOF_PASS","actual_frames",len(ledger),
          "review_contact_sheet",str(dst), "contact_sha",sha(dst)[:18])

if __name__=="__main__":main()
