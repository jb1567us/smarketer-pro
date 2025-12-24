<?php
// Deploy Shrooms Fix
// Auto-generated

$portal_code = <<<'PHP_EOD'
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
                    <button class="viz-tab" onclick="switchVizTab('unsplash')">Unsplash</button>
                </div>

                <div id="viz-tab-upload" style="display:block;">
                    <div class="viz-upload-zone" onclick="document.getElementById('room-upload-input').click()">
                        <div style="font-size:2rem; margin-bottom:1rem;">📷</div>
                        <div>Click to Upload Room Photo</div>
                        <input type="file" id="room-upload-input" accept="image/*" style="display:none">
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
                    <button class="btn-premium" style="width:100%;" onclick="closeVisualizer()">Select Different Art</button>
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
                
                const specUrl = `/downloads/spec_sheets/${item.title.replace(/ /g, '%20')}_spec.pdf`;
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
            
            if(vizState.roomLoaded) {
                addArtToRoom();
            }
        }

        function closeVisualizer() {
            const modal = document.getElementById('visualizer-modal');
            if(modal) modal.classList.remove('active');
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

            if(tabName === 'upload') {
                if(uploadTab) uploadTab.style.display = 'block';
                if(unsplashTab) unsplashTab.style.display = 'none';
            } else {
                if(uploadTab) uploadTab.style.display = 'none';
                if(unsplashTab) unsplashTab.style.display = 'block';
            }
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

$json_data = <<<'JSON_EOD'
[
    {
        "id": 1674,
        "title": "Portal",
        "slug": "portal-2",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal/1295487/6483753/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/PortalPainting.jpg",
        "date": "2025-09-25T15:30:02",
        "price": "1090",
        "width": "38.5",
        "height": "27.3",
        "medium": "Oil",
        "year": "2019",
        "cleanTitle": "Portal",
        "styles": "Abstract, Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Oil,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "link": "https://elliotspencermorgan.com/portal-2/",
        "type": "page",
        "dimensions": "38.5 W x 27.3 H x 0.1 D in",
        "depth": "0.1",
        "wordpress_id": 1927,
        "detected_colors": [
            "Red",
            "Brown",
            "Grey"
        ],
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is focusing on value contrast rather than chromatic complexity, anchored by Burgundy and Graphite tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": 1706,
        "title": "Portal 2",
        "slug": "portal_2-2",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-2/1295487/8146546/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Portal_2Painting.jpg",
        "date": "2025-09-25T15:30:02",
        "scrape_failed": true,
        "year": "2020",
        "styles": "Fine Art, Conceptual, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "link": "https://elliotspencermorgan.com/portal_2-2/",
        "type": "page",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1928,
        "detected_colors": [
            "Gold",
            "Brown",
            "Pink",
            "Grey"
        ],
        "price": "460",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is projecting an optimistic, solar luminosity, anchored by Saffron and Moss tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": 1708,
        "title": "self portrait 1",
        "slug": "self_portrait_1",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Self-Portrait-1/1295487/8125469/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/self_portrait_1Painting.jpg",
        "date": "2025-09-25T15:30:02",
        "scrape_failed": true,
        "year": "2020",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "link": "https://elliotspencermorgan.com/self_portrait_1/",
        "type": "page",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1708,
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is smoldering with latent intensity, anchored by Gold and Obsidian tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 1629,
        "title": "Convergence",
        "slug": "convergence",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Convergence/1295487/8754060/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ConvergencePainting.jpg",
        "date": "2025-09-25T15:30:02",
        "scrape_failed": true,
        "year": "2021",
        "styles": "Expressionism, Conceptual, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "link": "https://elliotspencermorgan.com/convergence/",
        "type": "page",
        "dimensions": "33 W x 42 H x 1 D in",
        "width": "33",
        "height": "42",
        "depth": "1",
        "wordpress_id": 1629,
        "detected_colors": [
            "Brown",
            "Grey",
            "Silver"
        ],
        "price": "1125",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is operating within a restrained, monochromatic discipline, anchored by Charcoal and Graphite tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    },
    {
        "id": 1630,
        "title": "Puzzled",
        "slug": "puzzled",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Puzzled/1295487/8146584/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/PuzzledPainting.jpg",
        "date": "2025-09-25T15:30:02",
        "scrape_failed": true,
        "year": "2020",
        "styles": "Luxury, Abstract, Abstract Expressionism, Structured, Fine Art, Geometric, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "link": "https://elliotspencermorgan.com/puzzled/",
        "type": "page",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1630,
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is radiating a saturated, thermal warmth, anchored by Saffron and Espresso tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": 1709,
        "title": "Finger print",
        "slug": "finger_print",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Finger-Print/1295487/8754025/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Finger_printPainting.jpg",
        "date": "2025-09-25T15:30:02",
        "scrape_failed": true,
        "year": "2021",
        "styles": "Expressionism, Conceptual, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Crate",
        "shippingFrom": "Worldwide",
        "link": "https://elliotspencermorgan.com/finger_print/",
        "type": "page",
        "dimensions": "48 W x 96 H x 1 D in",
        "width": "48",
        "height": "96",
        "depth": "1",
        "wordpress_id": 1709,
        "detected_colors": [
            "Grey",
            "Brown",
            "Silver"
        ],
        "price": "4000",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is possessing a crisp, mineral serenity, anchored by Graphite and Taupe tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 1710,
        "title": "Sheet Music",
        "slug": "sheet_music",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Sheet-Music/1295487/8146759/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Sheet_MusicPainting.jpg",
        "date": "2025-09-25T15:30:02",
        "scrape_failed": true,
        "year": "2020",
        "styles": "Abstract, Abstract Expressionism, Pop Art, Fine Art, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "link": "https://elliotspencermorgan.com/sheet_music/",
        "type": "page",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1710,
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is grounded in earthy, resonant octaves, anchored by Gold and Brass tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": 1711,
        "title": "Meeting in the Middle",
        "slug": "meeting_in_the_middle",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Meeting-In-The-Middle/1295487/8754042/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Meeting_in_the_MiddlePainting.jpg",
        "date": "2025-09-25T15:30:02",
        "scrape_failed": true,
        "year": "2021",
        "styles": "Expressionism, Conceptual, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Crate",
        "shippingFrom": "Worldwide",
        "link": "https://elliotspencermorgan.com/meeting_in_the_middle/",
        "type": "page",
        "dimensions": "16 W x 28 H x 1 D in",
        "width": "16",
        "height": "28",
        "depth": "1",
        "wordpress_id": 1711,
        "detected_colors": [
            "Grey",
            "Brown",
            "Black",
            "Silver"
        ],
        "price": "795",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is receding visually to create optical depth, anchored by Charcoal and Taupe tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 1585,
        "title": "Caviar",
        "slug": "caviarpainting",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/CaviarPainting.jpg",
        "date": "2025-09-25T15:30:02",
        "scrape_failed": true,
        "year": "2024",
        "styles": "Black & White, Contemporary, Abstract, Pop Art, Geometric",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "No",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "link": "https://elliotspencermorgan.com/caviarpainting/",
        "type": "page",
        "dimensions": "20 W x 16 H x 0.1 D in",
        "width": "20",
        "height": "16",
        "depth": "0.1",
        "wordpress_id": 1764,
        "detected_colors": [
            "Beige",
            "Grey",
            "Silver",
            "Brown"
        ],
        "price": "565",
        "description": "Curator's Note: Establishing a rigorous architectonic logic, this work is receding visually to create optical depth, anchored by Alabaster and Taupe tones. By introducing a consistent structural rhythm, it serves as an architectural anchor that organizes an open-plan space. This palette harmonizes effortlessly with modern chrome fixtures and glass surfaces, reinforcing a sleek, contemporary aesthetic."
    },
    {
        "id": 107,
        "title": "Heart Work Painting",
        "slug": "heart_workpainting",
        "link": "https://elliotspencermorgan.com/heart_workpainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Heart-Work/1295487/8146572/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Heart_WorkPainting.jpg",
        "type": "page",
        "year": "2020",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1852,
        "detected_colors": [
            "Gold",
            "Brown",
            "Grey"
        ],
        "price": "460",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is projecting an optimistic, solar luminosity, anchored by Saffron and Moss tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 111,
        "title": "Morning Joe Painting",
        "slug": "morning_joepainting",
        "link": "https://elliotspencermorgan.com/morning_joepainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Morning-Joe/1295487/8125458/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Morning_JoePainting.jpg",
        "type": "page",
        "year": "2020",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1854,
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is projecting an optimistic, solar luminosity, anchored by Gold and Obsidian tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": 112,
        "title": "Unity Painting",
        "slug": "unitypainting",
        "link": "https://elliotspencermorgan.com/unitypainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Unity/1295487/8125409/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/UnityPainting.jpg",
        "type": "page",
        "year": "2020",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1855,
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is smoldering with latent intensity, anchored by Gold and Saffron tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 113,
        "title": "Dog on a bike Painting",
        "slug": "dog_on_a_bikepainting",
        "link": "https://elliotspencermorgan.com/dog_on_a_bikepainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Dog-On-A-Bike/1295487/8125271/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Dog_on_a_bikePainting.jpg",
        "type": "page",
        "year": "2020",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1856,
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is grounded in earthy, resonant octaves, anchored by Saffron and Obsidian tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    },
    {
        "id": 114,
        "title": "Water People Painting",
        "slug": "water_peoplepainting",
        "link": "https://elliotspencermorgan.com/water_peoplepainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Water-People/1295487/7363373/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Water_PeoplePainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Fluid, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Crate",
        "shippingFrom": "Worldwide",
        "dimensions": "48 W x 48 H x 0.5 D in",
        "width": "48",
        "height": "48",
        "depth": "0.5",
        "wordpress_id": 1857,
        "detected_colors": [
            "Grey",
            "Brown",
            "Black",
            "Silver"
        ],
        "price": "4910",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is emphasizing the sculptural quality of light and shadow, anchored by Charcoal and Graphite tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    },
    {
        "id": 115,
        "title": "Towers Painting",
        "slug": "towerspainting",
        "link": "https://elliotspencermorgan.com/towerspainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Towers/1295487/7363345/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/TowersPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "40.5 W x 24.5 H x 1 D in",
        "width": "40.5",
        "height": "24.5",
        "depth": "1",
        "wordpress_id": 1858,
        "detected_colors": [
            "Brown",
            "Grey",
            "Beige",
            "Black"
        ],
        "price": "2175",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is receding visually to create optical depth, anchored by Charcoal and Obsidian tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 116,
        "title": "Granular Painting",
        "slug": "granularpainting",
        "link": "https://elliotspencermorgan.com/granularpainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Granular/1295487/7363339/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/GranularPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Structured, Fine Art, Geometric, Modern",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "24 W x 24 H x 0.5 D in",
        "width": "24",
        "height": "24",
        "depth": "0.5",
        "wordpress_id": 1859,
        "detected_colors": [
            "Black",
            "Grey",
            "Silver",
            "Brown"
        ],
        "price": "1320",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is receding visually to create optical depth, anchored by Obsidian and Sage tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. Ideally placed against white or light grey walls, the aquatics and cool hues expand the perceived volume of the room."
    },
    {
        "id": 117,
        "title": "Puzzle 2 Painting",
        "slug": "puzzle_2painting",
        "link": "https://elliotspencermorgan.com/puzzle_2painting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Puzzle-2/1295487/7363331/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/PuzzlePainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Structured, Fine Art, Geometric, Modern",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "26 W x 32 H x 0.5 D in",
        "width": "26",
        "height": "32",
        "depth": "0.5",
        "wordpress_id": 1860,
        "detected_colors": [
            "Grey",
            "Brown",
            "Black",
            "Silver"
        ],
        "price": "1530",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is emphasizing the sculptural quality of light and shadow, anchored by Charcoal and Taupe tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    },
    {
        "id": 118,
        "title": "Puzzle 1 Painting",
        "slug": "puzzle_1painting",
        "link": "https://elliotspencermorgan.com/puzzle_1painting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Puzzle-1/1295487/7363317/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Puzzle_1Painting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Figurative, Abstract, Abstract Expressionism, Structured, Fine Art, Geometric",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "24 W x 32.5 H x 0.5 D in",
        "width": "24",
        "height": "32.5",
        "depth": "0.5",
        "wordpress_id": 1861,
        "detected_colors": [
            "Grey",
            "Black",
            "Brown",
            "Silver"
        ],
        "price": "1845",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is focusing on value contrast rather than chromatic complexity, anchored by Taupe and Obsidian tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    },
    {
        "id": 119,
        "title": "Trichome Painting",
        "slug": "trichomepainting",
        "link": "https://elliotspencermorgan.com/trichomepainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Trichome/1295487/7363313/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/TrichomePainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Pastel,\u00a0Wood,\u00a0Steel",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Crate",
        "shippingFrom": "Worldwide",
        "dimensions": "15.3 W x 48.4 H x 1 D in",
        "width": "15.3",
        "height": "48.4",
        "depth": "1",
        "wordpress_id": 1862,
        "detected_colors": [
            "Grey",
            "Brown",
            "Silver"
        ],
        "price": "1845",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is evoking the clarity of northern light, anchored by Sage and Slate tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 120,
        "title": "Trichomes Painting",
        "slug": "trichomespainting",
        "link": "https://elliotspencermorgan.com/trichomespainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Trichomes/1295487/7363299/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/TrichomePainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Pastel,\u00a0Ink,\u00a0Wood,\u00a0Steel",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Crate",
        "shippingFrom": "Worldwide",
        "dimensions": "15.3 W x 48.3 H x 1 D in",
        "width": "15.3",
        "height": "48.3",
        "depth": "1",
        "wordpress_id": 1863,
        "detected_colors": [
            "Brown",
            "Grey",
            "Black"
        ],
        "price": "1845",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is emphasizing the sculptural quality of light and shadow, anchored by Charcoal and Graphite tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    },
    {
        "id": 121,
        "title": "Grill Painting",
        "slug": "grillpainting",
        "link": "https://elliotspencermorgan.com/grillpainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Grill/1295487/6783253/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/GrillPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1864,
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is radiating a saturated, thermal warmth, anchored by Gold and Espresso tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": 122,
        "title": "Quilted Painting",
        "slug": "quiltedpainting",
        "link": "https://elliotspencermorgan.com/quiltedpainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Quilted/1295487/6783247/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/QuiltedPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1865,
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is projecting an optimistic, solar luminosity, anchored by Gold and Bronze tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": 123,
        "title": "Interactions Painting",
        "slug": "interactionspainting",
        "link": "https://elliotspencermorgan.com/interactionspainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Interactions/1295487/6783239/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/InteractionsPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1866,
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is grounded in earthy, resonant octaves, anchored by Gold and Espresso tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 124,
        "title": "Rush Painting",
        "slug": "rushpainting",
        "link": "https://elliotspencermorgan.com/rushpainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Rush/1295487/6783231/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/RushPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1867,
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is radiating a saturated, thermal warmth, anchored by Gold and Obsidian tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 125,
        "title": "Yorkie Painting",
        "slug": "yorkiepainting",
        "link": "https://elliotspencermorgan.com/yorkiepainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Yorkie/1295487/6783225/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/YorkiePainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1868,
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is emphasizing the sculptural quality of light and shadow, anchored by Gold and Obsidian tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 126,
        "title": "Night Sky Painting",
        "slug": "night_skypainting",
        "link": "https://elliotspencermorgan.com/night_skypainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Night-Sky/1295487/6783211/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Night_SkyPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1869,
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is projecting an optimistic, solar luminosity, anchored by Gold and Brass tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": 127,
        "title": "Bold Painting",
        "slug": "boldpainting-4",
        "link": "https://elliotspencermorgan.com/boldpainting-4/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Bold/1295487/6783203/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/BoldPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 2036,
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is grounded in earthy, resonant octaves, anchored by Gold and Obsidian tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 128,
        "title": "Climbing Painting",
        "slug": "climbingpainting",
        "link": "https://elliotspencermorgan.com/climbingpainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Climbing/1295487/6783197/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ClimbingPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1871,
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "460",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is smoldering with latent intensity, anchored by Gold and Obsidian tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 129,
        "title": "Dance Painting",
        "slug": "dancepainting",
        "link": "https://elliotspencermorgan.com/dancepainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Dance/1295487/6783193/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/DancePainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17 W x 23 H x 0.1 D in",
        "width": "17",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1872,
        "detected_colors": [
            "Gold",
            "Brown",
            "Black",
            "Grey"
        ],
        "price": "460",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is grounded in earthy, resonant octaves, anchored by Saffron and Espresso tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": 130,
        "title": "Smoke Painting",
        "slug": "smokepainting",
        "link": "https://elliotspencermorgan.com/smokepainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Smoke/1295487/6783181/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/SmokePainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Luxury, Abstract, Abstract Expressionism, Fluid, Fine Art, Modern",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1873,
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "460",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is smoldering with latent intensity, anchored by Gold and Obsidian tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 131,
        "title": "Motion Painting",
        "slug": "motionpainting",
        "link": "https://elliotspencermorgan.com/motionpainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Motion/1295487/6783137/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/MotionPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1874,
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is grounded in earthy, resonant octaves, anchored by Gold and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": 132,
        "title": "Listening Painting",
        "slug": "listeningpainting",
        "link": "https://elliotspencermorgan.com/listeningpainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Listening/1295487/6783125/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ListeningPainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1875,
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is radiating a saturated, thermal warmth, anchored by Gold and Brass tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 133,
        "title": "Synapses Painting",
        "slug": "synapsespainting",
        "link": "https://elliotspencermorgan.com/synapsespainting/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Synapses/1295487/6783101/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/SynapsePainting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "wordpress_id": 1876,
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is operating within a restrained, monochromatic discipline, anchored by Gold and Obsidian tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 134,
        "title": "Microscope 7 Painting",
        "slug": "microscope_7painting-4",
        "link": "https://elliotspencermorgan.com/microscope_7painting-4/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-7/1295487/6782897/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Microscope_7Painting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood,\u00a0Steel",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "12 W x 18 H x 1 D in",
        "width": "12",
        "height": "18",
        "depth": "1",
        "wordpress_id": 2043,
        "detected_colors": [
            "Brown",
            "Grey",
            "Black",
            "Silver"
        ],
        "price": "775",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is possessing a crisp, mineral serenity, anchored by Obsidian and Espresso tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 135,
        "title": "Microscope 6 Painting",
        "slug": "microscope_6painting-4",
        "link": "https://elliotspencermorgan.com/microscope_6painting-4/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-6/1295487/6782859/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Microscope_6Painting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood,\u00a0Steel",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "12 W x 18 H x 1 D in",
        "width": "12",
        "height": "18",
        "depth": "1",
        "wordpress_id": 2044,
        "detected_colors": [
            "Brown",
            "Grey",
            "Silver",
            "Black"
        ],
        "price": "775",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is maintaining a cool, atmospheric detachment, anchored by Espresso and Sage tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. This palette harmonizes effortlessly with modern chrome fixtures and glass surfaces, reinforcing a sleek, contemporary aesthetic."
    },
    {
        "id": 136,
        "title": "Microscope 5 Painting",
        "slug": "microscope_5painting-4",
        "link": "https://elliotspencermorgan.com/microscope_5painting-4/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-5/1295487/6782839/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Microscope_5Painting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood,\u00a0Steel",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "12 W x 18 H x 1 D in",
        "width": "12",
        "height": "18",
        "depth": "1",
        "wordpress_id": 2045,
        "detected_colors": [
            "Brown",
            "Black",
            "Silver",
            "Grey"
        ],
        "price": "775",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is emphasizing the sculptural quality of light and shadow, anchored by Obsidian and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": 137,
        "title": "Microscope 4 Painting",
        "slug": "microscope_4painting-4",
        "link": "https://elliotspencermorgan.com/microscope_4painting-4/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-4/1295487/6782817/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Microscope_4Painting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Wood,\u00a0Steel",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "12 W x 18 H x 1 D in",
        "width": "12",
        "height": "18",
        "depth": "1",
        "wordpress_id": 2046,
        "detected_colors": [
            "Brown",
            "Grey",
            "Gold"
        ],
        "price": "775",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is focusing on value contrast rather than chromatic complexity, anchored by Espresso and Graphite tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": 138,
        "title": "Microscope 3 Painting",
        "slug": "microscope_3painting-4",
        "link": "https://elliotspencermorgan.com/microscope_3painting-4/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-3/1295487/6782785/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Microscope_3Painting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood,\u00a0Steel",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "12 W x 18 H x 1 D in",
        "width": "12",
        "height": "18",
        "depth": "1",
        "wordpress_id": 2047,
        "detected_colors": [
            "Brown",
            "Grey",
            "Silver",
            "Black"
        ],
        "price": "775",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is focusing on value contrast rather than chromatic complexity, anchored by Espresso and Graphite tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": 139,
        "title": "Microscope 2 Painting",
        "slug": "microscope_2painting-4",
        "link": "https://elliotspencermorgan.com/microscope_2painting-4/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-2/1295487/6782755/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Microscope_2Painting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Oil,\u00a0Wood,\u00a0Steel",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "12 W x 18 H x 1 D in",
        "width": "12",
        "height": "18",
        "depth": "1",
        "wordpress_id": 2048,
        "detected_colors": [
            "Brown",
            "Black",
            "Grey"
        ],
        "price": "775",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is operating within a restrained, monochromatic discipline, anchored by Obsidian and Espresso tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": 140,
        "title": "Microscope 1 Painting",
        "slug": "microscope_1painting-4",
        "link": "https://elliotspencermorgan.com/microscope_1painting-4/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-1/1295487/6782739/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Microscope_1Painting.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Wood,\u00a0Steel",
        "frame": "Black",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "12 W x 18 H x 1 D in",
        "width": "12",
        "height": "18",
        "depth": "1",
        "wordpress_id": 2049,
        "detected_colors": [
            "Black",
            "Grey",
            "Brown",
            "Silver"
        ],
        "price": "775",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is emphasizing the sculptural quality of light and shadow, anchored by Obsidian and Graphite tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": 141,
        "title": "Floating 6 - Rabbit Sculpture",
        "slug": "floating_6_-_rabbitSculpture",
        "link": "https://elliotspencermorgan.com/2025/09/25/floating_6_-_rabbitSculpture/",
        "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-6-Rabbit/1295487/6627463/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Floating_6_-_RabbitSculpture.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": null,
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "19 W x 26.5 H x 0.5 D in",
        "width": "19",
        "height": "26.5",
        "depth": "0.5",
        "detected_colors": [
            "Beige",
            "Red",
            "Silver",
            "Brown"
        ],
        "price": "900",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is focusing on value contrast rather than chromatic complexity, anchored by Platinum and Rust tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": 142,
        "title": "Floating 5 - Moth Sculpture",
        "slug": "floating_5_-_mothSculpture",
        "link": "https://elliotspencermorgan.com/2025/09/25/floating_5_-_mothSculpture/",
        "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-5-Moth/1295487/6627457/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Floating_5_-_MothSculpture.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": null,
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "26.8 W x 19 H x 0.5 D in",
        "width": "26.8",
        "height": "19",
        "depth": "0.5",
        "detected_colors": [
            "Beige",
            "Red",
            "Silver",
            "Brown"
        ],
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is focusing on value contrast rather than chromatic complexity, anchored by Platinum and Rust tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": 143,
        "title": "Floating 4 - Vines Sculpture",
        "slug": "floating_4_-_vinesSculpture",
        "link": "https://elliotspencermorgan.com/2025/09/25/floating_4_-_vinesSculpture/",
        "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-4-Vines/1295487/6627447/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Floating_4_-_VinesSculpture.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": null,
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "6.5 W x 29 H x 0.5 D in",
        "width": "6.5",
        "height": "29",
        "depth": "0.5",
        "detected_colors": [
            "White",
            "Beige",
            "Brown",
            "Silver"
        ],
        "price": "880",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is operating within a restrained, monochromatic discipline, anchored by Lavender and Rust tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": 144,
        "title": "Floating 3 - Tree Sculpture",
        "slug": "floating_3_-_treeSculpture",
        "link": "https://elliotspencermorgan.com/2025/09/25/floating_3_-_treeSculpture/",
        "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-3-Tree/1295487/6627443/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Floating_3_-_TreeSculpture.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Fluid, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": null,
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "19 W x 23 H x 0.5 D in",
        "width": "19",
        "height": "23",
        "depth": "0.5",
        "detected_colors": [
            "Beige",
            "Brown",
            "Silver",
            "Red"
        ],
        "price": "890",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is evoking the clarity of northern light, anchored by Platinum and Rust tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. This palette harmonizes effortlessly with modern chrome fixtures and glass surfaces, reinforcing a sleek, contemporary aesthetic."
    },
    {
        "id": 145,
        "title": "Floating 2 - Butterfly Sculpture",
        "slug": "floating_2_-_butterflySculpture",
        "link": "https://elliotspencermorgan.com/2025/09/25/floating_2_-_butterflySculpture/",
        "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-2-Butterfly/1295487/6627437/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Floating_2_-_ButterflySculpture.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": null,
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "27.5 W x 18.5 H x 5 D in",
        "width": "27.5",
        "height": "18.5",
        "depth": "5",
        "detected_colors": [
            "Red",
            "White",
            "Silver",
            "Beige"
        ],
        "price": "915",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is projecting an optimistic, solar luminosity, anchored by Ivory and Rust tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. Specifically, the warm palette complements natural wood grains and brass hardware, enhancing the organic character of the room."
    },
    {
        "id": 146,
        "title": "Floating 1 - Cicada Sculpture",
        "slug": "floating_1_-_cicadaSculpture",
        "link": "https://elliotspencermorgan.com/2025/09/25/floating_1_-_cicadaSculpture/",
        "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-1-Cicada/1295487/6627409/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Floating_1_-_CicadaSculpture.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": null,
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "25.5 W x 19 H x 0.5 D in",
        "width": "25.5",
        "height": "19",
        "depth": "0.5",
        "detected_colors": [
            "Beige",
            "Brown",
            "Silver",
            "Grey"
        ],
        "price": "890",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is maintaining a cool, atmospheric detachment, anchored by Platinum and Rust tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Ideally placed against white or light grey walls, the aquatics and cool hues expand the perceived volume of the room."
    },
    {
        "id": 147,
        "title": "Purple Night - Mulch Series Collage",
        "slug": "purple_night_-_mulch_seriesCollage",
        "link": "https://elliotspencermorgan.com/2025/09/25/purple_night_-_mulch_seriesCollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Purple-Night-Mulch-Series/1295487/6583797/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11/Purple_Night_-_Mulch_SeriesCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Acrylic,\u00a0Wood",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "16 W x 16 H x 1 D in",
        "width": "16",
        "height": "16",
        "depth": "1",
        "detected_colors": [
            "Brown",
            "Silver",
            "Grey",
            "Black"
        ],
        "price": "880",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is possessing a crisp, mineral serenity, anchored by Obsidian and Espresso tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 149,
        "title": "Purple 1 - Mulch Series Collage",
        "slug": "purple_1_-_mulch_seriesCollage",
        "link": "https://elliotspencermorgan.com/2025/09/25/purple_1_-_mulch_seriesCollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Purple-1-Mulch-Series/1295487/6583781/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11/Purple_1_-_Mulch_SeriesCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Acrylic,\u00a0Wood",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "16 W x 16 H x 1 D in",
        "width": "16",
        "height": "16",
        "depth": "1",
        "detected_colors": [
            "Brown",
            "Grey",
            "Silver",
            "Pink"
        ],
        "price": "880",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is receding visually to create optical depth, anchored by Espresso and Graphite tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. Ideally placed against white or light grey walls, the aquatics and cool hues expand the perceived volume of the room."
    },
    {
        "id": 151,
        "title": "Society - Mulch Series Collage",
        "slug": "society_-_mulch_seriesCollage",
        "link": "https://elliotspencermorgan.com/2025/09/25/society_-_mulch_seriesCollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Society-Mulch-Series/1295487/6583753/view",
        "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/09/Society_-_Mulch_SeriesCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Acrylic,\u00a0Wood",
        "frame": "Other",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "23.3 W x 12.5 H x 1 D in",
        "width": "23.3",
        "height": "12.5",
        "depth": "1",
        "detected_colors": [
            "Grey",
            "Brown",
            "Silver",
            "Gold"
        ],
        "price": "1110",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is smoldering with latent intensity, anchored by Birch and Graphite tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": 152,
        "title": "Pieces of Red Collage",
        "slug": "pieces_of_redcollage",
        "link": "https://elliotspencermorgan.com/pieces_of_redcollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Pieces-Of-Red/1295487/6583729/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11/Pieces_of_RedCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Acrylic,\u00a0Wood",
        "frame": "Other",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "7.9 W x 28.8 H x 1 D in",
        "width": "7.9",
        "height": "28.8",
        "depth": "1",
        "wordpress_id": 1895,
        "detected_colors": [
            "Brown",
            "Silver",
            "Black",
            "Grey"
        ],
        "price": "1320",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is focusing on value contrast rather than chromatic complexity, anchored by Pearl and Espresso tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": 154,
        "title": "Paper Peace Collage",
        "slug": "paper_peacecollage",
        "link": "https://elliotspencermorgan.com/paper_peacecollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Paper-Peace/1295487/6583693/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11/Paper_PeaceCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Wood,\u00a0Acrylic",
        "frame": "Other",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "9.8 W x 36.5 H x 1 D in",
        "width": "9.8",
        "height": "36.5",
        "depth": "1",
        "wordpress_id": 1897,
        "detected_colors": [
            "Silver",
            "Brown",
            "Grey",
            "Pink"
        ],
        "price": "1110",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is evoking the clarity of northern light, anchored by Silver and Sand tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Ideally placed against white or light grey walls, the aquatics and cool hues expand the perceived volume of the room."
    },
    {
        "id": 155,
        "title": "Honeycomb - Mulch Series Collage",
        "slug": "honeycomb_-_mulch_seriesCollage",
        "link": "https://elliotspencermorgan.com/2025/09/25/honeycomb_-_mulch_seriesCollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Honeycomb-Mulch-Series/1295487/6583683/view",
        "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/09/Honeycomb_-_Mulch_SeriesCollage.jpg",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Wood,\u00a0Acrylic",
        "frame": "Other",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "12.8 W x 23 H x 1 D in",
        "width": "12.8",
        "height": "23",
        "depth": "1",
        "detected_colors": [
            "Grey",
            "Brown",
            "Silver",
            "Pink"
        ],
        "price": "1110",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is possessing a crisp, mineral serenity, anchored by Sand and Graphite tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 156,
        "title": "Wild Zebra 2 - Mulch Series Collage",
        "slug": "wild_zebra_2_-_mulch_seriesCollage",
        "link": "https://elliotspencermorgan.com/2025/09/25/wild_zebra_2_-_mulch_seriesCollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Wild-Zebra-2-Mulch-Series/1295487/6583651/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11/Wild_Zebra_2_-_Mulch_SeriesCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Wood,\u00a0Acrylic",
        "frame": "Other",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "6.5 W x 26.5 H x 1 D in",
        "width": "6.5",
        "height": "26.5",
        "depth": "1",
        "detected_colors": [
            "Brown",
            "Grey",
            "Silver",
            "Black"
        ],
        "price": "890",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is evoking the clarity of northern light, anchored by Silver and Graphite tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 157,
        "title": "Wild Zebra 1 - Mulch Series Collage",
        "slug": "wild_zebra_1_-_mulch_seriesCollage",
        "link": "https://elliotspencermorgan.com/2025/09/25/wild_zebra_1_-_mulch_seriesCollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Wild-Zebra-1-Mulch-Series/1295487/6583633/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11/Wild_Zebra_1_-_Mulch_SeriesCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Wood,\u00a0Acrylic",
        "frame": "Other",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "6 W x 26.5 H x 1 D in",
        "width": "6",
        "height": "26.5",
        "depth": "1",
        "detected_colors": [
            "Brown",
            "Grey",
            "Silver",
            "Pink"
        ],
        "price": "1310",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is emphasizing the sculptural quality of light and shadow, anchored by Graphite and Platinum tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": 158,
        "title": "Work Party - Mulch Series Collage",
        "slug": "work_party_-_mulch_seriesCollage",
        "link": "https://elliotspencermorgan.com/2025/09/25/work_party_-_mulch_seriesCollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Work-Party-Mulch-Series/1295487/6583609/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11/Work_Party_-_Mulch_SeriesCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Wood,\u00a0Acrylic",
        "frame": "Other",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "10.8 W x 12 H x 1 D in",
        "width": "10.8",
        "height": "12",
        "depth": "1",
        "detected_colors": [
            "Black",
            "Silver",
            "Grey",
            "Brown"
        ],
        "price": "880",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is possessing a crisp, mineral serenity, anchored by Sand and Ebony tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. This palette harmonizes effortlessly with modern chrome fixtures and glass surfaces, reinforcing a sleek, contemporary aesthetic."
    },
    {
        "id": 159,
        "title": "Business Mulch Collage",
        "slug": "business_mulchcollage",
        "link": "https://elliotspencermorgan.com/business_mulchcollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Business-Mulch/1295487/6583595/view",
        "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/09/Business_MulchCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Abstract, Expressionism, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Paper,\u00a0Wood,\u00a0Acrylic",
        "frame": "Other",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "10.3 W x 8 H x 1 D in",
        "width": "10.3",
        "height": "8",
        "depth": "1",
        "wordpress_id": 1902,
        "detected_colors": [
            "Silver",
            "Brown",
            "Grey",
            "Black"
        ],
        "price": "880",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is evoking the clarity of northern light, anchored by Sand and Sage tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Ideally placed against white or light grey walls, the aquatics and cool hues expand the perceived volume of the room."
    },
    {
        "id": 160,
        "title": "Office Work Mulch Collage",
        "slug": "office_work_mulchcollage",
        "link": "https://elliotspencermorgan.com/office_work_mulchcollage/",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Office-Work-Mulch/1295487/6583581/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11/Office_Work_MulchCollage.jpg",
        "type": "page",
        "year": "2018",
        "styles": "Modern, Abstract, Abstract Expressionism, Pop Art",
        "mediumsDetailed": "Paper,\u00a0Wood,\u00a0Acrylic",
        "frame": "Brown",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "dimensions": "10.3 W x 12 H x 1 D in",
        "width": "10.3",
        "height": "12",
        "depth": "1",
        "wordpress_id": 1903,
        "detected_colors": [
            "Silver",
            "Brown",
            "Grey",
            "Black"
        ],
        "price": "880",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is possessing a crisp, mineral serenity, anchored by Silver and Obsidian tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 240,
        "title": "Blue Glacier Painting",
        "slug": "blue-glacier",
        "link": "https://elliotspencermorgan.com/blue-glacier/",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Blue-Glacier/1295487/6105345/view",
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Blue_GlacierPainting.jpg",
        "type": "page",
        "wordpress_id": 1605,
        "detected_colors": [
            "Grey",
            "Brown",
            "Black"
        ],
        "description": "Curator's Note: Negotiating the tension between rigid geometry and organic gesture, this work is emphasizing the sculptural quality of light and shadow, anchored by Obsidian and Graphite tones. The work's commanding presence draws the eye, establishing a clear hierarchy within the interior layout. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": "new_0",
        "title": "Meeting in the Middle",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Meeting-in-the-Middle/1295487/8754042/view",
        "type": "page",
        "year": "2021",
        "styles": "Expressionism, Conceptual, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "dimensions": "16 W x 28 H x 1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Crate",
        "shippingFrom": "Worldwide",
        "width": "16",
        "height": "28",
        "depth": "1",
        "link": "https://elliotspencermorgan.com/meeting_in_the_middle/",
        "slug": "meeting_in_the_middle",
        "wordpress_id": 1711,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Meeting_in_the_MiddlePainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Black",
            "Silver"
        ],
        "price": "795",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is receding visually to create optical depth, anchored by Charcoal and Taupe tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": "new_1",
        "title": "Finger print",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Finger-print/1295487/8754025/view",
        "type": "page",
        "year": "2021",
        "styles": "Expressionism, Conceptual, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Wood",
        "dimensions": "48 W x 96 H x 1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Crate",
        "shippingFrom": "Worldwide",
        "width": "48",
        "height": "96",
        "depth": "1",
        "link": "https://elliotspencermorgan.com/finger_print/",
        "slug": "finger_print",
        "wordpress_id": 1709,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Finger_printPainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Silver"
        ],
        "price": "4000",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is possessing a crisp, mineral serenity, anchored by Graphite and Taupe tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": "new_2",
        "title": "self portrait 1",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-self-portrait-1/1295487/8125469/view",
        "type": "page",
        "year": "2020",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/self_portrait_1/",
        "slug": "self_portrait_1",
        "wordpress_id": 1708,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/self_portrait_1Painting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is smoldering with latent intensity, anchored by Gold and Obsidian tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_3",
        "title": "Dog on a bike",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Dog-on-a-bike/1295487/8125271/view",
        "type": "page",
        "year": "2020",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/dog_on_a_bikepainting/",
        "slug": "dog_on_a_bikepainting",
        "wordpress_id": 1856,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Dog_on_a_bikePainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "460",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is grounded in earthy, resonant octaves, anchored by Saffron and Obsidian tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    },
    {
        "id": "new_4",
        "title": "City at Night Mulch Series",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-City-at-Night-Mulch-Series/1295487/6583787/view",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Acrylic,\u00a0Wood",
        "dimensions": "16 W x 16 H x 1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "16",
        "height": "16",
        "depth": "1",
        "link": "https://elliotspencermorgan.com/city-at-night-mulch-series/",
        "slug": "city-at-night-mulch-series",
        "wordpress_id": 2077,
        "image_url": "https://images.saatchiart.com/saatchi/1295487/art/6583787/5653457-HSC00001-7.jpg",
        "detected_colors": [
            "Silver",
            "Black",
            "Brown",
            "Grey"
        ],
        "price": "880",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is maintaining a cool, atmospheric detachment, anchored by Obsidian and Espresso tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": "new_5",
        "title": "Close up Mulch Series",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Close-up-Mulch-Series/1295487/6583777/view",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Wood,\u00a0Acrylic",
        "dimensions": "12 W x 12 H x 1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "12",
        "height": "12",
        "depth": "1",
        "link": "https://elliotspencermorgan.com/close-up-mulch-series/",
        "slug": "close-up-mulch-series",
        "wordpress_id": 2078,
        "image_url": "https://images.saatchiart.com/saatchi/1295487/art/6583777/5653447-HSC00001-7.jpg",
        "detected_colors": [
            "Brown",
            "Grey",
            "Silver",
            "White"
        ],
        "price": "880",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is focusing on value contrast rather than chromatic complexity, anchored by Graphite and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": "new_7",
        "title": "Red and Black Mulch Series",
        "saatchi_url": "https://www.saatchiart.com/art/Collage-Red-and-Black-Mulch-Series/1295487/6583709/view",
        "type": "page",
        "year": "2018",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Paper,\u00a0Acrylic,\u00a0Wood",
        "dimensions": "7.8 W x 22.8 H x 1 D in",
        "frame": "Other",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "7.8",
        "height": "22.8",
        "depth": "1",
        "link": "https://elliotspencermorgan.com/red-and-black-mulch-series/",
        "slug": "red-and-black-mulch-series",
        "wordpress_id": 2080,
        "image_url": "https://images.saatchiart.com/saatchi/1295487/art/6583709/5653379-HSC00001-7.jpg",
        "detected_colors": [
            "Brown",
            "Grey",
            "Black",
            "Silver"
        ],
        "price": "1320",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is operating within a restrained, monochromatic discipline, anchored by Obsidian and Sand tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    },
    {
        "id": "new_8",
        "title": "Jaguar",
        "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Jaguar/1295487/6513325/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": null,
        "dimensions": "20 W x 30 H x 2 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "20",
        "height": "30",
        "depth": "2",
        "link": "https://elliotspencermorgan.com/jaguar/",
        "slug": "jaguar",
        "wordpress_id": 2081,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/JaguarSculpture.jpg",
        "detected_colors": [
            "Beige",
            "Brown",
            "Black",
            "Pink"
        ],
        "price": "900",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is receding visually to create optical depth, anchored by Charcoal and Birch tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": "new_9",
        "title": "Megapixels",
        "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Megapixels/1295487/6513307/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": null,
        "dimensions": "18 W x 30 H x 2 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "18",
        "height": "30",
        "depth": "2",
        "link": "https://elliotspencermorgan.com/megapixels/",
        "slug": "megapixels",
        "wordpress_id": 2082,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/MegapixelsSculpture-672x1024.jpg",
        "detected_colors": [
            "Silver",
            "Black",
            "Beige",
            "Brown"
        ],
        "price": "900",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is maintaining a cool, atmospheric detachment, anchored by Sand and Ebony tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": "new_10",
        "title": "ESM S17",
        "saatchi_url": "https://www.saatchiart.com/art/Sculpture-ESM-S17/1295487/6513257/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": null,
        "dimensions": "21 W x 29.5 H x 2 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "21",
        "height": "29.5",
        "depth": "2",
        "link": "https://elliotspencermorgan.com/esm-s17/",
        "slug": "esm-s17",
        "wordpress_id": 2083,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ESM_S17Sculpture.jpg",
        "detected_colors": [
            "Black",
            "Beige",
            "Pink",
            "Silver"
        ],
        "price": "900",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is emphasizing the sculptural quality of light and shadow, anchored by Ebony and Birch tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": "new_11",
        "title": "Fire Flow",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Fire-Flow/1295487/6513221/view",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Fluid, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Acrylic,\u00a0Paper",
        "dimensions": "17.3 W x 23.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.3",
        "height": "23.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/fire-flow/",
        "slug": "fire-flow",
        "wordpress_id": 2084,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Fire_FlowPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Grey"
        ],
        "price": "565",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is smoldering with latent intensity, anchored by Saffron and Gold tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_12",
        "title": "Owls in Fall",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Owls-in-Fall/1295487/6513209/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Ink,\u00a0Acrylic,\u00a0Paper",
        "dimensions": "17.5 W x 25.3 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "25.3",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/owls-in-fall/",
        "slug": "owls-in-fall",
        "wordpress_id": 2085,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Owls_in_FallPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Silver",
            "Grey"
        ],
        "price": "565",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is smoldering with latent intensity, anchored by Saffron and Graphite tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_13",
        "title": "Connectivity",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Connectivity/1295487/6513163/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 25.3 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "25.3",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/connectivity/",
        "slug": "connectivity",
        "wordpress_id": 2086,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ConnectivityPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "565",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is grounded in earthy, resonant octaves, anchored by Saffron and Gold tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_14",
        "title": "Atomic Flow",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Atomic-Flow/1295487/6513149/view",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Fluid, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 25.3 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "25.3",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/atomic-flow/",
        "slug": "atomic-flow",
        "wordpress_id": 2087,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Atomic_FlowPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "565",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is grounded in earthy, resonant octaves, anchored by Saffron and Gold tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_15",
        "title": "Trees",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Trees/1295487/6513127/view",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Fluid, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 25.3 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "25.3",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/trees/",
        "slug": "trees",
        "wordpress_id": 2088,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/TreesPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Grey"
        ],
        "price": "565",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is smoldering with latent intensity, anchored by Saffron and Gold tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_16",
        "title": "Animal Kingdom",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Animal-Kingdom/1295487/6513109/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "25.3 W x 17.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "25.3",
        "height": "17.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/animal-kingdom/",
        "slug": "animal-kingdom",
        "wordpress_id": 2089,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Animal_KingdomPainting.jpg",
        "detected_colors": [
            "Brown",
            "Gold",
            "Silver",
            "Grey"
        ],
        "price": "565",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is radiating a saturated, thermal warmth, anchored by Graphite and Saffron tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": "new_17",
        "title": "Clean Hands",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Clean-Hands/1295487/6513085/view",
        "type": "page",
        "year": "2019",
        "styles": "Conceptual, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "25.3 W x 17.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "25.3",
        "height": "17.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/clean-hands/",
        "slug": "clean-hands",
        "wordpress_id": 2090,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Clean_HandsPainting.jpg",
        "detected_colors": [
            "Gold",
            "Grey",
            "Brown"
        ],
        "price": "565",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is smoldering with latent intensity, anchored by Brass and Gold tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_18",
        "title": "Reflection",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Reflection/1295487/6513075/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "25.3 W x 17.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "25.3",
        "height": "17.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/reflection/",
        "slug": "reflection",
        "wordpress_id": 2091,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ReflectionPainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Gold",
            "Silver"
        ],
        "price": "565",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is emphasizing the sculptural quality of light and shadow, anchored by Graphite and Taupe tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_19",
        "title": "Eggs and Eyes",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Eggs-and-Eyes/1295487/6492629/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/eggs-and-eyes/",
        "slug": "eggs-and-eyes",
        "wordpress_id": 2092,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Eggs_and_EyesPainting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown",
            "Silver"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is projecting an optimistic, solar luminosity, anchored by Gold and Obsidian tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_20",
        "title": "Moon Dance",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Moon-Dance/1295487/6492627/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Airbrush,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/moon-dance/",
        "slug": "moon-dance",
        "wordpress_id": 2093,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Moon_DancePainting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is radiating a saturated, thermal warmth, anchored by Saffron and Obsidian tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Specifically, the warm palette complements natural wood grains and brass hardware, enhancing the organic character of the room."
    },
    {
        "id": "new_21",
        "title": "Floating Leaves",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Floating-Leaves/1295487/6492617/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/floating-leaves/",
        "slug": "floating-leaves",
        "wordpress_id": 2094,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Floating_LeavesPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is projecting an optimistic, solar luminosity, anchored by Saffron and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    },
    {
        "id": "new_22",
        "title": "Arrowheads",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Arrowheads/1295487/6492613/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/arrowheads/",
        "slug": "arrowheads",
        "wordpress_id": 2095,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ArrowheadsPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is radiating a saturated, thermal warmth, anchored by Saffron and Gold tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_23",
        "title": "campground",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-campground/1295487/6492597/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/campground/",
        "slug": "campground",
        "wordpress_id": 2096,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/campgroundPainting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is projecting an optimistic, solar luminosity, anchored by Saffron and Obsidian tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_25",
        "title": "Streams and Ponds",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Streams-and-Ponds/1295487/6492583/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/streams-and-ponds/",
        "slug": "streams-and-ponds",
        "wordpress_id": 2098,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Streams_and_PondsPainting.jpg",
        "detected_colors": [
            "Brown",
            "Gold",
            "Black",
            "Grey"
        ],
        "price": "355",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is grounded in earthy, resonant octaves, anchored by Saffron and Espresso tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": "new_26",
        "title": "Cluster of Caps",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Cluster-of-Caps/1295487/6492577/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/cluster-of-caps/",
        "slug": "cluster-of-caps",
        "wordpress_id": 2099,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Cluster_of_CapsPainting.jpg",
        "detected_colors": [
            "Brown",
            "Gold",
            "Grey"
        ],
        "price": "355",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is focusing on value contrast rather than chromatic complexity, anchored by Saffron and Espresso tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": "new_27",
        "title": "Duck pond",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Duck-pond/1295487/6492573/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/duck-pond/",
        "slug": "duck-pond",
        "wordpress_id": 2100,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Duck_pondPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is smoldering with latent intensity, anchored by Saffron and Espresso tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": "new_28",
        "title": "Creek Bottom",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Creek-Bottom/1295487/6492497/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Pop Art, Fine Art, Luxury, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/creek-bottom/",
        "slug": "creek-bottom",
        "wordpress_id": 2101,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Creek_BottomPainting.jpg",
        "detected_colors": [
            "Brown",
            "Gold",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is projecting an optimistic, solar luminosity, anchored by Saffron and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_29",
        "title": "Organic Mushrooms",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Organic-Mushrooms/1295487/6492491/view",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Luxury, Abstract, Abstract Expressionism, Fluid, Fine Art, Modern",
        "mediumsDetailed": "Airbrush,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/organic-mushrooms/",
        "slug": "organic-mushrooms",
        "wordpress_id": 2102,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Organic_MushroomsPainting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is radiating a saturated, thermal warmth, anchored by Saffron and Obsidian tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_30",
        "title": "Stones",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Stones/1295487/6492487/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/stones/",
        "slug": "stones",
        "wordpress_id": 2103,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/StonesPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is projecting an optimistic, solar luminosity, anchored by Saffron and Obsidian tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    },
    {
        "id": "new_31",
        "title": "Cubes",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Cubes/1295487/6492481/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Structured, Fine Art, Geometric, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/cubes/",
        "slug": "cubes",
        "wordpress_id": 2104,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/CubesPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Grey"
        ],
        "price": "355",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is smoldering with latent intensity, anchored by Saffron and Graphite tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Specifically, the warm palette complements natural wood grains and brass hardware, enhancing the organic character of the room."
    },
    {
        "id": "new_32",
        "title": "Seed pods",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Seed-pods/1295487/6492463/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/seed-pods/",
        "slug": "seed-pods",
        "wordpress_id": 2105,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Seed_podsPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is grounded in earthy, resonant octaves, anchored by Saffron and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_33",
        "title": "Excited Bird",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Excited-Bird/1295487/6492447/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/excited-bird/",
        "slug": "excited-bird",
        "wordpress_id": 2106,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Excited_BirdPainting-600x800.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is grounded in earthy, resonant octaves, anchored by Saffron and Obsidian tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_34",
        "title": "Mushroom Exclamation",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Mushroom-Exclamation/1295487/6492441/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/mushroom-exclamation/",
        "slug": "mushroom-exclamation",
        "wordpress_id": 2107,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Mushroom_ExclamationPainting-600x800.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is smoldering with latent intensity, anchored by Saffron and Gold tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_35",
        "title": "Snake and Rocks",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Snake-and-Rocks/1295487/6492431/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/snake-and-rocks/",
        "slug": "snake-and-rocks",
        "wordpress_id": 2108,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Snake_and_RocksPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is grounded in earthy, resonant octaves, anchored by Saffron and Obsidian tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": "new_36",
        "title": "Shapeshifter",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Shapeshifter/1295487/6492415/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/shapeshifter/",
        "slug": "shapeshifter",
        "wordpress_id": 2109,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ShapeshifterPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is radiating a saturated, thermal warmth, anchored by Saffron and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_37",
        "title": "Coiled Snake",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Coiled-Snake/1295487/6492413/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/coiled-snake/",
        "slug": "coiled-snake",
        "wordpress_id": 2110,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Coiled_SnakePainting.jpg",
        "detected_colors": [
            "Brown",
            "Gold",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is smoldering with latent intensity, anchored by Saffron and Obsidian tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Specifically, the warm palette complements natural wood grains and brass hardware, enhancing the organic character of the room."
    },
    {
        "id": "new_38",
        "title": "Avacado Snack",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Avacado-Snack/1295487/6492407/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Conceptual",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/avacado-snack/",
        "slug": "avacado-snack",
        "wordpress_id": 2111,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Avacado_SnackPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black",
            "Grey"
        ],
        "price": "355",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is grounded in earthy, resonant octaves, anchored by Saffron and Obsidian tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_39",
        "title": "Gold Shapes",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Shapes/1295487/6492375/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.3 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.3",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/gold-shapes/",
        "slug": "gold-shapes",
        "wordpress_id": 2112,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Gold_ShapesPainting.jpg",
        "detected_colors": [
            "Brown",
            "Gold",
            "Black",
            "Grey"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is grounded in earthy, resonant octaves, anchored by Saffron and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Specifically, the warm palette complements natural wood grains and brass hardware, enhancing the organic character of the room."
    },
    {
        "id": "new_40",
        "title": "Musical Embrace",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Musical-Embrace/1295487/6492355/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Conceptual",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.3 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.3",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/musical-embrace/",
        "slug": "musical-embrace",
        "wordpress_id": 2113,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Musical_EmbracePainting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is grounded in earthy, resonant octaves, anchored by Saffron and Espresso tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_41",
        "title": "Organic food",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Organic-food/1295487/6492337/view",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Luxury, Abstract, Abstract Expressionism, Fluid, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.3 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.3",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/organic-food/",
        "slug": "organic-food",
        "wordpress_id": 2114,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Organic_foodPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is radiating a saturated, thermal warmth, anchored by Saffron and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_42",
        "title": "Snake Eggs",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Snake-Eggs/1295487/6492325/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/snake-eggs/",
        "slug": "snake-eggs",
        "wordpress_id": 2115,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Snake_EggsPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is grounded in earthy, resonant octaves, anchored by Saffron and Obsidian tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_43",
        "title": "Brush Strokes",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Brush-Strokes/1295487/6492323/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.3 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.3",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/brush-strokes/",
        "slug": "brush-strokes",
        "wordpress_id": 2116,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Brush_StrokesPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is smoldering with latent intensity, anchored by Saffron and Espresso tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_44",
        "title": "Blanket",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Blanket/1295487/6492319/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.3 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.3",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/blanket/",
        "slug": "blanket",
        "wordpress_id": 2117,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/BlanketPainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Grey",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is grounded in earthy, resonant octaves, anchored by Moss and Obsidian tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_45",
        "title": "Dance",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Dance/1295487/6492311/view",
        "type": "page",
        "year": "2019",
        "styles": "Luxury, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.3 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.3",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/dancepainting/",
        "slug": "dancepainting",
        "wordpress_id": 1872,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/DancePainting.jpg",
        "detected_colors": [
            "Gold",
            "Brown",
            "Black"
        ],
        "price": "355",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is grounded in earthy, resonant octaves, anchored by Saffron and Espresso tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_46",
        "title": "Bloom",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Bloom/1295487/6492303/view",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Luxury, Abstract, Abstract Expressionism, Fluid, Fine Art, Modern",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "23 W x 17.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "23",
        "height": "17.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/bloom/",
        "slug": "bloom",
        "wordpress_id": 1608,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/BloomPainting.jpg",
        "detected_colors": [
            "Brown",
            "Gold"
        ],
        "price": "355",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is grounded in earthy, resonant octaves, anchored by Saffron and Graphite tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_47",
        "title": "Organic Shapes",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Organic-Shapes/1295487/6492289/view",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Fluid, Abstract, Abstract Expressionism, Luxury, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/organic-shapes/",
        "slug": "organic-shapes",
        "wordpress_id": 2120,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Organic_ShapesPainting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is focusing on value contrast rather than chromatic complexity, anchored by Gold and Obsidian tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_48",
        "title": "Silver",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Silver/1295487/6483881/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Conceptual, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.5 W x 27.3 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.5",
        "height": "27.3",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/silver/",
        "slug": "silver",
        "wordpress_id": 2121,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/SilverPainting.jpg",
        "detected_colors": [
            "Red",
            "Grey",
            "Silver",
            "Brown"
        ],
        "price": "1090",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is focusing on value contrast rather than chromatic complexity, anchored by Burgundy and Taupe tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    },
    {
        "id": "new_49",
        "title": "Fortune",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Fortune/1295487/6483865/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.5 W x 27.3 H x 1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.5",
        "height": "27.3",
        "depth": "1",
        "link": "https://elliotspencermorgan.com/fortune/",
        "slug": "fortune",
        "wordpress_id": 2122,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/FortunePainting.jpg",
        "detected_colors": [
            "Red",
            "Silver",
            "Grey",
            "Beige"
        ],
        "price": "1090",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is emphasizing the sculptural quality of light and shadow, anchored by Rust and Burgundy tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": "new_50",
        "title": "Transformation",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Transformation/1295487/6483815/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.5 W x 27.3 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.5",
        "height": "27.3",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/transformation/",
        "slug": "transformation",
        "wordpress_id": 1607,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/TransformationPainting.jpg",
        "detected_colors": [
            "Red",
            "Beige",
            "Silver",
            "White"
        ],
        "price": "1090",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is radiating a saturated, thermal warmth, anchored by Crimson and Pearl tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Specifically, the warm palette complements natural wood grains and brass hardware, enhancing the organic character of the room."
    },
    {
        "id": "new_51",
        "title": "Golden Nugget",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Golden-Nugget/1295487/6483777/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.5 W x 27.3 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.5",
        "height": "27.3",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/golden-nugget/",
        "slug": "golden-nugget",
        "wordpress_id": 2124,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Golden_NuggetPainting.jpg",
        "detected_colors": [
            "Gold",
            "Red"
        ],
        "price": "1090",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is smoldering with latent intensity, anchored by Brass and Burgundy tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_52",
        "title": "Golden Rule",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Golden-Rule/1295487/6483759/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.5 W x 27.3 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.5",
        "height": "27.3",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/golden-rule/",
        "slug": "golden-rule",
        "wordpress_id": 1606,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Golden_RulePainting.jpg",
        "detected_colors": [
            "Red",
            "Gold",
            "Pink"
        ],
        "price": "1090",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is projecting an optimistic, solar luminosity, anchored by Crimson and Sand tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_53",
        "title": "Feather trees",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Feather-trees/1295487/6447005/view",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Fluid, Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.5 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.5",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/feather-trees/",
        "slug": "feather-trees",
        "wordpress_id": 2126,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Feather_treesPainting.jpg",
        "detected_colors": [
            "Red",
            "Brown",
            "Grey"
        ],
        "price": "1090",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is projecting an optimistic, solar luminosity, anchored by Burgundy and Graphite tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    },
    {
        "id": "new_54",
        "title": "Magic Carpet",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Magic-Carpet/1295487/6446995/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.8 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/magic-carpet/",
        "slug": "magic-carpet",
        "wordpress_id": 2127,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Magic_CarpetPainting.jpg",
        "detected_colors": [
            "Brown",
            "Red",
            "Grey"
        ],
        "price": "1090",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is radiating a saturated, thermal warmth, anchored by Graphite and Burgundy tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": "new_55",
        "title": "Screen",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Screen/1295487/6446983/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.3 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.3",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/screen/",
        "slug": "screen",
        "wordpress_id": 2128,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ScreenPainting.jpg",
        "detected_colors": [
            "Brown",
            "Red",
            "Grey"
        ],
        "price": "1090",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is emphasizing the sculptural quality of light and shadow, anchored by Rust and Espresso tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": "new_56",
        "title": "Spring Blooms",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Spring-Blooms/1295487/6446977/view",
        "type": "page",
        "year": "2019",
        "styles": "Organic, Fluid, Abstract, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.5 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.5",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/spring-blooms/",
        "slug": "spring-blooms",
        "wordpress_id": 2129,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Spring_BloomsPainting.jpg",
        "detected_colors": [
            "Grey",
            "Silver",
            "Red"
        ],
        "price": "1090",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is evoking the clarity of northern light, anchored by Sage and Taupe tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. This palette harmonizes effortlessly with modern chrome fixtures and glass surfaces, reinforcing a sleek, contemporary aesthetic."
    },
    {
        "id": "new_57",
        "title": "Celebrate",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Celebrate/1295487/6446967/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.3 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.3",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/celebrate/",
        "slug": "celebrate",
        "wordpress_id": 2130,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/CelebratePainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Red"
        ],
        "price": "1090",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is radiating a saturated, thermal warmth, anchored by Rust and Graphite tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": "new_58",
        "title": "Anemones",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Anemones/1295487/6446959/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.3 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.3",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/anemones/",
        "slug": "anemones",
        "wordpress_id": 2131,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/AnemonesPainting.jpg",
        "detected_colors": [
            "Grey",
            "Red",
            "Brown",
            "Silver"
        ],
        "price": "1090",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is focusing on value contrast rather than chromatic complexity, anchored by Rust and Sage tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    },
    {
        "id": "new_59",
        "title": "Coral",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Coral/1295487/6446941/view",
        "type": "page",
        "year": "2019",
        "styles": "Fine Art, Modern, Abstract, Abstract Expressionism",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.3 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.3",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/coral/",
        "slug": "coral",
        "wordpress_id": 2132,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/CoralPainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Red",
            "Silver"
        ],
        "price": "1090",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is radiating a saturated, thermal warmth, anchored by Taupe and Rust tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    },
    {
        "id": "new_60",
        "title": "Existance",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Existance/1295487/6446929/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Abstract Expressionism, Fine Art, Modern, Minimalist",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.3 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.3",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/existance/",
        "slug": "existance",
        "wordpress_id": 2133,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/ExistancePainting-768x539.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Red"
        ],
        "price": "1090",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is focusing on value contrast rather than chromatic complexity, anchored by Taupe and Rust tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": "new_61",
        "title": "Fireworks",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Fireworks/1295487/6446913/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract, Expressionism, Abstract Expressionism, Fine Art, Modern",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.3 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.3",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/fireworks/",
        "slug": "fireworks",
        "wordpress_id": 2134,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/FireworksPainting.jpg",
        "detected_colors": [
            "Grey",
            "Silver",
            "Red",
            "Brown"
        ],
        "price": "1090",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is receding visually to create optical depth, anchored by Rust and Sage tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. This palette harmonizes effortlessly with modern chrome fixtures and glass surfaces, reinforcing a sleek, contemporary aesthetic."
    },
    {
        "id": "new_62",
        "title": "Synapse",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Synapse/1295487/6446909/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "38.3 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.3",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/synapse/",
        "slug": "synapse",
        "wordpress_id": 2135,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/SynapsePainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Red",
            "Silver"
        ],
        "price": "1090",
        "description": "Curator's Note: Relying on asymmetrical balance to drive visual movement, this work is radiating a saturated, thermal warmth, anchored by Rust and Taupe tones. By harmonizing complex tones, it creates a sophisticated backdrop that unifies the room's color story. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": "new_63",
        "title": "Stick men",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Stick-men/1295487/6446901/view",
        "type": "page",
        "year": "2019",
        "styles": "Minimalist, Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Ink,\u00a0Paper",
        "dimensions": "39.3 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "39.3",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/stick-men/",
        "slug": "stick-men",
        "wordpress_id": 2136,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Stick_menPainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Red"
        ],
        "price": "1090",
        "description": "Curator's Note: Utilizing expansive negative space to frame its central motif, this work is grounded in earthy, resonant octaves, anchored by Taupe and Graphite tones. By harmonizing complex tones, it creates a sophisticated backdrop that unifies the room's color story. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": "new_64",
        "title": "Descending",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Descending/1295487/6446893/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "39.3 W x 27.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "39.3",
        "height": "27.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/descending/",
        "slug": "descending",
        "wordpress_id": 2137,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/DescendingPainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Red",
            "Black"
        ],
        "price": "1090",
        "description": "Curator's Note: Distilling form into essential rhythmic iterations, this work is smoldering with latent intensity, anchored by Espresso and Graphite tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light."
    },
    {
        "id": "new_65",
        "title": "lifeforce",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-lifeforce/1295487/6446799/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.8 W x 25.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "25.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/lifeforce/",
        "slug": "lifeforce",
        "wordpress_id": 2138,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/lifeforcePainting.jpg",
        "detected_colors": [
            "Silver",
            "Red",
            "Grey",
            "Brown"
        ],
        "price": "1090",
        "description": "Curator's Note: Relying on asymmetrical balance to drive visual movement, this work is evoking the clarity of northern light, anchored by Silver and Crimson tones. The work's commanding presence draws the eye, establishing a clear hierarchy within the interior layout. Ideally placed against white or light grey walls, the aquatics and cool hues expand the perceived volume of the room."
    },
    {
        "id": "new_66",
        "title": "Turquoise and Peppers",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Turquoise-and-Peppers/1295487/6446775/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.8 W x 25.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "25.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/turquoise-and-peppers/",
        "slug": "turquoise-and-peppers",
        "wordpress_id": 2139,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Turquoise_and_PeppersPainting.jpg",
        "detected_colors": [
            "Brown",
            "Red",
            "Grey",
            "Black"
        ],
        "price": "1090",
        "description": "Curator's Note: Employing a flattened plane that emphasizes surface continuity, this work is grounded in earthy, resonant octaves, anchored by Slate and Graphite tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    },
    {
        "id": "new_67",
        "title": "Turquoise blend",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Turquoise-blend/1295487/6446755/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.8 W x 25.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "25.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/turquoise-blend/",
        "slug": "turquoise-blend",
        "wordpress_id": 2140,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Turquoise_blendPainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Red"
        ],
        "price": "1090",
        "description": "Curator's Note: Utilizing expansive negative space to frame its central motif, this work is radiating a saturated, thermal warmth, anchored by Graphite and Crimson tones. By harmonizing complex tones, it creates a sophisticated backdrop that unifies the room's color story. The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    },
    {
        "id": "new_68",
        "title": "Turquoise stretch",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Turquoise-stretch/1295487/6446705/view",
        "type": "page",
        "year": "2019",
        "styles": "Minimalist, Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.8 W x 25.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "25.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/turquoise-stretch/",
        "slug": "turquoise-stretch",
        "wordpress_id": 2141,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Turquoise_stretchPainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown"
        ],
        "price": "1090",
        "description": "Curator's Note: Employing a flattened plane that emphasizes surface continuity, this work is smoldering with latent intensity, anchored by Graphite and Slate tones. By harmonizing complex tones, it creates a sophisticated backdrop that unifies the room's color story. The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    },
    {
        "id": "new_69",
        "title": "Turquoise Circuit board",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Turquoise-Circuit-board/1295487/6446693/view",
        "type": "page",
        "year": "2019",
        "styles": "Geometric, Minimalist, Abstract, Structured",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.5 W x 25.5 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.5",
        "height": "25.5",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/turquoise-circuit-board/",
        "slug": "turquoise-circuit-board",
        "wordpress_id": 2142,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Turquoise_Circuit_boardPainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Red"
        ],
        "price": "1090",
        "description": "Curator's Note: Employing a flattened plane that emphasizes surface continuity, this work is smoldering with latent intensity, anchored by Rust and Graphite tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. Specifically, the warm palette complements natural wood grains and brass hardware, enhancing the organic character of the room."
    },
    {
        "id": "new_70",
        "title": "Blast of Blue on Red",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Blast-of-Blue-on-Red/1295487/6446665/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "25.8 W x 38.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "25.8",
        "height": "38.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/blast-of-blue-on-red/",
        "slug": "blast-of-blue-on-red",
        "wordpress_id": 2143,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Blast_of_Blue_on_RedPainting.jpg",
        "detected_colors": [
            "Grey",
            "Gold",
            "Silver",
            "Red"
        ],
        "price": "1090",
        "description": "Curator's Note: Negotiating the tension between rigid geometry and organic gesture, this work is emphasizing the sculptural quality of light and shadow, anchored by Terra Cotta and Slate tones. The work's commanding presence draws the eye, establishing a clear hierarchy within the interior layout. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": "new_71",
        "title": "Blue Gold",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Blue-Gold/1295487/6446651/view",
        "type": "page",
        "year": "2019",
        "styles": "Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.8 W x 25.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "25.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/blue-gold/",
        "slug": "blue-gold",
        "wordpress_id": 2144,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Blue_GoldPainting.jpg",
        "detected_colors": [
            "Brown",
            "Black"
        ],
        "price": "1090",
        "description": "Curator's Note: Negotiating the tension between rigid geometry and organic gesture, this work is focusing on value contrast rather than chromatic complexity, anchored by Espresso and Obsidian tones. By harmonizing complex tones, it creates a sophisticated backdrop that unifies the room's color story. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": "new_72",
        "title": "Blue Glacier",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Blue-Glacier/1295487/6446603/view",
        "type": "page",
        "year": "2019",
        "styles": "Minimalist, Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.8 W x 25.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "25.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/blue-glacier/",
        "slug": "blue-glacier",
        "wordpress_id": 1605,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Blue_GlacierPainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Black"
        ],
        "price": "1090",
        "description": "Curator's Note: Negotiating the tension between rigid geometry and organic gesture, this work is emphasizing the sculptural quality of light and shadow, anchored by Obsidian and Graphite tones. The work's commanding presence draws the eye, establishing a clear hierarchy within the interior layout. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": "new_73",
        "title": "Blue Wave",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Blue-Wave/1295487/6446583/view",
        "type": "page",
        "year": "2019",
        "styles": "Minimalist, Organic, Fluid, Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.8 W x 25.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "25.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/blue-wave/",
        "slug": "blue-wave",
        "wordpress_id": 2146,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Blue_WavePainting.jpg",
        "detected_colors": [
            "Grey",
            "Brown",
            "Black"
        ],
        "price": "1090",
        "description": "Curator's Note: Employing a flattened plane that emphasizes surface continuity, this work is emphasizing the sculptural quality of light and shadow, anchored by Obsidian and Graphite tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    },
    {
        "id": "new_74",
        "title": "Blue Mesh",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Blue-Mesh/1295487/6446557/view",
        "type": "page",
        "year": "2019",
        "styles": "Minimalist, Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.8 W x 25.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "25.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/blue-mesh/",
        "slug": "blue-mesh",
        "wordpress_id": 2147,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Blue_MeshPainting.jpg",
        "detected_colors": [
            "Grey",
            "Black",
            "Brown"
        ],
        "price": "1090",
        "description": "Curator's Note: Employing a flattened plane that emphasizes surface continuity, this work is maintaining a cool, atmospheric detachment, anchored by Obsidian and Slate tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. This palette harmonizes effortlessly with modern chrome fixtures and glass surfaces, reinforcing a sleek, contemporary aesthetic."
    },
    {
        "id": "new_75",
        "title": "Cold Blue",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Cold-Blue/1295487/6446543/view",
        "type": "page",
        "year": "2019",
        "styles": "Minimalist, Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "25.8 W x 38.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "25.8",
        "height": "38.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/cold-blue/",
        "slug": "cold-blue",
        "wordpress_id": 2148,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Cold_BluePainting.jpg",
        "detected_colors": [
            "Grey",
            "Black",
            "Brown"
        ],
        "price": "1090",
        "description": "Curator's Note: Relying on asymmetrical balance to drive visual movement, this work is operating within a restrained, monochromatic discipline, anchored by Slate and Graphite tones. By harmonizing complex tones, it creates a sophisticated backdrop that unifies the room's color story. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": "new_76",
        "title": "Blue Storm",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-Blue-Storm/1295487/6446503/view",
        "type": "page",
        "year": "2019",
        "styles": "Minimalist, Abstract",
        "mediumsDetailed": "Acrylic,\u00a0Paper",
        "dimensions": "38.8 W x 25.8 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "38.8",
        "height": "25.8",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/blue-storm/",
        "slug": "blue-storm",
        "wordpress_id": 1602,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Blue_StormPainting.jpg",
        "detected_colors": [
            "Grey",
            "Black",
            "Brown"
        ],
        "price": "1090",
        "description": "Curator's Note: Relying on asymmetrical balance to drive visual movement, this work is receding visually to create optical depth, anchored by Taupe and Slate tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": "new_77",
        "title": "No Public Shrooms Limited Edition of 1",
        "saatchi_url": "https://www.saatchiart.com/art/Printmaking-No-Public-Shrooms-Limited-Edition-of-1/1295487/6444945/view",
        "type": "page",
        "year": "2018",
        "styles": "Expressionism",
        "mediumsDetailed": "Metal,\u00a0Stainless Steel",
        "dimensions": "10 W x 14 H x 0.3 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "10",
        "height": "14",
        "depth": "0.3",
        "link": "https://elliotspencermorgan.com/no-public-shrooms-limited-edition-of-1/",
        "slug": "no-public-shrooms-limited-edition-of-1",
        "wordpress_id": 2150,
        "image_url": "https://images.saatchiart.com/saatchi/1295487/art/6444945/5514681-HSC00002-7.jpg",
        "detected_colors": [
            "Blue",
            "Beige",
            "Silver",
            "Grey"
        ],
        "price": "775",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is possessing a crisp, mineral serenity, anchored by Charcoal and Birch tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": "new_79",
        "title": "Start Sign Limited Edition of 1",
        "saatchi_url": "https://www.saatchiart.com/art/Printmaking-Start-Sign-Limited-Edition-of-1/1295487/6444891/view",
        "type": "page",
        "year": "2018",
        "styles": "Expressionism",
        "mediumsDetailed": "Metal,\u00a0Stainless Steel",
        "dimensions": "20 W x 20 H x 0.3 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "20",
        "height": "20",
        "depth": "0.3",
        "link": "https://elliotspencermorgan.com/start-sign-limited-edition-of-1/",
        "slug": "start-sign-limited-edition-of-1",
        "wordpress_id": 2152,
        "image_url": "https://images.saatchiart.com/saatchi/1295487/art/6444891/5514627-UOIQHDXE-7.jpg",
        "detected_colors": [
            "Red",
            "Silver",
            "Gold",
            "Brown"
        ],
        "price": "785",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is focusing on value contrast rather than chromatic complexity, anchored by Burgundy and Sand tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes."
    },
    {
        "id": "new_80",
        "title": "Right Way Limited Edition of 1",
        "saatchi_url": "https://www.saatchiart.com/art/Printmaking-Right-Way-Limited-Edition-of-1/1295487/6444853/view",
        "type": "page",
        "year": "2018",
        "styles": "Expressionism",
        "mediumsDetailed": "Metal,\u00a0Stainless Steel",
        "dimensions": "12 W x 8 H x 0.3 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "12",
        "height": "8",
        "depth": "0.3",
        "link": "https://elliotspencermorgan.com/right-way-limited-edition-of-1/",
        "slug": "right-way-limited-edition-of-1",
        "wordpress_id": 2153,
        "image_url": "https://images.saatchiart.com/saatchi/1295487/art/6444853/5514589-HSC00001-7.jpg",
        "detected_colors": [
            "Red",
            "Silver",
            "Gold"
        ],
        "price": "775",
        "description": "Curator's Note: Recording the physical velocity of the artist's hand, this work is smoldering with latent intensity, anchored by Burgundy and Sand tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_81",
        "title": "NO PORKING",
        "saatchi_url": "https://www.saatchiart.com/art/Installation-NO-PORKING/1295487/6444805/view",
        "type": "page",
        "year": "2018",
        "styles": "Minimalist, Expressionism",
        "mediumsDetailed": "Metal,\u00a0Stainless Steel",
        "dimensions": "14 W x 8 H x 0.5 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships in a Box",
        "shippingFrom": "Worldwide",
        "width": "14",
        "height": "8",
        "depth": "0.5",
        "link": "https://elliotspencermorgan.com/no-porking/",
        "slug": "no-porking",
        "wordpress_id": 2154,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/NO_PORKINGInstallation.jpg",
        "detected_colors": [
            "Silver",
            "Black",
            "Gold",
            "Grey"
        ],
        "price": "775"
    },
    {
        "id": "new_82",
        "title": "GOLD SERIES 006",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-GOLD-SERIES-006/1295487/6412863/view",
        "type": "page",
        "year": "2018",
        "styles": "Luxury, Abstract",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 24 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "24",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/gold-series-006/",
        "slug": "gold-series-006",
        "wordpress_id": 2155,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/GOLD_SERIES_006Painting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Grey"
        ],
        "price": "355",
        "description": "Curator's Note: Utilizing expansive negative space to frame its central motif, this work is smoldering with latent intensity, anchored by Obsidian and Brass tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_83",
        "title": "GOLD SERIES 005",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-GOLD-SERIES-005/1295487/6412831/view",
        "type": "page",
        "year": "2018",
        "styles": "Minimalist, Luxury, Abstract",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/gold-series-005/",
        "slug": "gold-series-005",
        "wordpress_id": 2156,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/GOLD_SERIES_005Painting.jpg",
        "detected_colors": [
            "Black",
            "Gold",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Utilizing expansive negative space to frame its central motif, this work is smoldering with latent intensity, anchored by Obsidian and Brass tones. The work's commanding presence draws the eye, establishing a clear hierarchy within the interior layout. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_84",
        "title": "GOLD SERIES 004",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-GOLD-SERIES-004/1295487/6412815/view",
        "type": "page",
        "year": "2018",
        "styles": "Minimalist, Luxury, Abstract",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/gold-series-004/",
        "slug": "gold-series-004",
        "wordpress_id": 2157,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/GOLD_SERIES_004Painting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Distilling form into essential rhythmic iterations, this work is grounded in earthy, resonant octaves, anchored by Obsidian and Brass tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_85",
        "title": "GOLD SERIES 003",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-GOLD-SERIES-003/1295487/6412813/view",
        "type": "page",
        "year": "2018",
        "styles": "Minimalist, Luxury, Abstract",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "Worldwide",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/gold-series-003/",
        "slug": "gold-series-003",
        "wordpress_id": 2158,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/GOLD_SERIES_003Painting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Employing a flattened plane that emphasizes surface continuity, this work is smoldering with latent intensity, anchored by Obsidian and Brass tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day."
    },
    {
        "id": "new_86",
        "title": "GOLD SERIES 002",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-GOLD-SERIES-002/1295487/6412799/view",
        "type": "page",
        "year": "2018",
        "styles": "Luxury, Abstract",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "United States.",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/gold-series-002/",
        "slug": "gold-series-002",
        "wordpress_id": 2159,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/GOLD_SERIES_002Painting.jpg",
        "detected_colors": [
            "Black",
            "Gold",
            "Brown"
        ],
        "price": "355",
        "description": "Curator's Note: Negotiating the tension between rigid geometry and organic gesture, this work is projecting an optimistic, solar luminosity, anchored by Obsidian and Espresso tones. The work's commanding presence draws the eye, establishing a clear hierarchy within the interior layout. Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    },
    {
        "id": "new_87",
        "title": "GOLD SERIES 001",
        "price": "355",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-GOLD-SERIES-001/1295487/6412791/view",
        "type": "page",
        "year": "2018",
        "styles": "Luxury, Abstract",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "17.5 W x 23 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "Not Applicable",
        "packaging": "Ships Rolled in a Tube",
        "shippingFrom": "United States.",
        "width": "17.5",
        "height": "23",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/gold-series-001/",
        "slug": "gold-series-001",
        "wordpress_id": 2160,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/GOLD_SERIES_001Painting.jpg",
        "detected_colors": [
            "Gold",
            "Black",
            "Brown"
        ],
        "description": "Curator's Note: Relying on asymmetrical balance to drive visual movement, this work is grounded in earthy, resonant octaves, anchored by Obsidian and Gold tones. The work's commanding presence draws the eye, establishing a clear hierarchy within the interior layout. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": "new_88",
        "title": "Waves",
        "saatchi_url": "https://www.saatchiart.com/art/Painting-waves/1295487/6364287/view",
        "type": "page",
        "year": "2018",
        "styles": "Figurative, Organic, Fluid, Abstract Expressionism, Modern, Conceptual",
        "mediumsDetailed": "Ink,\u00a0Paper",
        "dimensions": "20 W x 15 H x 0.1 D in",
        "frame": "Not Framed",
        "readyToHang": "No",
        "packaging": "Ships in a Box",
        "shippingFrom": null,
        "width": "20",
        "height": "15",
        "depth": "0.1",
        "link": "https://elliotspencermorgan.com/waves/",
        "slug": "waves",
        "wordpress_id": 1601,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/wavesPainting.jpg",
        "detected_colors": [
            "Pink",
            "Brown",
            "Silver",
            "Black"
        ],
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is operating within a restrained, monochromatic discipline, anchored by Birch and Espresso tones. The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": 3,
        "title": "Privacy Policy",
        "slug": "privacy-policy",
        "link": "https://elliotspencermorgan.com/?page_id=3",
        "saatchi_url": null,
        "image_url": null,
        "type": "page"
    },
    {
        "id": 1602,
        "title": "Blue Storm",
        "slug": "blue-storm",
        "link": "https://elliotspencermorgan.com/blue-storm/",
        "saatchi_url": null,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Blue_StormPainting.jpg",
        "type": "page",
        "wordpress_id": 1602,
        "detected_colors": [
            "Grey",
            "Black",
            "Brown"
        ],
        "styles": "Minimalist",
        "description": "Curator's Note: Relying on asymmetrical balance to drive visual movement, this work is receding visually to create optical depth, anchored by Taupe and Slate tones. Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings. The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated."
    },
    {
        "id": 1605,
        "title": "Blue Glacier",
        "slug": "blue-glacier",
        "link": "https://elliotspencermorgan.com/blue-glacier/",
        "saatchi_url": null,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Blue_GlacierPainting.jpg",
        "type": "page",
        "wordpress_id": 1605,
        "detected_colors": [
            "Grey",
            "Brown",
            "Black"
        ],
        "description": "Curator's Note: Negotiating the tension between rigid geometry and organic gesture, this work is emphasizing the sculptural quality of light and shadow, anchored by Obsidian and Graphite tones. The work's commanding presence draws the eye, establishing a clear hierarchy within the interior layout. The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue."
    },
    {
        "id": 1606,
        "title": "Golden Rule",
        "slug": "golden-rule",
        "link": "https://elliotspencermorgan.com/golden-rule/",
        "saatchi_url": null,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/Golden_RulePainting.jpg",
        "type": "page",
        "wordpress_id": 1606,
        "detected_colors": [
            "Red",
            "Gold",
            "Pink"
        ],
        "styles": "Minimalist",
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is projecting an optimistic, solar luminosity, anchored by Crimson and Sand tones. Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    },
    {
        "id": 1607,
        "title": "Transformation",
        "slug": "transformation",
        "link": "https://elliotspencermorgan.com/transformation/",
        "saatchi_url": null,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/TransformationPainting.jpg",
        "type": "page",
        "wordpress_id": 1607,
        "detected_colors": [
            "Red",
            "Pink",
            "Beige",
            "Silver"
        ],
        "description": "Curator's Note: Building density through layered, frenetic mark-making, this work is radiating a saturated, thermal warmth, anchored by Crimson and Pearl tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. Specifically, the warm palette complements natural wood grains and brass hardware, enhancing the organic character of the room."
    },
    {
        "id": 1608,
        "title": "Bloom",
        "slug": "bloom",
        "link": "https://elliotspencermorgan.com/bloom/",
        "saatchi_url": null,
        "image_url": "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/BloomPainting.jpg",
        "type": "page",
        "wordpress_id": 1608,
        "detected_colors": [
            "Brown",
            "Gold"
        ],
        "styles": "Luxury, Organic, Fluid",
        "description": "Curator's Note: Privileging gestural immediacy over calculated finish, this work is grounded in earthy, resonant octaves, anchored by Saffron and Graphite tones. It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance. These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture."
    }
]
JSON_EOD;

$root = $_SERVER['DOCUMENT_ROOT'];
$plugin_file = $root . '/wp-content/mu-plugins/esm-trade-portal.php';
$json_file = $root . '/artwork_data.json';

// Deploy Plugin
if (!is_dir(dirname($plugin_file))) {
    mkdir(dirname($plugin_file), 0755, true);
}

$log = [];

if (file_put_contents($plugin_file, $portal_code)) {
    $log[] = "✅ Plugin updated: $plugin_file (" . strlen($portal_code) . " bytes)";
} else {
    $log[] = "❌ Failed to write plugin file";
}

// Deploy JSON
if (file_put_contents($json_file, $json_data)) {
    $log[] = "✅ JSON updated: $json_file (" . strlen($json_data) . " bytes)";
} else {
    $log[] = "❌ Failed to write JSON file";
}

echo "<div style='font-family:monospace; padding:20px; background:#fafafa; border:1px solid #ddd;'>";
foreach($log as $l) {
    echo "<div>$l</div>";
}
echo "<br><a href='/trade/' style='display:inline-block; padding:10px 20px; background:black; color:white; text-decoration:none;'>Go to Portal</a>";
echo "</div>";
?>
