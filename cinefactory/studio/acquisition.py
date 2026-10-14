from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from pydantic import BaseModel, Field

from .contracts import DepartmentId
from .knowledge import (
    KnowledgeGate,
    KnowledgeItem,
    KnowledgeKind,
    KnowledgeRegistry,
    SourceTier,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CaptureMode(StrEnum):
    AGENT_SNAPSHOT = "AGENT_SNAPSHOT"
    LOCAL_FILE = "LOCAL_FILE"
    USER_SUPPLIED = "USER_SUPPLIED"
    OFFICIAL_EXPORT = "OFFICIAL_EXPORT"
    INTERNAL_STANDARD = "INTERNAL_STANDARD"


class KnowledgeSource(BaseModel):
    source_id: str
    tool_id: str
    title: str
    source_uri: str | None = None
    source_tier: SourceTier
    source_version: str | None = None
    owner: DepartmentId = DepartmentId.RND
    capture_mode: CaptureMode = CaptureMode.AGENT_SNAPSHOT
    enabled: bool = True
    metadata: dict = Field(default_factory=dict)


class KnowledgeSnapshot(BaseModel):
    snapshot_id: str
    source_id: str
    content_sha256: str
    captured_at: datetime = Field(default_factory=utcnow)
    char_count: int
    metadata: dict = Field(default_factory=dict)


class KnowledgeChunk(BaseModel):
    chunk_id: str
    source_id: str
    snapshot_id: str
    tool_id: str
    source_version: str | None = None
    ordinal: int
    heading: str | None = None
    text: str
    operations: set[str] = Field(default_factory=set)
    keywords: set[str] = Field(default_factory=set)


class AgentKnowledgePacket(BaseModel):
    agent_id: str
    source: KnowledgeSource
    content: str
    operation_hints: dict[str, list[str]] = Field(default_factory=dict)
    task: str | None = None
    metadata: dict = Field(default_factory=dict)


class AcquisitionResult(BaseModel):
    source_id: str
    snapshot_id: str
    duplicate_snapshot: bool = False
    chunks_created: int = 0
    chunk_ids: list[str] = Field(default_factory=list)


class RetrievalHit(BaseModel):
    chunk: KnowledgeChunk
    score: float
    reasons: list[str] = Field(default_factory=list)


class OperationCoverage(BaseModel):
    tool_id: str
    required_operations: list[str] = Field(default_factory=list)
    covered_operations: list[str] = Field(default_factory=list)
    missing_operations: list[str] = Field(default_factory=list)
    coverage: float = Field(default=0.0, ge=0.0, le=1.0)


class KnowledgeAcquisitionStore:
    """Durable provenance store for source descriptors, snapshots and chunks."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.sources_dir = self.root / "sources"
        self.snapshots_dir = self.root / "snapshots"
        self.chunks_dir = self.root / "chunks"
        for folder in (self.sources_dir, self.snapshots_dir, self.chunks_dir):
            folder.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value)

    def register_source(self, source: KnowledgeSource) -> Path:
        path = self.sources_dir / f"{self._safe(source.source_id)}.json"
        if path.exists():
            existing = KnowledgeSource.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            if existing != source:
                raise FileExistsError(
                    f"immutable knowledge source already exists: {source.source_id}"
                )
            return path
        path.write_text(source.model_dump_json(indent=2), encoding="utf-8")
        return path

    def get_source(self, source_id: str) -> KnowledgeSource:
        path = self.sources_dir / f"{self._safe(source_id)}.json"
        if not path.exists():
            raise KeyError(source_id)
        return KnowledgeSource.model_validate_json(path.read_text(encoding="utf-8"))

    def list_sources(self) -> list[KnowledgeSource]:
        return [
            KnowledgeSource.model_validate_json(path.read_text(encoding="utf-8"))
            for path in sorted(self.sources_dir.glob("*.json"))
        ]

    def save_snapshot(
        self,
        snapshot: KnowledgeSnapshot,
        content: str,
    ) -> KnowledgeSnapshot:
        base = self.snapshots_dir / self._safe(snapshot.snapshot_id)
        meta = base.with_suffix(".json")
        text = base.with_suffix(".txt")
        if meta.exists():
            return KnowledgeSnapshot.model_validate_json(
                meta.read_text(encoding="utf-8")
            )
        text.write_text(content, encoding="utf-8")
        meta.write_text(snapshot.model_dump_json(indent=2), encoding="utf-8")
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> tuple[KnowledgeSnapshot, str]:
        base = self.snapshots_dir / self._safe(snapshot_id)
        meta = base.with_suffix(".json")
        text = base.with_suffix(".txt")
        if not meta.exists() or not text.exists():
            raise KeyError(snapshot_id)
        return (
            KnowledgeSnapshot.model_validate_json(meta.read_text(encoding="utf-8")),
            text.read_text(encoding="utf-8"),
        )

    def find_snapshot_by_hash(
        self,
        source_id: str,
        content_sha256: str,
    ) -> KnowledgeSnapshot | None:
        for path in self.snapshots_dir.glob("*.json"):
            item = KnowledgeSnapshot.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            if item.source_id == source_id and item.content_sha256 == content_sha256:
                return item
        return None

    def save_chunk(self, chunk: KnowledgeChunk) -> Path:
        path = self.chunks_dir / f"{self._safe(chunk.chunk_id)}.json"
        if path.exists():
            existing = KnowledgeChunk.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            if existing != chunk:
                raise FileExistsError(f"chunk collision: {chunk.chunk_id}")
            return path
        path.write_text(chunk.model_dump_json(indent=2), encoding="utf-8")
        return path

    def list_chunks(
        self,
        *,
        tool_id: str | None = None,
        snapshot_id: str | None = None,
    ) -> list[KnowledgeChunk]:
        result: list[KnowledgeChunk] = []
        for path in sorted(self.chunks_dir.glob("*.json")):
            item = KnowledgeChunk.model_validate_json(path.read_text(encoding="utf-8"))
            if tool_id and item.tool_id != tool_id:
                continue
            if snapshot_id and item.snapshot_id != snapshot_id:
                continue
            result.append(item)
        return result


class KnowledgeChunker:
    """Heading-aware, deterministic chunking without requiring an LLM."""

    TOKEN_RE = re.compile(r"[A-Za-z0-9_./:+-]{2,}")

    def __init__(self, max_chars: int = 2200) -> None:
        self.max_chars = max_chars

    @classmethod
    def keywords(cls, text: str) -> set[str]:
        return {
            token.lower()
            for token in cls.TOKEN_RE.findall(text)
            if len(token) >= 3
        }

    @staticmethod
    def _sections(text: str) -> list[tuple[str | None, str]]:
        lines = text.replace("\r\n", "\n").split("\n")
        sections: list[tuple[str | None, list[str]]] = []
        heading: str | None = None
        body: list[str] = []
        for line in lines:
            match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
            if match:
                if body:
                    sections.append((heading, body))
                    body = []
                heading = match.group(1).strip()
            else:
                body.append(line)
        if body or heading:
            sections.append((heading, body))
        return [
            (title, "\n".join(lines_).strip())
            for title, lines_ in sections
            if "\n".join(lines_).strip()
        ]

    def split(
        self,
        *,
        source: KnowledgeSource,
        snapshot: KnowledgeSnapshot,
        text: str,
        operation_hints: dict[str, list[str]] | None = None,
    ) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        ordinal = 0
        hints = operation_hints or {}
        for heading, body in self._sections(text):
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
            buffer = ""
            for paragraph in paragraphs:
                candidate = paragraph if not buffer else f"{buffer}\n\n{paragraph}"
                if len(candidate) <= self.max_chars:
                    buffer = candidate
                    continue
                if buffer:
                    chunks.append(
                        self._make_chunk(
                            source, snapshot, heading, buffer, ordinal, hints
                        )
                    )
                    ordinal += 1
                if len(paragraph) <= self.max_chars:
                    buffer = paragraph
                    continue
                start = 0
                while start < len(paragraph):
                    piece = paragraph[start : start + self.max_chars].strip()
                    if piece:
                        chunks.append(
                            self._make_chunk(
                                source, snapshot, heading, piece, ordinal, hints
                            )
                        )
                        ordinal += 1
                    start += self.max_chars
                buffer = ""
            if buffer:
                chunks.append(
                    self._make_chunk(source, snapshot, heading, buffer, ordinal, hints)
                )
                ordinal += 1
        return chunks

    def _make_chunk(
        self,
        source: KnowledgeSource,
        snapshot: KnowledgeSnapshot,
        heading: str | None,
        text: str,
        ordinal: int,
        operation_hints: dict[str, list[str]],
    ) -> KnowledgeChunk:
        searchable = f"{heading or ''} {text}".lower()
        operations: set[str] = set()
        for operation, aliases in operation_hints.items():
            phrases = [operation, *aliases]
            if any(phrase.lower() in searchable for phrase in phrases):
                operations.add(operation)
        digest = hashlib.sha256(
            f"{snapshot.snapshot_id}:{ordinal}:{text}".encode("utf-8")
        ).hexdigest()[:16]
        return KnowledgeChunk(
            chunk_id=f"KCH_{digest}",
            source_id=source.source_id,
            snapshot_id=snapshot.snapshot_id,
            tool_id=source.tool_id,
            source_version=source.source_version,
            ordinal=ordinal,
            heading=heading,
            text=text,
            operations=operations,
            keywords=self.keywords(searchable),
        )


class KnowledgeRetriever:
    def __init__(self, store: KnowledgeAcquisitionStore) -> None:
        self.store = store

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return KnowledgeChunker.keywords(text)

    def search(
        self,
        query: str,
        *,
        tool_id: str | None = None,
        operation: str | None = None,
        limit: int = 8,
    ) -> list[RetrievalHit]:
        query_tokens = self._tokens(query)
        hits: list[RetrievalHit] = []
        for chunk in self.store.list_chunks(tool_id=tool_id):
            overlap = query_tokens & chunk.keywords
            score = float(len(overlap))
            reasons: list[str] = []
            if overlap:
                reasons.append(f"token_overlap={len(overlap)}")
            if operation and operation in chunk.operations:
                score += 5.0
                reasons.append("operation_match")
            if tool_id and chunk.tool_id == tool_id:
                score += 1.0
                reasons.append("tool_match")
            if score <= 0:
                continue
            hits.append(RetrievalHit(chunk=chunk, score=score, reasons=reasons))
        return sorted(
            hits,
            key=lambda hit: (-hit.score, hit.chunk.ordinal, hit.chunk.chunk_id),
        )[:limit]


class KnowledgeAcquisitionEngine:
    """Ingest immutable source snapshots and expose reviewed promotion to KnowledgeRegistry."""

    def __init__(
        self,
        store: KnowledgeAcquisitionStore,
        registry: KnowledgeRegistry,
    ) -> None:
        self.store = store
        self.registry = registry
        self.chunker = KnowledgeChunker()
        self.retriever = KnowledgeRetriever(store)

    def register_source(self, source: KnowledgeSource) -> KnowledgeSource:
        self.store.register_source(source)
        return source

    def ingest_text(
        self,
        *,
        source_id: str,
        text: str,
        operation_hints: dict[str, list[str]] | None = None,
        metadata: dict | None = None,
    ) -> AcquisitionResult:
        source = self.store.get_source(source_id)
        if not source.enabled:
            raise ValueError(f"source disabled: {source_id}")
        normalized = text.replace("\r\n", "\n").strip()
        if not normalized:
            raise ValueError("cannot ingest empty knowledge source")
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
        existing = self.store.find_snapshot_by_hash(source_id, digest)
        if existing:
            chunks = self.store.list_chunks(snapshot_id=existing.snapshot_id)
            return AcquisitionResult(
                source_id=source_id,
                snapshot_id=existing.snapshot_id,
                duplicate_snapshot=True,
                chunks_created=0,
                chunk_ids=[item.chunk_id for item in chunks],
            )
        identity_digest = hashlib.sha256(
            f"{source_id}:{digest}".encode("utf-8")
        ).hexdigest()
        snapshot = KnowledgeSnapshot(
            snapshot_id=f"KSN_{identity_digest[:16]}",
            source_id=source_id,
            content_sha256=digest,
            char_count=len(normalized),
            metadata=metadata or {},
        )
        self.store.save_snapshot(snapshot, normalized)
        chunks = self.chunker.split(
            source=source,
            snapshot=snapshot,
            text=normalized,
            operation_hints=operation_hints,
        )
        for chunk in chunks:
            self.store.save_chunk(chunk)
        return AcquisitionResult(
            source_id=source_id,
            snapshot_id=snapshot.snapshot_id,
            chunks_created=len(chunks),
            chunk_ids=[item.chunk_id for item in chunks],
        )

    def ingest_agent_packet(
        self,
        packet: AgentKnowledgePacket,
    ) -> AcquisitionResult:
        source = packet.source.model_copy(
            update={"capture_mode": CaptureMode.AGENT_SNAPSHOT}
        )
        try:
            self.register_source(source)
        except FileExistsError:
            if self.store.get_source(source.source_id) != source:
                raise
        metadata = {
            **packet.metadata,
            "agent_id": packet.agent_id,
            "task": packet.task,
            "capture_mode": CaptureMode.AGENT_SNAPSHOT.value,
        }
        return self.ingest_text(
            source_id=source.source_id,
            text=packet.content,
            operation_hints=packet.operation_hints,
            metadata=metadata,
        )

    def ingest_file(
        self,
        *,
        source_id: str,
        path: str | Path,
        operation_hints: dict[str, list[str]] | None = None,
    ) -> AcquisitionResult:
        source = self.store.get_source(source_id)
        file_path = Path(path)
        if not file_path.is_file():
            raise FileNotFoundError(file_path)
        if file_path.suffix.lower() not in {".txt", ".md", ".rst", ".json"}:
            raise ValueError(
                "unsupported knowledge file type; materialize/extract text first"
            )
        return self.ingest_text(
            source_id=source.source_id,
            text=file_path.read_text(encoding="utf-8"),
            operation_hints=operation_hints,
            metadata={
                "local_path": str(file_path),
                "capture_mode": CaptureMode.LOCAL_FILE.value,
            },
        )

    def create_reviewed_item(
        self,
        *,
        knowledge_id: str,
        title: str,
        body: str,
        chunk_ids: list[str],
        kind: KnowledgeKind = KnowledgeKind.PROCEDURE,
        operations: set[str] | None = None,
        confidence: float = 0.9,
        tested: bool = False,
    ) -> KnowledgeItem:
        if not chunk_ids:
            raise ValueError("reviewed knowledge requires source chunks")
        chunk_map = {
            chunk.chunk_id: chunk
            for chunk in self.store.list_chunks()
            if chunk.chunk_id in set(chunk_ids)
        }
        if len(chunk_map) != len(set(chunk_ids)):
            raise KeyError("one or more source chunks do not exist")
        chunks = [chunk_map[item] for item in chunk_ids]
        source_ids = {chunk.source_id for chunk in chunks}
        if len(source_ids) != 1:
            raise ValueError("one knowledge item must cite chunks from one source")
        source = self.store.get_source(next(iter(source_ids)))
        merged_operations = set(operations or set())
        for chunk in chunks:
            merged_operations.update(chunk.operations)
        item = KnowledgeItem(
            knowledge_id=knowledge_id,
            title=title,
            body=body,
            kind=kind,
            source_tier=source.source_tier,
            source_uri=source.source_uri,
            source_version=source.source_version,
            applicable_versions=[source.source_version]
            if source.source_version
            else [],
            confidence=confidence,
            tested=tested,
            owner=source.owner,
            tool_id=source.tool_id,
            operations=merged_operations,
            source_snapshot_id=chunks[0].snapshot_id,
            source_chunk_ids=chunk_ids,
        )
        decision = KnowledgeGate.review(item)
        if not decision.promotable:
            raise ValueError(
                "knowledge not promotable: " + ",".join(decision.reasons)
            )
        self.registry.register(item)
        return item


def operation_coverage(kernel, tool_id: str) -> OperationCoverage:
    specs = kernel.tool_skills.list(tool_id)
    required = sorted(
        {
            operation
            for spec in specs
            for operation in spec.operations
        }
    )
    covered = sorted(
        {
            operation
            for item in kernel.knowledge.list()
            if item.tool_id == tool_id
            for operation in item.operations
        }
    )
    missing = sorted(set(required) - set(covered))
    return OperationCoverage(
        tool_id=tool_id,
        required_operations=required,
        covered_operations=covered,
        missing_operations=missing,
        coverage=(len(set(required) & set(covered)) / len(required))
        if required
        else 1.0,
    )


class ToolKnowledgeContext(BaseModel):
    tool_id: str
    task: str
    operations: list[str] = Field(default_factory=list)
    chunk_ids: list[str] = Field(default_factory=list)
    procedures: list[str] = Field(default_factory=list)
    missing_operations: list[str] = Field(default_factory=list)
    blocked: bool = False


class ToolTaskKnowledgeResolver:
    """Resolve the minimum relevant procedures before executing a tool operation."""

    def __init__(self, kernel) -> None:
        self.kernel = kernel

    def resolve(
        self,
        *,
        tool_id: str,
        operations: Iterable[str],
        task: str,
        strict: bool = True,
    ) -> ToolKnowledgeContext:
        required = list(dict.fromkeys(operations))
        chunk_ids: list[str] = []
        procedures: list[str] = []
        missing: list[str] = []
        for operation in required:
            hits = self.kernel.knowledge_acquisition.retriever.search(
                f"{task} {operation}",
                tool_id=tool_id,
                operation=operation,
                limit=3,
            )
            operation_hits = [
                hit for hit in hits if operation in hit.chunk.operations
            ]
            if not operation_hits:
                missing.append(operation)
                continue
            operation_hits.sort(
                key=lambda hit: (
                    0
                    if (hit.chunk.heading or "").strip().lower()
                    == operation.strip().lower()
                    else 1,
                    -hit.score,
                    hit.chunk.ordinal,
                )
            )
            best = operation_hits[0].chunk
            if best.chunk_id not in chunk_ids:
                chunk_ids.append(best.chunk_id)
                heading = best.heading or operation
                procedures.append(f"{heading}: {best.text}")
        return ToolKnowledgeContext(
            tool_id=tool_id,
            task=task,
            operations=required,
            chunk_ids=chunk_ids,
            procedures=procedures,
            missing_operations=missing,
            blocked=bool(missing) and strict,
        )

    def require(
        self,
        *,
        tool_id: str,
        operations: Iterable[str],
        task: str,
    ) -> ToolKnowledgeContext:
        context = self.resolve(
            tool_id=tool_id,
            operations=operations,
            task=task,
            strict=True,
        )
        if context.blocked:
            raise RuntimeError(
                f"TOOL_KNOWLEDGE_GAP:{tool_id}:"
                + ",".join(context.missing_operations)
            )
        return context
