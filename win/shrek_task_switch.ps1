# Define the task name and task action
$taskName = "Shrek_Generator"
$taskAction1 = New-ScheduledTaskAction -Execute 'python' -Argument 'D:\sentiMation\generators\shrek_gen\shrek_CN_image_gen.py'
$taskAction2 = New-ScheduledTaskAction -Execute 'python' -Argument 'D:\sentiMation\generators\shrek_gen\shrek_generatorv1.py'

# Check if the task already exists
$taskExists = Get-ScheduledTask | Where-Object {$_.TaskName -eq $taskName}

# If task doesn't exist, create it
if ($taskExists -eq $null) {
    Write-Host "Task does not exist. Creating new task."
    $taskActions = @($taskAction1, $taskAction2)
    $taskTrigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Thursday -At 9am
    Register-ScheduledTask -Action $taskActions -Trigger $taskTrigger -TaskName $taskName -User "NT AUTHORITY\SYSTEM" -Settings (New-ScheduledTaskSettingsSet -WakeToRun)
    Write-Host "Task created."
}
else {
    # If task exists, toggle enable/disable
    Write-Host "Task already exists. Toggling state."
    $currentState = (Get-ScheduledTask -TaskName $taskName).State
    if ($currentState -eq "Disabled") {
        Enable-ScheduledTask -TaskName $taskName
        Write-Host "Task enabled."
    }
    else {
        Disable-ScheduledTask -TaskName $taskName
        Write-Host "Task disabled."
    }
}
