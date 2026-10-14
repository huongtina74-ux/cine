param(
    [ValidateSet("status","test","api")]
    [string]$Mode = "status"
)
$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not (Test-Path (Join-Path $Repo ".git")) -or -not (Test-Path (Join-Path $Repo "pyproject.toml"))) {
    throw "Canonical CineFactory checkout not found: $Repo"
}
$Python = Join-Path $Repo ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { $Python = "python" }
$Artifacts = Join-Path (Split-Path -Parent $Repo) ".tools\workspace"
New-Item -ItemType Directory -Path $Artifacts -Force | Out-Null
Push-Location $Repo
try {
    $env:CINEFACTORY_CANONICAL_ROOT = $Repo
    Write-Host "CineFactory canonical repo: $Repo"
    Write-Host "Branch: $(git branch --show-current)"
    if ($Mode -eq "status") {
        Write-Host "Tracked/untracked changes: $(@(git status --porcelain).Count)"
        Write-Host "Generated test artifacts: $Artifacts"
    } elseif ($Mode -eq "test") {
        $Unique = (Get-Date -Format "yyyyMMdd_HHmmss") + "_" + [guid]::NewGuid().ToString("N").Substring(0, 8)
        & $Python -m pytest tests -q -p no:cacheprovider --basetemp (Join-Path $Artifacts "pytest_$Unique")
        exit $LASTEXITCODE
    } elseif ($Mode -eq "api") {
        & $Python -m uvicorn cinefactory.api.app:app --host 127.0.0.1 --port 8765
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}
