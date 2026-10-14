# Nightly unattended CineFactory loop with Claude Code headless (print mode).
# Stage 1 research -> Stage 2 produce (plan, render, Director Cut, auto edit, QC loop, policy, package) -> phone message.
# Register once (as the owner, PowerShell in the repo root):
#   $a = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PWD\tools\nightly_factory.ps1`""
#   $t = New-ScheduledTaskTrigger -Daily -At 10:00pm
#   Register-ScheduledTask -TaskName "CineFactory Nightly" -Action $a -Trigger $t
# Turn it on only after 3 episodes in a row passed QC with you watching.
param(
    [string]$Channel = "zoomi",
    [string]$Niche = "kids 3D animal long slide",
    [int]$Count = 1,
    [int]$Seconds = 330,
    [switch]$SkipResearch,
    [switch]$SkipProduce
)
$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$LogDir = Join-Path $Root "data\logs\nightly"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmm"
$Common = "Work fully unattended: never ask questions; when information is missing pick the option that matches the latest OWNER decision in tools/cf_decision.py and note it in HANDOFF.md. Never upload, never spend credits."
$Tools = "Read,Grep,Glob,Edit,Write,Task," +
  "Bash(python scripts/plan_long_slide_series.py:*),Bash(python scripts/make_long_slide_episode.py:*),Bash(python scripts/produce_long_slide_episode.py:*),Bash(python scripts/assemble_long_slide_episode.py:*)," +
  "Bash(python tools/cf_status.py:*),Bash(python tools/cf_qc.py:*),Bash(python tools/cf_director_cut.py:*),Bash(python tools/cf_auto_edit.py:*)," +
  "Bash(python tools/cf_policy_check.py:*),Bash(python tools/cf_research_stats.py:*),Bash(python tools/cf_decision.py:*),Bash(ffprobe:*),Bash(ffmpeg:*)," +
  "mcp__vidiq__vidiq_outliers,mcp__vidiq__vidiq_trending_videos,mcp__vidiq__vidiq_channel_videos,mcp__vidiq__vidiq_keyword_research,mcp__vidiq__vidiq_video_comments"

function Run-Stage([string]$Name, [string]$Prompt, [int]$Turns) {
    $Log = Join-Path $LogDir "$($Stamp)_$Name.json"
    claude -p $Prompt --output-format json --max-turns $Turns --permission-mode acceptEdits --allowedTools $Tools |
        Out-File -Encoding utf8 $Log
    return @{ Code = $LASTEXITCODE; Log = $Log }
}

$Summary = @()
if (-not $SkipResearch) {
    $r = Run-Stage "research" ("Use the nightly-research skill for CHANNEL=$Channel NICHE=`"$Niche`". $Common " +
                               "Finish with: report path, median views, number of outliers, the 3 proposals in one line each.") 60
    $Summary += "research exit=$($r.Code)"
    python tools/cf_notify.py "CineFactory research $Stamp (exit $($r.Code))" --file $r.Log | Out-Null
}
if (-not $SkipProduce) {
    $p = Run-Stage "produce" ("Use the produce-episode skill: CHANNEL=$Channel COUNT=$Count SECONDS=$Seconds PROFILE=kids_long. $Common " +
                              "Run scripts/produce_long_slide_episode.py for every episode that is already greenlit and not handed off " +
                              "(see tools/cf_status.py). Never greenlight. Then plan $Count new episode(s) for the owner's morning greenlight. " +
                              "Finish with one paragraph: episode ids, QC verdict per episode, fix loops used, policy verdict, HANDOFF.md paths, new plans waiting for greenlight.") 160
    $Summary += "produce exit=$($p.Code)"
    python tools/cf_notify.py "CineFactory produce $Stamp (exit $($p.Code))" --file $p.Log | Out-Null
}
"$Stamp  $($Summary -join '  ')" | Out-File -Append -Encoding utf8 (Join-Path $LogDir "nightly_index.txt")
