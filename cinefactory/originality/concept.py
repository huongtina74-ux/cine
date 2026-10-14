from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from cinefactory.domain.models import ShotSpec, StorySpec
from cinefactory.discovery.models import TopicStrategy
from cinefactory.originality.models import ConceptFingerprint, DifferentiationPlan
from cinefactory.originality.similarity import sequence_similarity, token_jaccard


def _norm_list(values: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        v = " ".join(str(value).split()).strip()
        key = v.casefold()
        if v and key not in seen:
            seen.add(key)
            out.append(v)
    return out


def fingerprint_from_project(
    story: StorySpec,
    *,
    strategy: TopicStrategy | None = None,
    differentiation: DifferentiationPlan | None = None,
    shots: list[ShotSpec] | None = None,
) -> ConceptFingerprint:
    beat_functions = [b.purpose for b in story.beats]
    evidence_domains: list[str] = []
    narrative_device = ""
    visual_grammar_tags: list[str] = []
    audience_promise = ""
    causal_mechanism = story.central_conflict

    if strategy is not None:
        audience_promise = strategy.angle
        evidence_domains.extend(strategy.differentiation_axes)
    if differentiation is not None:
        audience_promise = differentiation.original_thesis or audience_promise
        narrative_device = differentiation.narrative_device
        evidence_domains.extend(differentiation.evidence_plan)
        visual_grammar_tags.append(differentiation.visual_grammar)

    if shots:
        visual_grammar_tags.extend(
            f"{s.camera.shot_size}|{s.camera.movement.kind}|{s.camera.angle}|{int(round(s.camera.lens_mm / 10.0) * 10)}mm"
            for s in shots
        )

    return ConceptFingerprint(
        thesis=story.premise,
        primary_question=story.beats[0].audience_question or story.central_conflict if story.beats else story.central_conflict,
        causal_mechanism=causal_mechanism,
        audience_promise=audience_promise or story.protagonist_goal,
        narrative_device=narrative_device or "linear causal progression",
        evidence_domains=_norm_list(evidence_domains),
        example_entities=[],
        beat_functions=_norm_list(beat_functions),
        visual_grammar_tags=_norm_list(visual_grammar_tags),
    )


@dataclass(frozen=True)
class FingerprintComparison:
    overall: float
    collision_axes: tuple[str, ...]
    scores: dict[str, float]


def _text_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return max(token_jaccard(a, b), sequence_similarity(a, b))


def _list_score(a: list[str], b: list[str]) -> float:
    if not a or not b:
        return 0.0
    aa = " | ".join(a)
    bb = " | ".join(b)
    return max(token_jaccard(aa, bb), sequence_similarity(aa, bb))


def compare_fingerprints(candidate: ConceptFingerprint, reference: ConceptFingerprint) -> FingerprintComparison:
    scores = {
        "thesis": _text_score(candidate.thesis, reference.thesis),
        "primary_question": _text_score(candidate.primary_question, reference.primary_question),
        "causal_mechanism": _text_score(candidate.causal_mechanism, reference.causal_mechanism),
        "audience_promise": _text_score(candidate.audience_promise, reference.audience_promise),
        "narrative_device": _text_score(candidate.narrative_device, reference.narrative_device),
        "evidence_domains": _list_score(candidate.evidence_domains, reference.evidence_domains),
        "example_entities": _list_score(candidate.example_entities, reference.example_entities),
        "beat_functions": _list_score(candidate.beat_functions, reference.beat_functions),
        "visual_grammar": _list_score(candidate.visual_grammar_tags, reference.visual_grammar_tags),
    }
    # Concept collision should be driven mainly by thesis/mechanism/promise/structure.
    weights = {
        "thesis": 0.20,
        "primary_question": 0.10,
        "causal_mechanism": 0.18,
        "audience_promise": 0.14,
        "narrative_device": 0.10,
        "evidence_domains": 0.08,
        "example_entities": 0.05,
        "beat_functions": 0.10,
        "visual_grammar": 0.05,
    }
    overall = sum(scores[k] * weights[k] for k in weights)
    collision_axes = tuple(k for k, v in scores.items() if v >= 0.72)
    return FingerprintComparison(round(overall, 4), collision_axes, {k: round(v, 4) for k, v in scores.items()})
