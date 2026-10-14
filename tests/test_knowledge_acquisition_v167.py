from __future__ import annotations

from pathlib import Path

from cinefactory.studio.acquisition import (
    AgentKnowledgePacket,
    CaptureMode,
    KnowledgeAcquisitionEngine,
    KnowledgeAcquisitionStore,
    KnowledgeSource,
    ToolTaskKnowledgeResolver,
    operation_coverage,
)
from cinefactory.studio.contracts import DepartmentId
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.knowledge import KnowledgeRegistry, SourceTier


def _engine(tmp_path: Path) -> KnowledgeAcquisitionEngine:
    registry = KnowledgeRegistry(tmp_path / "knowledge")
    store = KnowledgeAcquisitionStore(tmp_path / "acquisition")
    return KnowledgeAcquisitionEngine(store, registry)


def test_snapshot_ingest_is_hash_deduplicated_and_chunked(tmp_path: Path):
    engine = _engine(tmp_path)
    source = KnowledgeSource(
        source_id="blender.test",
        tool_id="blender",
        title="Blender test source",
        source_uri="https://docs.blender.org/",
        source_tier=SourceTier.OFFICIAL_DOCS,
        source_version="4.5",
        owner=DepartmentId.TECHNICAL_DIRECTION,
        capture_mode=CaptureMode.AGENT_SNAPSHOT,
    )
    engine.register_source(source)
    text = """# Camera
Create a camera and assign it to the scene.

# Render
Use background mode for unattended render jobs."""
    first = engine.ingest_text(
        source_id=source.source_id,
        text=text,
        operation_hints={
            "camera": ["camera"],
            "render": ["render"],
        },
    )
    second = engine.ingest_text(
        source_id=source.source_id,
        text=text,
        operation_hints={
            "camera": ["camera"],
            "render": ["render"],
        },
    )
    assert first.duplicate_snapshot is False
    assert first.chunks_created == 2
    assert second.duplicate_snapshot is True
    assert second.snapshot_id == first.snapshot_id
    assert set(second.chunk_ids) == set(first.chunk_ids)


def test_retrieval_and_reviewed_item_keep_exact_provenance(tmp_path: Path):
    engine = _engine(tmp_path)
    source = KnowledgeSource(
        source_id="premiere.test",
        tool_id="premiere",
        title="Premiere source",
        source_uri="https://developer.adobe.com/premiere-pro/uxp/",
        source_tier=SourceTier.OFFICIAL_DOCS,
        source_version="26.x",
        owner=DepartmentId.EDITORIAL,
    )
    engine.register_source(source)
    result = engine.ingest_text(
        source_id=source.source_id,
        text="# Trim\nSet explicit in and out points on timeline track items.",
        operation_hints={"trim": ["in point", "out point", "trim"]},
    )
    hits = engine.retriever.search(
        "trim timeline using in point",
        tool_id="premiere",
        operation="trim",
    )
    assert hits
    assert hits[0].chunk.chunk_id in result.chunk_ids
    item = engine.create_reviewed_item(
        knowledge_id="premiere.reviewed.trim",
        title="Premiere trim",
        body="Use explicit timeline in/out points for deterministic trim operations.",
        chunk_ids=[hits[0].chunk.chunk_id],
        operations={"trim"},
    )
    assert item.tool_id == "premiere"
    assert item.source_snapshot_id == result.snapshot_id
    assert item.source_chunk_ids == [hits[0].chunk.chunk_id]
    assert item.operations == {"trim"}


def test_default_curriculum_covers_all_declared_operations(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    for tool_id in (
        "blender",
        "premiere",
        "ffmpeg",
        "resolve",
        "aftereffects",
        "photoshop",
        "unreal",
        "canva",
        "comfyui",
    ):
        report = operation_coverage(kernel, tool_id)
        assert report.coverage == 1.0, (
            tool_id,
            report.missing_operations,
        )
        assert report.missing_operations == []


def test_curriculum_retrieval_resolves_task_specific_blender_knowledge(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    hits = kernel.knowledge_acquisition.retriever.search(
        "render animation without UI in background mode",
        tool_id="blender",
        operation="headless batch",
        limit=3,
    )
    assert hits
    assert "headless batch" in hits[0].chunk.operations
    assert hits[0].chunk.source_id == "blender.4_5.production_curriculum"


def test_task_resolver_prefers_exact_operation_heading(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    context = ToolTaskKnowledgeResolver(kernel).require(
        tool_id="blender",
        operations=["animation", "render"],
        task="render an animated shot unattended",
    )
    assert context.blocked is False
    assert len(context.chunk_ids) == 2
    assert context.procedures[0].startswith("Animation:")
    assert context.procedures[1].startswith("Render:")


def test_agent_packets_share_one_acquisition_contract(tmp_path: Path):
    engine = _engine(tmp_path)
    for agent_id, source_id in (
        ("chatgpt", "agent.chatgpt.blender"),
        ("codex", "agent.codex.blender"),
        ("claude", "agent.claude.blender"),
    ):
        packet = AgentKnowledgePacket(
            agent_id=agent_id,
            source=KnowledgeSource(
                source_id=source_id,
                tool_id="blender",
                title=f"{agent_id} curated Blender note",
                source_uri="https://docs.blender.org/manual/en/4.5/",
                source_tier=SourceTier.OFFICIAL_DOCS,
                source_version="4.5",
                owner=DepartmentId.TECHNICAL_DIRECTION,
            ),
            content="# Render\nUse explicit render settings and verify the output.",
            operation_hints={"render": ["render"]},
            task="learn Blender render automation",
        )
        result = engine.ingest_agent_packet(packet)
        assert result.chunks_created == 1
        snapshot, _ = engine.store.get_snapshot(result.snapshot_id)
        assert snapshot.metadata["agent_id"] == agent_id
        assert snapshot.metadata["capture_mode"] == "AGENT_SNAPSHOT"


def test_craft_curriculum_resolves_professional_principles(tmp_path: Path):
    kernel = build_studio_kernel(tmp_path)
    resolver = ToolTaskKnowledgeResolver(kernel)
    camera = resolver.require(
        tool_id="craft.cinematography",
        operations=["coverage", "eyeline", "axis", "motivated camera"],
        task="plan dialogue coverage for a two-character dramatic scene",
    )
    acting = resolver.require(
        tool_id="craft.performance",
        operations=["objective", "trigger reaction", "gaze", "pose clarity", "timing"],
        task="direct a surprised Roblox character reaction",
    )
    audio = resolver.require(
        tool_id="craft.audio",
        operations=["dialogue priority", "foley", "music", "loudness", "sync"],
        task="finish a dialogue-heavy scene",
    )
    color = resolver.require(
        tool_id="craft.color",
        operations=["normalization", "shot matching", "look", "scopes", "delivery"],
        task="finish the final sequence consistently",
    )
    assert not camera.blocked
    assert not acting.blocked
    assert not audio.blocked
    assert not color.blocked
    assert len(camera.procedures) == 4
    assert len(acting.procedures) == 5
