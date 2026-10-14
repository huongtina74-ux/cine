param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("daily","health","pod","inspect")]
    [string]$Mode
)
$ErrorActionPreference = "Stop"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$State = Join-Path $Repo 'data\research_runtime'
$Company = 'C:\Users\ADMIN\Downloads\Company Youtube'
$Python = Join-Path $Repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $Python)) { $Python = (Get-Command python -ErrorAction Stop).Source }
if (-not (Test-Path (Join-Path $Repo '.git'))) { throw "CANONICAL_GIT_MISSING" }
if (-not (Test-Path -LiteralPath $State)) { throw "CANONICAL_RESEARCH_STATE_MISSING: $State" }
if ($Mode -eq "inspect") {
    Write-Output "REPO=$Repo"
    Write-Output "STATE=$State"
    Write-Output "PYTHON=$Python"
    Write-Output "COMPANY=$Company"
    exit 0
}
if ($Mode -eq "daily" -and -not (Test-Path $Company)) { throw "COMPANY_SOURCE_MISSING" }
Push-Location $Repo
try {
    if ($Mode -eq "daily") {
        $Log = Join-Path $State 'scheduled_daily.log'
        & $Python -m cinefactory.research_intelligence daily-run --company-root $Company --state-root $State --profile focused --timeout 600 --retry *>> $Log
    } elseif ($Mode -eq "health") {
        $Log = Join-Path $State 'scheduled_health.log'
        & $Python -m cinefactory.research_intelligence daily-health --state-root $State --max-age-hours 36 *>> $Log
    } elseif ($Mode -eq "pod") {
        foreach ($name in @("approved_pods","verified_bridges","pod_dispatch_daily")) {
            New-Item -Path (Join-Path $State $name) -ItemType Directory -Force | Out-Null
        }
        $Log = Join-Path $State 'scheduled_pod_watch.log'
        & $Python -m cinefactory.research_intelligence.pod_daily_runner --pods-root (Join-Path $State 'approved_pods') --bridges-root (Join-Path $State 'verified_bridges') --state-root (Join-Path $State 'pod_dispatch_daily') *>> $Log
    }
    $Status = $LASTEXITCODE
    if ($Status -ne 0) { Write-Output "CINE_RESEARCH_RUN_NOT_COMPLETE mode=$Mode code=$Status"; exit $Status }
} finally {
    Pop-Location
}
