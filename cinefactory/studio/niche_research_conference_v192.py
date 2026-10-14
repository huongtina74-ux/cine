from __future__ import annotations
"""v1.6.32 professional media R&D conference.

Machine-readable departmental SOPs, source-backed methods and falsifiable
experiments. It does NOT access the web, install tools, run paid APIs, approve
copyright, produce creative media or claim that a research hypothesis passed.
The capability lab/executors remain separately authorized.
"""
from datetime import date
from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, Field, model_validator

from .production_selection_council import Stage
from .production_tool_catalog_v191 import (
    NICHE_BLUEPRINTS, ProductionPortfolioAdvisor, NicheBlueprint
)
from .research_brief_parser_v192 import (
    ProductionResearchInput,ResearchInputAnalysis,analyze_research_input,
)


class ResearchMaturity(StrEnum):
    GUIDANCE = "GUIDANCE"
    HYPOTHESIS = "HYPOTHESIS"
    BENCHMARK_PENDING = "BENCHMARK_PENDING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class SourceEvidence(BaseModel):
    source_id: str
    url: str
    publisher: str
    claim_scope: str
    captured_on: date
    verified_for_scope: bool = False
    # Citation of a reference doesn't mean a workflow or licence is qualified.
    license_review_complete: bool = False

    @model_validator(mode="after")
    def source_must_be_http(self):
        if not self.url.startswith(("https://","http://")):
            raise ValueError("SOURCE_URL_MUST_BE_HTTP")
        return self


OFFICIAL_SOURCE_SNAPSHOT: dict[str,SourceEvidence] = {
    r.source_id:r for r in [
        SourceEvidence(source_id="BLENDER_RIG",publisher="Blender Foundation",
            url="https://docs.blender.org/manual/en/4.5/animation/shape_keys/introduction.html",
            claim_scope="organic facial deformation with shape keys",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="BLENDER_PASSES",publisher="Blender Foundation",
            url="https://docs.blender.org/manual/en/4.5/render/layers/passes.html",
            claim_scope="depth and object Cryptomatte render masks",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="OPENTOONZ_WORKFLOW",publisher="OpenToonz Documentation",
            url="https://opentoonz.readthedocs.io/en/latest/production_workflow.html",
            claim_scope="2D planning, storyboards, animatic, Xsheet and reusable assets",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="GODOT_LICENSE",publisher="Godot Engine",
            url="https://godotengine.org/license/",
            claim_scope="MIT engine licensing, source media rights separately",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="FFMPEG_METRICS",publisher="FFmpeg Project",
            url="https://www.ffmpeg.org/ffmpeg-filters.html",
            claim_scope="SSIM and PSNR full-reference codec metrics",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="FFMPEG_ENCODER",publisher="FFmpeg Project",
            url="https://www.ffmpeg.org/ffmpeg-all.html",
            claim_scope="libx264 CRF and encoder preset controls",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="YOUTUBE_KIDS",publisher="Google/YouTube",
            url="https://support.google.com/youtube/answer/10774223",
            claim_scope="kids/family content quality and learning safety",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="YOUTUBE_ORIGINALITY",publisher="Google/YouTube",
            url="https://support.google.com/youtube/answer/1311392",
            claim_scope="original and non-mass-produced reused content",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="REMOTION_LICENSE",publisher="Remotion",
            url="https://www.remotion.dev/docs/license/pricing",
            claim_scope="company-size and usage licensing eligibility",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="COMFYUI_REPO",publisher="Comfy Org",
            url="https://github.com/Comfy-Org/ComfyUI",
            claim_scope="local graph workflow software, not video quality model licence",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="LTX2B_REPO",publisher="Lightricks",
            url="https://github.com/Lightricks/LTX-Video",
            claim_scope="distilled 2B video generation candidate; license checkpoint independently",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="WAN22_OFFICIAL",publisher="Wan Video",
            url="https://github.com/Wan-Video/Wan2.2",
            claim_scope="TI2V-5B official reference inference requires at least 24GB GPU, not native 12GB",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="MUSESCORE_REPO",publisher="MuseScore",
            url="https://github.com/musescore/MuseScore",
            claim_scope="music scoring and MIDI/musicXML with GPLv3 software license, not automatic composition",captured_on=date(2026,10,9)),
        SourceEvidence(source_id="PIPER_OLD_REPO",publisher="Rhasspy",
            url="https://github.com/rhasspy/piper",
            claim_scope="historical local MIT TTS repository archived in 2025; voice models separate rights",captured_on=date(2026,10,9)),
    ]
}


class DepartmentProcedure(BaseModel):
    department_id: str
    responsibility: str
    inputs: list[str] = Field(min_length=1)
    research_questions: list[str] = Field(min_length=1)
    deliverables: list[str] = Field(min_length=1)
    candidate_tool_families: list[str] = Field(default_factory=list)
    objective_qc: list[str] = Field(min_length=1)
    human_qc: list[str] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    last_verified_quality: bool = False


def proc(id,responsibility,inputs,questions,deliverables,tools,qc,sources=(),human=()):
    return DepartmentProcedure(
        department_id=id,responsibility=responsibility,
        inputs=list(inputs),research_questions=list(questions),
        deliverables=list(deliverables),candidate_tool_families=list(tools),
        objective_qc=list(qc),human_qc=list(human),source_ids=list(sources))


DEPARTMENT_PLAYBOOK: dict[str,DepartmentProcedure] = {
    d.department_id:d for d in [
        proc("executive","Choose safe genre/format portfolio",["target niche","cost cap"],["Does this format create original audience value?"],["investment thesis","no-spend R&D budget"],["production economics"],["budget cap respected"],human=["human project approval"]),
        proc("audience_research","Evidence-backed format analysis",["reference URLs","locale"],["What attracts views in mature and new channels?","What isn't reproducible legally?"],["format DNA","research source ledger"],["YouTube","research tools"],["age of sources","noncopied references"],["YOUTUBE_ORIGINALITY"]),
        proc("creative_direction","Author an original episode aesthetic",["content DNA","brand bible"],["What original hook and emotional arc?"],["creative brief","style bible"],["storyboard editor","Blender"],["originality boundary"],human=["human creative review"]),
        proc("script","Develop dialogue, episodes and original narratives",["brief","audience"],["What is story causality and dialogue purpose?"],["versioned script","shot beats"],["local LLM","script editor"],["narrative continuity","word count"],human=["script quality editorial"]),
        proc("curriculum_child_safety","Age-specific learning and child safety",["audience age band","learning objective"],["Is it truly instructive and safe, not deceptively educational?"],["learning review","safe-action checklist"],["curriculum reviewer"],["incorrect lessons absent","unsafe imitation blocked"],["YOUTUBE_KIDS"],human=["child development/editorial review"]),
        proc("songwriting_music","Create an original song and mix-ready structure",["song theme","age band","lyrics"],["Are melody, rhythm, stems and master owned?","Does vocal phrase align to choreography?"],["original composition","tempo map","licensed music stems"],["DAW/MIDI","original performer"],["tempo grid","rights ledger"],["MUSESCORE_REPO"],human=["music director review"]),
        proc("voice_cast","Record authorized speech and singing",["script","consented performer"],["Naturalness and clarity?","Does sung delivery match score?"],["isolated vocal WAV","speaker identity log"],["SAPI for tests","authorized voice talent"],["audio intelligibility","consent recorded"],["PIPER_OLD_REPO"],human=["voice performance review"]),
        proc("concept_character_ip","Original character art and design",["creative brief","IP boundary"],["Are designs distinct?","Which character variants and assets are reusable?"],["character sheet","original asset registry"],["Blender","Krita","licensed meshes"],["character variation","source rights"],human=["art and IP review"]),
        proc("rigging","Controllable characters and expressions",["character meshes","actor IDs"],["Do required visemes and deformations exist?","Are organic and voxel rigs different needs?"],["versioned rig","pose/face test clip"],["Blender rigging","shape keys"],["joint stress test","skin deform","identity continuity"],["BLENDER_RIG"],human=["facial/art performance"]),
        proc("storyboard","Camera and scene timing plan",["script","music timecode"],["Does every shot communicate the story beat?"],["animatic","camera coverage plan"],["2D boards","Blender"],["storyboard completeness","timing"],["OPENTOONZ_WORKFLOW"],human=["director review"]),
        proc("animation","Body/face acting and motion design",["rig","animatic","audio timing"],["Will reusable clips lower cost without repetition?","What is physical plausibility?"],["animation clips","renderable shot scenes"],["Blender","Godot","game engines"],["joint limit","actor continuity","tempo tracking"],["BLENDER_RIG"],human=["acting/pacing and life likeness"]),
        proc("game_simulation","Run genuine deterministic game or physical simulation",["approved runtime","course specification"],["Does outcome follow physics and make engaging footage?"],["seeded simulation","capture footage"],["Godot","runtime capture","Blender physics"],["replay seed","collision QC","game rights"],["GODOT_LICENSE"]),
        proc("camera_lighting","Produce controlled exposure and cinema language",["shot plan","target style"],["Can shadows/occlusion be measured with passes?"],["shot camera metadata","lighting templates"],["Blender EEVEE/Cycles","real cinematography"],["exposure","focus","frame continuity"],["BLENDER_PASSES"],human=["cinematography review"]),
        proc("ai_generatives","Test video/image AI when reliable and licensed",["shot prompt","source image rights"],["Is character consistency measurable?","Does 12GB VRAM fit?","What is real re-generation cost?"],["workflow manifest","candidate media","model card"],["ComfyUI","approved local models"],["artifact integrity","identity","license","performance"],["COMFYUI_REPO","LTX2B_REPO","WAN22_OFFICIAL"],human=["AI artefact review"]),
        proc("capture_foley","Capture believable authentic footage and sound",["location consent","recording plan"],["Does this content require actual human camera and microphone?"],["recordings","consent and location rights"],["camera","microphones","OBS candidate"],["clipping","dropouts","background noise"],human=["authenticity"]),
        proc("audio_post","Master narration, ambience, music and sfx",["WAV stems","mix notes"],["Is final loudness comfortable?","Are loops seamless?"],["stems","master WAV"],["FFmpeg","DAW"],["true peak","audibility","clipping","loop seam"],["FFMPEG_METRICS"],human=["listening QC"]),
        proc("editorial_2d","Edit story, motion graphics, conform video",["approved clips","time-base","captions"],["Which editor yields same quality faster?","Are transitions readable?"],["locked timeline","master MP4","subtitles"],["FFmpeg","Remotion (license review)","OpenToonz"],["frame count","SSIM/PSNR","audio sync","titles readability"],["FFMPEG_METRICS","FFMPEG_ENCODER","OPENTOONZ_WORKFLOW","REMOTION_LICENSE"],human=["editorial rhythm"]),
        proc("localization","Voice, captions and translations",["language pack","master timeline"],["Are translations faithful, culturally appropriate and synced?"],["language WAV/subtitles","localization QC"],["TTS","subtitle tools","translator"],["subtitle sync","proper names"],human=["language expert"]),
        proc("qa_compliance","Cross-domain quality and legal gates",["master media","scene metadata","rights ledger"],["Does media meet the specific niche acceptance rubric?"],["QC evidence","defect tickets","human-signoff checklist"],["FFprobe","CV","reviewer"],["render defects","rights","continuity","audio","child policies"],["YOUTUBE_ORIGINALITY","YOUTUBE_KIDS"],human=["human visual and legal review"]),
        proc("compute_finance","Measure accepted-minute costs and schedule jobs",["GPU data","wall time","retry count"],["What is *accepted* minute throughput?","Can CPU tasks overlap safely?"],["cost ledger","VRAM timings","queue policy"],["OS telemetry","FFmpeg benchmark"],["peak VRAM","elapsed per accepted minute","gpu occupancy"],human=["budget approval"]),
        proc("distribution_analytics","Package original output and learn from results",["approved master","niche audience"],["Does title and first minute accurately represent content?"],["metadata","publish request","retention test plan"],["YouTube publishing authorization","analytics"],["consent","originality","release approval"],["YOUTUBE_ORIGINALITY"],human=["publish authorization"]),
        proc("rnd_security","Experiment, compare tools and control software risks",["verified source URLs","capability gaps"],["Does new tool beat benchmark?","Is model licence commercially fit?","Can adapter be isolated?"],["reproducible benchmark","SBOM","versioned rules"],["GitHub repos","security lab","model cards"],["sample hashes","no unapproved installs","tests stable"],human=["supply chain and license review"]),
    ]
}


class ExperimentPlan(BaseModel):
    experiment_id: str
    niche_id: str
    department_id: str
    stage: Stage
    question: str
    control_method: str | None = None
    challenger_methods: list[str] = Field(default_factory=list)
    input_equivalence: str
    output_media: str
    metrics: list[str] = Field(min_length=1)
    quality_floor: float = Field(ge=0.,le=1.)
    benchmark_status: ResearchMaturity = ResearchMaturity.BENCHMARK_PENDING
    human_signoff_required: bool = True
    license_gate: bool = True
    execution_authorized: bool = False
    must_not_train_on_holdout: bool = True
    eligible_to_promote: bool = False


class ResearchDepartmentReview(BaseModel):
    department_id: str
    relevant: bool
    research_questions: list[str]
    deliverables: list[str]
    qc: list[str]
    tool_families: list[str]
    source_ids: list[str]
    maturity: ResearchMaturity = ResearchMaturity.GUIDANCE


class NicheResearchConferenceReport(BaseModel):
    schema_version: str = "v1.6.32"
    niche_id: str
    project_id: str
    status: str = "RESEARCH_CONFERENCE_COMPLETE_PRODUCTION_BLOCKED"
    source_ledger: list[SourceEvidence]
    department_reviews: list[ResearchDepartmentReview]
    experiments: list[ExperimentPlan]
    stage_decisions: list[dict]
    blocked_stages: list[str]
    blockers: list[str]
    production_qualified: bool = False
    external_research_performed_live: bool = False
    source_claims_are_verified_for_scope: bool = False
    creative_quality_human_approved: bool = False
    input_analysis: ResearchInputAnalysis | None = None


STAGE_OWNER: dict[Stage, tuple[str,...]] = {
    Stage.RESEARCH:("audience_research","creative_direction"),
    Stage.SCRIPT:("script","creative_direction","curriculum_child_safety"),
    Stage.MUSIC:("songwriting_music","audio_post","curriculum_child_safety"),
    Stage.VOICE:("voice_cast","audio_post"),
    Stage.CHARACTER_RIG:("concept_character_ip","rigging"),
    Stage.ANIMATION:("animation","camera_lighting","rigging"),
    Stage.GAME_RUNTIME:("game_simulation","camera_lighting","capture_foley"),
    Stage.AI_VIDEO:("ai_generatives","camera_lighting","concept_character_ip"),
    Stage.GRAPHICS_2D:("editorial_2d","storyboard"),
    Stage.CAPTURE:("capture_foley","camera_lighting"),
    Stage.AUDIO_POST:("audio_post","voice_cast"),
    Stage.EDITORIAL:("editorial_2d","qa_compliance","localization"),
    Stage.FINAL_QC:("qa_compliance","curriculum_child_safety"),
}


class NicheResearchConference:
    """Deterministically combines source-backed department SOPs with V191 plans.

    It compiles *falsifiable experiment plans*. Running experiments or browsing
    the web requires a separate approved tool runner, never this conference.
    """
    def __init__(self,root:str|Path):
        self.root=Path(root).resolve()
        self.portfolio=ProductionPortfolioAdvisor(self.root)

    def convene(self,niche_id:str,*,project_id:str="NICHE_RESEARCH",
                context:dict|None=None)->NicheResearchConferenceReport:
        if niche_id not in NICHE_BLUEPRINTS:
            raise ValueError("UNKNOWN_NICHE_REQUIRES_EXTERNAL_EVIDENCED_RESEARCH")
        niche: NicheBlueprint=NICHE_BLUEPRINTS[niche_id]
        report=self.portfolio.niche_report(niche_id)
        stage_decisions=report["stage_decisions"]
        active_roles={"executive","audience_research","creative_direction",
                      "qa_compliance","compute_finance","rnd_security","distribution_analytics"}
        experiments=[]
        blocked=[]
        for i,step in enumerate(stage_decisions):
            stage=Stage(step["stage"])
            roles=set(STAGE_OWNER[stage])
            if not niche.children_audience:
                roles.discard("curriculum_child_safety")
            active_roles.update(roles)
            selection=step["selection"]
            if selection["status"]!="PRODUCTION_METHOD_SELECTED":
                blocked.append(stage.value)
            selected=[x["method_id"] for x in selection["reviews"] if x["preview_candidate"]]
            specs=step["capabilities"]
            for owner in sorted(roles):
                experiments.append(ExperimentPlan(
                    experiment_id=f"{project_id}_{niche_id}_{i:02d}_{owner}",
                    niche_id=niche_id,department_id=owner,
                    stage=stage,
                    question=f"Can {owner} satisfy {', '.join(specs)} better per accepted shot?",
                    control_method=selected[0] if selected else None,
                    challenger_methods=selected[1:3],
                    input_equivalence="SAME_LOCKED_SHOT_BRIEF_SOURCE_RIGHTS_SEED_AND_FORMAT",
                    output_media="GOLDEN_15_30_SECOND_SHOT_OR_AUDIO_STEM",
                    metrics=["human_blind_quality","critical_failure_rate",
                             "accepted_minutes_per_wallclock_hour",
                             "total_cost_usd_per_accepted_minute",
                             "repeatability","rights_compliance"],
                    quality_floor=.90 if niche.children_audience else .85,
                ))
        reviews=[]
        sources=set()
        for name in sorted(active_roles):
            role=DEPARTMENT_PLAYBOOK[name]
            reviews.append(ResearchDepartmentReview(
                department_id=name,relevant=True,
                research_questions=role.research_questions,
                deliverables=role.deliverables,
                qc=role.objective_qc+role.human_qc,
                tool_families=role.candidate_tool_families,
                source_ids=role.source_ids,
            ))
            sources.update(role.source_ids)
        input_analysis=(
            analyze_research_input(ProductionResearchInput.model_validate(context))
            if context is not None else None
        )
        reasons=[
            "NO_AUTOMATIC_PRODUCTION_APPROVAL_WITHOUT_REAL_BENCHMARK_AND_LICENSE",
            "DEPARTMENT_SOP_GUIDANCE_DOES_NOT_EQUAL_LIVE_INDEPENDENT_WEB_RESEARCH",
            "QUALITY_PREFERENCE_REQUIRES_BLIND_HUMAN_MEDIA_REVIEW",
            "COST_PER_ACCEPTED_MINUTE_REQUIRES_RETRY_LABOUR_ELECTRICITY_AND_SUBSCRIPTION_LEDGER",
            "NEW_TOOL_DISCOVERY_AND_INSTALL_REQUIRES_SEPARATE_AUTHORIZED_RESEARCH_EXECUTION",
        ]
        if blocked:
            reasons.append("UNQUALIFIED_PRODUCTION_STAGES:"+",".join(sorted(set(blocked))))
        if input_analysis is not None:
            reasons.extend(input_analysis.blockers)
            # Explicit scene hypotheses feed downstream actual shot analysis,
            # but do not add unverified method scores or certify video URLs.
        if niche.children_audience:
            reasons.append("PRESCHOOL_IP_EDUCATIONAL_CHILD_SAFETY_MUSIC_RIGHTS_HUMAN_GATES")
        return NicheResearchConferenceReport(
            niche_id=niche_id,project_id=project_id,
            source_ledger=[OFFICIAL_SOURCE_SNAPSHOT[k] for k in sorted(sources)],
            department_reviews=reviews,experiments=experiments,
            stage_decisions=stage_decisions,
            blocked_stages=blocked,blockers=reasons,
            input_analysis=input_analysis,
        )
