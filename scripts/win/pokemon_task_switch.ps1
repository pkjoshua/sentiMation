# Define the task name and task action
$repoPath = "C:\path\to\sentiMation" # Update to your local path
$userId = "$env:USERDOMAIN\$env:USERNAME"
$taskName = "Pokemon_Generator"
$taskAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-WindowStyle Hidden -c python $repoPath\generators\pokemon\call_pokemon.py" -WorkingDirectory "$repoPath\generators\pokemon"

# Check if the task already exists
$taskExists = Get-ScheduledTask | Where-Object {$_.TaskName -eq $taskName}

# If task doesn't exist, create it
if (-not $taskExists) {
    Write-Host "Task does not exist. Creating new task."
    $taskTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Tuesday,Thursday,Friday -At 10am
    $taskSettings = New-ScheduledTaskSettingsSet -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType ServiceAccount -RunLevel Highest

    # Register the task
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
