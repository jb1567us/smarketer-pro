<?php
require_once('wp-load.php');

echo "<pre>";
// Spot Check 1: Portal (ID 1927)
// Expected: NO "Art Deco", YES Colors
$p1 = 1927;
echo "Checking 'Portal' (ID $p1):\n";
$tags1 = get_the_tags($p1);
if ($tags1) {
    foreach ($tags1 as $t)
        echo "- " . $t->name . "\n";
} else {
    echo "No tags.\n";
}

echo "\n";

// Spot Check 2: Red Planet (ID 1704)
// Expected: YES "Red"
$p2 = 1704;
echo "Checking 'Red Planet' (ID $p2):\n";
$tags2 = get_the_tags($p2);
if ($tags2) {
    foreach ($tags2 as $t)
        echo "- " . $t->name . "\n";
} else {
    echo "No tags.\n";
}

echo "</pre>";
?>