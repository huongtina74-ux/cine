from __future__ import annotations

import json
from pathlib import Path


class IncrementalTimeline:
    """Crash-safe rough-cut journal that can be updated as shots are accepted."""
    def __init__(self,path:Path)->None:
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        if not self.path.exists(): self._write({"revision":0,"shots":{}})

    def _read(self)->dict:
        return json.loads(self.path.read_text(encoding="utf-8"))
    def _write(self,data:dict)->None:
        tmp=self.path.with_suffix(self.path.suffix+".tmp")
        tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8"); tmp.replace(self.path)

    def accept_shot(self,*,shot_id:str,path:str,order:int,duration_seconds:float|None=None,edit_intent:str|None=None)->dict:
        data=self._read(); data["revision"]+=1
        data["shots"][shot_id]={"shot_id":shot_id,"path":path,"order":order,"duration_seconds":duration_seconds,"edit_intent":edit_intent,"status":"ACCEPTED"}
        self._write(data); return data

    def remove_shot(self,shot_id:str)->dict:
        data=self._read(); data["revision"]+=1; data["shots"].pop(shot_id,None); self._write(data); return data

    def ordered(self)->list[dict]:
        return sorted(self._read()["shots"].values(),key=lambda x:(x["order"],x["shot_id"]))
