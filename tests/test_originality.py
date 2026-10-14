from pathlib import Path

from cinefactory.domain.models import ScriptScene, ScriptSpec, StoryBeat, StorySpec, DialogueLine
from cinefactory.originality import OriginalityGuard, ReferenceKind, ReferenceLibrary, ReferenceRecord, ScriptCritic


def story(title: str, premise: str, goal: str = "protect the family") -> StorySpec:
    return StorySpec(
        title=title,
        premise=premise,
        theme="sacrifice",
        protagonist_goal=goal,
        central_conflict="a hidden decision changes the family relationship",
        ending_state="the family understands the cost and makes a new choice",
        beats=[
            StoryBeat(beat_id="B1", purpose="discover", change="a receipt reveals the hidden decision"),
            StoryBeat(beat_id="B2", purpose="investigate", change="new evidence changes who holds the truth"),
            StoryBeat(beat_id="B3", purpose="resolve", change="a direct conversation changes the relationship"),
        ],
    )


def test_exact_competitor_expression_is_blocked():
    ref=ReferenceRecord(
        kind=ReferenceKind.COMPETITOR,
        title="The Hidden House Sale",
        raw_text="The daughter opens the drawer and finds a folded receipt proving her father sold the house to pay the hospital bill. She confronts him at dinner.",
        idea_summary="A daughter discovers her father secretly sold the family home to pay medical bills and confronts him.",
        structure_beats=["daughter finds receipt", "daughter investigates", "daughter confronts father"],
    )
    candidate=story("The Hidden House Sale", "The daughter opens the drawer and finds a folded receipt proving her father sold the house to pay the hospital bill. She confronts him at dinner.")
    report=OriginalityGuard().check_story(candidate,[ref])
    assert not report.passed
    assert {f.metric for f in report.findings} & {"TITLE_SIMILARITY","SHINGLE_COVERAGE","SENTENCE_SIMILARITY","IDEA_COLLISION"}


def test_independent_angle_passes_same_broad_topic():
    ref=ReferenceRecord(
        kind=ReferenceKind.COMPETITOR,
        title="7 Retirement Mistakes",
        raw_text="Seven retirement mistakes can destroy your nest egg. We count them down from seven to one.",
        idea_summary="Countdown list of seven retirement mistakes that reduce savings.",
        structure_beats=["mistake 7", "mistake 6", "mistake 5", "mistake 4", "mistake 3", "mistake 2", "mistake 1"],
    )
    candidate=story(
        "Why Retirement Plans Break Under Sequence Risk",
        "A retired couple stress-tests three withdrawal paths to reveal how sequence risk changes outcomes, then builds a decision rule around cash-flow timing.",
        goal="build a resilient withdrawal rule",
    )
    report=OriginalityGuard().check_story(candidate,[ref])
    assert report.passed


def test_same_idea_summary_blocks_even_without_copied_wording():
    ref=ReferenceRecord(
        kind=ReferenceKind.COMPETITOR,
        title="Competitor",
        raw_text="Completely different surface wording here.",
        idea_summary="daughter discovers father secretly sold family home to pay medical bills and confronts him",
        structure_beats=["clue", "investigation", "confrontation"],
    )
    candidate=story(
        "A Quiet Receipt",
        "A daughter learns that her father secretly sold the family home to pay medical bills and forces him to explain the sacrifice.",
    )
    report=OriginalityGuard().check_story(candidate,[ref])
    assert not report.passed
    assert any(f.metric=="IDEA_COLLISION" for f in report.findings)


def test_script_critic_rejects_repeated_dialogue():
    scene=lambda sid: ScriptScene(
        scene_id=sid, heading="INT. ROOM - DAY", location_id="L1", time_of_day="DAY",
        dramatic_event="new information arrives", action=["opens the letter"],
        dialogue=[DialogueLine(speaker="C1", text="I need to understand what is happening now.")],
    )
    script=ScriptSpec(title="x",logline="x",scenes=[scene("S1"),scene("S2")])
    report=ScriptCritic().review(script)
    assert not report.passed
    assert report.repeated_dialogue


def test_reference_library_roundtrip(tmp_path: Path):
    library=ReferenceLibrary(tmp_path)
    src=tmp_path/"competitor.txt"
    src.write_text("A competitor transcript",encoding="utf-8")
    record=library.import_text(src,kind=ReferenceKind.COMPETITOR,title="Competitor")
    loaded=library.get(record.reference_id)
    assert loaded.raw_text=="A competitor transcript"

from cinefactory.originality import ConceptFingerprint


def test_quarantine_view_never_exposes_competitor_expression():
    ref=ReferenceRecord(
        kind=ReferenceKind.COMPETITOR,
        title="Exact Competitor Title Formula",
        raw_text="A distinctive competitor sentence that must never enter creative context.",
        idea_summary="A specific competitor premise",
        structure_beats=["exact beat one", "exact beat two"],
        collision_tags=["countdown-list", "fear-hook"],
    )
    view=ref.quarantine_view()
    dumped=str(view)
    assert "Exact Competitor Title Formula" not in dumped
    assert "distinctive competitor sentence" not in dumped
    assert "specific competitor premise" not in dumped
    assert "exact beat one" not in dumped
    assert view["collision_tags"] == ["countdown-list", "fear-hook"]


def test_structured_concept_collision_blocks_surface_rewrite():
    fp=ConceptFingerprint(
        thesis="Retirees can lose money because early market losses interact with withdrawals",
        primary_question="How do early losses change retirement outcomes?",
        causal_mechanism="sequence risk plus fixed withdrawals",
        audience_promise="show why identical average returns can produce different retirement outcomes",
        narrative_device="compare three retiree timelines",
        evidence_domains=["withdrawal math", "sequence risk"],
        beat_functions=["setup", "compare", "reveal", "rule"],
        visual_grammar_tags=["timeline comparison", "cash-flow chart"],
    )
    ref=ReferenceRecord(
        kind=ReferenceKind.COMPETITOR,
        title="Competitor",
        concept_fingerprint=fp,
    )
    report=OriginalityGuard().authenticity_report(
        expression_report=OriginalityGuard().check_text("Fresh surface wording", [ref], artifact_kind="STORY"),
        fingerprint=fp,
        references=[ref],
    )
    assert not report.passed
    assert any(x.severity == "BLOCK" for x in report.concept_findings)
    assert "thesis" in report.concept_findings[0].collision_axes


def test_structured_concept_allows_same_domain_with_new_mechanism_and_device():
    ref=ReferenceRecord(
        kind=ReferenceKind.COMPETITOR,
        title="Competitor",
        concept_fingerprint=ConceptFingerprint(
            thesis="Seven common retirement mistakes reduce savings",
            primary_question="Which retirement mistakes are worst?",
            causal_mechanism="behavioral mistakes",
            audience_promise="count down seven mistakes",
            narrative_device="countdown list",
            evidence_domains=["generic tips"],
            beat_functions=["mistake", "mistake", "mistake"],
            visual_grammar_tags=["talking head", "list cards"],
        ),
    )
    candidate=ConceptFingerprint(
        thesis="Withdrawal timing changes failure risk even when average returns are equal",
        primary_question="Why can two identical portfolios end differently?",
        causal_mechanism="sequence-of-returns interaction with cash-flow withdrawals",
        audience_promise="derive a decision rule from three simulated timelines",
        narrative_device="counterfactual timeline experiment",
        evidence_domains=["historical returns", "cash-flow simulation"],
        beat_functions=["hypothesis", "experiment", "failure", "decision rule"],
        visual_grammar_tags=["scenario timeline", "animated cash-flow model"],
    )
    expression=OriginalityGuard().check_text("Independent wording", [ref], artifact_kind="STORY")
    report=OriginalityGuard().authenticity_report(expression_report=expression,fingerprint=candidate,references=[ref])
    assert report.passed


def test_prior_own_collision_sets_high_channel_repetition_risk():
    fp=ConceptFingerprint(
        thesis="A daughter discovers a father's hidden sacrifice",
        primary_question="Why did he hide the sale?",
        causal_mechanism="secret sacrifice causes family conflict",
        audience_promise="reveal the sacrifice and emotional consequence",
        narrative_device="clue investigation confrontation",
        evidence_domains=["family documents"],
        beat_functions=["clue", "investigate", "confront", "reconcile"],
        visual_grammar_tags=["restrained close-ups", "document insert"],
    )
    ref=ReferenceRecord(kind=ReferenceKind.PRIOR_OWN,title="Earlier upload",concept_fingerprint=fp)
    expression=OriginalityGuard().check_text("Newly worded script", [ref], artifact_kind="STORY")
    report=OriginalityGuard().authenticity_report(expression_report=expression,fingerprint=fp,references=[ref])
    assert report.channel_repetition_risk == "HIGH"
    assert not report.passed


def test_thumbnail_concept_collision_is_blocked():
    ref=ReferenceRecord(
        kind=ReferenceKind.COMPETITOR,
        title="Retirement Trap",
        packaging_notes=["elderly couple staring at a red account balance with a giant warning triangle"],
    )
    report=OriginalityGuard().check_packaging(
        title="A Different Retirement Title",
        thumbnail_concept="elderly couple staring at a red account balance with a giant warning triangle",
        supporting_text="A different description",
        references=[ref],
        artifact_kind="RELEASE_PACKAGE",
    )
    assert not report.passed
    assert any(x.metric == "THUMBNAIL_CONCEPT_COLLISION" for x in report.findings)
