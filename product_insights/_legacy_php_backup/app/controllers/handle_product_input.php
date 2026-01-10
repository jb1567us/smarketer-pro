<?php
session_start();
$product = $_POST['product_description'] ?? '';
$sections = $_POST['sections'] ?? [];

if (!$product) {
    die("No product description provided.");
}
if (empty($sections)) {
    die("Please select at least one section.");
}

require_once '../utils/openai_helper.php';
$response = getCustomerInsightsFromProduct($product, $sections);
$_SESSION['insights'] = $response;
$_SESSION['product'] = $product;
$_SESSION['sections'] = $sections;

header("Location: ../views/results.php");
exit;
?>