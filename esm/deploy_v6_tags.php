<?php
// deploy_v6_tags.php
// Restore V6 with TAGS

$root = __DIR__;
$new_file = 'anemones_v6.html';
$path = $root . '/' . $new_file;
$time = date('Y-m-d H:i:s');

// 1. Full Content (V6 with TAGS)
$html = <<<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anemones – Elliot Spencer Morgan</title>
    <!-- V6 TAGS: $time -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; background: #fff; color: #1a1a1a; }
        a { text-decoration: none; color: inherit; }
        .site-header { padding: 40px 20px; text-align: center; border-bottom: 1px solid #f0f0f0; margin-bottom: 40px; }
        .site-title { margin: 0; font-family: 'Playfair Display', serif; font-size: 28px; font-weight: normal; }
        .site-footer { text-align: center; padding: 60px 20px; border-top: 1px solid #f0f0f0; margin-top: 60px; color: #666; font-size: 13px; }
        .artwork-page-container { max-width: 1400px; margin: 0 auto; padding: 0 20px; }
        
        /* Specs Box Styling */
        .specs-box { border: 1px solid #e0e0e0; padding: 2rem; border-radius: 8px; position: relative; overflow: hidden; max-width: 800px; margin: 3rem auto; }
        .specs-box::before { content: "TRADE ONLY"; position: absolute; top: 1rem; right: 1rem; font-size: 0.6rem; font-weight: 700; border: 1px solid #1a1a1a; padding: 0.25rem 0.5rem; border-radius: 2px; }
        .check-icon { color: #27ae60; margin-right: 0.75rem; }
        .download-link { font-size: 0.9rem; color: #666; text-decoration: none; border-bottom: 1px dotted #999; margin-right: 1.5rem; }
        .download-link:hover { color: #000; border-bottom: 1px solid #000; }
        .tag-pill { font-size: 0.85rem; color: #666; margin-right: 0.5rem; }
    </style>
</head>
<body>
    <header class="site-header">
        <h1 class="site-title"><a href="/">Elliot Spencer Morgan</a></h1>
    </header>
    <main>
        <div class="artwork-page-container">
            <header class="artwork-header" style="text-align:center; margin-bottom: 2rem;">
                <h1 class="artwork-title" style="font-family: 'Playfair Display', serif; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 400;">Anemones</h1>
                <div class="artwork-price" style="font-size: 1.75rem; font-family: 'Playfair Display', serif;">$2,400</div>
            </header>

            <img src="https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/AnemonesPainting.jpg" alt="Anemones" style="width: 100%; max-width: 800px; height: auto; display: block; margin: 0 auto 2.5rem auto; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">

            <div class="artwork-actions" style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2.5rem; max-width: 400px; margin-left: auto; margin-right: auto;">
                <a href="https://www.saatchiart.com/art/Painting-Anemones/123456/7890" class="btn-premium" style="display: flex; justify-content: center; padding: 1rem; background-color: #1a1a1a; color: #fff; text-transform: uppercase;">Purchase on Saatchi Art</a>
                <a href="/trade" class="btn-premium" style="display: flex; justify-content: center; padding: 1rem; border: 1px solid #1a1a1a; color: #1a1a1a; text-transform: uppercase;">Request Trade Pricing</a>
            </div>

            <div style="max-width: 800px; margin: 3rem auto; font-size: 1.05rem; color: #4a4a4a; line-height: 1.8;">
                <h3 style="font-family: 'Playfair Display', serif;">About the Work</h3>
                <p>A vibrant exploration of organic forms.</p>
                 <div style="font-size: 0.9em; color: #666; margin-top:10px;">Dimensions: 48" x 48" x 1.5"</div>
            </div>

            <!-- RESTORED: Designer Specs Section -->
            <div class="specs-box">
                 <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-top:0;">Designer Specifications</h3>
                 <ul style="list-style: none; padding: 0;">
                    <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;"><span class="check-icon">✓</span> <strong>Installation:</strong> Wired & Ready to Hang</li>
                    <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;"><span class="check-icon">✓</span> <strong>Weight:</strong> 5 lbs (Lightweight)</li>
                    <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;"><span class="check-icon">✓</span> <strong>Framing:</strong> Gallery Wrapped (Unframed)</li>
                    <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;"><span class="check-icon">✓</span> <strong>Lead Time:</strong> Ships in 5-7 Days</li>
                    <!-- TAGS ROW -->
                    <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;">
                         <span style="font-size: 0.75rem; color: #999; text-transform: uppercase; letter-spacing: 1px; margin-right: 0.5rem;">Tags:</span>
                         <span class="tag-pill">Abstract</span>, <span class="tag-pill">Blue</span>, <span class="tag-pill">Oversized</span>
                    </li>
                 </ul>
                 <div style="margin-top: 2rem;">
                    <a href="/downloads/caviar-spec-sheet.pdf" class="download-link">Download Spec Sheet</a>
                    <a href="/downloads/caviar-high-res.zip" class="download-link">High-Res Images</a>
                 </div>
            </div>

        </div>
    </main>
    <footer class="site-footer">
        &copy; 2025 Elliot Spencer Morgan - V6 Tags
    </footer>
</body>
</html>
HTML;

file_put_contents($path, $html);
echo "✅ Created $new_file<br>";

// 2. Update Wrapper index.php
$index = $root . '/index.php';
$wrapper = <<<'PHP'
<?php
// STATIC BYPASS WRAPPER v6
if (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/anemones/') !== false) {
    header("Cache-Control: no-cache, must-revalidate");
    readfile(__DIR__ . '/anemones_v6.html');
    exit;
}
require(__DIR__ . '/index_wp.php');
?>
PHP;

file_put_contents($index, $wrapper);
echo "✅ Updated index.php to point to v6<br>";

// 3. FLUSH OPCACHE
if (function_exists('opcache_reset')) {
    opcache_reset();
    echo "✅ OPCACHE RESET executed.<br>";
}

echo "<a href='/anemones/'>Check Site</a>";
?>