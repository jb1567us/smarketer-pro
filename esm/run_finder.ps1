$source = "c:\sandbox\esm\find_path.php"
$ftp = "ftp://elk.lev3.com/public_html/find_path.php"
$user = "elliotspencermor"
$pass = "!Meimeialibe4r"

try {
    Write-Host "Uploading find_path.php..."
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass)
    $webclient.UploadFile($ftp, $source)
    Write-Host "Upload Success."

    Write-Host "Executing find_path.php..."
    $response = Invoke-WebRequest -Uri "https://elliotspencermorgan.com/find_path.php" -UseBasicParsing
    Write-Host "Output: $($response.Content)"
} catch {
    Write-Error "Error: $_"
}
