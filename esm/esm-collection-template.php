<?php
/*
Plugin Name: ESM Collection Template
Description: Dynamic template for collection pages.
Version: 1.0
Author: ESM Dev
*/

// Prevent direct access
if (!defined('ABSPATH')) {
    if (file_exists(__DIR__ . '/wp-load.php')) {
        require_once __DIR__ . '/wp-load.php';
    } else {
        exit;
    }
}

if (!class_exists('ESM_Collection_Template')) {
class ESM_Collection_Template
{
    private $collections_map = [];

    public function __construct()
    {
        // High priority to override other templates
        add_filter('template_include', [$this, 'override_template'], 9999);
        // add_action('wp_footer', [$this, 'visible_debug_info']);
        $this->load_data();
    }

    public function visible_debug_info() {
        // if (!current_user_can('administrator')) return; 
        
        global $post;
        $slug = $post ? $post->post_name : 'NO POST';
        $key = strtolower(trim($slug));
        $count = isset($this->collections_map) ? count($this->collections_map) : 0;
        $found = isset($this->collections_map[$key]) ? 'YES' : 'NO';
        
        $paths_checked = [
            __DIR__ . '/collections_data.json',
            ABSPATH . 'collections_data.json',
            dirname(ABSPATH) . '/collections_data.json'
        ];
        
        echo "<div style='background:red; color:white; padding:20px; position:fixed; bottom:0; left:0; width:100%; z-index:99999;'>";
        echo "<strong>ESM DEBUG:</strong> Slug: $slug | Key: $key | Collections Loaded: $count | Match: $found<br>";
        echo "ABSPATH: " . ABSPATH . "<br>";
        echo "Paths Checked:<br>";
        foreach ($paths_checked as $p) echo "$p (" . (file_exists($p) ? "FOUND" : "NOT FOUND") . ")<br>";
        echo "</div>";
    }

    private function load_data()
    {
        $possible_paths = [
            WP_CONTENT_DIR . '/collections_data.json',
            __DIR__ . '/collections_data.json',
            ABSPATH . 'collections_data.json',
            dirname(ABSPATH) . '/collections_data.json',
            'c:/sandbox/esm/collections_data.json' // Hard fallback for this env
        ];

        foreach ($possible_paths as $file) {
            if (file_exists($file)) {
                $json = file_get_contents($file);
                $data = json_decode($json, true);
                if ($data) {
                    // Normalize keys to lowercase just in case
                    foreach ($data as $k => $v) {
                        $this->collections_map[strtolower($k)] = $v;
                    }
                    return;
                }
            }
        }
    }

    public function override_template($template)
    {
        if (!is_page()) {
            return $template;
        }

        $post = get_post();
        if (!$post) return $template;

        $slug = $post->post_name;
        $key = strtolower(trim($slug));

        if (isset($this->collections_map[$key])) {
            // MATCH FOUND: Render our custom layout
            $this->render_page($post, $this->collections_map[$key]);
            exit; 
        }

        return $template;
    }

    private function render_page($post, $collection_data)
    {
        $title = $collection_data['title'];
        $desc = isset($collection_data['description']) ? $collection_data['description'] : '';
        $artworks = isset($collection_data['artworks']) ? $collection_data['artworks'] : [];

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
    
    <style>
        /* RESET & CORE (Matching Artwork Template) */
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
            display: flex; justify-content: flex-end; align-items: center;
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
            white-space: nowrap;
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

        /* COLLECTION PAGE SPECIFIC */
        .collection-page {
            margin-top: 120px; /* Offset for fixed header */
            padding-bottom: 60px;
        }
        .collection-header {
            text-align: center;
            max-width: 800px;
            margin: 0 auto 60px auto;
            padding: 0 20px;
        }
        .collection-title {
            font-family: 'Playfair Display', serif;
            font-size: 3rem;
            margin-bottom: 20px;
            color: #1a1a1a;
        }
        .collection-intro {
            font-size: 1.1rem;
            line-height: 1.6;
            color: #555;
        }

        /* GRID */
        .gold-collection-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 40px;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .artwork-card {
            text-align: center;
            transition: transform 0.3s ease;
        }
        .artwork-card:hover {
            transform: translateY(-5px);
        }
        .artwork-card img {
            width: 100%;
            aspect-ratio: 3/4;
            object-fit: cover;
            margin-bottom: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }
        .artwork-card h3 {
            font-family: 'Playfair Display', serif;
            font-size: 1.2rem;
            margin: 10px 0 5px 0;
            font-weight: 500;
        }
        .artwork-card .details {
            font-size: 0.9rem;
            color: #888;
            margin: 0;
        }

        /* CTA SECTION */
        .collection-cta {
            text-align: center;
            margin: 80px auto;
            padding: 80px 20px;
            background: #fafafa;
            border-radius: 4px;
            max-width: 1200px;
        }

        /* FOOTER */
        footer { margin-top: 80px; padding: 40px; background: #111; color: #fff; text-align: center; }

        @media(max-width: 768px) {
            .collection-title { font-size: 2rem; }
            header { padding: 15px 20px; }
            .gold-collection-grid { grid-template-columns: 1fr; gap: 60px; }
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
             <span class="bar" style="transform: rotate(45deg); position: absolute;"></span>
             <span class="bar" style="transform: rotate(-45deg); position: absolute;"></span>
        </button>
    </div>

    <!-- MAIN CONTENT -->
    <div class="collection-page">
        <div class="collection-header">
            <h1 class="collection-title"><?php echo esc_html($title); ?></h1>
            <p class="collection-intro"><?php echo esc_html($desc); ?></p>
        </div>
        
        <div class="gold-collection-grid">
            <?php foreach ($artworks as $aw): 
                $aw_title = $aw['title'];
                $aw_img = $aw['image_url'];
                $aw_slug = isset($aw['slug']) ? $aw['slug'] : sanitize_title($aw_title);
                
                // Ensure link is relative and correct
                $aw_link = '/' . $aw_slug . '/';
                
                $aw_dims = '';
                if (isset($aw['dimensions'])) {
                    $aw_dims = $aw['dimensions'];
                } elseif (isset($aw['width'], $aw['height'])) {
                    $aw_dims = $aw['width'] . ' x ' . $aw['height'] . ' in';
                }
                
                $aw_medium = isset($aw['mediumsDetailed']) ? $aw['mediumsDetailed'] : (isset($aw['medium']) ? $aw['medium'] : '');
            ?>
            <div class="artwork-card">
                <a href="<?php echo esc_url($aw_link); ?>">
                    <img src="<?php echo esc_url($aw_img); ?>" alt="<?php echo esc_attr($aw_title); ?>" loading="lazy">
                </a>
                <h3><a href="<?php echo esc_url($aw_link); ?>"><?php echo esc_html($aw_title); ?></a></h3>
                <p class="details"><?php echo esc_html($aw_dims); ?> | <?php echo esc_html($aw_medium); ?></p>
            </div>
            <?php endforeach; ?>
        </div>
        
        <div class="collection-cta">
            <h2 style="font-family: 'Playfair Display', serif; margin-bottom: 20px; font-size: 2rem;">Questions About This Collection?</h2>
            <p style="margin-bottom: 30px; color: #666; font-size: 1.1rem;">I'd love to help you find the perfect piece for your space.</p>
            <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
                <a href="/contact" style="display: inline-block; background: #1a1a1a; color: #fff; padding: 15px 40px; text-decoration: none; text-transform: uppercase; letter-spacing: 1px; font-size: 14px; transition: opacity 0.3s; border-radius: 4px;">Get in Touch</a>
                <a href="/trade" style="display: inline-block; border: 1px solid #1a1a1a; color: #1a1a1a; padding: 15px 40px; text-decoration: none; text-transform: uppercase; letter-spacing: 1px; font-size: 14px; transition: all 0.3s; border-radius: 4px;">Trade Program</a>
            </div>
        </div>
        
        <div class="related-collections" style="margin: 60px auto; border-top: 1px solid #eee; padding-top: 60px; max-width: 1200px; text-align: center;">
            <h2 style="font-family: 'Playfair Display', serif; margin-bottom: 40px;">Explore More Collections</h2>
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px;">
                <?php 
                foreach ($this->collections_map as $k => $c) {
                    if ($k === $collection_data['slug']) continue;
                    echo '<a href="/' . esc_attr($k) . '/" style="padding: 10px 20px; border: 1px solid #eee; border-radius: 30px; font-size: 0.9rem; color: #555;">' . esc_html($c['title']) . '</a>';
                }
                ?>
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
}
}

new ESM_Collection_Template();
?>
