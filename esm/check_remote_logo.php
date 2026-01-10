<?php
// check_remote_logo.php
$logo_url = 'https://elliotspencermorgan.com/logo.png';
$headers = get_headers($logo_url);
if (strpos($headers[0], '200') !== false) {
    echo "Logo exists at $logo_url";
} else {
    echo "Logo NOT found at $logo_url";
}
?>
