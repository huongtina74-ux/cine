from cinefactory.autopilot.scaffold import LocalScaffoldPlanner
from cinefactory.domain.enums import ShotComplexity
from cinefactory.production.video_factory import VideoFactory


def test_pilot_contains_first_and_highest_complexity_shot():
    p=LocalScaffoldPlanner(); story=p.story('x story'); script=p.script(story); director=p.director(script); shots=p.shots(script,director)
    shots[-1].complexity=ShotComplexity.HERO
    pilot=VideoFactory.choose_pilot(shots,2)
    assert pilot[0].shot_id==shots[0].shot_id
    assert shots[-1].shot_id in {x.shot_id for x in pilot}
