# mini_host.ps1
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://+:7070/")
$listener.Start()
Write-Host "Listening on http://+:7070/"

while ($listener.IsListening) {
    $ctx = $listener.GetContext()

    # read the body properly
    $reader = New-Object System.IO.StreamReader($ctx.Request.InputStream, $ctx.Request.ContentEncoding)
    $body = $reader.ReadToEnd()
    $reader.Close()

    Write-Host "Request received: $($ctx.Request.HttpMethod) $($ctx.Request.Url.AbsolutePath)"
    Write-Host "Body: $body"

    $resp = [Text.Encoding]::UTF8.GetBytes("{""status"":""received""}")
    $ctx.Response.ContentType = "application/json"
    $ctx.Response.OutputStream.Write($resp,0,$resp.Length)
    $ctx.Response.Close()
}
