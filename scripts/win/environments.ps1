# Define the task name and task action
$repoPath = "C:\path\to\sentiMation" # Update to your local path
$userId = "$env:USERDOMAIN\$env:USERNAME"
$taskName = "environments_Generator"
$taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -c python $repoPath\generators\environments\call.py" -WorkingDirectory "$repoPath\generators\environments"

# Check if the task already exists
$taskExists = Get-ScheduledTask | Where-Object {$_.TaskName -eq $taskName}

# If task doesn't exist, create it
if (-not $taskExists) {
    Write-Host "Task does not exist. Creating new task."
    $taskTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Wednesday -At 6am
    $taskSettings = New-ScheduledTaskSettingsSet -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType ServiceAccount -RunLevel Highest

    Register-ScheduledTask -Action $taskAction -Principal $principal -Trigger $taskTrigger -TaskName $taskName -Settings $taskSettings
    Write-Host "Task created."
} else {
    # If task exists, toggle enable/disable
    Write-Host "Task already exists. Toggling state."
    $currentTask = Get-ScheduledTask -TaskName $taskName
    if ($currentTask.State -eq "Disabled") {
        Enable-ScheduledTask -TaskName $taskName
        Write-Host "Task enabled."
    } else {
        Disable-ScheduledTask -TaskName $taskName
        Write-Host "Task disabled."
    }
}
