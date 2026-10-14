from __future__ import annotations

import hashlib
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ModelManifest(BaseModel):
    model_id: str
    revision: str
    modality: str
    local_path: str | None = None
    code_license: str | None = None
    weights_license: str | None = None
    commercial_use_reviewed: bool = False
    output_terms_reviewed: bool = False
    approved_for_production: bool = False
    notes: list[str] = Field(default_factory=list)


class ModelRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.items: dict[
            tuple[str, str],
            ModelManifest,
        ] = {}

    def load(self):
        self.items = {}
        if not self.path.exists():
            return self
        raw = yaml.safe_load(
            self.path.read_text(encoding="utf-8")
        ) or {}
        for item in raw.get("models", []):
            model = ModelManifest.model_validate(item)
            self.items[
                (model.model_id, model.revision)
            ] = model
        return self

    def get(
        self,
        model_id: str,
        revision: str,
    ) -> ModelManifest:
        try:
            return self.items[(model_id, revision)]
        except KeyError as exc:
            raise KeyError(
                f"Unknown model {model_id}@{revision}"
            ) from exc

    def require_approved(
        self,
        model_id: str,
        revision: str,
    ) -> ModelManifest:
        model = self.get(model_id, revision)
        if not (
            model.approved_for_production
            and model.commercial_use_reviewed
            and model.output_terms_reviewed
        ):
            raise RuntimeError(
                "Model not approved for production: "
                f"{model_id}@{revision}"
            )
        return model

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(
                lambda: fh.read(1024 * 1024),
                b"",
            ):
                h.update(chunk)
        return h.hexdigest()

    def promote_for_production(
        self,
        model_id: str,
        revision: str,
        *,
        root: str | Path,
        evidence_ref: str,
        expected_sha256: str | None = None,
    ) -> ModelManifest:
        """Persist a production approval only after deterministic evidence.

        This method intentionally does not decide whether the evidence is
        sufficient. The caller must be an approved qualification controller.
        It enforces registry-level invariants: rights/output reviews, local
        artifact existence and exact content identity.
        """
        model = self.get(model_id, revision)
        blockers: list[str] = []
        if not model.commercial_use_reviewed:
            blockers.append(
                "MODEL_COMMERCIAL_USE_NOT_REVIEWED"
            )
        if not model.output_terms_reviewed:
            blockers.append(
                "MODEL_OUTPUT_TERMS_NOT_REVIEWED"
            )
        if not model.local_path:
            blockers.append(
                "MODEL_LOCAL_PATH_MISSING"
            )
            artifact = None
        else:
            artifact = (
                Path(root)
                / model.local_path
            ).resolve()
            if not artifact.is_file():
                blockers.append(
                    "MODEL_LOCAL_ARTIFACT_MISSING"
                )

        digest = None
        if artifact is not None and artifact.is_file():
            digest = self._sha256(artifact)
        pinned = expected_sha256
        if pinned is None and revision.startswith(
            "sha256:"
        ):
            pinned = revision.removeprefix(
                "sha256:"
            )
        if pinned:
            if digest is None:
                blockers.append(
                    "MODEL_HASH_NOT_MEASURED"
                )
            elif digest.lower() != pinned.lower():
                blockers.append(
                    "MODEL_HASH_MISMATCH"
                )
        if not evidence_ref:
            blockers.append(
                "MODEL_QUALIFICATION_EVIDENCE_MISSING"
            )
        if blockers:
            raise RuntimeError(
                "MODEL_PRODUCTION_PROMOTION_BLOCKED:"
                + ",".join(sorted(set(blockers)))
            )

        evidence_note = (
            "Production qualification evidence: "
            + evidence_ref
        )
        notes = [
            note
            for note in model.notes
            if not str(note).lower().startswith(
                "production approval remains false until"
            )
        ]
        if evidence_note not in notes:
            notes.append(evidence_note)
        promoted = model.model_copy(
            update={
                "approved_for_production": True,
                "notes": notes,
            }
        )
        self.items[
            (model_id, revision)
        ] = promoted
        self._persist()
        return promoted

    def _persist(self) -> None:
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        rows = [
            self.items[key].model_dump(
                mode="json"
            )
            for key in sorted(self.items)
        ]
        self.path.write_text(
            yaml.safe_dump(
                {"models": rows},
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )
