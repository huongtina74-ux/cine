import shutil
import pytest
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.post.mastering import MasteringService


@pytest.mark.skipif(shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None, reason='ffmpeg missing')
def test_mastering_hits_requested_resolution(tmp_path):
    media=FFmpegToolchain()
    src=media.make_slate('X',tmp_path/'src.mp4',duration=0.35,size='320x180')
    out,q=MasteringService(media).master(src,tmp_path/'master.mp4',width=640,height=360,fps=24)
    assert q.passed
    assert q.probe.width==640 and q.probe.height==360
