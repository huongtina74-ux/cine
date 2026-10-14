from __future__ import annotations
"""Safe script-based R&D scoping, not video understanding or transcription.

Recognizes explicit scene boundaries from owned supplied script/brief. URLs are
references to be inspected by an authorized research agent later. Never claim
to have watched or analysed a video without obtaining actual video content.
"""
import re
from pydantic import BaseModel, Field
from .production_selection_council import Stage


class ProductionResearchInput(BaseModel):
    project_brief: str = ""
    script_text: str = ""
    reference_video_urls: list[str] = Field(default_factory=list)
    target_language: str = "en"
    intended_audience: str = "general"
    target_duration_minutes: float | None = Field(default=None,gt=0)
    source_media_rights_confirmed: bool = False
    allow_external_api_cost: bool = False


class ShotResearchHypothesis(BaseModel):
    source_segment_index: int
    text_excerpt: str
    inferred_stages: list[Stage]
    risk_tags: list[str]
    attribution: str = "USER_SUPPLIED_SCRIPT_OR_BRIEF_TEXT_ONLY"
    confidence: str = "HEURISTIC_NOT_VIDEO_EVIDENCE"
    visual_reference_content_inspected: bool = False
    ready_for_production: bool = False


class ResearchInputAnalysis(BaseModel):
    input_kind: str
    script_segments: int
    scenes: list[ShotResearchHypothesis]
    media_urls_supplied: int
    media_url_content_verified: bool = False
    blockers: list[str] = Field(default_factory=list)


TRIGGERS:tuple[tuple[Stage,tuple[str,...]],...]=(
    (Stage.MUSIC,("song","sing","lyric","chorus","bài hát","hát","nhạc","dance","nhảy")),
    (Stage.VOICE,("speak","dialogue","say","nói","thoại","voice","narrat")),
    (Stage.ANIMATION,("character","nhân vật","walking","running","dance","jump","chạy","nhảy","cử động")),
    (Stage.GAME_RUNTIME,("gameplay","slide","obstacle","physics","đường trượt","va chạm","trò chơi")),
    (Stage.CAPTURE,("footage","camera recording","real microphone","quay thực","thu âm thực","fishing","câu cá")),
    (Stage.AUDIO_POST,("asmr","sleep","rain","tiếng mưa","white noise","âm thanh","ambient")),
    (Stage.GRAPHICS_2D,("subtitles","chart","kinetic text","infographic","biểu đồ","phụ đề")),
    (Stage.AI_VIDEO,("generative visual","ai video","comfyui","text-to-video","video ai")),
)


def _parts(text:str)->list[str]:
    if not text.strip():
        return []
    # Only explicit scene markers are treated as scene boundaries.
    chunks=re.split(r"(?im)^(?:scene|cảnh|shot)\s*(?:\d+[.:\-]?|[:\-])\s*",text)
    return [c.strip()[:600] for c in chunks if c.strip()][:32]


def analyze_research_input(value:ProductionResearchInput)->ResearchInputAnalysis:
    text=value.script_text.strip() or value.project_brief.strip()
    chunks=_parts(text)
    hypotheses=[]
    for i,chunk in enumerate(chunks):
        lower=chunk.lower()
        stages=[st for st,triggers in TRIGGERS if any(x in lower for x in triggers)]
        if not stages:stages=[Stage.SCRIPT,Stage.EDITORIAL]
        # Safety metadata from script signals is advisory, NOT a content safety approval.
        risks=[]
        if any(x in lower for x in ("baby","kid","child","bé","trẻ em")):
            risks.append("CHILD_SAFETY_AND_CURRICULUM_REVIEW")
        if any(x in lower for x in ("copyright","cocomelon","disney","gta","copyrighted")):
            risks.append("REFERENCE_IP_AND_RIGHTS_REVIEW")
        if Stage.AI_VIDEO in stages:
            risks.append("GENERATIVE_MODEL_LICENSE_AND_IDENTITY_REVIEW")
        hypotheses.append(ShotResearchHypothesis(
            source_segment_index=i,text_excerpt=chunk[:320],
            inferred_stages=list(dict.fromkeys(stages)),
            risk_tags=risks,
        ))
    issues=[]
    if value.reference_video_urls:
        issues.append("REFERENCE_VIDEO_URL_CONTENT_NOT_FETCHED_OR_ANALYZED")
    if not value.source_media_rights_confirmed and value.reference_video_urls:
        issues.append("REFERENCE_MEDIA_REUSE_RIGHTS_UNCONFIRMED")
    if not chunks:
        issues.append("SCRIPT_AND_PROJECT_BRIEF_MISSING")
    return ResearchInputAnalysis(
        input_kind="USER_SUPPLIED_SCRIPT" if value.script_text.strip() else
             "USER_BRIEF" if value.project_brief.strip() else
             "UNINSPECTED_MEDIA_LINKS" if value.reference_video_urls else "EMPTY",
        script_segments=len(chunks),scenes=hypotheses,
        media_urls_supplied=len(value.reference_video_urls),blockers=issues,
    )
