from __future__ import annotations

from dataclasses import dataclass

from cinefactory.domain.models import ShotSpec, WorldState


@dataclass
class ContinuityIssue:
    code: str
    field: str
    previous_value: str | None
    next_value: str | None
    message: str


class ContinuityValidator:
    """Deterministic first-pass continuity checks between adjacent shots."""

    def compare_states(self, previous: WorldState, current: WorldState) -> list[ContinuityIssue]:
        issues: list[ContinuityIssue] = []

        if previous.location_id != current.location_id:
            issues.append(
                ContinuityIssue(
                    "LOCATION_JUMP",
                    "location_id",
                    previous.location_id,
                    current.location_id,
                    "Location changed without an explicit scene transition.",
                )
            )

        shared = set(previous.characters) & set(current.characters)
        for cid in sorted(shared):
            a = previous.characters[cid]
            b = current.characters[cid]
            for field in ("costume_id", "position", "facing", "eyeline"):
                av = getattr(a, field)
                bv = getattr(b, field)
                if av is not None and bv is not None and av != bv:
                    issues.append(
                        ContinuityIssue(
                            "CHARACTER_STATE_MISMATCH",
                            f"{cid}.{field}",
                            str(av),
                            str(bv),
                            f"{cid} changed {field} across the cut without an encoded transition.",
                        )
                    )

        for prop, state in previous.props.items():
            if prop in current.props and current.props[prop] != state:
                issues.append(
                    ContinuityIssue(
                        "PROP_STATE_MISMATCH",
                        f"prop.{prop}",
                        state,
                        current.props[prop],
                        f"Prop {prop} changed state across the cut.",
                    )
                )

        return issues

    def validate_adjacent(self, previous_shot: ShotSpec, next_shot: ShotSpec) -> list[ContinuityIssue]:
        return self.compare_states(previous_shot.exit_state, next_shot.entry_state)
