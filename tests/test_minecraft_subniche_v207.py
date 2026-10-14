"""v207: Minecraft is not one production ontology, reuse only by explicit request."""
import pytest
from cinefactory.studio.minecraft_subniche_v207 import (
    CATALOG, Lane, classify_minecraft,assess_transfer,
    compare_for_one_channel,rank_subniche_research,
)
from cinefactory.studio.minecraft_capture_v207 import register_capture_handlers
from cinefactory.studio.contracts import StudioProjectSpec
from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.contract_integrity import audit_company_wiring
from cinefactory.studio.company_handlers import FilmCompanyHandlers
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.channel_franchise_v206 import minecraft_original_starter,ChannelLibrary
from typer.testing import CliRunner
from cinefactory.cli import app


@pytest.mark.parametrize("prompt,wanted",[
 ("Original Minecraft 3D animated adventure",Lane.FILM_ANIMATION),
 ("Minecraft livestream người chơi realtime thật",Lane.LIVE_RUNTIME),
 ("Minecraft survival gameplay recorded by real player",Lane.CAPTURED_GAMEPLAY),
 ("Minecraft scripted machinima shot inside minecraft runtime",Lane.STAGED_GAME_MACHINIMA),
 ("Minecraft school comedy animated episode",Lane.FILM_ANIMATION),
])
def test_minecraft_classifier_uses_media_provenance(prompt,wanted):
    result=classify_minecraft(prompt)
    assert not result.blocker
    assert result.production_lane == wanted


def test_live_and_story_mixed_prompts_block_instead_of_fake_blender():
    assert classify_minecraft("Minecraft realtime livestream with Blender animation").blocker
    assert classify_minecraft("Minecraft video please").blocker
    assert classify_minecraft("Minecraft original cinematic episode").blocker
    assert classify_minecraft("Minecraft original cinematic film").blocker
    assert classify_minecraft("Create an original Minecraft cinematic story about rescuing a friend.").blocker
    assert classify_minecraft(
        "Minecraft người chơi thật đang live",
        explicit_subniche="minecraft_story_adventure",
    ).blocker
    assert classify_minecraft(
        "Minecraft recorded gameplay of real players",
        explicit_subniche="minecraft_story_adventure",
    ).blocker


def test_livestream_not_accepted_as_story_or_longform_rpm_view_signal():
    live=CATALOG["minecraft_live_gameplay"]
    story=CATALOG["minecraft_story_adventure"]
    assert live.production_lane is Lane.LIVE_RUNTIME
    assert live.source_truth != story.source_truth
    assert "EXCLUDED" in live.target_output
    assert not compare_for_one_channel(live.subniche_id,story.subniche_id)[
        "can_share_channel_editorial_strategy"]
    assert compare_for_one_channel(
        "minecraft_school_comedy","minecraft_story_adventure")[
        "can_share_channel_editorial_strategy"]


@pytest.mark.parametrize("pattern,wanted",[
 ("hook_structure",True),
 ("title_clarity",True),
 ("story_structure",False),
 ("rig",False),
 ("live_scene_capture",False),
 ("production_assets",False),
])
def test_cross_group_knowledge_is_not_auto_copied(pattern,wanted):
    result=assess_transfer("minecraft_live_gameplay","minecraft_story_adventure",pattern)
    assert result["transferable_as_test_hypothesis"] is wanted
    assert result["copy_source_expression_allowed"] is False


def test_ranking_fails_closed_and_has_no_paid_credit_assumptions():
    empty=rank_subniche_research([])
    assert not empty["verified_research_shortlist"]
    reported=rank_subniche_research([
        {"subniche_id":"minecraft_live_gameplay",
         "source_provenance":"INDEPENDENTLY_REVIEWED_YOUTUBE_API_ARCHIVE",
         "distinct_new_channel_1m_longform_14d":100},
        {"subniche_id":"minecraft_story_adventure",
         "source_provenance":"SCRAPED_UNREVIEWED",
         "distinct_new_channel_1m_longform_14d":2},
    ])
    assert not reported["verified_research_shortlist"]
    assert {x["reason"] for x in reported["rejected_or_unknown"]} == {
        "LIVE_VIEWS_EXCLUDED","NO_INDEPENDENTLY_REVIEWED_PROVIDER_ARCHIVE"
    }


@pytest.mark.parametrize("subniche,wanted_first",[
 ("minecraft_live_gameplay","MC_MODE_INTAKE"),
 ("minecraft_recorded_survival","MC_MODE_INTAKE"),
 ("minecraft_scripted_machinima","MC_MODE_INTAKE"),
 ("minecraft_story_adventure","PROJECT_INTAKE"),
])
def test_orchestrator_never_routes_actual_gameplay_into_blender_story(tmp_path,subniche,wanted_first):
    kernel=build_studio_kernel(tmp_path)
    project=StudioProjectSpec(
        prompt="Minecraft original content",
        niche="minecraft",minecraft_subniche=subniche,
        duration_seconds=540,
    )
    bp=CompanyOrchestrator(kernel).build_blueprint(
        project,professional_governance=True,
    )
    assert bp.stages[0].stage_id == wanted_first
    assert audit_company_wiring(bp.stages).valid
    assert bp.minecraft_route.subniche_id==subniche
    if subniche!="minecraft_story_adventure":
        names={s.stage_id for s in bp.stages}
        assert "WRITING" not in names and "ASSET_BUILD" not in names
        assert "MC_REAL_CAPTURE" in names
        assert bp.studio_plan.product.format.value=="GAMEPLAY"
        assert bp.studio_plan.product.actual_gameplay_required is True
        assert bp.project_dna.format_rules["format"]=="GAMEPLAY"
        assert bp.production_recipe.blocked is True
        assert bp.production_recipe.tasks == []
        assert bp.executable is False
        assert "REAL_GAME_CAPTURE_NOT_YET_INDEPENDENTLY_QUALIFIED" in bp.blockers
        handlers=FilmCompanyHandlers(kernel).registry(production_route=bp.minecraft_route)
        assert set(handlers.ids())==names
    else:
        assert "WRITING" in {s.stage_id for s in bp.stages}
        assert "MC_REAL_CAPTURE" not in {s.stage_id for s in bp.stages}


def test_channel_does_not_force_existing_characters_by_default(tmp_path):
    bible=minecraft_original_starter("v207_channel_demo","Lantern Vale Stories")
    lib=ChannelLibrary(tmp_path)
    lib.register_draft(bible)
    def project(reuse):
        return StudioProjectSpec(
            prompt="Minecraft original 3D animated adventure",
            niche="minecraft",minecraft_subniche="minecraft_story_adventure",
            channel_brand_id=bible.channel_brand_id,
            series_id="lantern_trails",episode_id="lt_bridge",
            reuse_series_characters=reuse,duration_seconds=60,
        )
    kernel=build_studio_kernel(tmp_path)
    new=CompanyOrchestrator(kernel).build_blueprint(project(False),professional_governance=True)
    old=CompanyOrchestrator(kernel).build_blueprint(project(True),professional_governance=True)
    assert new.channel_episode_strategy.cast_ids == []
    assert old.channel_episode_strategy.cast_ids == ["orin","tessa"]
    assert new.project.reuse_series_characters is False
    assert old.project.reuse_series_characters is True


def test_real_gameplay_cannot_attach_to_animation_series(tmp_path):
    bible=minecraft_original_starter("v207_channel_gate","Lantern Vale Stories")
    ChannelLibrary(tmp_path).register_draft(bible)
    project=StudioProjectSpec(
        prompt="Minecraft realtime livestream of true players",
        niche="minecraft",minecraft_subniche="minecraft_live_gameplay",
        channel_brand_id=bible.channel_brand_id,
        series_id="lantern_trails",episode_id="lt_bridge",
    )
    with pytest.raises(ValueError,match="SERIES_SUBNICHE_CANNOT_CHANGE"):
        CompanyOrchestrator(build_studio_kernel(tmp_path)).build_blueprint(
            project,professional_governance=True
        )


def test_cli_routes_livestream_without_faking_story_pipeline(tmp_path,monkeypatch):
    import cinefactory.cli as cli
    from types import SimpleNamespace
    kernel=build_studio_kernel(tmp_path)
    monkeypatch.setattr(cli,"context",lambda: SimpleNamespace(
        studio=kernel,root=tmp_path
    ))
    result=CliRunner().invoke(app,[
        "company-plan","--project-id","real_live_capture_test",
        "--prompt","Minecraft livestream người chơi realtime thật",
        "--niche","minecraft","--duration","900",
    ])
    assert result.exit_code==0,result.output[-1000:]
    import json
    bp=json.loads(result.output)
    assert bp["minecraft_route"]["production_lane"]=="LIVE_RUNTIME"
    assert bp["studio_plan"]["product"]["format"]=="GAMEPLAY"
    assert bp["studio_plan"]["product"]["constraints"]["real_game_runtime_mandatory"] is True
    assert bp["stages"][0]["stage_id"]=="MC_MODE_INTAKE"
    assert bp["executable"] is False


def test_non_minecraft_cannot_claim_minecraft_specific_subniche():
    with pytest.raises(ValueError,match="MINECRAFT_SUBNICHE_REQUIRES"):
        StudioProjectSpec(prompt="Roblox recorded game",niche="roblox_animation",
                          minecraft_subniche="minecraft_live_gameplay")


def test_brand_new_episode_cast_requires_independent_rights_and_separate_rig(tmp_path,monkeypatch):
    import base64
    import json
    from pathlib import Path
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives import serialization
    import yaml
    from cinefactory.studio.channel_franchise_v206 import verify_fresh_episode_cast_readiness
    project_id="fresh_original_video_001"
    brand_id="some_channel_brand"
    missing=verify_fresh_episode_cast_readiness(tmp_path,project_id,brand_id)
    assert missing["ready"] is False
    assert "FRESH_EPISODE_CAST_MANIFEST_REQUIRED" in missing["blockers"]
    real_root=Path(__file__).resolve().parents[1]
    registry=yaml.safe_load((real_root/"config"/"block_animation"/"characters.yaml").read_text(encoding="utf8"))
    for row in registry["characters"]:
        if row["rig_id"]=="mc_a":
            row.setdefault("identity",{})["original_character_id"]="new_episode_lead"
    config=tmp_path/"config"/"block_animation"
    config.mkdir(parents=True)
    (config/"characters.yaml").write_text(yaml.safe_dump(registry),encoding="utf8")
    actors=[{"character_id":"new_episode_lead","rig_id":"mc_a"}]
    body={
        "schema":"cine.original_episode_cast.v207",
        "project_id":project_id,"channel_brand_id":brand_id,
        "actors":actors,
    }
    private=Ed25519PrivateKey.generate()
    pub_path=tmp_path/"rights_public.pem"
    pub_path.write_bytes(private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo))
    payload=json.dumps(body,sort_keys=True,separators=(",",":"),
                       ensure_ascii=False).encode("utf8")
    body["independent_rights_review"]={
        "schema":"cine.fresh_episode_rights_review.v207",
        "decision":"CLEARED_ORIGINAL_EPISODE_CHARACTERS",
        "signature_b64":base64.b64encode(private.sign(payload)).decode(),
    }
    inputs=tmp_path/"data"/"projects"/project_id/"inputs"
    inputs.mkdir(parents=True)
    manifest=inputs/"original_episode_cast.json"
    manifest.write_text(json.dumps(body),encoding="utf8")
    not_trusted=verify_fresh_episode_cast_readiness(tmp_path,project_id,brand_id)
    assert not not_trusted["ready"]
    monkeypatch.setenv("CINEFACTORY_RIGHTS_TRUST_PUBKEY",str(pub_path))
    accepted=verify_fresh_episode_cast_readiness(tmp_path,project_id,brand_id)
    assert accepted["ready"] is True
    body["actors"][0]["character_id"]="stolen_actor_identity"
    manifest.write_text(json.dumps(body),encoding="utf8")
    tampered=verify_fresh_episode_cast_readiness(tmp_path,project_id,brand_id)
    assert not tampered["ready"]


def test_capture_lane_registered_handlers_fail_closed_before_unauthorized_game_recording(tmp_path):
    from cinefactory.studio.company_runner import StageExecutionContext
    kernel=build_studio_kernel(tmp_path)
    project=StudioProjectSpec(
        prompt="Minecraft realtime livestream người chơi thật",
        niche="minecraft",minecraft_subniche="minecraft_live_gameplay",
        duration_seconds=600,
    )
    bp=CompanyOrchestrator(kernel).build_blueprint(project,professional_governance=True)
    handlers=FilmCompanyHandlers(kernel).registry(production_route=bp.minecraft_route)
    intake=next(x for x in bp.stages if x.stage_id=="MC_MODE_INTAKE")
    result=handlers.get("MC_MODE_INTAKE")(StageExecutionContext(
        blueprint=bp,stage=intake,kernel=kernel,
    ))
    assert result.ok
    artifact=kernel.blackboard.get(bp.project.studio_project_id,"mc_mode_brief")["payload"]
    assert artifact["source_never_fake_live"] is True
    capture=next(x for x in bp.stages if x.stage_id=="MC_REAL_CAPTURE")
    denial=handlers.get("MC_REAL_CAPTURE")(StageExecutionContext(
        blueprint=bp,stage=capture,kernel=kernel,
    ))
    assert denial.ok is False
    assert denial.error=="MINECRAFT_REAL_GAME_QUALIFICATION_REQUIRED"

def test_new_animated_challenge_is_valid_series_but_real_gameplay_cannot_be_sneaked_in():
    from cinefactory.studio.channel_franchise_v206 import SeriesBible, ChannelBible
    b=minecraft_original_starter("minecraft_new_animated_challenge","Lantern Vale Stories")
    raw=b.model_dump()
    raw["series"][0]["subniche"]="minecraft_animated_challenge"
    assert ChannelBible.model_validate(raw).series[0].subniche=="minecraft_animated_challenge"
    raw["series"][0]["subniche"]="minecraft_live_gameplay"
    with pytest.raises(ValueError,match="UNKNOWN_MINECRAFT_SUBNICHE"):
        ChannelBible.model_validate(raw)


def test_standalone_animation_video_shares_channel_promise_but_not_old_series_cast(tmp_path):
    from cinefactory.studio.company_runner import StageExecutionContext
    b=minecraft_original_starter("standalone_original_channel","Lantern Vale Stories")
    ChannelLibrary(tmp_path).register_draft(b)
    project=StudioProjectSpec(
        prompt="Create a fresh original Minecraft animated story with new actors",
        niche="minecraft",minecraft_subniche="minecraft_story_adventure",
        channel_brand_id=b.channel_brand_id,
        duration_seconds=60,
    )
    kernel=build_studio_kernel(tmp_path)
    bp=CompanyOrchestrator(kernel).build_blueprint(project,professional_governance=True)
    strategy=bp.channel_episode_strategy
    assert strategy.series_id=="standalone_film"
    assert strategy.episode_id==project.studio_project_id
    assert strategy.cast_ids==[]
    assert strategy.world_rules==[]
    assert strategy.brand_promise==b.audience_promise
    assert bp.project.reuse_series_characters is False
    assert audit_company_wiring(bp.stages).valid
    handler=FilmCompanyHandlers(kernel)
    stage=next(s for s in bp.stages if s.stage_id=="CHANNEL_IDENTITY")
    receipt=handler.channel_identity(StageExecutionContext(
        blueprint=bp,stage=stage,kernel=kernel))
    assert receipt.ok
    identity=kernel.blackboard.get(project.studio_project_id,"channel_identity")["payload"]
    assert identity["characters"]=={}
    assert identity["new_episode_cast_required"] is True
    assert identity["release_permission"] is False


def test_standalone_cannot_request_reuse_without_explicit_series_context():
    with pytest.raises(ValueError,match="EXPLICIT_SERIES_CONTEXT_REQUIRED"):
        StudioProjectSpec(prompt="Original Minecraft animation",niche="minecraft",
                          channel_brand_id="a_channel",reuse_series_characters=True)
