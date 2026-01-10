<?php
// deploy_centered_design.php
// 1. Enqueue Google Fonts (Playfair Display)
// 2. Center Header Layout
// 3. Apply Typography

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
if (!is_dir($mu_dir)) {
    mkdir($mu_dir, 0755, true);
}

// --- PART 1: FONTS & STYLES (MU-Plugin) ---
$style_code = <<<'PHP'
<?php
/* Plugin Name: FSE Typography & Layout Fix */

// 1. Load Google Fonts
add_action('wp_enqueue_scripts', function() {
    wp_enqueue_style(
        'esm-google-fonts', 
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap', 
        [], 
        null
    );
});

// 2. CSS Overrides (Force Center & Font)
add_action('wp_head', function() {
    echo '<style>
    /* Site Title Typography */
    .wp-block-site-title a {
        font-family: "Playfair Display", serif !important;
        font-weight: 400;
        font-size: 2rem; /* Reasonable default */
        text-decoration: none;
        color: #1a1a1a;
    }
    
    /* Ensure Container is Centered */
    .wp-block-group.header-centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Double Title Fix (Repeated here for safety) */
    .wp-block-post-title { display: none !important; }
    
    /* Nav Button Centering override */
    .wp-block-navigation {
        justify-content: center !important;
    }
    </style>';
});
PHP;

file_put_contents($mu_dir . '/fse-styles.php', $style_code);
echo "✅ Installed Typography MU-Plugin.<br>";


// --- PART 2: CENTERED HEADER TEMPLATE (DB Override) ---

$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;

// Header Structure: Group (Vertical, Centered) -> [ Site Title, Navigation ]
// Note: We use "align":"full" for the outer group, but inner content is centered.
$header_content = <<<HTML
<!-- wp:group {"align":"full","className":"header-centered","style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30"}}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"center","alignItems":"center"}} -->
<div class="wp-block-group alignfull header-centered" style="padding-top:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30)">
    
    <!-- wp:site-title {"level":1,"textAlign":"center","style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->

    <!-- wp:navigation {"ref":$nav_id,"overlayMenu":"always","layout":{"type":"flex","justifyContent":"center","orientation":"horizontal"}} /-->

</div>
<!-- /wp:group -->
HTML;

$args = [
    'post_title' => 'Header',
    'post_name' => 'twentytwentyfour//header',
    'post_content' => $header_content,
    'post_status' => 'publish',
    'post_type' => 'wp_template_part',
    'tax_input' => [
        'wp_theme' => ['twentytwentyfour'],
        'wp_template_part_area' => ['header']
    ]
];

// Update or Insert
$query = new WP_Query([
    'post_type' => 'wp_template_part',
    'name' => 'twentytwentyfour//header',
    'post_status' => 'any'
]);

if ($query->have_posts()) {
    $query->the_post();
    $args['ID'] = get_the_ID();
    $id = wp_update_post($args);
    echo "✅ Updated DB Header Override (ID: $id)<br>";
} else {
    $id = wp_insert_post($args);
    echo "✅ Inserted DB Header Override (ID: $id)<br>";
}

if (!is_wp_error($id)) {
    wp_set_object_terms($id, 'twentytwentyfour', 'wp_theme');
    wp_set_object_terms($id, 'header', 'wp_template_part_area');
}

// Flush
if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>