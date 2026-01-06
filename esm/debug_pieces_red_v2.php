<?php
// debug_pieces_red_v2.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$id = 2410; // Pieces of Red
$p = get_post($id);

echo "<h1>Dump Content (Base64)</h1>";
if ($p) {
    echo "<textarea style='width:100%;height:300px;'>" . base64_encode($p->post_content) . "</textarea>";
} else {
    echo "Post not found.";
}
?>