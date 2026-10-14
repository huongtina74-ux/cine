from pathlib import Path
from cinefactory.turbo.incremental_editor import IncrementalTimeline


def test_incremental_timeline(tmp_path: Path):
    tl=IncrementalTimeline(tmp_path/'timeline.json')
    tl.accept_shot(shot_id='S2',path='b.mp4',order=2)
    tl.accept_shot(shot_id='S1',path='a.mp4',order=1)
    assert [x['shot_id'] for x in tl.ordered()]==['S1','S2']
    assert tl._read()['revision']==2
