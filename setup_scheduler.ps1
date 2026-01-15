
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "src/automation_routines/daily_health_check.py" -WorkingDirectory "$PWD"
$Trigger = New-ScheduledTaskTrigger -Daily -At 7am
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -LogonType Interactive
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

$TaskName = "B2B_Outreach_DailyHealthCheck"

Register-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -TaskName $TaskName -Description "Daily Health Check for WordPress Automation" -Force

Write-Host "✅ Task '$TaskName' created successfully. It will run daily at 7 AM."
Write-Host "To run it now manually: Start-ScheduledTask -TaskName '$TaskName'"
