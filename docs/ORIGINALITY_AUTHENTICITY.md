# Originality & Authenticity Architecture

CineFactory treats competitor material as **negative reference data**, never as creative source material.

## Goals

1. Do not copy competitor wording, titles, thumbnail concepts, examples, metaphors, scene order or beat order.
2. Do not recreate the same premise/angle/causal mechanism with surface paraphrasing.
3. Do not mass-produce near-duplicate videos inside the same channel/project library.
4. Permit common topics when the actual thesis, evidence, structure, narrative device and visual execution are materially different.

## Competitor quarantine

Raw competitor text is stored only inside the local `ReferenceLibrary` for collision detection. Creative reasoning receives `quarantine_view()` only. It excludes:

- raw transcript/script
- exact title
- exact hook wording
- exact beat/scene text
- source URL

The creative model is expected to invent independently. Similarity gates compare the result **after generation**.

## Gates

### Expression gate

Checks:

- generated shingle coverage
- document Jaccard overlap
- sentence similarity
- title similarity
- thumbnail concept similarity

### Idea / structure gate

Checks the candidate StorySpec against competitor/prior-own summaries for:

- central idea collision
- beat/structure collision

### Concept fingerprint gate

`ConceptFingerprint` compares semantic production axes:

- thesis
- primary question
- causal mechanism
- audience promise
- narrative device
- evidence domains
- example entities
- beat functions
- visual grammar

A high score is not enough by itself: a hard block also requires collision across multiple axes. This avoids treating a broad common topic as plagiarism while still blocking a renamed clone.

### Channel self-collision gate

Previous CineFactory projects are converted to `PRIOR_OWN` references automatically. A new project that is materially interchangeable with a prior project is blocked before expensive production.

### Final packaging gate

The final title, thumbnail concept, description and chapters are checked again after the film exists.

## Important boundary

This system reduces collision/reuse risk; it is not a legal determination and cannot guarantee zero copyright or monetization risk. Broad ideas and facts can legitimately overlap. The system is designed to force independent expression and materially differentiated creative substance.
