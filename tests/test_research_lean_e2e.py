"""Zero-API closed-loop acceptance: real local video -> evidence -> department -> owned analytics -> learning."""
import shutil
import subprocess
import pytest

from cinefactory.research_intelligence.smart import observe_smart
from cinefactory.research_intelligence.core import create_department_tasks, assess_production
from cinefactory.research_intelligence.analytics_adapter import import_studio_csv, select_owned_video, map_retention_to_frames
from cinefactory.research_intelligence.learning import ingest_department_result, propose_learning
from cinefactory.research_intelligence.technical_qc import evaluate_video_quality
from cinefactory.research_intelligence.triage import select_departments


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg unavailable")
def test_zero_api_closed_loop_with_real_video_samples(tmp_path):
    paths = []
    for i in range(2):
        video = tmp_path / f"clip_{i}.mp4"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
             "-i", f"testsrc2=size=320x180:rate={4+i}", "-t", "3",
             "-c:v", "mpeg4", str(video)],
            check=True, capture_output=True
        )
        paths.append(video)
    ref = observe_smart(paths[0], tmp_path / "ref", max_frames=8, detect_changes=False)
    own = observe_smart(paths[1], tmp_path / "own", max_frames=8, detect_changes=False)
    assert ref["frames"] and own["frames"]
    dispatch = create_department_tasks(ref, tmp_path / "tasks", niche="Minecraft animation",
                                      reference_id="example", approved=True,
                                      departments=select_departments("Minecraft animation"))
    assert len(dispatch["tasks"]) == 5
    csv = tmp_path / "youtube_studio.csv"
    csv.write_text("Video ID,Views,Impressions,Impressions click-through rate (%),Average view duration,Watch time (hours)\nabcdefghijk,100,1200,3.5%,0:01:20,2.3\n", encoding="utf-8")
    studio = import_studio_csv(csv, tmp_path / "studio.json", period_start="2026-10-01",
                               period_end="2026-10-08", channel_id="UC-owned")
    analytics = select_owned_video(studio, "abcdefghijk")
    feedback = assess_production(ref, own, analytics["metrics"])
    feedback["owned_analytics_provenance"] = analytics["source"]
    qc = evaluate_video_quality(own, tmp_path / "qc.json", min_width=320, min_height=180, require_audio=False)
    assert qc["passed"]
    first = dispatch["tasks"][0]
    reviewed = ingest_department_result(first, {"findings": [
        {"claim": "Test an original hook with faster visual payoff", "status": "HYPOTHESIS", "evidence": [{"timestamp_seconds": 0}]}
    ]}, tmp_path / "review.json")
    learning = propose_learning(feedback, [reviewed], tmp_path / "learning.json")
    assert learning["state"] == "awaiting_experiment_and_human_approval"
    assert learning["metrics"]["ctr"] == pytest.approx(0.035)
    drops = map_retention_to_frames(own, [{"second": 0, "retention_pct": 98}, {"second": 1, "retention_pct": 70}])
    assert len(drops["drops"]) == 1
    assert drops["drops"][0]["nearest_sampled_frame"]
