import shutil
import pytest
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.qc.technical import TechnicalQC


@pytest.mark.skipif(shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None, reason='ffmpeg missing')
def test_ffmpeg_slate_and_qc(tmp_path):
    media=FFmpegToolchain()
    p=media.make_slate('TEST',tmp_path/'test.mp4',duration=0.5,size='320x180')
    q=TechnicalQC(media).video(p,min_duration=0.2)
    assert q.passed
    assert q.probe.width==320
    assert q.probe.height==180
