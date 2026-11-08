# sound: production practice

This is an original studio decision aid, not course completion or production certification. Work in the selected CineFactory checkout. Current SOPs and owner decisions remain authoritative.

## Decisions before execution
Read the matching specialty section of `knowledge/professional/department-practice.md` in the selected checkout. It contains the decision matrix, failure diagnosis, controlled exercise, review rubric and downstream handoff. For directing, also read `knowledge/professional/director.md`. These are studio-authored practices requiring output review, not imported course certificates.

1. Select voice takes by intention and intelligibility; keep pronunciation and source/consent records.
2. Spot ambience, Foley and effects by event/role; make ducking follow phrasing rather than syllables.
3. Measure the encoded mix and record listening separately; intentional silence is format-dependent.

## Required handoff

Measured encoded mix plus separate listening/word-sync findings.

Use a packet carrying project_id, artifact_id, department, decisions, inputs, artifacts and data. Each input/output file has a repository-relative path and SHA-256. Each decision gives at least two alternatives, the selected option, reason and tradeoff. This preserves provenance; it does not authenticate a person's identity.

Create an unfilled packet with:

```text
python tools/cf_professional.py template sound --project-id PROJECT --out NEW_PACKET.json
python tools/cf_professional.py check-packet NEW_PACKET.json --root . --out CHECK_REPORT.json
```

Templates intentionally fail until real decisions and evidence are supplied. Exact domain fields are in config/professional/templates.json; the executable domain checks are in cinefactory/professional.py. Do not add invented schema fields to the existing Director Cut or producer input.

## Review rubric

- Contract: check identity, source versions and decision consistency.
- Domain counterexamples: LUFS/peak outside delivery target, missing listening scope.
- Output quality: inspect the actual artifact with the required modality, at its intended size/speed/context.
- Scope: PASS from check-packet means a local contract passed, not expert craft or commercial readiness.
- Handoff: send findings to the owner of the earliest cause, with a retest condition and changed artifact version.

Use criterion-by-criterion findings rather than a compensating average. Unknown evidence stays unknown. For training, compare an intentional failure against a corrected case and retain both. Tests/test_professional_handoffs.py contains positive/counterexample fixtures for this specialty; those fixtures are synthetic, not production output.

## Sources and access

- [audacity](https://manual.audacityteam.org/man/auto_duck.html) — primary technical page read. License/use: Manual terms; reference only. No manual or audio files copied.
- [blackmagic](https://www.blackmagicdesign.com/products/davinciresolve/training) — public course descriptions read. License/use: Blackmagic copyright/training terms; reference only. Full videos/books not completed.
- [mit_sound](https://ocw.mit.edu/courses/21m-380-music-and-technology-recording-techniques-and-audio-production-fall-2016/pages/lecture-notes/) — lecture index read. License/use: CC-BY-NC-SA-4.0; current OCW AI terms also apply. No course materials embedded in commercial runtime.

See config/professional/standards.json for the dated source ledger. These notes do not grant rights to redistribute source courses or install candidate repositories.
