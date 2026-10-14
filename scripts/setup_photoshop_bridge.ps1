$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$PluginRoot = Join-Path $RepoRoot "integrations\adobe\photoshop"
$TokenPath = Join-Path $RepoRoot "data\studio\adobe_bridge\token.txt"
$ConfigPath = Join-Path $PluginRoot "bridge-config.local.js"

& (Join-Path $PSScriptRoot "start_adobe_bridge.ps1")

$deadline = (Get-Date).AddSeconds(20)
while (!(Test-Path $TokenPath) -and (Get-Date) -lt $deadline) {
    Start-Sleep -Milliseconds 250
}
if (!(Test-Path $TokenPath)) {
    throw "Adobe bridge token was not created"
}

$token = (Get-Content $TokenPath -Raw).Trim()
if ($token.Length -lt 32) {
    throw "Adobe bridge token is invalid"
}

$content = @"
globalThis.CINEFACTORY_BRIDGE_CONFIG = {
  baseUrl: "http://127.0.0.1:8791",
  token: "$token"
};
"@
Set-Content -Path $ConfigPath -Value $content -Encoding UTF8

Write-Host "Photoshop plugin prepared at:"
Write-Host "  $PluginRoot"
Write-Host ""
Write-Host "Load this folder with Adobe UXP Developer Tool after enabling Developer Mode."
Write-Host "The plugin requests full filesystem access so CineFactory can write deterministic sandbox exports."
