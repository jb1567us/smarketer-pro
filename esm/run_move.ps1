$source = "c:\sandbox\esm\move_fix.php"
$ftp = "ftp://elk.lev3.com/public_html/move_fix.php"
$user = "elliotspencermor"
$pass = "!Meimeialibe4r"

try {
    Write-Host "Uploading move_fix.php..."
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass)
    $webclient.UploadFile($ftp, $source)
    Write-Host "Upload Success."

    Write-Host "Executing move_fix.php..."
    $response = Invoke-WebRequest -Uri "https://elliotspencermorgan.com/move_fix.php" -UseBasicParsing
    Write-Host "Output: $($response.Content)"
}
catch {
    Write-Error "Error: $_"
}
