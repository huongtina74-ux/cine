from __future__ import annotations

import re

from pydantic import BaseModel, Field

from .acquisition import CaptureMode, KnowledgeSource, operation_coverage
from .contracts import DepartmentId
from .knowledge import SourceTier


class CurriculumModule(BaseModel):
    source: KnowledgeSource
    text: str
    operation_hints: dict[str, list[str]] = Field(default_factory=dict)


class CurriculumBootstrapReport(BaseModel):
    sources: list[str] = Field(default_factory=list)
    snapshots: list[str] = Field(default_factory=list)
    knowledge_items: list[str] = Field(default_factory=list)
    coverage: dict[str, float] = Field(default_factory=dict)


def _source(
    source_id: str,
    tool_id: str,
    title: str,
    uri: str,
    version: str,
    owner: DepartmentId,
) -> KnowledgeSource:
    return KnowledgeSource(
        source_id=source_id,
        tool_id=tool_id,
        title=title,
        source_uri=uri,
        source_tier=SourceTier.OFFICIAL_DOCS,
        source_version=version,
        owner=owner,
        capture_mode=CaptureMode.AGENT_SNAPSHOT,
        metadata={
            "content_policy": "concise operational paraphrase; official source remains canonical",
        },
    )


def default_curriculum_modules() -> list[CurriculumModule]:
    return [
        CurriculumModule(
            source=_source(
                "blender.4_5.production_curriculum",
                "blender",
                "Blender 4.5 LTS production automation curriculum",
                "https://docs.blender.org/manual/en/4.5/",
                "4.5 LTS",
                DepartmentId.TECHNICAL_DIRECTION,
            ),
            operation_hints={
                "scene assembly": ["scene", "collection", "object"],
                "rigging": ["armature", "bone", "rig"],
                "animation": ["keyframe", "action", "animation"],
                "camera": ["camera", "lens", "active camera"],
                "lighting": ["light", "exposure", "world"],
                "render": ["render", "eevee", "cycles"],
                "compositing": ["compositor", "nodes", "composite"],
                "asset conversion": ["import", "export", "asset"],
                "headless batch": ["background", "command line", "--background"],
            },
            text="""# Scene assembly
Build scenes deterministically through bpy: create or link objects into explicit collections, name persistent assets predictably, set transforms numerically, and save a project copy before destructive conversion. Avoid relying on selection or UI focus when an operator has a data API alternative.

# Rigging
Treat the armature, deform bones, control bones and constraints as separate responsibilities. Validate parent relationships and rest pose before animation. When automating block characters, use persistent bone or body-part identifiers so clips can be retargeted without guessing names.

# Animation
Set scene FPS before placing keys. Prefer explicit data paths, actions and keyframe times over UI-driven manipulation. Keep locomotion, gesture, reaction and facial layers separable so the director can repair one layer without rebuilding a whole take.

# Camera
Create cameras with explicit transforms and lens settings, assign the intended camera to the scene, and validate subject visibility before rendering. Preserve screen direction and eyelines at the shot-planning layer rather than repairing them in post.

# Lighting
Create named lights and world settings from a style or scene recipe. Keep key, fill, rim and environment responsibilities understandable so lighting can be tuned systematically. Validate exposure and subject readability with a preview before expensive final rendering.

# Render
Use an explicit render engine, frame range, resolution, FPS, output format and output path. For automation, Blender background mode can render frames or animations without the UI. Treat a successful process exit as insufficient until the produced media is probed and QC passes.

# Compositing
Use compositor nodes for deterministic post-render operations such as alpha handling, glare or color transforms when those effects belong to the 3D render pipeline. Keep final editorial semantics outside Blender unless the project explicitly chooses Blender VSE as the NLE.

# Asset conversion
Import or export assets in a controlled sandbox, preserve source assets, normalize scale and orientation deliberately, and verify materials, armatures and animation after conversion. Record the converter and version in asset provenance.

# Headless batch
For unattended jobs use Blender command-line background mode and Python scripts or expressions. Disable automatic execution of untrusted blend-file scripts by default; enable auto-execution only for trusted controlled project inputs. Pass job-specific values after the command-line separator or through validated configuration.""",
        ),
        CurriculumModule(
            source=_source(
                "premiere.uxp.production_curriculum",
                "premiere",
                "Premiere Pro UXP editorial automation curriculum",
                "https://developer.adobe.com/premiere-pro/uxp/",
                "26.x",
                DepartmentId.EDITORIAL,
            ),
            operation_hints={
                "import media": ["import", "media", "project item"],
                "create sequence": ["sequence", "create sequence"],
                "place clip": ["track item", "insert", "overwrite", "place clip"],
                "trim": ["in point", "out point", "trim"],
                "markers": ["marker", "markers"],
                "captions": ["caption", "captions"],
                "audio edit": ["audio track", "mute", "audio"],
                "effects": ["effect", "transition"],
                "export": ["export", "encoder"],
            },
            text="""# Import media
Use the Premiere UXP application/project APIs to work with the active project and project items. Keep filesystem permission handling in the plugin layer and preserve imported media provenance so a timeline can be rebuilt.

# Create sequence
Resolve the active project first, then create or select the intended sequence through the supported Premiere DOM. Read sequence settings and timebase instead of assuming a frame rate. Store the sequence identity in the project artifact.

# Place clip
Use sequence/timeline editing APIs to insert, overwrite, move or clone track items at explicit times and tracks. The backend-neutral edit decision graph remains the source of editorial intent; Premiere is an execution backend, not the place where the agent invents new cuts.

# Trim
Represent in/out points and clip timing using Premiere time objects rather than floating-point guesses. Make trim actions deterministic and re-read item timing after mutation before accepting the edit.

# Markers
Use markers for machine-readable editorial notes, QC findings, review points and synchronization cues where supported. Names and comments should include stable project identifiers rather than natural-language-only references.

# Captions
Treat caption content, timing and language as versioned artifacts before writing them to the NLE. Keep transcript correction upstream so regenerating a timeline does not destroy the source of truth.

# Audio edit
Read audio track state and operate on explicit audio clips/tracks. Dialogue intelligibility, loudness targets and mix intent come from the audio plan; Premiere executes the edit but does not redefine the mix specification.

# Effects
Apply transitions and effects only when required by the edit or visual specification. Prefer supported UXP actions and inspect minimum-version requirements because Premiere UXP methods can change between releases.

# Export
Export only from a locked sequence/version and record the export preset/settings with the master artifact. Verify the exported file independently with ffprobe and final QC rather than trusting export completion alone.""",
        ),
        CurriculumModule(
            source=_source(
                "ffmpeg.7_1.post_curriculum",
                "ffmpeg",
                "FFmpeg 7.1 post-production curriculum",
                "https://ffmpeg.org/documentation.html",
                "7.1",
                DepartmentId.EDITORIAL,
            ),
            operation_hints={
                "probe": ["ffprobe", "probe"],
                "transcode": ["transcode", "codec", "encode"],
                "concat": ["concat", "join"],
                "filter": ["filter", "filtergraph"],
                "audio mix": ["amix", "audio", "loudness"],
                "captions": ["caption", "subtitle", "srt", "mov_text"],
                "master": ["master", "pixel format", "container"],
                "delivery QC": ["ffprobe", "verify", "qc"],
            },
            text="""# Probe
Run ffprobe before processing unknown media and request machine-readable output for format, stream, duration, frame rate, dimensions, pixel format, sample rate and channel layout. A positive failure code means the input could not be opened or recognized and must fail the stage.

# Transcode
Select codecs, pixel format, frame rate and audio parameters explicitly. Avoid unnecessary generation loss by copying streams when safe, but transcode when normalization or filters are required. Preserve the command and source hashes in provenance for reproducibility.

# Concat
Use the concat demuxer when compatible streams can be joined without re-encoding; use a concat/filter workflow when streams require processing or normalization. Validate timestamps and final duration after joining.

# Filter
Build filtergraphs from structured parameters instead of concatenating untrusted command fragments. Keep scale, crop, fps, subtitles and color operations explicit and test the graph on a short sample before a long render.

# Audio mix
Mix named dialogue, music, ambience and SFX inputs deliberately. Prevent clipping, preserve dialogue priority and measure loudness in the QC layer. Do not infer that a command succeeded merely because an output file exists.

# Captions
Treat captions as a versioned timed-text artifact such as SRT or WebVTT. Validate cue ordering and timing before muxing or burning them. For delivery, choose an explicit subtitle codec/container combination, then probe the output to confirm the subtitle stream exists; keep the source timed-text file as the editable source of truth.

# Master
Write a master with explicit container, video codec, audio codec, pixel format, resolution and frame rate. Keep an intermediate/mezzanine option when repeated downstream derivatives would otherwise cause avoidable re-encoding.

# Delivery QC
Probe every final derivative and compare measured properties with the delivery contract. Check duration, streams, codecs, dimensions, frame rate and audio properties, then run higher-level black/freeze/loudness checks where required.""",
        ),
    ]


class ToolCurriculumBootstrap:
    def __init__(self, modules: list[CurriculumModule] | None = None) -> None:
        self.modules = modules or (
            default_curriculum_modules() + extended_curriculum_modules()
        )

    @staticmethod
    def _slug(value: str) -> str:
        value = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_").lower()
        return value[:72] or "knowledge"

    def bootstrap(self, kernel) -> CurriculumBootstrapReport:
        report = CurriculumBootstrapReport()
        engine = kernel.knowledge_acquisition
        for module in self.modules:
            try:
                engine.register_source(module.source)
            except FileExistsError:
                existing = engine.store.get_source(module.source.source_id)
                if existing != module.source:
                    raise
            report.sources.append(module.source.source_id)
            acquired = engine.ingest_text(
                source_id=module.source.source_id,
                text=module.text,
                operation_hints=module.operation_hints,
                metadata={"curriculum": True},
            )
            report.snapshots.append(acquired.snapshot_id)
            chunks = engine.store.list_chunks(snapshot_id=acquired.snapshot_id)
            for chunk in chunks:
                title = chunk.heading or f"{module.source.tool_id} procedure"
                knowledge_id = (
                    f"{module.source.tool_id}.curriculum."
                    f"{self._slug(title)}.{chunk.chunk_id[-8:].lower()}"
                )
                try:
                    engine.create_reviewed_item(
                        knowledge_id=knowledge_id,
                        title=title,
                        body=chunk.text,
                        chunk_ids=[chunk.chunk_id],
                        operations=set(chunk.operations),
                        confidence=0.95,
                        tested=False,
                    )
                except FileExistsError:
                    pass
                report.knowledge_items.append(knowledge_id)

        for tool_id in sorted({module.source.tool_id for module in self.modules}):
            report.coverage[tool_id] = operation_coverage(kernel, tool_id).coverage
        return report


def extended_curriculum_modules() -> list[CurriculumModule]:
    return [
        CurriculumModule(
            source=_source(
                "resolve.21_1.post_curriculum",
                "resolve",
                "DaVinci Resolve 21.1 post-production curriculum",
                "https://www.blackmagicdesign.com/support/",
                "21.1",
                DepartmentId.COLOR,
            ),
            operation_hints={
                "edit": ["edit", "timeline", "clip", "trim"],
                "Fusion comp": ["fusion", "node", "composition"],
                "color": ["color", "grade", "node", "scopes"],
                "Fairlight mix": ["fairlight", "audio", "mix", "bus"],
                "deliver": ["deliver", "render", "export", "preset"],
            },
            text="""# edit
Build the timeline from locked edit decisions, explicit source/timecode references and known frame rate. Keep clip placement, trimming, track assignment and versioning deterministic so the edit can be regenerated. Resolve is an execution backend; story and edit intent remain upstream artifacts.

# Fusion comp
Use Fusion as a node graph for compositing and motion/VFX tasks that require explicit image-processing relationships. Keep inputs, masks, transforms and output nodes named and versioned so a failed composite can be repaired without rebuilding unrelated post stages.

# color
Grade from a defined color-management and look contract. Separate technical normalization from creative look decisions, use scopes rather than display appearance alone, and preserve shot-to-shot consistency before adding local refinements.

# Fairlight mix
Build dialogue, ambience, Foley, SFX and music as separately controllable tracks or buses. Preserve dialogue intelligibility first, maintain headroom, and verify sync and loudness after processing instead of trusting mixer state.

# deliver
Render only from a locked timeline/version. Make output path, container, codec, resolution, frame rate and audio settings explicit. Treat render completion as provisional until independent media probe and delivery QC pass.""",
        ),
        CurriculumModule(
            source=_source(
                "aftereffects.2026.motion_curriculum",
                "aftereffects",
                "After Effects 2026 motion and automation curriculum",
                "https://developer.adobe.com/after-effects/",
                "2026",
                DepartmentId.VFX,
            ),
            operation_hints={
                "compositions": ["composition", "comp", "composition item"],
                "layers": ["layer", "layers", "source"],
                "keyframes": ["keyframe", "property", "time"],
                "expressions": ["expression", "javascript", "property"],
                "templates": ["template", "mogrt", "essential graphics"],
                "render queue": ["render queue", "aerender", "output module"],
            },
            text="""# compositions
Create or resolve compositions by stable identifiers and explicit dimensions, frame rate and duration. Keep composition ownership clear so generated layers do not silently mutate unrelated comps.

# layers
Operate on explicit layer references and preserve source, ordering, in/out times and parenting. Avoid automation that depends only on current UI selection because batch execution must remain deterministic.

# keyframes
Set property values and keyframe times from structured animation data. Keep easing and interpolation intentional and verify temporal ordering after changes so generated motion does not create accidental jumps or duplicate keys.

# expressions
Use expressions for property relationships and procedural animation, not as a substitute for project-wide orchestration. Expressions evaluate property values while scripts perform application actions; keep the distinction explicit and version-sensitive.

# templates
Treat reusable motion-graphics templates as versioned assets with named editable controls. Validate required fonts, media, dimensions and exposed properties before populating them automatically.

# render queue
Queue only known compositions and explicit output modules. For unattended rendering use supported command-line rendering such as aerender where appropriate, isolate sandbox projects, and verify every rendered output externally.""",
        ),
        CurriculumModule(
            source=_source(
                "photoshop.2026.image_curriculum",
                "photoshop",
                "Photoshop UXP production-design curriculum",
                "https://developer.adobe.com/photoshop/uxp/ps_reference/",
                "2026",
                DepartmentId.PRODUCTION_DESIGN,
            ),
            operation_hints={
                "layers": ["layer", "layers", "document"],
                "masks": ["mask", "selection"],
                "smart objects": ["smart object", "placed layer", "replace contents"],
                "text": ["text", "text layer", "font"],
                "composite": ["composite", "blend", "opacity"],
                "thumbnail": ["thumbnail", "canvas", "composition"],
                "batch export": ["export", "save", "batch"],
            },
            text="""# layers
Prefer Photoshop's UXP DOM for document and layer operations. Resolve layers by stable document/layer identity where possible, preserve hierarchy, and avoid relying only on the currently selected layer.

# masks
Create selections and masks as reversible operations. Keep source pixels intact when possible, validate mask bounds, and use non-destructive layer structure so later packaging revisions remain repairable.

# smart objects
Use Smart Objects when an asset must be replaceable without destroying the surrounding design. Preserve transform and placement intent, then verify the replacement visually and by expected dimensions.

# text
Keep text content, font choice, size, bounds and alignment as structured brand artifacts. Validate font availability and prevent overflow before export.

# composite
Use explicit blend mode, opacity, masks and layer order to build composites. Prefer DOM operations first; use batchPlay only when required functionality is not exposed through the DOM, and run state-mutating commands in the required modal execution scope.

# thumbnail
Build thumbnails from a locked visual hierarchy: focal subject, readable title treatment when required, controlled contrast and safe-edge composition. Preserve a layered source so copy, crop and locale variants can be regenerated.

# batch export
Export derivatives from a known document state with explicit size, format and destination. Preserve layered originals, use asynchronous UXP operations correctly, and verify output dimensions and file existence after export.""",
        ),

        CurriculumModule(
            source=_source(
                "unreal.5_8.realtime_curriculum",
                "unreal",
                "Unreal Engine 5.8 realtime cinematic curriculum",
                "https://dev.epicgames.com/documentation/unreal-engine/movie-render-pipeline-in-unreal-engine",
                "5.8",
                DepartmentId.TECHNICAL_DIRECTION,
            ),
            operation_hints={
                "level assembly": ["level", "actor", "asset", "map"],
                "Sequencer": ["sequencer", "level sequence", "track"],
                "camera": ["camera", "cine camera", "camera cut"],
                "lighting": ["light", "lumen", "exposure"],
                "Movie Render Pipeline": ["movie render", "mrq", "mrg", "render job"],
            },
            text="""# level assembly
Assemble a cinematic level from named assets, actors and maps with explicit transforms. Separate reusable set assets from shot-specific state and validate required plugins/assets before attempting a render job.

# Sequencer
Use Level Sequences as the authoritative cinematic timing container for Unreal execution. Keep tracks, bindings, shot sections and timing explicit so camera, animation and events can be regenerated from upstream production artifacts.

# camera
Use Cine Camera Actors and camera-cut tracks with intentional lens, focus and transform settings. Preserve screen direction and coverage logic from the shot book rather than allowing realtime staging to invent new camera semantics.

# lighting
Build lighting from a scene look and exposure contract. Validate realtime preview for subject readability, then use production render settings when offline output requires higher quality than viewport playback.

# Movie Render Pipeline
Use Movie Render Queue or Movie Render Graph for production linear output. Create jobs from Level Sequences, set the correct map and explicit output configuration, wait for pipeline completion, and verify the resulting media or image sequence before accepting the stage.""",
        ),
        CurriculumModule(
            source=_source(
                "canva.2026.packaging_curriculum",
                "canva",
                "Canva Developers SDK packaging curriculum",
                "https://www.canva.dev/docs/apps/",
                "2026-09",
                DepartmentId.PRODUCTION_DESIGN,
            ),
            operation_hints={
                "brand template": ["brand", "template", "design"],
                "text replacement": ["text", "replace", "content"],
                "asset replacement": ["asset", "image", "media", "replace"],
                "social derivative": ["page", "resize", "derivative", "social"],
                "export": ["export", "requestexport", "export job"],
            },
            text="""# brand template
Treat the Canva design or template as a versioned brand artifact. Preserve layout, typography, palette and locked brand elements; only expose fields that downstream automation is authorized to change.

# text replacement
Replace only approved text fields and validate length, wrapping and layout after mutation. Keep the source copy artifact upstream so localized or revised variants can be reproduced.

# asset replacement
Replace images or media through supported app/API surfaces with explicit asset provenance. Preserve crop and placement intent where possible and visually verify the result before publication.

# social derivative
Generate platform derivatives from a canonical design while preserving hierarchy and brand constraints. Treat each target size/page as a separate output contract rather than blindly scaling the master.

# export
Use the supported Apps SDK export flow or REST export job depending on the integration surface. REST exports are asynchronous: create the job, poll its status, retrieve the resulting URL, then persist the exported file because temporary download links expire.""",
        ),
        CurriculumModule(
            source=_source(
                "comfyui.current.generative_curriculum",
                "comfyui",
                "ComfyUI local generative workflow curriculum",
                "https://docs.comfy.org/",
                "current",
                DepartmentId.GENERATIVE_MEDIA,
            ),
            operation_hints={
                "workflow load": ["workflow", "json", "graph"],
                "node validation": ["node", "validate", "custom node"],
                "prompt queue": ["queue", "prompt", "execution"],
                "seed control": ["seed", "noise", "deterministic"],
                "output collection": ["output", "history", "image", "video"],
                "provenance": ["workflow", "seed", "model", "metadata"],
            },
            text="""# workflow load
Treat the ComfyUI workflow graph as a versioned production artifact. Load only workflows whose required nodes, models and parameters are known to the project, and keep API-format workflow data separate from UI-only assumptions.

# node validation
Resolve every required node type and model before queueing execution. Missing or incompatible custom nodes must block the workflow rather than silently changing graph semantics.

# prompt queue
Submit validated prompt/workflow graphs to the local execution queue and track the execution identifier through completion or failure. Do not infer success from HTTP acceptance alone.

# seed control
Persist seeds and relevant sampler/model parameters whenever reproducibility matters. A repair pass may intentionally change a seed, but that change must be recorded in provenance.

# output collection
Collect only outputs associated with the submitted execution and expected output nodes. Validate file existence, dimensions/media properties and project destination before registering generated assets.

# provenance
Store workflow version/hash, model identifiers, custom-node environment, seed and material input references with each generated asset so successful outputs can be reproduced and failures can be diagnosed.""",
        ),
    ]
