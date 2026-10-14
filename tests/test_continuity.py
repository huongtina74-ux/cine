from cinefactory.core.continuity import ContinuityValidator
from cinefactory.domain.models import CharacterState, WorldState


def test_detects_costume_jump():
    validator = ContinuityValidator()
    a = WorldState(
        location_id="ROOM",
        characters={"C01": CharacterState(character_id="C01", costume_id="W01", position="door")},
    )
    b = WorldState(
        location_id="ROOM",
        characters={"C01": CharacterState(character_id="C01", costume_id="W02", position="door")},
    )
    issues = validator.compare_states(a, b)
    assert any(i.field == "C01.costume_id" for i in issues)
