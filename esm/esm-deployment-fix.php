<?php

/*

Plugin Name: ESM Deployment Fix

Description: Full-page override to render premium artwork layouts.

Version: 3.1

Author: ESM Dev

*/



// Prevent direct access

if (!defined('ABSPATH'))

    exit;



class ESM_Artwork_Template_Fix

{



    private $data_map = [];



    public function __construct()

    {

        add_filter('template_include', [$this, 'override_template']);

        add_action('wp_head', [$this, 'debug_info']);

        $this->load_data();

    }



    public function debug_info() {

        echo "<!-- ESM FIX PLUGIN ACTIVE -->";

    }



    private function load_data()

    {

        // Look in mu-plugins first, then plugins root

        $file = WP_CONTENT_DIR . '/mu-plugins/artwork_data.json';

        if (!file_exists($file))

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

            $this->render_full_page($post, $this->data_map[$key]);

            exit;

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

        $desc .= " Signed and delivered with a Certificate of Authenticity.";



        $installation = isset($data['readyToHang']) ? $data['readyToHang'] : "Wired & Ready to Hang";

        if ($installation === 'No') $installation = "Requires Framing";

        

        $framing = isset($data['frame']) ? $data['frame'] : "Unframed";

        $shipping = isset($data['shippingFrom']) ? $data['shippingFrom'] : "United States";

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

<head><meta charset="utf-8">

    

    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title><?php echo esc_html($title); ?> - Elliot Spencer Morgan</title>

    <!-- Fonts -->

    <link rel="preconnect" href="https://fonts.googleapis.com">

    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">

    

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

            display: flex; justify-content: space-between; align-items: center;

            padding: 20px 40px;

            z-index: 1000;

            background: rgba(255,255,255,0.95);

            backdrop-filter: blur(5px);

            border-bottom: 1px solid rgba(0,0,0,0.05);

        }

        .site-title {

            font-family: 'Playfair Display', serif;

            font-size: 1.5rem;

            font-weight: 400;

            text-transform: uppercase;

            letter-spacing: 1px;

            color: #1a1a1a;

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

    <div class="artwork-container">

        

        <div class="hero-section">

            <?php if ($image_url): ?>

            <img src="<?php echo esc_url($image_url); ?>" alt="<?php echo esc_attr($title); ?>" class="artwork-hero-image">

            <?php endif; ?>

        </div>



        <div class="info-section">

            <h1 class="artwork-title"><?php echo esc_html($title); ?></h1>

            <div class="artwork-price"><?php echo esc_html($price); ?></div>



            <div class="actions">

                <?php if ($saatchi_url): ?>

                <a href="<?php echo esc_url($saatchi_url); ?>" class="btn btn-primary" target="_blank">Purchase on Saatchi Art</a>

                <?php endif; ?>

                <a href="/trade" class="btn btn-secondary">Request Trade Pricing</a>

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



            <div class="specs-box">

                <h3 class="specs-header">Designer Specifications</h3>

                <ul class="specs-list" style="list-style: none; padding: 0;">

                    <li><span class="check">✓</span> <strong>Installation:</strong> <?php echo esc_html($installation); ?></li>

                    <li><span class="check">✓</span> <strong>Framing:</strong> <?php echo esc_html($framing); ?></li>

                    <li><span class="check">✓</span> <strong>Lead Time:</strong> Ships in 5-7 Days</li>

                </ul>



                <?php if ($spec_file || $zip_file): ?>

                <div class="downloads">

                    <?php if ($spec_file): ?>

                        <a href="/downloads/spec_sheets/<?php echo esc_attr($spec_file); ?>" class="download-link" download>Download Spec Sheet</a>

                    <?php endif; ?>

                    <?php if ($zip_file): ?>

                        <a href="/downloads/high_res/<?php echo esc_attr($zip_file); ?>" class="download-link" download>High-Res Images</a>

                    <?php endif; ?>

                </div>

                <?php endif; ?>

            </div>

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

    </script>

</body>

</html>

        <?php

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



new ESM_Artwork_Template_Fix();

?>

