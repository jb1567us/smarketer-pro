$source = "c:\sandbox\esm\esm-trade-portal.php"
# Correct path for MU-Plugin
$ftp = "ftp://elk.lev3.com/public_html/wp-content/mu-plugins/esm-trade-portal.php"
$user = "elliotspencermor"
$pass = "!Meimeialibe4r"

try {
    Write-Host "Attempting Direct FTP Upload to mu-plugins..."
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass)
    $webclient.UploadFile($ftp, $source)
    Write-Host "Upload Success: esm-trade-portal.php updated in mu-plugins."
    
    # Trigger to make sure cache clears or just ping
    $response = Invoke-WebRequest -Uri "https://elliotspencermorgan.com/trade/?preview=Portal" -UseBasicParsing
    Write-Host "Triggered portal page. Code: $($response.StatusCode)"
} catch {
    Write-Error "Error: $_"
}
