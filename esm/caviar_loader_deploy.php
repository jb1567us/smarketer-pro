<?php
// caviar_loader_deploy.php
// Deploy MU-Plugin to hijack rendering for Anemones

$dir = WP_CONTENT_DIR . '/mu-plugins';
if (!is_dir($dir))
    mkdir($dir, 0755, true);

$plugin = <<<'PHP'
<?php
/*
Plugin Name: Caviar Layout Loader
Description: Force renders Premium Layout for Anemones
Version: 1.0
*/

add_action('template_redirect', function() {
    // Target Check
    if (strpos($_SERVER['REQUEST_URI'], '/anemones/') === false) {
        return;
    }

    global $wpdb;
    
    // Manual DB Fetch (most reliable)
    $content = $wpdb->get_var("SELECT post_content FROM $wpdb->posts WHERE ID = 213");
    
    if (!$content) {
        // Fallback if ID 213 is wrong
        $content = "<h1>Error: Content Not Found via MU-ID</h1>";
    }

    // Force Render
    ?>
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Anemones – Elliot Spencer Morgan</title>
        <style>
            /* Critical CSS for Layout */
            body { margin: 0; padding: 0; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #fff; color: #333; }
            .site-header { padding: 20px; text-align: center; border-bottom: 1px solid #eee; }
            .site-title { margin: 0; font-size: 24px; font-weight: normal; }
            .site-title a { text-decoration: none; color: #000; }
            
            /* Premium Container */
            .artwork-page-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px 20px;
                display: flex;
                flex-wrap: wrap;
                gap: 40px;
            }
            .artwork-image { flex: 1 1 600px; }
            .artwork-image img { width: 100%; height: auto; display: block; }
            .artwork-details { flex: 1 1 300px; padding-top: 20px; }
            .artwork-title { font-size: 32px; margin: 0 0 10px 0; font-weight: normal; }
            .artwork-meta { font-size: 14px; color: #666; line-height: 1.6; }
            .artwork-price { font-size: 18px; margin-top: 20px; color: #111; }
            .artwork-button { display: inline-block; margin-top: 20px; padding: 10px 20px; background: #000; color: #fff; text-decoration: none; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; }
            .artwork-button:hover { background: #333; }
        </style>
    </head>
    <body>
        <header class="site-header">
             <h1 class="site-title"><a href="/">Elliot Spencer Morgan</a></h1>
        </header>
        
        <main>
            <?php 
                // Determine if content has container or if we need to wrap it
                if (strpos($content, 'artwork-page-container') === false) {
                    echo '<div class="artwork-page-container">';
                    echo do_shortcode($content); // Process shortcodes just in case
                    echo '</div>';
                } else {
                    echo do_shortcode($content);
                }
            ?>
        </main>
        
        <footer style="text-align:center; padding: 40px; font-size: 12px; color: #999;">
            &copy; <?php echo date('Y'); ?> Elliot Spencer Morgan
        </footer>
    </body>
    </html>
    <?php
    exit; // STOP WORDPRESS
});
PHP;

file_put_contents($dir . '/caviar-loader.php', $plugin);
echo "<h1>✅ Caviar Loader Deployed</h1>";
echo "view site: <a href='/anemones/'>/anemones/</a>";
?>