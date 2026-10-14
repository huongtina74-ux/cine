from __future__ import annotations

import re

from pydantic import BaseModel, Field

from .acquisition import CaptureMode, KnowledgeSource
from .contracts import DepartmentId
from .knowledge import SourceTier


class CraftCurriculumModule(BaseModel):
    source: KnowledgeSource
    text: str
    operation_hints: dict[str, list[str]] = Field(default_factory=dict)


class CraftCurriculumReport(BaseModel):
    sources: list[str] = Field(default_factory=list)
    snapshots: list[str] = Field(default_factory=list)
    knowledge_items: list[str] = Field(default_factory=list)


def _craft_source(
    source_id: str,
    craft_id: str,
    title: str,
    owner: DepartmentId,
) -> KnowledgeSource:
    return KnowledgeSource(
        source_id=source_id,
        tool_id=craft_id,
        title=title,
        source_uri=None,
        source_tier=SourceTier.STANDARD,
        source_version="cinefactory-craft-v1",
        owner=owner,
        capture_mode=CaptureMode.INTERNAL_STANDARD,
        metadata={
            "authority": "internal studio craft standard",
            "purpose": "deterministic production guidance; not an external factual authority",
        },
    )


def default_craft_modules() -> list[CraftCurriculumModule]:
    return [
        CraftCurriculumModule(
            source=_craft_source(
                "craft.cinematography.v1",
                "craft.cinematography",
                "CineFactory cinematography craft standard",
                DepartmentId.CINEMATOGRAPHY,
            ),
            operation_hints={
                "coverage": ["coverage", "wide", "medium", "close"],
                "eyeline": ["eyeline", "look", "gaze"],
                "axis": ["axis", "180", "screen direction"],
                "motivated camera": ["camera move", "motivated", "dolly", "pan"],
                "lens": ["lens", "focal length", "perspective"],
                "lighting": ["key light", "fill", "rim", "exposure"],
            },
            text="""# coverage
Design coverage around the scene objective and edit needs: establish geography, capture the dramatic action, protect reactions and provide enough angle/size variation to cut without breaking spatial logic. Do not create extra shots that have no editorial purpose.

# eyeline
Keep looking direction and subject-to-subject eyelines coherent across coverage. A close-up must still read as the same spatial relationship established by wider shots unless the scene intentionally resets geography.

# axis
Establish the action axis from blocking and keep cameras on a consistent side until an intentional neutral shot or visible camera/actor movement resets the axis. Screen direction is a continuity contract, not a cosmetic preference.

# motivated camera
Move the camera because audience attention, character movement or dramatic emphasis motivates it. Avoid constant floating motion. Start and stop movement with readable intention and protect stable frames where performance or information needs to land.

# lens
Choose focal length for perspective and emotional distance, not merely framing. Wider lenses exaggerate spatial relationships when close; longer lenses compress space. Keep lens changes consistent with the visual grammar of the project.

# lighting
Light for subject readability, depth, continuity and mood. Separate key/fill/rim/environment responsibilities where useful, protect important faces or focal subjects, and validate exposure across adjacent shots before final render.""",
        ),
        CraftCurriculumModule(
            source=_craft_source(
                "craft.performance.v1",
                "craft.performance",
                "CineFactory performance and animation craft standard",
                DepartmentId.PERFORMANCE,
            ),
            operation_hints={
                "objective": ["objective", "want", "goal"],
                "trigger reaction": ["trigger", "reaction", "response"],
                "gaze": ["gaze", "look", "eyes", "head"],
                "pose clarity": ["pose", "silhouette", "readability"],
                "body mechanics": ["weight", "balance", "hips", "feet"],
                "timing": ["timing", "anticipation", "hold", "settle"],
            },
            text="""# objective
Every performance beat should express what the character wants now. Body direction, gesture, facial state and vocal intention should support that objective instead of displaying random emotion.

# trigger reaction
A reaction must have a perceivable trigger. Preserve the order stimulus, recognition, response; do not make every body part move at the same frame. The audience should be able to understand what caused the change.

# gaze
Use eye, head and torso orientation to show attention. Large attention shifts usually lead with the eyes/head and may recruit the torso; listening characters still perform through gaze and micro-reactions rather than freezing.

# pose clarity
Build readable silhouettes and avoid tangencies that hide important limbs or gestures. Strong key poses should communicate the action even without motion, especially for stylized Minecraft and Roblox characters.

# body mechanics
Respect balance, support and weight transfer. Foot plants should not slide unintentionally, hips and torso should respond to locomotion, and contacts with props or other characters must align spatially.

# timing
Use anticipation, action, reaction, settle and holds deliberately. Fast motion needs readable preparation or aftermath; emotional beats often need a small hold so the audience can register the change before the next action.""",
        ),
        CraftCurriculumModule(
            source=_craft_source(
                "craft.editorial.v1",
                "craft.editorial",
                "CineFactory editorial craft standard",
                DepartmentId.EDITORIAL,
            ),
            operation_hints={
                "continuity": ["continuity", "match", "screen direction"],
                "cut timing": ["cut", "timing", "action"],
                "J/L cut": ["j cut", "l cut", "audio lead", "audio trail"],
                "pacing": ["pacing", "rhythm", "dead time"],
                "reaction": ["reaction", "response shot"],
                "information": ["information", "clarity", "setup", "payoff"],
            },
            text="""# continuity
Preserve spatial, action, prop and performance continuity unless a deliberate discontinuity serves the project. Cut points should not create impossible positions, duplicated actions or broken screen direction.

# cut timing
Cut when new information, movement, emotion or attention justifies the transition. Cutting on action can hide the edit and preserve momentum, but do not cut so aggressively that setup or reaction becomes unreadable.

# J/L cut
Use audio leads and trails to smooth dialogue or scene transitions when they support comprehension and rhythm. Audio overlap is an editorial device, not a default effect; protect intelligibility and sync-critical events.

# pacing
Control perceived speed through shot duration, information density, movement and sound. Remove dead time that adds no tension, comprehension or atmosphere, but preserve necessary holds for reactions and important visual information.

# reaction
Protect reaction shots when they deliver consequence, emotion or causality. A major event without a readable response can make a scene feel mechanically assembled even when all dialogue and actions are present.

# information
The edit must preserve the minimum information required for the audience to understand cause, objective, change and payoff. Do not sacrifice essential setup for superficial speed.""",
        ),

        CraftCurriculumModule(
            source=_craft_source(
                "craft.audio.v1",
                "craft.audio",
                "CineFactory audio and sound-design craft standard",
                DepartmentId.AUDIO,
            ),
            operation_hints={
                "dialogue priority": ["dialogue", "speech", "intelligibility"],
                "ambience": ["ambience", "room tone", "environment"],
                "foley": ["foley", "contact", "movement"],
                "sfx": ["sfx", "sound effect", "impact"],
                "music": ["music", "score", "duck"],
                "loudness": ["loudness", "peak", "limiter"],
                "sync": ["sync", "lip", "event"],
            },
            text="""# dialogue priority
Keep speech intelligible before adding density elsewhere. Voice level, EQ, noise control and competing music/SFX should support comprehension and character performance.

# ambience
Use room tone and environmental beds to establish place and prevent unnatural silence between edits. Ambience should change when the acoustic environment changes and remain stable enough to hide picture edits.

# foley
Use Foley for readable physical contacts, footsteps, cloth and prop interaction when those sounds help sell weight and action. Synchronize important contacts precisely enough that the picture feels grounded.

# sfx
Sound effects should reinforce story events, scale and attention. Avoid stacking many effects only to make a moment louder; choose layers with distinct functions such as impact, texture, tail and environment response.

# music
Music supports emotion, structure and momentum but must not mask dialogue. Automate or duck music where speech needs space, and treat copyrighted or licensed tracks as rights-controlled assets.

# loudness
Maintain headroom through the mix, prevent digital clipping and evaluate loudness at the delivery stage. A limiter is a safety/control tool, not a substitute for balanced gain staging.

# sync
Keep dialogue, Foley and event-critical effects synchronized to the intended visual action. A technically valid file with perceptible sync drift is a failed audio master.""",
        ),
        CraftCurriculumModule(
            source=_craft_source(
                "craft.color.v1",
                "craft.color",
                "CineFactory color-finishing craft standard",
                DepartmentId.COLOR,
            ),
            operation_hints={
                "normalization": ["normalize", "input transform", "color management"],
                "exposure balance": ["exposure", "white balance", "contrast"],
                "shot matching": ["match", "adjacent shot", "continuity"],
                "look": ["look", "creative grade", "palette"],
                "scopes": ["waveform", "vectorscope", "scope"],
                "delivery": ["delivery", "output transform", "legal range"],
            },
            text="""# normalization
Normalize source material into the chosen color-management pipeline before creative grading. Keep input interpretation and output transform explicit so the same grade can be reproduced.

# exposure balance
Correct exposure, white balance and baseline contrast before adding a creative look. Protect important subject detail and avoid compensating for one bad shot by breaking the rest of the sequence.

# shot matching
Match adjacent shots for brightness, color balance and subject appearance before local polish. Continuity is more important than making every isolated frame maximally dramatic.

# look
Apply the creative look as a controlled layer on top of technical normalization and matching. Keep palette and contrast behavior consistent with project visual DNA and avoid destroying important detail solely for style.

# scopes
Use objective scopes alongside the display: waveform for luminance/exposure relationships, vectorscope for chroma direction/saturation and other monitoring appropriate to the pipeline. Displays alone can mislead.

# delivery
Render through the intended output transform and delivery contract. Verify range, codec, bit depth/pixel format where applicable, and ensure the final encode preserves the approved grade.""",
        ),
    ]


class CraftCurriculumBootstrap:
    def __init__(self, modules: list[CraftCurriculumModule] | None = None) -> None:
        self.modules = modules or default_craft_modules()

    @staticmethod
    def _slug(value: str) -> str:
        value = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
        return value[:72] or "craft"

    def bootstrap(self, kernel) -> CraftCurriculumReport:
        report = CraftCurriculumReport()
        engine = kernel.knowledge_acquisition
        for module in self.modules:
            try:
                engine.register_source(module.source)
            except FileExistsError:
                if engine.store.get_source(module.source.source_id) != module.source:
                    raise
            report.sources.append(module.source.source_id)
            result = engine.ingest_text(
                source_id=module.source.source_id,
                text=module.text,
                operation_hints=module.operation_hints,
                metadata={"craft_curriculum": True},
            )
            report.snapshots.append(result.snapshot_id)
            chunks = engine.store.list_chunks(snapshot_id=result.snapshot_id)
            for chunk in chunks:
                title = chunk.heading or module.source.title
                knowledge_id = (
                    f"{module.source.tool_id}."
                    f"{self._slug(title)}.{chunk.chunk_id[-8:].lower()}"
                )
                try:
                    engine.create_reviewed_item(
                        knowledge_id=knowledge_id,
                        title=title,
                        body=chunk.text,
                        chunk_ids=[chunk.chunk_id],
                        operations=set(chunk.operations),
                        confidence=0.9,
                        tested=False,
                    )
                except FileExistsError:
                    pass
                report.knowledge_items.append(knowledge_id)
        return report
