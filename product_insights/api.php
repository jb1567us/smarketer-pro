<?php
header('Content-Type: application/json');

require_once 'config.php';
require_once 'lib/GeminiService.php';

try {
    // Load config
    $config = require 'config.php';
    
    // Check for POST
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        throw new Exception('Only POST requests are allowed');
    }

    // Get input
    $input = json_decode(file_get_contents('php://input'), true);
    $productData = $input['productData'] ?? '';
    $sections = $input['sections'] ?? [];

    if (empty($productData)) {
        throw new Exception('Missing product data');
    }

    // Call Service
    // Prefer Env var but fall back to config file valid value
    $apiKey = getenv('GEMINI_API_KEY');
    if (!$apiKey || $apiKey === 'YOUR_API_KEY_HERE_IF_NOT_IN_ENV') {
         // Try to look for a local .env file if getenv fails (common in shared hosting)
         // For now, we rely on the user setting it in config.php or cPanel env
         $apiKey = $config['gemini_api_key'];
    }

    if (empty($apiKey) || strpos($apiKey, 'YOUR_API_KEY') !== false) {
        throw new Exception('Server Configuration Error: Missing API Key');
    }

    $service = new GeminiService($apiKey);
    $insights = $service->generateInsights($productData, $sections);

    echo json_encode(['insights' => $insights]);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
