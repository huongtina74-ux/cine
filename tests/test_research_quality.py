from cinefactory.research_intelligence.technical_qc import evaluate_video_quality

def sample(width=1920, audio=True):
    return {"schema":"cine.research.observation.v1","source":"owned.mp4","duration_seconds":10.0,"streams":[{"type":"video","width":width,"height":1080}],"frames":[{"second":0}],"audio":{"present":audio}}

def test_passes_measured_constraints(tmp_path):
    output = evaluate_video_quality(sample(), tmp_path / "qc.json", expected_duration_seconds=10)
    assert output["passed"]
    assert len(output["checks"]) == 4

def test_fails_resolution_and_audio(tmp_path):
    output = evaluate_video_quality(sample(640, False), tmp_path / "qc.json")
    assert not output["passed"]
    assert {c["name"] for c in output["checks"] if not c["passed"]} == {"resolution", "audio_present"}
