<?php
// Deploy Trade Portal v1.4
// Auto-generated deployment script

// Direct embedding uses Nowdoc (<<<'EOD') to prevent variable expansion
$payload = <<<'EOD'
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

    /* ... */
    
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
                console.log("Portal Init v1.4 - Force Update");
                // Parallel fetch with cache busting
                const [artRes, collRes] = await Promise.all([
                    fetch(ART_DATA_URL, {cache: "no-store"}),
                    fetch(COLL_DATA_URL, {cache: "no-store"})
                ]);
                
                if (!artRes.ok || !collRes.ok) throw new Error("Failed to fetch data assets");

                const artRaw = await artRes.json();
                collections = await collRes.json();

                // Process Artworks
                artworks = [];
                let seenTitles = new Set();

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

                artRaw.forEach(a => {
                    if (!a.image_url) return;
                    
                    // Attach membership
                    a.membership = artToCollections[a.title] || [];

                    if (a.type === 'page') {
                        if(a.slug) a.link = '/' + a.slug + '/';
                        artworks.push(a);
                        seenTitles.add(a.title);
                    } 
                    else if (a.type === 'post' || a.type === 'new_from_saatchi') {
                        if (!seenTitles.has(a.title)) {
                            if(a.slug) a.link = '/' + a.slug + '/';
                            else if(a.title) a.link = '/' + a.title.toLowerCase().replace(/ /g, '-').replace(/[^\w-]+/g, '') + '/';
                            
                            artworks.push(a);
                            seenTitles.add(a.title); 
                        }
                    }
                });

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
EOD;

$file = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins/esm-trade-portal.php';

// Prepare dir
if (!is_dir(dirname($file))) {
    mkdir(dirname($file), 0755, true);
}

if (file_put_contents($file, $payload)) {
    echo "<div style='font-family:sans-serif; padding:20px; background:#e8f5e9; border:1px solid #c8e6c9;'>";
    echo "<h2>✅ Trade Portal v1.4 Deployed Successfully</h2>";
    echo "<p>File written to: <code>$file</code></p>";
    echo "<p>Size: " . strlen($payload) . " bytes</p>";
    echo "<p><a href='/trade/' target='_blank' style='display:inline-block; padding:10px 20px; background:#2ecc71; color:white; text-decoration:none; border-radius:5px;'>Open Portal</a></p>";
    echo "</div>";
    
    // Attempt to flush rules
    if(function_exists('flush_rewrite_rules')) {
        flush_rewrite_rules();
        echo "<p>Rewrite rules flushed.</p>";
    }
} else {
    echo "<h2>❌ Failed to write file</h2>";
    echo "<p>Check permissions for " . dirname($file) . "</p>";
}
?>
