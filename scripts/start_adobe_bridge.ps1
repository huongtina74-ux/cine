$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$StateRoot = Join-Path $RepoRoot "data\studio\adobe_bridge"
$TokenPath = Join-Path $StateRoot "token.txt"
$LogDir = Join-Path $RepoRoot "data\logs"
$Stdout = Join-Path $LogDir "adobe_bridge.stdout.log"
$Stderr = Join-Path $LogDir "adobe_bridge.stderr.log"
$BaseUrl = "http://127.0.0.1:8791"

if (Test-Path $TokenPath) {
    try {
        $token = (Get-Content $TokenPath -Raw).Trim()
        $headers = @{ Authorization = "Bearer $token" }
        $response = Invoke-WebRequest -UseBasicParsing -Headers $headers -Uri "$BaseUrl/v1/health" -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            exit 0
        }
    } catch {
    }
}

$uv = (Get-Command uv -ErrorAction SilentlyContinue).Source
if (!$uv) {
    $candidate = Join-Path $env:LOCALAPPDATA "hermes\bin\uv.exe"
    if (Test-Path $candidate) {
        $uv = $candidate
    }
}
if (!$uv) {
    throw "uv executable not found"
}

New-Item -ItemType Directory -Force -Path $StateRoot | Out-Null
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$args = @(
    "run",
    "--python", "3.11",
    "python", "-m", "cinefactory.adobe.server",
    "--root", "data/studio/adobe_bridge",
    "--host", "127.0.0.1",
    "--port", "8791"
)

Start-Process -FilePath $uv -ArgumentList $args -WorkingDirectory $RepoRoot -WindowStyle Hidden -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr
