<?php
$files = ['deploy_dashboard.php', 'check_dashboard.php'];
foreach ($files as $f) {
    if (file_exists($f)) {
        unlink($f);
        echo "Deleted $f<br>";
    } else {
        echo "$f not found<br>";
    }
}
// Delete self
unlink(__FILE__);
echo "Cleanup complete.";
?>
