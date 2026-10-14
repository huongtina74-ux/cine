"""Keep CineFactory running from its canonical checkout after Downloads cleanup."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def test_windows_research_scheduler_uses_canonical_data_root():
    text = (SCRIPTS / "research_scheduled_runner.ps1").read_text(encoding="utf8")
    assert "$PSScriptRoot" in text
    assert "data\\research_runtime" in text
    assert "CineResearch_DailyState" not in text
    assert "CineFactory_Autonomous_Build" not in text


def test_windows_comfyui_launcher_rejects_old_checkout_port_owner():
    text = (SCRIPTS / "start_comfyui.ps1").read_text(encoding="utf8")
    assert "COMFYUI_PORT_8188_OWNED_BY_DIFFERENT_CHECKOUT" in text
    assert "Get-CimInstance Win32_Process" in text
    assert 'Join-Path $RepoRoot ".tools\\ComfyUI"' in text


def test_no_hardcoded_old_checkout_in_execution_scripts():
    for path in SCRIPTS.rglob("*.ps1"):
        assert "CineFactory_Autonomous_Build" not in path.read_text(encoding="utf8"), str(path)


def test_test_runner_isolates_ephemeral_pytest_data():
    text = (SCRIPTS / "workspace_runner.ps1").read_text(encoding="utf8")
    assert 'Split-Path -Parent $Repo' in text
    assert "--basetemp" in text
