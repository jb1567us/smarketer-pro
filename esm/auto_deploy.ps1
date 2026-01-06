$source = "c:\sandbox\esm\deploy_visualizer_fix.php"
$ftp = "ftp://elk.lev3.com/public_html/deploy_visualizer_fix.php"
$user = "elliotspencermor"
$pass = "!Meimeialibe4r"

try {
    Write-Host "Starting FTP Upload..."
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass)
    $webclient.UploadFile($ftp, $source)
    Write-Host "Upload Success!"

    Write-Host "Triggering Deployment Script..."
    $response = Invoke-WebRequest -Uri "https://elliotspencermorgan.com/deploy_visualizer_fix.php" -UseBasicParsing
    Write-Host "Server Response: $($response.Content)"
} catch {
    Write-Error "Error: $_"
}
