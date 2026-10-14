"""v206 regression: Minecraft is one niche with persistent multi-series identity."""
import json
from pathlib import Path
import pytest
from typer.testing import CliRunner

from cinefactory.studio.channel_franchise_v206 import (
    ChannelBible, ChannelLibrary, OriginalCharacter, minecraft_original_starter,
    draft_editorial_slate, evaluate_evergreen_slate,
)
from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.company_handlers import FilmCompanyHandlers
from cinefactory.studio.company_runner import StageExecutionContext
from cinefactory.studio.contracts import StudioProjectSpec, DepartmentId, ArtifactState
from cinefactory.studio.contract_integrity import audit_company_wiring
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.cli import app


def make_project(tmp_path):
    b = minecraft_original_starter("lantern_channel_test","Lantern Vale Stories")
    lib = ChannelLibrary(tmp_path)
    lib.register_draft(b)
    project = StudioProjectSpec(
        prompt="Build an original Minecraft 3D cinematic adventure episode",
        niche="minecraft",
        channel_brand_id=b.channel_brand_id,
        series_id="lantern_trails", episode_id="lt_bridge",
        reuse_series_characters=True,
        duration_seconds=60,
    )
    kernel = build_studio_kernel(tmp_path)
    bp = CompanyOrchestrator(kernel).build_blueprint(
        project,professional_governance=True,
    )
    return b,lib,project,kernel,bp


def test_maizen_bigschool_jj_are_benchmarks_not_separate_niches(tmp_path):
    b,lib,project,kernel,bp=make_project(tmp_path)
    assert b.niche=="minecraft"
    assert len(b.series)==3
    subniches={s.subniche for s in b.series}
    assert {"minecraft_story_adventure","minecraft_school_comedy",
            "minecraft_challenge_survival"} <= subniches
    assert len({c.character_id for c in b.character_registry})==3
    assert len(b.references_for_structural_study)==3
    assert all(not x.startswith("Maizen") for x in [
        c.display_name for c in b.character_registry])
    assert b.verified_youtube_channel_id is None
    assert b.channel_status=="DRAFT_REQUIRES_OWNER_REVIEW"


def test_channels_cannot_clone_reference_brand_or_characters():
    x=minecraft_original_starter("channel_brand_test","Lantern Vale Stories")
    tampered = x.model_copy(update={"proposed_brand_name":"Maizen Official"})
    with pytest.raises(ValueError,match="REFERENCE_CHANNEL_BRAND_CLONE"):
        ChannelBible.model_validate(tampered.model_dump())
    with pytest.raises(ValueError,match="REFERENCE_CHANNEL_BRAND_CLONE"):
        ChannelLibrary(Path.cwd()).register_draft(tampered)
    with pytest.raises(ValueError,match="REFERENCE_CHARACTER_IDENTITY"):
        OriginalCharacter(
            character_id="fake_jj",display_name="JJ",
            design_identity="A definitely copied recognizable branded character",
            inner_conflict="Wanted to mirror the benchmark's distinct expressions",
            consistent_motivations=["act in stories","talk to companions"],
        )


def test_editorial_slate_rotates_series_without_committing_publication(tmp_path):
    b,*_=make_project(tmp_path)
    slate=draft_editorial_slate(b,weeks=12)
    assert slate["weeks_with_candidate"]==9
    assert slate["inventory_gap_weeks"]==3
    assert slate["calendar_has_approved_episodes"] is False
    ids=[row["episode_id"] for row in slate["slate"]]
    assert len(ids)==len(set(ids))
    assert len({row["series_id"] for row in slate["slate"]})==3
    assert not any(row["publish_committed"] for row in slate["slate"])
    assert all(row["editorial_status"]=="DRAFT_NEEDS_SCRIPT_AND_FILM_QC"
               for row in slate["slate"])
    assert evaluate_evergreen_slate(b)["business_traction_verified"] is False


def test_channel_library_is_append_only_and_detects_source_drift(tmp_path):
    b,lib,project,kernel,bp=make_project(tmp_path)
    with pytest.raises(FileExistsError):
        lib.register_draft(b)
    assert bp.channel_episode_strategy
    path=lib.path_for(b.channel_brand_id)
    updated=b.model_copy(update={"audience_promise":"Changed outside validated project run"})
    path.write_text(updated.model_dump_json(indent=2),encoding="utf8")
    assert lib.load(b.channel_brand_id)[1]!=bp.channel_episode_strategy.source_sha256
    handler=FilmCompanyHandlers(kernel)
    stage=next(x for x in bp.stages if x.stage_id=="CHANNEL_IDENTITY")
    result=handler.channel_identity(StageExecutionContext(
        blueprint=bp,stage=stage,kernel=kernel,
    ))
    assert not result.ok
    assert result.error=="CHANNEL_BIBLE_CHANGED_AFTER_BLUEPRINT"


def test_all_channel_episodes_have_originality_and_season_continuity(tmp_path):
    b,*_=make_project(tmp_path)
    episodes=[ep for series in b.series for ep in series.episodes]
    assert len(episodes)==9
    assert all(ep.continuity_changes and ep.payoff and ep.original_premise
               for ep in episodes)
    assert len({ep.original_premise for ep in episodes})==9


def test_channel_blueprint_has_real_department_handoffs(tmp_path):
    b,lib,project,kernel,bp=make_project(tmp_path)
    ids=[stage.stage_id for stage in bp.stages]
    assert "CHANNEL_IDENTITY" in ids and "SERIES_EDITORIAL" in ids
    assert ids.index("CHANNEL_IDENTITY") < ids.index("CREATIVE_STRATEGY")
    assert ids.index("SERIES_EDITORIAL") < ids.index("WRITING")
    assert audit_company_wiring(bp.stages).valid
    assert bp.channel_episode_strategy.channel_brand_id==b.channel_brand_id
    assert bp.project_dna.brand.promise==b.audience_promise
    for stage in ("CREATIVE_STRATEGY","WRITING","PRODUCTION","FINAL_QC","PACKAGING"):
        obj=next(s for s in bp.stages if s.stage_id==stage)
        assert "series_editorial_plan" in obj.artifacts_in or stage=="CREATIVE_STRATEGY"
    assert not bp.portfolio_greenlight.approved_for_production


def test_channel_identity_handler_persists_real_source_context(tmp_path):
    b,lib,project,kernel,bp=make_project(tmp_path)
    handler=FilmCompanyHandlers(kernel)
    stage=next(s for s in bp.stages if s.stage_id=="CHANNEL_IDENTITY")
    got=handler.channel_identity(StageExecutionContext(
        blueprint=bp,stage=stage,kernel=kernel,
    ))
    assert got.ok
    stored=kernel.blackboard.get(project.studio_project_id,"channel_identity")["payload"]
    assert stored["source_sha256"]==bp.channel_episode_strategy.source_sha256
    assert set(stored["characters"])==set(bp.channel_episode_strategy.cast_ids)
    assert stored["release_permission"] is False
    assert "Maizen" not in [v["display_name"] for v in stored["characters"].values()]


def test_series_editorial_handler_uses_channel_handoff_without_fake_art_qc(tmp_path):
    b,lib,project,kernel,bp=make_project(tmp_path)
    handler=FilmCompanyHandlers(kernel)
    ch=next(s for s in bp.stages if s.stage_id=="CHANNEL_IDENTITY")
    assert handler.channel_identity(StageExecutionContext(
        blueprint=bp,stage=ch,kernel=kernel,
    )).ok
    kernel.blackboard.put(
        project.studio_project_id,"creative_brief",DepartmentId.CREATIVE_STRATEGY,
        {"original_story_direction":"prototype, not reviewed"},
        state=ArtifactState.VALIDATED,
    )
    editorial=next(s for s in bp.stages if s.stage_id=="SERIES_EDITORIAL")
    got=handler.series_editorial(StageExecutionContext(
        blueprint=bp,stage=editorial,kernel=kernel,
    ))
    assert got.ok
    persisted=kernel.blackboard.get(project.studio_project_id,"series_editorial_plan")["payload"]
    assert persisted["automatically_greenlit"] is False
    assert persisted["independent_script_review"]=="REQUIRED_BEFORE_COMMERCIAL_RELEASE"
    assert persisted["channel_bible_sha256"]==bp.channel_episode_strategy.source_sha256


def test_channel_ref_must_bind_three_levels_and_match_minecraft(tmp_path):
    # Channel-only independent videos are allowed; series references must
    # contain both series and episode IDs.
    standalone=StudioProjectSpec(prompt="Original animation",channel_brand_id="my_channel")
    assert standalone.series_id is None
    with pytest.raises(ValueError,match="CHANNEL_SERIES_EPISODE"):
        StudioProjectSpec(prompt="Original animation",channel_brand_id="my_channel",
                          series_id="some_series")
    b,lib,project,kernel,bp=make_project(tmp_path)
    changed=project.model_copy(update={"niche":"roblox_animation"})
    with pytest.raises(ValueError,match="PROFESSIONAL_MINECRAFT_NICHE"):
        CompanyOrchestrator(kernel).build_blueprint(changed,professional_governance=True)


def test_channel_cli_operates_on_isolated_draft_root(tmp_path,monkeypatch):
    import cinefactory.cli as cli
    monkeypatch.setattr(cli,"ROOT",tmp_path)
    runner=CliRunner()
    created=runner.invoke(app,[
        "channel-init","--brand-id","safe_original_draft",
        "--working-name","Original Forest Studio",
    ])
    assert created.exit_code==0,created.output[-1000:]
    obj=json.loads(created.output)
    assert obj["created_youtube_channel"] is False
    assert obj["episodes"]==9
    assert (tmp_path/"data"/"channels"/"safe_original_draft"/"channel_bible.json").is_file()
    repeated=runner.invoke(app,["channel-init","--brand-id","safe_original_draft"])
    assert repeated.exit_code!=0
    slate=runner.invoke(app,["channel-slate","--brand-id","safe_original_draft"])
    assert slate.exit_code==0,slate.output[-1200:]
    assert json.loads(slate.output)["weeks_with_candidate"]==9
    episode=runner.invoke(app,[
        "channel-episode","--brand-id","safe_original_draft",
        "--series-id","lantern_trails","--episode-id","lt_bridge",
    ])
    assert episode.exit_code==0,episode.output[-1200:]
    assert json.loads(episode.output)["video_release_permission"] is False


def test_channel_owned_analytics_remains_unpromoted_and_immutable(tmp_path):
    from cinefactory.studio.channel_growth_v206 import (
        ChannelOwnedGrowthLedger, learning_hypothesis,
    )
    from cinefactory.studio.youtube_oauth_transport_v205 import (
        GoogleYouTubeOwnedAnalyticsTransport,
    )
    b, lib, project, kernel, bp = make_project(tmp_path)
    youtube_id = "UC" + "n"*22
    updated = b.model_copy(update={"verified_youtube_channel_id": youtube_id})
    lib.path_for(b.channel_brand_id).write_text(
        ChannelBible.model_validate(updated.model_dump()).model_dump_json(indent=2),
        encoding="utf8",
    )
    video_id = "videoABC123"
    receipt = {
        "schema": "cine.youtube.private_upload_verified.v205",
        "state": "UPLOADED_PRIVATE_VERIFIED",
        "channel_id": youtube_id,
        "privacy_status": "private",
        "video_id": video_id,
        "master_sha256": "f"*64,
        "source": "LIVE_AUTHORIZED_YOUTUBE_API_READBACK",
    }

    # Fake transport is a TEST-ONLY substitute; it proves call plumbing,
    # not that any real YouTube metrics have been fetched.
    transport = object.__new__(GoogleYouTubeOwnedAnalyticsTransport)
    transport.owned_channel_id = youtube_id
    transport.fetch_owned_video_metrics = lambda owned, video: {
        "metrics": {
            "video_id": video, "window_start": "2026-10-01",
            "window_end": "2026-10-08", "views": 244,
            "watch_minutes": 1120,
        },
        "provenance": {
            "provider": "YOUTUBE_ANALYTICS_API",
            "authenticated_provider_readback": True,
            "channel_id": owned, "video_id": video,
        },
    }
    ledger = ChannelOwnedGrowthLedger(tmp_path)
    result = ledger.record_verified_episode(
        brand_id=b.channel_brand_id, series_id="lantern_trails",
        episode_id="lt_bridge", release_receipt=receipt, transport=transport,
    )
    assert result["status"] == "OWNED_OBSERVATION_RECORDED_UNPROMOTED"
    record = json.loads(Path(result["path"]).read_text(encoding="utf8"))
    assert record["decision"] == "OBSERVED_NOT_PROMOTED"
    assert record["learning_candidate"]["causal_claim_verified"] is False
    assert record["learning_candidate"]["rules_automatically_updated"] is False
    assert record["learning_candidate"]["actual_owned_metrics"]["views"] == 244
    with pytest.raises(FileExistsError):
        ledger.record_verified_episode(
            brand_id=b.channel_brand_id, series_id="lantern_trails",
            episode_id="lt_bridge", release_receipt=receipt, transport=transport,
        )
    with pytest.raises(ValueError, match="OWNED_ANALYTICS"):
        learning_hypothesis(
            lib.resolve_episode(b.channel_brand_id,"lantern_trails","lt_bridge"),
            {"schema": "untrusted_public_channel_metrics"},
        )


def test_channel_growth_rejects_unverified_channel_and_forged_public_metrics(tmp_path):
    from cinefactory.studio.channel_growth_v206 import ChannelOwnedGrowthLedger
    from cinefactory.studio.youtube_oauth_transport_v205 import (
        GoogleYouTubeOwnedAnalyticsTransport,
    )
    b,lib,_,_,_ = make_project(tmp_path)
    transport = object.__new__(GoogleYouTubeOwnedAnalyticsTransport)
    transport.owned_channel_id = "UC" + "x"*22
    receipt = {
        "schema": "cine.youtube.private_upload_verified.v205",
        "source": "LIVE_AUTHORIZED_YOUTUBE_API_READBACK",
        "state": "UPLOADED_PRIVATE_VERIFIED",
        "channel_id": transport.owned_channel_id,
        "video_id": "videoABC123",
        "privacy_status": "private",
    }
    with pytest.raises(PermissionError,match="CHANNEL_YOUTUBE_OWNERSHIP_NOT_BOUND"):
        ChannelOwnedGrowthLedger(tmp_path).record_verified_episode(
            brand_id=b.channel_brand_id,series_id="lantern_trails",
            episode_id="lt_bridge",release_receipt=receipt,transport=transport,
        )


def test_channel_editorial_mix_rejects_trend_chasing(tmp_path):
    b,lib,_,_,_ = make_project(tmp_path)
    obj=b.model_dump()
    obj["series"][0]["episodes"][0]["editorial_pillar"]="TREND"
    obj["series"][0]["episodes"][1]["editorial_pillar"]="TREND"
    obj["series"][0]["episodes"][2]["editorial_pillar"]="TREND"
    with pytest.raises(ValueError,match="TREND_CHASING|EVERGREEN_PORTFOLIO_SHARE"):
        ChannelBible.model_validate(obj)
    assert len(b.series[0].episodes)==3
    assert evaluate_evergreen_slate(b)["evergreen_share"]==1.0


def test_real_company_plan_cli_reaches_channel_and_series_dag(tmp_path, monkeypatch):
    from types import SimpleNamespace
    import cinefactory.cli as cli
    b=minecraft_original_starter("studio_original_channel","Lantern Vale Stories")
    ChannelLibrary(tmp_path).register_draft(b)
    kernel=build_studio_kernel(tmp_path)
    monkeypatch.setattr(cli,"context",lambda: SimpleNamespace(studio=kernel,root=tmp_path))
    result=CliRunner().invoke(app,[
        "company-plan",
        "--prompt","Original animated Minecraft adventure with persistent world",
        "--niche","minecraft",
        "--project-id","series_original_001",
        "--channel-brand-id","studio_original_channel",
        "--series-id","lantern_trails",
        "--episode-id","lt_bridge",
        "--duration","60",
    ])
    assert result.exit_code==0,result.output[-1400:]
    payload=json.loads(result.output)
    assert payload["project"]["studio_project_id"]=="series_original_001"
    assert payload["channel_episode_strategy"]["episode_id"]=="lt_bridge"
    assert payload["channel_episode_strategy"]["video_release_permission"] is False
    ids={x["stage_id"] for x in payload["stages"]}
    assert {"CHANNEL_IDENTITY","SERIES_EDITORIAL","WRITING","PRODUCTION"} <= ids
    assert payload["portfolio_greenlight"]["approved_for_production"] is False


def test_channel_actor_rigs_are_required_before_expensive_rendering(tmp_path):
    from cinefactory.studio.channel_franchise_v206 import (
        verify_original_cast_rig_readiness,
    )
    b,lib,project,kernel,bp=make_project(tmp_path)
    readiness=verify_original_cast_rig_readiness(
        tmp_path,bp.channel_episode_strategy,
    )
    assert readiness["ready"] is False
    assert any("ORIGINAL_CHARACTER_RIG_UNASSIGNED" in item
               for item in readiness["blockers"])
    assert readiness["independent_rights_and_art_approval_still_required"]


def test_original_character_ids_must_be_bound_to_distinct_registered_rigs(tmp_path):
    from cinefactory.studio.channel_franchise_v206 import (
        verify_original_cast_rig_readiness,
    )
    from pathlib import Path
    import yaml
    b,lib,project,kernel,bp=make_project(tmp_path)
    for char in b.character_registry:
        if char.character_id=="orin":
            char.visual_asset_id="mc_a"
            char.character_rights_status="RIGHTS_REVIEWED"
        elif char.character_id=="tessa":
            char.visual_asset_id="mc_b"
            char.character_rights_status="RIGHTS_REVIEWED"
    lib.path_for(b.channel_brand_id).write_text(b.model_dump_json(indent=2),encoding="utf8")
    strategy=lib.resolve_episode("lantern_channel_test","lantern_trails","lt_bridge")
    config_root=tmp_path/"config"/"block_animation"
    config_root.mkdir(parents=True)
    current_root=Path(__file__).resolve().parents[1]
    catalog=yaml.safe_load(
        (current_root/"config"/"block_animation"/"characters.yaml").read_text(encoding="utf8")
    )
    # First, original identity is UNBOUND even if a generic registered Minecraft rig exists.
    (config_root/"characters.yaml").write_text(
        yaml.safe_dump(catalog),encoding="utf8",
    )
    blocked=verify_original_cast_rig_readiness(tmp_path,strategy)
    assert blocked["ready"] is False
    assert any("ORIGINAL_CHARACTER_IDENTITY_NOT_BOUND_TO_RIG"
               in x for x in blocked["blockers"])
    for rig in catalog["characters"]:
        if rig["rig_id"]=="mc_a":
            rig.setdefault("identity",{})["original_character_id"]="orin"
        if rig["rig_id"]=="mc_b":
            rig.setdefault("identity",{})["original_character_id"]="tessa"
    (config_root/"characters.yaml").write_text(
        yaml.safe_dump(catalog),encoding="utf8",
    )
    result=verify_original_cast_rig_readiness(tmp_path,strategy)
    assert result["ready"] is True
    assert result["technical_check_only"] is True
    assert result["independent_rights_and_art_approval_still_required"] is True
