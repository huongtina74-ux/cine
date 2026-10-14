from __future__ import annotations

from collections import Counter

from .contracts import LongSlideEpisodeSpec


class SemanticNoveltyScorer:
    """Compare episode structure while intentionally ignoring random seeds."""

    @staticmethod
    def tokens(episode: LongSlideEpisodeSpec) -> list[str]:
        out: list[str] = []
        for module in episode.modules:
            out.extend([
                f"scene:{module.scene_kind.value}",
                f"animal:{module.animal_id}",
                f"outcome:{module.outcome.value}",
            ])
            out.extend(f"obstacle:{o.obstacle_id}" for o in module.obstacles if o.enabled)
            out.extend(f"camera:{b.pattern_id}" for b in module.camera_beats)
        return out

    @classmethod
    def similarity(cls, a: LongSlideEpisodeSpec, b: LongSlideEpisodeSpec) -> float:
        ca, cb = Counter(cls.tokens(a)), Counter(cls.tokens(b))
        keys = set(ca) | set(cb)
        intersection = sum(min(ca[k], cb[k]) for k in keys)
        union = sum(max(ca[k], cb[k]) for k in keys)
        return 1.0 if union == 0 else intersection / union

    @classmethod
    def max_similarity(
        cls,
        candidate: LongSlideEpisodeSpec,
        history: list[LongSlideEpisodeSpec],
    ) -> float:
        return max((cls.similarity(candidate, item) for item in history), default=0.0)
