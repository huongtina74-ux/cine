from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

_WORD = re.compile(r"\w+", re.UNICODE)
_SENTENCE = re.compile(r"(?<=[.!?。！？])\s+|\n+")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(_WORD.findall(text))


def tokens(text: str) -> list[str]:
    return _WORD.findall(unicodedata.normalize("NFKC", text).casefold())


def shingles(text: str, n: int = 7) -> set[tuple[str, ...]]:
    t = tokens(text)
    if len(t) < n:
        return {tuple(t)} if t else set()
    return {tuple(t[i : i + n]) for i in range(len(t) - n + 1)}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def generated_coverage(generated: set, reference: set) -> float:
    if not generated:
        return 0.0
    return len(generated & reference) / len(generated)


def sequence_similarity(a: str, b: str) -> float:
    na, nb = normalize_text(a), normalize_text(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb, autojunk=False).ratio()


def max_sentence_similarity(a: str, b: str, *, min_words: int = 7) -> float:
    sa = [x.strip() for x in _SENTENCE.split(a) if len(tokens(x)) >= min_words]
    sb = [x.strip() for x in _SENTENCE.split(b) if len(tokens(x)) >= min_words]
    highest = 0.0
    for x in sa:
        nx = normalize_text(x)
        for y in sb:
            score = SequenceMatcher(None, nx, normalize_text(y), autojunk=False).ratio()
            highest = max(highest, score)
    return highest


def token_jaccard(a: str, b: str) -> float:
    return jaccard(set(tokens(a)), set(tokens(b)))
