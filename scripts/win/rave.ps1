# Define the task name and task action
$repoPath = "C:\path\to\sentiMation" # Update to your local path
$userId = "$env:USERDOMAIN\$env:USERNAME"
$taskName = "rave_Generator"
$taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -c python $repoPath\generators\rave\call.py" -WorkingDirectory "$repoPath\generators\rave"

# Check if the task already exists
$taskExists = Get-ScheduledTask | Where-Object {$_.TaskName -eq $taskName}

# If task doesn't exist, create it
if (-not $taskExists) {
    Write-Host "Task does not exist. Creating new task."

    # Create two triggers, one for each schedule
    $saturdayTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At 8am
    $fridayTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At 6am

    $taskSettings = New-ScheduledTaskSettingsSet -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType ServiceAccount -RunLevel Highest

    # Register the task with both triggers
    Register-ScheduledTask -Action $taskAction -Principal $principal -Trigger $saturdayTrigger, $fridayTrigger -TaskName $taskName -Settings $taskSettings
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
