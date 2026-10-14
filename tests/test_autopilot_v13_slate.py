import shutil
from pathlib import Path
import pytest
from cinefactory.appctx import build_context
from cinefactory.autopilot import AutopilotRequest, AutopilotRunner


@pytest.mark.skipif(shutil.which('ffmpeg') is None or shutil.which('ffprobe') is None, reason='ffmpeg required')
def test_autopilot_slate_has_asset_keyframe_pilot_and_dailies(tmp_path:Path):
    src=Path(__file__).resolve().parents[1]
    # build_context expects config/knowledge/model registry in root; use project root but isolate DB/data through cwd.
    ctx=build_context(src)
    result=AutopilotRunner(ctx).run(AutopilotRequest(
        prompt='A wholly original family choice changes a relationship', production_mode='slate',
        tts_mode='none', master_4k=False, include_prior_projects=False, require_visual_qc=False,
        originality_strict=False,
    ))
    assert result.success, result.warnings
    names=[x.name for x in result.stages]
    assert 'asset_factory' in names
    assert 'storyboard_keyframe_gate' in names
    assert 'production' in names
    project_root=src/'data'/'projects'/result.project_id
    assert (project_root/'reports'/'asset_factory.json').exists()
    assert (project_root/'reports'/'storyboard_gate.json').exists()
    assert (project_root/'reports'/'dailies.json').exists()
