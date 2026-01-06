<?php
echo "cURL: " . (function_exists('curl_init') ? 'OK' : 'MISSING') . "\n";
echo "Zip: " . (class_exists('ZipArchive') ? 'OK' : 'MISSING') . "\n";
?>
