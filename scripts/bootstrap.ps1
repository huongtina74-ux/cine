$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
$Python = if ($env:PYTHON) { $env:PYTHON } else { "python" }
& $Python -m venv .venv
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]"
New-Item -ItemType Directory -Force -Path data\projects, data\artifacts, workflows | Out-Null
& .\.venv\Scripts\cinefactory.exe doctor
Write-Host "CineFactory installed. Start API with: .\.venv\Scripts\uvicorn.exe cinefactory.api.app:app --host 127.0.0.1 --port 8765"
