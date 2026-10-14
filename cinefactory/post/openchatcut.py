from __future__ import annotations
import json, shlex, subprocess
from pathlib import Path
from .timeline import TimelineSpec


class OpenChatCutBridge:
    """Optional local OpenChatCut handoff without coupling CineFactory to its internal DB.

    A user-configured bridge command receives the CineFactory TimelineSpec JSON on stdin.
    This keeps OpenChatCut as the editorial owner while CineFactory remains semantic truth.
    """
    def __init__(self,command:str,timeout:int=3600):
        self.argv=shlex.split(command); self.timeout=timeout
        if not self.argv: raise ValueError('OpenChatCut bridge command cannot be empty')
    def send(self,timeline:TimelineSpec)->dict:
        proc=subprocess.run(self.argv,input=timeline.model_dump_json(),text=True,capture_output=True,timeout=self.timeout,check=False)
        if proc.returncode!=0: raise RuntimeError(f'OpenChatCut bridge failed: {proc.stderr[-4000:]}')
        if not proc.stdout.strip(): return {'ok':True}
        try:return json.loads(proc.stdout)
        except json.JSONDecodeError:return {'ok':True,'stdout':proc.stdout[-4000:]}
