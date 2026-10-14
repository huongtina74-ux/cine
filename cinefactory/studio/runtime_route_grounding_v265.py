"""v265: prevent declarative capability candidates from impersonating local executables.

Narrow guard for Blender and FFmpeg routes only. Does not install software or certify
render quality; checks that a candidate executable exists and launches --version.
Intended for professional-governance StudioPlan before the ProductionCompiler.
"""
from __future__ import annotations
import os
import shutil
import subprocess
from pathlib import Path
from cinefactory.studio.control_plane import StudioPlan

VERIFIED_BACKENDS={
    "blender.local":"blender",
    "ffmpeg.editorial":"ffmpeg",
}
def backend_executable_probe(backend:str)->dict:
    if backend not in VERIFIED_BACKENDS:
        return {"backend":backend,"type":"NOT_A_RUNTIME_PROBED_BACKEND",
                "path":None,"executed":False,"available":None}
    cmd=VERIFIED_BACKENDS[backend]
    search=[]
    if backend=="blender.local":
        for key in ("CINEFACTORY_BLENDER_EXECUTABLE","BLENDER_BIN"):
            if os.environ.get(key):search.append(os.environ[key])
        for directory in (Path("C:/Program Files/Blender Foundation"),
                          Path("C:/Program Files (x86)/Blender Foundation")):
            if directory.is_dir():
                search.extend(str(p) for p in directory.glob("Blender */blender.exe"))
    if backend=="ffmpeg.editorial":
        configured=os.environ.get("CINEFACTORY_FFMPEG_EXECUTABLE")
        if configured:search.append(configured)
        search.append(str(Path.home()/"ffmpeg"/"bin"/"ffmpeg.exe"))
    which=shutil.which(cmd)
    if which:search.append(which)
    for path in dict.fromkeys(search):
        exe=Path(path)
        if not exe.is_file():continue
        try:
            p=subprocess.run([str(exe),"-version" if backend=="ffmpeg.editorial" else "--version"],capture_output=True,
                             text=True,timeout=6,check=False)
        except (OSError,subprocess.TimeoutExpired):
            continue
        if p.returncode==0:
            stdout=(p.stdout+"\n"+p.stderr).strip()[:160]
            return {"backend":backend,"type":"RUNTIME_VERSION_PROBED",
                    "path":str(exe),"executed":True,"available":True,
                    "version_line":stdout.splitlines()[0] if stdout else ""}
    return {"backend":backend,"type":"RUNTIME_EXECUTABLE_NOT_VERIFIED",
            "path":None,"executed":False,"available":False}

def ground_professional_plan(plan:StudioPlan,probe=backend_executable_probe)->StudioPlan:
    inspected={}
    newsegments=[]
    planblockers=list(plan.blockers)
    for item in plan.segments:
        newroutes=[];stage_blockers=list(item.blockers)
        for route in item.routes:
            backend=route.selected_capability_id
            if backend not in VERIFIED_BACKENDS:
                newroutes.append(route)
                continue
            if backend not in inspected:inspected[backend]=probe(backend)
            evidence=inspected[backend]
            if evidence["available"] is not True:
                reason=f"{item.segment.segment_id}:RUNTIME_EXECUTABLE_UNVERIFIED:{backend}"
                stage_blockers.append(reason)
                if reason not in planblockers:planblockers.append(reason)
                newroutes.append(route.model_copy(update={
                    "executable":False,
                    "warnings":list(route.warnings)+["LOCAL_RUNTIME_NOT_PROVED_DO_NOT_RENDER"],
                }))
            else:newroutes.append(route)
        newsegments.append(item.model_copy(update={
            "routes":newroutes,
            "blockers":list(dict.fromkeys(stage_blockers)),
            "executable":not stage_blockers,
        }))
    return plan.model_copy(update={
        "segments":newsegments,
        "blockers":list(dict.fromkeys(planblockers)),
        "executable":not planblockers,
    })
