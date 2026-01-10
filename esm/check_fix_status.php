<?php
// check_fix_status.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$id = 2240;
$p = get_post($id);
$c = $p->post_content;

echo "<h1>Status Check ID $id</h1>";
if (strpos($c, 'class="trade-button"') !== false && strpos($c, 'class="trade-link"') !== false) {
    echo "⚠️ Double Class FOUND!<br>";
    echo "This page is likely broken.<br>";
} else {
    echo "✅ Double Class NOT found (or fixed).<br>";
}

if (preg_match('/\.trade-button\s*\{/', $c) && strpos($c, '</style>') === false) {
    echo "⚠️ Unclosed CSS FOUND!<br>";
} else {
    echo "✅ CSS Structure looks ok (or Regex mismatch).<br>";
}
?>