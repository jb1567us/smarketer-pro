$source = "c:\sandbox\esm\esm-trade-portal.php"
# Correct path for Wordpress plugin
$ftp = "ftp://elk.lev3.com/public_html/content/plugins/esm-trade-portal/esm-trade-portal.php"
$user = "elliotspencermor"
$pass = "!Meimeialibe4r"

try {
    Write-Host "Starting Direct FTP Upload of Plugin File..."
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass)
    $webclient.UploadFile($ftp, $source)
    Write-Host "Upload Success: esm-trade-portal.php updated directly."
} catch {
    Write-Error "Error: $_"
}
