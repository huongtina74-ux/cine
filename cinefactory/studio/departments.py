from __future__ import annotations

from .contracts import DepartmentId, DepartmentSpec, KnowledgeScope


def _d(
    department_id: DepartmentId,
    mission: str,
    knowledge: list[str],
    skills: list[str],
    tools: list[str],
    reads: list[str],
    writes: list[str],
    rules: list[str],
    qc: list[str],
    scope: list[KnowledgeScope] | None = None,
) -> DepartmentSpec:
    return DepartmentSpec(
        department_id=department_id,
        mission=mission,
        knowledge_domains=knowledge,
        skills=skills,
        tools=tools,
        reads=reads,
        writes=writes,
        rules=rules,
        qc_gates=qc,
        learning_scope=scope or [KnowledgeScope.PROJECT, KnowledgeScope.DOMAIN, KnowledgeScope.STUDIO],
    )


DEFAULT_DEPARTMENTS: dict[DepartmentId, DepartmentSpec] = {
    DepartmentId.INTELLIGENCE: _d(
        DepartmentId.INTELLIGENCE,
        "Understand market, audience, competitors, formats and production methods without copying expression.",
        ["market research", "audience research", "competitive intelligence", "platform discovery", "video decomposition"],
        ["source discovery", "shot segmentation", "pattern mining", "production-method classification", "gap analysis"],
        ["web research", "PySceneDetect", "WhisperX", "vision models", "analytics connectors"],
        ["project_brief", "reference_material"],
        ["research_pack", "research_confidence", "research_portfolio", "competitor_profiles", "niche_playbook"],
        ["aggregate across multiple examples", "separate observation from rule", "raw competitor expression never enters writing context"],
        ["SOURCE_PROVENANCE", "SAMPLE_SUFFICIENCY", "PATTERN_CONFIDENCE", "ORIGINALITY_BOUNDARY"],
    ),
    DepartmentId.EVIDENCE: _d(
        DepartmentId.EVIDENCE,
        "Map factual claims to trustworthy evidence and preserve uncertainty.",
        ["source evaluation", "fact checking", "claim-evidence graphs", "freshness", "contradiction handling"],
        ["claim extraction", "source tiering", "cross-checking", "citation mapping"],
        ["web research", "document readers", "structured evidence store"],
        ["research_pack", "script_draft"],
        ["evidence_map", "claim_graph"],
        ["unknown is not verified", "claims requiring evidence must have support", "preserve source meaning"],
        ["CLAIM_SUPPORT", "SOURCE_TIER", "FRESHNESS", "CONTRADICTION"],
    ),
    DepartmentId.CREATIVE_STRATEGY: _d(
        DepartmentId.CREATIVE_STRATEGY,
        "Turn audience and market understanding into an original project promise and DNA.",
        ["positioning", "audience psychology", "brand strategy", "format strategy", "series design"],
        ["concept development", "differentiation", "project DNA", "format selection"],
        ["reasoning models", "brand systems", "mood/reference boards"],
        ["research_pack", "niche_playbook", "evidence_map"],
        ["creative_brief", "project_dna"],
        ["differentiate at concept and execution levels", "do not inherit competitor story/dialogue/branding"],
        ["AUDIENCE_PROMISE", "DIFFERENTIATION", "FORMAT_FIT", "BRAND_FIT"],
    ),
    DepartmentId.PLANNING: _d(
        DepartmentId.PLANNING,
        "Convert the approved creative strategy and research inputs into an executable production approach before writing and expensive production begin.",
        ["format planning", "retention structure", "production economics", "tool capability", "reference abstraction", "originality boundaries"],
        ["strategy synthesis", "reference-pattern abstraction", "production-mode selection", "automation planning", "fallback planning"],
        ["CapabilityRegistry", "ToolAdapterRegistry", "ExecutionMasteryStore", "research artifacts"],
        ["research_pack", "research_confidence", "research_portfolio", "competitor_profiles", "niche_playbook", "creative_brief", "project_dna"],
        ["production_strategy", "reference_pattern_map", "originality_boundaries", "script_source_pack", "production_conference"],
        ["learn patterns, never copy expression", "creative intent precedes software choice", "track ideal and currently executable tools separately"],
        ["STRATEGY_FIT", "ORIGINALITY_BOUNDARY", "AUTOMATION_FIT", "PRODUCTION_FEASIBILITY"],
    ),
    DepartmentId.WRITERS_ROOM: _d(
        DepartmentId.WRITERS_ROOM,
        "Create format-appropriate scripts, narrative or informational structures and dialogue.",
        ["screenwriting", "causality", "setup/payoff", "dialogue", "exposition", "tutorial structure", "documentary structure"],
        ["beat design", "scene writing", "dialogue writing", "informational scripting", "revision"],
        ["reasoning models", "story skill packs", "evidence map"],
        ["creative_brief", "project_dna", "production_strategy", "script_source_pack", "production_conference", "evidence_map", "niche_playbook"],
        ["script", "beat_graph"],
        ["format grammar before scene grammar", "no unsupported factual claims", "no action without motivation"],
        ["CAUSALITY", "SETUP_PAYOFF", "DIALOGUE_PURPOSE", "FACTUAL_GROUNDING"],
    ),
    DepartmentId.SCRIPT_LOGIC: _d(
        DepartmentId.SCRIPT_LOGIC,
        "Compile scripts into logically consistent state transitions and detect contradictions.",
        ["continuity", "causality", "state machines", "character knowledge", "setup/payoff"],
        ["continuity compilation", "state validation", "contradiction detection", "repair scoping"],
        ["deterministic validators", "story state store"],
        ["script", "beat_graph", "world_bible"],
        ["logic_report", "continuity_contract"],
        ["LLM may propose; code verifies", "repair earliest owning layer", "do not patch downstream symptoms"],
        ["STATE_CONTINUITY", "CHARACTER_KNOWLEDGE", "SETUP_PAYOFF", "CAUSAL_ORDER"],
    ),
    DepartmentId.DIRECTION: _d(
        DepartmentId.DIRECTION,
        "Translate the script or format into audience experience, performance, blocking and audiovisual intent.",
        ["dramaturgy", "actor direction", "blocking", "visual storytelling", "coverage", "editing awareness", "sound intent"],
        ["scene purpose", "emotional arc", "blocking design", "performance intent", "coverage planning"],
        ["director knowledge packs", "previs", "storyboards"],
        ["script", "project_dna", "logic_report"],
        ["director_cut", "scene_dramatic_specs"],
        ["no shot without purpose", "no emotion without cause", "blocking before camera", "workers cannot silently rewrite creative intent"],
        ["SCENE_PURPOSE", "EMOTIONAL_TURN", "BLOCKING_LOGIC", "PAYOFF"],
    ),
    DepartmentId.PERFORMANCE: _d(
        DepartmentId.PERFORMANCE,
        "Convert character objectives and emotion into readable body, face, gaze, timing and voice performance.",
        ["acting", "body mechanics", "facial expression", "gaze", "reaction timing", "prosody"],
        ["performance beats", "gesture planning", "reaction planning", "voice emotion"],
        ["Blender rigs", "facial systems", "voice engines", "motion libraries"],
        ["director_cut", "character_bible"],
        ["performance_plan"],
        ["performance follows objective", "reactions need triggers", "avoid mannequin motion"],
        ["POSE_CLARITY", "GAZE", "CONTACT", "REACTION_TIMING", "EMOTIONAL_READABILITY"],
    ),
    DepartmentId.CINEMATOGRAPHY: _d(
        DepartmentId.CINEMATOGRAPHY,
        "Design composition, lenses, coverage, camera movement and lighting to serve story and information.",
        ["composition", "optics", "lens perspective", "lighting", "exposure", "180-degree rule", "eyelines", "screen direction"],
        ["coverage design", "lens selection", "camera placement", "lighting design", "screen-direction control"],
        ["Blender camera", "Unreal Sequencer", "previs tools"],
        ["director_cut", "blocking_plan", "visual_dna"],
        ["shot_book", "camera_plan", "lighting_plan"],
        ["no shot without purpose", "camera move must be motivated", "preserve action axis unless intentionally reset", "coverage must support edit"],
        ["FRAMING", "EYELINE", "AXIS", "EXPOSURE", "OCCLUSION", "CAMERA_PURPOSE"],
    ),
    DepartmentId.PRODUCTION_DESIGN: _d(
        DepartmentId.PRODUCTION_DESIGN,
        "Own the coherent visual world, characters, costumes, sets, props, materials and graphic language.",
        ["character design", "set design", "color language", "materials", "costume", "props", "visual hierarchy"],
        ["look development", "reference design", "asset bible", "style lock"],
        ["Photoshop", "Blender", "AI image tools", "Canva for fast branded derivatives"],
        ["project_dna", "director_cut"],
        ["asset_bible", "world_bible", "design_bible"],
        ["identity before variation", "assets use persistent IDs", "variants derive from canonical base"],
        ["IDENTITY", "SILHOUETTE", "STYLE_CONSISTENCY", "SPATIAL_READABILITY"],
    ),
    DepartmentId.TECHNICAL_DIRECTION: _d(
        DepartmentId.TECHNICAL_DIRECTION,
        "Translate creative intent into capability requirements and choose execution technology per segment.",
        ["pipeline design", "rendering", "simulation", "DCC automation", "GPU constraints", "tool limitations"],
        ["capability routing", "resource planning", "backend preflight", "fallback analysis"],
        ["CapabilityRegistry", "ToolDoctor", "model registry", "worker adapters"],
        ["production_strategy", "production_conference", "director_cut", "shot_book", "asset_bible"],
        ["production_recipe", "resource_plan", "routing_decisions", "scene_tool_plan", "scene_production_conference", "production_memory_advice", "production_handoff"],
        ["creative intent precedes tool choice", "unsupported backend fails closed", "never silently substitute authenticity-sensitive execution"],
        ["CAPABILITY_FIT", "RESOURCE_FIT", "LICENSE_FIT", "DETERMINISM", "FAIL_CLOSED"],
    ),
    DepartmentId.EDITORIAL: _d(
        DepartmentId.EDITORIAL,
        "Control information, time, attention, emotion and rhythm using a backend-neutral edit plan.",
        ["continuity editing", "montage", "dialogue editing", "J/L cuts", "pacing", "multicam", "B-roll", "retention editing"],
        ["take selection", "rough cut", "pacing pass", "audio-led edit", "versioning"],
        ["OpenTimelineIO", "FFmpeg", "DaVinci Resolve", "Premiere Pro", "Blender VSE"],
        ["director_cut", "dailies", "audio_plan"],
        ["edit_decision_graph", "timeline"],
        ["craft semantics before NLE operations", "preserve payoff and critical information", "minimum necessary cut"],
        ["PACING", "CONTINUITY_EDIT", "INFORMATION_CLARITY", "DEAD_TIME", "VERSION_INTEGRITY"],
    ),
    DepartmentId.AUDIO: _d(
        DepartmentId.AUDIO,
        "Create intelligible, emotionally purposeful dialogue, voice, ambience, Foley, SFX, music and final mix.",
        ["voice direction", "prosody", "dialogue edit", "Foley", "sound design", "music storytelling", "EQ", "dynamics", "loudness"],
        ["voice casting", "TTS direction", "ADR", "SFX design", "mixing", "mastering"],
        ["local TTS", "music models", "SFX libraries", "Fairlight", "FFmpeg"],
        ["script", "director_cut", "timeline"],
        ["voice_plan", "sound_plan", "audio_master"],
        ["silence is intentional", "dialogue intelligibility first", "music must not mask speech", "rights apply to every sound asset"],
        ["CLIPPING", "LOUDNESS", "DIALOGUE_INTELLIGIBILITY", "SYNC", "MUSIC_SFX_BALANCE"],
    ),
    DepartmentId.QC: _d(
        DepartmentId.QC,
        "Independently verify the final experience and route defects to the earliest owning department.",
        ["technical QC", "story QC", "identity", "continuity", "camera", "audio", "color", "rights", "platform delivery"],
        ["automated validation", "watch-through review", "failure taxonomy", "repair routing"],
        ["ffprobe", "VMAF", "vision QC", "audio meters", "deterministic validators"],
        ["all_locked_artifacts", "dailies", "timeline", "master"],
        ["qc_report", "repair_requests"],
        ["render success is not quality success", "whole-film watchability required", "repair minimum scope"],
        ["TECHNICAL", "STORY", "IDENTITY", "CONTINUITY", "CAMERA", "AUDIO", "COLOR", "RIGHTS", "ORIGINALITY"],
    ),
    DepartmentId.RND: _d(
        DepartmentId.RND,
        "Discover, study, test and safely promote new knowledge, tools, models, repositories and skills.",
        ["documentation research", "software architecture", "benchmarking", "security", "licensing", "experimental design"],
        ["tool learning", "repo intake", "skill compilation", "eval design", "regression testing", "deprecation"],
        ["official docs", "GitHub", "papers", "books supplied/licensed by user", "sandbox environments"],
        ["problem_records", "tool_gaps", "analytics_observations"],
        ["skill_candidates", "benchmark_reports", "promotion_decisions"],
        ["official docs first", "knowledge is version-aware", "no production promotion without eval and regression", "core self-modification requires elevated review"],
        ["LICENSE", "SECURITY", "COMPATIBILITY", "BENCHMARK", "REGRESSION"],
    ),
}

# Complete the 26-role company charter, without inventing executable readiness.
# Professional handlers, independent art QC and rights approval must still be
# qualified separately from the presence of these DepartmentSpec records.
from .department_charters_v205 import specialist_department_specs
DEFAULT_DEPARTMENTS.update(specialist_department_specs())


def department_registry() -> dict[DepartmentId, DepartmentSpec]:
    return dict(DEFAULT_DEPARTMENTS)


class DepartmentRegistry:
    def __init__(self, items: dict[DepartmentId, DepartmentSpec] | None = None) -> None:
        self._items = dict(items or DEFAULT_DEPARTMENTS)

    def get(self, department_id: DepartmentId) -> DepartmentSpec:
        return self._items[department_id]

    def list(self) -> list[DepartmentSpec]:
        return [self._items[k] for k in sorted(self._items, key=lambda x: x.value)]


def default_department_registry() -> DepartmentRegistry:
    items = dict(DEFAULT_DEPARTMENTS)
    if DepartmentId.RD_KNOWLEDGE not in items:
        base = items[DepartmentId.RND].model_copy(deep=True)
        base.department_id = DepartmentId.RD_KNOWLEDGE
        items[DepartmentId.RD_KNOWLEDGE] = base
    return DepartmentRegistry(items)
