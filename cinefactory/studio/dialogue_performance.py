from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from cinefactory.block_animation.contracts import (
    ActionCue,
    ExpressionCue,
    GazeCue,
    ReactionTrigger,
)


class DialogueRole(StrEnum):
    SPEAKER = "SPEAKER"
    LISTENER = "LISTENER"


class SpeechTimingToken(BaseModel):
    """Provided word/phoneme annotations, not measured A/V lipsync evidence."""

    text: str = Field(min_length=1)
    kind: Literal["word", "phoneme"] = "word"
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)
    provenance: Literal["manual", "forced_alignment"] = "manual"

    @model_validator(mode="after")
    def valid_interval(self):
        if self.end_seconds <= self.start_seconds:
            raise ValueError("speech token end must be after start")
        return self


class DialogueLineIntent(BaseModel):
    line_id: str
    speaker_id: str
    listener_ids: list[str] = Field(default_factory=list)
    text: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    action_verb: str = Field(min_length=1)
    subtext: str | None = None
    emotion: str = "neutral"
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)
    reaction_trigger: str | None = None
    reaction_delay_seconds: float = Field(default=0.16, ge=0, le=2.0)
    gesture: str | None = None
    voice_emotion: str | None = None
    speech_timing: list[SpeechTimingToken] = Field(default_factory=list)
    speech_alignment_required: bool = False

    @model_validator(mode="after")
    def timing(self):
        if self.end_seconds <= self.start_seconds:
            raise ValueError("dialogue line end must be after start")
        if self.speaker_id in self.listener_ids:
            raise ValueError("speaker cannot also be a listener")
        if len(self.listener_ids) != len(set(self.listener_ids)):
            raise ValueError("listener ids must be unique")
        return self


class SemanticPerformanceDirective(BaseModel):
    line_id: str
    actor_id: str
    role: DialogueRole
    objective: str
    action_verb: str
    subtext: str | None = None
    emotion: str = "neutral"
    gaze_target: str | None = None
    outward_behavior: str | None = None
    listening_behavior: str | None = None
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)
    reaction_trigger: str | None = None
    reaction_delay_seconds: float | None = Field(default=None, ge=0)
    voice_emotion: str | None = None
    spoken_text: str | None = None
    speech_timing: list[SpeechTimingToken] = Field(default_factory=list)
    speech_alignment_status: str | None = None


class DialoguePerformanceQC(BaseModel):
    passed: bool
    score: float = Field(ge=0, le=1)
    measured_checks: int = Field(ge=0)
    passed_checks: int = Field(ge=0)
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    speaker_checks: list[dict[str, Any]] = Field(default_factory=list)
    listener_checks: list[dict[str, Any]] = Field(default_factory=list)
    timing_checks: list[dict[str, Any]] = Field(default_factory=list)
    alignment_checks: list[dict[str, Any]] = Field(default_factory=list)
    audio_lipsync_measured: bool = False


class DialoguePerformanceCompilation(BaseModel):
    shot_id: str
    directives: list[SemanticPerformanceDirective] = Field(default_factory=list)
    actions: list[ActionCue] = Field(default_factory=list)
    expressions: list[ExpressionCue] = Field(default_factory=list)
    gaze: list[GazeCue] = Field(default_factory=list)
    reactions: list[ReactionTrigger] = Field(default_factory=list)
    qc: DialoguePerformanceQC


class DialoguePerformanceEngine:
    """Compile semantic dialogue intent into executable block-animation cues.

    The engine is deterministic and backend-neutral at the intent layer.
    Current executable cue output targets the existing Block Animation contracts.
    It does not claim phoneme/lip-sync measurement yet.
    """

    EMOTION_TO_EXPRESSION = {
        "neutral": "neutral",
        "happy": "happy",
        "joy": "happy",
        "amused": "laugh",
        "laugh": "laugh",
        "sad": "sad",
        "hurt": "sad",
        "angry": "angry",
        "frustrated": "angry",
        "surprised": "surprised",
        "shocked": "surprised",
        "terrified": "terrified",
        "afraid": "terrified",
        "confused": "confused",
        "smug": "smug",
        "skeptical": "confused",
    }
    ACTION_TO_GESTURE = {
        "accuse": "point",
        "challenge": "point",
        "convince": "point",
        "warn": "point",
        "greet": "wave",
        "celebrate": "wave",
        "laugh": "laugh_body",
        "cry": "cry_body",
    }
    ACTION_TO_TRIGGER = {
        "accuse": "accusation",
        "reveal": "reveal",
        "shock": "reveal",
        "hit": "impact",
        "push": "impact",
    }

    @staticmethod
    def _normalize(value: str | None) -> str:
        return str(value or "").strip().lower().replace("-", "_")

    def _expression(self, emotion: str) -> str:
        key = self._normalize(emotion)
        return self.EMOTION_TO_EXPRESSION.get(key, "neutral")

    def _gesture(self, line: DialogueLineIntent) -> str | None:
        if line.gesture:
            return line.gesture
        return self.ACTION_TO_GESTURE.get(
            self._normalize(line.action_verb)
        )

    def _trigger(self, line: DialogueLineIntent) -> str | None:
        if line.reaction_trigger:
            return line.reaction_trigger
        return self.ACTION_TO_TRIGGER.get(
            self._normalize(line.action_verb)
        )

    def compile(
        self,
        *,
        shot_id: str,
        duration_seconds: float,
        actor_ids: list[str],
        lines: list[DialogueLineIntent],
    ) -> DialoguePerformanceCompilation:
        actors = set(actor_ids)
        directives: list[SemanticPerformanceDirective] = []
        actions: list[ActionCue] = []
        expressions: list[ExpressionCue] = []
        gaze: list[GazeCue] = []
        reactions: list[ReactionTrigger] = []
        blockers: list[str] = []
        warnings: list[str] = []
        speaker_checks: list[dict[str, Any]] = []
        listener_checks: list[dict[str, Any]] = []
        timing_checks: list[dict[str, Any]] = []
        alignment_checks: list[dict[str, Any]] = []
        seen_line_ids: set[str] = set()
        measured = 0
        passed = 0

        ordered = sorted(
            lines,
            key=lambda item: (
                item.start_seconds,
                item.end_seconds,
                item.line_id,
            ),
        )
        previous_end = 0.0
        for line in ordered:
            measured += 1
            unique_line = line.line_id not in seen_line_ids
            seen_line_ids.add(line.line_id)
            if unique_line:
                passed += 1
            else:
                blockers.append(f"{line.line_id}:DUPLICATE_LINE_ID")

            measured += 1
            timing_ok = bool(
                0 <= line.start_seconds < line.end_seconds
                <= duration_seconds + 1e-9
            )
            timing_checks.append(
                {
                    "line_id": line.line_id,
                    "start_seconds": line.start_seconds,
                    "end_seconds": line.end_seconds,
                    "passed": timing_ok,
                }
            )
            if timing_ok:
                passed += 1
            else:
                blockers.append(
                    f"{line.line_id}:DIALOGUE_TIMING_OUT_OF_RANGE"
                )

            if line.start_seconds < previous_end - 0.08:
                warnings.append(
                    f"{line.line_id}:DIALOGUE_LINE_OVERLAP"
                )
            previous_end = max(previous_end, line.end_seconds)

            measured += 1
            speaker_ok = line.speaker_id in actors
            speaker_checks.append(
                {
                    "line_id": line.line_id,
                    "speaker_id": line.speaker_id,
                    "passed": speaker_ok,
                }
            )
            if speaker_ok:
                passed += 1
            else:
                blockers.append(
                    f"{line.line_id}:UNKNOWN_SPEAKER:{line.speaker_id}"
                )
                continue

            unknown_listeners = [
                actor_id
                for actor_id in line.listener_ids
                if actor_id not in actors
            ]
            measured += 1
            listeners_ok = not unknown_listeners
            listener_checks.append(
                {
                    "line_id": line.line_id,
                    "listener_ids": list(line.listener_ids),
                    "unknown": unknown_listeners,
                    "passed": listeners_ok,
                }
            )
            if listeners_ok:
                passed += 1
            else:
                blockers.extend(
                    f"{line.line_id}:UNKNOWN_LISTENER:{actor_id}"
                    for actor_id in unknown_listeners
                )

            alignment_ok = True
            alignment_status = "NOT_REQUESTED"
            if line.speech_alignment_required or line.speech_timing:
                previous_token_end = line.start_seconds
                alignment_ok = bool(line.speech_timing)
                for token in line.speech_timing:
                    if (
                        token.start_seconds < line.start_seconds - 1e-9
                        or token.end_seconds > line.end_seconds + 1e-9
                        or token.start_seconds < previous_token_end - 1e-9
                    ):
                        alignment_ok = False
                    previous_token_end = max(previous_token_end, token.end_seconds)
                alignment_status = (
                    "ANNOTATED_NOT_AUDIO_VERIFIED" if alignment_ok
                    else "INVALID_OR_MISSING"
                )
                measured += 1
                if alignment_ok:
                    passed += 1
                else:
                    blockers.append(f"{line.line_id}:SPEECH_ALIGNMENT_INVALID_OR_MISSING")
                alignment_checks.append({
                    "line_id": line.line_id,
                    "speaker_id": line.speaker_id,
                    "token_count": len(line.speech_timing),
                    "status": alignment_status,
                    "passed": alignment_ok,
                    "audio_lipsync_measured": False,
                })

            # Block partial/invalid animation contracts from entering render.
            if not all((unique_line, timing_ok, listeners_ok, alignment_ok)):
                continue

            expression_id = self._expression(line.emotion)
            expressions.append(
                ExpressionCue(
                    actor_id=line.speaker_id,
                    expression_id=expression_id,
                    start_seconds=line.start_seconds,
                    end_seconds=line.end_seconds,
                    intensity=0.72,
                )
            )
            primary_listener = (
                line.listener_ids[0]
                if line.listener_ids
                else None
            )
            if primary_listener:
                gaze.append(
                    GazeCue(
                        actor_id=line.speaker_id,
                        target_actor_id=primary_listener,
                        start_seconds=line.start_seconds,
                        end_seconds=line.end_seconds,
                        intensity=0.88,
                    )
                )

            gesture = self._gesture(line)
            if gesture:
                actions.append(
                    ActionCue(
                        actor_id=line.speaker_id,
                        clip_id=gesture,
                        start_seconds=line.start_seconds,
                        end_seconds=min(
                            line.end_seconds,
                            line.start_seconds + 1.25,
                        ),
                        intensity=0.72,
                        layer="upper" if gesture in {"point", "wave"} else None,
                    )
                )

            directives.append(
                SemanticPerformanceDirective(
                    line_id=line.line_id,
                    actor_id=line.speaker_id,
                    role=DialogueRole.SPEAKER,
                    objective=line.objective,
                    action_verb=line.action_verb,
                    subtext=line.subtext,
                    emotion=line.emotion,
                    gaze_target=primary_listener,
                    outward_behavior=(
                        gesture or f"speak with {line.emotion} intent"
                    ),
                    start_seconds=line.start_seconds,
                    end_seconds=line.end_seconds,
                    reaction_trigger=self._trigger(line),
                    reaction_delay_seconds=line.reaction_delay_seconds,
                    voice_emotion=(
                        line.voice_emotion or line.emotion
                    ),
                    spoken_text=line.text,
                    speech_timing=list(line.speech_timing),
                    speech_alignment_status=alignment_status,
                )
            )

            trigger = self._trigger(line)
            for listener_id in line.listener_ids:
                if listener_id not in actors:
                    continue
                # Listening starts slightly before the line to avoid a robotic
                # head snap exactly on the first phoneme.
                listen_start = max(0.0, line.start_seconds - 0.10)
                listen_end = min(
                    duration_seconds,
                    line.end_seconds + line.reaction_delay_seconds + 0.35,
                )
                gaze.append(
                    GazeCue(
                        actor_id=listener_id,
                        target_actor_id=line.speaker_id,
                        start_seconds=listen_start,
                        end_seconds=listen_end,
                        intensity=0.82,
                    )
                )
                directives.append(
                    SemanticPerformanceDirective(
                        line_id=line.line_id,
                        actor_id=listener_id,
                        role=DialogueRole.LISTENER,
                        objective=f"listen and respond to {line.speaker_id}",
                        action_verb="listen",
                        subtext=line.subtext,
                        emotion="listening",
                        gaze_target=line.speaker_id,
                        outward_behavior="active listening",
                        listening_behavior=(
                            "maintain eyeline, delay reaction until semantic beat lands"
                        ),
                        start_seconds=listen_start,
                        end_seconds=listen_end,
                        reaction_trigger=trigger,
                        reaction_delay_seconds=line.reaction_delay_seconds,
                    )
                )
                if trigger:
                    at = min(
                        duration_seconds,
                        line.end_seconds + line.reaction_delay_seconds,
                    )
                    reactions.append(
                        ReactionTrigger(
                            trigger=trigger,
                            at_seconds=at,
                            source_actor_id=line.speaker_id,
                            target_actor_ids=[listener_id],
                        )
                    )

                measured += 1
                coverage_ok = bool(
                    listen_start <= line.start_seconds
                    and listen_end >= line.end_seconds
                )
                listener_checks.append(
                    {
                        "line_id": line.line_id,
                        "listener_id": listener_id,
                        "listening_start": listen_start,
                        "listening_end": listen_end,
                        "passed": coverage_ok,
                    }
                )
                if coverage_ok:
                    passed += 1
                else:
                    blockers.append(
                        f"{line.line_id}:LISTENING_COVERAGE_INCOMPLETE:{listener_id}"
                    )

        score = (
            passed / measured
            if measured
            else 1.0
        )
        qc = DialoguePerformanceQC(
            passed=not blockers,
            score=score,
            measured_checks=measured,
            passed_checks=passed,
            blockers=sorted(set(blockers)),
            warnings=sorted(set(warnings)),
            speaker_checks=speaker_checks,
            listener_checks=listener_checks,
            timing_checks=timing_checks,
            alignment_checks=alignment_checks,
            audio_lipsync_measured=False,
        )
        return DialoguePerformanceCompilation(
            shot_id=shot_id,
            directives=directives,
            actions=actions,
            expressions=expressions,
            gaze=gaze,
            reactions=reactions,
            qc=qc,
        )

    @staticmethod
    def apply_to_shot(shot: Any, compilation: DialoguePerformanceCompilation):
        """Fail closed on invalid dialogue before copying cues into a shot."""
        if not compilation.qc.passed:
            raise ValueError(
                "DIALOGUE_QC_BLOCKED:" + "|".join(compilation.qc.blockers)
            )
        if getattr(shot, "shot_id", None) != compilation.shot_id:
            raise ValueError("DIALOGUE_SHOT_ID_MISMATCH")
        shot_actors = {
            actor.actor_id for actor in getattr(shot, "actors", [])
        }
        if any(
            directive.actor_id not in shot_actors
            for directive in compilation.directives
        ):
            raise ValueError("DIALOGUE_SHOT_ACTOR_MISMATCH")
        updates = {
            "actions": list(getattr(shot, "actions", []))
            + list(compilation.actions),
            "expressions": list(getattr(shot, "expressions", []))
            + list(compilation.expressions),
            "gaze": list(getattr(shot, "gaze", []))
            + list(compilation.gaze),
            "reactions": list(getattr(shot, "reactions", []))
            + list(compilation.reactions),
            "performance_directives": list(
                getattr(shot, "performance_directives", [])
            )
            + [
                item.model_dump(mode="json")
                for item in compilation.directives
            ],
            "creative_intent": {
                **dict(getattr(shot, "creative_intent", {}) or {}),
                "semantic_performance_required": True,
                "dialogue_performance_qc": compilation.qc.model_dump(
                    mode="json"
                ),
            },
        }
        return shot.model_copy(update=updates)
