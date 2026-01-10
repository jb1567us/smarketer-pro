<?php
// build_static_portfolio.php
// Generate complete static HTML portfolio

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// Get all posts
$posts = get_posts([
    'post_type' => 'post',
    'posts_per_page' => -1,
    'post_status' => 'publish',
    'orderby' => 'date',
    'order' => 'DESC'
]);

// Start building HTML
$html = '<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elliot Spencer Morgan - Portfolio</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: "Inter", sans-serif;
            line-height: 1.6;
            color: #333;
            background: #fff;
        }
        
        header {
            text-align: center;
            padding: 2rem 1rem 1rem;
            border-bottom: 1px solid #eee;
        }
        
        h1 {
            font-family: "Playfair Display", serif;
            font-size: 2.5rem;
            font-weight: 400;
            margin-bottom: 1rem;
            color: #1a1a1a;
        }
        
        .logo {
            width: 180px;
            max-width: 100%;
            margin: 0 auto 1rem;
            display: block;
        }
        
        .hamburger {
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 1.5rem;
            cursor: pointer;
            background: none;
            border: none;
            padding: 0.5rem;
        }
        
        nav {
            position: fixed;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100vh;
            background: #fff;
            z-index: 1000;
            transition: left 0.3s ease;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        nav.active { left: 0; }
        
        nav a {
            font-size: 1.5rem;
            margin: 1rem 0;
            text-decoration: none;
            color: #333;
        }
        
        .close-btn {
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 2rem;
            cursor: pointer;
            background: none;
            border: none;
        }
        
        main {
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }
        
        .artwork-item {
            margin-bottom: 3rem;
            text-align: center;
        }
        
        .artwork-item img {
            width: 100%;
            height: auto;
            display: block;
            transition: opacity 0.3s ease;
            border-radius: 4px;
        }
        
        .artwork-item a:hover img {
            opacity: 0.85;
        }
        
        .artwork-title {
            margin-top: 0.75rem;
            font-size: 1.1rem;
            color: #333;
            font-weight: 400;
        }
        
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            main { padding: 1.5rem 1rem; }
        }
    </style>
</head>
<body>
    <header>
        <button class="hamburger" onclick="toggleMenu()">☰</button>
        <h1>Elliot Spencer Morgan</h1>
        <img src="https://elliotspencermorgan.com/logo.png" alt="ESM Logo" class="logo">
    </header>
    
    <nav id="nav">
        <button class="close-btn" onclick="toggleMenu()">✕</button>
        <a href="/">Portfolio</a>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
    </nav>
    
    <main>';

// Add each artwork
foreach ($posts as $post) {
    $thumbnail_id = get_post_thumbnail_id($post->ID);
    if (!$thumbnail_id)
        continue;

    $image_url = wp_get_attachment_image_url($thumbnail_id, 'large');
    $title = get_the_title($post->ID);

    // Create Saatchi URL
    $slug = sanitize_title($title);
    $slug = str_replace(['-painting', '-sculpture', '-collage', '-installation', '-print'], '', $slug);
    $saatchi_url = 'https://www.saatchiart.com/art/Painting-' . ucfirst($slug);

    $html .= '
        <div class="artwork-item">
            <a href="' . esc_url($saatchi_url) . '" target="_blank" rel="noopener">
                <img src="' . esc_url($image_url) . '" alt="' . esc_attr($title) . '" loading="lazy">
            </a>
            <div class="artwork-title">' . esc_html($title) . '</div>
        </div>';
}

$html .= '
    </main>
    
    <script>
        function toggleMenu() {
            document.getElementById("nav").classList.toggle("active");
        }
    </script>
</body>
</html>';

// Save to file
file_put_contents($_SERVER['DOCUMENT_ROOT'] . '/portfolio.html', $html);

echo "<h1>✅ Portfolio Generated!</h1>";
echo "<p>Created portfolio.html with " . count($posts) . " artworks</p>";
echo "<br><a href='/portfolio.html'>View Portfolio</a>";
?>