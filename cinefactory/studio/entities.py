from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class EntityKind(StrEnum):
    CHARACTER = "CHARACTER"
    PRESENTER = "PRESENTER"
    PRODUCT = "PRODUCT"
    BRAND = "BRAND"
    LOCATION = "LOCATION"
    PROP = "PROP"
    VEHICLE = "VEHICLE"
    UI = "UI"
    DATA_SERIES = "DATA_SERIES"
    WORLD = "WORLD"


class EntityRepresentation(BaseModel):
    representation_id: str
    backend: str
    asset_ref: str | None = None
    identity_constraints: dict[str, Any] = Field(default_factory=dict)
    state: dict[str, Any] = Field(default_factory=dict)
    verified: bool = False


class PersistentEntity(BaseModel):
    entity_id: str
    kind: EntityKind
    canonical_name: str
    identity_lock: str | dict[str, Any] = Field(default_factory=dict)
    continuity_state: dict[str, Any] = Field(default_factory=dict)
    representations: list[EntityRepresentation] = Field(default_factory=list)

    @model_validator(mode="after")
    def representation_ids_unique(self) -> "PersistentEntity":
        ids = [x.representation_id for x in self.representations]
        if len(ids) != len(set(ids)):
            raise ValueError("representation_id values must be unique")
        return self


class EntityRegistry(BaseModel):
    entities: list[PersistentEntity] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_entity_ids(self) -> "EntityRegistry":
        ids = [item.entity_id for item in self.entities]
        if len(ids) != len(set(ids)):
            raise ValueError("entity_id values must be unique")
        return self

    def register(self, entity: PersistentEntity) -> None:
        existing = next((x for x in self.entities if x.entity_id == entity.entity_id), None)
        if existing is not None:
            if existing.kind != entity.kind:
                raise ValueError("entity kind cannot change")
            raise ValueError("entity already exists")
        self.entities.append(entity)

    def get(self, entity_id: str) -> PersistentEntity:
        for item in self.entities:
            if item.entity_id == entity_id:
                return item
        raise KeyError(entity_id)

    def update_state(self, entity_id: str, **state: Any) -> PersistentEntity:
        item = self.get(entity_id)
        item.continuity_state.update(state)
        return item

    def add_representation(self, entity_id: str, representation: EntityRepresentation) -> PersistentEntity:
        item = self.get(entity_id)
        if any(x.representation_id == representation.representation_id for x in item.representations):
            raise ValueError("representation already exists")
        item.representations.append(representation)
        return item
