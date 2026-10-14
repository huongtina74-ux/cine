from __future__ import annotations

from cinefactory.animal_long_slide.planner import LongSlideEpisodePlanner
from cinefactory.animal_long_slide.series import SeriesBible
from cinefactory.animal_long_slide.director import VariationDirector
from cinefactory.animal_long_slide.variation import EpisodeHistory, VariedEpisode
from cinefactory.studio.contracts import StudioProjectSpec


class LongSlideCompanyAdapter:
    """Company-facing entry point for the Animal Long Slide vertical."""

    @staticmethod
    def matches(project: StudioProjectSpec) -> bool:
        text = f"{project.domain} {project.niche or ''} {project.prompt}".lower()
        return any(
            token in text
            for token in (
                "long slide",
                "long slice",
                "animal fountain",
                "fountain crossing",
                "paint animals",
                "3d animal game",
                "funanimation",
                "animal_long_slide",
            )
        )

    def plan_episode(
        self,
        project: StudioProjectSpec,
        *,
        episode_id: str = "EP_LONG_SLIDE_001",
        seed: int = 1,
        animals: list[str] | None = None,
        target_duration_seconds: float | None = None,
        module_count: int | None = None,
    ):
        if not self.matches(project):
            raise ValueError("project is not an Animal Long Slide vertical")
        duration = (
            float(target_duration_seconds)
            if target_duration_seconds is not None
            else float(project.duration_seconds or 660)
        )
        return LongSlideEpisodePlanner(seed=seed).plan(
            project_id=project.studio_project_id,
            episode_id=episode_id,
            title=project.prompt,
            target_duration_seconds=duration,
            animals=animals,
            module_count=module_count,
        )

    def plan_series_episode(
        self,
        project: StudioProjectSpec,
        *,
        history: EpisodeHistory,
        bible: SeriesBible | None = None,
        episode_id: str = "EP_LONG_SLIDE_001",
        seed: int = 1,
        target_duration_seconds: float | None = None,
        renderable_animals: set[str] | None = None,
    ) -> VariedEpisode:
        """Plan a monetization-safe series episode that differs from the channel history.

        Raises VariationExhaustedError when no candidate passes, so production stops
        instead of publishing a repeat.
        """
        if not self.matches(project):
            raise ValueError("project is not an Animal Long Slide vertical")
        duration = (
            float(target_duration_seconds)
            if target_duration_seconds is not None
            else float(project.duration_seconds or 330)
        )
        director = VariationDirector(
            bible or SeriesBible.default(),
            history,
            renderable_animals=renderable_animals,
        )
        return director.next_episode(
            project_id=project.studio_project_id,
            episode_id=episode_id,
            target_duration_seconds=duration,
            seed=seed,
        )
