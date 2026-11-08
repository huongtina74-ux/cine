# writing: production practice

This is an original studio decision aid, not course completion or production certification. Work in the selected CineFactory checkout. Current SOPs and owner decisions remain authoritative.

## Decisions before execution
Read the matching specialty section of `knowledge/professional/department-practice.md` in the selected checkout. It contains the decision matrix, failure diagnosis, controlled exercise, review rubric and downstream handoff. For directing, also read `knowledge/professional/director.md`. These are studio-authored practices requiring output review, not imported course certificates.

1. Track objective -> obstacle -> choice -> consequence; list what each character knows at the time.
2. Plant a resource before it solves the conflict, and preserve the cost of the protagonist's choice.
3. Read dialogue for intention, then remove lines that only duplicate visible action unless the format needs them.

## Required handoff

Beat/choice/consequence graph and knowledge/prop ledger.

Use a packet carrying project_id, artifact_id, department, decisions, inputs, artifacts and data. Each input/output file has a repository-relative path and SHA-256. Each decision gives at least two alternatives, the selected option, reason and tradeoff. This preserves provenance; it does not authenticate a person's identity.

Create an unfilled packet with:

```text
python tools/cf_professional.py template writing --project-id PROJECT --out NEW_PACKET.json
python tools/cf_professional.py check-packet NEW_PACKET.json --root . --out CHECK_REPORT.json
```

Templates intentionally fail until real decisions and evidence are supplied. Exact domain fields are in config/professional/templates.json; the executable domain checks are in cinefactory/professional.py. Do not add invented schema fields to the existing Director Cut or producer input.

## Review rubric

- Contract: check identity, source versions and decision consistency.
- Domain counterexamples: cycles, uncaused beats and impossible knowledge changes.
- Output quality: inspect the actual artifact with the required modality, at its intended size/speed/context.
- Scope: PASS from check-packet means a local contract passed, not expert craft or commercial readiness.
- Handoff: send findings to the owner of the earliest cause, with a retest condition and changed artifact version.

Use criterion-by-criterion findings rather than a compensating average. Unknown evidence stays unknown. For training, compare an intentional failure against a corrected case and retain both. Tests/test_professional_handoffs.py contains positive/counterexample fixtures for this specialty; those fixtures are synthetic, not production output.

## Sources and access

- [pixar](https://www.khanacademy.org/partners/pixar) — public syllabus only. License/use: Mixed partner-content rights; no licensed assets/curriculum copied. Individual lesson captions unavailable.
- [suny_story](https://milnepublishing.geneseo.edu/exploring-movie-construction-and-production/chapter/3-what-are-the-mechanics-of-story-and-plot/) — candidate chapter; not yet fully inspected. License/use: CC-BY-NC-SA-4.0. Link-only academic learning; no course text incorporated.

- [Pixar character-arc activity](https://www.khanacademy.org/computing/pixar/storytelling/character/a/exercise-4): primary activity text visible in search index; direct open returned no body. Link-only, partner-content redistribution rights not cleared. Not a completed course.

See config/professional/standards.json for the dated source ledger. These notes do not grant rights to redistribute source courses or install candidate repositories.
