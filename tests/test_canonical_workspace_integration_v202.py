"""Regression gates for canonical CineFactory workspace wiring.

Static tests only; never register a Windows task or launch a live scanner.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LEGACY_LOCATION = "CineFactory_Autonomous_Build"


def test_canonical_checkout_has_single_executable_project():
    assert (ROOT / "pyproject.toml").is_file()
    assert (ROOT / "cinefactory" / "studio" / "company.py").is_file()
    assert (ROOT / "cinefactory" / "research_intelligence" / "__init__.py").is_file()


def test_daily_research_resolves_repo_from_own_script_location():
    for filename in (
        "daily_cinefactory_research_v199.ps1",
        "install_daily_cinefactory_task_v199.ps1",
    ):
        text = (SCRIPTS / filename).read_text(encoding="utf-8")
        assert "$PSScriptRoot" in text
        assert LEGACY_LOCATION not in text


def test_workspace_runner_keeps_pytest_temp_outside_git_root():
    script = (SCRIPTS / "workspace_runner.ps1").read_text(encoding="utf-8")
    assert 'Split-Path -Parent $Repo' in script
    assert '--basetemp' in script
    assert 'pytest' in script


def test_diagnostic_and_premium_visual_gates_stay_separate():
    code = (ROOT / "cinefactory" / "studio" / "company_handlers.py").read_text(encoding="utf-8")
    assert code.count("self.config.allow_diagnostic_slate") >= 3
    policy = (ROOT / "cinefactory" / "qc" / "visual_policy.py").read_text(encoding="utf-8")
    assert "normalized_visual_review" in policy
