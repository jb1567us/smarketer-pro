<?php
// deploy_static_bypass.php
// 1. Create static HTML
// 2. Wrap root index.php

$root = __DIR__;

// --- 1. Generate Static HTML ---
$html = <<<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anemones – Elliot Spencer Morgan</title>
    <style>
        body { margin: 0; padding: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #fff; color: #333; }
        .site-header { padding: 40px 20px; text-align: center; border-bottom: 1px solid #f0f0f0; }
        .site-title { margin: 0; font-size: 24px; letter-spacing: 2px; text-transform: uppercase; font-weight: normal; }
        .site-title a { text-decoration: none; color: #000; }
        
        .artwork-page-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 60px 20px;
            display: flex;
            flex-wrap: wrap;
            gap: 60px;
        }
        
        .artwork-image-col {
            flex: 1 1 600px;
        }
        .artwork-image-col img {
            width: 100%;
            height: auto;
            display: block;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        }
        
        .artwork-info-col {
            flex: 1 1 300px;
            padding-top: 20px;
        }
        .entry-title {
            font-size: 36px;
            font-weight: 300;
            margin: 0 0 20px 0;
            color: #000;
        }
        .artwork-meta {
            font-size: 14px;
            line-height: 1.8;
            color: #666;
            margin-bottom: 30px;
        }
        .artwork-price {
            font-size: 24px;
            color: #000;
            margin-bottom: 30px;
            font-weight: 400;
        }
        .purchase-button {
            display: inline-block;
            background: #000;
            color: #fff;
            padding: 15px 30px;
            text-decoration: none;
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 2px;
            transition: background 0.3s;
        }
        .purchase-button:hover {
            background: #333;
        }
        
        @media (max-width: 768px) {
            .artwork-page-container { flex-direction: column; gap: 30px; }
            .entry-title { font-size: 28px; }
        }
        
        /* Demo Content to Replace with Real */
        .mock-image { background: #eee; height: 600px; width: 100%; display: flex; align-items: center; justify-content: center; color: #999; }
    </style>
</head>
<body>
    <header class="site-header">
        <h1 class="site-title"><a href="/">Elliot Spencer Morgan</a></h1>
    </header>
    
    <main>
        <div class="artwork-page-container">
            <div class="artwork-image-col">
                 <!-- Real Image URL would go here -->
                 <div class="mock-image">Artwork Image Placeholder</div>
            </div>
            <div class="artwork-info-col">
                <h1 class="entry-title">Anemones</h1>
                <div class="artwork-meta">
                    Mixed Media on Canvas<br>
                    48 x 60 inches<br>
                    2024
                </div>
                <div class="artwork-price">$4,500</div>
                <a href="#" class="purchase-button">Inquire</a>
            </div>
        </div>
    </main>
    
    <footer style="text-align:center; padding: 60px; color: #ccc; font-size: 12px; border-top: 1px solid #f9f9f9;">
        &copy; 2025 Elliot Spencer Morgan
    </footer>
</body>
</html>
HTML;

file_put_contents($root . '/anemones_static.html', $html);
echo "✅ Created anemones_static.html<br>";

// --- 2. Wrap Index ---
$index_files = ['index.php', 'index_wp.php'];
$current_index = $root . '/index.php';
$backup_index = $root . '/index_wp.php';

// Check if already wrapped
$content = file_get_contents($current_index);
if (strpos($content, 'anemones_static.html') !== false) {
    echo "⚠️ Already wrapped.<br>";
} else {
    // Move original index
    if (!file_exists($backup_index)) {
        rename($current_index, $backup_index);
        echo "✅ Renamed index.php -> index_wp.php<br>";
    }

    // Create new wrapper
    $wrapper = <<<'PHP'
<?php
// STATIC BYPASS WRAPPER
if (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/anemones/') !== false) {
    readfile(__DIR__ . '/anemones_static.html');
    exit;
}
// Fallback to WordPress
require(__DIR__ . '/index_wp.php');
?>
PHP;
    file_put_contents($current_index, $wrapper);
    echo "✅ Created Wrapper index.php<br>";
}

echo "<a href='/anemones/'>Check Site</a>";
?>