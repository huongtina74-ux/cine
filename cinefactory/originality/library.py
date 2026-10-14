from __future__ import annotations

import json
from pathlib import Path

from cinefactory.discovery.models import TopicStrategy
from cinefactory.domain.models import ScriptSpec, ShotSpecBatch, StorySpec
from cinefactory.originality.concept import fingerprint_from_project
from cinefactory.originality.models import ConceptFingerprint, DifferentiationPlan, ReferenceKind, ReferenceRecord


class ReferenceLibrary:
    """Local reference corpus used only for collision detection and negative constraints.

    Competitor/source raw text is quarantined here. Creative reasoning must never receive
    ``raw_text`` or exact competitor packaging/beat text from this store.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def add(self, record: ReferenceRecord) -> Path:
        path = self.root / f"{record.reference_id}.json"
        if path.exists():
            raise FileExistsError(path)
        path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
        return path

    def get(self, reference_id: str) -> ReferenceRecord:
        return ReferenceRecord.model_validate_json((self.root / f"{reference_id}.json").read_text(encoding="utf-8"))

    def list(self, kinds: set[ReferenceKind] | None = None) -> list[ReferenceRecord]:
        out: list[ReferenceRecord] = []
        for path in sorted(self.root.glob("REF_*.json")):
            record = ReferenceRecord.model_validate_json(path.read_text(encoding="utf-8"))
            if kinds is None or record.kind in kinds:
                out.append(record)
        return out

    def import_text(
        self,
        path: str | Path,
        *,
        kind: ReferenceKind,
        title: str | None = None,
        source_url: str | None = None,
        idea_summary: str | None = None,
        hook_summary: str | None = None,
        structure_beats: list[str] | None = None,
        concept_fingerprint: ConceptFingerprint | None = None,
        collision_tags: list[str] | None = None,
    ) -> ReferenceRecord:
        src = Path(path)
        record = ReferenceRecord(
            kind=kind,
            title=title or src.stem,
            source_url=source_url,
            raw_text=src.read_text(encoding="utf-8"),
            idea_summary=idea_summary,
            hook_summary=hook_summary,
            structure_beats=structure_beats or [],
            concept_fingerprint=concept_fingerprint,
            collision_tags=collision_tags or [],
        )
        self.add(record)
        return record


def _latest_payload(project: Path, stage: str) -> tuple[str | None, dict | None]:
    folder = project / "creative" / stage
    latest = folder / "LATEST"
    if not latest.exists():
        return None, None
    try:
        version = int(latest.read_text(encoding="utf-8").strip())
        envelope = json.loads((folder / f"v{version}.json").read_text(encoding="utf-8"))
        return envelope.get("schema"), envelope.get("payload", {})
    except Exception:
        return None, None


def _latest_schema_payload(project: Path, stage: str, schema_name: str) -> dict | None:
    folder = project / "creative" / stage
    if not folder.exists():
        return None
    versions = sorted(
        [p for p in folder.glob("v*.json") if p.stem.removeprefix("v").isdigit()],
        key=lambda p: int(p.stem.removeprefix("v")),
        reverse=True,
    )
    for path in versions:
        try:
            envelope = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if envelope.get("schema") == schema_name:
            return envelope.get("payload", {})
    return None


def _story_text(story: StorySpec) -> str:
    return "\n".join([
        story.title,
        story.premise,
        story.theme or "",
        story.protagonist_goal,
        story.central_conflict,
        story.ending_state,
        *[f"{b.purpose}: {b.change}. {b.audience_question or ''}" for b in story.beats],
    ])


def _script_text(script: ScriptSpec) -> str:
    chunks = [script.title, script.logline]
    for scene in script.scenes:
        chunks.extend([scene.heading, scene.dramatic_event, *scene.action])
        chunks.extend(line.text for line in scene.dialogue)
    return "\n".join(chunks)


def prior_project_references(projects_root: str | Path, *, exclude_project_id: str | None = None) -> list[ReferenceRecord]:
    """Build ephemeral PRIOR_OWN references from existing CineFactory projects.

    The fingerprint includes story semantics and, when available, the project's shot grammar.
    This protects against YouTube-style self-repetition where uploads become interchangeable
    even though the surface wording changed.
    """
    root = Path(projects_root)
    records: list[ReferenceRecord] = []
    if not root.exists():
        return records

    for project in sorted(p for p in root.iterdir() if p.is_dir()):
        if exclude_project_id and project.name == exclude_project_id:
            continue

        _, story_payload = _latest_payload(project, "story")
        _, script_payload = _latest_payload(project, "script")
        if not story_payload and not script_payload:
            continue

        story = StorySpec.model_validate(story_payload) if story_payload else None
        script = ScriptSpec.model_validate(script_payload) if script_payload else None
        strategy_payload = _latest_schema_payload(project, "topic_strategy", "TopicStrategy")
        diff_payload = _latest_schema_payload(project, "originality", "DifferentiationPlan")
        shots_payload = _latest_schema_payload(project, "shot_spec", "ShotSpecBatch")

        strategy = TopicStrategy.model_validate(strategy_payload) if strategy_payload else None
        diff = DifferentiationPlan.model_validate(diff_payload) if diff_payload else None
        shots = ShotSpecBatch.model_validate(shots_payload).shots if shots_payload else []

        raw_chunks: list[str] = []
        title = project.name
        idea_summary: str | None = None
        structure: list[str] = []
        fingerprint: ConceptFingerprint | None = None

        if story:
            title = story.title
            raw_chunks.append(_story_text(story))
            idea_summary = " ".join([story.premise, story.protagonist_goal, story.central_conflict, story.ending_state])
            structure = [f"{b.purpose}:{b.change}" for b in story.beats]
            fingerprint = fingerprint_from_project(story, strategy=strategy, differentiation=diff, shots=shots)
        if script:
            raw_chunks.append(_script_text(script))

        release_path = project / "release" / "package.json"
        packaging_notes: list[str] = []
        if release_path.exists():
            try:
                release = json.loads(release_path.read_text(encoding="utf-8"))
                packaging_notes = [
                    str(release.get("final_title") or ""),
                    str(release.get("thumbnail_concept") or ""),
                ]
            except Exception:
                pass

        records.append(ReferenceRecord(
            reference_id=f"OWN_{project.name}",
            kind=ReferenceKind.PRIOR_OWN,
            title=title,
            raw_text="\n".join(raw_chunks),
            idea_summary=idea_summary,
            structure_beats=structure,
            packaging_notes=[x for x in packaging_notes if x],
            concept_fingerprint=fingerprint,
            collision_tags=["prior-own-channel-content"],
            metadata={"project_id": project.name},
        ))
    return records
