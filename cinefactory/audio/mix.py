from __future__ import annotations

from pathlib import Path
from cinefactory.media.ffmpeg import FFmpegToolchain


class AudioMixer:
    def __init__(self, media: FFmpegToolchain | None=None): self.media=media or FFmpegToolchain()

    def replace_or_mix_voice(self, video: str|Path, voice: str|Path, output: str|Path, *, keep_original: bool=False) -> Path:
        v=Path(video).resolve(); a=Path(voice).resolve(); out=Path(output).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
        if keep_original:
            args=[self.media.ffmpeg,'-y','-i',str(v),'-i',str(a),'-filter_complex','[0:a][1:a]amix=inputs=2:duration=longest:weights=0.35 1.0[a]','-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-shortest',str(out)]
        else:
            args=[self.media.ffmpeg,'-y','-i',str(v),'-i',str(a),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-shortest',str(out)]
        self.media._run(args); return out
