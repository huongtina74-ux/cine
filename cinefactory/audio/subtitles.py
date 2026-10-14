from __future__ import annotations

from pathlib import Path
from cinefactory.domain.models import ScriptSpec


def _stamp(seconds: float) -> str:
    ms=max(0,int(round(seconds*1000))); h,rem=divmod(ms,3600000); m,rem=divmod(rem,60000); s,ms=divmod(rem,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


class SubtitleBuilder:
    def from_script(self, script: ScriptSpec, output: str|Path, total_duration: float) -> Path:
        lines=[(scene.scene_id, line.speaker, line.text) for scene in script.scenes for line in scene.dialogue]
        out=Path(output); out.parent.mkdir(parents=True,exist_ok=True)
        if not lines:
            out.write_text('',encoding='utf-8'); return out
        slot=total_duration/len(lines); blocks=[]
        for i,(scene,speaker,text) in enumerate(lines,1):
            start=(i-1)*slot; end=max(start+0.5,i*slot-0.08)
            blocks.append(f"{i}\n{_stamp(start)} --> {_stamp(end)}\n{speaker}: {text}\n")
        out.write_text('\n'.join(blocks),encoding='utf-8'); return out
