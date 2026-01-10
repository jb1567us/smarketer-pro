$url = "https://wordpress.org/latest.zip"
$zip = "core_update.zip"
$extractPath = "temp_core_update"

Write-Host "Downloading WordPress..."
Invoke-WebRequest -Uri $url -OutFile $zip

Write-Host "Unzipping..."
Expand-Archive -Path $zip -DestinationPath $extractPath -Force

Write-Host "Done."
