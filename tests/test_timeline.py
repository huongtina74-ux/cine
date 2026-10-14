import pytest
from cinefactory.post.timeline import TimelineClip, TimelineSpec


def test_timeline_rejects_duplicate_order():
    with pytest.raises(ValueError):
        TimelineSpec(project_id='P', clips=[
            TimelineClip(clip_id='A',path='a.mp4',order=0),
            TimelineClip(clip_id='B',path='b.mp4',order=0),
        ])
