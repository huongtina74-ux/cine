"""Persistent channel/series/season operating contracts for long-term YouTube IP.

A channel is above projects: niche > subniche > format > channel > series > episode.
Reference creators are benchmark labels, never characters, story licenses, or clones.
Channel planning is NOT a substitute for owned audience analytics or original art QC.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Literal

from pydantic import BaseModel, Field, model_validator

SAFE_ID = re.compile(r"^[a-z][a-z0-9_]{2,63}$")
REFERENCE_ALIASES = {
    "maizen": {"niche": "minecraft", "observation": "accessible, character-led adventures and repeatable escalation"},
    "jj & mikey": {"niche": "minecraft", "observation": "duo dynamics and recognizable protagonist contrast; not a separate niche"},
    "bigschool": {"niche": "minecraft", "observation": "school setting, ensemble comedy and short conflict-to-payoff cycles"},
}
MINECRAFT_FORMATS = {
    "minecraft_story_adventure": "Original character-led exploration and conflict",
    "minecraft_school_comedy": "Original campus ensemble comedy and relational stakes",
    "minecraft_challenge_survival": "Legacy alias: animated challenge stories, never authentic gameplay footage",
    "minecraft_animated_challenge": "Original scripted/animated challenge episodes",
    "minecraft_monster_fantasy": "Original creature lore, mystery and fantasy worldbuilding",
}
BLOCKED_COPYRIGHT_NAMES = ("maizen", "bigschool", "jj & mikey", "cocomelon")


def _valid_id(value: str) -> str:
    if not SAFE_ID.fullmatch(value):
        raise ValueError("USE_LOWERCASE_CANONICAL_CHANNEL_IDS")
    return value


def _hash(path: Path) -> str:
    stream_hash = sha256()
    with path.open("rb") as file:
        while block := file.read(1024 * 1024):
            stream_hash.update(block)
    return stream_hash.hexdigest()


class OriginalCharacter(BaseModel):
    character_id: str
    display_name: str = Field(min_length=2)
    design_identity: str = Field(min_length=12)
    inner_conflict: str = Field(min_length=12)
    consistent_motivations: list[str] = Field(min_length=2)
    relationship_constraints: list[str] = Field(default_factory=list)
    visual_asset_id: str | None = None
    character_rights_status: Literal["ORIGINAL_DRAFT", "RIGHTS_REVIEWED"] = "ORIGINAL_DRAFT"

    @model_validator(mode="after")
    def safe_identity(self):
        _valid_id(self.character_id)
        if self.display_name.strip().lower() in ("jj", "mikey", *BLOCKED_COPYRIGHT_NAMES):
            raise ValueError("REFERENCE_CHARACTER_IDENTITY_MUST_NOT_BE_CLONED")
        return self


class EpisodeCard(BaseModel):
    episode_id: str
    season_number: int = Field(ge=1, le=50)
    episode_number: int = Field(ge=1)
    title_working: str = Field(min_length=10)
    original_premise: str = Field(min_length=25)
    opening_hook: str = Field(min_length=12)
    central_conflict: str = Field(min_length=12)
    character_growth: str = Field(min_length=12)
    payoff: str = Field(min_length=12)
    continuity_changes: list[str] = Field(min_length=1)
    production_reuse: list[str] = Field(default_factory=list)
    variation_axis: str = Field(min_length=8)
    editorial_pillar: Literal["EVERGREEN", "EXPERIMENT", "TREND"] = "EVERGREEN"
    experiment_hypothesis: str | None = None
    release_status: Literal[
        "IDEA", "SCRIPT_REVIEW", "IN_PRODUCTION", "QC_REVIEW",
        "OWNER_APPROVED", "PUBLISHED"
    ] = "IDEA"

    @model_validator(mode="after")
    def identity(self):
        _valid_id(self.episode_id)
        return self


class SeriesBible(BaseModel):
    series_id: str
    subniche: str
    format_id: str
    series_promise: str = Field(min_length=20)
    recurring_conflict_engine: str = Field(min_length=20)
    world_rules: list[str] = Field(min_length=2)
    recurring_cast_ids: list[str] = Field(min_length=1)
    season_arc: str = Field(min_length=30)
    episodic_entry_rule: str = Field(min_length=15)
    continuity_policy: list[str] = Field(min_length=2)
    episodes: list[EpisodeCard] = Field(min_length=3)
    season_status: Literal["INCUBATING", "APPROVED_FOR_SCRIPT_DEVELOPMENT"] = "INCUBATING"

    @model_validator(mode="after")
    def check_series(self):
        _valid_id(self.series_id)
        _valid_id(self.format_id)
        if self.subniche not in MINECRAFT_FORMATS and self.subniche.startswith("minecraft_"):
            raise ValueError("UNKNOWN_MINECRAFT_SUBNICHE")
        ids = [e.episode_id for e in self.episodes]
        if len(ids) != len(set(ids)):
            raise ValueError("DUPLICATE_EPISODE_IDENTITIES")
        slots = [(e.season_number, e.episode_number) for e in self.episodes]
        if len(slots) != len(set(slots)):
            raise ValueError("DUPLICATE_SERIES_EPISODE_SLOTS")
        premises = [re.sub(r"\s+", " ", e.original_premise.casefold().strip()) for e in self.episodes]
        if len(premises) != len(set(premises)):
            raise ValueError("EPISODES_REUSE_IDENTICAL_PREMISE")
        return self


class GrowthPolicy(BaseModel):
    evergreen_share_min: float = Field(default=0.70, ge=0.5, le=1.0)
    experimental_share_max: float = Field(default=0.20, ge=0, le=0.4)
    trend_share_max: float = Field(default=0.15, ge=0, le=0.4)
    maximum_same_format_streak: int = Field(default=3, ge=1, le=6)
    publishing_cadence_target_days: int = Field(default=7, ge=1, le=45)
    production_buffer_target_episodes: int = Field(default=3, ge=1, le=10)
    quality_over_deadline: bool = True
    do_not_infer_revenue_or_ctr: bool = True
    experimentation_requires_source_data: bool = True


class ChannelBible(BaseModel):
    schema_id: Literal["cine.channel.bible.v206"] = "cine.channel.bible.v206"
    channel_brand_id: str
    proposed_brand_name: str = Field(min_length=5)
    niche: Literal["minecraft"] = "minecraft"
    target_language: str = "en"
    intended_audience: str = Field(min_length=15)
    audience_promise: str = Field(min_length=25)
    differentiator: str = Field(min_length=30)
    world_identity: str = Field(min_length=30)
    editorial_principles: list[str] = Field(min_length=3)
    character_registry: list[OriginalCharacter] = Field(min_length=2)
    series: list[SeriesBible] = Field(min_length=1)
    growth_policy: GrowthPolicy = Field(default_factory=GrowthPolicy)
    references_for_structural_study: list[str] = Field(default_factory=list)
    forbidden_imitation: list[str] = Field(default_factory=lambda: [
        "reference channel title and thumbnail imitation",
        "reference character names, visual skin, voice and likeness",
        "copied dialogue, script beats, settings or branded assets",
        "claims of official franchise affiliation",
    ])
    channel_status: Literal["DRAFT_REQUIRES_OWNER_REVIEW", "ARCHIVED"] = (
        "DRAFT_REQUIRES_OWNER_REVIEW"
    )
    verified_youtube_channel_id: str | None = None

    @model_validator(mode="after")
    def validate_channel(self):
        _valid_id(self.channel_brand_id)
        if any(term in self.proposed_brand_name.casefold() for term in BLOCKED_COPYRIGHT_NAMES):
            raise ValueError("REFERENCE_CHANNEL_BRAND_CLONE_BLOCKED")
        registry = [c.character_id for c in self.character_registry]
        if len(registry) != len(set(registry)):
            raise ValueError("DUPLICATE_CHARACTER_IDS")
        ids = [s.series_id for s in self.series]
        if len(ids) != len(set(ids)):
            raise ValueError("DUPLICATE_SERIES_IDS")
        known = set(registry)
        for s in self.series:
            if not set(s.recurring_cast_ids).issubset(known):
                raise ValueError("SERIES_USES_UNREGISTERED_ACTOR")
        episodes = [episode for series in self.series for episode in series.episodes]
        evergreen = sum(e.editorial_pillar == "EVERGREEN" for e in episodes) / len(episodes)
        trend = sum(e.editorial_pillar == "TREND" for e in episodes) / len(episodes)
        experiments = sum(e.editorial_pillar == "EXPERIMENT" for e in episodes) / len(episodes)
        if evergreen < self.growth_policy.evergreen_share_min:
            raise ValueError("EVERGREEN_PORTFOLIO_SHARE_TOO_LOW")
        if trend > self.growth_policy.trend_share_max:
            raise ValueError("TREND_CHASING_EXCEEDS_CHANNEL_POLICY")
        if experiments > self.growth_policy.experimental_share_max:
            raise ValueError("EXPERIMENT_SHARE_EXCEEDS_CHANNEL_POLICY")
        return self


class ChannelEpisodeStrategy(BaseModel):
    schema_id: Literal["cine.channel.episode_strategy.v206"] = "cine.channel.episode_strategy.v206"
    channel_brand_id: str
    series_id: str
    episode_id: str
    source_sha256: str
    niche: str
    subniche: str
    format_id: str
    brand_promise: str
    series_promise: str
    original_premise: str
    opening_hook: str
    central_conflict: str
    episode_payoff: str
    character_development: str
    continuity_requirements: list[str]
    cast_ids: list[str]
    world_rules: list[str]
    production_reuse: list[str]
    experiment_hypothesis: str | None = None
    readiness: Literal["DRAFT_FOR_SCRIPT_DEVELOPMENT"] = "DRAFT_FOR_SCRIPT_DEVELOPMENT"
    video_release_permission: bool = False


class ChannelLibrary:
    def __init__(self, canonical_root: str | Path):
        self.root = Path(canonical_root).resolve()
        self.channels = self.root / "data" / "channels"

    def path_for(self, channel_brand_id: str) -> Path:
        return self.channels / _valid_id(channel_brand_id) / "channel_bible.json"

    def register_draft(self, bible: ChannelBible) -> Path:
        # Pydantic model_copy(update=...) does not revalidate. This storage
        # trust boundary always reparses the complete proposed channel bible.
        bible = ChannelBible.model_validate(bible.model_dump())
        path = self.path_for(bible.channel_brand_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        # An existing channel bible must be amended as a reviewed, versioned
        # document. Never silently overwrite the identity behind past episodes.
        with path.open("x", encoding="utf8") as file:
            file.write(bible.model_dump_json(indent=2) + "\n")
        return path

    def load(self, channel_brand_id: str) -> tuple[ChannelBible, str]:
        path = self.path_for(channel_brand_id)
        bible = ChannelBible.model_validate_json(path.read_text(encoding="utf8"))
        if bible.channel_brand_id != channel_brand_id:
            raise ValueError("CHANNEL_FILE_ID_MISMATCH")
        return bible, _hash(path)

    def resolve_standalone(
        self, channel_brand_id: str, project_id: str,
        original_prompt: str, subniche: str,
    ) -> ChannelEpisodeStrategy:
        """Bind a new independent original video to a persistent brand only.

        No series cast, world continuity, previous episode plot or rigs leak in.
        """
        from .minecraft_subniche_v207 import canonical_subniche, CATALOG, Lane
        bible, digest = self.load(channel_brand_id)
        chosen = canonical_subniche(subniche)
        if chosen not in CATALOG or CATALOG[chosen].production_lane is not Lane.FILM_ANIMATION:
            raise ValueError("STANDALONE_CHANNEL_ONLY_SUPPORTS_ORIGINAL_ANIMATED_FILMS")
        if bible.channel_status != "DRAFT_REQUIRES_OWNER_REVIEW":
            raise PermissionError("CHANNEL_NOT_OPEN_FOR_ORIGINAL_STANDALONE_PLANNING")
        return ChannelEpisodeStrategy(
            channel_brand_id=channel_brand_id,
            series_id="standalone_film",
            episode_id=project_id,
            source_sha256=digest,
            niche=bible.niche,
            subniche=chosen,
            format_id="standalone_original_video_v1",
            brand_promise=bible.audience_promise,
            series_promise="New independent video respecting the channel audience promise",
            original_premise=original_prompt,
            opening_hook="TO_BE_ORIGINALLY_WRITTEN_BY_SCRIPT_ROOM",
            central_conflict="TO_BE_DEFINED_IN_ORIGINAL_WRITERS_ROOM",
            episode_payoff="TO_BE_ORIGINALLY_DEVELOPED_AND_REVIEWED",
            character_development="NEW_CAST_REQUIRES_INDEPENDENT_ORIGINAL_ART_DEVELOPMENT",
            continuity_requirements=[
                "Keep the channel audience/brand promise consistent",
                "Do not inherit prior character identities, designs, skins, voices or rigs",
            ],
            cast_ids=[],
            world_rules=[],
            production_reuse=[],
            experiment_hypothesis=None,
        )

    def resolve_episode(
        self, channel_brand_id: str, series_id: str, episode_id: str,
        *, reuse_characters: bool = True,
    ) -> ChannelEpisodeStrategy:
        bible, source_hash = self.load(channel_brand_id)
        if bible.channel_status != "DRAFT_REQUIRES_OWNER_REVIEW":
            raise PermissionError("CHANNEL_NOT_OPEN_FOR_DRAFT_PLANNING")
        series = next((s for s in bible.series if s.series_id == series_id), None)
        if series is None:
            raise ValueError("SERIES_NOT_IN_CHANNEL_BIBLE")
        ep = next((e for e in series.episodes if e.episode_id == episode_id), None)
        if ep is None:
            raise ValueError("EPISODE_NOT_IN_SERIES")
        return ChannelEpisodeStrategy(
            channel_brand_id=channel_brand_id,
            series_id=series_id,
            episode_id=episode_id,
            source_sha256=source_hash,
            niche=bible.niche,
            subniche=series.subniche,
            format_id=series.format_id,
            brand_promise=bible.audience_promise,
            series_promise=series.series_promise,
            original_premise=ep.original_premise,
            opening_hook=ep.opening_hook,
            central_conflict=ep.central_conflict,
            episode_payoff=ep.payoff,
            character_development=ep.character_growth,
            continuity_requirements=[
                *series.continuity_policy, *ep.continuity_changes,
            ],
            cast_ids=(list(series.recurring_cast_ids) if reuse_characters else []),
            world_rules=list(series.world_rules),
            production_reuse=list(ep.production_reuse),
            experiment_hypothesis=ep.experiment_hypothesis,
        )


def evaluate_evergreen_slate(bible: ChannelBible) -> dict:
    """Structural sustainability signals only, never predicted growth."""
    all_episodes = [e for s in bible.series for e in s.episodes]
    counts = Counter(s.subniche for s in bible.series for _ in s.episodes)
    formats = set(counts)
    return {
        "schema": "cine.channel.long_horizon_diagnostic.v206",
        "channel_brand_id": bible.channel_brand_id,
        "episodes_planned": len(all_episodes),
        "series_planned": len(bible.series),
        "subniche_mix": dict(counts),
        "distinct_formats": len(formats),
        "quality_over_deadline": bible.growth_policy.quality_over_deadline,
        "evergreen_share": round(
            sum(e.editorial_pillar == "EVERGREEN" for e in all_episodes) / len(all_episodes),
            3,
        ),
        "trend_share": round(
            sum(e.editorial_pillar == "TREND" for e in all_episodes) / len(all_episodes),
            3,
        ),
        "business_traction_verified": False,
        "youtube_channel_created": bool(bible.verified_youtube_channel_id),
        "watch_time_or_rpm_observed": False,
        "brand_and_world_originality_review": "PENDING_INDEPENDENT_SIGNOFF",
        "risk_warnings": (
            ["FORMAT_CONCENTRATION_REQUIRES_EDITORIAL_REVIEW"]
            if len(formats) < 2 else []
        ),
    }


def minecraft_original_starter(channel_brand_id: str, proposed_name: str) -> ChannelBible:
    """Illustrative original-IP DRAFT, not a claimed available YouTube brand."""
    _valid_id(channel_brand_id)
    characters = [
        OriginalCharacter(
            character_id="orin",
            display_name="Orin",
            design_identity="Copper scarf, tiny lantern satchel and a careful inventor silhouette",
            inner_conflict="Wants to keep others safe but hesitates to share unfinished ideas",
            consistent_motivations=["protect the valley", "solve problems through observation"],
            relationship_constraints=["learns from mistakes", "never humiliates companions"],
        ),
        OriginalCharacter(
            character_id="tessa",
            display_name="Tessa",
            design_identity="Patchwork explorer cloak, field notebook and distinctive moss-green boots",
            inner_conflict="Craves discovery while learning to respect other people's boundaries",
            consistent_motivations=["map forgotten paths", "keep promises made to friends"],
            relationship_constraints=["shares credit for discoveries", "does not lie for a cheap twist"],
        ),
        OriginalCharacter(
            character_id="nori",
            display_name="Nori",
            design_identity="Indigo work apron, custom redstone goggles and painted compass emblem",
            inner_conflict="Feels pressured to prove every invention works on the first attempt",
            consistent_motivations=["build useful machines", "help the village thrive"],
            relationship_constraints=["fails constructively", "trusts the team with prototypes"],
        ),
    ]

    def episode(eid, number, title, premise, hook, conflict, growth, payoff, change, axis):
        return EpisodeCard(
            episode_id=eid, season_number=1, episode_number=number,
            title_working=title, original_premise=premise,
            opening_hook=hook, central_conflict=conflict,
            character_growth=growth, payoff=payoff,
            continuity_changes=[change], variation_axis=axis,
            production_reuse=["original valley terrain", "approved persistent character rigs"],
        )

    series = [
        SeriesBible(
            series_id="lantern_trails",
            subniche="minecraft_story_adventure",
            format_id="character_adventure_v1",
            series_promise="Small mysteries resolved by character choices and creative problem-solving",
            recurring_conflict_engine="Each new path conceals a puzzle linked to the valley's ecological history",
            world_rules=["The valley keeps physical consequences from prior episodes",
                         "Magic maps cannot replace practical investigation"],
            recurring_cast_ids=["orin", "tessa"],
            season_arc="An original lantern map slowly reveals why abandoned routes keep changing after storms",
            episodic_entry_rule="Each episode introduces a self-contained dilemma and one returning character beat",
            continuity_policy=["Record invented prop positions and prior injuries",
                               "Preserve character motivations between consecutive episodes"],
            episodes=[
                episode("lt_bridge",1,"The Bridge that Moved Overnight",
                        "A familiar wooden bridge changes position and the explorers investigate erosion clues.",
                        "A delivery cart arrives at a bridge that is no longer there.",
                        "The team must choose between a risky shortcut and rescuing villagers.",
                        "Orin practices admitting when a plan is uncertain.",
                        "They find a safe route and recover an original map fragment.",
                        "The northern crossing is now closed.", "environmental mystery"),
                episode("lt_lake",2,"The Lantern Hidden Beneath the Lake",
                        "An old bell rings beneath a lake, revealing a forgotten safety signal mechanism.",
                        "A soft underwater bell rings while every house is asleep.",
                        "Tessa must return a family keepsake before exploring the lake.",
                        "Tessa learns exploration requires care for other people's belongings.",
                        "A floating marker restores the signal and reveals a new route.",
                        "The team adds the flooded lower tunnel to its map.", "underwater rescue"),
                episode("lt_tower",3,"The Observatory with Two Shadows",
                        "An abandoned tower casts impossible shadows because its mirrors still track moving light.",
                        "At sunset the tower suddenly casts two separate shadows.",
                        "Orin must solve the mirror puzzle without breaking the delicate observatory.",
                        "Orin trusts a collaborative solution instead of forcing an invention.",
                        "The mirrors align and show where the next season mystery begins.",
                        "A new constellation symbol is documented for later episodes.", "optical puzzle"),
            ],
        ),
        SeriesBible(
            series_id="workshop_days",
            subniche="minecraft_school_comedy",
            format_id="ensemble_workshop_comedy_v1",
            series_promise="Warm ensemble comedy about building, cooperation and surprising inventions",
            recurring_conflict_engine="The class must solve a village task with limited resources and misread instructions",
            world_rules=["Workshop lessons occur in the same original craft school",
                         "Every failed contraption has a believable physical cause"],
            recurring_cast_ids=["orin", "tessa", "nori"],
            season_arc="Nori forms a mixed-skill workshop team ahead of a seasonal community repair festival",
            episodic_entry_rule="Each episode begins with a standalone build challenge and concludes with a lesson",
            continuity_policy=["Maintain consistent tool and classroom layouts",
                               "Track who has learned each engineering skill"],
            episodes=[
                episode("wd_umbrella",1,"A Roof that Became an Umbrella",
                        "A classroom roof prototype folds unexpectedly during a calm practice rainstorm.",
                        "The roof rises like an umbrella just before a harmless indoor rain test.",
                        "Nori has to fix a design flaw without blaming the helpers.",
                        "Nori learns to accept feedback from less experienced classmates.",
                        "A simple hinge repair protects the school garden.",
                        "The school keeps the improved hinge pattern.", "engineering slapstick"),
                episode("wd_crates",2,"The Crates that Sorted Themselves",
                        "An automatic storage shelf swaps labels and creates a chain of harmless delivery mistakes.",
                        "The bakery receives three boxes of empty planting pots.",
                        "The team must find a labeling bug before a timed village delivery.",
                        "Tessa learns to verify details instead of racing ahead.",
                        "They publish a color-coded labeling rule and finish the delivery.",
                        "The new label system remains visible in future shots.", "timed puzzle"),
                episode("wd_clock",3,"The Clock That Ran Backwards",
                        "A festival clock prototype runs in reverse and the class investigates the gear ratios.",
                        "The school's clock announces lunch before breakfast.",
                        "Orin must ask for advice from the class's newest pupil.",
                        "Orin learns a useful idea can come from anyone.",
                        "The team repairs the clock before the festival rehearsal.",
                        "The repaired clock becomes a recurring school prop.", "mechanical comedy"),
            ],
        ),
        SeriesBible(
            series_id="redstone_trials",
            subniche="minecraft_challenge_survival",
            format_id="friendly_rules_survival_v1",
            series_promise="Original puzzle challenges with clear rules, visible stakes and fair team victories",
            recurring_conflict_engine="A limited inventory creates a tough but solvable environmental puzzle",
            world_rules=["Challenges never require deceptive or harmful real-world behavior",
                         "All puzzles display their mechanics before solutions"],
            recurring_cast_ids=["tessa", "nori"],
            season_arc="The friends learn three linked craft skills while preparing a safe village celebration",
            episodic_entry_rule="Each episode explains fair rules, attempts, setbacks and a demonstrable solution",
            continuity_policy=["Preserve inventory and puzzle rules between shots",
                               "Never show cheating solutions as an unexplained trick"],
            episodes=[
                episode("rt_flood",1,"Can a Small Gate Save the Garden?",
                        "The team uses a limited inventory to redirect rainwater away from a flooded garden.",
                        "The garden's water level rises with only five blocks left in inventory.",
                        "The friends choose between saving tools and protecting seeds.",
                        "Nori accepts a simpler low-tech fix proposed by Tessa.",
                        "They open a safe spillway before the timer expires.",
                        "A new canal remains part of the valley map.", "resource allocation"),
                episode("rt_light",2,"The Glowstone Path Puzzle",
                        "A broken night trail must be relit using exactly six lamps and a finite energy source.",
                        "One lamp dims just as travelers reach a path intersection.",
                        "Tessa must trade speed for careful route planning.",
                        "Tessa learns to test assumptions before placing the last lamp.",
                        "An efficient pattern illuminates the full route.",
                        "The path's lighting arrangement becomes a reusable world asset.", "logic and spatial reasoning"),
                episode("rt_train",3,"The Cart that Missed its Stop",
                        "A rail-cart prototype has to stop within a narrow marked zone using limited switches.",
                        "A cart rolls through its first test station without slowing down.",
                        "The friends must explain and fix the braking failure before the final attempt.",
                        "Nori learns that repeated testing is part of success.",
                        "They redesign the braking section with a clear visual payoff.",
                        "The upgraded rail is documented for future episodes.", "physical timing"),
            ],
        ),
    ]
    return ChannelBible(
        channel_brand_id=channel_brand_id,
        proposed_brand_name=proposed_name,
        intended_audience="English-speaking families and general audiences enjoying original Minecraft-inspired stories",
        audience_promise="Clear original adventures, warm comedy and meaningful payoffs with recognizable characters",
        differentiator="A continuous original valley world with cause-and-effect history, practical puzzles and empathetic character growth",
        world_identity="An original crafted valley connecting a workshop school, lantern trails and fair redstone challenge grounds",
        editorial_principles=[
            "Every episode gives a self-contained emotional or practical payoff",
            "Maintain consistent character goals, visual silhouettes and world continuity",
            "Introduce meaningful variation without replacing established audience promises",
            "Avoid copying benchmark-channel characters, stories, voices or thumbnail treatments",
        ],
        character_registry=characters,
        series=series,
        references_for_structural_study=[
            "Maizen: high-level character-led adventure structure only",
            "JJ & Mikey: duo dynamics as generic storytelling pattern, not licensed characters",
            "BigSchool: classroom ensemble structure only, not specific scripts/skins",
        ],
    )


def draft_editorial_slate(bible: ChannelBible, weeks: int = 12) -> dict:
    """Round-robin across series, maintain internal serial sequence, no dates asserted."""
    if not 1 <= weeks <= 52:
        raise ValueError("EDITORIAL_HORIZON_1_TO_52_WEEKS")
    buckets = [
        list(sorted(s.episodes, key=lambda ep: (ep.season_number, ep.episode_number)))
        for s in bible.series
    ]
    slate = []
    cursor = 0
    while len(slate) < weeks and any(buckets):
        idx = cursor % len(buckets)
        cursor += 1
        if not buckets[idx]:
            continue
        episode = buckets[idx].pop(0)
        series = bible.series[idx]
        slate.append({
            "week_offset": len(slate) + 1,
            "series_id": series.series_id,
            "subniche": series.subniche,
            "format_id": series.format_id,
            "episode_id": episode.episode_id,
            "season_episode": [episode.season_number, episode.episode_number],
            "editorial_status": "DRAFT_NEEDS_SCRIPT_AND_FILM_QC",
            "publish_committed": False,
            "owner_approval": "NOT_GIVEN",
        })
    return {
        "schema": "cine.channel.editorial_slate.v206",
        "channel_brand_id": bible.channel_brand_id,
        "weeks_requested": weeks,
        "weeks_with_candidate": len(slate),
        "inventory_gap_weeks": weeks - len(slate),
        "calendar_has_approved_episodes": False,
        "cadence_target_days": bible.growth_policy.publishing_cadence_target_days,
        "production_buffer_target_episodes": bible.growth_policy.production_buffer_target_episodes,
        "quality_over_deadline": True,
        "data_derived_prediction": False,
        "slate": slate,
    }


def verify_original_cast_rig_readiness(
    canonical_root: str | Path,
    strategy: ChannelEpisodeStrategy,
) -> dict:
    """Reconcile original actor bible to real registered Minecraft rigs.

    Source claims alone are NOT rights proof; this is one narrow fail-closed
    technical preflight before expensive rendering.
    """
    from cinefactory.block_animation.registry import BlockAnimationLibraries

    bible, current_hash = ChannelLibrary(canonical_root).load(
        strategy.channel_brand_id
    )
    if current_hash != strategy.source_sha256:
        return {
            "ready": False, "blockers": ["CHANNEL_BIBLE_HASH_DRIFT"],
            "technical_check_only": True,
            "independent_rights_and_art_approval_still_required": True,
        }
    cast = {c.character_id: c for c in bible.character_registry}
    blockers = []
    rig_ids = []
    for actor_id in strategy.cast_ids:
        character = cast.get(actor_id)
        if character is None:
            blockers.append(f"UNREGISTERED_STORY_CHARACTER:{actor_id}")
            continue
        if character.character_rights_status != "RIGHTS_REVIEWED":
            blockers.append(f"CHARACTER_RIGHTS_REVIEW_PENDING:{actor_id}")
        if not character.visual_asset_id:
            blockers.append(f"ORIGINAL_CHARACTER_RIG_UNASSIGNED:{actor_id}")
        else:
            rig_ids.append(character.visual_asset_id)
    if len(rig_ids) != len(set(rig_ids)):
        blockers.append("MULTIPLE_ORIGINAL_ACTORS_SHARE_ONE_RIG_IDENTITY")
    if not rig_ids:
        return {
            "ready": False, "blockers": blockers,
            "technical_check_only": True,
            "independent_rights_and_art_approval_still_required": True,
        }
    try:
        rigs = BlockAnimationLibraries.load(Path(canonical_root)).rigs
        for actor_id in strategy.cast_ids:
            char = cast.get(actor_id)
            if char is None or not char.visual_asset_id:
                continue
            rig_id = char.visual_asset_id
            rig = rigs.maybe_get(rig_id)
            if rig is None:
                blockers.append(f"CHARACTER_RIG_NOT_IN_FACTORY_REGISTRY:{rig_id}")
            elif rig.style != "MINECRAFT":
                blockers.append(f"CHARACTER_RIG_STYLE_NOT_MINECRAFT:{rig_id}")
            elif rig.identity.get("original_character_id") != actor_id:
                blockers.append(
                    f"ORIGINAL_CHARACTER_IDENTITY_NOT_BOUND_TO_RIG:{actor_id}:{rig_id}"
                )
    except (OSError, ValueError, KeyError, TypeError):
        blockers.append("CHARACTER_RIG_REGISTRY_NOT_VALIDATED")
    return {
        "ready": not blockers,
        "blockers": blockers,
        "identity_rig_ids": rig_ids,
        "bible_sha256": strategy.source_sha256,
        "technical_check_only": True,
        "independent_rights_and_art_approval_still_required": True,
    }


def verify_fresh_episode_cast_readiness(
    canonical_root: str | Path, project_id: str, channel_brand_id: str,
) -> dict:
    """Fresh per-video actor manifest; never use last episode's character rigs.

    Character creation is a separate local process. Requires real pre-existing
    Minecraft registered rigs with matching original actor IDs AND an
    externally trusted rights-review Ed25519 signature for this manifest.
    """
    import base64
    import os
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidSignature
    from cinefactory.block_animation.registry import BlockAnimationLibraries

    root=Path(canonical_root).resolve()
    manifest=root/"data"/"projects"/project_id/"inputs"/"original_episode_cast.json"
    result={
        "ready":False,
        "source":str(manifest),
        "new_character_assets_required":True,
        "previous_series_rig_reuse_allowed":False,
        "independent_art_review_still_required":True,
        "blockers":[],
    }
    if not manifest.is_file():
        result["blockers"].append("FRESH_EPISODE_CAST_MANIFEST_REQUIRED")
        return result
    try:
        raw=json.loads(manifest.read_text(encoding="utf8"))
        entries=raw["actors"]
        if (raw.get("schema")!="cine.original_episode_cast.v207"
                or raw.get("project_id")!=project_id
                or raw.get("channel_brand_id")!=channel_brand_id
                or not isinstance(entries,list) or len(entries)<1):
            raise ValueError("UNTRUSTED_FRESH_CAST_MANIFEST")
        ids=[x["character_id"] for x in entries]
        rigs=[x["rig_id"] for x in entries]
        if len(ids)!=len(set(ids)) or len(rigs)!=len(set(rigs)):
            raise ValueError("DUPLICATE_FRESH_ACTOR_OR_RIG")
        for identity in ids:
            _valid_id(identity)
        signature=raw["independent_rights_review"]
        if signature.get("schema")!="cine.fresh_episode_rights_review.v207":
            raise ValueError("WRONG_RIGHTS_REVIEW_SCHEMA")
        canonical=json.dumps({
            "schema":raw["schema"],"project_id":project_id,
            "channel_brand_id":channel_brand_id,"actors":entries,
        },sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf8")
        key_path=os.environ.get("CINEFACTORY_RIGHTS_TRUST_PUBKEY")
        if not key_path:
            raise PermissionError("TRUSTED_INDEPENDENT_RIGHTS_KEY_REQUIRED")
        reviewer=serialization.load_pem_public_key(
            Path(key_path).resolve(strict=True).read_bytes())
        if not isinstance(reviewer,Ed25519PublicKey):
            raise ValueError("UNSUPPORTED_RIGHTS_REVIEW_SIGNATURE")
        if signature.get("decision")!="CLEARED_ORIGINAL_EPISODE_CHARACTERS":
            raise PermissionError("ORIGINAL_CHARACTER_RIGHTS_NOT_CLEARED")
        reviewer.verify(
            base64.b64decode(signature["signature_b64"],validate=True),canonical,
        )
        factory=BlockAnimationLibraries.load(root).rigs
        for actor in entries:
            rig=factory.maybe_get(actor["rig_id"])
            if rig is None or rig.style != "MINECRAFT":
                raise ValueError("ORIGINAL_EPISODE_RIG_NOT_REGISTERED_AS_MINECRAFT")
            if rig.identity.get("original_character_id")!=actor["character_id"]:
                raise ValueError("FRESH_EPISODE_RIG_WRONG_ACTOR_IDENTITY")
        result["ready"]=True
        result["actor_count"]=len(entries)
        return result
    except (KeyError,ValueError,TypeError,OSError,InvalidSignature,PermissionError) as e:
        result["blockers"].append("FRESH_EPISODE_CHARACTER_CLEARANCE_FAILED:"+type(e).__name__)
        return result
