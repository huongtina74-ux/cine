from pathlib import Path

from cinefactory.autopilot.scaffold import LocalScaffoldPlanner
from cinefactory.prompts.compiler import ShotPromptCompiler
from cinefactory.production.router import ShotRouter


def test_scaffold_chain_is_schema_valid():
    p=LocalScaffoldPlanner()
    story=p.story('A family secret changes a relationship')
    script=p.script(story)
    assets=p.assets(script)
    director=p.director(script)
    shots=p.shots(script,director)
    assert len(shots)==len(script.scenes)
    assert all(s.camera.narrative_purpose for s in shots)
    compiled=ShotPromptCompiler().compile_video(shots[0],assets)
    assert shots[0].narrative_purpose in compiled.positive
    assert 'identity drift' in compiled.negative
    assert ShotRouter().route(shots[0]).candidates >= 1
