# INSTALL/INSPECT ONLY on explicit user instruction. Does not execute scout now.
$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$script=Join-Path $repo 'scripts\daily_cinefactory_research_v199.ps1'
$name='CineFactory-Daily-YouTube-Research'
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "' + $script + '"') -WorkingDirectory $repo
$trigger=New-ScheduledTaskTrigger -Daily -At '08:00'
$principal=New-ScheduledTaskPrincipal -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel Limited
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 25)
$task=Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description 'CineFactory local owned YouTube research: public source scanning, history/competitor DB, no paid video agents.' -Force
$lookup=Get-ScheduledTask -TaskName $name
$info=Get-ScheduledTaskInfo -TaskName $name
Write-Host "CINEFACTORY_WINDOWS_TASK_REGISTERED $($lookup.TaskName) STATE=$($lookup.State) NEXT_RUN=$($info.NextRunTime.ToString('o')) LOGON=InteractiveToken"
