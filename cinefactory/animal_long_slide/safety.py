"""Pre-upload monetization safety gate for the Animal Long Slide channel.

Each check maps to a published rule:
- YouTube "inauthentic content" (renamed 15 Jul 2025, clarified Jul 2026):
  templated, repetitive episodes, characters in the same situation with the
  same outcome, animals in exaggerated distress or peril.
- YouTube made-for-kids setting (COPPA): mandatory for content aimed at children.
- Copyright and trademarks: no franchise characters in titles, tags or stories.
- Metadata spam: keyword stuffing and copied competitor title templates.
The gate re-derives everything it can from the episode itself and never trusts
stored fingerprints or flags. It never approves on its own: a person must still
review every upload.
"""
from __future__ import annotations

import re

from .contracts import OutcomeKind
from .qc import LongSlideQC
from .series import SeriesBible, is_peril
from .variation import (
    EpisodeHistory,
    SafetyFinding,
    SafetyReport,
    VariationPolicy,
    VariedEpisode,
    episode_fingerprint,
    evaluate_variation,
    normalize_text,
    structural_tokens,
    title_key,
    title_similarity,
    title_tokens,
)

# Matched on normalize_text() output (accents stripped, punctuation collapsed),
# with an optional plural "s".
BLOCKED_IP_TERMS = (
    "spiderman", "spider man", "marvel", "disney", "elsa", "paw patrol", "peppa", "cocomelon",
    "bluey", "minecraft", "roblox", "gta", "grand theft auto", "pokemon", "pikachu", "sonic",
    "mario", "luigi", "batman", "iron man", "hulk", "venom", "barbie", "shrek", "mickey", "minion",
    "skibidi", "huggy wuggy", "poppy playtime", "superhero", "superheroes", "baby shark", "pinkfong",
    "lightning mcqueen", "hello kitty", "talking tom", "angry birds", "fnaf",
    "five nights at freddy", "sprunki", "masha and the bear", "blippi", "ms rachel",
)
# Regex stems with their inflections, matched on normalized text.
DISTRESS_PATTERNS = (
    r"cr(y|ies|ied|ying)", r"hurts?|hurting", r"injur(e|ed|es|ing|y|ies)", r"blood(y)?", r"bleed(s|ing)?",
    r"scar(e|ed|es|y|ier|iest|ing)", r"terrif(ied|ies|ying)", r"dangers?|dangerous", r"d(ie|ies|ied|ying)",
    r"dead(ly)?", r"deaths?", r"help me", r"trap(s|ped|ping)?", r"sad(ly|ness)?", r"pain(s|ful)?",
    r"scream(s|ed|ing)?", r"crash(es|ed|ing)?", r"drown(s|ed|ing)?", r"tears", r"afraid", r"stuck",
    r"panic(s|ked|king)?", r"sob(s|bed|bing)?", r"wound(s|ed)?", r"suffer(s|ed|ing)?",
)
ANIMAL_WORDS = frozenset({
    "cow", "elephant", "gorilla", "hippopotamus", "hippo", "tiger", "lion", "dinosaur",
    "duck", "giraffe", "buffalo", "monkey", "zebra", "bear", "dog", "cat", "horse", "pig",
    "sheep", "rabbit", "panda", "crocodile", "shark", "whale", "chicken", "goat", "fox",
})
COMPETITOR_TEMPLATES = (
    re.compile(r"long slide game with"),
    re.compile(r"\b\d+ giant duck cartoon"),
    re.compile(r"3d animal game funny"),
    re.compile(r"funny 3d animals?$"),
    re.compile(r"paint wild animals crossing fountain"),
)


def _term_hits(text: str, terms: tuple[str, ...]) -> list[str]:
    plain = f" {normalize_text(text)} "
    return [t for t in terms if re.search(rf" {re.escape(t)}s? ", plain)]


def _distress_hits(text: str) -> list[str]:
    plain = f" {normalize_text(text)} "
    return [p for p in DISTRESS_PATTERNS if re.search(rf" (?:{p}) ", plain)]


def _animal_count(title: str) -> int:
    found = set()
    for word in normalize_text(title).split():
        for form in (word, word[:-1] if word.endswith("s") else None, word[:-2] if word.endswith("es") else None):
            if form and form in ANIMAL_WORDS:
                found.add(form)
                break
    return len(found)


class MonetizationSafetyGate:
    def __init__(self, policy: VariationPolicy | None = None, bible: SeriesBible | None = None) -> None:
        self.policy = policy or VariationPolicy()
        self.bible = bible

    def review(self, varied: VariedEpisode, history: EpisodeHistory) -> SafetyReport:
        findings: list[SafetyFinding] = []
        findings += self._history_checks(varied, history)
        findings += self._title_checks(varied, history)
        findings += self._content_term_checks(varied)
        findings += self._episode_checks(varied)
        findings += self._upload_setting_checks(varied)
        return SafetyReport(
            passed=not any(f.severity == "ERROR" for f in findings),
            findings=findings,
            evidence={
                "checked_against_episodes": len(history.recent(self.policy.compare_window)),
                "checked_against_titles": len(history),
                "policy": self.policy.model_dump(mode="json"),
            },
        )

    def _history_checks(self, varied: VariedEpisode, history: EpisodeHistory) -> list[SafetyFinding]:
        fingerprint = episode_fingerprint(varied.concept, varied.episode)
        tokens = structural_tokens(varied.concept, varied.episode)
        out: list[SafetyFinding] = []
        if fingerprint != varied.fingerprint or tokens != varied.tokens:
            out.append(SafetyFinding(code="EVIDENCE_MISMATCH", message="stored fingerprint does not match the episode"))
        _, _, raw = evaluate_variation(self.policy, fingerprint, tokens, history)
        for item in raw:
            out.append(SafetyFinding(code=item.split(":", 1)[0], message=f"{item} (repetitive episodes)"))
        if varied.episode.originality_signature in history.signatures():
            out.append(SafetyFinding(code="DUPLICATE_SIGNATURE", message="this exact module plan was already approved"))
        return out

    def _title_checks(self, varied: VariedEpisode, history: EpisodeHistory) -> list[SafetyFinding]:
        title = varied.package.title
        out: list[SafetyFinding] = []
        if varied.episode.title != title:
            out.append(SafetyFinding(code="TITLE_MISMATCH", message="episode title and upload title differ"))
        if title_key(title) in history.title_keys():
            out.append(SafetyFinding(code="DUPLICATE_TITLE", message="this title was already used on the channel"))
        for record in history.recent(self.policy.title_window):
            score = title_similarity(title, record.title)
            if score > self.policy.max_title_similarity:
                out.append(SafetyFinding(code="TITLE_TOO_SIMILAR", message=f"{score:.2f} similar to {record.episode_id}"))
                break
        brand = self.bible.brand if self.bible else varied.episode.metadata.get("series_brand")
        if brand and normalize_text(brand) not in normalize_text(title):
            out.append(SafetyFinding(code="TITLE_MISSING_BRAND", message=f"title must carry the channel brand '{brand}'"))
        if len(title) > self.policy.max_title_length:
            out.append(SafetyFinding(code="TITLE_TOO_LONG", message=f"title has {len(title)} characters"))
        words = normalize_text(title).split()
        repeated = [w for w in title_tokens(title) if words.count(w) >= 3]
        if _animal_count(title) > self.policy.max_animal_names_in_title or repeated:
            out.append(SafetyFinding(code="KEYWORD_STUFFING", message=f"{_animal_count(title)} animal names, repeated {repeated}"))
        if any(p.search(normalize_text(title)) for p in COMPETITOR_TEMPLATES):
            out.append(SafetyFinding(code="COMPETITOR_TEMPLATE", message="title copies a known competitor template"))
        return out

    @staticmethod
    def _content_term_checks(varied: VariedEpisode) -> list[SafetyFinding]:
        package = varied.package
        out: list[SafetyFinding] = []
        ip_hits = _term_hits(" ".join([package.title, package.description, *package.tags]), BLOCKED_IP_TERMS)
        if ip_hits:
            out.append(SafetyFinding(code="BLOCKED_IP_TERM", message=f"franchise or trademark terms: {ip_hits}"))
        distress = _distress_hits(" ".join([package.title, package.description]))
        if distress:
            out.append(SafetyFinding(code="DISTRESS_LANGUAGE", message=f"distress or peril wording: {distress}"))
        return out

    def _episode_checks(self, varied: VariedEpisode) -> list[SafetyFinding]:
        modules = varied.episode.modules
        out: list[SafetyFinding] = []
        peril = [m for m in modules if is_peril(m)]
        if len(peril) > self.policy.peril_cap(len(modules)):
            out.append(SafetyFinding(code="PERIL_OVERUSE", message=f"{len(peril)} of {len(modules)} modules show peril"))
        if any(m.outcome not in {OutcomeKind.ESCAPE, OutcomeKind.SUCCESS} for m in peril):
            out.append(SafetyFinding(code="PERIL_UNRESOLVED", message="every peril module must end in escape or success"))
        if modules[-1].outcome not in {OutcomeKind.SUCCESS, OutcomeKind.TRANSFORM}:
            out.append(SafetyFinding(code="NEGATIVE_FINALE", message="the episode must end positively"))
        combos = [(m.animal_id, m.scene_kind, tuple(o.obstacle_id for o in m.obstacles), m.outcome) for m in modules]
        if len(set(combos)) != len(combos):
            out.append(SafetyFinding(code="WITHIN_EPISODE_REPETITION", message="two modules repeat the same setup and outcome"))
        if len(modules) >= 4 and len({m.outcome for m in modules}) < self.policy.min_outcome_kinds:
            out.append(SafetyFinding(code="LOW_OUTCOME_VARIETY", message="too few different outcomes in one episode"))
        if len(modules) >= 4 and len({m.scene_kind for m in modules}) < self.policy.min_scene_kinds:
            out.append(SafetyFinding(code="LOW_SCENE_VARIETY", message="too few different scenes in one episode"))
        cams = [tuple(b.pattern_id for b in m.camera_beats) for m in modules]
        if any(a == b for a, b in zip(cams, cams[1:])):
            out.append(SafetyFinding(code="CAMERA_REPETITION", message="adjacent modules reuse the same camera sequence"))
        if not varied.concept.synopsis or any("character_id" not in m.metadata for m in modules):
            out.append(SafetyFinding(code="MISSING_STORY", message="every episode needs a synopsis and named characters"))
        qc = LongSlideQC().review(varied.episode)
        if not qc.passed:
            out.append(SafetyFinding(code="EPISODE_QC_FAILED", message="; ".join(f.code for f in qc.findings)))
        return out

    @staticmethod
    def _upload_setting_checks(varied: VariedEpisode) -> list[SafetyFinding]:
        out: list[SafetyFinding] = []
        if varied.package.made_for_kids is not True:
            out.append(SafetyFinding(code="MADE_FOR_KIDS_NOT_SET", message="kids content must be marked made for kids"))
        if varied.package.requires_human_approval is not True:
            out.append(SafetyFinding(code="HUMAN_APPROVAL_DISABLED", message="a person must approve every upload"))
        return out
