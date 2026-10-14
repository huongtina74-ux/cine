"""Original procedurally composed 2-second sparkles/chime for v197 visual pilot.

No third-party recordings, no voice clone, no copyrighted game OST.
Sound FX sample, not professional scored song or dialogue.
"""
from pathlib import Path
import numpy as np,wave,json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/verification/v197_minecraft_art_direction"
RATE=48000
dur=2.0
t=np.arange(int(RATE*dur),dtype=np.float64)/RATE
audio=np.zeros(len(t),dtype=np.float64)
# Original three note motif C5-E5-G5, no sampled external audio.
for when,note,length,amp in (
    (.06,523.25,.42,.16),(.37,659.25,.52,.17),(.75,783.99,.65,.21),
    (1.46,493.88,.26,.13)):
    i0=int(when*RATE)
    n=min(len(audio)-i0,int(length*RATE))
    x=np.arange(n)/RATE
    attack=np.minimum(1.,x/.012)
    decay=np.exp(-x*5.8)
    envelope=attack*decay
    wavelet=np.sin(2*np.pi*note*x)+.24*np.sin(2*np.pi*2*note*x)+.08*np.sin(2*np.pi*3*note*x)
    audio[i0:i0+n]+=amp*envelope*wavelet
# Very light authored transient sparkle; no third-party loop or soundtrack.
rng=np.random.default_rng(197)
for when in (.1,.5,1.2):
    i0=int(when*RATE);n=1800
    env=np.exp(-np.arange(n)/260.)
    audio[i0:i0+n]+=.018*rng.standard_normal(n)*env
peak=max(1.,float(np.max(np.abs(audio)))/.87)
audio=np.int16(np.clip(audio/peak,-.95,.95)*32767)
wav=OUT/"original_quest_chime.wav"
with wave.open(str(wav),"wb") as w:
    w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(audio.tobytes())
# Renderer must have exactly 48 output frames; fail rather than fake final video.
frames=sorted((OUT/"frames").glob("v197_*.png"))
if len(frames)!=48:
    raise RuntimeError(f"EXPECTED_48_RENDERED_FRAMES_FOUND_{len(frames)}")
mp4=OUT/"minecraft_3shot_visual_pilot_with_original_sfx.mp4"
cmd=["ffmpeg","-hide_banner","-loglevel","error","-y",
     "-framerate","24","-start_number","1","-i",str(OUT/"frames"/"v197_%04d.png"),
     "-i",str(wav),"-c:v","libx264","-preset","fast","-crf","18",
     "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
     "-t","2.0","-movflags","+faststart",str(mp4)]
subprocess.run(cmd,check=True,timeout=120)
obj=json.loads(subprocess.check_output([
    "ffprobe","-v","error","-count_frames","-show_streams","-of","json",str(mp4)],
    text=True,timeout=30))
video=next(x for x in obj["streams"] if x.get("codec_type")=="video")
sound=next(x for x in obj["streams"] if x.get("codec_type")=="audio")
assert int(video.get("nb_read_frames"))==48 and video["width"]==960 and video["height"]==540
assert sound["codec_name"]=="aac"
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
contract={
    "status":"REAL_FIRST_PARTY_2S_STORYBOARD_PILOT_WITH_AUDIO",
    "video_path":str(mp4.resolve()),"video_sha256":hashfile(mp4),
    "original_synth_sfx_wav":str(wav.resolve()),"wav_sha256":hashfile(wav),
    "duration_seconds":2.0,"fps":24,"frames":48,
    "resolution":[960,540],"real_video_and_audio":True,
    "competitor_video_decoded_and_analyzed":False,
    "production_qualified":False,
    "professional_story_acting_musical_scoring_approved":False,
    "skin_artist_and_facial_animation_signoff":False,
    "licence_human_review_complete":False,
}
(OUT/"pilot_media_evidence.json").write_text(json.dumps(contract,indent=2),encoding="utf-8")
print("V197_REAL_ANIMATED_PILOT",json.dumps(contract),flush=True)
