<?php
require_once('wp-load.php');
// Final Verification - Unique File
echo "<pre>";
$p1 = 1927;
echo "PORTAL (1927) Verifying:\n";
$tags1 = get_the_tags($p1);
if ($tags1) {
    foreach ($tags1 as $t)
        echo "- " . $t->name . "\n";
}
echo "\nRED PLANET (1704) Verifying:\n";
$p2 = 1704;
$tags2 = get_the_tags($p2);
if ($tags2) {
    foreach ($tags2 as $t)
        echo "- " . $t->name . "\n";
}
echo "</pre>";
?>