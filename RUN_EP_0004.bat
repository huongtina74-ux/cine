@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
if not exist data\logs mkdir data\logs
echo === CineFactory: san xuat EP_0004 (render khoang 2 gio, KHONG tat may / khong de may ngu) ===
echo Nhat ky: data\logs\EP_0004_produce.log
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "python scripts\produce_long_slide_episode.py --channel zoomi --episode EP_0004 2>&1 | Tee-Object -FilePath data\logs\EP_0004_produce.log; exit $LASTEXITCODE"
set CODE=%ERRORLEVEL%
echo.
echo === KET THUC, ma thoat %CODE% (0 = xong, 3 = QC bao loi, 2 = bi chan) ===
echo Bao Claude "xong roi" de Claude doc ket qua va kiem tra video.
pause
