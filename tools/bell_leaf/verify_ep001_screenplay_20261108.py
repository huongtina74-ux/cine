#!/usr/bin/env python3
"""EP001 Bell & Leaf draft integrity audit: exact shot timings, five acts and Canon safety.

NOT an acceptance of runtime speech duration, character assets, human story quality
or publication. The 10-second slots are target edit lengths, not actual rendered video.
"""
from __future__ import annotations
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EP=ROOT/"docs/story/bell_leaf/ep001_screenplay"
PATTERN="EP001_ACT_*.md"
SHOT=re.compile(r"(?m)^\*\*S(\d{3}) \[(\d\d):(\d\d)–(\d\d):(\d\d)\]\*\* (.+)$")
SCENE=re.compile(r"(?m)^### SC-(\d{3}) — (.+?) \| (\d\d):(\d\d)–(\d\d):(\d\d)$")
STORY=EP/"EP001_STORY_QUALITY_PLAN_v1.json"
PLAN_TEST_REVIEW="INDEPENDENT_STORY_EDITOR_REVIEW_REQUIRED"


def to_seconds(mm, ss):
    return int(mm)*60+int(ss)


def analyze():
    paths=sorted(EP.glob(PATTERN))
    assert len(paths)==5, f"EXPECTED 5 ACTS, found {len(paths)}"
    scenes=[];shots=[];words=[];content=[]
    for file in paths:
        text=file.read_text(encoding="utf-8-sig")
        content.append(text)
        scenes.extend(SCENE.findall(text))
        shots.extend(SHOT.findall(text))
    issues=[];spoken_by_scene=Counter();all_lines=[]
    for i,(code,start_m,start_s,end_m,end_s,action) in enumerate(shots,1):
        begin,end=to_seconds(start_m,start_s),to_seconds(end_m,end_s)
        if int(code)!=i or begin!=(i-1)*10 or end!=i*10 or end-begin!=10:
            issues.append(f"SHOT_TIME_OR_ID_ERROR_S{i:03d}")
        if len(action)<60:
            issues.append(f"UNDERDESCRIBED_PHYSICAL_ACTION_S{i:03d}")
        all_lines.append(action.strip().casefold())
        # Speech in these prose directions uses single or double quotes; count
        # without claiming exact TTS seconds or that all text is voice.
        quoted=re.findall(r"""(?<!\w)['"‘“](.+?)['"’”]""",action)
        spoken=sum(len(re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?",q)) for q in quoted)
        words.append(spoken)
        spoken_by_scene[1+(i-1)//9]+=spoken
        if spoken>34:
            issues.append(f"DIALOGUE_LONG_FOR_ONE_10SEC_SHOT_S{i:03d}_{spoken}_WORDS")
    for i,(scene_no,title,start_m,start_s,end_m,end_s) in enumerate(scenes,1):
        begin,end=to_seconds(start_m,start_s),to_seconds(end_m,end_s)
        if int(scene_no)!=i or begin!=(i-1)*90 or end!=i*90:
            issues.append(f"SCENE_TIME_OR_ID_ERROR_SC{i:03d}")
    all_content="\n".join(content)
    if re.search(r"\bIsel\b|\bVarr\b|Earth was forbidden|ancient Earth gate",all_content,re.I):
        issues.append("PUBLIC_SHOWRUNNER_SECRET_OR_OLD_CANON_DETECTED")
    if "ASSET_PENDING" not in all_content and "asset hold" not in all_content.lower():
        issues.append("AILA_APPROVAL_HOLD_NOT_RECORDED")
    if len(set(all_lines))!=len(all_lines):
        issues.append("EXACT_DUPLICATED_ACTION_LINES")
    if len(scenes)!=30:
        issues.append("NOT_30_SCENES")
    if len(shots)!=270:
        issues.append("NOT_270_SHOTS")
    if not STORY.is_file():
        issues.append("MISSING_EP001_QUALITY_PLAN")
    else:
        p=json.loads(STORY.read_text(encoding="utf-8-sig"))
        if len(p.get("scenes",[]))!=30 or len(p.get("beats",[]))!=15:
            issues.append("PLAN_SCENE_BEAT_MISMATCH")
        for i,s in enumerate(p["scenes"],1):
            if s["scene_id"]!=f"SC-{i:03d}" or s["start_s"]!=(i-1)*90:
                issues.append("SCENE_PLAN_TIMING_MISMATCH")
    return {
        "status":"INDEPENDENT_STORY_EDITOR_REVIEW_REQUIRED" if not issues else "BLOCKED",
        "episode_id":"BL-0001","niche_id":"magical_witch_family_stories",
        "act_files":[p.name for p in paths],
        "scenes":len(scenes),"shots":len(shots),
        "timed_script_seconds":len(shots)*10,
        "speech_words_quoted_approx":sum(words),
        "mean_quoted_words_per_10s":round(sum(words)/len(shots),2) if shots else 0,
        "dialogue_quiet_shots":sum(w==0 for w in words),
        "max_words_one_shot":max(words,default=0),
        "scene_speech_word_count":dict(spoken_by_scene),
        "problems":issues,
        "voice_lipsync_qc":"NOT_PRODUCED",
        "a2_dialogue_native_review":"PENDING",
        "real_timing_readthrough":"PENDING",
        "story_editor_approval":"PENDING",
        "new_character_assets":"PENDING",
        "disclaimer":"270x10s target storyboard cannot establish actual 45min final cut, dialogue intelligibility, identity continuity or originality."
    }


if __name__=="__main__":
    result=analyze()
    print(json.dumps(result,ensure_ascii=True,indent=2))
    if "--out" in sys.argv:
        p=Path(sys.argv[sys.argv.index("--out")+1])
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    sys.exit(0 if result["status"]!="BLOCKED" else 2)
