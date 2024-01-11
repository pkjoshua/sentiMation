# Define the task name and task action
$taskName = "dogshow_Generator"
$taskAction = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-WindowStyle Hidden -c python D:\sentiMation\generators\dogshow\call.py' -WorkingDirectory 'D:\sentiMation\generators\dogshow'

# Check if the task already exists
$taskExists = Get-ScheduledTask | Where-Object {$_.TaskName -eq $taskName}

# If task doesn't exist, create it
if (-not $taskExists) {
    Write-Host "Task does not exist. Creating new task."

    # Create two triggers, one for each schedule
    $saturdayTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Saturday -At 6am
    $fridayTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Friday -At 12pm

    $taskSettings = New-ScheduledTaskSettingsSet -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId "PALADIN1\josh" -LogonType ServiceAccount -RunLevel Highest

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
