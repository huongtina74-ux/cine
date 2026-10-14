from __future__ import annotations

import hashlib
import json
import re
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from cinefactory.domain.models import (
    DialogueLine,
    ScriptScene,
    ScriptSpec,
    StoryBeat,
    StorySpec,
)

from .contracts import PlanningInputKind, PlanningInputRef


class ScriptSourceMode(StrEnum):
    PROMPT_FALLBACK = "PROMPT_FALLBACK"
    LOCKED_SCRIPT = "LOCKED_SCRIPT"
    OUTLINE = "OUTLINE"


class ScriptRevisionPolicy(StrEnum):
    LOCK = "LOCK"
    POLISH = "POLISH"
    ADAPT = "ADAPT"


class ReferenceScriptAnalysis(BaseModel):
    input_id: str
    content_sha256: str
    approximate_word_count: int = 0
    scene_count: int = 0
    dialogue_block_count: int = 0
    dialogue_word_ratio: float = 0.0
    average_scene_words: float | None = None
    structure_patterns: list[str] = Field(default_factory=list)
    raw_expression_allowed: bool = False


class ScriptProductionProfile(BaseModel):
    scene_count: int = Field(default=0, ge=0)
    location_count: int = Field(default=0, ge=0)
    speaker_count: int = Field(default=0, ge=0)
    dialogue_line_count: int = Field(default=0, ge=0)
    dialogue_word_count: int = Field(default=0, ge=0)
    action_block_count: int = Field(default=0, ge=0)
    action_word_count: int = Field(default=0, ge=0)
    dialogue_density: float = Field(default=0.0, ge=0.0, le=1.0)
    estimated_dialogue_seconds: float = Field(default=0.0, ge=0.0)
    estimated_action_seconds: float = Field(default=0.0, ge=0.0)
    estimated_duration_seconds: float = Field(default=0.0, ge=0.0)
    duration_estimate_basis: str = "heuristic_only"
    performance_load: float = Field(default=0.0, ge=0.0, le=1.0)
    continuity_load: float = Field(default=0.0, ge=0.0, le=1.0)
    dialogue_present: bool = False
    multi_character_dialogue: bool = False
    reusable_location_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    planning_signals: list[str] = Field(default_factory=list)


class ScriptSourcePack(BaseModel):
    mode: ScriptSourceMode = ScriptSourceMode.PROMPT_FALLBACK
    revision_policy: ScriptRevisionPolicy = ScriptRevisionPolicy.LOCK
    primary_input_id: str | None = None
    primary_content_sha256: str | None = None
    source_format: str | None = None
    compiled_script: dict[str, Any] | None = None
    compiled_story: dict[str, Any] | None = None
    production_profile: ScriptProductionProfile | None = None
    reference_script_patterns: list[str] = Field(default_factory=list)
    reference_script_analyses: list[ReferenceScriptAnalysis] = Field(
        default_factory=list
    )
    supplemental_script_hashes: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    raw_reference_expression_allowed: bool = False


class ScriptInputCompiler:
    """Compile user-owned scripts/outlines while quarantining reference scripts."""

    _SCENE_HEADING = re.compile(
        r"^(?:"
        r"INT\.?|EXT\.?|INT\.?/EXT\.?|EXT\.?/INT\.?|I/E\.?|"
        r"NỘI\.?|NGOẠI\.?|NỘI/NGOẠI\.?|NGOẠI/NỘI\.?|"
        r"CANH\s+\d+|CẢNH\s+\d+|SCENE\s+\d+"
        r")\b",
        re.IGNORECASE,
    )
    _MARKDOWN_SCENE = re.compile(
        r"^#{1,4}\s+.+$",
        re.IGNORECASE,
    )
    _NUMBERED_SCENE = re.compile(
        r"^(?:\d+[.)]|(?:SCENE|CẢNH|CANH)\s+\d+[:.)]?)\s+.+$",
        re.IGNORECASE,
    )
    _BULLET = re.compile(r"^(?:[-*•]|\d+[.)])\s+(.+)$")

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.quarantine = (
            self.root
            / "data"
            / "studio"
            / "script_intelligence"
            / "quarantine"
        )
        self.safe_root = (
            self.root
            / "data"
            / "studio"
            / "script_intelligence"
            / "safe"
        )
        self.quarantine.mkdir(parents=True, exist_ok=True)
        self.safe_root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _resolve_content(
        self,
        item: PlanningInputRef,
    ) -> tuple[str, str]:
        inline = (item.content or "").lstrip("\ufeff").strip()
        if not inline:
            inline = (
                str(item.metadata.get("content") or "")
                .lstrip("\ufeff")
                .strip()
            )
        if inline:
            return inline, "inline"

        if not item.uri:
            raise ValueError(
                f"SCRIPT_CONTENT_MISSING:{item.input_id}"
            )
        uri = item.uri.strip()
        if uri.startswith(("http://", "https://")):
            raise ValueError(
                f"REMOTE_SCRIPT_URI_NOT_SUPPORTED:{item.input_id}"
            )
        if uri.startswith("file://"):
            uri = uri[7:]
        path = Path(uri).expanduser()
        if not path.is_absolute():
            path = (self.root / path).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.suffix.lower() not in {
            ".txt",
            ".md",
            ".markdown",
            ".fountain",
            ".json",
        }:
            raise ValueError(
                f"SCRIPT_FORMAT_UNSUPPORTED:{path.suffix.lower()}"
            )
        return (
            path.read_text(
                encoding="utf-8-sig",
                errors="ignore",
            ).lstrip("\ufeff"),
            path.suffix.lower().lstrip(".") or "text",
        )

    @staticmethod
    def _revision_policy(item: PlanningInputRef) -> ScriptRevisionPolicy:
        raw = str(
            item.metadata.get("revision_policy") or "LOCK"
        ).upper()
        try:
            return ScriptRevisionPolicy(raw)
        except ValueError:
            return ScriptRevisionPolicy.LOCK

    @classmethod
    def _is_scene_heading(cls, line: str) -> bool:
        value = line.strip()
        return bool(
            cls._SCENE_HEADING.match(value)
            or cls._MARKDOWN_SCENE.match(value)
            or cls._NUMBERED_SCENE.match(value)
        )

    @staticmethod
    def _is_speaker(line: str) -> bool:
        value = line.strip()
        if not value or len(value) > 48:
            return False
        if value.startswith(("(", "[", "{")):
            return False
        letters = [char for char in value if char.isalpha()]
        return bool(letters) and value.upper() == value

    @staticmethod
    def _time_of_day(heading: str) -> str:
        upper = heading.upper()
        for token in (
            "NIGHT",
            "DAY",
            "MORNING",
            "EVENING",
            "AFTERNOON",
            "DAWN",
            "DUSK",
            "ĐÊM",
            "NGÀY",
            "SÁNG",
            "CHIỀU",
            "TỐI",
        ):
            if token in upper:
                return token
        return "UNSPECIFIED"

    @staticmethod
    def _clean_heading(line: str) -> str:
        return re.sub(r"^#{1,4}\s+", "", line.strip())

    @staticmethod
    def _script_title(
        item: PlanningInputRef,
        lines: list[str],
    ) -> str:
        if item.title and item.title.strip():
            return item.title.strip()
        for line in lines[:8]:
            stripped = line.strip()
            if not stripped:
                continue
            if not ScriptInputCompiler._is_scene_heading(stripped):
                return stripped[:100]
        return "User Script"

    def parse_script_text(
        self,
        content: str,
        *,
        item: PlanningInputRef,
    ) -> ScriptSpec:
        raw = content.strip()
        if not raw:
            raise ValueError("SCRIPT_EMPTY")

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict) and parsed.get("scenes"):
            return ScriptSpec.model_validate(parsed)

        lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        title = self._script_title(item, lines)
        scene_chunks: list[tuple[str, list[str]]] = []
        current_heading: str | None = None
        current_lines: list[str] = []

        for raw_line in lines:
            line = raw_line.strip()
            if self._is_scene_heading(line):
                if current_heading is not None:
                    scene_chunks.append(
                        (
                            current_heading,
                            current_lines,
                        )
                    )
                elif scene_chunks:
                    scene_chunks.append(
                        (
                            f"SCENE {len(scene_chunks) + 1}",
                            current_lines,
                        )
                    )
                # Text before the first explicit scene heading is treated as
                # screenplay preamble/title material, not as a synthetic scene.
                current_heading = self._clean_heading(line)
                current_lines = []
                continue
            if line:
                current_lines.append(line)
            elif current_heading is not None or current_lines:
                # Preserve screenplay paragraph boundaries so dialogue blocks
                # do not absorb following action description.
                current_lines.append("")

        if current_heading is not None or current_lines:
            scene_chunks.append(
                (
                    current_heading
                    or f"SCENE {len(scene_chunks) + 1}",
                    current_lines,
                )
            )

        if not scene_chunks:
            scene_chunks = [("SCENE 1", [raw])]

        scenes: list[ScriptScene] = []
        for index, (heading, body) in enumerate(
            scene_chunks,
            start=1,
        ):
            actions: list[str] = []
            dialogue: list[DialogueLine] = []
            cursor = 0
            while cursor < len(body):
                line = body[cursor].strip()
                if not line:
                    cursor += 1
                    continue
                if (
                    self._is_speaker(line)
                    and cursor + 1 < len(body)
                ):
                    speaker = line.strip()
                    cursor += 1
                    parenthetical: str | None = None
                    if (
                        cursor < len(body)
                        and body[cursor].startswith("(")
                        and body[cursor].endswith(")")
                    ):
                        parenthetical = body[cursor][1:-1].strip()
                        cursor += 1
                    payload: list[str] = []
                    while cursor < len(body):
                        candidate = body[cursor].strip()
                        if self._is_speaker(candidate):
                            break
                        if self._is_scene_heading(candidate):
                            break
                        if not candidate:
                            cursor += 1
                            break
                        payload.append(candidate)
                        cursor += 1
                    if payload:
                        dialogue.append(
                            DialogueLine(
                                speaker=speaker,
                                text=" ".join(payload),
                                subtext=parenthetical,
                            )
                        )
                    continue
                actions.append(line)
                cursor += 1

            dramatic_event = (
                actions[0]
                if actions
                else (
                    dialogue[0].text
                    if dialogue
                    else heading
                )
            )
            scenes.append(
                ScriptScene(
                    scene_id=f"S{index:02d}",
                    heading=heading,
                    location_id=f"LOC{index:02d}",
                    time_of_day=self._time_of_day(heading),
                    dramatic_event=dramatic_event[:500],
                    action=actions,
                    dialogue=dialogue,
                    exit_state_summary=(
                        actions[-1][:500]
                        if actions
                        else dramatic_event[:500]
                    ),
                )
            )

        logline = next(
            (
                scene.dramatic_event
                for scene in scenes
                if scene.dramatic_event
            ),
            "A user-supplied script.",
        )
        return ScriptSpec(
            title=title,
            logline=logline[:500],
            scenes=scenes,
        )

    @staticmethod
    def production_profile(
        script: ScriptSpec,
    ) -> ScriptProductionProfile:
        speakers = {
            line.speaker.strip()
            for scene in script.scenes
            for line in scene.dialogue
            if line.speaker.strip()
        }
        dialogue_lines = [
            line
            for scene in script.scenes
            for line in scene.dialogue
        ]
        dialogue_words = sum(
            len(re.findall(r"\b\w+\b", line.text, re.UNICODE))
            for line in dialogue_lines
        )
        actions = [
            action
            for scene in script.scenes
            for action in scene.action
            if action.strip()
        ]
        action_words = sum(
            len(re.findall(r"\b\w+\b", action, re.UNICODE))
            for action in actions
        )
        total_words = dialogue_words + action_words
        dialogue_density = (
            dialogue_words / total_words
            if total_words
            else 0.0
        )
        locations = {
            scene.location_id
            for scene in script.scenes
            if scene.location_id
        }
        scene_count = len(script.scenes)
        location_count = len(locations)

        # Planning-only estimates. They are intentionally conservative and are
        # not used as timing truth after voice/render media exists.
        dialogue_seconds = dialogue_words / 150.0 * 60.0
        action_seconds = action_words / 130.0 * 60.0
        structural_floor = scene_count * 4.0
        estimated = max(
            structural_floor,
            dialogue_seconds + action_seconds,
        )

        performance_load = min(
            1.0,
            0.20
            + dialogue_density * 0.45
            + min(len(speakers), 5) / 5.0 * 0.20
            + min(len(dialogue_lines), 30) / 30.0 * 0.15,
        ) if scene_count else 0.0

        continuity_load = min(
            1.0,
            min(scene_count, 20) / 20.0 * 0.50
            + min(location_count, 10) / 10.0 * 0.30
            + min(len(speakers), 8) / 8.0 * 0.20,
        ) if scene_count else 0.0

        reusable_location_ratio = (
            max(0.0, 1.0 - location_count / scene_count)
            if scene_count
            else 0.0
        )
        signals: list[str] = []
        if dialogue_lines:
            signals.append(
                "dialogue exists; lock voice timing before lip-sync-sensitive animation"
            )
        if len(speakers) >= 2:
            signals.append(
                "multi-character dialogue requires eyeline, reaction and turn-taking continuity"
            )
        if dialogue_density >= 0.45:
            signals.append(
                "dialogue-heavy script; prioritize performance readability and speech intelligibility"
            )
        elif dialogue_density <= 0.15 and total_words:
            signals.append(
                "action-heavy script; prioritize visual blocking, camera clarity and physical continuity"
            )
        if scene_count >= 8:
            signals.append(
                "multi-scene script; schedule reusable rigs/assets and continuity checkpoints"
            )
        if reusable_location_ratio >= 0.5 and scene_count >= 3:
            signals.append(
                "locations repeat across scenes; reuse canonical sets rather than rebuilding them"
            )
        if continuity_load >= 0.65:
            signals.append(
                "high continuity load; require explicit state handoff across scenes"
            )

        return ScriptProductionProfile(
            scene_count=scene_count,
            location_count=location_count,
            speaker_count=len(speakers),
            dialogue_line_count=len(dialogue_lines),
            dialogue_word_count=dialogue_words,
            action_block_count=len(actions),
            action_word_count=action_words,
            dialogue_density=round(dialogue_density, 4),
            estimated_dialogue_seconds=round(dialogue_seconds, 2),
            estimated_action_seconds=round(action_seconds, 2),
            estimated_duration_seconds=round(estimated, 2),
            performance_load=round(performance_load, 4),
            continuity_load=round(continuity_load, 4),
            dialogue_present=bool(dialogue_lines),
            multi_character_dialogue=len(speakers) >= 2,
            reusable_location_ratio=round(
                reusable_location_ratio,
                4,
            ),
            planning_signals=signals,
        )

    @staticmethod
    def story_from_script(script: ScriptSpec) -> StorySpec:
        beats = [
            StoryBeat(
                beat_id=f"B{index:02d}",
                purpose=(
                    "establish"
                    if index == 1
                    else (
                        "resolve"
                        if index == len(script.scenes)
                        else "develop"
                    )
                ),
                change=scene.dramatic_event,
                audience_question=(
                    None
                    if index == len(script.scenes)
                    else "what changes next?"
                ),
            )
            for index, scene in enumerate(
                script.scenes,
                start=1,
            )
        ]
        return StorySpec(
            title=script.title,
            premise=script.logline,
            theme=None,
            protagonist_goal=(
                "complete the dramatic objective defined by the supplied script"
            ),
            central_conflict=(
                "the central conflict is preserved from the supplied script"
            ),
            ending_state=script.scenes[-1].exit_state_summary
            or script.scenes[-1].dramatic_event,
            beats=beats,
        )

    def outline_to_story(
        self,
        content: str,
        *,
        item: PlanningInputRef,
    ) -> StorySpec:
        lines = [
            line.strip()
            for line in content.replace("\r", "\n").split("\n")
            if line.strip()
        ]
        beats_raw: list[str] = []
        for line in lines:
            match = self._BULLET.match(line)
            if match:
                beats_raw.append(match.group(1).strip())
        if not beats_raw:
            paragraphs = [
                value.strip()
                for value in re.split(r"\n\s*\n|(?<=[.!?])\s{2,}", content)
                if value.strip()
            ]
            beats_raw = paragraphs
        if not beats_raw:
            beats_raw = [content.strip()]

        beats_raw = beats_raw[:24]
        title = item.title or "User Outline"
        beats = [
            StoryBeat(
                beat_id=f"B{index:02d}",
                purpose=(
                    "establish"
                    if index == 1
                    else (
                        "resolve"
                        if index == len(beats_raw)
                        else "develop"
                    )
                ),
                change=text[:1000],
                audience_question=(
                    None
                    if index == len(beats_raw)
                    else "what follows from this beat?"
                ),
            )
            for index, text in enumerate(beats_raw, start=1)
        ]
        return StorySpec(
            title=title,
            premise=content.strip()[:2000],
            theme=str(item.metadata.get("theme") or "") or None,
            protagonist_goal=str(
                item.metadata.get("protagonist_goal")
                or "complete the objective described by the outline"
            ),
            central_conflict=str(
                item.metadata.get("central_conflict")
                or "the conflict described by the supplied outline"
            ),
            ending_state=beats[-1].change,
            beats=beats,
        )

    @staticmethod
    def outline_production_profile(
        story: StorySpec,
    ) -> ScriptProductionProfile:
        beat_count = len(story.beats)
        estimated = max(beat_count * 12.0, 8.0 if beat_count else 0.0)
        continuity = min(
            1.0,
            beat_count / 16.0,
        ) if beat_count else 0.0
        signals = [
            (
                "outline-only planning estimate; recompute duration, "
                "performance and continuity after the full script is written"
            )
        ]
        if beat_count >= 8:
            signals.append(
                "multi-beat outline; reserve continuity checkpoints across the expanded script"
            )
        return ScriptProductionProfile(
            scene_count=beat_count,
            estimated_duration_seconds=round(estimated, 2),
            continuity_load=round(continuity, 4),
            duration_estimate_basis="outline_heuristic_only",
            planning_signals=signals,
        )

    def analyze_reference_script(
        self,
        item: PlanningInputRef,
        content: str,
    ) -> ReferenceScriptAnalysis:
        digest = self._hash(content)
        quarantine_dir = self.quarantine / digest[:16]
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        (quarantine_dir / "reference_script.txt").write_text(
            content,
            encoding="utf-8",
        )

        lines = [
            line.strip()
            for line in content.replace("\r", "\n").split("\n")
            if line.strip()
        ]
        scene_indexes = [
            index
            for index, line in enumerate(lines)
            if self._is_scene_heading(line)
        ]
        scene_count = max(1, len(scene_indexes))
        speakers = sum(self._is_speaker(line) for line in lines)
        words = re.findall(r"\b\w+\b", content, re.UNICODE)
        dialogue_words = 0
        for index, line in enumerate(lines[:-1]):
            if self._is_speaker(line):
                dialogue_words += len(
                    re.findall(
                        r"\b\w+\b",
                        lines[index + 1],
                        re.UNICODE,
                    )
                )
        ratio = (
            min(1.0, dialogue_words / len(words))
            if words
            else 0.0
        )
        average_scene_words = (
            len(words) / scene_count
            if scene_count
            else None
        )
        patterns: list[str] = []
        if scene_count >= 12:
            patterns.append(
                "uses a highly segmented multi-scene script structure"
            )
        elif scene_count <= 4:
            patterns.append(
                "uses a compact script structure with relatively few major scenes"
            )
        else:
            patterns.append(
                "uses a moderate number of major scene units"
            )
        if ratio >= 0.45:
            patterns.append(
                "uses dialogue-heavy scene construction"
            )
        elif ratio <= 0.15:
            patterns.append(
                "uses action/visual-description-heavy scene construction"
            )
        else:
            patterns.append(
                "balances dialogue with action/visual description"
            )
        if average_scene_words is not None:
            if average_scene_words <= 120:
                patterns.append(
                    "uses short script scene units with rapid structural turnover"
                )
            elif average_scene_words >= 450:
                patterns.append(
                    "uses long script scene units with extended development"
                )

        analysis = ReferenceScriptAnalysis(
            input_id=item.input_id,
            content_sha256=digest,
            approximate_word_count=len(words),
            scene_count=scene_count,
            dialogue_block_count=speakers,
            dialogue_word_ratio=round(ratio, 4),
            average_scene_words=(
                round(average_scene_words, 2)
                if average_scene_words is not None
                else None
            ),
            structure_patterns=patterns,
        )
        (self.safe_root / f"{digest[:16]}.json").write_text(
            analysis.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return analysis

    def compile(
        self,
        inputs: list[PlanningInputRef],
    ) -> ScriptSourcePack:
        scripts = [
            item
            for item in inputs
            if item.kind is PlanningInputKind.SCRIPT
        ]
        outlines = [
            item
            for item in inputs
            if item.kind is PlanningInputKind.SCRIPT_OUTLINE
        ]
        references = [
            item
            for item in inputs
            if item.kind is PlanningInputKind.REFERENCE_SCRIPT
        ]

        findings: list[str] = []
        reference_analyses: list[ReferenceScriptAnalysis] = []
        for item in references:
            try:
                content, _ = self._resolve_content(item)
                reference_analyses.append(
                    self.analyze_reference_script(item, content)
                )
            except Exception as exc:
                findings.append(
                    "REFERENCE_SCRIPT_ANALYSIS_FAILED:"
                    f"{item.input_id}:{type(exc).__name__}:{exc}"
                )

        reference_patterns = list(
            dict.fromkeys(
                pattern
                for analysis in reference_analyses
                for pattern in analysis.structure_patterns
            )
        )

        primary: PlanningInputRef | None = None
        mode = ScriptSourceMode.PROMPT_FALLBACK
        if scripts:
            explicitly_primary = [
                item
                for item in scripts
                if item.metadata.get("primary") is True
            ]
            primary = explicitly_primary[0] if explicitly_primary else scripts[0]
            mode = ScriptSourceMode.LOCKED_SCRIPT
            if len(scripts) > 1:
                findings.append(
                    "MULTIPLE_USER_SCRIPTS:"
                    f"primary={primary.input_id};"
                    "additional scripts tracked as supplemental"
                )
        elif outlines:
            explicitly_primary = [
                item
                for item in outlines
                if item.metadata.get("primary") is True
            ]
            primary = (
                explicitly_primary[0]
                if explicitly_primary
                else outlines[0]
            )
            mode = ScriptSourceMode.OUTLINE
            if len(outlines) > 1:
                findings.append(
                    "MULTIPLE_SCRIPT_OUTLINES:"
                    f"primary={primary.input_id}"
                )

        if primary is None:
            return ScriptSourcePack(
                mode=mode,
                reference_script_patterns=reference_patterns,
                reference_script_analyses=reference_analyses,
                findings=findings,
            )

        content, source_format = self._resolve_content(primary)
        digest = self._hash(content)
        supplemental_hashes: list[str] = []
        for item in scripts:
            if item.input_id == primary.input_id:
                continue
            try:
                supplemental, _ = self._resolve_content(item)
                supplemental_hashes.append(self._hash(supplemental))
            except Exception as exc:
                findings.append(
                    "SUPPLEMENTAL_SCRIPT_UNREADABLE:"
                    f"{item.input_id}:{type(exc).__name__}:{exc}"
                )

        if mode is ScriptSourceMode.LOCKED_SCRIPT:
            script = self.parse_script_text(content, item=primary)
            story = self.story_from_script(script)
            return ScriptSourcePack(
                mode=mode,
                revision_policy=self._revision_policy(primary),
                primary_input_id=primary.input_id,
                primary_content_sha256=digest,
                source_format=source_format,
                compiled_script=script.model_dump(mode="json"),
                compiled_story=story.model_dump(mode="json"),
                production_profile=self.production_profile(script),
                reference_script_patterns=reference_patterns,
                reference_script_analyses=reference_analyses,
                supplemental_script_hashes=supplemental_hashes,
                findings=findings,
            )

        story = self.outline_to_story(content, item=primary)
        return ScriptSourcePack(
            mode=mode,
            revision_policy=self._revision_policy(primary),
            primary_input_id=primary.input_id,
            primary_content_sha256=digest,
            source_format=source_format,
            compiled_story=story.model_dump(mode="json"),
            production_profile=self.outline_production_profile(story),
            reference_script_patterns=reference_patterns,
            reference_script_analyses=reference_analyses,
            findings=findings,
        )
