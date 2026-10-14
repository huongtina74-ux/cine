from __future__ import annotations

from pathlib import Path

import pytest

from cinefactory.animal_long_slide import LongSlideQC, SceneCompatibilityGate
from cinefactory.animal_long_slide.contracts import LongSlideSceneKind
from cinefactory.animal_long_slide.planner import LongSlideEpisodePlanner, ModuleDirective
from cinefactory.animal_long_slide.director import VariationDirector
from cinefactory.animal_long_slide.safety import MonetizationSafetyGate
from cinefactory.animal_long_slide.variation import (
    CAMERA_PATTERNS,
    EpisodeHistory,
    SeriesBible,
    VariationExhaustedError,
    VariationPolicy,
    title_similarity,
)


ROOT = Path(__file__).resolve().parents[1]


def _series(n: int, history: EpisodeHistory | None = None, *, seed: int = 11):
    history = EpisodeHistory() if history is None else history
    director = VariationDirector(SeriesBible.default(), history)
    out = []
    for i in range(n):
        varied = director.next_episode(
            project_id="STU_VAR",
            episode_id=f"EP_{i + 1:03d}",
            target_duration_seconds=330,
            seed=seed + i,
        )
        history.append(varied)
        out.append(varied)
    return out, history


def test_bible_loads_from_config_and_has_enough_axes():
    bible = SeriesBible.load(ROOT / "config" / "animal_long_slide" / "series_bible.yaml")
    assert bible.brand
    assert len(bible.cast) >= 6
    assert len(bible.environments) >= 6
    assert len(bible.formats) >= 6
    assert len({c.name for c in bible.cast}) == len(bible.cast)
    assert len({c.animal_id for c in bible.cast}) == len(bible.cast)


def test_every_episode_in_a_long_series_changes_on_enough_axes():
    episodes, _ = _series(14)
    policy = VariationPolicy()
    for index, varied in enumerate(episodes):
        assert varied.report.passed, varied.report.findings
        assert varied.safety.passed, varied.safety.findings
        for previous in episodes[max(0, index - policy.compare_window):index]:
            changed = sum(
                1 for axis in policy.axes
                if varied.fingerprint[axis] != previous.fingerprint[axis]
            )
            assert changed >= policy.min_axis_changes


def test_cooldowns_rotate_format_lead_environment_and_ending():
    episodes, _ = _series(12)
    policy = VariationPolicy()
    for axis, cooldown in policy.cooldowns.items():
        values = [e.fingerprint[axis] for e in episodes]
        for i in range(len(values)):
            window = values[max(0, i - cooldown):i]
            assert values[i] not in window, (axis, i, values)


def test_structural_similarity_stays_below_threshold():
    episodes, _ = _series(10)
    policy = VariationPolicy()
    for varied in episodes:
        assert varied.report.max_similarity <= policy.max_structural_similarity


def test_inside_one_episode_modules_are_varied_and_qc_clean():
    (varied,), _ = _series(1)
    episode = varied.episode
    modules = episode.modules
    assert len({m.outcome for m in modules}) >= 3
    assert len({m.scene_kind for m in modules}) >= 3
    assert all(not SceneCompatibilityGate.findings(m) for m in modules)
    combos = [(m.animal_id, m.scene_kind, tuple(o.obstacle_id for o in m.obstacles), m.outcome) for m in modules]
    assert len(set(combos)) == len(combos)
    sequences = [tuple(b.pattern_id for b in m.camera_beats) for m in modules]
    assert all(a != b for a, b in zip(sequences, sequences[1:]))
    assert all(b.pattern_id in CAMERA_PATTERNS for m in modules for b in m.camera_beats)
    assert modules[0].metadata["character_id"] == varied.concept.lead_character_id
    assert modules[-1].metadata["character_id"] == varied.concept.lead_character_id
    assert all("environment" in m.metadata for m in modules)
    assert LongSlideQC().review(episode).passed


def test_peril_is_capped_and_always_resolves_positively():
    episodes, _ = _series(10)
    policy = VariationPolicy()
    for varied in episodes:
        modules = varied.episode.modules
        peril = [m for m in modules if m.metadata.get("peril")]
        assert len(peril) <= max(1, int(len(modules) * policy.max_peril_share))
        assert all(m.outcome.value in {"ESCAPE", "SUCCESS"} for m in peril)
        assert modules[-1].outcome.value in {"SUCCESS", "TRANSFORM"}


def test_titles_are_branded_unique_and_policy_safe():
    episodes, _ = _series(12)
    titles = [e.package.title for e in episodes]
    assert len(set(titles)) == len(titles)
    for i, title in enumerate(titles):
        assert len(title) <= 100
        assert SeriesBible.default().brand in title
        for previous in titles[max(0, i - 30):i]:
            assert title_similarity(title, previous) <= VariationPolicy().max_title_similarity
    assert all(e.package.made_for_kids is True for e in episodes)
    assert all(e.package.requires_human_approval is True for e in episodes)


def test_history_persists_and_reloads(tmp_path):
    path = tmp_path / "history" / "channel.jsonl"
    history = EpisodeHistory(path)
    episodes, _ = _series(3, history)
    reloaded = EpisodeHistory(path)
    assert [r.episode_id for r in reloaded.records()] == [e.episode.episode_id for e in episodes]
    assert reloaded.records()[-1].fingerprint == episodes[-1].fingerprint
    assert reloaded.records()[-1].title == episodes[-1].package.title


def test_gate_blocks_a_repeated_episode():
    (varied,), history = _series(1)
    report = MonetizationSafetyGate().review(varied, history)
    codes = {f.code for f in report.findings}
    assert report.passed is False
    assert "VARIATION_TOO_SIMILAR" in codes
    assert "TITLE_TOO_SIMILAR" in codes


def test_gate_blocks_franchise_terms_distress_and_missing_kids_flag():
    (varied,), _ = _series(1)
    bad = varied.model_copy(deep=True)
    bad.package.title = "Spiderman Long Slide with crying Elephant - Sunny Paws Slide Club"
    bad.package.made_for_kids = False
    report = MonetizationSafetyGate().review(bad, EpisodeHistory())
    codes = {f.code for f in report.findings}
    assert report.passed is False
    assert {"BLOCKED_IP_TERM", "DISTRESS_LANGUAGE", "MADE_FOR_KIDS_NOT_SET"} <= codes


def test_gate_blocks_copied_competitor_template_and_keyword_stuffing():
    (varied,), _ = _series(1)
    bad = varied.model_copy(deep=True)
    bad.package.title = (
        "Long Slide Game With Cow Elephant Gorilla Hippopotamus Tiger Lion Dinosaur 3d Animal Game Funny 3d Animals"
    )
    report = MonetizationSafetyGate().review(bad, EpisodeHistory())
    codes = {f.code for f in report.findings}
    assert {"TITLE_MISSING_BRAND", "KEYWORD_STUFFING", "TITLE_TOO_LONG", "COMPETITOR_TEMPLATE"} <= codes


def test_director_fails_closed_when_every_option_is_on_cooldown():
    bible = SeriesBible.default()
    tiny = bible.model_copy(update={"formats": bible.formats[:1]}, deep=True)
    history = EpisodeHistory()
    director = VariationDirector(tiny, history)
    first = director.next_episode(project_id="P", episode_id="E1", target_duration_seconds=200, seed=1)
    history.append(first)
    with pytest.raises(VariationExhaustedError):
        director.next_episode(project_id="P", episode_id="E2", target_duration_seconds=200, seed=2)


def test_planner_honours_directives_and_keeps_default_behaviour():
    directives = [
        ModuleDirective(
            animal_id="elephant", scene_kind=LongSlideSceneKind.LONG_SLIDE, outcome="SUCCESS",
            camera_patterns=["wide_establish", "chase", "finish_reaction"], obstacle_ids=["bridge"],
            metadata={"character_id": "ellie"},
        ),
        ModuleDirective(
            animal_id="tiger", scene_kind=LongSlideSceneKind.FOUNTAIN, outcome="TRANSFORM",
            camera_patterns=["top_down", "low_front", "obstacle_side"], obstacle_ids=["water_pool"],
        ),
    ]
    episode = LongSlideEpisodePlanner(seed=3).plan(
        project_id="P", episode_id="E", title="t", target_duration_seconds=80, module_plan=directives,
    )
    assert [m.animal_id for m in episode.modules] == ["elephant", "tiger"]
    assert episode.modules[1].obstacles[0].obstacle_id == "water_pool"
    assert episode.modules[0].metadata["character_id"] == "ellie"
    assert episode.modules[0].camera_beats[0].pattern_id == "wide_establish"
    assert all(b.end_seconds - b.start_seconds <= 12.0 for m in episode.modules for b in m.camera_beats)
    default = LongSlideEpisodePlanner(seed=3).plan(
        project_id="P", episode_id="E", title="t", target_duration_seconds=80, animals=["cow", "tiger"],
    )
    assert default.modules[0].camera_beats[0].pattern_id == "hero_start"


def test_series_cli_plans_without_writing_history_and_approves_once(tmp_path, monkeypatch):
    cli = _load_cli()
    base = ["plan_long_slide_series.py", "--channel", "test", "--data-dir", str(tmp_path)]

    monkeypatch.setattr("sys.argv", [*base, "--count", "2"])
    assert cli.main() == 0
    history_file = tmp_path / "test" / "history.jsonl"
    assert not history_file.exists()
    for ep in ("EP_0001", "EP_0002"):
        folder = tmp_path / "test" / "episodes" / ep
        assert (folder / "upload_package.json").is_file()
        assert (folder / "safety_report.json").is_file()

    monkeypatch.setattr("sys.argv", [*base, "--approve", "EP_0001"])
    assert cli.main() == 0
    assert len(EpisodeHistory(history_file).records()) == 1
    monkeypatch.setattr("sys.argv", [*base, "--approve", "EP_0001"])
    assert cli.main() == cli.EXIT_ALREADY_RECORDED


def test_cli_approve_rejects_a_tampered_episode(tmp_path, monkeypatch):
    cli = _load_cli()
    base = ["x", "--channel", "test", "--data-dir", str(tmp_path)]
    monkeypatch.setattr("sys.argv", [*base, "--count", "2"])
    assert cli.main() == 0
    monkeypatch.setattr("sys.argv", [*base, "--approve", "EP_0001"])
    assert cli.main() == 0
    first = (tmp_path / "test" / "episodes" / "EP_0001" / "varied_episode.json").read_text(encoding="utf-8")
    clone = first.replace('"episode_id": "EP_0001"', '"episode_id": "EP_0002"')
    (tmp_path / "test" / "episodes" / "EP_0002" / "varied_episode.json").write_text(clone, encoding="utf-8")
    monkeypatch.setattr("sys.argv", [*base, "--approve", "EP_0002"])
    assert cli.main() == cli.EXIT_REJECTED


def test_company_adapter_plans_varied_series_episode():
    from cinefactory.studio.contracts import StudioProjectSpec
    from cinefactory.studio.long_slide_adapter import LongSlideCompanyAdapter

    project = StudioProjectSpec(prompt="Long Slide 3D animal game", duration_seconds=300)
    history = EpisodeHistory()
    adapter = LongSlideCompanyAdapter()
    first = adapter.plan_series_episode(project, history=history, episode_id="EP_A", seed=5)
    history.append(first)
    second = adapter.plan_series_episode(project, history=history, episode_id="EP_B", seed=6)
    assert first.safety.passed and second.safety.passed
    assert first.fingerprint["format"] != second.fingerprint["format"]
    assert abs(second.episode.planned_duration_seconds - 300) < 0.01


# ---------- regressions from code review ----------

def _load_cli():
    import importlib.util

    spec = importlib.util.spec_from_file_location("plan_series", ROOT / "scripts" / "plan_long_slide_series.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return cli


def test_cli_never_overwrites_an_existing_episode_folder(tmp_path, monkeypatch):
    cli = _load_cli()
    base = ["x", "--channel", "test", "--data-dir", str(tmp_path)]
    monkeypatch.setattr("sys.argv", [*base, "--count", "3"])
    assert cli.main() == 0
    for ep in ("EP_0001", "EP_0003"):
        monkeypatch.setattr("sys.argv", [*base, "--approve", ep])
        assert cli.main() == 0
    approved = (tmp_path / "test" / "episodes" / "EP_0003" / "varied_episode.json").read_text(encoding="utf-8")
    monkeypatch.setattr("sys.argv", [*base, "--count", "1"])
    assert cli.main() == 0
    assert (tmp_path / "test" / "episodes" / "EP_0003" / "varied_episode.json").read_text(encoding="utf-8") == approved
    assert (tmp_path / "test" / "episodes" / "EP_0004").is_dir()


def test_cli_rejects_path_traversal(tmp_path, monkeypatch):
    cli = _load_cli()
    monkeypatch.setattr("sys.argv", ["x", "--channel", "../evil", "--data-dir", str(tmp_path)])
    assert cli.main() == cli.EXIT_BAD_INPUT
    monkeypatch.setattr("sys.argv", ["x", "--channel", "ok", "--data-dir", str(tmp_path), "--approve", "../EP_0001"])
    assert cli.main() == cli.EXIT_BAD_INPUT


def test_gate_recomputes_fingerprint_instead_of_trusting_stored_values():
    (varied,), history = _series(1)
    forged = varied.model_copy(deep=True)
    forged.fingerprint = {axis: f"forged-{axis}" for axis in forged.fingerprint}
    forged.tokens = ["forged"]
    forged.package.title = "Totally Different Words Here | Zoomi Slide Club"
    forged.episode.title = forged.package.title
    codes = {f.code for f in MonetizationSafetyGate().review(forged, history).findings}
    assert "VARIATION_TOO_SIMILAR" in codes
    assert "EVIDENCE_MISMATCH" in codes


def test_gate_derives_peril_from_scene_and_obstacles():
    (varied,), _ = _series(1)
    tampered = varied.model_copy(deep=True)
    module = tampered.episode.modules[1]
    module.scene_kind = LongSlideSceneKind.KEY_DOOR
    module.obstacles[0].obstacle_id = "cage"
    module.outcome = module.outcome.__class__("COMIC_FAIL")
    module.metadata["peril"] = False
    codes = {f.code for f in MonetizationSafetyGate().review(tampered, EpisodeHistory()).findings}
    assert "PERIL_UNRESOLVED" in codes


def test_gate_rejects_exact_title_anywhere_in_history():
    episodes, history = _series(3)
    copy = episodes[2].model_copy(deep=True)
    old = history.records()[0]
    copy.package.title = old.title
    copy.episode.title = old.title
    long_window = VariationPolicy(title_window=1, compare_window=1)
    codes = {f.code for f in MonetizationSafetyGate(long_window).review(copy, history).findings}
    assert "DUPLICATE_TITLE" in codes


@pytest.mark.parametrize("title", [
    "Pokémon Slide Party | Zoomi Slide Club",
    "Spider‑Man Long Slide | Zoomi Slide Club",
    "Baby Shark Water Slide | Zoomi Slide Club",
    "Mario and Friends Slide | Zoomi Slide Club",
    "Hello Kitty Slide Day | Zoomi Slide Club",
])
def test_gate_catches_franchise_terms_with_accents_and_odd_hyphens(title):
    (varied,), _ = _series(1)
    bad = varied.model_copy(deep=True)
    bad.package.title = title
    bad.episode.title = title
    codes = {f.code for f in MonetizationSafetyGate().review(bad, EpisodeHistory()).findings}
    assert "BLOCKED_IP_TERM" in codes


@pytest.mark.parametrize("word", ["cried", "hurts", "scary", "crashed", "tears", "afraid", "stuck", "screams", "dangers"])
def test_gate_catches_inflected_distress_words(word):
    (varied,), _ = _series(1)
    bad = varied.model_copy(deep=True)
    bad.package.description = f"The little cow {word} on the slide."
    codes = {f.code for f in MonetizationSafetyGate().review(bad, EpisodeHistory()).findings}
    assert "DISTRESS_LANGUAGE" in codes


def test_gate_counts_plural_animal_names_as_stuffing():
    (varied,), _ = _series(1)
    bad = varied.model_copy(deep=True)
    bad.package.title = "Cows Elephants Gorillas Hippos Tigers on the Slide | Zoomi Slide Club"
    bad.episode.title = bad.package.title
    codes = {f.code for f in MonetizationSafetyGate().review(bad, EpisodeHistory()).findings}
    assert "KEYWORD_STUFFING" in codes


def test_bible_rejects_bad_templates_tiny_cast_and_empty_camera_variants():
    from pydantic import ValidationError

    data = SeriesBible.default().model_dump(mode="json")
    bad_title = {**data, "formats": [{**data["formats"][0], "title_templates": ["{environment} | {brand}"]}]}
    bad_synopsis = {**data, "formats": [{**data["formats"][0], "synopsis_templates": ["{crew} slide"]}]}
    tiny_cast = {**data, "min_cast": 2}
    empty_cam = {**data, "camera_styles": [{"style_id": "x", "variants": [[], ["chase"]]}, *data["camera_styles"]]}
    for broken in (bad_title, bad_synopsis, tiny_cast, empty_cam):
        with pytest.raises(ValidationError):
            SeriesBible.model_validate(broken)


def test_policy_rejects_settings_that_disable_checks():
    from pydantic import ValidationError

    for kwargs in ({"compare_window": 0}, {"title_window": 0}, {"min_axis_changes": 0},
                   {"max_structural_similarity": 0}, {"cooldowns": {"format": -1}}):
        with pytest.raises(ValidationError):
            VariationPolicy(**kwargs)


def test_planner_rejects_empty_module_plan():
    with pytest.raises(ValueError):
        LongSlideEpisodePlanner(seed=1).plan(
            project_id="P", episode_id="E", title="t", target_duration_seconds=80, module_plan=[],
        )


def test_directed_module_ends_on_its_last_camera_pattern():
    (varied,), _ = _series(1)
    for module in varied.episode.modules:
        patterns = [b.pattern_id for b in module.camera_beats]
        assert all(a != b for a, b in zip(patterns, patterns[1:]))
    directive = ModuleDirective(
        animal_id="cow", scene_kind=LongSlideSceneKind.LONG_SLIDE, outcome="SUCCESS",
        camera_patterns=["hero_start", "chase", "obstacle_side", "finish_reaction"], obstacle_ids=["bridge"],
    )
    other = ModuleDirective(
        animal_id="tiger", scene_kind=LongSlideSceneKind.FOUNTAIN, outcome="TRANSFORM",
        camera_patterns=["wide_establish", "low_front", "chase"], obstacle_ids=["water_pool"],
    )
    episode = LongSlideEpisodePlanner(seed=2).plan(
        project_id="P", episode_id="E", title="t", target_duration_seconds=90, module_plan=[directive, other],
    )
    assert episode.modules[0].camera_beats[0].pattern_id == "hero_start"
    assert episode.modules[0].camera_beats[-1].pattern_id == "finish_reaction"
    assert episode.modules[1].camera_beats[-1].pattern_id == "chase"


def test_history_append_survives_a_truncated_last_line(tmp_path):
    path = tmp_path / "h.jsonl"
    history = EpisodeHistory(path)
    episodes, _ = _series(2, history)
    path.write_text(path.read_text(encoding="utf-8").rstrip("\n"), encoding="utf-8")
    again = EpisodeHistory(path)
    again.append(episodes[1].model_copy(update={"episode": episodes[1].episode.model_copy(update={"episode_id": "EP_X"})}))
    assert [r.episode_id for r in EpisodeHistory(path).records()][-1] == "EP_X"


def test_lookdev_has_a_biome_and_toy_camera_for_every_theme_and_pattern():
    import ast

    source = (ROOT / "scripts" / "long_slide_lookdev.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    assigned = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Dict):
            assigned[node.targets[0].id] = {k.value for k in node.value.keys if isinstance(k, ast.Constant)}
    for env in SeriesBible.default().environments:
        assert env.theme_id in assigned["BIOMES"], env.theme_id
    assert set(CAMERA_PATTERNS) <= assigned["TOY_CAMERA_CANDIDATES"]
    worker = (ROOT / "scripts" / "render_long_slide_job.py").read_text(encoding="utf-8")
    assert "apply_lookdev(" in worker and "--still" in worker


def test_render_worker_knows_every_camera_pattern_and_reads_environment():
    worker = (ROOT / "scripts" / "render_long_slide_job.py").read_text(encoding="utf-8")
    for pattern in CAMERA_PATTERNS:
        assert f'"{pattern}"' in worker
    assert '"environment"' in worker
