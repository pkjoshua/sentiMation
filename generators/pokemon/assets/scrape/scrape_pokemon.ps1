# Directory where images will be saved
$saveDirectory = "D:\sentiMation\generators\pokemon\assets\scrape"

# Base URL
$baseUrl = "https://assets.pokemon.com/assets/cms2/img/pokedex/full/"

# Ensure save directory exists
if (-not (Test-Path -Path $saveDirectory)) {
    New-Item -Path $saveDirectory -ItemType Directory
}

# Loop through the sequence of numbers
1..151 | ForEach-Object {
    $number = $_.ToString("000")
    $fullUrl = "$baseUrl/$number.png"
    
    # Use Invoke-WebRequest to download the image
    $filePath = Join-Path -Path $saveDirectory -ChildPath "$number.png"
    Invoke-WebRequest -Uri $fullUrl -OutFile $filePath
}
