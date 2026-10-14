from __future__ import annotations

import subprocess
from pathlib import Path

from pydantic import BaseModel, Field

from .acquisition import operation_coverage
from .contracts import DepartmentId, SkillEvaluation, SkillManifest, SkillStatus
from .knowledge import (
    KnowledgeItem,
    KnowledgeKind,
    SourceTier,
    SkillCompiler,
)


class ToolKnowledgePack(BaseModel):
    tool_id: str
    skill_id: str
    version: str
    owner: DepartmentId
    craft_domain: str
    knowledge: list[KnowledgeItem]
    validation_tasks: list[str] = Field(default_factory=list)


class ToolKnowledgeBootstrapReport(BaseModel):
    registered_knowledge: list[str] = Field(default_factory=list)
    registered_skills: list[str] = Field(default_factory=list)
    installed_tools: dict[str, bool] = Field(default_factory=dict)
    production_ready: dict[str, bool] = Field(default_factory=dict)


def _k(
    knowledge_id: str,
    title: str,
    body: str,
    *,
    source_uri: str,
    source_version: str,
    owner: DepartmentId,
    tested: bool = False,
) -> KnowledgeItem:
    return KnowledgeItem(
        knowledge_id=knowledge_id,
        title=title,
        body=body,
        kind=KnowledgeKind.PROCEDURE,
        source_tier=SourceTier.OFFICIAL_DOCS,
        source_uri=source_uri,
        source_version=source_version,
        applicable_versions=[source_version],
        confidence=0.95,
        tested=tested,
        owner=owner,
    )


def default_tool_knowledge_packs() -> list[ToolKnowledgePack]:
    blender_manual = "https://docs.blender.org/manual/en/4.5/advanced/command_line/arguments.html"
    blender_api = "https://docs.blender.org/api/main/info_advanced_blender_as_bpy.html"
    premiere_uxp = "https://developer.adobe.com/premiere-pro/uxp/"
    photoshop_uxp = "https://developer.adobe.com/photoshop/uxp/ps_reference/"
    ae_render = "https://helpx.adobe.com/after-effects/desktop/render-and-export/automate-rendering/automated-rendering-network-rendering.html"
    ae_dev = "https://developer.adobe.com/after-effects/"
    resolve_support = "https://www.blackmagicdesign.com/support/"
    unreal_mrp = "https://dev.epicgames.com/documentation/unreal-engine/movie-render-pipeline-in-unreal-engine"
    ffmpeg_faq = "https://ffmpeg.org/faq.html"
    comfy_docs = "https://docs.comfy.org/essentials/core-concepts/links"
    canva_docs = "https://www.canva.dev/docs/apps/"

    return [
        ToolKnowledgePack(
            tool_id="blender",
            skill_id="tool.blender.production",
            version="4.5",
            owner=DepartmentId.TECHNICAL_DIRECTION,
            craft_domain="3d-production",
            knowledge=[
                _k(
                    "blender.4_5.background",
                    "Blender background automation",
                    "Use --background/-b for UI-less deterministic rendering. Set scene/frame ranges explicitly and keep job outputs inside the project root.",
                    source_uri=blender_manual,
                    source_version="4.5 LTS",
                    owner=DepartmentId.TECHNICAL_DIRECTION,
                    tested=True,
                ),
                _k(
                    "blender.4_5.python",
                    "Blender Python automation",
                    "Use bpy or Blender background Python scripts for scene assembly, rigging, animation, camera, lighting, render and conversion. Prefer a persistent worker when many shots share the same Blender process.",
                    source_uri=blender_api,
                    source_version="4.5 LTS",
                    owner=DepartmentId.TECHNICAL_DIRECTION,
                    tested=True,
                ),
            ],
            validation_tasks=[
                "launch Blender headless",
                "execute Python",
                "render deterministic shot",
                "ffprobe output",
                "verify persistent worker reuse",
            ],
        ),

        ToolKnowledgePack(
            tool_id="ffmpeg",
            skill_id="tool.ffmpeg.post",
            version="1",
            owner=DepartmentId.EDITORIAL,
            craft_domain="editorial-delivery",
            knowledge=[
                _k(
                    "ffmpeg.concat",
                    "FFmpeg concat strategy",
                    "Use concat filter when re-encoding is acceptable; use concat demuxer when compatible streams should be joined without re-encode. Verify every output with ffprobe.",
                    source_uri=ffmpeg_faq,
                    source_version="current",
                    owner=DepartmentId.EDITORIAL,
                    tested=True,
                )
            ],
            validation_tasks=[
                "probe input",
                "concat compatible clips",
                "transcode rough cut",
                "verify duration resolution codecs",
            ],
        ),
        ToolKnowledgePack(
            tool_id="premiere",
            skill_id="tool.premiere.editorial",
            version="2026",
            owner=DepartmentId.EDITORIAL,
            craft_domain="editorial",
            knowledge=[
                _k(
                    "premiere.uxp.2026",
                    "Premiere UXP automation",
                    "Use Premiere UXP for custom tools. Operate through the Premiere DOM for projects, sequences, tracks, clips, markers and application settings; keep edit semantics in the backend-neutral timeline before mutating the NLE.",
                    source_uri=premiere_uxp,
                    source_version="2026-05",
                    owner=DepartmentId.EDITORIAL,
                )
            ],
            validation_tasks=[
                "detect Premiere installation",
                "load signed/local UXP sandbox plugin",
                "create sandbox sequence",
                "place and trim clip",
                "write marker",
                "export and ffprobe",
            ],
        ),
        ToolKnowledgePack(
            tool_id="aftereffects",
            skill_id="tool.aftereffects.motion",
            version="2026",
            owner=DepartmentId.VFX,
            craft_domain="motion-graphics-vfx",
            knowledge=[
                _k(
                    "aftereffects.aerender",
                    "After Effects automated rendering",
                    "Use aerender for command-line render automation and render-farm style batch work. Use scripts/ExtendScript for project manipulation, then verify rendered media externally.",
                    source_uri=ae_render,
                    source_version="2026-compatible",
                    owner=DepartmentId.VFX,
                ),
                _k(
                    "aftereffects.scripting",
                    "After Effects scripting",
                    "Use scripts, panels and supported APIs to automate repetitive project operations; use command-line execution only inside a sandboxed project copy.",
                    source_uri=ae_dev,
                    source_version="2026",
                    owner=DepartmentId.VFX,
                ),
            ],
            validation_tasks=[
                "detect After Effects and aerender",
                "open sandbox project",
                "run script",
                "render composition",
                "ffprobe output",
            ],
        ),

        ToolKnowledgePack(
            tool_id="photoshop",
            skill_id="tool.photoshop.image",
            version="2026",
            owner=DepartmentId.PRODUCTION_DESIGN,
            craft_domain="production-design-packaging",
            knowledge=[
                _k(
                    "photoshop.uxp.2026",
                    "Photoshop UXP automation",
                    "Use the Photoshop UXP DOM to open and modify documents and execute supported operations. Treat UXP method calls as asynchronous where documented and preserve layered source files before export.",
                    source_uri=photoshop_uxp,
                    source_version="2026",
                    owner=DepartmentId.PRODUCTION_DESIGN,
                )
            ],
            validation_tasks=[
                "detect Photoshop",
                "open sandbox document",
                "replace smart object or layer asset",
                "export PNG",
                "verify dimensions",
            ],
        ),
        ToolKnowledgePack(
            tool_id="resolve",
            skill_id="tool.resolve.post",
            version="21.1",
            owner=DepartmentId.COLOR,
            craft_domain="editorial-color-audio",
            knowledge=[
                _k(
                    "resolve.21_1.manual",
                    "DaVinci Resolve 21.1 operational reference",
                    "Use the Resolve 21.1 manual for editing, color, Fusion, Fairlight and delivery. For scripting, prefer the Developer documentation installed with Resolve under Help > Documentation > Developer and gate external scripting by the locally installed version and exposed method surface.",
                    source_uri=resolve_support,
                    source_version="21.1",
                    owner=DepartmentId.COLOR,
                )
            ],
            validation_tasks=[
                "detect Resolve edition",
                "locate local Developer scripting README",
                "connect scripting API",
                "create sandbox timeline",
                "render short master",
                "verify media",
            ],
        ),
        ToolKnowledgePack(
            tool_id="unreal",
            skill_id="tool.unreal.realtime",
            version="5.8",
            owner=DepartmentId.TECHNICAL_DIRECTION,
            craft_domain="realtime-3d",
            knowledge=[
                _k(
                    "unreal.5_8.movie_render",
                    "Unreal Movie Render Pipeline",
                    "Use Movie Render Graph or Movie Render Queue for high-quality linear output. Build jobs from Level Sequences, apply explicit render configuration and use pipeline completion state before accepting output.",
                    source_uri=unreal_mrp,
                    source_version="5.8",
                    owner=DepartmentId.TECHNICAL_DIRECTION,
                )
            ],
            validation_tasks=[
                "detect Unreal",
                "enable Movie Render Queue plugin",
                "open sandbox project",
                "render Level Sequence",
                "verify frames and master",
            ],
        ),

        ToolKnowledgePack(
            tool_id="canva",
            skill_id="tool.canva.packaging",
            version="2026",
            owner=DepartmentId.PRODUCTION_DESIGN,
            craft_domain="fast-design-packaging",
            knowledge=[
                _k(
                    "canva.developer_sdk.2026",
                    "Canva Developers SDK automation",
                    "Use the Canva Developers SDK surfaces intentionally: apps inside Canva for editor automation, REST APIs for platform integration, and Canva for AI assistants where authorized. Keep preview APIs out of production until stable.",
                    source_uri=canva_docs,
                    source_version="2026-09",
                    owner=DepartmentId.PRODUCTION_DESIGN,
                )
            ],
            validation_tasks=[
                "resolve authorized Canva surface",
                "validate app/API permissions",
                "edit sandbox design",
                "export derivative",
                "verify dimensions and brand constraints",
            ],
        ),
        ToolKnowledgePack(
            tool_id="comfyui",
            skill_id="tool.comfyui.generative",
            version="current",
            owner=DepartmentId.GENERATIVE_MEDIA,
            craft_domain="generative-media",
            knowledge=[
                _k(
                    "comfyui.local.workflow",
                    "ComfyUI local workflow operation",
                    "Treat ComfyUI as a local node-based inference engine. Workflows are versioned artifacts; validate required nodes/models before queueing, preserve seeds and workflow versions, and distinguish local nodes from paid API nodes.",
                    source_uri=comfy_docs,
                    source_version="current",
                    owner=DepartmentId.GENERATIVE_MEDIA,
                )
            ],
            validation_tasks=[
                "detect local ComfyUI",
                "validate workflow nodes",
                "queue deterministic workflow",
                "collect output",
                "verify provenance and seed",
            ],
        ),
    ]


class ToolKnowledgeBootstrap:
    def __init__(self, packs: list[ToolKnowledgePack] | None = None) -> None:
        self.packs = packs or default_tool_knowledge_packs()
        self.compiler = SkillCompiler()

    def bootstrap(self, kernel) -> ToolKnowledgeBootstrapReport:
        report = ToolKnowledgeBootstrapReport()
        for pack in self.packs:
            for item in pack.knowledge:
                kernel.knowledge.register(item)
                report.registered_knowledge.append(item.knowledge_id)

            declared = [
                item
                for item in kernel.tool_skills.list(pack.tool_id)
                if item.skill_id == pack.skill_id
            ]
            enrichment_notes = [
                f"validation:{task}" for task in pack.validation_tasks
            ]
            if declared:
                spec = declared[0]
                enrichment_notes.extend(
                    [f"operation:{item}" for item in spec.operations]
                )
                enrichment_notes.extend(
                    [
                        f"automation_interface:{item}"
                        for item in spec.automation_interfaces
                    ]
                )

            try:
                kernel.skills.get(pack.skill_id, pack.version)
            except KeyError:
                manifest: SkillManifest = self.compiler.compile_candidate(
                    skill_id=pack.skill_id,
                    version=pack.version,
                    owner=pack.owner,
                    craft_domain=pack.craft_domain,
                    knowledge=pack.knowledge,
                    tool_binding=pack.tool_id,
                    commercial_safe=None,
                    security_reviewed=True,
                )
                manifest.description = (
                    f"Version-aware {pack.tool_id} skill compiled from official documentation"
                )
                manifest.notes.extend(enrichment_notes)
                kernel.skills.register(manifest)
                report.registered_skills.append(
                    f"{pack.skill_id}@{pack.version}"
                )
            kernel.skills.append_notes(
                pack.skill_id,
                pack.version,
                enrichment_notes,
            )

            env = kernel.tool_doctor.inspect(pack.tool_id)
            report.installed_tools[pack.tool_id] = env.installed
            try:
                manifest = kernel.skills.get(pack.skill_id, pack.version)
                report.production_ready[pack.tool_id] = (
                    manifest.status.value == "PRODUCTION"
                )
            except KeyError:
                report.production_ready[pack.tool_id] = False
        return report


class ToolMasteryEntry(BaseModel):
    tool_id: str
    skill_id: str
    version: str
    installed: bool
    detected_version: str | None = None
    knowledge_items: int
    validation_tasks: int
    skill_status: SkillStatus
    operation_coverage: float = Field(default=0.0, ge=0.0, le=1.0)
    missing_operations: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)


class ToolMasteryReport(BaseModel):
    complete: bool
    entries: list[ToolMasteryEntry]


def audit_tool_mastery(kernel) -> ToolMasteryReport:
    entries: list[ToolMasteryEntry] = []
    for pack in default_tool_knowledge_packs():
        env = kernel.tool_doctor.inspect(pack.tool_id)
        manifest = kernel.skills.get(pack.skill_id, pack.version)
        coverage = operation_coverage(kernel, pack.tool_id)
        gaps: list[str] = []
        if not env.installed and pack.tool_id != "canva":
            gaps.append("TOOL_NOT_INSTALLED")
        if coverage.missing_operations:
            gaps.append(
                "KNOWLEDGE_OPERATION_GAPS:"
                + ",".join(coverage.missing_operations)
            )
        if manifest.status is SkillStatus.CANDIDATE:
            gaps.append("SKILL_NOT_VALIDATED")
        elif manifest.status is SkillStatus.VALIDATED:
            gaps.append("SKILL_NOT_PRODUCTION")
        elif manifest.status is not SkillStatus.PRODUCTION:
            gaps.append(f"SKILL_STATUS_{manifest.status.value}")
        entries.append(
            ToolMasteryEntry(
                tool_id=pack.tool_id,
                skill_id=pack.skill_id,
                version=pack.version,
                installed=env.installed,
                detected_version=env.version,
                knowledge_items=len(pack.knowledge),
                validation_tasks=len(pack.validation_tasks),
                skill_status=manifest.status,
                operation_coverage=coverage.coverage,
                missing_operations=coverage.missing_operations,
                gaps=gaps,
            )
        )
    return ToolMasteryReport(
        complete=all(not item.gaps for item in entries),
        entries=entries,
    )


class LocalCoreSkillValidator:
    """Run deterministic local smoke tests before marking core tool skills validated."""

    def validate_blender(self, kernel) -> SkillEvaluation:
        pack = next(
            item
            for item in default_tool_knowledge_packs()
            if item.tool_id == "blender"
        )
        env = kernel.tool_doctor.inspect("blender")
        if not env.installed or not env.executable_path:
            return SkillEvaluation(
                skill_id=pack.skill_id,
                version=pack.version,
                passed=False,
                score=0.0,
                eval_id="local_environment_smoke",
                findings=["BLENDER_NOT_INSTALLED"],
                regression_passed=False,
            )
        proc = subprocess.run(
            [
                env.executable_path,
                "-b",
                "--python-expr",
                (
                    "import bpy;"
                    "bpy.ops.mesh.primitive_cube_add();"
                    "print('CINEFACTORY_BLENDER_OK')"
                ),
            ],
            cwd=kernel.root,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        passed = proc.returncode == 0 and "CINEFACTORY_BLENDER_OK" in (
            (proc.stdout or "") + (proc.stderr or "")
        )
        return SkillEvaluation(
            skill_id=pack.skill_id,
            version=pack.version,
            passed=passed,
            score=1.0 if passed else 0.0,
            eval_id="local_environment_smoke",
            findings=[] if passed else ["BLENDER_HEADLESS_PYTHON_FAILED"],
            regression_passed=passed,
        )

    def validate_ffmpeg(self, kernel) -> SkillEvaluation:
        pack = next(
            item
            for item in default_tool_knowledge_packs()
            if item.tool_id == "ffmpeg"
        )
        env = kernel.tool_doctor.inspect("ffmpeg")
        if not env.installed or not env.executable_path:
            return SkillEvaluation(
                skill_id=pack.skill_id,
                version=pack.version,
                passed=False,
                score=0.0,
                eval_id="local_environment_smoke",
                findings=["FFMPEG_NOT_INSTALLED"],
                regression_passed=False,
            )
        output_dir = Path(kernel.root) / "data" / "studio" / "tool_evals"
        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / "ffmpeg_smoke.mp4"
        proc = subprocess.run(
            [
                env.executable_path,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=gray:s=64x64:r=2:d=1",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(output),
            ],
            cwd=kernel.root,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        passed = proc.returncode == 0 and output.is_file() and output.stat().st_size > 0
        return SkillEvaluation(
            skill_id=pack.skill_id,
            version=pack.version,
            passed=passed,
            score=1.0 if passed else 0.0,
            eval_id="local_environment_smoke",
            findings=[] if passed else ["FFMPEG_ENCODE_FAILED"],
            regression_passed=passed,
        )

    def validate_installed_core(self, kernel) -> list[SkillEvaluation]:
        evaluations = [
            self.validate_blender(kernel),
            self.validate_ffmpeg(kernel),
        ]
        for evaluation in evaluations:
            kernel.skills.record_evaluation(evaluation)
            if evaluation.passed and evaluation.regression_passed:
                kernel.skills.validate_skill(
                    evaluation.skill_id,
                    evaluation.version,
                )
        return evaluations
