from __future__ import annotations
import json, shlex, subprocess
from pathlib import Path
from pydantic import BaseModel, Field


class VisualQCResponse(BaseModel):
    passed: bool
    identity_score: float|None=None
    continuity_score: float|None=None
    performance_score: float|None=None
    camera_score: float|None=None
    findings: list[str]=Field(default_factory=list)


class CommandVisualQC:
    """Local VLM bridge (e.g. a Qwen3-VL wrapper). No network calls are made by CineFactory."""
    def __init__(self,command:str,timeout:int=600):
        self.argv=shlex.split(command);self.timeout=timeout
        if not self.argv:raise ValueError('visual QC command cannot be empty')
    def review(self,media_path:str|Path,contract:dict)->VisualQCResponse:
        req={'media_path':str(Path(media_path).resolve()),'contract':contract}
        proc=subprocess.run(self.argv,input=json.dumps(req,ensure_ascii=False),text=True,capture_output=True,timeout=self.timeout,check=False)
        if proc.returncode!=0:raise RuntimeError(f'visual QC command failed: {proc.stderr[-4000:]}')
        return VisualQCResponse.model_validate_json(proc.stdout)
