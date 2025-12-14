<?php
// deploy_logo_injector.php
// INSTALL "esm-logo-injector.php" MU-PLUGIN
// Strategy: Filter 'render_block' to inject Logo after Site Title
// Bypasses FSE DB/Template issues completely.

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>💉 Deploying Logo Injector</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

$plugin_code = <<<'PHP'
<?php
/* Plugin Name: ESM Logo Injector */
/* Description: Injects Logo after Site Title via PHP Filter */

add_filter('render_block', function($block_content, $block) {
    // Target the Site Title block
    if ($block['blockName'] === 'core/site-title') {
        
        // Define Logo HTML (Absolute URL + Cache Bust + 180px Width)
        $logo_url = 'https://elliotspencermorgan.com/logo.png?v=INJECTOR_' . time();
        
        $logo_html = '
        <div class="header-logo-injected" style="text-align: center; width: 100%; margin: 1rem 0 1.5rem 0;">
            <a href="https://elliotspencermorgan.com/" style="text-decoration:none; border:none;">
                <img src="' . $logo_url . '" 
                     alt="Elliot Spencer Morgan Logo (Injected)" 
                     style="width: 180px; max-width: 100%; height: auto; display: inline-block;" />
            </a>
        </div>';
        
        // Return Title + Logo
        return $block_content . $logo_html;
    }
    
    return $block_content;
}, 10, 2);
PHP;

file_put_contents($mu_dir . '/esm-logo-injector.php', $plugin_code);
echo "✅ Installed: esm-logo-injector.php<br>";

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check Injection</a>";
?>