$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ComfyRoot = Join-Path $RepoRoot ".tools\ComfyUI"
$Python = Join-Path $ComfyRoot ".venv\Scripts\python.exe"
$Health = "http://127.0.0.1:8188/object_info"
$LogDir = Join-Path $RepoRoot "data\logs"
$Stdout = Join-Path $LogDir "comfyui.stdout.log"
$Stderr = Join-Path $LogDir "comfyui.stderr.log"

try {
    $response = Invoke-WebRequest -UseBasicParsing -Uri $Health -TimeoutSec 2
    if ($response.StatusCode -eq 200) {
        $owned = @(Get-CimInstance Win32_Process -Filter "name='python.exe'" |
            Where-Object { $_.CommandLine -like ('*' + $Python + '*') -and $_.CommandLine -like '*main.py*' })
        if ($owned.Count -gt 0) { exit 0 }
        throw "COMFYUI_PORT_8188_OWNED_BY_DIFFERENT_CHECKOUT: refuse to accept stale service."
    }
} catch {
    if ($_.Exception.Message -like '*DIFFERENT_CHECKOUT*') { throw }
}

if (!(Test-Path $Python)) {
    throw "ComfyUI Python runtime not found: $Python"
}

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$env:PYTHONUTF8 = "1"
$env:CINEFACTORY_COMFYUI = "http://127.0.0.1:8188"

$args = @(
    "main.py",
    "--listen", "127.0.0.1",
    "--port", "8188",
    "--disable-auto-launch",
    "--disable-all-custom-nodes",
    "--disable-api-nodes"
)

Start-Process -FilePath $Python -ArgumentList $args -WorkingDirectory $ComfyRoot -WindowStyle Hidden -RedirectStandardOutput $Stdout -RedirectStandardError $Stderr
