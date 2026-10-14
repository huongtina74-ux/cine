$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python -m cinefactory.cli block-factory --poll-seconds 0.05
