# CineCouncil — Unified Research Intelligence (October 2026)

## System contract

**One question → one source registry → independent specialist positions → adversarial cross-examination → one versioned decision → optional bounded experiment.**

Unlike nine isolated AI opinions, CineCouncil requires every department to answer the same `issue_id` and `question`, inspect the same evidence registry, and explicitly challenge one another. A majority vote does not override a material contradiction or a Quality objection.

The deterministic arbiter is not an LLM: it checks provenance, role identity, source reuse, objections, rebuttal closure and required approvals. It **cannot prove that an LLM's semantic interpretation is true**. All conclusions remain advisory until the real-world production experiment and human approval.

## Source of truth & lineage
- Every evidence item points to an existing local file, SHA-256 and declared source lineage. Identical file bytes are forbidden from claiming different lineages.
- Source registry checks detect tampering. SHA-256 protects integrity, **not** authenticity or causal truth. Independent-root labels need external validation by the research team.
- Public-video metadata is NOT a channel owner's private CTR/retention/RPM.
- No downloading YouTube videos through unauthorized means is introduced.

## Department protocol

1. **Initial**: each relevant department independently proposes SUPPORT / OPPOSE / UNKNOWN with reasons, confidence and registered evidence IDs. Quality role is mandatory.
2. **Cross-exam**: specialists receive each others' claims, inspect assumptions and respond via `responds_to`. A round-2 rebuttal by Quality and at least one other reviewer is mandatory even when initial reports agree.
3. **Arbitration**: a deterministic rule engine evaluates all views. If there is any unresolved OPPOSE/UNKNOWN, it returns `CONFLICT_UNRESOLVED`. A single source lineage yields `SINGLE_SOURCE`, initial agreement yields `NEEDS_CROSS_EXAM`, unclosed challenge yields `CHALLENGE_NOT_CLOSED`, and only reviewed agreement with distinct evidence roots yields `SUPPORTED_FOR_TEST`.
4. **One canonical answer**: `council-case` produces `case.json` pointing to a single `decision.json` in a versioned subfolder. Historical versions remain available; stale previous experiments are not authoritative.
5. **Learning**: `council-learn` requires supporting council decision, exact owned video ID, reporting window, the imported Analytics source's SHA-256 matching an independently registered owned-analytics evidence item, and passing technical QC for the same produced video. Result is only `WAITING_FOR_EXPERIMENT_DESIGN_AND_AUTHORIZATION`—never a self-applied style rule or published video.

## Command flow

From the CineFactory repo root (use your own authorized files; examples are placeholders):

```powershell
python -m cinefactory.research_intelligence council-evidence "D:\case\sources.json" "D:\case\registry.json"
python -m cinefactory.research_intelligence council-round "D:\case\issue.json" "D:\case\registry.json" "D:\case\observation.json" "D:\case\initial" --niche "Minecraft animation"
# Review and authorize selected task files before any paid Claude Code work.
# python -m cinefactory.research_intelligence run-claude "D:\case\approved_task.json" "D:\case\claude_result.json"
python -m cinefactory.research_intelligence council-import "D:\case\approved_task.json" "D:\case\claude_result.json" "D:\case\registry.json" "D:\case\reviewer_opinion.json"
# Assemble reviewer opinions into one JSON list, then:
python -m cinefactory.research_intelligence council-case "D:\case\issue.json" "D:\case\registry.json" "D:\case\opinions.json" "D:\case\current"
python -m cinefactory.research_intelligence council-round "D:\case\issue.json" "D:\case\registry.json" "D:\case\observation.json" "D:\case\rebuttal" --niche "Minecraft animation" --round rebuttal --previous-opinions "D:\case\opinions.json"
# After authorized peer review, append rebuttal opinions and rerun council-case.
# An experiment plan needs OWNED video measurements + matching technical QC.
```

Each `sources.json` item: `{"evidence_id":"ref-video","kind":"observation","path":"D:\case\observation.json","independent_root":"source-video-123","verified_by":"local_machine"}`. A second independent source (e.g. owner-authorized analytics) must have an independently evidenced root.

`issue.json` example: `{"issue_id":"minecraft-hook-01","question":"Should we experiment with an original faster opening?"}`

`opinions.json` is a list; each opinion: `{"issue_id":"minecraft-hook-01","department":"quality","round":"initial","stance":"UNKNOWN","evidence_ids":[],"rationale":"Need more data about pacing","confidence":0.2,"responds_to":[]}`. `rebuttal` opinions must address peer reviewers explicitly.

## Non-negotiable failure rules
- No automated production changes from one viral video, majority preference, or a fabricated citation.
- No silent mixing of incompatible report dates or metrics from different owned channels.
- No "VERIFIED" semantic claim merely because a file exists or two agents agree.
- No task approval inferred from running a scheduler; Claude execution remains explicit and budget-bound.
- Disagreeing departments generate concrete questions for another research round. If still unresolved, label uncertainty and stop.
- A real test, a human-approved conclusion, and reproducible positive effect are needed before any production playbook rule changes.

## Validation limits
Current tests include evidence tampering, duplicate sources, independent-root checks, consensus-only-from-one-source rejection, Quality veto, rebuttal closure, mismatched Claude output, mock Claude end-to-end and revisioned case manifests.

The Claude Code bridge has only been tested with mocked execution. No paid live cross-agent conference, multi-niche production benchmark or automatic verified learning promotion has been certified at this stage.
