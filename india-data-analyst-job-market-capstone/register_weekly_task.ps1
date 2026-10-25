$ErrorActionPreference = 'Stop'
$Project = Split-Path -Parent $MyInvocation.MyCommand.Path
$TaskName = 'India Data Analyst Job Market Weekly Collection'
$Action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$Project\run_weekly.ps1`"" -WorkingDirectory $Project
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 8:00AM
$Settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description 'Collect Adzuna India and Chennai analyst job search snapshots and refresh aggregate reports.' -Force
Write-Host "Registered '$TaskName'. Edit the trigger in Windows Task Scheduler to change its time."
