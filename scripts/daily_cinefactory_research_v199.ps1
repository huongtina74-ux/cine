# CineFactory DAILY LOCAL scout: no key, no vidIQ, no Claude spend.
# A fixed public-only metadata and storyboard research job. Do not run any
# external repositories or download complete YouTube media.
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$script = Join-Path $repo 'scripts\run_daily_cinefactory_youtube_v199.py'
$python = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { $python = 'python' }
$logdir = Join-Path $repo 'data\research\youtube_breakout\logs'
New-Item -ItemType Directory -Force -Path $logdir | Out-Null
if (-not (Test-Path -LiteralPath $script)) { throw 'Missing owned research script' }
if (-not (Get-Command $python -ErrorAction SilentlyContinue)) { throw 'Missing local research interpreter' }
Set-Location -LiteralPath $repo
$timestamp = (Get-Date).ToString('yyyyMMdd_HHmmss')
$log = Join-Path $logdir ('scheduled_cinefactory_' + $timestamp + '.log')
& $python $script --live --with-storyboards --max-metadata 20 --search-per-lane 8 --storyboard-count 2 *>> $log
if ($LASTEXITCODE -ne 0) {
  Add-Content $log ('Research failed with exit ' + $LASTEXITCODE)
  exit $LASTEXITCODE
}
# v1.6.41: second research workflow reads the first workflow's saved
# evidence, independently scans the bounded UNKNOWN FORMAT frontier and
# creates two strictly separated reports. Branch 2 only inspects formats
# explicitly approved by the studio owner (zero approvals by default).
# No subscriptions, Claude Code, uploads or video stream downloads.
$branchScript = Join-Path $repo 'scripts\run_two_track_research_v201.py'
if (-not (Test-Path -LiteralPath $branchScript)) {
  Add-Content $log 'TWO_TRACK_RESEARCH_SCRIPT_MISSING'
  exit 3
}
# v211: lightweight public GitHub technology discovery rotates across the
# company's approved-for-research FORMAT ONTOLOGY. Zero paid APIs, no cloning
# or installing, and only append-only pending R&D evidence.
& $python $branchScript --with-frontier --scan-approved --discover-technologies *>> $log
if ($LASTEXITCODE -ne 0) {
  Add-Content $log ('Two-track research failed with exit ' + $LASTEXITCODE)
  exit $LASTEXITCODE
}
Add-Content $log ('DAILY_TWO_TRACK_RESEARCH_COMPLETED ' + (Get-Date).ToString('o'))
