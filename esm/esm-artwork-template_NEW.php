<?php
/*
Plugin Name: ESM Artwork Master Template
Description: Full-page override to render premium artwork layouts, bypassing the active theme.
Version: 3.0
Author: ESM Dev
*/

// Prevent direct access
// Prevent direct access - or load WP environment for IDE/Debug context
if (!defined('ABSPATH')) {
    if (file_exists(__DIR__ . '/wp-load.php')) {
        require_once __DIR__ . '/wp-load.php';
    } else {
        exit;
    }
}

if (!class_exists('ESM_Artwork_Template')) {
class ESM_Artwork_Template
{

    private $data_map = [];

    public function __construct()
    {
        // Use template_include to override the entire page content
        add_filter('template_include', [$this, 'override_template']);
        add_filter('wp_lazy_loading_enabled', '__return_false'); // Disable Core Lazy Load
        add_action('wp_head', [$this, 'debug_info']);
        $this->load_data();
    }

    public function debug_info() {
        global $post;
        $title = $post ? $post->post_title : 'NO POST';
        $slug = $post ? $post->post_name : 'NO SLUG';
        $key = strtolower(trim($title));
        $match = isset($this->data_map[$key]) ? 'YES' : 'NO';
        echo "\n<!-- ESM DEBUG: Title='{$title}', Slug='{$slug}', Key='{$key}', Match='{$match}' -->\n";
    }

    private function load_data()
    {
        $file = __DIR__ . '/artwork_data.json';
        if (!file_exists($file))
            $file = ABSPATH . 'artwork_data.json';
        
        if (file_exists($file)) {
            $json = file_get_contents($file);
            $data = json_decode($json, true);
            if ($data) {
                foreach ($data as $item) {
                    if (isset($item['title'])) {
                        $key = strtolower(trim($item['title']));
                        $this->data_map[$key] = $item;
                    }
                }
            }
        }
    }

    public function override_template($template)
    {
        if (!is_singular() && !is_page()) {
            return $template;
        }

        $post = get_post();
        if (!$post) return $template;

        // Check if this page matches an artwork in our DB
        $title = trim($post->post_title);
        $key = strtolower($title);

        if (isset($this->data_map[$key])) {
            // MATCH FOUND: Render our custom layout and exit
            $this->render_full_page($post, $this->data_map[$key]);
            exit; // Stop WordPress from loading the theme template
        }

        return $template;
    }

    private function render_full_page($post, $data)
    {
        $title = trim($post->post_title);
        
        // --- DATA PREP ---
        $price = isset($data['price']) ? '$' . number_format($data['price']) : 'Inquire';
        $dimensions = isset($data['dimensions']) ? $data['dimensions'] : '';
        if (!$dimensions && isset($data['width'], $data['height'])) {
            $dimensions = "{$data['width']} W x {$data['height']} H in";
        }
        $width = isset($data['width']) ? $data['width'] : '';
        $height = isset($data['height']) ? $data['height'] : '';

        $medium = isset($data['mediumsDetailed']) ? $data['mediumsDetailed'] : (isset($data['medium']) ? $data['medium'] : 'Mixed Media');
        $year = isset($data['year']) ? $data['year'] : '';
        $styles = isset($data['styles']) ? $data['styles'] : '';
        
        $detected_colors = isset($data['detected_colors']) && is_array($data['detected_colors']) ? implode(', ', $data['detected_colors']) : '';
        $tags_combined = [];
        if ($styles) $tags_combined[] = $styles;
        if ($detected_colors) $tags_combined[] = $detected_colors;
        $tags_display = implode(', ', $tags_combined);

        $desc = "Original {$medium} painting by Elliot Spencer Morgan.";
        if ($year) $desc .= " Created in {$year}.";
        if ($styles) $desc .= " Featuring elements of {$styles}.";
        $desc .= " Perfect for interior design projects, high-end residential spaces, and hospitality environments.";
        $desc .= " Signed and delivered with a Certificate of Authenticity. Available for trade professionals.";

        $installation = isset($data['readyToHang']) ? $data['readyToHang'] : "Wired & Ready to Hang";
        if ($installation === 'No') $installation = "Requires Framing";
        
        $framing = isset($data['frame']) ? $data['frame'] : "Unframed";
        $shipping = isset($data['shippingFrom']) ? $data['shippingFrom'] : "United States";
        $packaging = isset($data['packaging']) ? $data['packaging'] : "Ships in a Box";

        $image_url = isset($data['image_url']) ? $data['image_url'] : '';
        $saatchi_url = isset($data['saatchi_url']) ? $data['saatchi_url'] : '';

        // --- FILTERING CATEGORIES ---
        $w_num = floatval($width);
        $size_cat = 'medium';
        if ($w_num < 24) $size_cat = 'small';
        elseif ($w_num >= 24 && $w_num < 40) $size_cat = 'medium';
        elseif ($w_num >= 40 && $w_num < 60) $size_cat = 'large';
        elseif ($w_num >= 60) $size_cat = 'oversized';

        $price_num = floatval(isset($data['price']) ? $data['price'] : 0);
        $price_range = 'under-1000';
        if ($price_num < 1000) $price_range = 'under-1000';
        elseif ($price_num >= 1000 && $price_num < 2000) $price_range = '1000-2000';
        elseif ($price_num >= 2000 && $price_num < 3000) $price_range = '2000-3000';
        elseif ($price_num >= 3000 && $price_num < 5000) $price_range = '3000-5000';
        elseif ($price_num >= 5000) $price_range = '5000-plus';

        // File Lookups
        $candidates = [
            isset($data['slug']) ? $data['slug'] . '_spec.pdf' : '', // Priority 1: Exact JSON slug
            isset($data['title']) ? $data['title'] . '_spec.pdf' : '',
            $title . '_spec.pdf',
            sanitize_title($title) . '_spec.pdf',
            // Add new detected patterns
            isset($data['title']) ? $data['title'] . '_Sheet.pdf' : '',
            isset($data['title']) ? $data['title'] . ' Painting_Sheet.pdf' : '',
            $title . '_Sheet.pdf',
            $title . ' Painting_Sheet.pdf'
        ];
        $candidates = array_filter($candidates);
        $spec_file = $this->find_file(ABSPATH . 'downloads/spec_sheets/', $candidates);

        $zip_candidates = [
            isset($data['title']) ? $data['title'] . '_HighRes.zip' : '',
            isset($data['slug']) ? $data['slug'] . '_HighRes.zip' : '',
            $title . '_HighRes.zip',
            sanitize_title($title) . '_HighRes.zip'
        ];
        $zip_candidates = array_filter($zip_candidates);
        $zip_file = $this->find_file(ABSPATH . 'downloads/high_res/', $zip_candidates);

        // --- FULL HTML OUTPUT ---
        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo esc_html($title); ?> - Elliot Spencer Morgan</title>
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "VisualArtwork",
      "name": "<?php echo esc_js($title); ?>",
      "image": "<?php echo esc_url($image_url); ?>",
      "description": "<?php echo esc_js($desc); ?>",
      "artist": {
        "@type": "Person",
        "name": "Elliot Spencer Morgan"
      },
      "width": {"@type": "Distance", "value": "<?php echo esc_js($width); ?>", "unitCode": "INH"},
      "height": {"@type": "Distance", "value": "<?php echo esc_js($height); ?>", "unitCode": "INH"},
      "additionalProperty": [
        {
          "@type": "PropertyValue",
          "name": "Ready to Hang",
          "value": "<?php echo esc_js($installation); ?>"
        },
        {
          "@type": "PropertyValue",
          "name": "Framing",
          "value": "<?php echo esc_js($framing); ?>"
        }
      ]
    }
    </script>
    
    <style>
        /* RESET & CORE */
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 0;
            font-family: 'Inter', sans-serif;
            color: #2c3e50;
            background: #ffffff;
            overflow-x: hidden;
            width: 100%;
        }
        a { color: inherit; text-decoration: none; }
        
        /* HEADER - FIXED & TRANSPARENT */
        header {
            position: fixed; top: 0; left: 0; width: 100%;
            display: flex; justify-content: flex-end; align-items: center; /* Changed spacing to flex-end */
            padding: 20px 40px;
            z-index: 1000;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(5px);
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        .site-title {
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            font-family: 'Playfair Display', serif;
            font-size: 1.5rem;
            font-weight: 400;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #1a1a1a;
            white-space: nowrap; /* Prevent wrapping on desktop */
        }
        
        /* HAMBURGER MENU */
        .menu-toggle {
            background: none; border: none; cursor: pointer;
            display: flex; flex-direction: column; gap: 6px;
            z-index: 2000; padding: 10px;
        }
        .bar { width: 24px; height: 1px; background: #1a1a1a; transition: 0.3s; }
        
        /* MENU OVERLAY */
        .menu-overlay {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: white; z-index: 1500;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            opacity: 0; pointer-events: none; transition: 0.4s ease;
        }
        .menu-overlay.active { opacity: 1; pointer-events: auto; }
        .menu-overlay nav a {
            display: block; font-family: 'Playfair Display', serif;
            font-size: 2rem; margin: 15px 0; color: #1a1a1a;
            text-align: center; transition: 0.2s;
        }
        .menu-overlay nav a:hover { color: #555; transform: scale(1.02); }

        /* ARTWORK CONTAINER */
        .artwork-container {
            max-width: 100%;
            margin-top: 80px; /* Offset for fixed header */
            padding-bottom: 60px;
        }

        /* HERO IMAGE */
        .hero-section {
            width: 100%;
            display: flex; justify-content: center;
            background: #fafafa;
            padding: 40px 20px;
            margin-bottom: 40px;
        }
        .artwork-hero-image {
            max-width: 900px;
            width: 100%;
            height: auto;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        }

        /* INFO SECTION */
        .info-section {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
            text-align: center;
        }
        .artwork-title {
            font-family: 'Playfair Display', serif;
            font-size: 3rem; margin: 0 0 10px 0;
            color: #1a1a1a; font-weight: 400;
        }
        .artwork-price {
            font-family: 'Playfair Display', serif;
            font-size: 1.5rem; margin-bottom: 30px;
            color: #444;
        }

        /* BUTTONS */
        .actions { display: flex; flex-direction: column; align-items: center; gap: 15px; margin-bottom: 50px; }
        .btn {
            padding: 14px 30px; font-size: 0.9rem; text-transform: uppercase;
            letter-spacing: 1px; border-radius: 4px; transition: 0.3s;
            width: 100%; max-width: 300px; text-align: center;
        }
        .btn-primary { background: #1a1a1a; color: white; border: 1px solid #1a1a1a; }
        .btn-primary:hover { background: #333; }
        .btn-secondary { background: transparent; color: #1a1a1a; border: 1px solid #1a1a1a; }
        .btn-secondary:hover { background: #f5f5f5; }

        /* DETAILS GRID */
        .details-grid {
            display: grid; grid-template-columns: 1fr 1fr;
            border-top: 1px solid #eee; border-bottom: 1px solid #eee;
            margin-bottom: 40px; text-align: left;
        }
        .detail-item {
            padding: 20px; border-bottom: 1px solid #eee;
            border-right: 1px solid #eee;
        }
        .detail-item:nth-child(2n) { border-right: none; }
        .label { font-size: 0.8rem; text-transform: uppercase; color: #888; display: block; margin-bottom: 5px; }
        .value { font-size: 1rem; color: #222; }

        /* DESCRIPTION */
        .description {
            font-size: 1.1rem; line-height: 1.8; color: #444;
            margin-bottom: 60px; max-width: 700px; margin-left: auto; margin-right: auto;
        }

        /* SPECS BOX */
        .specs-box {
            border: 1px solid #ddd; padding: 30px; border-radius: 8px;
            background: #fff; position: relative; max-width: 700px; margin: 0 auto 60px auto;
            text-align: left;
        }
        .specs-box::before {
            content: "TRADE ONLY"; position: absolute; top: 20px; right: 20px;
            font-size: 0.7rem; font-weight: 700; border: 1px solid #000; padding: 4px 8px; border-radius: 4px;
        }
        .specs-header { font-family: 'Playfair Display', serif; font-size: 1.6rem; margin: 0 0 20px 0; }
        .specs-list li { margin-bottom: 10px; display: flex; align-items: center; }
        .check { color: green; margin-right: 10px; }
        .downloads { margin-top: 20px; border-top: 1px dashed #ddd; padding-top: 20px; display: flex; gap: 20px; }
        .download-link { font-size: 0.9rem; color: #666; border-bottom: 1px dotted #888; }

        /* FOOTER */
        footer { margin-top: 80px; padding: 40px; background: #111; color: #fff; text-align: center; }
        
        /* RESPONSIVE */
        @media(max-width: 768px) {
            .artwork-title { font-size: 2rem; }
            .details-grid { grid-template-columns: 1fr; }
            .detail-item { border-right: none; }
            header { padding: 15px 20px; }
        }
    </style>
</head>
<body>

    <!-- HEADER -->
    <header>
        <a href="/" class="site-title">Elliot Spencer Morgan</a>
        <button class="menu-toggle" id="menuToggle" aria-label="Open Menu">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
        </button>
    </header>

    <!-- MENU OVERLAY -->
    <div class="menu-overlay" id="menuOverlay">
        <nav>
            <a href="/">Home</a>
            <a href="/artworks">Artworks</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
            <a href="/trade">Trade</a>
        </nav>
        <button class="menu-toggle" id="menuClose" style="position: absolute; top: 20px; right: 40px;">
             <!-- Close Icon -->
             <span class="bar" style="transform: rotate(45deg); position: absolute;"></span>
             <span class="bar" style="transform: rotate(-45deg); position: absolute;"></span>
        </button>
    </div>

    <!-- MAIN CONTENT -->
    <div class="artwork-container" 
         data-size-category="<?php echo esc_attr($size_cat); ?>"
         data-price-range="<?php echo esc_attr($price_range); ?>"
         data-style="<?php echo esc_attr(strtolower(str_replace(', ', '-', $styles))); ?>"
         data-colors="<?php echo esc_attr(strtolower(str_replace(', ', '-', $detected_colors))); ?>">
        
        <div class="hero-section">
            <?php if ($image_url): ?>
            <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($title); ?>" class="artwork-hero-image no-lazy" data-no-lazy="1">
            <?php endif; ?>
        </div>

        <div class="info-section">
            <h1 class="artwork-title"><?php echo esc_html($title); ?></h1>
            <div class="artwork-price"><?php echo esc_html($price); ?></div>

            <div class="actions">
                <?php if ($saatchi_url): ?>
                <a href="<?php echo esc_url($saatchi_url); ?>" class="btn btn-primary btn-collector" target="_blank">Purchase on Saatchi Art</a>
                <?php endif; ?>
                <a href="/trade" class="btn btn-secondary btn-designer">Request Trade Pricing</a>
                <button class="btn btn-secondary btn-preview" onclick="launchVisualizer()">Preview in Your Room</button>
            </div>

            <div class="details-grid">
                <div class="detail-item"><span class="label">Dimensions</span> <span class="value"><?php echo esc_html($dimensions); ?></span></div>
                <div class="detail-item"><span class="label">Medium</span> <span class="value"><?php echo esc_html($medium); ?></span></div>
                <div class="detail-item"><span class="label">Styles</span> <span class="value"><?php echo esc_html($styles); ?></span></div>
                <div class="detail-item"><span class="label">Frame</span> <span class="value"><?php echo esc_html($framing); ?></span></div>
                <div class="detail-item"><span class="label">Packaging</span> <span class="value"><?php echo esc_html($packaging); ?></span></div>
                <div class="detail-item"><span class="label">Shipping</span> <span class="value"><?php echo esc_html($shipping); ?></span></div>
            </div>

            <div class="description">
                <p><?php echo esc_html($desc); ?></p>
            </div>

            <div class="specs-box" style="background: rgba(255,255,255,0.7); backdrop-filter: blur(10px); border: 1px solid rgba(0,0,0,0.05);">
                <h3 class="specs-header">For Interior Designers</h3>
                <p style="font-size: 0.9rem; color: #666; margin-bottom: 20px;">Perfect for interior design projects and high-end residential spaces. Trade pricing available for professionals.</p>
                <ul class="specs-list" style="list-style: none; padding: 0;">
                    <li><span class="check">✓</span> <strong>Installation:</strong> <?php echo esc_html($installation); ?></li>
                    <li><span class="check">✓</span> <strong>Weight:</strong> Estimated <?php echo $w_num > 40 ? '10-15' : '5-8'; ?> lbs</li>
                    <li><span class="check">✓</span> <strong>Framing:</strong> <?php echo esc_html($framing); ?></li>
                    <li><span class="check">✓</span> <strong>Lead Time:</strong> Ships in 5-7 Days</li>
                </ul>

                <?php if ($spec_file || $zip_file): ?>
                <div class="downloads">
                    <?php if ($spec_file): ?>
                        <a href="/downloads/spec_sheets/<?php echo esc_attr($spec_file); ?>" class="download-link" download>📄 Download Spec Sheet</a>
                    <?php endif; ?>
                    <?php if ($zip_file): ?>
                        <a href="/downloads/high_res/<?php echo esc_attr($zip_file); ?>" class="download-link" download>🖼️ High-Res Package</a>
                    <?php endif; ?>
                </div>
                <?php endif; ?>
                
                
            </div>

            <!-- RELATED PIECES -->
            <?php 
            $related = $this->get_related($data, 3);
            if ($related): 
            ?>
            <div class="related-section" style="margin-top: 80px; padding-top: 60px; border-top: 1px solid #eee;">
                <h3 style="font-family: 'Playfair Display', serif; font-size: 1.8rem; margin-bottom: 40px;">Related Pieces for Your Project</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; text-align: left;">
                    <?php foreach ($related as $r): ?>
                    <a href="<?php echo esc_url($r['link']); ?>" style="display: block;">
                        <img src="<?php echo esc_url($r['image_url']); ?>" class="no-lazy" data-no-lazy="1" style="width: 100%; aspect-ratio: 1; object-fit: cover; margin-bottom: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.05);">
                        <div style="font-weight: 500;"><?php echo esc_html($r['title']); ?></div>
                        <div style="font-size: 0.85rem; color: #888;"><?php echo esc_html($r['dimensions'] ?? ($r['width'].' x '.$r['height'].' in')); ?></div>
                    </a>
                    <?php endforeach; ?>
                </div>
                <div style="margin-top: 40px;">
                    <a href="/trade" style="font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; color: #8b7355; font-weight: 500;">View Full Trade Collection &rsaquo;</a>
                </div>
            </div>
            <?php endif; ?>
        </div>

    </div>

    <!-- FOOTER -->
    <footer>
        <p>&copy; <?php echo date('Y'); ?> Elliot Spencer Morgan. All Rights Reserved.</p>
    </footer>

    <!-- JS -->
    <script>
        const toggle = document.getElementById('menuToggle');
        const close = document.getElementById('menuClose');
        const overlay = document.getElementById('menuOverlay');
        const body = document.body;

        function toggleMenu() {
            overlay.classList.toggle('active');
            // Prevent scrolling when menu is open
            if(overlay.classList.contains('active')) {
                body.style.overflow = 'hidden';
            } else {
                body.style.overflow = '';
            }
        }

        toggle.addEventListener('click', toggleMenu);
        close.addEventListener('click', toggleMenu);

        // Analytics & Interaction
        document.querySelector('.btn-collector')?.addEventListener('click', () => {
            console.log("Analytics: Collector CTA Clicked for <?php echo esc_js($title); ?>");
            if(window.gtag) gtag('event', 'collector_purchase_click', { 'artwork': '<?php echo esc_js($title); ?>' });
        });

        document.querySelector('.btn-designer')?.addEventListener('click', () => {
            console.log("Analytics: Designer CTA Clicked for <?php echo esc_js($title); ?>");
            if(window.gtag) gtag('event', 'designer_trade_click', { 'artwork': '<?php echo esc_js($title); ?>' });
        });

        function launchVisualizer() {
            // Future integration with the Visualizer tool
            window.location.href = '/trade/?preview=<?php echo urlencode($title); ?>';
        }
    </script>
</body>
</html>
        <?php
    }

    private function get_related($current, $count = 3) {
        $related = [];
        $current_styles = isset($current['styles']) ? explode(', ', $current['styles']) : [];
        $current_id = $current['wordpress_id'] ?? $current['id'];

        foreach($this->data_map as $item) {
            $item_id = $item['wordpress_id'] ?? $item['id'];
            if($item_id == $current_id) continue;
            if(!isset($item['image_url'])) continue;

            $item_styles = isset($item['styles']) ? explode(', ', $item['styles']) : [];
            $common = array_intersect($current_styles, $item_styles);
            
            if(count($common) > 0) {
                $related[] = $item;
                if(count($related) >= $count) break;
            }
        }

        // Fallback to random if not enough matches
        if(count($related) < $count) {
            foreach($this->data_map as $item) {
                $item_id = $item['wordpress_id'] ?? $item['id'];
                if($item_id == $current_id) continue;
                if(!isset($item['image_url'])) continue;
                if(in_array($item, $related)) continue;
                
                $related[] = $item;
                if(count($related) >= $count) break;
            }
        }

        return $related;
    }

    private function find_file($dir, $candidates)
    {
        if (!is_dir($dir)) return false;
        
        // Exact match first
        foreach ($candidates as $c) {
            if (file_exists($dir . $c)) return $c;
        }

        // Case insensitive match
        $files = scandir($dir);
        $candidates_lower = array_map('strtolower', $candidates);

        foreach ($files as $f) {
            if ($f === '.' || $f === '..') continue;
            if (in_array(strtolower($f), $candidates_lower)) return $f;
        }
        return false;
    }
}
}

new ESM_Artwork_Template();
?>