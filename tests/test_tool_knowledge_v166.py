from __future__ import annotations

from pathlib import Path

from cinefactory.studio.contracts import SkillStatus
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.tool_knowledge import (
    ToolKnowledgeBootstrap,
    audit_tool_mastery,
    default_tool_knowledge_packs,
)
from cinefactory.studio.tooling import DEFAULT_TOOL_SKILLS, ToolDoctor


def test_kernel_bootstraps_versioned_tool_knowledge_and_skill_candidates(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    knowledge = {item.knowledge_id for item in kernel.knowledge.list()}
    assert "blender.4_5.background" in knowledge
    assert "premiere.uxp.2026" in knowledge
    assert "resolve.21_1.manual" in knowledge
    assert "unreal.5_8.movie_render" in knowledge
    assert "comfyui.local.workflow" in knowledge

    blender = kernel.skills.get("tool.blender.production", "4.5")
    premiere = kernel.skills.get("tool.premiere.editorial", "2026")
    assert blender.status is SkillStatus.CANDIDATE
    assert premiere.status is SkillStatus.CANDIDATE
    assert any(note.startswith("validation:") for note in blender.notes)
    assert "operation:scene assembly" in blender.notes
    assert any(
        note.startswith("automation_interface:")
        for note in premiere.notes
    )


def test_tool_knowledge_bootstrap_is_idempotent(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    before_knowledge = len(kernel.knowledge.list())
    before_skills = len(kernel.skills.list())
    ToolKnowledgeBootstrap().bootstrap(kernel)
    assert len(kernel.knowledge.list()) == before_knowledge
    assert len(kernel.skills.list()) == before_skills


def test_tooldoctor_wildcard_install_discovery(monkeypatch, tmp_path: Path):
    program_files = tmp_path / "Program Files"
    premiere = (
        program_files
        / "Adobe"
        / "Adobe Premiere Pro 2026"
        / "Adobe Premiere Pro.exe"
    )
    premiere.parent.mkdir(parents=True)
    premiere.write_bytes(b"fake")
    monkeypatch.setenv("ProgramFiles", str(program_files))
    env = ToolDoctor(tmp_path).inspect("premiere")
    assert env.installed is True
    assert Path(env.executable_path) == premiere


def test_every_declared_core_tool_skill_has_official_knowledge_pack():
    declared = {item.tool_id for item in DEFAULT_TOOL_SKILLS}
    packed = {item.tool_id for item in default_tool_knowledge_packs()}
    assert declared <= packed


def test_mastery_audit_reports_unvalidated_gaps(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    report = audit_tool_mastery(kernel)
    assert report.complete is False
    blender = next(item for item in report.entries if item.tool_id == "blender")
    assert blender.knowledge_items >= 2
    assert "SKILL_NOT_VALIDATED" in blender.gaps
