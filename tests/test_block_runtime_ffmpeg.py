import shutil,pytest
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.block_animation.runtime import BlockAnimationRuntime
def test_concat(tmp_path):
    if not shutil.which('ffmpeg'):pytest.skip()
    f=FFmpegToolchain(); a=f.make_slate('A',tmp_path/'a.mp4',duration=.35,size='320x180'); b=f.make_slate('B',tmp_path/'b.mp4',duration=.35,size='320x180'); r=BlockAnimationRuntime(tmp_path).assemble_episode({'output_path':str(tmp_path/'o.mp4'),'shots':[{'order':0,'path':str(a)},{'order':1,'path':str(b)}]}); assert r['qc_passed'] and r['duration']>.5
