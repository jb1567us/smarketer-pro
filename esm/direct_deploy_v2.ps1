$source = "c:\sandbox\esm\esm-trade-portal.php"
# Try wp-content instead of content
$ftp = "ftp://elk.lev3.com/public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal.php"
$user = "elliotspencermor"
$pass = "!Meimeialibe4r"

try {
    Write-Host "Attempting Direct FTP Upload to wp-content..."
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass)
    $webclient.UploadFile($ftp, $source)
    Write-Host "Upload Success: esm-trade-portal.php updated in wp-content."
} catch {
    Write-Error "Error: $_"
}
