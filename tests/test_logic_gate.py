from cinefactory.domain.models import CameraMove, CameraSpec, CharacterState, ShotSpec, WorldState
from cinefactory.turbo.logic_gate import PreRenderLogicGate


def shot(sid,entry,exit,prev=None,next_=None):
    return ShotSpec(shot_id=sid,scene_id='S',narrative_purpose='tell story',audience_endpoint='understand change',duration_seconds=4,
        entry_state=entry,exit_state=exit,previous_shot_id=prev,next_shot_id=next_,performance={},action_beats=[],
        camera=CameraSpec(narrative_purpose='observe reaction',shot_size='MCU',lens_mm=50,movement=CameraMove(kind='static',purpose='hold tension')))


def test_logic_gate_autofills_missing_state():
    a=WorldState(location_id='ROOM',characters={'C':CharacterState(character_id='C',costume_id='W1',position='left')},props={'P':'held'})
    b=WorldState(location_id=None,characters={'C':CharacterState(character_id='C')},props={})
    s1=shot('A',a,a,next_='B'); s2=shot('B',b,b,prev='A')
    r=PreRenderLogicGate().validate([s1,s2])
    assert r.passed
    assert r.shots[1].entry_state.location_id=='ROOM'
    assert r.shots[1].entry_state.characters['C'].costume_id=='W1'
    assert r.shots[1].entry_state.props['P']=='held'


def test_logic_gate_blocks_explicit_contradiction():
    a=WorldState(location_id='ROOM',characters={'C':CharacterState(character_id='C',costume_id='W1')})
    b=WorldState(location_id='ROOM',characters={'C':CharacterState(character_id='C',costume_id='W2')})
    r=PreRenderLogicGate().validate([shot('A',a,a,next_='B'),shot('B',b,b,prev='A')])
    assert not r.passed
    assert any('CHARACTER_STATE_MISMATCH' in x for x in r.findings)
