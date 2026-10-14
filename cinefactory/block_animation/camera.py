from cinefactory.block_animation.contracts import CameraTake


def resolved_camera_roll(intent, pattern) -> float:
    """Keep the horizon level unless the story explicitly requests a Dutch angle."""
    roll = float(getattr(intent, "camera_roll", 0.0) or 0.0)
    if abs(roll) > 0.001 and intent.purpose not in {"dutch_tension", "explicit_dutch"}:
        raise ValueError("camera roll requires an explicit dutch_tension camera purpose")
    return roll


class CameraCoverageEngine:
    def __init__(self, grammar):
        self.grammar = grammar

    @staticmethod
    def _anchor_for(pattern, anchors, index):
        if not anchors:
            return None
        key = f"{pattern.pattern_id} {pattern.purpose}".lower()
        preferred = None
        for token, candidates in (
            ("establish", ("establishing", "front")),
            ("reaction", ("left_three_quarter", "medium", "aisle_left", "front")),
            ("medium", ("medium", "front", "aisle_left")),
            # Presentation beats need a readable hand-held silhouette.  The
            # room-side three-quarter anchor puts the crowd between the lens
            # and the prop in the fidelity classroom, so prefer the centered
            # medium anchor and keep the aisle option as a fallback.
            ("presentation", ("medium", "right_three_quarter", "aisle_right", "front")),
            ("prop", ("medium", "right_three_quarter", "front")),
            ("track", ("left_three_quarter", "aisle_left", "medium", "front")),
            ("orbit", ("orbit", "right_three_quarter", "front")),
            ("group", ("establishing", "front", "medium")),
        ):
            if token in key:
                preferred = candidates
                break
        if preferred:
            for candidate in preferred:
                if candidate in anchors:
                    return candidate
        return anchors[index % len(anchors)]

    def compile(self, intent, *, shot_id, duration_seconds, scene):
        patterns = [self.grammar.get(intent.pattern_id)] if intent.pattern_id else self.grammar.for_purpose(intent.purpose)
        if not patterns:
            raise ValueError(f"no camera pattern for purpose {intent.purpose!r}")
        selected = patterns[:min(intent.alternatives, len(patterns))]
        anchors = list(scene.camera_anchors)
        out = []
        for i, p in enumerate(selected):
            out.append(CameraTake(
                take_id=f"{shot_id}_CAM_{i+1:02d}",
                pattern_id=p.pattern_id,
                purpose=intent.purpose,
                targets=intent.targets,
                lens_mm=p.lens_mm,
                motion=p.motion,
                start_seconds=0,
                end_seconds=duration_seconds,
                anchor=self._anchor_for(p, anchors, i),
                prop_id=intent.prop_id,
                shot_size=p.shot_size,
                target_mode=p.target_mode,
                framing_margin=p.framing_margin,
                motion_strength=p.motion_strength,
                dof_fstop=p.dof_fstop,
                camera_roll=resolved_camera_roll(intent, p),
                horizontal_safe_margin=p.horizontal_safe_margin,
                vertical_safe_margin=p.vertical_safe_margin,
                min_subject_occupancy=p.min_subject_occupancy,
                max_subject_occupancy=p.max_subject_occupancy,
            ))
        return out
