<?php
/*
Plugin Name: ESM Trade Portal
Description: Enhanced virtual page at /trade/ with Collections, Search, Premium UI, and Art Visualizer.
Version: 2.1
Author: ESM Dev (Upgraded)
*/

if (!defined('ABSPATH')) exit;

$log_file = plugin_dir_path(__FILE__) . 'debug_trace.log';

if (!class_exists('ESM_Trade_Portal')) {
class ESM_Trade_Portal {

    public function __construct() {
        add_action('init', [$this, 'add_endpoint']);
        add_action('template_redirect', [$this, 'render_portal'], 1);
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
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 2rem;
            width: 100%;
        }

        #viz-tab-upload {
            display: block; 
            padding-top: 1rem;
        }

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

        #loader-overlay {
            position: fixed; inset: 0; background: var(--bg); z-index: 2000;
            display: flex; justify-content: center; align-items: center;
            transition: opacity 0.5s ease-out;
        }
        
        /* VISUALIZER MODAL STYLES */
        #visualizer-modal {
            position: fixed; inset: 0; background: rgba(0, 0, 0, 0.95);
            backdrop-filter: blur(15px); z-index: 1500;
            display: none; flex-direction: column;
        }
        
        #visualizer-modal.active { display: flex; }

        .viz-header {
            padding: 1.5rem 3rem; border-bottom: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center;
        }
        
        .viz-title { font-family: 'Playfair Display'; font-size: 1.5rem; color: #fff; }
        .viz-close {
            background: none; border: none; color: #fff; font-size: 1.5rem; cursor: pointer;
            padding: 0.5rem; transition: color 0.3s;
        }
        .viz-close:hover { color: var(--accent); }

        .viz-body {
            flex: 1; display: flex; gap: 2rem; padding: 2rem; overflow: hidden;
        }

        .viz-controls {
            width: 320px; background: var(--surface); border: 1px solid var(--border);
            padding: 2rem; display: flex; flex-direction: column; gap: 2rem;
            overflow-y: auto; max-height: 100%;
        }

        .viz-canvas-area {
            flex: 1; background: #1a1a1a; border: 1px solid var(--border);
            position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;
            background-image: radial-gradient(#333 1px, transparent 1px); background-size: 20px 20px;
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
            border: 2px dashed var(--border); padding: 3rem 1rem; text-align: center;
            cursor: pointer; transition: all 0.3s;
        }
        .viz-upload-zone:hover { border-color: var(--accent); background: var(--surface-hover); }

        .viz-gallery {
            display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
            max-height: 250px; overflow-y: auto; margin-top: 1rem;
        }
        .viz-photo {
            aspect-ratio: 16/9; cursor: pointer; opacity: 0.8; transition: opacity 0.2s;
        }
        .viz-photo:hover { opacity: 1; }
        .viz-photo img { width: 100%; height: 100%; object-fit: cover; }

        .viz-active-art-info {
            background: var(--surface-elevated); padding: 1rem;
            border-left: 2px solid var(--accent); margin-bottom: 1rem;
        }

        .range-control {
            display: flex; flex-direction: column; gap: 0.5rem;
        }
        .range-control input { width: 100%; accent-color: var(--accent); }
        .range-label { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-secondary); }

        /* Mobile Optimization */
        @media (max-width: 992px) {
            :root { --sidebar-w: 100%; --header-h: 60px; }
            header { padding: 0 1rem; }
            .brand { font-size: 1.2rem; }
            .nav-actions { display: none; }
            .app-container { flex-direction: column; }
            
            /* Sidebar anchored to bottom */
            aside {
                position: fixed; top: var(--header-h); left: -100%; width: 100%;
                bottom: 0; height: auto; background: var(--bg); z-index: 1000;
                transition: left 0.4s; padding: 1.5rem;
                border-right: none; border-top: 1px solid var(--border);
            }
            aside.active { left: 0; }
            
            main { padding: 1rem; padding-bottom: 80px; /* Space for bottom nav */ }
            .view-header { flex-direction: column; gap: 0.5rem; margin-bottom: 1.5rem; }
            .view-title { font-size: 1.8rem; }
            #artwork-grid { grid-template-columns: repeat(2, 1fr); gap: 0.8rem; }
            
            /* Mobile Visualizer Layout */
            .viz-body { flex-direction: column; padding: 0; gap: 0; height: 100vh; }
            
            /* Canvas Area - Top */
            .viz-canvas-area { 
                width: 100%; height: 55vh; flex: none; order: 1; 
                border-bottom: 1px solid var(--border);
            }
            
            /* Controls - Bottom Half */
            .viz-controls { 
                width: 100%; height: 45vh; order: 2; padding: 1rem; 
                border-left: none; overflow-y: auto; padding-bottom: 80px; 
            }
            
            /* Bottom Navigation Bar */
            .viz-tabs {
                position: fixed; bottom: 0; left: 0; right: 0; height: 60px;
                background: #111; border-top: 1px solid #333;
                display: flex; justify-content: space-around; align-items: center;
                z-index: 2000; padding: 0; margin: 0; border-bottom: none;
            }
            
            .viz-tab {
                flex: 1; height: 100%; border: none; border-top: 3px solid transparent;
                background: none; color: #888; text-align: center; font-size: 0.7rem;
                display: flex; flex-direction: column; justify-content: center; align-items: center;
                gap: 4px; padding: 0;
            }
            .viz-tab.active { 
                color: var(--accent); border-bottom: none; border-top-color: var(--accent); background: #1a1a1a;
            }
            
            /* Compact Horizontal Scrolls */
            #room-templates-container > div {
                display: flex !important; grid-template-columns: none !important; 
                overflow-x: auto; gap: 10px; padding-bottom: 10px;
                scrollbar-width: none; /* Firefox */
            }
            #room-templates-container > div::-webkit-scrollbar { display: none; }
            
            .viz-photo {
                flex: 0 0 100px; height: 70px; /* Specific size for horizontal items */
                font-size: 0.65rem;
            }
            
            .swatch-grid {
                display: flex; overflow-x: auto; gap: 15px; padding-bottom: 10px;
            }
            .swatch { flex: 0 0 40px; }
            
            /* Larger Touch Targets */
            .btn-premium { padding: 16px 20px; font-size: 0.85rem; }
            input[type=range] { height: 30px; } /* Easier to grab */
        }

        .mobile-filter-btn {
            display: none; background: var(--surface); border: 1px solid var(--border);
            color: var(--accent); padding: 8px 16px; border-radius: 4px;
            font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;
            cursor: pointer; align-items: center; gap: 8px;
        }
        @media (max-width: 992px) { .mobile-filter-btn { display: flex; } }
        #loader-overlay { pointer-events: none; }
        #loader-overlay.active { pointer-events: auto; }
    </style>
</head>
<body>
    <div id="loader-overlay">
        <div class="view-title">ELLIOT SPENCER MORGAN</div>
    </div>

    <header>
        <a href="/" class="brand">ESM <span>Trade Portal</span></a>
        <div class="nav-actions">
            <a href="/" class="nav-link">Gallery</a>
            <a href="/contact/" class="nav-link">Inquire</a>
        </div>
        <button class="mobile-filter-btn" onclick="document.querySelector('aside').classList.toggle('active')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M3 17v2h6v-2H3zM3 5v2h10V5H3zm10 16v-2h8v-2h-8v-2h-2v6h2zM7 9v2H3v2h4v2h2V9H7zm14 4v-2H11v2h10zm-6-4h2V7h4V5h-4V3h-2v6z"/></svg>
            Filters
        </button>
    </header>

    <div class="app-container">
        <aside>
            <div class="search-box">
                <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
                <input type="text" id="global-search" placeholder="Search title or series...">
            </div>

            <div class="filter-section">
                <div class="filter-label">Collections</div>
                <div class="checkbox-group" id="collection-filters"></div>
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
                <div class="swatch-grid" id="color-filters"></div>
            </div>
        </aside>

        <main>
            <div class="view-header">
                <div class="view-title" id="page-title">Curated Selection</div>
                <div class="results-count" id="count-display">Analyzing works...</div>
            </div>
            
            <div id="artwork-grid"></div>
        </main>
    </div>

    <!-- VISUALIZER MODAL -->
    <div id="visualizer-modal">
        <div class="viz-header">
            <div class="viz-title">In-Situ Visualizer</div>
            <div style="display:flex; gap:10px;">
                <button class="btn-premium outline" style="padding:5px 15px; font-size:0.7rem;" onclick="ESM_Visualizer.openSaveModal()">Save Session</button>
                <button class="btn-premium outline" style="padding:5px 15px; font-size:0.7rem;" onclick="ESM_Visualizer.openLoadModal()">My Saves</button>
                <button class="viz-close" onclick="ESM_Visualizer.close()">✕</button>
            </div>
        </div>
        <div class="viz-body">
            <!-- VIZ CONTROLS -->
            <div class="viz-controls">
                
                <div class="viz-active-art-info">
                    <div style="font-size:0.7rem; color:var(--text-secondary); text-transform:uppercase; margin-bottom:5px;">Currently Viewing</div>
                    <div id="viz-art-title" style="font-family:'Playfair Display'; font-size:1.2rem; color:var(--accent);">Select Artwork</div>
                    <div id="viz-art-dims" style="font-size:0.85rem; color:var(--text-secondary);">Dimensions</div>
                </div>

                <div class="viz-tabs">
                    <button class="viz-tab active" onclick="ESM_Visualizer.switchTab('controls')">Adjust</button>
                    <button class="viz-tab" onclick="ESM_Visualizer.switchTab('room')">Room</button>
                    <button class="viz-tab" onclick="ESM_Visualizer.switchTab('lighting')">Lighting</button>
                    <button class="viz-tab" onclick="ESM_Visualizer.switchTab('camera')">Camera</button>
                </div>

                <div id="viz-tab-controls" style="display:block;">
                    <div class="range-control">
                        <div class="range-label"><span>Scale</span> <span id="scale-val">70%</span></div>
                        <input type="range" id="viz-scale" min="20" max="150" value="70" oninput="ESM_Visualizer.updateTransform()">
                    </div>
                    <div class="range-control">
                        <div class="range-label"><span>Rotation</span> <span id="rot-val">0°</span></div>
                        <input type="range" id="viz-rot" min="-15" max="15" value="0" oninput="ESM_Visualizer.updateTransform()">
                    </div>
                    
                    <div id="multi-art-controls" style="margin-top:10px; display:flex; gap:10px; display:none;">
                        <button class="btn-premium outline" style="flex:1; padding:8px; font-size:0.75rem;" onclick="ESM_Visualizer.addArtwork()">+ Dup</button>
                        <button class="btn-premium outline" style="flex:1; padding:8px; font-size:0.75rem;" onclick="ESM_Visualizer.removeArtwork()">- Del</button>
                    </div>

                    <div class="checkbox-item" style="margin-top:20px;">
                        <input type="checkbox" id="show-dims" onchange="ESM_Visualizer.toggleDimensions(this.checked)">
                        <label for="show-dims">Show Dimensions</label>
                    </div>
                    <div class="checkbox-item">
                        <input type="checkbox" id="show-scale-ref" onchange="ESM_Visualizer.toggleScaleRef(this.checked)">
                        <label for="show-scale-ref">Show Scale Ref (6' Person)</label>
                    </div>
                </div>

                <div id="viz-tab-room" style="display:none;">
                    <div class="viz-upload-zone" onclick="document.getElementById('room-upload-input').click()">
                        <div style="font-size:2rem; margin-bottom:1rem;">📷</div>
                        <div>Upload Room Photo</div>
                        <input type="file" id="room-upload-input" accept="image/*" style="display:none" onchange="ESM_Visualizer.handleRoomUpload(this)">
                    </div>
                    <details open style="margin-bottom:15px; border:1px solid var(--border); border-radius:4px; padding:10px;">
                    <summary style="cursor:pointer; font-size:0.85rem; color:var(--text-secondary); margin-bottom:10px;">Choose Room Style</summary>
                    <div id="room-templates-container" style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px;">
                        <!-- JS injects here -->
                    </div>
                </details>

                    <button class="btn-premium outline" style="width:100%; margin-top:20px;" onclick="ESM_Visualizer.openAR()">
                        <span style="margin-right:5px;">📱</span> Launch AR Preview
                    </button>
                    
                    <div style="margin-top:20px;">
                        <div class="filter-label">Wall Color</div>
                        <div style="display:flex; gap:5px; flex-wrap:wrap; margin-top:5px;">
                            <div class="swatch" style="background:#fff;" onclick="ESM_Visualizer.setWallColor(null)"></div>
                            <div class="swatch" style="background:#f5f5dc;" onclick="ESM_Visualizer.setWallColor('#f5f5dc')"></div>
                            <div class="swatch" style="background:#808080;" onclick="ESM_Visualizer.setWallColor('#808080')"></div>
                            <div class="swatch" style="background:#2c3e50;" onclick="ESM_Visualizer.setWallColor('#2c3e50')"></div>
                            <div class="swatch" style="background:#000;" onclick="ESM_Visualizer.setWallColor('#000000')"></div>
                            <div class="swatch" style="background:#c0392b;" onclick="ESM_Visualizer.setWallColor('#c0392b')" title="Red"></div>
                        </div>
                    </div>
                </div>

                <div id="viz-tab-lighting" style="display:none;">
                    <div class="range-control">
                        <div class="range-label"><span>Brightness</span> <span id="bright-val">100%</span></div>
                        <input type="range" id="viz-bright" min="50" max="150" value="100" oninput="ESM_Visualizer.updateLighting()">
                    </div>
                    <div class="range-control">
                        <div class="range-label"><span>Contrast</span> <span id="contrast-val">100%</span></div>
                        <input type="range" id="viz-contrast" min="50" max="150" value="100" oninput="ESM_Visualizer.updateLighting()">
                    </div>
                    <div class="checkbox-item" style="margin-top:15px;">
                        <input type="checkbox" id="viz-spotlight" onchange="ESM_Visualizer.toggleSpotlight(this.checked)">
                        <label for="viz-spotlight">Enable Spotlight Effect</label>
                    </div>
                </div>

                <div id="viz-tab-camera" style="display:none;">
                    <div style="background:var(--surface-elevated); padding:20px; border-radius:8px; text-align:center; margin-top:20px;">
                         <button class="btn-premium accent" style="width:100%; font-size:1.1rem; padding:20px;" onclick="ESM_Visualizer.openAR()">
                            LAUNCH CAMERA
                        </button>
                    </div>
                    
                    <p style="color:#888; font-size:0.8rem; margin-top:20px; text-align:center; line-height:1.5;">
                        <strong>Instructions:</strong><br>
                        1. Tap 'Launch Camera'<br>
                        2. Allow camera access<br>
                        3. Point at your wall<br>
                        4. Tap the Circle button to capture
                        <br><br>
                        <span id="camera-error-msg" style="color:#e74c3c; display:none;">Camera access denied. Check browser permissions.</span>
                    </p>
                </div>

                <div style="margin-top:auto; display:flex; flex-direction:column; gap:12px; margin-bottom:20px;">
                     <!-- Spacer for layout -->
                </div>
            </div>

            <!-- VIZ CANVAS -->
            <div class="viz-canvas-area" id="viz-canvas-container">
                 <canvas id="viz-canvas" style="width:100%; height:100%; object-fit:contain;"></canvas>
            </div>
        </div>
    </div>

    <!-- AR PREVIEW MODAL -->
    <div id="ar-preview-modal" style="display:none; position:fixed; inset:0; background:black; z-index:2000;">
        <video id="ar-video" playsinline autoplay muted style="display:none;"></video>
        <canvas id="ar-canvas" style="width:100%; height:100%; object-fit:cover;"></canvas>
        <div style="position:absolute; top:20px; left:20px; right:20px; display:flex; justify-content:space-between; align-items:center;">
             <button class="btn-premium outline" onclick="ESM_Visualizer.closeAR()">✕ Close</button>
             <button class="btn-premium outline" onclick="ESM_Visualizer.switchCamera()">↻ Camera</button>
        </div>
        <div style="position:absolute; bottom:20px; left:20px; right:20px; background:rgba(0,0,0,0.7); padding:15px; border-radius:8px;">
            <div class="range-control">
                <div class="range-label"><span>AR Scale</span> <span id="ar-scale-val">100%</span></div>
                <input type="range" id="ar-scale" min="0.3" max="2.0" step="0.1" value="1.0" oninput="ESM_Visualizer.updateARScale(this.value)">
            </div>
            <p style="color:#aaa; font-size:12px; text-align:center; margin-top:10px;">Tap and drag to reposition artwork</p>
            
            <button class="btn-premium accent" onclick="ESM_Visualizer.captureRoom()" style="
                display:block; width:60px; height:60px; border-radius:50%; 
                margin:15px auto 0 auto; padding:0; border:4px solid white; 
                box-shadow: 0 0 10px rgba(0,0,0,0.5); font-size:0;">
                Capture
            </button>
        </div>
    </div>

    <!-- COMPARISON MODAL -->
    <div id="comparison-modal" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.95); z-index:1600; flex-direction:column;">
        <div class="viz-header">
            <div class="viz-title">Comparison View</div>
            <button class="viz-close" onclick="document.getElementById('comparison-modal').style.display='none'">✕</button>
        </div>
        <div style="flex:1; display:flex; padding:20px; gap:20px; overflow:auto;">
            <div style="flex:1; display:flex; flex-direction:column; gap:10px;">
                <canvas id="compare-canvas-1" style="width:100%; background:#111; border:1px solid #333;"></canvas>
                <div id="compare-meta-1" style="color:#fff;"></div>
            </div>
            <div style="flex:1; display:flex; flex-direction:column; gap:10px;">
                <canvas id="compare-canvas-2" style="width:100%; background:#111; border:1px solid #333;"></canvas>
                <div id="compare-meta-2" style="color:#fff;"></div>
            </div>
        </div>
    </div>

    <!-- SAVE SESSION MODAL -->
    <div id="save-session-modal" class="glass" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); padding:30px; z-index:1700; width:400px; max-width:90%;">
        <h3 style="color:white; font-family:'Playfair Display'; margin-bottom:20px;">Save Session</h3>
        <input type="text" id="session-name-input" placeholder="Enter session name..." style="width:100%; padding:10px; margin-bottom:20px; background:#222; border:1px solid #444; color:white;">
        <div style="display:flex; gap:10px; justify-content:flex-end;">
            <button class="btn-premium outline" onclick="document.getElementById('save-session-modal').style.display='none'">Cancel</button>
            <button class="btn-premium accent" onclick="ESM_Visualizer.confirmSaveSession()">Save</button>
        </div>
    </div>

    <!-- LOAD SESSION MODAL -->
    <div id="load-session-modal" class="glass" style="display:none; position:fixed; top:50%; left:50%; transform:translate(-50%, -50%); padding:30px; z-index:1700; width:500px; max-width:90%; max-height:80vh; overflow-y:auto;">
        <h3 style="color:white; font-family:'Playfair Display'; margin-bottom:20px; display:flex; justify-content:space-between; flex-wrap:wrap;">
            <span>Saved Sessions</span>
            <button onclick="document.getElementById('load-session-modal').style.display='none'" style="background:none; border:none; color:white; cursor:pointer;">✕</button>
        </h3>
        <div id="sessions-list" style="display:flex; flex-direction:column; gap:10px;"></div>
    </div>

    <script src="<?php echo plugin_dir_url(__FILE__); ?>esm-trade-portal-v2.js?v=2.1.0"></script>
</body>
</html>
        <?php
        exit;
    }
}
}

new ESM_Trade_Portal();
