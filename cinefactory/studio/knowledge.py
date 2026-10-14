from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from .contracts import DepartmentId, KnowledgeScope, SkillManifest, SkillStatus


class SourceTier(StrEnum):
    OFFICIAL_DOCS = "OFFICIAL_DOCS"
    OFFICIAL_SDK = "OFFICIAL_SDK"
    STANDARD = "STANDARD"
    MAINTAINER_REPO = "MAINTAINER_REPO"
    PEER_REVIEWED = "PEER_REVIEWED"
    TRUSTED_BOOK = "TRUSTED_BOOK"
    TECHNICAL_TUTORIAL = "TECHNICAL_TUTORIAL"
    COMMUNITY = "COMMUNITY"
    UNVERIFIED = "UNVERIFIED"


class KnowledgeKind(StrEnum):
    FACT = "FACT"
    CONVENTION = "CONVENTION"
    HEURISTIC = "HEURISTIC"
    HYPOTHESIS = "HYPOTHESIS"
    PROCEDURE = "PROCEDURE"


class KnowledgeItem(BaseModel):
    knowledge_id: str
    title: str
    body: str
    kind: KnowledgeKind
    source_tier: SourceTier
    source_uri: str | None = None
    source_version: str | None = None
    applicable_versions: list[str] = Field(default_factory=list)
    scope: KnowledgeScope = KnowledgeScope.STUDIO
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    tested: bool = False
    contradictions: list[str] = Field(default_factory=list)
    owner: DepartmentId = DepartmentId.RND
    tool_id: str | None = None
    operations: set[str] = Field(default_factory=set)
    tags: set[str] = Field(default_factory=set)
    source_snapshot_id: str | None = None
    source_chunk_ids: list[str] = Field(default_factory=list)


class ToolEnvironment(BaseModel):
    tool_id: str
    installed: bool
    version: str | None = None
    api_version: str | None = None
    python_version: str | None = None
    gpu_backend: str | None = None
    vram_gb: float | None = None
    executable_path: str | None = None
    capabilities: set[str] = Field(default_factory=set)
    known_issues: list[str] = Field(default_factory=list)
class KnowledgePromotionDecision(BaseModel):
    knowledge_id: str
    promotable: bool
    reasons: list[str] = Field(default_factory=list)


class KnowledgeGate:
    """Fail-closed promotion rules for turning research into studio knowledge."""

    @staticmethod
    def review(item: KnowledgeItem) -> KnowledgePromotionDecision:
        reasons: list[str] = []
        if item.source_tier is SourceTier.UNVERIFIED:
            reasons.append("UNVERIFIED_SOURCE")
        if item.kind in {KnowledgeKind.HEURISTIC, KnowledgeKind.HYPOTHESIS} and not item.tested:
            reasons.append("UNTESTED_NON_FACTUAL_KNOWLEDGE")
        if item.confidence < 0.6:
            reasons.append("LOW_CONFIDENCE")
        if item.contradictions:
            reasons.append("UNRESOLVED_CONTRADICTIONS")
        return KnowledgePromotionDecision(
            knowledge_id=item.knowledge_id,
            promotable=not reasons,
            reasons=reasons,
        )


class SkillCompiler:
    """Converts reviewed knowledge into a candidate skill manifest, never directly into production."""

    def compile_candidate(
        self,
        *,
        skill_id: str,
        version: str,
        owner: DepartmentId,
        craft_domain: str,
        knowledge: list[KnowledgeItem],
        tool_binding: str | None = None,
        commercial_safe: bool | None = None,
        security_reviewed: bool = False,
    ) -> SkillManifest:
        if not knowledge:
            raise ValueError("cannot compile a skill without knowledge")
        rejected = [k.knowledge_id for k in knowledge if not KnowledgeGate.review(k).promotable]
        if rejected:
            raise ValueError("knowledge not promotable: " + ",".join(rejected))
        return SkillManifest(
            skill_id=skill_id,
            version=version,
            owner=owner,
            status=SkillStatus.CANDIDATE,
            craft_domain=craft_domain,
            tool_binding=tool_binding,
            source_type="COMPILED_KNOWLEDGE",
            commercial_safe=commercial_safe,
            security_reviewed=security_reviewed,
            required_evals=[f"{skill_id}.functional", f"{skill_id}.regression"],
            notes=[f"compiled_from={','.join(k.knowledge_id for k in knowledge)}"],
        )


class KnowledgeRegistry:
    """Immutable, version-aware studio knowledge store."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, knowledge_id: str) -> Path:
        safe = knowledge_id.replace("/", "_").replace("\\", "_")
        return self.root / f"{safe}.json"

    def register(self, item: KnowledgeItem) -> Path:
        path = self._path(item.knowledge_id)
        if path.exists():
            existing = KnowledgeItem.model_validate_json(
                path.read_text(encoding="utf-8")
            )
            if existing != item:
                raise FileExistsError(
                    f"immutable knowledge item already exists: {item.knowledge_id}"
                )
            return path
        path.write_text(item.model_dump_json(indent=2), encoding="utf-8")
        return path

    def get(self, knowledge_id: str) -> KnowledgeItem:
        path = self._path(knowledge_id)
        if not path.exists():
            raise KeyError(knowledge_id)
        return KnowledgeItem.model_validate_json(path.read_text(encoding="utf-8"))

    def list(self) -> list[KnowledgeItem]:
        return [
            KnowledgeItem.model_validate_json(path.read_text(encoding="utf-8"))
            for path in sorted(self.root.glob("*.json"))
        ]

    def by_owner(self, owner: DepartmentId) -> list[KnowledgeItem]:
        return [item for item in self.list() if item.owner is owner]
