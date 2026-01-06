$source = "c:\sandbox\esm\esm-trade-portal.php"
$ftp = "ftp://elk.lev3.com/public_html/esm-trade-portal.php"
$user = "elliotspencermor"
$pass = "!Meimeialibe4r"

try {
    Write-Host "Uploading to public_html root..."
    $webclient = New-Object System.Net.WebClient
    $webclient.Credentials = New-Object System.Net.NetworkCredential($user, $pass)
    $webclient.UploadFile($ftp, $source)
    Write-Host "Upload Success! File is at /public_html/esm-trade-portal.php"
} catch {
    Write-Error "Error: $_"
}
