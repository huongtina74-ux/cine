from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from cinefactory.domain.models import ScriptSpec, StorySpec
from cinefactory.originality.models import (
    AuthenticityReport,
    ConceptCollisionFinding,
    ConceptFingerprint,
    OriginalityPolicy,
    OriginalityReport,
    ReferenceKind,
    ReferenceRecord,
    ScriptCriticReport,
    SimilarityFinding,
)
from cinefactory.originality.concept import compare_fingerprints
from cinefactory.originality.similarity import (
    generated_coverage,
    jaccard,
    max_sentence_similarity,
    normalize_text,
    sequence_similarity,
    shingles,
    token_jaccard,
)


class OriginalityViolation(RuntimeError):
    pass


def story_text(story: StorySpec) -> str:
    beats = "\n".join(f"{b.purpose}: {b.change}. {b.audience_question or ''}" for b in story.beats)
    return "\n".join([
        story.title, story.premise, story.theme or "", story.protagonist_goal,
        story.central_conflict, story.ending_state, beats,
    ])


def story_idea_text(story: StorySpec) -> str:
    return " ".join([
        story.premise, story.protagonist_goal, story.central_conflict, story.ending_state,
        " ".join(b.change for b in story.beats),
    ])


def story_structure_text(story: StorySpec) -> str:
    return " | ".join(f"{b.purpose}:{b.change}" for b in story.beats)


def script_text(script: ScriptSpec) -> str:
    chunks = [script.title, script.logline]
    for scene in script.scenes:
        chunks.extend([scene.heading, scene.dramatic_event, *scene.action])
        chunks.extend(line.text for line in scene.dialogue)
    return "\n".join(chunks)


class OriginalityGuard:
    def __init__(self, policy: OriginalityPolicy | None = None) -> None:
        self.policy = policy or OriginalityPolicy()

    def _finding(self, ref: ReferenceRecord, metric: str, score: float, threshold: float, detail: str) -> SimilarityFinding:
        return SimilarityFinding(
            reference_id=ref.reference_id,
            reference_title=ref.title,
            metric=metric,
            score=round(score, 4),
            threshold=threshold,
            severity="BLOCK" if score >= threshold else "WARN",
            detail=detail,
        )

    def check_text(self, text: str, references: list[ReferenceRecord], *, artifact_kind: str, title: str | None = None) -> OriginalityReport:
        findings: list[SimilarityFinding] = []
        highest = 0.0
        gen_sh = shingles(text, self.policy.shingle_size)
        for ref in references:
            if not ref.raw_text.strip() and not ref.idea_summary and not ref.structure_beats:
                continue
            # Raw expression comparison. Source material is included here: facts may be reused,
            # but distinctive wording should not be copied.
            if ref.raw_text.strip():
                ref_sh = shingles(ref.raw_text, self.policy.shingle_size)
                cov = generated_coverage(gen_sh, ref_sh)
                jac = jaccard(gen_sh, ref_sh)
                sent = max_sentence_similarity(text, ref.raw_text)
                highest = max(highest, cov, jac, sent)
                if cov >= self.policy.max_generated_shingle_coverage:
                    findings.append(self._finding(ref, "SHINGLE_COVERAGE", cov, self.policy.max_generated_shingle_coverage, "Too much of the generated wording overlaps the reference."))
                if jac >= self.policy.max_document_jaccard:
                    findings.append(self._finding(ref, "DOCUMENT_JACCARD", jac, self.policy.max_document_jaccard, "Document-level phrase overlap is too high."))
                if sent >= self.policy.max_sentence_similarity:
                    findings.append(self._finding(ref, "SENTENCE_SIMILARITY", sent, self.policy.max_sentence_similarity, "At least one sentence is too close to the reference wording."))
            if title and ref.title:
                ts = sequence_similarity(title, ref.title)
                highest = max(highest, ts)
                if ts >= self.policy.max_title_similarity:
                    findings.append(self._finding(ref, "TITLE_SIMILARITY", ts, self.policy.max_title_similarity, "Title/packaging is too close to the reference."))
        directives = self._directives(findings)
        return OriginalityReport(
            passed=not any(x.severity == "BLOCK" for x in findings),
            artifact_kind=artifact_kind,
            highest_similarity=round(highest, 4),
            findings=findings,
            rewrite_directives=directives,
            compared_reference_ids=[r.reference_id for r in references],
        )

    def check_packaging(
        self,
        *,
        title: str,
        thumbnail_concept: str,
        supporting_text: str,
        references: list[ReferenceRecord],
        artifact_kind: str,
    ) -> OriginalityReport:
        base = self.check_text(supporting_text, references, artifact_kind=artifact_kind, title=title)
        findings = list(base.findings)
        highest = base.highest_similarity
        for ref in references:
            candidates = [x for x in [ref.title, ref.hook_summary, *ref.packaging_notes] if x]
            for candidate in candidates:
                ts = sequence_similarity(title, candidate)
                highest = max(highest, ts)
                if ts >= self.policy.max_title_similarity and not any(
                    f.reference_id == ref.reference_id and f.metric == "TITLE_SIMILARITY" and abs(f.score - round(ts, 4)) < 1e-6
                    for f in findings
                ):
                    findings.append(self._finding(
                        ref, "TITLE_SIMILARITY", ts, self.policy.max_title_similarity,
                        "Packaging title is too close to a reference title/hook pattern."
                    ))
                vs = max(token_jaccard(thumbnail_concept, candidate), sequence_similarity(thumbnail_concept, candidate))
                highest = max(highest, vs)
                if vs >= self.policy.max_idea_similarity:
                    findings.append(self._finding(
                        ref, "THUMBNAIL_CONCEPT_COLLISION", vs, self.policy.max_idea_similarity,
                        "Thumbnail concept is too close to a reference packaging idea."
                    ))
        return OriginalityReport(
            passed=not any(x.severity == "BLOCK" for x in findings),
            artifact_kind=artifact_kind,
            highest_similarity=round(highest, 4),
            findings=findings,
            rewrite_directives=self._directives(findings),
            compared_reference_ids=base.compared_reference_ids,
        )

    def check_story(self, story: StorySpec, references: list[ReferenceRecord]) -> OriginalityReport:
        report = self.check_text(story_text(story), references, artifact_kind="STORY", title=story.title)
        findings = list(report.findings)
        highest = report.highest_similarity
        idea = story_idea_text(story)
        structure = story_structure_text(story)
        for ref in references:
            if ref.kind not in {ReferenceKind.COMPETITOR, ReferenceKind.PRIOR_OWN, ReferenceKind.INSPIRATION}:
                continue
            if ref.idea_summary:
                score = max(
                    token_jaccard(idea, ref.idea_summary),
                    sequence_similarity(idea, ref.idea_summary),
                    token_jaccard(story.premise, ref.idea_summary),
                    sequence_similarity(story.premise, ref.idea_summary),
                )
                highest = max(highest, score)
                if score >= self.policy.max_idea_similarity:
                    findings.append(self._finding(ref, "IDEA_COLLISION", score, self.policy.max_idea_similarity, "The central angle/premise is too close to the reference idea summary."))
            if ref.structure_beats:
                ref_structure = " | ".join(ref.structure_beats)
                score = max(token_jaccard(structure, ref_structure), sequence_similarity(structure, ref_structure))
                highest = max(highest, score)
                if score >= self.policy.max_structure_similarity:
                    findings.append(self._finding(ref, "STRUCTURE_COLLISION", score, self.policy.max_structure_similarity, "The beat order/structure is too close to the reference."))
        return OriginalityReport(
            passed=not any(x.severity == "BLOCK" for x in findings),
            artifact_kind="STORY",
            highest_similarity=round(highest, 4),
            findings=findings,
            rewrite_directives=self._directives(findings),
            compared_reference_ids=report.compared_reference_ids,
        )

    def check_script(self, script: ScriptSpec, references: list[ReferenceRecord]) -> OriginalityReport:
        return self.check_text(script_text(script), references, artifact_kind="SCRIPT", title=script.title)

    @staticmethod
    def _directives(findings: list[SimilarityFinding]) -> list[str]:
        metrics = {f.metric for f in findings if f.severity == "BLOCK"}
        directives: list[str] = []
        if {"SHINGLE_COVERAGE", "DOCUMENT_JACCARD", "SENTENCE_SIMILARITY"} & metrics:
            directives.append("Rewrite from first principles; do not paraphrase sentence-by-sentence or preserve distinctive phrasing from references.")
        if "IDEA_COLLISION" in metrics:
            directives.append("Change the thesis/angle, causal mechanism, audience promise, examples or evidence set so the project is independently conceived.")
        if "STRUCTURE_COLLISION" in metrics:
            directives.append("Rebuild the narrative architecture and beat order; do not mirror the reference sequence with renamed details.")
        if "TITLE_SIMILARITY" in metrics:
            directives.append("Create a new packaging concept rather than modifying a competitor title with synonyms or numbers.")
        if "THUMBNAIL_CONCEPT_COLLISION" in metrics:
            directives.append("Change the thumbnail's visual premise, focal subject, contrast mechanism and information reveal; cosmetic layout changes are insufficient.")
        if findings and not directives:
            directives.append("Increase expressive distance from references while preserving only independently verifiable facts.")
        return directives

    def check_concept(self, fingerprint: ConceptFingerprint, references: list[ReferenceRecord]) -> list[ConceptCollisionFinding]:
        findings: list[ConceptCollisionFinding] = []
        for ref in references:
            if ref.kind not in {ReferenceKind.COMPETITOR, ReferenceKind.PRIOR_OWN, ReferenceKind.INSPIRATION}:
                continue
            if ref.concept_fingerprint is None:
                continue
            comp = compare_fingerprints(fingerprint, ref.concept_fingerprint)
            threshold = (
                self.policy.max_prior_own_fingerprint_similarity
                if ref.kind == ReferenceKind.PRIOR_OWN
                else self.policy.max_concept_fingerprint_similarity
            )
            axis_count = len(comp.collision_axes)
            blocked = comp.overall >= threshold and axis_count >= self.policy.min_concept_collision_axes
            warn = (comp.overall >= max(0.0, threshold - 0.10) and axis_count >= max(2, self.policy.min_concept_collision_axes - 1))
            if blocked or warn:
                findings.append(ConceptCollisionFinding(
                    reference_id=ref.reference_id,
                    kind=ref.kind,
                    overall_similarity=comp.overall,
                    collision_axes=list(comp.collision_axes),
                    axis_scores=comp.scores,
                    severity="BLOCK" if blocked else "WARN",
                ))
        return findings

    def authenticity_report(
        self,
        *,
        expression_report: OriginalityReport,
        fingerprint: ConceptFingerprint,
        references: list[ReferenceRecord],
    ) -> AuthenticityReport:
        concept_findings = self.check_concept(fingerprint, references)
        blocked = [x for x in concept_findings if x.severity == "BLOCK"]
        own = [x for x in concept_findings if x.kind == ReferenceKind.PRIOR_OWN]
        own_max = max((x.overall_similarity for x in own), default=0.0)
        if own_max >= self.policy.max_prior_own_fingerprint_similarity:
            repetition_risk = "HIGH"
        elif own_max >= max(0.0, self.policy.max_prior_own_fingerprint_similarity - 0.12):
            repetition_risk = "MEDIUM"
        else:
            repetition_risk = "LOW"
        required = list(expression_report.rewrite_directives)
        if blocked:
            axes = sorted({a for x in blocked for a in x.collision_axes})
            required.append(
                "Re-conceive the project across the colliding concept axes: " + ", ".join(axes) +
                ". A new title or surface paraphrase is insufficient."
            )
        if repetition_risk == "HIGH":
            required.append(
                "Channel self-collision is high. Change the thesis/mechanism/structure/visual grammar before production so the video is not interchangeable with prior uploads."
            )
        return AuthenticityReport(
            passed=expression_report.passed and not blocked and repetition_risk != "HIGH",
            expression_report=expression_report,
            concept_findings=concept_findings,
            channel_repetition_risk=repetition_risk,
            required_changes=list(dict.fromkeys(required)),
        )

    def require_authenticity_pass(self, report: AuthenticityReport) -> None:
        if not report.passed and self.policy.hard_block:
            details = []
            if report.expression_report and not report.expression_report.passed:
                details.append("expression")
            details.extend(
                f"concept:{x.reference_id}:{x.overall_similarity:.3f}:{','.join(x.collision_axes)}"
                for x in report.concept_findings if x.severity == "BLOCK"
            )
            if report.channel_repetition_risk == "HIGH":
                details.append("channel_repetition")
            raise OriginalityViolation("AUTHENTICITY_GATE_FAILED: " + "; ".join(details))

    def require_pass(self, report: OriginalityReport) -> None:
        if not report.passed and self.policy.hard_block:
            details = "; ".join(f"{x.metric}:{x.reference_id}:{x.score:.3f}" for x in report.findings if x.severity == "BLOCK")
            raise OriginalityViolation("ORIGINALITY_GATE_FAILED: " + details)


class ScriptCritic:
    """Deterministic anti-repetition gate before expensive production."""

    @staticmethod
    def _duplicates(items: list[str]) -> list[str]:
        normalized = [normalize_text(x) for x in items if normalize_text(x)]
        counts = Counter(normalized)
        return [x for x, n in counts.items() if n > 1 and len(x.split()) >= 4]

    def review(self, script: ScriptSpec) -> ScriptCriticReport:
        dialogue = [line.text for scene in script.scenes for line in scene.dialogue]
        actions = [action for scene in script.scenes for action in scene.action]
        repeated_dialogue = self._duplicates(dialogue)
        repeated_actions = self._duplicates(actions)
        scene_flags: list[str] = []
        scene_text = [" ".join([s.dramatic_event, *s.action, *(d.text for d in s.dialogue)]) for s in script.scenes]
        for i, a in enumerate(scene_text):
            for j in range(i + 1, len(scene_text)):
                score = sequence_similarity(a, scene_text[j])
                if score >= 0.82:
                    scene_flags.append(f"SCENES_TOO_SIMILAR:{script.scenes[i].scene_id}:{script.scenes[j].scene_id}:{score:.3f}")
        directives: list[str] = []
        if repeated_dialogue:
            directives.append("Remove repeated dialogue; each line must change information, pressure, objective or relationship.")
        if repeated_actions:
            directives.append("Replace repeated action beats with distinct visible actions that advance the scene.")
        if scene_flags:
            directives.append("Differentiate scene purpose and event progression; avoid re-running the same scene with cosmetic changes.")
        return ScriptCriticReport(
            passed=not (repeated_dialogue or repeated_actions or scene_flags),
            repeated_dialogue=repeated_dialogue,
            repeated_actions=repeated_actions,
            scene_similarity_flags=scene_flags,
            revision_directives=directives,
        )
