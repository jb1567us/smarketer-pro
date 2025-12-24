<?php
/**
 * Mobile Spec Sheet - Responsive Digital Version
 * Pulls data from artwork_data.json
 */

$artwork_param = isset($_GET['artwork']) ? $_GET['artwork'] : '';
$data_file = __DIR__ . '/artwork_data.json';
$artwork = null;

if (file_exists($data_file)) {
    $data = json_decode(file_get_contents($data_file), true);
    if ($data) {
        foreach ($data as $item) {
            // Match by slug or title
            if ((isset($item['slug']) && $item['slug'] === $artwork_param) || 
                (isset($item['title']) && $item['title'] === $artwork_param) ||
                (isset($item['title']) && strtolower(trim($item['title'])) === strtolower(trim($artwork_param)))) {
                $artwork = $item;
                break;
            }
        }
    }
}

if (!$artwork) {
    die("Artwork not found.");
}

// Data Prep
$title = $artwork['title'] ?? 'Untitled';
$image_url = $artwork['image_url'] ?? '';
$medium = $artwork['mediumsDetailed'] ?? ($artwork['medium'] ?? 'Mixed Media');
$dimensions = $artwork['dimensions'] ?? ($artwork['width'] . ' x ' . $artwork['height'] . ' in');
$year = $artwork['year'] ?? date('Y');
$price = isset($artwork['price']) ? '$' . number_format($artwork['price']) : 'Inquire';
$ready = $artwork['readyToHang'] ?? 'Yes';
$frame = $artwork['frame'] ?? 'Unframed';
$packaging = $artwork['packaging'] ?? 'Box';
$colors = $artwork['detected_colors'] ?? [];

// CM conversion
$width_cm = isset($artwork['width']) ? round($artwork['width'] * 2.54, 1) : null;
$height_cm = isset($artwork['height']) ? round($artwork['height'] * 2.54, 1) : null;

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spec: <?php echo htmlspecialchars($title); ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #0a0a0a;
            --card: #141414;
            --accent: #E5C07B;
            --text: #ffffff;
            --text-dim: #a0a0a0;
            --border: rgba(255, 255, 255, 0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            padding-bottom: 50px;
        }

        header {
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
        }

        .brand {
            font-family: 'Playfair Display', serif;
            font-size: 1.2rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--accent);
        }

        .hero-img {
            width: 100%;
            display: block;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }

        .content {
            padding: 0 25px;
        }

        h1 {
            font-family: 'Playfair Display', serif;
            font-size: 2.2rem;
            margin-bottom: 5px;
            font-weight: 400;
        }

        .subtitle {
            font-size: 0.9rem;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 25px;
        }

        .price-badge {
            display: inline-block;
            background: var(--accent);
            color: #000;
            padding: 5px 15px;
            font-weight: 600;
            border-radius: 4px;
            font-size: 1.1rem;
            margin-bottom: 30px;
        }

        .section {
            margin-bottom: 35px;
        }

        .section-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--accent);
            margin-bottom: 15px;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }

        .spec-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        .spec-item .label {
            font-size: 0.75rem;
            color: var(--text-dim);
            text-transform: uppercase;
            margin-bottom: 4px;
        }

        .spec-item .value {
            font-size: 1rem;
            font-weight: 400;
        }

        .palette {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .color-swatch-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
        }

        .color-swatch {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: 1px solid var(--border);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        
        .color-name {
            font-size: 0.65rem;
            text-transform: uppercase;
            color: var(--text-dim);
            letter-spacing: 0.5px;
        }

        .footer-cta {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 15px 25px;
            background: rgba(10, 10, 10, 0.9);
            backdrop-filter: blur(10px);
            border-top: 1px solid var(--border);
            display: flex;
            gap: 15px;
        }

        .btn {
            flex: 1;
            padding: 14px;
            text-align: center;
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            border-radius: 4px;
            transition: 0.3s;
        }

        .btn-primary { background: var(--accent); color: #000; }
        .btn-outline { border: 1px solid var(--accent); color: var(--accent); }

        /* CM Toggle / Display */
        .metric { font-size: 0.85rem; color: var(--text-dim); margin-top: 2px; }

    </style>
</head>
<body>

    <div class="container">
        <header>
            <div class="brand">Elliot Spencer Morgan</div>
        </header>

        <?php if ($image_url): ?>
        <img src="<?php echo htmlspecialchars($image_url); ?>" alt="<?php echo htmlspecialchars($title); ?>" class="hero-img">
        <?php endif; ?>

        <div class="content">
            <h1><?php echo htmlspecialchars($title); ?></h1>
            <div class="subtitle"><?php echo htmlspecialchars($medium); ?> • <?php echo htmlspecialchars($year); ?></div>
            
            <div class="price-badge"><?php echo htmlspecialchars($price); ?></div>

            <div class="section">
                <div class="section-title">Physical Properties</div>
                <div class="spec-grid">
                    <div class="spec-item">
                        <div class="label">Imperial</div>
                        <div class="value"><?php echo htmlspecialchars($dimensions); ?></div>
                    </div>
                    <?php if ($width_cm): ?>
                    <div class="spec-item">
                        <div class="label">Metric</div>
                        <div class="value"><?php echo "$width_cm x $height_cm cm"; ?></div>
                    </div>
                    <?php endif; ?>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Verified Palette</div>
                <div class="palette">
                    <?php 
                    $colorMap = [
                        // Basic
                        'Red' => '#c0392b', 'Blue' => '#2980b9', 'Green' => '#27ae60', 
                        'Gold' => '#d4af37', 'Silver' => '#bdc3c7', 'Black' => '#1a1a1a', 
                        'Grey' => '#7f8c8d', 'White' => '#f5f5f5', 'Pink' => '#e84393', 
                        'Brown' => '#63422d', 'Beige' => '#f5f5dc', 'Purple' => '#8e44ad', 
                        'Orange' => '#d35400', 'Yellow' => '#f1c40f',
                        
                        // Nuanced / Artistic
                        'Saffron' => '#f4c430', 'Moss' => '#8a9a5b', 'Obsidian' => '#0b0b0b',
                        'Charcoal' => '#36454f', 'Taupe' => '#483c32', 'Brass' => '#b5a642',
                        'Bronze' => '#cd7f32', 'Slate' => '#708090', 'Alabaster' => '#f2f0e6',
                        'Cream' => '#fffdd0', 'Ebony' => '#555d50', 'Platinum' => '#e5e4e2',
                        'Burgundy' => '#800020', 'Graphite' => '#252525'
                    ];

                    foreach ($colors as $color): 
                        $hex = $colorMap[$color] ?? '#333';
                        // Fallback generator for unknown colors (hash to color)
                        if (!isset($colorMap[$color])) {
                            $hash = md5($color);
                            $hex = '#' . substr($hash, 0, 6);
                        }
                    ?>
                        <div class="color-swatch-container">
                            <div class="color-swatch" style="background-color: <?php echo $hex; ?>;"></div>
                            <span class="color-name"><?php echo htmlspecialchars($color); ?></span>
                        </div>
                    <?php endforeach; ?>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Technical Specifications</div>
                <div class="spec-grid">
                    <div class="spec-item">
                        <div class="label">Ready to Hang</div>
                        <div class="value"><?php echo htmlspecialchars($ready); ?></div>
                    </div>
                    <div class="spec-item">
                        <div class="label">Framing</div>
                        <div class="value"><?php echo htmlspecialchars($frame); ?></div>
                    </div>
                    <div class="spec-item">
                        <div class="label">Lead Time</div>
                        <div class="value">5-7 Business Days</div>
                    </div>
                    <div class="spec-item">
                        <div class="label">Packaging</div>
                        <div class="value"><?php echo htmlspecialchars($packaging); ?></div>
                    </div>
                </div>
            </div>

            <div class="section" style="margin-top: 50px;">
                <p style="font-size: 0.8rem; color: var(--text-dim); text-align: center;">
                    Authenticity verified by Elliot Spencer Morgan Studio.<br>
                    Austin, Texas.
                </p>
            </div>
        </div>
    </div>

    <div class="footer-cta">
        <a href="mailto:studio@elliotspencermorgan.com?subject=Inquiry: <?php echo urlencode($title); ?>" class="btn btn-primary">Request Individual Pricing</a>
        <a href="/trade" class="btn btn-outline">Back to Trade</a>
    </div>

</body>
</html>
