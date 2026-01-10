<?php
echo "Current File: " . __FILE__ . "<br>";
echo "Document Root: " . $_SERVER['DOCUMENT_ROOT'] . "<br>";
echo "Content Dir: " . WP_CONTENT_DIR . "<br>"; // Might not be defined if not loading WP
echo "Check path: /home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.php : " . (file_exists('/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.php') ? 'EXISTS' : 'NOT FOUND') . "<br>";
echo "Check path: /home/elliotspencermor/public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal.php : " . (file_exists('/home/elliotspencermor/public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal.php') ? 'EXISTS' : 'NOT FOUND') . "<br>";
?>
