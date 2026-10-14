"""Character FX: race companions, cartoon eyes, paint gates (planning side + worker contracts)."""
from __future__ import annotations

import ast
import random
import re
import sys
from pathlib import Path

import pytest

from cinefactory.animal_long_slide import execution as execution_module
from cinefactory.animal_long_slide.blender_binder import LongSlideBlenderBinder
from cinefactory.animal_long_slide.contracts import LongSlideEpisodeSpec, LongSlideSceneKind, OutcomeKind
from cinefactory.animal_long_slide.director import VariationDirector
from cinefactory.animal_long_slide.execution import LongSlideExecutionPlanner
from cinefactory.animal_long_slide.motion import MotionCompatibilityGraph
from cinefactory.animal_long_slide.planner import LongSlideEpisodePlanner, ModuleDirective
from cinefactory.animal_long_slide.registry import LongSlideAssetRegistry
from cinefactory.animal_long_slide.series import PERIL_OBSTACLES, PERIL_SCENES
from cinefactory.animal_long_slide.variation import EpisodeHistory, SeriesBible

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import long_slide_fx_plan as fx  # noqa: E402


# ---------- pure FX planning ----------

def test_lanes_put_the_lead_in_the_centre():
    assert fx.lane_offsets(1) == [0.0]
    lanes = fx.lane_offsets(3)
    assert lanes[0] == 0.0 and lanes[1] < 0 < lanes[2]
    assert all(abs(x) < 2.0 for x in lanes)  # inside the slide rails (|x| < 2.6)
    with pytest.raises(ValueError):
        fx.lane_offsets(0)
    with pytest.raises(ValueError):
        fx.lane_offsets(4)


def test_race_paces_follow_the_outcome():
    for seed in range(20):
        assert all(p > 1.0 for p in fx.race_paces("SUCCESS", 2, seed))
        assert all(p < 1.0 for p in fx.race_paces("COMIC_FAIL", 2, seed))
        mixed = fx.race_paces("TRANSFORM", 2, seed)
        assert (mixed[0] - 1.0) * (mixed[1] - 1.0) <= 0  # one ahead, one behind
    assert fx.race_paces("ESCAPE", 2, 5) == fx.race_paces("ESCAPE", 2, 5)
    assert fx.race_paces("SUCCESS", 0, 1) == []
    with pytest.raises(ValueError):
        fx.race_paces("SUCCESS", fx.MAX_COMPANIONS + 1, 1)


def test_blinks_are_irregular_and_fit_the_module():
    fps, end = 24, 192
    starts = fx.blink_starts(end, fps, seed=3)
    span = fx.BLINK_CLOSE_FRAMES + fx.BLINK_HOLD_FRAMES + fx.BLINK_OPEN_FRAMES
    assert len(starts) >= 2
    assert all(1 < s and s + span <= end for s in starts)
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    assert all(g >= fx.BLINK_MIN_SECONDS * fps - 1 for g in gaps)
    assert len(set(gaps)) > 1 or len(gaps) <= 1
    assert fx.blink_starts(end, fps, seed=3) != fx.blink_starts(end, fps, seed=4)
    assert fx.blink_starts(1, fps, seed=1) == []


def test_blink_keys_close_and_reopen():
    keys = fx.blink_keys(10)
    frames = [f for f, _ in keys]
    assert frames == sorted(frames) and frames[0] == 10
    assert keys[0][1] == 1.0 and keys[-1][1] == 1.0
    assert min(v for _, v in keys) == fx.BLINK_CLOSED_SCALE


def test_paint_colours_are_distinct_and_vary_by_seed():
    colors = fx.paint_colors(3, seed=1)
    assert len(set(colors)) == 3
    assert colors == fx.paint_colors(3, seed=1)
    assert any(fx.paint_colors(3, seed=s) != colors for s in range(2, 8))
    with pytest.raises(ValueError):
        fx.paint_colors(0, seed=1)


def test_curtain_strips_fill_the_gate_without_overlap():
    strips = fx.curtain_strips(-1.85, 1.85)
    assert len(strips) >= 8
    assert strips == sorted(strips)
    assert strips[0] - 0.13 >= -1.85 - 1e-9 and strips[-1] + 0.13 <= 1.85 + 1e-9
    assert all(b - a >= 0.26 for a, b in zip(strips, strips[1:]))
    assert fx.curtain_strips(0.0, 0.1) == [0.05]
    lanes = fx.lane_offsets(3)
    assert fx.lane_for_x(-1.4, lanes) == 1 and fx.lane_for_x(0.2, lanes) == 0


# ---------- director ----------

def _episode(director: VariationDirector, seed: int = 11):
    return director.next_episode(project_id="STU_FX", episode_id="EP_FX", target_duration_seconds=330, seed=seed)


def test_director_adds_friends_to_non_peril_modules_only():
    bible = SeriesBible.default()
    seen_race = False
    for seed in range(11, 19):
        varied = _episode(VariationDirector(bible, EpisodeHistory()), seed)
        cast_animals = {bible.character(c).animal_id for c in varied.concept.cast_ids}
        for module in varied.episode.modules:
            companions = module.metadata["companions"]
            assert len(companions) <= fx.MAX_COMPANIONS
            assert module.animal_id not in companions
            assert len(set(companions)) == len(companions)
            assert set(companions) <= cast_animals
            peril = module.scene_kind in PERIL_SCENES or any(o.obstacle_id in PERIL_OBSTACLES for o in module.obstacles)
            if peril:
                assert companions == []
            seen_race = seen_race or bool(companions)
    assert seen_race


def test_director_only_picks_renderable_friends():
    bible = SeriesBible.default()
    renderable = {"cow", "duck"}
    varied = _episode(VariationDirector(bible, EpisodeHistory(), renderable_animals=renderable), 13)
    for module in varied.episode.modules:
        assert set(module.metadata["companions"]) <= renderable
    nobody = _episode(VariationDirector(bible, EpisodeHistory(), renderable_animals=set()), 13)
    assert all(m.metadata["companions"] == [] for m in nobody.episode.modules)


# ---------- execution planner + binder ----------

def _race_episode(companions, lead="cow", scene=LongSlideSceneKind.LONG_SLIDE):
    directive = ModuleDirective(
        animal_id=lead, scene_kind=scene, outcome=OutcomeKind.SUCCESS,
        camera_patterns=["hero_start", "chase", "finish_reaction"], obstacle_ids=[],
        metadata={"companions": companions},
    )
    module = LongSlideEpisodePlanner(seed=5)._directed_module(0, directive, 12.0, random.Random(0))
    return LongSlideEpisodeSpec(project_id="STU_FX", episode_id="EP_RACE", title="race", target_duration_seconds=16,
                                modules=[module], originality_signature=LongSlideEpisodeSpec.signature_for([module]))


def test_execution_resolves_companion_assets_and_motions(tmp_path):
    registry = LongSlideAssetRegistry.load(ROOT)
    motions = MotionCompatibilityGraph.load(ROOT)
    plan = LongSlideExecutionPlanner(registry, motions).plan(
        _race_episode(["pig", "sheep"]), output_dir=tmp_path, render_preview=True)
    assert plan.executable, plan.blockers
    job = plan.jobs[0]
    assert {"animal.pig", "animal.sheep"} <= set(job.required_asset_ids)
    assert set(job.companion_motions) == {"pig", "sheep"}
    assert all(m[0].semantic_action == "run" for m in job.companion_motions.values())

    payload = LongSlideBlenderBinder(ROOT, blender_executable=ROOT / "missing.exe", registry=registry).compile_payload(job)
    rows = {row["asset_id"]: row for row in payload["companions"]}
    assert set(rows) == {"animal.pig", "animal.sheep"}
    for row in rows.values():
        assert Path(row["path"]).is_file()
        assert row["motions"] and Path(row["motions"][0]["local_path"]).is_file()


def test_solo_modules_compile_an_empty_companion_list(tmp_path):
    registry = LongSlideAssetRegistry.load(ROOT)
    plan = LongSlideExecutionPlanner(registry, MotionCompatibilityGraph.load(ROOT)).plan(
        _race_episode([]), output_dir=tmp_path, render_preview=True)
    assert plan.executable, plan.blockers
    payload = LongSlideBlenderBinder(ROOT, blender_executable=ROOT / "missing.exe", registry=registry).compile_payload(plan.jobs[0])
    assert payload["companions"] == []


@pytest.mark.parametrize("companions, code", [
    (["cow"], "same_as_lead"),
    (["pig", "sheep", "zebra"], "too_many"),
    (["../evil"], "bad_id"),
    (["pig", "pig"], "duplicate"),
    ("pig", "not_a_list"),
])
def test_invalid_companions_block_execution(tmp_path, companions, code):
    registry = LongSlideAssetRegistry.load(ROOT)
    plan = LongSlideExecutionPlanner(registry, MotionCompatibilityGraph.load(ROOT)).plan(
        _race_episode(companions), output_dir=tmp_path, render_preview=True)
    assert not plan.executable
    assert any(b.startswith("INVALID_COMPANION:") and code in b for b in plan.blockers), plan.blockers


def test_companion_without_locomotion_blocks_execution(tmp_path):
    registry = LongSlideAssetRegistry.load(ROOT)
    plan = LongSlideExecutionPlanner(registry, MotionCompatibilityGraph.load(ROOT)).plan(
        _race_episode(["elephant"]), output_dir=tmp_path, render_preview=True)
    assert not plan.executable
    assert any("MISSING_MOTION:animal.elephant" in b for b in plan.blockers)


def test_unknown_companion_asset_blocks_execution(tmp_path):
    registry = LongSlideAssetRegistry.load(ROOT)
    plan = LongSlideExecutionPlanner(registry, MotionCompatibilityGraph.load(ROOT)).plan(
        _race_episode(["unicorn"]), output_dir=tmp_path, render_preview=True)
    assert "MISSING_ASSET:animal.unicorn" in plan.blockers


def test_companion_limit_matches_worker_lanes():
    assert execution_module.MAX_COMPANIONS == fx.MAX_COMPANIONS
    assert len(fx.LANE_OFFSETS) == fx.MAX_COMPANIONS + 1


# ---------- worker contracts (bpy-free checks) ----------

def _worker_functions(*names):
    source = (SCRIPTS / "render_long_slide_job.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    picked = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assigns = [node for node in tree.body if isinstance(node, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "LOCOMOTION_RANK" for t in node.targets)]
    module = ast.Module(body=assigns + picked, type_ignores=[])
    namespace = {"re": re}
    exec(compile(module, "render_long_slide_job.py", "exec"), namespace)
    return namespace


class _Action:
    def __init__(self, name):
        self.name = name


def test_worker_prefers_locomotion_over_idle():
    ns = _worker_functions("base_action_name", "select_source_action")
    actions = [_Action(n) for n in ("Idle", "Run", "Walk", "Death")]
    motions = [
        {"semantic_action": "idle", "source_action": "Idle"},
        {"semantic_action": "run", "source_action": "Run"},
    ]
    assert ns["select_source_action"](motions, actions).name == "Run"


def test_worker_matches_renamed_appended_actions():
    ns = _worker_functions("base_action_name", "select_source_action")
    assert ns["base_action_name"]("Run.001") == "Run"
    assert ns["base_action_name"]("Run.v2") == "Run.v2"
    actions = [_Action("Idle.002"), _Action("Gallop.002")]
    assert ns["select_source_action"]([{"semantic_action": "run", "source_action": "Gallop"}], actions).name == "Gallop.002"


def test_worker_wires_eyes_race_and_paint_gates():
    source = (SCRIPTS / "render_long_slide_job.py").read_text(encoding="utf-8")
    for needle in ("add_cartoon_eyes(", "apply_paint_gates(", "race_paces(", "lane_offsets(", "foreground_clutter("):
        assert needle in source, needle
    lookdev = (SCRIPTS / "long_slide_lookdev.py").read_text(encoding="utf-8")
    assert '"companion"' in lookdev and "ensure_node_material(" in lookdev
    fx_source = (SCRIPTS / "long_slide_fx.py").read_text(encoding="utf-8")
    assert 'event") == "paint_transform"' in fx_source


# ---------- real CC0 set dressing ----------

from cinefactory.animal_long_slide.foundry import AssetFoundry  # noqa: E402
from cinefactory.animal_long_slide import kit_props as kit_props_module  # noqa: E402
from cinefactory.animal_long_slide.kit_props import (  # noqa: E402
    KitPropCatalog,
    KitPropConfig,
    KitPropRow,
    approved_license_roots,
)
from cinefactory.animal_long_slide.contracts import LicenseState  # noqa: E402

KIT_PACKS = {
    "kenney.coaster_kit", "kenney.marble_kit", "kenney.platformer_kit", "kenney.nature_kit",
    "kenney.food_kit", "kenney.holiday_kit", "quaternius.ultimate_platformer",
}
UNSAFE_PROP_WORDS = ("bomb", "saw", "spike", "skull", "gun", "cannon", "hazard", "trap", "knife")


def test_prop_packs_are_registered_as_approved_cc0():
    packs = {p.pack_id: p for p in AssetFoundry.load_source_packs(ROOT)}
    assert KIT_PACKS <= set(packs)
    for pack_id in KIT_PACKS:
        pack = packs[pack_id]
        assert pack.license_state is LicenseState.APPROVED and pack.commercial_use
        assert pack.license_name == "CC0-1.0"
        assert pack.license_evidence_uri.endswith("License.txt")


def test_every_theme_resolves_real_props_from_approved_packs():
    catalog = KitPropCatalog.load(ROOT)
    bible = SeriesBible.default()
    for env in bible.environments:
        rows = catalog.rows_for(env.theme_id)
        assert any(r["zone"] == "backdrop" for r in rows), env
        assert any(r["zone"] == "finish" for r in rows)
        assert any(r["zone"] == "air" for r in rows)
        assert all(Path(r["path"]).is_file() for r in rows)
        assert {r["pack"] for r in rows} <= KIT_PACKS
    assert catalog.findings == []
    assert catalog.rows_for(None) == []


def test_prop_catalog_is_kid_safe():
    config = KitPropCatalog.load(ROOT).config
    rows = list(config.common) + [r for rows in config.themes.values() for r in rows]
    for row in rows:
        assert not any(word in row.file.lower() for word in UNSAFE_PROP_WORDS), row.file


@pytest.mark.parametrize("bad", ["../secrets.glb", "C:/Windows/x.glb", "/etc/x.glb", "tree.exe"])
def test_prop_rows_reject_unsafe_paths(bad):
    with pytest.raises(ValueError):
        KitPropRow(pack="kenney.nature_kit", file=bad, zone="backdrop", count=1, height=1.0)


def test_unapproved_pack_rows_are_dropped(tmp_path):
    pack_dir = tmp_path / "pack"
    pack_dir.mkdir()
    (pack_dir / "tree.glb").write_bytes(b"glTF")
    config = KitPropConfig(
        packs={"x.unvetted": "pack", "x.vetted": "pack"},
        themes={"sunny_park": [
            KitPropRow(pack="x.unvetted", file="tree.glb", zone="backdrop", count=2, height=3.0),
            KitPropRow(pack="x.vetted", file="tree.glb", zone="backdrop", count=2, height=3.0),
            KitPropRow(pack="x.vetted", file="missing.glb", zone="backdrop", count=1, height=3.0),
        ]},
    )
    catalog = KitPropCatalog(tmp_path, config, approved_packs={"x.vetted": pack_dir})
    rows = catalog.rows_for("sunny_park")
    catalog.rows_for("sunny_park")
    assert len(catalog.findings) == len(set(catalog.findings))  # no duplicates across calls
    assert [r["pack"] for r in rows] == ["x.vetted"]
    assert "KIT_PACK_NOT_APPROVED:x.unvetted" in catalog.findings
    assert "KIT_FILE_MISSING:x.vetted:missing.glb" in catalog.findings


def test_undeclared_pack_in_config_is_rejected(tmp_path):
    config = KitPropConfig(packs={}, common=[KitPropRow(pack="x.ghost", file="a.glb", zone="air", count=1, height=1)])
    with pytest.raises(ValueError):
        KitPropCatalog(tmp_path, config, approved_packs={})


def test_binder_ships_props_for_themed_modules_only(tmp_path):
    registry = LongSlideAssetRegistry.load(ROOT)
    motions = MotionCompatibilityGraph.load(ROOT)
    binder = LongSlideBlenderBinder(ROOT, blender_executable=ROOT / "missing.exe", registry=registry)
    themed = _race_episode([])
    module = themed.modules[0].model_copy(update={"metadata": {
        **themed.modules[0].metadata,
        "environment": SeriesBible.default().environment("snow_peak").render_settings(),
    }})
    themed = themed.model_copy(update={"modules": [module]})
    job = LongSlideExecutionPlanner(registry, motions).plan(themed, output_dir=tmp_path, render_preview=True).jobs[0]
    payload = binder.compile_payload(job)
    assert payload["kit_props"] and all(Path(r["path"]).is_file() for r in payload["kit_props"])
    plain = LongSlideExecutionPlanner(registry, motions).plan(_race_episode([]), output_dir=tmp_path, render_preview=True).jobs[0]
    assert binder.compile_payload(plain)["kit_props"] == []


def test_pack_folder_must_sit_under_its_licence_file(tmp_path):
    licensed = tmp_path / "licensed"
    other = tmp_path / "other"
    for folder in (licensed, other):
        folder.mkdir()
        (folder / "tree.glb").write_bytes(b"glTF")
    config = KitPropConfig(
        packs={"x.pack": "other"},
        themes={"sunny_park": [KitPropRow(pack="x.pack", file="tree.glb", zone="backdrop", count=1, height=3)]},
    )
    catalog = KitPropCatalog(tmp_path, config, approved_packs={"x.pack": licensed})
    assert catalog.rows_for("sunny_park") == []
    assert "KIT_PACK_OUTSIDE_LICENSE_ROOT:x.pack" in catalog.findings


@pytest.mark.parametrize("folder", ["../outside", "C:/assets", "/abs/assets", ""])
def test_pack_folders_must_be_relative(folder):
    with pytest.raises(ValueError):
        KitPropConfig(packs={"x.pack": folder})


def _write_packs(root, rows):
    path = root / "config" / "animal_long_slide" / "source_packs.yaml"
    path.parent.mkdir(parents=True)
    import yaml
    path.write_text(yaml.safe_dump({"source_packs": rows}), encoding="utf-8")


def _pack(pack_id, evidence, state="APPROVED", commercial=True):
    return {"pack_id": pack_id, "title": pack_id, "provider": "x", "source_uri": "https://example.org",
            "license_name": "CC0-1.0", "license_evidence_uri": evidence, "license_state": state,
            "commercial_use": commercial}


def test_licence_roots_need_local_evidence_and_unanimous_approval(tmp_path):
    (tmp_path / "packs" / "a").mkdir(parents=True)
    (tmp_path / "packs" / "a" / "License.txt").write_text("CC0", encoding="utf-8")
    (tmp_path / "packs" / "b").mkdir(parents=True)
    (tmp_path / "packs" / "b" / "License.txt").write_text("CC0", encoding="utf-8")
    _write_packs(tmp_path, [
        _pack("ok.local", "packs/a/License.txt"),
        _pack("web.only", "https://example.org/license"),
        _pack("revoked", "packs/b/License.txt"),
        _pack("revoked", "packs/b/License.txt", state="RESTRICTED"),
        _pack("no.commercial", "packs/b/License.txt", commercial=False),
        _pack("missing.file", "packs/c/License.txt"),
    ])
    roots = approved_license_roots(tmp_path)
    assert set(roots) == {"ok.local"}
    assert roots["ok.local"] == (tmp_path / "packs" / "a").resolve()


def test_binder_payload_carries_prop_findings(tmp_path):
    registry = LongSlideAssetRegistry.load(ROOT)
    binder = LongSlideBlenderBinder(ROOT, blender_executable=ROOT / "missing.exe", registry=registry)
    job = LongSlideExecutionPlanner(registry, MotionCompatibilityGraph.load(ROOT)).plan(
        _race_episode([]), output_dir=tmp_path, render_preview=True).jobs[0]
    assert binder.compile_payload(job)["kit_prop_findings"] == []
    assert kit_props_module.logger.name.endswith("kit_props")
