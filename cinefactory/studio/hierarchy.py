from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ContentNodeKind(StrEnum):
    PROJECT = "PROJECT"
    ACT = "ACT"
    SECTION = "SECTION"
    SEQUENCE = "SEQUENCE"
    SCENE = "SCENE"
    CONTENT_UNIT = "CONTENT_UNIT"
    BEAT = "BEAT"
    EVENT = "EVENT"
    SEGMENT = "SEGMENT"
    SHOT = "SHOT"
    FRAME_EVENT = "FRAME_EVENT"


ALLOWED_CHILDREN: dict[ContentNodeKind, set[ContentNodeKind]] = {
    ContentNodeKind.PROJECT: {
        ContentNodeKind.ACT, ContentNodeKind.SECTION, ContentNodeKind.SEQUENCE,
        ContentNodeKind.CONTENT_UNIT,
    },
    ContentNodeKind.ACT: {ContentNodeKind.SEQUENCE, ContentNodeKind.SCENE, ContentNodeKind.CONTENT_UNIT},
    ContentNodeKind.SECTION: {ContentNodeKind.SEQUENCE, ContentNodeKind.SCENE, ContentNodeKind.CONTENT_UNIT},
    ContentNodeKind.SEQUENCE: {ContentNodeKind.SCENE, ContentNodeKind.CONTENT_UNIT},
    ContentNodeKind.SCENE: {ContentNodeKind.BEAT, ContentNodeKind.EVENT, ContentNodeKind.SHOT},
    ContentNodeKind.CONTENT_UNIT: {
        ContentNodeKind.BEAT, ContentNodeKind.EVENT, ContentNodeKind.SEGMENT, ContentNodeKind.SHOT,
    },
    ContentNodeKind.BEAT: {ContentNodeKind.SHOT},
    ContentNodeKind.EVENT: {ContentNodeKind.SHOT},
    ContentNodeKind.SEGMENT: {ContentNodeKind.SHOT},
    ContentNodeKind.SHOT: {ContentNodeKind.FRAME_EVENT},
    ContentNodeKind.FRAME_EVENT: set(),
}


class ContentNode(BaseModel):
    node_id: str
    kind: ContentNodeKind
    title: str
    parent_id: str | None = None
    order: int = Field(default=0, ge=0)
    intent: dict[str, Any] = Field(default_factory=dict)
    override_fields: set[str] = Field(default_factory=set)


class CreativeIntentHierarchy:
    def __init__(self) -> None:
        self._nodes: dict[str, ContentNode] = {}

    def add(self, node: ContentNode) -> None:
        if node.node_id in self._nodes:
            raise ValueError(f"node exists: {node.node_id}")
        if node.parent_id is None:
            if node.kind is not ContentNodeKind.PROJECT:
                raise ValueError("only PROJECT can be a hierarchy root")
        else:
            parent = self._nodes.get(node.parent_id)
            if parent is None:
                raise KeyError(f"missing parent: {node.parent_id}")
            if node.kind not in ALLOWED_CHILDREN[parent.kind]:
                raise ValueError(f"{node.kind.value} cannot be child of {parent.kind.value}")
        self._nodes[node.node_id] = node

    def get(self, node_id: str) -> ContentNode:
        return self._nodes[node_id]

    def lineage(self, node_id: str) -> list[ContentNode]:
        out: list[ContentNode] = []
        current = self._nodes[node_id]
        while True:
            out.append(current)
            if current.parent_id is None:
                break
            current = self._nodes[current.parent_id]
        return list(reversed(out))

    def effective_intent(self, node_id: str) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for node in self.lineage(node_id):
            for key, value in node.intent.items():
                if key not in result or key in node.override_fields or node.parent_id is None:
                    result[key] = value
        return result

    def ordered_children(self, node_id: str) -> list[ContentNode]:
        return sorted(
            [n for n in self._nodes.values() if n.parent_id == node_id],
            key=lambda n: (n.order, n.node_id),
        )
