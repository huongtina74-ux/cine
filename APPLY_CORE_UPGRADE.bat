@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
echo [1/3] Cap nhat .claude (skill produce-episode, agent showrunner/blender-td, settings)
echo      Ban cu da sao luu o backups\core_upgrade_20261015\claude\
xcopy /E /Y /I /Q "update_claude" ".claude" >nul || goto :fail
echo [2/3] Kiem tra trang thai nha may
python tools\cf_status.py
echo.
echo [3/3] Chay test vong khep kin (khong can Blender, mat khoang 2-3 phut)
if not exist data\tmp mkdir data\tmp
python -m pytest tests\test_long_slide_closed_loop.py tests\test_cf_tools.py -q -p no:cacheprovider --basetemp=data\tmp\pytest
if errorlevel 1 goto :fail
echo.
echo === XONG. Doc data\animal_long_slide\series\zoomi\APPROVAL_POINT1.md de bat den xanh EP_0004 ===
pause
exit /b 0
:fail
echo.
echo === CO LOI - chup man hinh nay gui Claude ===
pause
exit /b 1
