<?php
// view_portfolio_source.php
// Show the actual HTML source

$html = file_get_contents($_SERVER['DOCUMENT_ROOT'] . '/portfolio.html');

header('Content-Type: text/plain');
echo substr($html, 0, 5000); // Show first 5000 characters
?>