<?php
// force_update_static.php
// Force overwrite with explicit relative path and checks

$file = __DIR__ . '/anemones_static.html';
echo "<h1>Target: $file</h1>";

// Delete first to be sure
if (file_exists($file)) {
    unlink($file);
    echo "Deleted old file.<br>";
}

// content with timestamp
$time = date('Y-m-d H:i:s');
$html = <<<HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anemones – Elliot Spencer Morgan</title>
    <!-- UPDATED: $time -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    
    <style>
        /* Base Reset & Typography */
        body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; background: #fff; color: #1a1a1a; -webkit-font-smoothing: antialiased; }
        a { text-decoration: none; color: inherit; transition: opacity 0.2s; }
        a:hover { opacity: 0.7; }
        
        /* Layout Structure */
        .site-header { padding: 40px 20px; text-align: center; border-bottom: 1px solid #f0f0f0; margin-bottom: 40px; }
        .site-title { margin: 0; font-family: 'Playfair Display', serif; font-size: 28px; font-weight: normal; letter-spacing: 0.5px; }
        .site-footer { text-align: center; padding: 60px 20px; border-top: 1px solid #f0f0f0; margin-top: 60px; color: #666; font-size: 13px; letter-spacing: 0.5px; }
        .artwork-page-container { max-width: 1400px; margin: 0 auto; padding: 0 20px; }
        @media (max-width: 768px) {
            .site-header { padding: 20px; }
        }
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
                <a href="#" class="btn-premium" style="display: flex; justify-content: center; padding: 1rem; background-color: #1a1a1a; color: #fff; text-transform: uppercase;">Purchase on Saatchi Art</a>
            </div>

            <div style="max-width: 800px; margin: 3rem auto; font-size: 1.05rem; color: #4a4a4a; line-height: 1.8;">
                <h3 style="font-family: 'Playfair Display', serif;">About the Work</h3>
                <p>A vibrant exploration of organic forms.</p>
                 <div style="font-size: 0.9em; color: #666;">Dimensions: 48" x 48" x 1.5"</div>
            </div>
        </div>
    </main>
    <footer class="site-footer">
        &copy; 2025 Elliot Spencer Morgan - Premium Restored $time
    </footer>
</body>
</html>
HTML;

$bytes = file_put_contents($file, $html);
echo "✅ Wrote $bytes bytes.<br>";

// Verify
$read = file_get_contents($file);
if (strpos($read, $time) !== false) {
    echo "✅ Verification: Timestamp found in file.<br>";
} else {
    echo "❌ Verification Failed.<br>";
}

echo "<a href='/anemones/'>Check Site</a>";
?>