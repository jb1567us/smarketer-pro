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

        #artwork-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 3rem;
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

                <div style="margin-top:auto;">
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

        async function init() {
            try {
                // Parallel fetch
                const [artRes, collRes] = await Promise.all([
                    fetch(ART_DATA_URL),
                    fetch(COLL_DATA_URL)
                ]);
                
                const artRaw = await artRes.json();
                collections = await collRes.json();

                // Process Artworks
                artworks = artRaw.filter(a => a.type === 'page' && a.image_url);
                
                // Map collection metadata back to artworks
                artworks.forEach(art => {
                    art.membership = [];
                    for(let slug in collections) {
                        if(collections[slug].artworks.some(ca => ca.id === art.wordpress_id || ca.wordpress_id === art.wordpress_id)) {
                            art.membership.push(collections[slug].title);
                        }
                    }
                });

                renderFilters();
                applyFilters();
                
                // Remove loader
                setTimeout(() => {
                    document.getElementById('loader-overlay').style.opacity = '0';
                    setTimeout(() => document.getElementById('loader-overlay').remove(), 500);
                }, 800);

            } catch (err) {
                console.error("Portal Init Error:", err);
                document.getElementById('artwork-grid').innerHTML = "<p>Critical Error loading portal assets. Please contact support.</p>";
            }
        }

        // ============================================
        // FILTER & GRID LOGIC
        // ============================================

        function renderFilters() {
            // Render Collections
            const collContainer = document.getElementById('collection-filters');
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

            // Render Colors
            const colorContainer = document.getElementById('color-filters');
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

            // Search listener
            document.getElementById('global-search').addEventListener('input', (e) => {
                activeFilters.search = e.target.value.toLowerCase().trim();
                applyFilters();
            });

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
                    const matchColl = art.membership.some(m => m.toLowerCase().includes(activeFilters.search));
                    if(!matchTitle && !matchColl) return false;
                }
                
                // Collection
                if(activeFilters.collections.size > 0) {
                    if(!art.membership.some(m => activeFilters.collections.has(m))) return false;
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
            document.getElementById('count-display').innerText = `${filtered.length} Works Identified`;
        }

        function renderGrid(items) {
            const grid = document.getElementById('artwork-grid');
            grid.innerHTML = '';
            
            items.forEach((item, index) => {
                const card = document.createElement('div');
                card.className = 'card';
                
                const specUrl = `/downloads/spec_sheets/${item.title.replace(/ /g, '%20')}_spec.pdf`;
                
                // Need to pass full item object safely to onclick, so we store index
                // Better approach: Attach onclick via JS after creation, or simply use a lookup
                // Since items is a filtered array, we should refer to it carefully.
                // Or better: store ID in data attribute.
                
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
                        <div class="card-tag">${item.membership[0] || 'Original Series'}</div>
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
            document.getElementById('viz-art-title').textContent = art.title;
            document.getElementById('viz-art-dims').textContent = art.dimensions || `${art.width} x ${art.height} in`;
            
            const modal = document.getElementById('visualizer-modal');
            modal.classList.add('active');

            // Load art into overlay
            const artImg = document.getElementById('art-overlay-img');
            artImg.src = art.image_url;
            
            if(vizState.roomLoaded) {
                addArtToRoom();
            }
        }

        function closeVisualizer() {
            document.getElementById('visualizer-modal').classList.remove('active');
        }

        function switchVizTab(tabName) {
            document.querySelectorAll('.viz-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('[onclick="switchVizTab(\''+tabName+'\')"]')[0].classList.add('active');
            
            if(tabName === 'upload') {
                document.getElementById('viz-tab-upload').style.display = 'block';
                document.getElementById('viz-tab-unsplash').style.display = 'none';
            } else {
                document.getElementById('viz-tab-upload').style.display = 'none';
                document.getElementById('viz-tab-unsplash').style.display = 'block';
            }
        }

        // Room Upload
        document.getElementById('room-upload-input').addEventListener('change', function(e) {
            if (e.target.files && e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    setRoomImage(e.target.result);
                }
                reader.readAsDataURL(e.target.files[0]);
            }
        });

        function setRoomImage(src) {
            const roomImg = document.getElementById('room-image-layer');
            roomImg.onload = function() {
                document.getElementById('viz-placeholder').style.display = 'none';
                roomImg.style.display = 'block';
                vizState.roomLoaded = true;
                addArtToRoom(); // Auto-add art once room is ready
            };
            roomImg.src = src;
        }

        function addArtToRoom() {
            if(!vizState.roomLoaded || !vizState.art) return;
            
            const overlay = document.getElementById('art-overlay-layer');
            const room = document.getElementById('room-image-layer');
            const container = document.getElementById('viz-canvas');
            
            overlay.style.display = 'block';
            
            // Initial positioning (Center)
            // Use simple percentage for center to avoid complex rect math on init
            overlay.style.top = '30%';
            overlay.style.left = '40%';
            
            updateArtTransform();
        }

        // Unsplash Logic
        async function searchUnsplash() {
            const query = document.getElementById('unsplash-query').value;
            if(!query) return;
            
            const container = document.getElementById('unsplash-results');
            container.innerHTML = '<div style="color:#888; padding:10px;">Searching...</div>';
            
            try {
                const res = await fetch(`https://api.unsplash.com/search/photos?query=${encodeURIComponent(query + ' interior')}&per_page=10&client_id=${UNSPLASH_KEY}`);
                const data = await res.json();
                
                container.innerHTML = '';
                if(data.results.length === 0) {
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
                container.innerHTML = '<div style="color:red;">Error loading photos.</div>';
            }
        }

        // Controls Logic
        const scaleRange = document.getElementById('viz-scale');
        const rotRange = document.getElementById('viz-rot');
        
        scaleRange.addEventListener('input', (e) => {
            document.getElementById('scale-val').textContent = e.target.value + '%';
            updateArtTransform();
        });
        
        rotRange.addEventListener('input', (e) => {
            document.getElementById('rot-val').textContent = e.target.value + '°';
            updateArtTransform();
        });

        function updateArtTransform() {
            const overlay = document.getElementById('art-overlay-layer');
            const scale = scaleRange.value / 100;
            const rot = rotRange.value;
            
            // Base width of artwork relative to room. 
            // Better approximation: Let's assume a "Medium" art is 200px wide at 100% scale
            // And respect aspect ratio.
            if(vizState.art) {
                const aspect = vizState.art.width / vizState.art.height;
                const baseWidth = 300; // px
                
                overlay.style.width = (baseWidth * scale) + 'px';
                overlay.style.height = ((baseWidth / aspect) * scale) + 'px';
                overlay.style.transform = `rotate(${rot}deg)`;
            }
        }

        // Draggable Logic
        const dragItem = document.getElementById('art-overlay-layer');
        let active = false;
        let currentX;
        let currentY;
        let initialX;
        let initialY;
        let xOffset = 0;
        let yOffset = 0;

        document.getElementById('viz-canvas').addEventListener('mousedown', dragStart);
        document.getElementById('viz-canvas').addEventListener('mouseup', dragEnd);
        document.getElementById('viz-canvas').addEventListener('mousemove', drag);

        function dragStart(e) {
            if (e.target.closest('#art-overlay-layer')) {
                // If clicking the overlay
                initialX = e.clientX - xOffset;
                initialY = e.clientY - yOffset;
                active = true;
            }
        }

        function dragEnd(e) {
            initialX = currentX;
            initialY = currentY;
            active = false;
        }

        function drag(e) {
            if (active) {
                e.preventDefault();
                currentX = e.clientX - initialX;
                currentY = e.clientY - initialY;
                xOffset = currentX;
                yOffset = currentY;
                setTranslate(currentX, currentY, dragItem);
            }
        }

        function setTranslate(xPos, yPos, el) {
            // We use left/top for position and transform for scale/rotation to avoid conflict
            // But dragging usually works best with transform translate. 
            // However, we are already using transform for scale/rotate.
            // Let's use left/top relative deltas.
            
            // Actually, simpler approach for this MVP:
            // Just update left/top directly using existing style + delta.
            // But coordinate systems are tricky.
            
            // Let's stick to standard "style.left/top" approach without mixed transforms if possible.
            // The dragStart/drag logic above calculates offsets. 
            // Let's rely on the previous simple CSS drag logic in Deepseek's code which used left/top.
        }
        
        // Re-implementing Simple Drag from Deepseek source
        let isDragging = false;
        let startX, startY;
        
        dragItem.addEventListener('mousedown', e => {
            isDragging = true;
            startX = e.clientX - dragItem.offsetLeft;
            startY = e.clientY - dragItem.offsetTop;
            dragItem.style.cursor = 'grabbing';
            e.preventDefault();
        });
        
        document.addEventListener('mouseup', () => {
            isDragging = false;
            dragItem.style.cursor = 'grab';
        });
        
        document.addEventListener('mousemove', e => {
            if(!isDragging) return;
            e.preventDefault();
            dragItem.style.left = (e.clientX - startX) + 'px';
            dragItem.style.top = (e.clientY - startY) + 'px';
        });

        init();
    </script>
</body>
</html>
        <?php
        exit;
    }
}

new ESM_Trade_Portal();
?>