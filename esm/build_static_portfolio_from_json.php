<?php
// build_static_portfolio_from_json.php
// Generate complete static HTML portfolio using artwork_data.json source of truth

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>🎨 Building Portfolio from JSON Data</h1>";

// 1. Load the JSON data
$json_path = dirname(__FILE__) . '/artwork_data.json';
if (!file_exists($json_path)) {
    die("❌ Error: artwork_data.json not found at $json_path");
}

$json_content = file_get_contents($json_path);
$artworks = json_decode($json_content, true);

if (!$artworks) {
    die("❌ Error: Failed to parse artwork_data.json");
}

echo "✅ Loaded " . count($artworks) . " items from artwork_data.json<br>";

// 2. Start building HTML
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
            background: #fff;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        h1 {
            font-family: "Playfair Display", serif;
            font-size: 2.2rem;
            font-weight: 400;
            margin-bottom: 0.5rem;
            color: #1a1a1a;
        }
        
        .logo {
            width: 140px;
            max-width: 100%;
            margin: 0.5rem auto 0;
            display: block;
        }
        
        /* Mobile Hamburger */
        .hamburger {
            position: absolute;
            top: 25px;
            right: 20px;
            font-size: 1.5rem;
            cursor: pointer;
            background: none;
            border: none;
            padding: 0.5rem;
            z-index: 1001;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            width: 2rem;
            height: 2rem;
        }

        .hamburger span {
            width: 100%;
            height: 2px;
            background-color: #333;
            transition: all 0.3s ease;
        }
        
        /* Fullscreen Navigation Overlay */
        nav {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100vh;
            background: #fff;
            z-index: 1000;
            display: flex; /* Use flexbox to center content */
            flex-direction: column;
            justify-content: center;
            align-items: center;
            
            /* Hidden state */
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s ease, visibility 0.3s ease;
        }
        
        /* Active state */
        nav.active { 
            opacity: 1;
            visibility: visible;
        }
        
        nav a {
            font-family: "Playfair Display", serif;
            font-size: 2rem;
            margin: 1.5rem 0;
            text-decoration: none;
            color: #333;
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.4s ease, transform 0.4s ease;
        }
        
        nav.active a {
            opacity: 1;
            transform: translateY(0);
        }

        /* Staggered animation for links */
        nav.active a:nth-child(1) { transition-delay: 0.1s; }
        nav.active a:nth-child(2) { transition-delay: 0.2s; }
        nav.active a:nth-child(3) { transition-delay: 0.3s; }
        
        main {
            max-width: 600px;
            margin: 0 auto;
            padding: 3rem 1rem;
        }
        
        .artwork-item {
            margin-bottom: 4rem;
            text-align: center;
        }
        
        .artwork-item img {
            width: 100%;
            height: auto;
            display: block;
            /* margin-bottom to separate from title */
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        }
        
        .artwork-item a {
            display: block; /* Ensure the link wraps the image */
            transition: opacity 0.3s ease;
        }

        .artwork-item a:hover {
            opacity: 0.9;
        }
        
        .artwork-title {
            margin-top: 1rem;
            font-family: "Inter", sans-serif;
            font-size: 0.95rem;
            color: #555;
            letter-spacing: 0.02em;
            text-transform: uppercase;
        }
        
        footer {
            text-align: center;
            padding: 3rem 1rem;
            font-size: 0.8rem;
            color: #888;
            border-top: 1px solid #f5f5f5;
            margin-top: 2rem;
        }

        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; }
            .logo { width: 120px; }
            main { padding: 2rem 1rem; }
            .artwork-item { margin-bottom: 3rem; }
        }
    </style>
</head>
<body>
    <header>
        <button class="hamburger" onclick="toggleMenu()" aria-label="Toggle Menu">
            <span></span>
            <span></span>
            <span></span>
        </button>
        <h1>Elliot Spencer Morgan</h1>
        <img src="https://elliotspencermorgan.com/logo.png" alt="ESM Logo" class="logo">
    </header>
    
    <nav id="nav">
        <a href="portfolio.html" onclick="toggleMenu()">Portfolio</a>
        <a href="#" onclick="alert(\'Coming Soon\')">About</a>
        <a href="#" onclick="alert(\'Coming Soon\')">Contact</a>
    </nav>
    
    <main>';

// 3. Loop through artworks and add to HTML
$count = 0;
foreach ($artworks as $item) {
    // Only verify image if we aren't sure, but JSON has the URLs directly.
    // We trust the image_url from JSON as source of truth.
    if (empty($item['image_url']))
        continue;

    $title = isset($item['cleanTitle']) ? $item['cleanTitle'] : $item['title'];

    // Explicit exclusion per user request
    if (strcasecmp($title, 'Red Planet') === 0)
        continue;

    $image_url = $item['image_url'];

    // Saatchi URL logic
    $saatchi_url = '';
    if (!empty($item['saatchi_url'])) {
        $saatchi_url = $item['saatchi_url'];
    } else {
        // Fallback generator
        $slug = sanitize_title($title);
        $slug = str_replace(['-painting', '-sculpture', '-collage', '-installation', '-print'], '', $slug);
        $saatchi_url = 'https://www.saatchiart.com/art/Painting-' . ucfirst($slug);
    }

    $html .= '
        <div class="artwork-item">
            <a href="' . esc_url($saatchi_url) . '" target="_blank" rel="noopener">
                <img src="' . esc_url($image_url) . '" alt="' . esc_attr($title) . '" loading="lazy">
            </a>
            <div class="artwork-title">' . esc_html($title) . '</div>
        </div>';
    $count++;
}

$html .= '
    </main>
    
    <footer>
        &copy; ' . date("Y") . ' Elliot Spencer Morgan. All rights reserved.
    </footer>

    <script>
        function toggleMenu() {
            const nav = document.getElementById("nav");
            const hamburger = document.querySelector(".hamburger");
            nav.classList.toggle("active");
            
            // Simple hamburger animation toggle
            const spans = hamburger.querySelectorAll("span");
            if (nav.classList.contains("active")) {
                spans[0].style.transform = "rotate(45deg) translate(5px, 5px)";
                spans[1].style.opacity = "0";
                spans[2].style.transform = "rotate(-45deg) translate(5px, -5px)";
            } else {
                spans[0].style.transform = "none";
                spans[1].style.opacity = "1";
                spans[2].style.transform = "none";
            }
        }
    </script>
</body>
</html>';

// 4. Save to file
file_put_contents($_SERVER['DOCUMENT_ROOT'] . '/portfolio.html', $html);

echo "<h1>✅ Portfolio HTML Generated!</h1>";
echo "<p>Processed $count artworks from JSON data.</p>";
echo "<br><a href='/portfolio.html' target='_blank'>View Live Portfolio</a>";

if (function_exists('opcache_reset'))
    opcache_reset();
?>