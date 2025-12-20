<?php
/*
Plugin Name: ESM Trade Portal
Description: Enhanced virtual page at /trade/ with Collections, Search, and Premium UI.
Version: 1.1
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
            --text-primary: #ffffff;
            --text-secondary: #a0a0a0;
            --accent: #E5C07B; /* Gold-ish accent */
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
            background: rgba(13, 13, 13, 0.8);
            border-bottom: 1px solid var(--border);
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
            cursor: pointer;
            padding-bottom: 4px;
            border-bottom: 2px solid transparent;
        }
        .nav-link:hover { color: var(--text-primary); }
        .nav-link.active {
            color: var(--text-primary);
            border-bottom-color: var(--accent);
        }

        /* Main Layout */
        .app-container {
            display: flex;
            flex: 1;
            overflow: hidden;
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
            transition: transform 0.3s ease;
        }

        @media (max-width: 1000px) {
            aside {
                position: fixed;
                top: var(--header-h);
                left: 0;
                bottom: 0;
                background: var(--bg);
                z-index: 500;
                transform: translateX(-100%);
            }
            aside.open {
                transform: translateX(0);
            }
        }

        .search-box {
            position: relative;
        }
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
            background: rgba(13, 13, 13, 0.4);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            opacity: 0;
            transition: opacity 0.4s;
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
        }
        .btn-premium:hover { background: var(--accent); transform: scale(1.05); }
        .btn-premium.outline {
            background: transparent;
            border: 1px solid white;
            color: white;
        }
        .btn-premium.outline:hover { background: white; color: black; }

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
        /* Spinner CSS */
        /* Sections */
        .portal-section {
            margin-top: 80px;
            padding: 60px;
            background: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
        }

        .section-title-premium {
            font-family: 'Playfair Display', serif;
            font-size: 2.5rem;
            margin-bottom: 2rem;
            color: var(--accent);
        }

        .benefit-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 40px;
        }

        .benefit-item h4 {
            font-family: 'Playfair Display', serif;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }

        .benefit-item p {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.6;
        }

        /* Inquiry Form */
        .inquiry-form {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .form-group.full { grid-column: span 2; }

        .form-group label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
        }

        .form-group input, .form-group textarea {
            padding: 14px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: white;
            font-family: inherit;
            outline: none;
        }

        .form-group input:focus, .form-group textarea:focus {
            border-color: var(--accent);
        }

        .btn-submit {
            grid-column: span 2;
            padding: 16px;
            background: var(--accent);
            color: black;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 2px;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .btn-submit:hover { transform: translateY(-2px); }

        /* Visualizer Specific Styles */
        .viz-layout {
            display: grid;
            grid-template-columns: 1fr 350px;
            gap: 2rem;
        }

        .viz-preview-area {
            background: #1a1a1a;
            aspect-ratio: 16/9;
            position: relative;
            overflow: hidden;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: inset 0 0 100px rgba(0,0,0,0.5);
        }

        #room-image-preview {
            max-width: 100%;
            max-height: 100%;
            display: none;
            border-radius: 8px;
        }

        #art-overlay {
            position: absolute;
            cursor: move;
            display: none;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.1s ease-out; /* Smooth rotation */
        }

        #art-overlay img { width: 100%; height: 100%; pointer-events: none; }

        .viz-controls {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            background: var(--surface);
            padding: 2.5rem;
            border-radius: 12px;
            border: 1px solid var(--border);
        }

        .viz-upload-box {
            border: 2px dashed var(--border);
            padding: 2rem;
            text-align: center;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .viz-upload-box:hover { border-color: var(--accent); background: var(--surface-elevated); }

        .viz-slider-group { display: flex; flex-direction: column; gap: 0.5rem; }
        .viz-slider-group label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 1px; }
        .viz-slider-group input { width: 100%; accent-color: var(--accent); }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>

    <div id="loader-overlay">
        <div class="view-title">ELLIOT SPENCER MORGAN</div>
    </div>

    <header>
        <a href="/" class="brand">ESM <span>Trade Portal</span></a>
        <div class="nav-actions">
            <div class="mobile-filter-toggle nav-link" onclick="toggleSidebar()" style="display: none;">Filters</div>
            <div class="nav-link active" onclick="switchTab('collection')">Collection</div>
            <div class="nav-link" onclick="switchTab('visualizer')">Visualizer</div>
            <a href="/contact/" class="nav-link">Inquire</a>
        </div>
    </header>

    <div class="app-container">
        <aside>
            <div class="search-box">
                <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                <input type="text" id="global-search" placeholder="Search title or series...">
            </div>

            <div class="filter-section">
                <div class="filter-label">Collections</div>
                <div class="checkbox-group" id="collection-filters">
                    <!-- Populated via JS -->
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
                    <!-- Populated via JS -->
                </div>
            </div>
        </aside>

        <main id="collection-view">
            <style>
                @media (max-width: 1000px) {
                    .mobile-filter-toggle { display: block !important; }
                }
            </style>
            <div class="view-header">
            
            <div id="artwork-grid">
                <!-- Artworks here -->
            </div>

            <!-- WHY WORK WITH US -->
            <div class="portal-section">
                <h3 class="section-title-premium">The Trade Advantage</h3>
                <div class="benefit-grid">
                    <div class="benefit-item">
                        <h4>Exclusive Pricing</h4>
                        <p>Enjoy registered trade member pricing on all original works and commissions. High-volume discounts available for project-wide styling.</p>
                    </div>
                    <div class="benefit-item">
                        <h4>Designer Resources</h4>
                        <p>Access high-resolution asset packages, detailed technical spec sheets, and 3D room mockup compatibility files for every piece.</p>
                    </div>
                    <div class="benefit-item">
                        <h4>Bespoke Commissions</h4>
                        <p>Collaborate directly with Elliot on site-specific installations, custom size requirements, and adjusted color palettes to match your project.</p>
                    </div>
                </div>
            </div>

            <!-- INQUIRY FORM -->
            <div class="portal-section" id="inquiry">
                <h3 class="section-title-premium">Trade Inquiry</h3>
                <form class="inquiry-form" onsubmit="handleInquiry(event)">
                    <div class="form-group">
                        <label>Full Name</label>
                        <input type="text" name="name" required placeholder="John Designer">
                    </div>
                    <div class="form-group">
                        <label>Email Address</label>
                        <input type="email" name="email" required placeholder="john@studio.com">
                    </div>
                    <div class="form-group">
                        <label>Project Name</label>
                        <input type="text" name="project" placeholder="The Residences at High Street">
                    </div>
                    <div class="form-group">
                        <label>Company</label>
                        <input type="text" name="company" placeholder="Studio Luxe Design">
                    </div>
                    <div class="form-group full">
                        <label>Project Budget / Scope</label>
                        <textarea name="message" rows="4" placeholder="Describe your project needs..."></textarea>
                    </div>
                    <button type="submit" class="btn-submit">Send Trade Request</button>
                </form>
            </div>
        </main>

        <main id="visualizer-view" style="display: none;">
            <div class="view-header">
                <div class="view-title">Room Visualizer</div>
                <div class="results-count">Upload a room photo to preview your selection</div>
            </div>

            <div class="viz-layout">
                <div class="viz-preview-area" id="viz-area">
                    <div id="viz-placeholder" style="color: var(--text-secondary); text-align: center;">
                        <svg style="width: 48px; opacity: 0.5; margin-bottom: 1rem;" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-5.04-6.71l-2.75 3.54-1.96-2.36L6.5 17h11l-3.54-4.71z"/></svg>
                        <p>Upload a photo of your space to begin</p>
                    </div>
                    <img id="room-image-preview">
                    <div id="art-overlay"></div>
                </div>

                <div class="viz-controls">
                    <div class="viz-upload-box" onclick="document.getElementById('viz-file').click()">
                        <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">Upload Room Image</p>
                        <p style="font-size: 0.75rem; color: var(--text-secondary);">JPG, PNG supported</p>
                        <input type="file" id="viz-file" hidden accept="image/*" onchange="handleRoomUpload(this)">
                    </div>

                    <div class="viz-slider-group">
                        <label>Scale Artwork</label>
                        <input type="range" id="viz-scale" min="10" max="100" value="50" oninput="updateArtTransform()">
                    </div>

                    <div class="viz-slider-group">
                        <label>Perspective / Rotation</label>
                        <input type="range" id="viz-rotate" min="-20" max="20" value="0" oninput="updateArtTransform()">
                    </div>

                    <div style="margin-top: 1rem;">
                        <div class="filter-label">Currently Previewing</div>
                        <div id="preview-active-info" style="margin-top: 1rem; font-size: 0.9rem; font-family: 'Playfair Display', serif;">
                            No artwork selected
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="portal-section" style="margin-top: 4rem;">
                <h3 class="section-title-premium">Select Artwork to Preview</h3>
                <div id="visualizer-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem;">
                    <!-- Small cards for visualizer -->
                </div>
            </div>
        </main>
    </div>

    <script>
        const ART_DATA_URL = '/artwork_data.json';
        const COLL_DATA_URL = '/collections_data.json';

        let artworks = [];
        let collections = {};
        let activeFilters = {
            search: '',
            collections: new Set(),
            sizes: new Set(),
            colors: new Set()
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
                renderVisualizerGrid();
                
                // Check for preview parameter
                const urlParams = new URLSearchParams(window.location.search);
                const previewTitle = urlParams.get('preview');
                if (previewTitle) {
                    const artwork = artworks.find(a => a.title === previewTitle);
                    if (artwork) {
                        switchTab('visualizer');
                        selectArtForPreview(artwork);
                    }
                }
                
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
                const zipUrl = `/downloads/high_res/${item.title.replace(/ /g, '%20')}_HighRes.zip`;

                card.innerHTML = `
                    <div class="image-container">
                        <img src="${item.image_url}" class="card-image" loading="lazy">
                        <div class="card-actions">
                            <a href="${item.link}" target="_blank" class="btn-premium">View Work</a>
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
                
                // Staggered appearance
                setTimeout(() => card.classList.add('visible'), index * 30);
            });
        }

        function renderVisualizerGrid() {
            const grid = document.getElementById('visualizer-grid');
            grid.innerHTML = '';
            artworks.forEach(item => {
                const div = document.createElement('div');
                div.style.cursor = 'pointer';
                div.innerHTML = `<img src="${item.image_url}" style="width: 100%; border-radius: 4px; border: 1px solid var(--border);">`;
                div.onclick = () => selectArtForPreview(item);
                grid.appendChild(div);
            });
        }

        // --- TAB SYSTEM ---
        function switchTab(tab) {
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            document.getElementById('collection-view').style.display = 'none';
            document.getElementById('visualizer-view').style.display = 'none';
            document.querySelector(`aside`).style.display = 'none';

            if (tab === 'collection') {
                document.querySelector('.nav-link:nth-child(1)').classList.add('active');
                document.getElementById('collection-view').style.display = 'block';
                document.querySelector(`aside`).style.display = 'flex';
            } else {
                document.querySelector('.nav-link:nth-child(2)').classList.add('active');
                document.getElementById('visualizer-view').style.display = 'block';
            }
        }

        // --- VISUALIZER LOGIC ---
        let vizState = {
            roomImg: null,
            currentArt: null,
            scale: 50,
            rotate: 0,
            x: 0,
            y: 0
        };

        function handleRoomUpload(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.getElementById('room-image-preview');
                    img.src = e.target.result;
                    img.style.display = 'block';
                    document.getElementById('viz-placeholder').style.display = 'none';
                    vizState.roomImg = e.target.result;
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        function selectArtForPreview(artwork) {
            vizState.currentArt = artwork;
            const overlay = document.getElementById('art-overlay');
            overlay.innerHTML = `<img src="${artwork.image_url}">`;
            overlay.style.display = 'block';
            document.getElementById('preview-active-info').innerText = artwork.title;
            updateArtTransform();
        }

        function updateArtTransform() {
            const scale = document.getElementById('viz-scale').value;
            const rotate = document.getElementById('viz-rotate').value;
            const overlay = document.getElementById('art-overlay');
            
            // Basic scaling logic
            const baseSize = 300;
            overlay.style.width = (baseSize * (scale/50)) + 'px';
            overlay.style.transform = `rotate(${rotate}deg)`;
        }

        // DRAG AND DROP
        let isDragging = false;
        let startX, startY;

        const overlay = document.getElementById('art-overlay');
        overlay.onmousedown = (e) => {
            isDragging = true;
            startX = e.clientX - overlay.offsetLeft;
            startY = e.clientY - overlay.offsetTop;
            overlay.style.cursor = 'grabbing';
        };

        window.onmousemove = (e) => {
            if (!isDragging) return;
            overlay.style.left = (e.clientX - startX) + 'px';
            overlay.style.top = (e.clientY - startY) + 'px';
        };

        window.onmouseup = () => {
            isDragging = false;
            overlay.style.cursor = 'move';
        };

        function toggleSidebar() {
            document.querySelector('aside').classList.toggle('open');
        }

        function handleInquiry(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            console.log("Trade Inquiry Received:", data);
            
            // Show success state
            e.target.innerHTML = `<div style="text-align: center; padding: 40px;">
                <h4 style="font-family: 'Playfair Display', serif; font-size: 2rem; margin-bottom: 1rem;">Request Received</h4>
                <p style="color: var(--text-secondary);">Thank you for your interest. Our trade concierge will contact you within 24 hours.</p>
            </div>`;

            if(window.gtag) {
                gtag('event', 'generate_lead', {
                    'event_category': 'Trade',
                    'event_label': data.company
                });
            }
        }

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