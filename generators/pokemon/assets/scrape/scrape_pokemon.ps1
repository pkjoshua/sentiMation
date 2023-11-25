# Specify the URL of the directory containing the files
$baseUrl = "https://img.pokemondb.net/artwork/large/"

# Send a request to the URL
$response = Invoke-WebRequest -Uri $baseUrl

# Check if the request was successful
if ($response.StatusCode -eq 200) {
    # Parse the HTML content to extract links to the files
    $htmlContent = $response.Content
    $matches = [regex]::Matches($htmlContent, 'href="([^"]+\.(mp3|jpg|png))"')

    # Count the number of matched files
    $fileCount = $matches.Count

    # Prompt for confirmation with the number of files
    $confirmationMessage = "There are $fileCount files in the directory. Do you want to download them all? (Y/N)"
    $confirmation = Read-Host -Prompt $confirmationMessage

    if ($confirmation -eq "Y" -or $confirmation -eq "y") {
        # Loop through the matched links and download each file
        foreach ($match in $matches) {
            $fileUrl = $baseUrl + $match.Groups[1].Value
            $fileName = [System.IO.Path]::GetFileName($fileUrl)
            
            # Use Invoke-WebRequest to download the file
            Invoke-WebRequest -Uri $fileUrl -OutFile $fileName
        }
    }
    else {
        Write-Host "Download cancelled."
    }
}
else {
    Write-Host "Failed to retrieve the website. Status code: $($response.StatusCode)"
}
