from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone


def gpu_snapshot()->dict:
    exe=shutil.which("nvidia-smi")
    if not exe: return {"available":False,"reason":"nvidia-smi not found"}
    fields="name,memory.total,memory.used,utilization.gpu,temperature.gpu,power.draw"
    try:
        p=subprocess.run([exe,f"--query-gpu={fields}","--format=csv,noheader,nounits"],capture_output=True,text=True,timeout=8,check=True)
        gpus=[]
        for idx,line in enumerate(p.stdout.strip().splitlines()):
            vals=[x.strip() for x in line.split(',')]
            gpus.append({"index":idx,"name":vals[0],"vram_mb":float(vals[1]),"vram_used_mb":float(vals[2]),"utilization_pct":float(vals[3]),"temperature_c":float(vals[4]),"power_w":float(vals[5])})
        return {"available":True,"gpus":gpus,"captured_at":datetime.now(timezone.utc).isoformat()}
    except Exception as exc:
        return {"available":False,"reason":str(exc)}
