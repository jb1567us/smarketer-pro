<?php
// force_global_style.php
// 1. "Nuclear" CSS to force centering regardless of HTML structure
// 2. Identify and Overwrite ALL Header Template Parts

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🚀 Force Global Style (Nuclear Option)</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
if (!is_dir($mu_dir)) {
    mkdir($mu_dir, 0755, true);
}

// --- PART 1: NUCLEAR CSS ---
// This CSS targets the blocks directly, ignoring container alignment.
$css_code = <<<'PHP'
<?php
/* Plugin Name: Nuclear Center Styles */
add_action('wp_head', function() {
    echo '<style>
    /* 1. Force Site Title */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin-bottom: 1rem !important;
    }
    .wp-block-site-title a {
        font-family: "Playfair Display", serif !important;
        font-weight: 400 !important;
        text-decoration: none !important;
        font-size: 2rem !important;
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }

    /* 2. Force Hamburger / Navigation */
    .wp-block-navigation {
        justify-content: center !important;
        width: 100% !important;
        display: flex !important;
    }
    /* Inner Container for Hamburger */
    .wp-block-navigation__responsive-container {
        justify-content: center !important;
    }
    .wp-block-navigation__responsive-container-open {
        margin: 0 auto !important; /* Center the button itself */
        display: flex !important;
    }
    
    /* 3. Force Header Group Container to Column */
    /* Attempt to target the top-level header group */
    header .wp-block-group {
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* 4. Hide Double Title (Double Check) */
    .wp-block-post-title { display: none !important; }

    /* 5. Hide the Default Page List if it leaks through */
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999); // Late priority
PHP;

file_put_contents($mu_dir . '/nuclear-styles.php', $css_code);
echo "✅ Installed 'Nuclear' CSS MU-Plugin.<br>";


// --- PART 2: BLANKET DB OVERRIDE ---
// Find ANY wp_template_part that looks like a header and overwrite it.

$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
$nav_id = $nav ? $nav->ID : 0;

$header_content = <<<HTML
<!-- wp:group {"align":"full","style":{"spacing":{"padding":{"top":"var:preset|spacing|30","bottom":"var:preset|spacing|30"}}},"layout":{"type":"flex","orientation":"vertical","justifyContent":"center","alignItems":"center"}} -->
<div class="wp-block-group alignfull" style="padding-top:var(--wp--preset--spacing--30);padding-bottom:var(--wp--preset--spacing--30)">
    <!-- wp:site-title {"level":1,"textAlign":"center","style":{"typography":{"fontStyle":"normal","fontWeight":"400"}}} /-->
    <!-- wp:navigation {"ref":$nav_id,"overlayMenu":"always","layout":{"type":"flex","justifyContent":"center","orientation":"horizontal"}} /-->
</div>
<!-- /wp:group -->
HTML;

$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [
        [
            'taxonomy' => 'wp_template_part_area',
            'field' => 'slug',
            'terms' => 'header'
        ]
    ]
]);

if ($headers) {
    foreach ($headers as $h) {
        $update = [
            'ID' => $h->ID,
            'post_content' => $header_content
        ];
        wp_update_post($update);
        echo "✅ Updated Loop: Header ID " . $h->ID . " (" . $h->post_name . ")<br>";
    }
} else {
    echo "⚠️ No existing Header template parts found to update via loop.<br>";
    // Fallback: Ensure 'twentytwentyfour//header' exists
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
    // ... insert logic (omitted for brevity, previous script handled insertion)
    $id = wp_insert_post($args); // Try insert
    if (!is_wp_error($id)) {
        wp_set_object_terms($id, 'twentytwentyfour', 'wp_theme');
        wp_set_object_terms($id, 'header', 'wp_template_part_area');
        echo "✅ Created fallback 'twentytwentyfour//header' (ID: $id)<br>";
    }
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/sheet_music/'>Check /sheet_music/</a>";
?>