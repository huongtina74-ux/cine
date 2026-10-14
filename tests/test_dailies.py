from cinefactory.production.contracts import TakeRecord
from cinefactory.production.dailies import DailiesSelector


def take(name, score, technical=True, visual=True):
    return TakeRecord(take_id=name,shot_id='SH01',path=f'/{name}.mp4',technical_pass=technical,visual_pass=visual,
                      identity_score=score,continuity_score=score,performance_score=score,camera_score=score)


def test_dailies_selects_best_eligible_take():
    r=DailiesSelector(0.7).select_shot('SH01',[take('A',.75),take('B',.91),take('C',.88)])
    assert r.passed
    assert r.selected_take_id=='B'


def test_dailies_never_selects_technically_broken_take():
    r=DailiesSelector(0.7).select_shot('SH01',[take('A',.99,technical=False),take('B',.75)])
    assert r.selected_take_id=='B'
