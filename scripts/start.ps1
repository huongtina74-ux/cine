$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root
& .\.venv\Scripts\uvicorn.exe cinefactory.api.app:app --host 127.0.0.1 --port 8765
