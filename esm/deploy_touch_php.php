<?php
// Deploy PHP Fix
$root = $_SERVER['DOCUMENT_ROOT'];
$php_path = $root . '/wp-content/mu-plugins/esm-trade-portal.php';
$php_code = <<<'PHP_EOD'
<?php
/*
Plugin Name: ESM Trade Portal
Description: Enhanced virtual page at /trade/ with Collections, Search, Premium UI, and Art Visualizer.
Version: 1.2
Author: ESM Dev
*/

echo "<!-- DEBUG: esm-trade-portal.php FILE LOADED -->";

if (!defined('ABSPATH')) exit;

class ESM_Trade_Portal {

    public function __construct() {
        // echo "<!-- DEBUG: __construct entered -->";
        add_action('init', [$this, 'add_endpoint']);
        add_action('template_redirect', [$this, 'render_portal'], 1);
    }

    public function add_endpoint() {
        // echo "<!-- DEBUG: add_endpoint entered -->";
        global $log_file;
        file_put_contents($log_file, "Trace: add_endpoint entered.\n", FILE_APPEND);
        add_rewrite_rule('^trade/?$', 'index.php?esm_trade=1', 'top');
        add_rewrite_tag('%esm_trade%', '1');
    }

    public function render_portal() {
        global $wp_query, $log_file;
        file_put_contents($log_file, "Trace: render_portal entered.\n", FILE_APPEND);
        
        // DEBUG START
        echo "<!-- DEBUG: render_portal entered -->";
        if (isset($wp_query->query_vars['esm_trade'])) {
             echo "<!-- DEBUG: esm_trade var IS set -->";
             file_put_contents($log_file, "Trace: esm_trade IS set.\n", FILE_APPEND);
        } else {
             echo "<!-- DEBUG: esm_trade var NOT set -->";
             file_put_contents($log_file, "Trace: esm_trade NOT set.\n", FILE_APPEND);
        }
        try {
            $url = plugin_dir_url(__FILE__);
            echo "<!-- DEBUG: plugin_url calculated: $url -->";
        } catch (Throwable $t) {
            echo "<!-- DEBUG: plugin_url failed: " . $t->getMessage() . " -->";
        }
        // DEBUG END

        if (!isset($wp_query->query_vars['esm_trade'])) return;

        file_put_contents($log_file, "Trace: Rendering portal content and exiting.\n", FILE_APPEND);
        status_header(200);
        ?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Designer Trade Portal | Elliot Spencer Morgan</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    
    <style>
        :root {
            --bg: #0d0d0d;
            --surface: rgba(255, 255, 255, 0.05);
            --surface-elevated: rgba(255, 255, 255, 0.1);
            --surface-hover: rgba(255, 255, 255, 0.15);
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #E5C07B;
            --border: rgba(255, 255, 255, 0.1);
            --sidebar-w: 320px;
            --header-h: 80px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            -webkit-font-smoothing: antialiased;
        }

        /* Glassmorphism utility */
        .glass {
            background: var(--surface);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid var(--border);
        }

        /* Header */
        header {
            height: var(--header-h);
            display: flex;
            align-items: center;
            padding: 0 3rem;
            z-index: 100;
            justify-content: space-between;
            background: rgba(13, 13, 13, 0.85);
            border-bottom: 1px solid var(--border);
            backdrop-filter: blur(10px);
        }

        .brand {
            font-family: 'Playfair Display', serif;
            font-size: 1.8rem;
            font-weight: 700;
            text-decoration: none;
            color: var(--text-primary);
            letter-spacing: -0.5px;
        }

        .brand span {
            font-family: 'Inter', sans-serif;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 3px;
            color: var(--accent);
            display: block;
            margin-top: -4px;
        }

        .nav-actions { display: flex; align-items: center; gap: 1.5rem; }
        .nav-link {
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            transition: color 0.3s;
        }
        .nav-link:hover { color: var(--text-primary); }

        /* Main Layout */
        .app-container {
            display: flex;
            flex: 1;
            overflow: hidden;
            position: relative;
        }

        /* Sidebar Filters */
        aside {
            width: var(--sidebar-w);
            padding: 2.5rem;
            overflow-y: auto;
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            gap: 2.5rem;
            scrollbar-width: thin;
        }

        .search-box { position: relative; }
        .search-box input {
            width: 100%;
            padding: 1rem 1rem 1rem 2.8rem;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: white;
            font-family: inherit;
            outline: none;
            transition: border-color 0.3s, background 0.3s;
        }
        .search-box input:focus {
            border-color: var(--accent);
            background: var(--surface-elevated);
        }
        .search-box svg {
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            width: 1.2rem;
            height: 1.2rem;
            fill: var(--text-secondary);
        }

        .filter-section { display: flex; flex-direction: column; gap: 1.2rem; }
        .filter-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--text-secondary);
            font-weight: 600;
        }

        .checkbox-group { display: flex; flex-direction: column; gap: 0.8rem; }
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            cursor: pointer;
            font-size: 0.9rem;
            color: var(--text-secondary);
            transition: color 0.2s;
        }
        .checkbox-item:hover { color: var(--text-primary); }
        .checkbox-item input {
            appearance: none;
            width: 16px;
            height: 16px;
            border: 1px solid var(--border);
            border-radius: 4px;
            background: var(--surface);
            cursor: pointer;
            position: relative;
        }
        .checkbox-item input:checked {
            background: var(--accent);
            border-color: var(--accent);
        }
        .checkbox-item input:checked::after {
            content: "✓";
            position: absolute;
            color: #000;
            font-size: 10px;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }

        /* Swatches */
        .swatch-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }
        .swatch {
            aspect-ratio: 1;
            border-radius: 50%;
            cursor: pointer;
            border: 1px solid var(--border);
            position: relative;
            transition: transform 0.2s, border-color 0.2s;
        }
        .swatch:hover { transform: scale(1.1); }
        .swatch.active { border: 2px solid var(--accent); transform: scale(1.1); }

        /* Main View */
        main {
            flex: 1;
            padding: 3rem;
            overflow-y: auto;
            scrollbar-width: thin;
        }

        .view-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 3rem;
        }
        .view-title { font-family: 'Playfair Display', serif; font-size: 3rem; font-weight: 400; }
        .results-count { font-size: 0.9rem; color: var(--text-secondary); letter-spacing: 1px; }

/* Main Grid Fix */
        #artwork-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 2rem;
            width: 100%;
        }

        /* ... existing styles ... */

        /* Visualizer Upload Tab Fix */
        #viz-tab-upload {
            display: block; /* Ensure visible by default */
            padding-top: 1rem;
        }



        /* Premium Card */
        .card {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
            transition: transform 0.4s ease;
            opacity: 0;
            transform: translateY(20px);
        }
        .card.visible { opacity: 1; transform: translateY(0); }

        .image-container {
            width: 100%;
            aspect-ratio: 3/4;
            background: var(--surface);
            overflow: hidden;
            position: relative;
            cursor: pointer;
        }
        .card-image {
            width: 100%;
            height: 100%;
            object-fit: cover;
            filter: grayscale(0.2);
            transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1), filter 0.5s;
        }
        .image-container:hover .card-image {
            transform: scale(1.08);
            filter: grayscale(0);
        }

        .card-actions {
            position: absolute;
            inset: 0;
            background: rgba(13, 13, 13, 0.6);
            backdrop-filter: blur(2px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            opacity: 0;
            transition: all 0.4s;
        }
        .image-container:hover .card-actions { opacity: 1; }

        .btn-premium {
            padding: 14px 28px;
            background: white;
            color: black;
            text-decoration: none;
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 2px;
            transition: background 0.3s, transform 0.2s;
            cursor: pointer;
            border: none;
        }
        .btn-premium:hover { background: var(--accent); transform: scale(1.05); }
        .btn-premium.outline {
            background: transparent;
            border: 1px solid white;
            color: white;
        }
        .btn-premium.outline:hover { background: white; color: black; }
        
        .btn-premium.accent {
            background: var(--accent);
            color: black;
            border: none;
        }
        .btn-premium.accent:hover { background: #fff; }

        .card-details { display: flex; flex-direction: column; gap: 0.3rem; }
        .card-title { font-family: 'Playfair Display', serif; font-size: 1.4rem; font-weight: 400; }
        .card-meta { font-size: 0.85rem; color: var(--text-secondary); font-weight: 300; }
        .card-tag { 
            font-size: 0.7rem; 
            text-transform: uppercase; 
            color: var(--accent); 
            letter-spacing: 1px; 
            margin-top: 0.5rem;
            font-weight: 600;
        }

        /* Loading Overlay */
        #loader-overlay {
            position: fixed; inset: 0; background: var(--bg); z-index: 2000;
            display: flex; justify-content: center; align-items: center;
            transition: opacity 0.5s ease-out;
        }
        
        /* -----------------------------------------------------
           VISUALIZER MODAL STYLES (Adapted for Dark Theme)
           ----------------------------------------------------- */
        #visualizer-modal {
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(15px);
            z-index: 1500;
            display: none; /* Hidden by default */
            flex-direction: column;
        }
        
        #visualizer-modal.active { display: flex; }

        .viz-header {
            padding: 1.5rem 3rem;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .viz-title { font-family: 'Playfair Display'; font-size: 1.5rem; color: #fff; }
        .viz-close {
            background: none; border: none; color: #fff; font-size: 1.5rem; cursor: pointer;
            padding: 0.5rem; transition: color 0.3s;
        }
        .viz-close:hover { color: var(--accent); }

        .viz-body {
            flex: 1;
            display: flex;
            gap: 2rem;
            padding: 2rem;
            overflow: hidden;
        }

        .viz-controls {
            width: 320px;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            overflow-y: auto;
            max-height: 100%; /* Ensure it doesn't overflow parent */
        }

        .viz-canvas-area {
            flex: 1;
            background: #1a1a1a;
            border: 1px solid var(--border);
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background-image: radial-gradient(#333 1px, transparent 1px);
            background-size: 20px 20px;
            touch-action: none;
        }

        .viz-tabs { display: flex; border-bottom: 1px solid var(--border); margin-bottom: 1.5rem; }
        .viz-tab {
            flex: 1; padding: 10px; background: none; border: none;
            color: var(--text-secondary); text-transform: uppercase;
            font-size: 0.75rem; letter-spacing: 1px; cursor: pointer;
            border-bottom: 2px solid transparent;
        }
        .viz-tab.active { color: var(--accent); border-bottom-color: var(--accent); }

        .viz-upload-zone {
            border: 2px dashed var(--border);
            padding: 3rem 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .viz-upload-zone:hover { border-color: var(--accent); background: var(--surface-hover); }

        .viz-unsplash-search input {
            width: 100%; padding: 0.8rem; background: rgba(0,0,0,0.3);
            border: 1px solid var(--border); color: #fff; margin-bottom: 1rem;
        }
        
        .viz-gallery {
            display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
            max-height: 250px; overflow-y: auto; margin-top: 1rem;
        }
        .viz-photo {
            aspect-ratio: 16/9; cursor: pointer; opacity: 0.8; transition: opacity 0.2s;
        }
        .viz-photo:hover { opacity: 1; }
        .viz-photo img { width: 100%; height: 100%; object-fit: cover; }

        /* Art Overlay on Canvas */
        #room-image-layer { 
            max-width: 100%; max-height: 100%; display: none; box-shadow: 0 0 50px rgba(0,0,0,0.5); 
        }
        #art-overlay-layer {
            position: absolute; width: 200px; /* Init size */
            cursor: grab; display: none;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.2);
            touch-action: none;
        }
        #art-overlay-layer:active { cursor: grabbing; border-color: var(--accent); }
        #art-overlay-layer img { width: 100%; height: 100%; display: block; }
        
        .viz-active-art-info {
            background: var(--surface-elevated);
            padding: 1rem;
            border-left: 2px solid var(--accent);
            margin-bottom: 1rem;
        }

        .range-control {
            display: flex; flex-direction: column; gap: 0.5rem;
        }
        .range-control input { width: 100%; accent-color: var(--accent); }
        .range-label { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-secondary); }

        /* Mobile Responsiveness */
        @media (max-width: 992px) {
            :root {
                --sidebar-w: 100%;
                --header-h: 70px;
            }

            header {
                padding: 0 1.5rem;
            }

            .brand {
                font-size: 1.4rem;
            }

            .nav-actions {
                display: none; /* Hide top nav links on mobile to save space */
            }

            .app-container {
                flex-direction: column;
            }

            aside {
                position: fixed;
                top: var(--header-h);
                left: -100%;
                width: 100%;
                height: calc(100vh - var(--header-h));
                background: var(--bg);
                z-index: 1000;
                transition: left 0.4s cubic-bezier(0.16, 1, 0.3, 1);
                border-right: none;
                border-bottom: 1px solid var(--border);
                padding: 1.5rem;
            }

            aside.active {
                left: 0;
            }

            main {
                padding: 1.5rem;
            }

            .view-header {
                flex-direction: column;
                gap: 0.5rem;
                margin-bottom: 2rem;
            }

            .view-title {
                font-size: 2rem;
            }

            #artwork-grid {
                grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
                gap: 1rem;
            }

            .card-title {
                font-size: 1.1rem;
            }

            .card-meta {
                font-size: 0.75rem;
            }

            /* Visualizer Mobile */
            .viz-body {
                flex-direction: column;
                padding: 1rem;
                gap: 1rem;
                overflow-y: auto;
            }

            .viz-controls {
                width: 100%;
                max-height: none;
                order: 2;
                padding: 1.5rem;
            }

            .viz-canvas-area {
                width: 100%;
                height: 40vh;
                flex: none;
                order: 1;
            }

            .viz-header {
                padding: 1rem 1.5rem;
            }

            .viz-title {
                font-size: 1.2rem;
            }

            .btn-premium {
                padding: 10px 15px;
                font-size: 0.7rem;
            }
        }

        /* Menu Toggle Button */
        .mobile-filter-btn {
            display: none;
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--accent);
            padding: 8px 16px;
            border-radius: 4px;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            align-items: center;
            gap: 8px;
        }

        @media (max-width: 992px) {
            .mobile-filter-btn {
                display: flex;
            }
        }
            /* Loading screen fix */
            #loader-overlay { pointer-events: none; }
            #loader-overlay.active { pointer-events: auto; }
</style>
</head>
<body>

    <div id="loader-overlay">
        <div class="view-title">ELLIOT SPENCER MORGAN</div>
    </div>

    <!-- MAIN APP STRUCTURE -->
    <header>
        <a href="/" class="brand">ESM <span>Trade Portal</span></a>
        <div class="nav-actions">
            <a href="/" class="nav-link">Gallery</a>
            <a href="/contact/" class="nav-link">Inquire</a>
        </div>
        <button class="mobile-filter-btn" onclick="toggleSidebar()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/></svg>
            Filters
        </button>
    </header>

    <div class="app-container">
        <!-- SIDEBAR -->
        <aside>
            <div class="search-box">
                <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                <input type="text" id="global-search" placeholder="Search title or series...">
            </div>

            <div class="filter-section">
                <div class="filter-label">Collections</div>
                <div class="checkbox-group" id="collection-filters">
                    <!-- JS Populated -->
                </div>
            </div>

            <div class="filter-section">
                <div class="filter-label">Dimensions</div>
                <div class="checkbox-group">
                    <label class="checkbox-item"><input type="checkbox" name="size" value="Small"> Small (Under 20")</label>
                    <label class="checkbox-item"><input type="checkbox" name="size" value="Medium"> Medium (20" - 40")</label>
                    <label class="checkbox-item"><input type="checkbox" name="size" value="Large"> Large (40" - 60")</label>
                    <label class="checkbox-item"><input type="checkbox" name="size" value="Oversized"> Oversized (60"+)</label>
                </div>
            </div>

            <div class="filter-section">
                <div class="filter-label">Dominant Tone</div>
                <div class="swatch-grid" id="color-filters">
                    <!-- JS Populated -->
                </div>
            </div>
        </aside>

        <!-- MAIN GRID -->
        <main>
            <div class="view-header">
                <div class="view-title" id="page-title">Curated Selection</div>
                <div class="results-count" id="count-display">Analyzing works...</div>
            </div>
            
            <div id="artwork-grid">
                <!-- Artworks here -->
            </div>
        </main>
    </div>

    <!-- VISUALIZER MODAL -->
    <div id="visualizer-modal">
        <div class="viz-header">
            <div class="viz-title">In-Situ Visualizer</div>
            <button class="viz-close" onclick="closeVisualizer()">✕</button>
        </div>
        <div class="viz-body">
            <!-- VIZ CONTROLS -->
            <div class="viz-controls">
                
                <div class="viz-active-art-info">
                    <div style="font-size:0.7rem; color:var(--text-secondary); text-transform:uppercase; margin-bottom:5px;">Currently Viewing</div>
                    <div id="viz-art-title" style="font-family:'Playfair Display'; font-size:1.2rem; color:var(--accent);">Select Artwork</div>
                    <div id="viz-art-dims" style="font-size:0.85rem; color:var(--text-secondary);">Dimensions</div>
                </div>

                <div class="range-control">
                    <div class="range-label"><span>Scale</span> <span id="scale-val">70%</span></div>
                    <input type="range" id="viz-scale" min="20" max="150" value="70">
                </div>

                <div class="range-control">
                    <div class="range-label"><span>Rotation</span> <span id="rot-val">0°</span></div>
                    <input type="range" id="viz-rot" min="-15" max="15" value="0">
                </div>

                <hr style="border:0; border-top:1px solid var(--border);">

                <div class="viz-tabs">
                    <button class="viz-tab active" onclick="switchVizTab('upload')">Upload Room</button>
                    <button class="viz-tab" onclick="switchVizTab('camera')">Camera</button>
                    <button class="viz-tab" onclick="switchVizTab('unsplash')">Unsplash</button>
                </div>

                <div id="viz-tab-upload" style="display:block;">
                    <div class="viz-upload-zone" onclick="document.getElementById('room-upload-input').click()">
                        <div style="font-size:2rem; margin-bottom:1rem;">📷</div>
                        <div>Click to Upload Room Photo</div>
                        <input type="file" id="room-upload-input" accept="image/*" style="display:none">
                    </div>
                </div>

                <div id="viz-tab-camera" style="display:none;">
                    <div style="text-align:center;">
                        <video id="camera-stream" playsinline autoplay style="width:100%; border-radius:8px; background:#000; display:none; margin-bottom:10px;"></video>
                        <div id="camera-error" style="color:var(--accent); font-size:0.8rem; margin-bottom:10px; display:none;"></div>
                        
                        <div id="camera-controls">
                            <button class="btn-premium outline" style="width:100%; margin-bottom:10px;" onclick="startCamera()">Start Camera</button>
                        </div>
                        
                        <button id="btn-capture" class="btn-premium accent" style="width:100%; display:none;" onclick="capturePhoto()">Capture Photo</button>
                    </div>
                </div>

                <div id="viz-tab-unsplash" style="display:none;">
                    <div class="viz-unsplash-search">
                        <input type="text" id="unsplash-query" placeholder="E.g. modern living room">
                        <button class="btn-premium outline" style="width:100%;" onclick="searchUnsplash()">Search</button>
                    </div>
                    <div class="viz-gallery" id="unsplash-results">
                        <!-- Results -->
                    </div>
                </div>

                <div style="margin-top:auto; display:flex; flex-direction:column; gap:10px;">
                    <button id="btn-download-pdf" class="btn-premium outline" style="width:100%;" onclick="downloadVisualizerPDF()">Download Scene as PDF</button>
                    <button id="btn-share-scene" class="btn-premium outline" style="width:100%; margin-top:10px;" onclick="shareVisualizerScene()">Share Scene</button>
                    <button class="btn-premium" style="width:100%; margin-top:10px;" onclick="closeVisualizer()">Select Different Art</button>
                </div>

            </div>

            <!-- VIZ CANVAS -->
            <div class="viz-canvas-area" id="viz-canvas">
                <div id="viz-placeholder" style="text-align:center; color:var(--text-secondary);">
                    <h1>🏠</h1>
                    <p>Upload a room photo to start</p>
                </div>
                <img id="room-image-layer">
                <div id="art-overlay-layer">
                    <img id="art-overlay-img">
                </div>
            </div>
        </div>
    </div>

    <!-- JS loaded via wp_enqueue_script in PHP class -->
    <script src="<?php echo plugin_dir_url(__FILE__); ?>esm-trade-portal.js?v=1.4.2"></script>
</body>
</html>
        <?php
        exit;
    }
}


// DEBUG TRACE
$log_file = dirname(__FILE__) . '/trace.log';
file_put_contents($log_file, "Trace: File loaded at " . date('Y-m-d H:i:s') . "\n", FILE_APPEND);

try {
    file_put_contents($log_file, "Trace: Instantiating class...\n", FILE_APPEND);
    new ESM_Trade_Portal();
    file_put_contents($log_file, "Trace: Instantiation complete.\n", FILE_APPEND);
} catch (Throwable $e) {
    file_put_contents($log_file, "Trace: CRASH: " . $e->getMessage() . "\n" . $e->getTraceAsString() . "\n", FILE_APPEND);
    echo "<!-- DEBUG: CRASH CAUGHT: " . $e->getMessage() . " -->";
}

PHP_EOD;

if (file_put_contents($php_path, $php_code)) {
    echo "<div style='color:green'>✅ PHP deployed to $php_path</div>";
} else {
    echo "<div style='color:red'>❌ Failed to deploy PHP to $php_path</div>";
}
?>
