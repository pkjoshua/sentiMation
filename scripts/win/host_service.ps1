# host_service.ps1
# Run in Windows PowerShell 5.1 as Administrator

$JobsRoot = Join-Path $env:ProgramData "A1111Scheduler\Jobs"
$LogsRoot = Join-Path $env:ProgramData "A1111Scheduler\Logs"
New-Item -ItemType Directory -Force -Path $JobsRoot, $LogsRoot | Out-Null

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://+:7070/")
$listener.Start()
Write-Host "Host agent listening on http://+:7070/ (Ctrl+C to stop)"

function New-JobScript {
  param(
    [string]$TaskName,
    [hashtable]$Env = @{},
    [array]$Steps
  )
  $scriptPath = Join-Path $JobsRoot ($TaskName + ".ps1")

  # Build environment exports robustly for Hashtable or PSCustomObject
  $envPairs = @()
  if ($Env -is [hashtable]) { $envPairs = $Env.GetEnumerator() } else { $envPairs = $Env.PSObject.Properties }
  $envLines = $envPairs | ForEach-Object {
    $k = if ($_.Name) { $_.Name } else { $_.Key }
    $v = $_.Value
    '$env:' + $k + ' = "' + ($v -replace '"','`"') + '"'
  } | Out-String

  $stepBlocks = $Steps | ForEach-Object {
    if ($_.type -eq "http") {
      $method = if ($_.http.method) { [string]$_.http.method } else { "POST" }
      $url = [string]$_.http.url
      $contentType = if ($_.http.contentType) { [string]$_.http.contentType } else { "application/json" }
      $bodyRaw = [string]$_.http.body
      $bodyB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($bodyRaw))
      $headerLines = ""
      if ($_.http.headers) {
        $headerLines = ($_.http.headers.PSObject.Properties | ForEach-Object {
          '  $headers["' + $_.Name + '"] = "' + ($_.Value -replace '"','`"') + '"'
        }) -join "`n"
      }
@"
Write-Host "`n=== STEP: $($_.name) ==="
`$timeoutSec = $([int]$_.timeoutSec)
`$retries = $([int]$_.retries)
`$method = "$method"
`$url = "$url"
`$contentType = "$contentType"
`$bodyB64 = "$bodyB64"
`$headers = @{}
$headerLines

for (`$attempt = 0; `$attempt -le `$retries; `$attempt++) {
  Write-Host ("[$($_.name)] Attempt {0}/{1}" -f (`$attempt+1), (`$retries+1))
  try {
    `$bytes = [Convert]::FromBase64String(`$bodyB64)
    `$body = [Text.Encoding]::UTF8.GetString(`$bytes)
    Invoke-RestMethod -Method `$method -Uri `$url -Headers `$headers -ContentType `$contentType -Body `$body -TimeoutSec `$timeoutSec | Out-Null
    Write-Host "[$($_.name)] Success"
    break
  } catch {
    `$errMsg = `$_.Exception.Message
    Write-Warning ("[$($_.name)] Error: {0}" -f `$errMsg)
  }
  if (`$attempt -eq `$retries) { throw ("[$($_.name)] Failed after {0} attempts." -f (`$retries+1)) }
}
"@
    } else {
@"
Write-Host "`n=== STEP: $($_.name) ==="
`$dockerArgs = "$($_.dockerArgs)"
`$timeoutSec = $([int]$_.timeoutSec)
`$retries = $([int]$_.retries)

for (`$attempt = 0; `$attempt -le `$retries; `$attempt++) {
  Write-Host ("[$($_.name)] Attempt {0}/{1}" -f (`$attempt+1), (`$retries+1))
  `$proc = Start-Process -FilePath "docker" -ArgumentList ("run --rm " + `$dockerArgs) -NoNewWindow -PassThru
  if (`$proc.WaitForExit(`$timeoutSec * 1000)) {
    if (`$proc.ExitCode -eq 0) { Write-Host "[$($_.name)] Success"; break }
    else { Write-Warning "[$($_.name)] ExitCode=`$($proc.ExitCode)" }
  } else {
    Write-Warning "[$($_.name)] Timeout after `$timeoutSec s"
    try { Stop-Process -Id `$proc.Id -Force -ErrorAction SilentlyContinue } catch {}
  }
  if (`$attempt -eq `$retries) { throw "[$($_.name)] Failed after `$($retries+1) attempts." }
}
"@
    }
  } | Out-String

  $content = @"
# Auto-generated for $TaskName
`$ErrorActionPreference = 'Stop'
`$ts = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
`$logFile = Join-Path "$LogsRoot" ("$TaskName`_`$ts.log")
Start-Transcript -Path `$logFile -Append

if (-not (Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue)) {
  Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  Start-Sleep -Seconds 25
}

$envLines
$stepBlocks

Stop-Transcript
"@

  Set-Content -Path $scriptPath -Value $content -Encoding UTF8
  Write-Host ("Generated job script: {0}" -f $scriptPath)
  return $scriptPath
}

function Execute-JobImmediately {
  param(
    [string]$TaskName,
    [hashtable]$Env = @{},
    [array]$Steps
  )
  
  # Create a temporary script for immediate execution
  $tempScriptPath = Join-Path $JobsRoot ($TaskName + "_immediate_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".ps1")
  
  # Build environment exports robustly for Hashtable or PSCustomObject
  $envPairs = @()
  if ($Env -is [hashtable]) { $envPairs = $Env.GetEnumerator() } else { $envPairs = $Env.PSObject.Properties }
  $envLines = $envPairs | ForEach-Object {
    $k = if ($_.Name) { $_.Name } else { $_.Key }
    $v = $_.Value
    '$env:' + $k + ' = "' + ($v -replace '"','`"') + '"'
  } | Out-String

  $stepBlocks = $Steps | ForEach-Object {
    if ($_.type -eq "http") {
      $method = if ($_.http.method) { [string]$_.http.method } else { "POST" }
      $url = [string]$_.http.url
      $contentType = if ($_.http.contentType) { [string]$_.http.contentType } else { "application/json" }
      $bodyRaw = [string]$_.http.body
      $bodyB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($bodyRaw))
      $headerLines = ""
      if ($_.http.headers) {
        $headerLines = ($_.http.headers.PSObject.Properties | ForEach-Object {
          '  $headers["' + $_.Name + '"] = "' + ($_.Value -replace '"','`"') + '"'
        }) -join "`n"
      }
@"
Write-Host "`n=== STEP: $($_.name) ==="
`$timeoutSec = $([int]$_.timeoutSec)
`$retries = $([int]$_.retries)
`$method = "$method"
`$url = "$url"
`$contentType = "$contentType"
`$bodyB64 = "$bodyB64"
`$headers = @{}
$headerLines

for (`$attempt = 0; `$attempt -le `$retries; `$attempt++) {
  Write-Host ("[$($_.name)] Attempt {0}/{1}" -f (`$attempt+1), (`$retries+1))
  try {
    `$bytes = [Convert]::FromBase64String(`$bodyB64)
    `$body = [Text.Encoding]::UTF8.GetString(`$bytes)
    Invoke-RestMethod -Method `$method -Uri `$url -Headers `$headers -ContentType `$contentType -Body `$body -TimeoutSec `$timeoutSec | Out-Null
    Write-Host "[$($_.name)] Success"
    break
  } catch {
    `$errMsg = `$_.Exception.Message
    Write-Warning ("[$($_.name)] Error: {0}" -f `$errMsg)
  }
  if (`$attempt -eq `$retries) { throw ("[$($_.name)] Failed after {0} attempts." -f (`$retries+1)) }
}
"@
    } else {
@"
Write-Host "`n=== STEP: $($_.name) ==="
`$dockerArgs = "$($_.dockerArgs)"
`$timeoutSec = $([int]$_.timeoutSec)
`$retries = $([int]$_.retries)

for (`$attempt = 0; `$attempt -le `$retries; `$attempt++) {
  Write-Host ("[$($_.name)] Attempt {0}/{1}" -f (`$attempt+1), (`$retries+1))
  `$proc = Start-Process -FilePath "docker" -ArgumentList ("run --rm " + `$dockerArgs) -NoNewWindow -PassThru
  if (`$proc.WaitForExit(`$timeoutSec * 1000)) {
    if (`$proc.ExitCode -eq 0) { Write-Host "[$($_.name)] Success"; break }
    else { Write-Warning "[$($_.name)] ExitCode=`$($proc.ExitCode)" }
  } else {
    Write-Warning "[$($_.name)] Timeout after `$timeoutSec s"
    try { Stop-Process -Id `$proc.Id -Force -ErrorAction SilentlyContinue } catch {}
  }
  if (`$attempt -eq `$retries) { throw "[$($_.name)] Failed after `$($retries+1) attempts." }
}
"@
    }
  } | Out-String

  $content = @"
# Immediate execution script for $TaskName
`$ErrorActionPreference = 'Stop'
`$ts = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
`$logFile = Join-Path "$LogsRoot" ("$TaskName`_immediate_`$ts.log")
Start-Transcript -Path `$logFile -Append

if (-not (Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue)) {
  Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  Start-Sleep -Seconds 25
}

$envLines
$stepBlocks

Stop-Transcript
"@

  Set-Content -Path $tempScriptPath -Value $content -Encoding UTF8
  
  # Execute the script immediately
  try {
    $result = Start-Process -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$tempScriptPath`"" -NoNewWindow -PassThru -Wait
    $logFile = Join-Path $LogsRoot ($TaskName + "_immediate_" + (Get-Date -Format "yyyy-MM-dd_HH-mm-ss") + ".log")
    return @{status="ok"; log=$logFile; exitCode=$result.ExitCode}
  } catch {
    return @{status="error"; error=$_.Exception.Message}
  }
}

function Ensure-Task {
  param(
    [string]$TaskName,
    [string]$TimeHHmm,
    [string]$ScriptPath,
    [string[]]$Days = @()
  )
  $time = [DateTime]::ParseExact($TimeHHmm,'HH:mm',$null)
  if ($Days -and $Days.Count -gt 0) {
    try {
      $dow = @()
      foreach ($d in $Days) { $dow += [System.Enum]::Parse([System.DayOfWeek], $d, $true) }
      $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $dow -At $time
    } catch {
      # Fallback to daily if parsing failed
      $trigger  = New-ScheduledTaskTrigger -Daily -At $time
    }
  } else {
    $trigger  = New-ScheduledTaskTrigger -Daily -At $time
  }
  $settings = New-ScheduledTaskSettingsSet -WakeToRun:$true -AllowStartIfOnBatteries:$true -StartWhenAvailable:$true -MultipleInstances Queue
  $action   = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""

  if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
    Set-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings | Out-Null
  } else {
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -User $env:UserName | Out-Null
  }
}

function Remove-TaskSafely {
  param(
    [string]$TaskName
  )
  try {
    if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
      Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop | Out-Null
      Write-Host ("[DELETE] Unregistered Task: {0}" -f $TaskName)
    } else {
      Write-Host ("[DELETE] Task not found: {0}" -f $TaskName)
    }
  } catch {
    Write-Warning ("[DELETE] Error removing task {0}: {1}" -f $TaskName, $_.Exception.Message)
    throw
  }
  # Optionally remove generated script
  try {
    $scriptPath = Join-Path $JobsRoot ($TaskName + ".ps1")
    if (Test-Path $scriptPath) {
      Remove-Item -Path $scriptPath -Force -ErrorAction SilentlyContinue
      Write-Host ("[DELETE] Removed script: {0}" -f $scriptPath)
    }
  } catch {}
}

try {
  while ($true) {
    $ctx = $listener.GetContext()  # <-- this blocks until a request comes in
    try {
      $reader = New-Object System.IO.StreamReader($ctx.Request.InputStream, $ctx.Request.ContentEncoding)
      $body = $reader.ReadToEnd()
      $reader.Close()

      if ($ctx.Request.HttpMethod -eq "POST" -and $ctx.Request.Url.AbsolutePath -eq "/schedule") {
        $payload = $body | ConvertFrom-Json
        $envTable = if ($null -eq $payload.Env) { @{} } else { $payload.Env }
        $days = @()
        if ($payload.PSObject.Properties.Name -contains 'Days' -and $null -ne $payload.Days) { $days = $payload.Days }

        $stepCount = if ($null -eq $payload.Steps) { 0 } else { $payload.Steps.Count }
        $daysText = if ($days -and $days.Count -gt 0) { ($days -join ', ') } else { '(daily)' }
        Write-Host ("[SCHEDULE] TaskName={0} Time={1} Days={2} Steps={3}" -f $payload.TaskName, $payload.Time, $daysText, $stepCount)

        $scriptPath = New-JobScript -TaskName $payload.TaskName -Env $envTable -Steps $payload.Steps
        Ensure-Task -TaskName $payload.TaskName -TimeHHmm $payload.Time -ScriptPath $scriptPath -Days $days
        Write-Host ("[SCHEDULE] Registered in Task Scheduler: {0} at {1} Days={2}" -f $payload.TaskName, $payload.Time, $daysText)

        $json = @{status="ok"; script=$scriptPath} | ConvertTo-Json -Compress
        $resp = [Text.Encoding]::UTF8.GetBytes($json)
        $ctx.Response.ContentType = "application/json"
        $ctx.Response.OutputStream.Write($resp,0,$resp.Length)
      } elseif ($ctx.Request.HttpMethod -eq "POST" -and $ctx.Request.Url.AbsolutePath -eq "/run-now") {
        $payload = $body | ConvertFrom-Json
        $envTable = if ($null -eq $payload.Env) { @{} } else { $payload.Env }
        $stepCount = if ($null -eq $payload.Steps) { 0 } else { $payload.Steps.Count }
        Write-Host ("[RUN-NOW] TaskName={0} Steps={1}" -f $payload.TaskName, $stepCount)
        $result = Execute-JobImmediately -TaskName $payload.TaskName -Env $envTable -Steps $payload.Steps
        if ($result -and $result.status -eq 'ok') {
          Write-Host ("[RUN-NOW] Completed: ExitCode={0} Log={1}" -f $result.exitCode, $result.log)
        } else {
          Write-Warning ("[RUN-NOW] Error: {0}" -f ($result.error))
        }
        
        $json = $result | ConvertTo-Json -Compress
        $resp = [Text.Encoding]::UTF8.GetBytes($json)
        $ctx.Response.ContentType = "application/json"
        $ctx.Response.OutputStream.Write($resp,0,$resp.Length)
      } elseif ($ctx.Request.HttpMethod -eq "POST" -and $ctx.Request.Url.AbsolutePath -eq "/delete") {
        $payload = $body | ConvertFrom-Json
        $taskName = [string]$payload.TaskName
        Write-Host ("[DELETE] Request TaskName={0}" -f $taskName)
        try {
          Remove-TaskSafely -TaskName $taskName
          $json = @{status="ok"} | ConvertTo-Json -Compress
          $resp = [Text.Encoding]::UTF8.GetBytes($json)
          $ctx.Response.ContentType = "application/json"
          $ctx.Response.OutputStream.Write($resp,0,$resp.Length)
        } catch {
          $ctx.Response.StatusCode = 500
          $errorJson = @{status="error"; error=$_.Exception.Message} | ConvertTo-Json -Compress
          $resp = [Text.Encoding]::UTF8.GetBytes($errorJson)
          $ctx.Response.ContentType = "application/json"
          $ctx.Response.OutputStream.Write($resp,0,$resp.Length)
        }
      } elseif ($ctx.Request.HttpMethod -eq "GET" -and $ctx.Request.Url.AbsolutePath -eq "/health") {
        $json = @{status="ok"} | ConvertTo-Json -Compress
        $resp = [Text.Encoding]::UTF8.GetBytes($json)
        $ctx.Response.ContentType = "application/json"
        $ctx.Response.OutputStream.Write($resp,0,$resp.Length)
      } else {
        $ctx.Response.StatusCode = 404
      }
    } catch {
      $ctx.Response.StatusCode = 500
      $errorJson = @{status="error"; error=$_.Exception.Message} | ConvertTo-Json -Compress
      $resp = [Text.Encoding]::UTF8.GetBytes($errorJson)
      $ctx.Response.ContentType = "application/json"
      $ctx.Response.OutputStream.Write($resp,0,$resp.Length)
      Write-Error ("[ERROR] " + $_.Exception.Message)
    }
    $ctx.Response.Close()
  }
} finally {
  $listener.Stop()
  $listener.Close()
  Write-Host "Host agent stopped."
}
