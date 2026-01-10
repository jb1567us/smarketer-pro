<?php
// Deploy Share Button
$root = $_SERVER['DOCUMENT_ROOT'];
$plugin_path = $root . '/wp-content/mu-plugins/esm-trade-portal.php';

$plugin_code = <<<'PHP_EOD'
<?php
/*
Plugin Name: ESM Trade Portal
Description: Enhanced virtual page at /trade/ with Collections, Search, Premium UI, and Art Visualizer.
Version: 1.2
Author: ESM Dev
*/

if (!defined('ABSPATH')) exit;

class ESM_Trade_Portal {

    public function __construct() {
        add_action('init', [$this, 'add_endpoint']);
        add_action('template_redirect', [$this, 'render_portal']);
    }

    public function add_endpoint() {
        add_rewrite_rule('^trade/?$', 'index.php?esm_trade=1', 'top');
        add_rewrite_tag('%esm_trade%', '1');
    }

    public function render_portal() {
        global $wp_query;
        if (!isset($wp_query->query_vars['esm_trade'])) return;

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

    <script>
        const ART_DATA_URL = '/artwork_data.json';
        const COLL_DATA_URL = '/collections_data.json';
        const UNSPLASH_KEY = '8gzaWlidpscOoUenn-sYrdR-UxdI_kPcxvYgnHfq8l0'; // Public Demo Key
        const DEFAULT_ROOM = '/istockphoto-1535511484-1024x1024.jpg';

        let artworks = [];
        let collections = {};
        let activeFilters = {
            search: '',
            collections: new Set(),
            sizes: new Set(),
            colors: new Set()
        };

        // State for Visualizer
        let vizState = {
            art: null,
            roomLoaded: false
        };

        const colorMap = {
            'Red': '#c0392b', 'Blue': '#2980b9', 'Green': '#27ae60', 'Gold': '#d4af37',
            'Silver': '#bdc3c7', 'Black': '#000000', 'Grey': '#7f8c8d', 'White': '#ffffff',
            'Pink': '#e84393', 'Brown': '#63422d', 'Beige': '#f5f5dc', 'Purple': '#8e44ad',
            'Orange': '#d35400', 'Yellow': '#f1c40f'
        };

        function safeSetText(id, text) {
            const el = document.getElementById(id);
            if(el) el.textContent = text;
        }

        function safeSetVal(id, val) {
            const el = document.getElementById(id);
            if(el) el.value = val;
        }

        async function init() {
            try {
                console.log("Portal Init v1.4.2 - ArtMap Active");
                // Parallel fetch with cache busting
                const [artRes, collRes] = await Promise.all([
                    fetch(ART_DATA_URL, {cache: "no-store"}),
                    fetch(COLL_DATA_URL, {cache: "no-store"})
                ]);
                
                if (!artRes.ok || !collRes.ok) throw new Error("Failed to fetch data assets");

                const artRaw = await artRes.json();
                collections = await collRes.json();

                // Create a reverse lookup for membership
                const artToCollections = {};
                Object.values(collections).forEach(coll => {
                    if(coll.artworks) {
                        coll.artworks.forEach(a => {
                            if(!artToCollections[a.title]) artToCollections[a.title] = [];
                            artToCollections[a.title].push(coll.title);
                        });
                    }
                });

                // Process Artworks - Deduplicate by Image URL & Prioritize items with Dimensions
                const artMap = new Map();

                artRaw.forEach(a => {
                    if (!a.image_url) return;
                    
                    // Attach membership from collections
                    a.membership = artToCollections[a.title] || [];

                    const hasDims = (a.width && a.height && a.width !== 'undefined' && a.height !== 'undefined');
                    const existing = artMap.get(a.image_url);

                    if (existing) {
                        const existingHasDims = (existing.width && existing.height && existing.width !== 'undefined' && existing.height !== 'undefined');
                        // If existing has no dims but new one DOES, replace it
                        if (hasDims && !existingHasDims) {
                            artMap.set(a.image_url, a);
                        } 
                        // If both have dims or both don't, check if the NEW one is "better" (e.g. has more data)
                        // For now, we stick to the first one unless the new one has dimensions and old one doesn't.
                    } else {
                        // NEW: Slug/Title Collision Check
                        // Before adding by image_url, check if we already have this Title/Slug under a different Image URL
                        let duplicateFound = false;
                        for (const [key, val] of artMap.entries()) {
                             // Check slug match
                             if(a.slug && val.slug && a.slug === val.slug) {
                                  duplicateFound = true;
                                  // If new one has dims and old one doesn't, REPLACE the old key
                                  const valHasDims = (val.width && val.height && val.width !== 'undefined' && val.height !== 'undefined');
                                  if(hasDims && !valHasDims) {
                                      artMap.delete(key); // Remove old entry
                                      artMap.set(a.image_url, a); // Add new one
                                  }
                                  break; 
                             }
                        }
                        
                        if(!duplicateFound) {
                            artMap.set(a.image_url, a);
                        }
                    }

                    // Ensure link is present
                    if (a.type === 'page') {
                        if(a.slug) a.link = '/' + a.slug + '/';
                    } else {
                        if(a.slug) a.link = '/' + a.slug + '/';
                        else if(a.title) a.link = '/' + a.title.toLowerCase().replace(/ /g, '-').replace(/[^\w-]+/g, '') + '/';
                    }
                });

                artworks = Array.from(artMap.values());

                renderFilters();
                applyFilters();
                
                // Check for Preview Request (from Artwork Page)
                const urlParams = new URLSearchParams(window.location.search);
                const previewTitle = urlParams.get('preview');
                
                if(previewTitle) {
                    const decoded = decodeURIComponent(previewTitle).toLowerCase();
                    const targetArt = artworks.find(a => a.title.toLowerCase() === decoded);
                    
                    if(targetArt) {
                        console.log("Auto-launching visualizer for:", targetArt.title);
                        openVisualizer(targetArt);
                        
                        // Clean URL without refresh
                        const newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
                        window.history.pushState({path:newUrl},'',newUrl);
                    }
                }

                // Remove loader
                setTimeout(() => {
                    const loader = document.getElementById('loader-overlay');
                    if(loader) {
                        loader.style.opacity = '0';
                        setTimeout(() => loader.remove(), 500);
                    }
                }, 800);

            } catch (err) {
                console.error("Portal Init Error:", err);
                const grid = document.getElementById('artwork-grid');
                if(grid) {
                    grid.innerHTML = `<div style="grid-column:1/-1; text-align:center; padding:50px; color:var(--text-secondary);">
                        <h2 style="font-family:'Playfair Display'; color:white; margin-bottom:20px;">Portal Error (v1.4)</h2>
                        <p>We encountered an issue loading the gallery. Please clear your cache and refresh.</p>
                        <p style="font-size:0.8rem; margin-top:10px; color:#555;">${err.message}</p>
                    </div>`;
                }
            }
        }

        // ============================================
        // FILTER & GRID LOGIC
        // ============================================

        function renderFilters() {
            // Render Collections
            const collContainer = document.getElementById('collection-filters');
            if(collContainer) {
                collContainer.innerHTML = ''; // Clear first
                Object.values(collections).sort((a,b) => a.title.localeCompare(b.title)).forEach(coll => {
                    const label = document.createElement('label');
                    label.className = 'checkbox-item';
                    label.innerHTML = `<input type="checkbox" value="${coll.title}"> ${coll.title}`;
                    label.querySelector('input').addEventListener('change', (e) => {
                        if(e.target.checked) activeFilters.collections.add(coll.title);
                        else activeFilters.collections.delete(coll.title);
                        applyFilters();
                    });
                    collContainer.appendChild(label);
                });
            }

            // Render Colors
            const colorContainer = document.getElementById('color-filters');
            if(colorContainer) {
                colorContainer.innerHTML = ''; // Clear first
                const uniqueColors = new Set();
                artworks.forEach(a => a.detected_colors?.forEach(c => uniqueColors.add(c)));
                
                Array.from(uniqueColors).sort().forEach(color => {
                    const div = document.createElement('div');
                    div.className = 'swatch';
                    div.style.backgroundColor = colorMap[color] || '#ccc';
                    div.title = color;
                    div.addEventListener('click', () => {
                        div.classList.toggle('active');
                        if(div.classList.contains('active')) activeFilters.colors.add(color);
                        else activeFilters.colors.delete(color);
                        applyFilters();
                    });
                    colorContainer.appendChild(div);
                });
            }

            // Search listener
            const searchInput = document.getElementById('global-search');
            if(searchInput) {
                // Remove old listeners to prevent dupes if re-run (not critical here but good practice)
                const newSearch = searchInput.cloneNode(true);
                searchInput.parentNode.replaceChild(newSearch, searchInput);
                
                newSearch.addEventListener('input', (e) => {
                    activeFilters.search = e.target.value.toLowerCase().trim();
                    applyFilters();
                });
            }

            // Size listeners
            document.querySelectorAll('input[name="size"]').forEach(el => {
                el.addEventListener('change', (e) => {
                    if(e.target.checked) activeFilters.sizes.add(e.target.value);
                    else activeFilters.sizes.delete(e.target.value);
                    applyFilters();
                });
            });
        }

        function applyFilters() {
            const filtered = artworks.filter(art => {
                // Search
                if(activeFilters.search) {
                    const matchTitle = art.title.toLowerCase().includes(activeFilters.search);
                    const matchColl = art.membership && art.membership.some(m => m.toLowerCase().includes(activeFilters.search));
                    if(!matchTitle && !matchColl) return false;
                }
                
                // Collection
                if(activeFilters.collections.size > 0) {
                    if(!art.membership || !art.membership.some(m => activeFilters.collections.has(m))) return false;
                }

                // Size
                if(activeFilters.sizes.size > 0) {
                    const w = parseFloat(art.width);
                    let sizeMatch = false;
                    if(activeFilters.sizes.has('Small') && w < 20) sizeMatch = true;
                    if(activeFilters.sizes.has('Medium') && w >= 20 && w < 40) sizeMatch = true;
                    if(activeFilters.sizes.has('Large') && w >= 40 && w < 60) sizeMatch = true;
                    if(activeFilters.sizes.has('Oversized') && w >= 60) sizeMatch = true;
                    if(!sizeMatch) return false;
                }

                // Color
                if(activeFilters.colors.size > 0) {
                    if(!art.detected_colors?.some(c => activeFilters.colors.has(c))) return false;
                }

                return true;
            });

            renderGrid(filtered);
            safeSetText('count-display', `${filtered.length} Works Identified`);
        }

        function renderGrid(items) {
            const grid = document.getElementById('artwork-grid');
            if(!grid) return;
            
            grid.innerHTML = '';
            
            items.forEach((item, index) => {
                const card = document.createElement('div');
                card.className = 'card';
                
                const specUrl = `/downloads/spec_sheets/${item.slug}_spec.pdf`;
                const membershipDisplay = (item.membership && item.membership.length > 0) ? item.membership[0] : 'Original Series';

                card.innerHTML = `
                    <div class="image-container">
                        <img src="${item.image_url}" class="card-image" loading="lazy">
                        <div class="card-actions">
                            <button class="btn-premium accent" onclick="openVisualizerById('${item.id}')">Visualize in Room</button>
                            <a href="${item.link}" target="_blank" class="btn-premium">View Details</a>
                            <a href="${specUrl}" download class="btn-premium outline">Spec Sheet</a>
                        </div>
                    </div>
                    <div class="card-details">
                        <div class="card-title">${item.title}</div>
                        <div class="card-meta">${item.dimensions || item.width + ' x ' + item.height + ' in'}</div>
                        <div class="card-tag">${membershipDisplay}</div>
                    </div>
                `;
                grid.appendChild(card);
                setTimeout(() => card.classList.add('visible'), index * 30);
            });
        }
        
        function openVisualizerById(id) {
            const art = artworks.find(a => a.id == id);
            if(art) openVisualizer(art);
        }

        // ============================================
        // VISUALIZER LOGIC
        // ============================================

        function openVisualizer(art) {
            vizState.art = art;
            
            // Update UI sidebar
            safeSetText('viz-art-title', art.title);
            safeSetText('viz-art-dims', art.dimensions || `${art.width} x ${art.height} in`);
            
            const modal = document.getElementById('visualizer-modal');
            if(modal) modal.classList.add('active');

            // Load art into overlay
            const artImg = document.getElementById('art-overlay-img');
            if(artImg) artImg.src = art.image_url;
            
            if(!vizState.roomLoaded) {
                setRoomImage(DEFAULT_ROOM);
            } else {
                addArtToRoom();
            }
        }

        function closeVisualizer() {
            const modal = document.getElementById('visualizer-modal');
            if(modal) modal.classList.remove('active');
            stopCamera();
        }

        function switchVizTab(tabName) {
            document.querySelectorAll('.viz-tab').forEach(t => t.classList.remove('active'));
            
            // Fix: more robust selection
            const buttons = document.querySelectorAll('.viz-tab');
            buttons.forEach(b => {
                 if(b.textContent.toLowerCase().includes(tabName)) b.classList.add('active');
            });
            
            const uploadTab = document.getElementById('viz-tab-upload');
            const unsplashTab = document.getElementById('viz-tab-unsplash');
            const cameraTab = document.getElementById('viz-tab-camera');

            if(uploadTab) uploadTab.style.display = 'none';
            if(unsplashTab) unsplashTab.style.display = 'none';
            if(cameraTab) cameraTab.style.display = 'none';
            
            stopCamera(); // Ensure camera stops when switching away

            if(tabName === 'upload' && uploadTab) uploadTab.style.display = 'block';
            if(tabName === 'unsplash' && unsplashTab) unsplashTab.style.display = 'block';
            if(tabName === 'camera' && cameraTab) cameraTab.style.display = 'block';
        }

        // Camera Logic
        let cameraStream = null;

        async function startCamera() {
            const errorEl = document.getElementById('camera-error');
            const video = document.getElementById('camera-stream');
            const btnStart = document.querySelector('#camera-controls button'); // Start button
            const btnCapture = document.getElementById('btn-capture');
            
            if(errorEl) errorEl.style.display = 'none';

            try {
                cameraStream = await navigator.mediaDevices.getUserMedia({ 
                    video: { facingMode: 'environment' } 
                });
                
                if(video) {
                    video.srcObject = cameraStream;
                    video.style.display = 'block';
                }
                
                if(btnStart) btnStart.style.display = 'none';
                if(btnCapture) btnCapture.style.display = 'block';

            } catch(err) {
                console.error("Camera Error:", err);
                if(errorEl) {
                    errorEl.textContent = "Could not access camera. Please allow permissions.";
                    errorEl.style.display = 'block';
                }
            }
        }

        function stopCamera() {
            if(cameraStream) {
                cameraStream.getTracks().forEach(track => track.stop());
                cameraStream = null;
            }
            
            const video = document.getElementById('camera-stream');
            if(video) video.style.display = 'none';
            
            const btnStart = document.querySelector('#camera-controls button');
            if(btnStart) btnStart.style.display = 'block';
            
            const btnCapture = document.getElementById('btn-capture');
            if(btnCapture) btnCapture.style.display = 'none';
        }

        function capturePhoto() {
            const video = document.getElementById('camera-stream');
            if(!video || !cameraStream) return;

            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            const dataUrl = canvas.toDataURL('image/jpeg');
            setRoomImage(dataUrl);
            stopCamera();
        }

        // Room Upload
        const roomInput = document.getElementById('room-upload-input');
        if(roomInput) {
            // Remove old listener to avoid dupes
            const newRoomInput = roomInput.cloneNode(true);
            roomInput.parentNode.replaceChild(newRoomInput, roomInput);
            
            newRoomInput.addEventListener('change', function(e) {
                if (e.target.files && e.target.files[0]) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        setRoomImage(e.target.result);
                    }
                    reader.readAsDataURL(e.target.files[0]);
                }
            });
        }

        function setRoomImage(src) {
            const roomImg = document.getElementById('room-image-layer');
            if(!roomImg) return;
            
            roomImg.onload = function() {
                const ph = document.getElementById('viz-placeholder');
                if(ph) ph.style.display = 'none';
                roomImg.style.display = 'block';
                vizState.roomLoaded = true;
                addArtToRoom(); // Auto-add art once room is ready
            };
            roomImg.src = src;
        }

        function addArtToRoom() {
            if(!vizState.roomLoaded || !vizState.art) return;
            
            const overlay = document.getElementById('art-overlay-layer');
            if(overlay) {
                overlay.style.display = 'block';
                // Only center if first time or explicit reset needed? 
                // For now, keep it simple.
                // overlay.style.top = '30%';
                // overlay.style.left = '40%';
            }
            updateArtTransform();
        }

        // Unsplash Logic
        async function searchUnsplash() {
            const queryEl = document.getElementById('unsplash-query');
            if(!queryEl) return;
            const query = queryEl.value;
            if(!query) return;
            
            const container = document.getElementById('unsplash-results');
            if(!container) return;
            
            container.innerHTML = '<div style="color:#888; padding:10px;">Searching...</div>';
            
            try {
                const res = await fetch(`https://api.unsplash.com/search/photos?query=${encodeURIComponent(query + ' interior')}&per_page=10&client_id=${UNSPLASH_KEY}`);
                const data = await res.json();
                
                container.innerHTML = '';
                if(!data.results || data.results.length === 0) {
                    container.innerHTML = '<div style="color:#888;">No results found.</div>';
                    return;
                }

                data.results.forEach(photo => {
                    const div = document.createElement('div');
                    div.className = 'viz-photo';
                    div.innerHTML = `<img src="${photo.urls.small}" loading="lazy">`;
                    div.onclick = () => setRoomImage(photo.urls.regular);
                    container.appendChild(div);
                });

            } catch(e) {
                console.error(e);
                container.innerHTML = '<div style="color:var(--text-secondary);">Error loading photos.</div>';
            }
        }

        // Controls Logic
        const scaleRange = document.getElementById('viz-scale');
        const rotRange = document.getElementById('viz-rot');
        
        if(scaleRange) {
             // Avoid dupes
            const newScale = scaleRange.cloneNode(true);
            scaleRange.parentNode.replaceChild(newScale, scaleRange);
            
            newScale.addEventListener('input', (e) => {
                safeSetText('scale-val', e.target.value + '%');
                updateArtTransform();
            });
        }
        
        if(rotRange) {
             // Avoid dupes
            const newRot = rotRange.cloneNode(true);
            rotRange.parentNode.replaceChild(newRot, rotRange);
            
            newRot.addEventListener('input', (e) => {
                safeSetText('rot-val', e.target.value + '°');
                updateArtTransform();
            });
        }

        function updateArtTransform() {
            const overlay = document.getElementById('art-overlay-layer');
            if(!overlay) return;
            
            const scaleRange = document.getElementById('viz-scale');
            const rotRange = document.getElementById('viz-rot');

            const scale = scaleRange ? scaleRange.value / 100 : 0.7;
            const rot = rotRange ? rotRange.value : 0;
            
            if(vizState.art) {
                // Using 300px as arbitrary base width for visualizer
                const h = parseFloat(vizState.art.height) || 10;
                const w = parseFloat(vizState.art.width) || 10;
                const aspect = w / h;
                const baseWidth = 300; 
                
                overlay.style.width = (baseWidth * scale) + 'px';
                overlay.style.height = ((baseWidth / aspect) * scale) + 'px';
                overlay.style.transform = `rotate(${rot}deg)`;
            }
        }

        async function downloadVisualizerPDF() {
            const { jsPDF } = window.jspdf;
            const canvasArea = document.getElementById('viz-canvas');
            
            try {
                // Show loading state
                const btn = document.getElementById('btn-download-pdf');
                const originalText = btn.textContent;
                btn.textContent = "Generating PDF...";
                
                const canvas = await html2canvas(canvasArea, {
                    scale: 2, // Higher quality
                    useCORS: true,
                    backgroundColor: '#1a1a1a' 
                });
                
                const imgData = canvas.toDataURL('image/jpeg', 0.9);
                const pdf = new jsPDF({
                    orientation: 'landscape',
                    unit: 'px',
                    format: [canvas.width, canvas.height]
                });
                
                pdf.addImage(imgData, 'JPEG', 0, 0, canvas.width, canvas.height);
                pdf.save(`ESM_Visualizer_${vizState.art ? vizState.art.title.replace(/[^a-z0-9]/gi, '_') : 'Scene'}.pdf`);
                
                btn.textContent = originalText;
            } catch(e) {
                console.error(e);
                alert("Could not generate PDF. Please try again.");
                document.getElementById('btn-download-pdf').textContent = "Download Scene as PDF";
            }
        }

        async function shareVisualizerScene() {
            const canvasArea = document.getElementById('viz-canvas');
            const btn = document.getElementById('btn-share-scene');
            const originalText = btn.textContent;
            
            // Debounce/Prevent double click
            if(btn.textContent === "Preparing...") return;
            
            btn.textContent = "Preparing...";
            
            try {
                // Capture canvas
                const canvas = await html2canvas(canvasArea, {
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#1a1a1a'
                });

                canvas.toBlob(async (blob) => {
                    if (!blob) {
                        throw new Error("Canvas blob creation failed");
                    }
                    
                    const file = new File([blob], "visualizer_scene.png", { type: "image/png" });
                    
                    // Try Native Share
                    if (navigator.canShare && navigator.canShare({ files: [file] })) {
                        try {
                            await navigator.share({
                                files: [file],
                                title: 'ESM Art Visualizer',
                                text: 'Check out this artwork in my room!'
                            });
                            btn.textContent = originalText;
                        } catch (err) {
                           // User likely cancelled share
                           console.log("Share cancelled or failed", err);
                           btn.textContent = originalText;
                        }
                    } else {
                        // Fallback: Clipboard
                        try {
                            if(typeof ClipboardItem !== "undefined") {
                                const item = new ClipboardItem({ "image/png": blob });
                                await navigator.clipboard.write([item]);
                                alert("Image copied to clipboard!");
                            } else {
                                throw new Error("Clipboard API not supported");
                            }
                            btn.textContent = originalText;
                        } catch (err) {
                            console.error("Clipboard failed", err);
                            // Verify if it's a permissions issue or context issue
                            alert("Could not share natively. You can Download as PDF instead.");
                            btn.textContent = originalText;
                        }
                    }
                }, 'image/png');

            } catch (e) {
                console.error("Share Error:", e);
                alert("Could not generate image for sharing.");
                btn.textContent = originalText;
            }
        }

        // Draggable Logic - Simple 
        const dragItem = document.getElementById('art-overlay-layer');
        if(dragItem) {
            let isDragging = false;
            let startX, startY;
            
             // Avoid dupes - cloneNode kills event listeners but we need to re-add them
            const newDrag = dragItem.cloneNode(true);
            dragItem.parentNode.replaceChild(newDrag, dragItem);
            
            newDrag.addEventListener('mousedown', e => {
                isDragging = true;
                startX = e.clientX - newDrag.offsetLeft;
                startY = e.clientY - newDrag.offsetTop;
                newDrag.style.cursor = 'grabbing';
                e.preventDefault();
            });
            
            document.addEventListener('mouseup', () => {
                isDragging = false;
                if(newDrag) newDrag.style.cursor = 'grab';
            });
            
            document.addEventListener('mousemove', e => {
                if(!isDragging) return;
                e.preventDefault();
                newDrag.style.left = (e.clientX - startX) + 'px';
                newDrag.style.top = (e.clientY - startY) + 'px';
            });
        }

        // Wait for DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
    </script>
</body>
</html>
        <?php
        exit;
    }
}

new ESM_Trade_Portal();
?>
PHP_EOD;

if (file_put_contents($plugin_path, $plugin_code)) {
    echo "<div style='color:green'>✅ Plugin updated successfully at $plugin_path</div>";
    echo "<br><b>Share Button Logic Included.</b>";
} else {
    echo "<div style='color:red'>❌ Failed to update plugin at $plugin_path</div>";
}
?>
