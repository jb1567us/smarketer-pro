<?php
/*
Plugin Name: ESM Trade Portal
Description: Creates a virtual page at /trade/ for interior designers to filter and download assets.
Version: 1.0
Author: ESM Dev
*/

if (!defined('ABSPATH'))
    exit;

class ESM_Trade_Portal
{

    public function __construct()
    {
        add_action('init', [$this, 'add_endpoint']);
        add_action('template_redirect', [$this, 'render_portal']);
    }

    public function add_endpoint()
    {
        add_rewrite_rule('^trade/?$', 'index.php?esm_trade=1', 'top');
        add_rewrite_tag('%esm_trade%', '1');
    }

    public function render_portal()
    {
        global $wp_query;
        if (!isset($wp_query->query_vars['esm_trade']))
            return;

        // Force 200 OK
        status_header(200);

        // Output the App
        ?>
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Trade Portal | Elliot Spencer Morgan</title>
            <!-- Fonts -->
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link
                href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap"
                rel="stylesheet">

            <style>
                :root {
                    --bg: #FAFAFA;
                    --text: #111;
                    --accent: #111;
                    --border: #E5E5E5;
                    --sidebar-w: 280px;
                }

                * {
                    box-sizing: border-box;
                }

                body {
                    margin: 0;
                    font-family: 'Inter', sans-serif;
                    background: var(--bg);
                    color: var(--text);
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    /* App-like feel */
                }

                /* Header */
                header {
                    height: 70px;
                    border-bottom: 1px solid var(--border);
                    display: flex;
                    align-items: center;
                    padding: 0 2rem;
                    background: #fff;
                    flex-shrink: 0;
                    justify-content: space-between;
                }

                .brand {
                    font-family: 'Playfair Display', serif;
                    font-size: 1.5rem;
                    font-weight: 600;
                    text-decoration: none;
                    color: #000;
                }

                .brand span {
                    font-weight: 400;
                    color: #666;
                    font-size: 1.2rem;
                    margin-left: 10px;
                }

                .nav-link {
                    color: #666;
                    text-decoration: none;
                    font-size: 0.9rem;
                    margin-left: 20px;
                    transition: color 0.2s;
                }

                .nav-link:hover {
                    color: #000;
                }

                /* Layout */
                .app-container {
                    display: flex;
                    flex: 1;
                    overflow: hidden;
                }

                /* Sidebar */
                aside {
                    width: var(--sidebar-w);
                    border-right: 1px solid var(--border);
                    background: #fff;
                    padding: 2rem;
                    overflow-y: auto;
                    flex-shrink: 0;
                }

                .filter-group {
                    margin-bottom: 2rem;
                }

                .filter-title {
                    font-size: 0.85rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    color: #888;
                }

                .filter-option {
                    display: block;
                    margin-bottom: 0.5rem;
                    cursor: pointer;
                    font-size: 0.95rem;
                    color: #333;
                }

                .filter-option input {
                    margin-right: 10px;
                }

                /* Swatches */
                .swatch-grid {
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 8px;
                }

                .swatch {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    border: 1px solid #ddd;
                    cursor: pointer;
                    position: relative;
                }

                .swatch.active::after {
                    content: '';
                    position: absolute;
                    top: -3px;
                    left: -3px;
                    right: -3px;
                    bottom: -3px;
                    border: 2px solid #000;
                    border-radius: 50%;
                }

                /* Main Grid */
                main {
                    flex: 1;
                    padding: 2rem;
                    overflow-y: auto;
                    background: #fdfdfd;
                }

                #artwork-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                    gap: 2rem;
                }

                /* Card */
                .card {
                    background: #fff;
                    border: 1px solid transparent;
                    break-inside: avoid;
                    transition: transform 0.2s, box-shadow 0.2s;
                }

                .card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
                    border-color: #eee;
                }

                .card-img-wrap {
                    position: relative;
                    aspect-ratio: 2/3;
                    /* Portrait */
                    overflow: hidden;
                    background: #f0f0f0;
                }

                .card-img {
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    transition: transform 0.5s;
                }

                .card:hover .card-img {
                    transform: scale(1.05);
                }

                .card-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(255, 255, 255, 0.9);
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    opacity: 0;
                    transition: opacity 0.3s;
                    gap: 10px;
                }

                .card:hover .card-overlay {
                    opacity: 1;
                }

                .btn-dl {
                    padding: 10px 20px;
                    background: #000;
                    color: #fff;
                    text-decoration: none;
                    font-size: 0.8rem;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    border-radius: 4px;
                    width: 180px;
                    text-align: center;
                }

                .btn-dl:hover {
                    background: #333;
                }

                .btn-dl.ghost {
                    background: transparent;
                    border: 1px solid #000;
                    color: #000;
                }

                .btn-dl.ghost:hover {
                    background: #000;
                    color: #fff;
                }

                .card-info {
                    padding: 1rem 0;
                }

                .card-title {
                    font-family: 'Playfair Display', serif;
                    font-size: 1.1rem;
                    margin: 0;
                }

                .card-meta {
                    font-size: 0.85rem;
                    color: #666;
                    margin-top: 4px;
                }

                #loading {
                    text-align: center;
                    margin-top: 5rem;
                    color: #999;
                }
            </style>
        </head>

        <body>

            <header>
                <a href="/" class="brand">Elliot Spencer Morgan <span>Trade Portal</span></a>
                <nav>
                    <a href="/" class="nav-link">Back to Site</a>
                    <a href="/contact/" class="nav-link">Contact Studio</a>
                </nav>
            </header>

            <div class="app-container">
                <aside>
                    <div class="filter-group">
                        <div class="filter-title">Dimensions</div>
                        <label class="filter-option"><input type="checkbox" name="size" value="Small"> Small (< 20")</label>
                                <label class="filter-option"><input type="checkbox" name="size" value="Medium"> Medium (20" -
                                    40")</label>
                                <label class="filter-option"><input type="checkbox" name="size" value="Large"> Large (40" -
                                    60")</label>
                                <label class="filter-option"><input type="checkbox" name="size" value="Oversized"> Oversized
                                    (60"+)</label>
                    </div>

                    <div class="filter-group">
                        <div class="filter-title">Style</div>
                        <div id="style-filters">
                            <!-- Populated via JS -->
                        </div>
                    </div>

                    <div class="filter-group">
                        <div class="filter-title">Dominant Color</div>
                        <div class="swatch-grid" id="color-filters">
                            <!-- Populated via JS -->
                        </div>
                    </div>

                    <div id="count-display" style="font-size:0.8rem; color:#888; margin-top:2rem;">Loading...</div>
                </aside>

                <main>
                    <div id="artwork-grid">
                        <div id="loading">Loading Collection...</div>
                    </div>
                </main>
            </div>

            <script>
                const API_URL = '/artwork_data.json';
                let allArtwork = [];
                let activeFilters = {
                    size: new Set(),
                    style: new Set(),
                    color: new Set()
                };

                async function init() {
                    try {
                        const response = await fetch(API_URL);
                        const data = await response.json();

                        // Filter out non-pages or items without images
                        allArtwork = data.filter(item => item.type === 'page' && item.image_url);

                        populateFilters();
                        renderGrid(allArtwork);
                        updateCount(allArtwork.length);
                    } catch (err) {
                        console.error(err);
                        document.getElementById('loading').innerText = "Error loading artwork data.";
                    }
                }

                function populateFilters() {
                    // styles
                    const styles = new Set();
                    // colors
                    const colors = new Set();

                    allArtwork.forEach(item => {
                        // Parse Styles
                        if (item.styles) {
                            item.styles.split(',').forEach(s => styles.add(s.trim()));
                        }
                        // Parse Colors
                        if (item.detected_colors) {
                            item.detected_colors.forEach(c => colors.add(c));
                        }
                    });

                    // Render Styles
                    const styleContainer = document.getElementById('style-filters');
                    Array.from(styles).sort().forEach(style => {
                        const label = document.createElement('label');
                        label.className = 'filter-option';
                        label.innerHTML = `<input type="checkbox" name="style" value="${style}"> ${style}`;
                        label.querySelector('input').addEventListener('change', (e) => toggleFilter('style', style, e.target.checked));
                        styleContainer.appendChild(label);
                    });

                    // Render Colors
                    const colorContainer = document.getElementById('color-filters');
                    const colorMap = {
                        'Red': '#e74c3c', 'Blue': '#3498db', 'Green': '#2ecc71', 'Gold': '#f1c40f',
                        'Silver': '#bdc3c7', 'Black': '#2c3e50', 'Grey': '#95a5a6', 'White': '#ecf0f1',
                        'Pink': '#fd79a8', 'Brown': '#795548', 'Beige': '#f5f5dc', 'Purple': '#9b59b6',
                        'Orange': '#e67e22', 'Yellow': '#f1c40f'
                    };

                    Array.from(colors).sort().forEach(color => {
                        const div = document.createElement('div');
                        div.className = 'swatch';
                        div.title = color;
                        div.style.backgroundColor = colorMap[color] || '#ccc';
                        if (color === 'White' || color === 'Beige') div.style.border = '1px solid #ccc';

                        div.addEventListener('click', () => {
                            div.classList.toggle('active');
                            toggleFilter('color', color, div.classList.contains('active'));
                        });
                        colorContainer.appendChild(div);
                    });

                    // Size Listeners
                    document.querySelectorAll('input[name="size"]').forEach(el => {
                        el.addEventListener('change', (e) => toggleFilter('size', e.target.value, e.target.checked));
                    });
                }

                function toggleFilter(category, value, isChecked) {
                    if (isChecked) {
                        activeFilters[category].add(value);
                    } else {
                        activeFilters[category].delete(value);
                    }
                    applyFilters();
                }

                function applyFilters() {
                    const results = allArtwork.filter(item => {
                        // Size Check
                        if (activeFilters.size.size > 0) {
                            const w = parseFloat(item.width);
                            let matched = false;
                            if (activeFilters.size.has('Small') && w < 20) matched = true;
                            if (activeFilters.size.has('Medium') && w >= 20 && w < 40) matched = true;
                            if (activeFilters.size.has('Large') && w >= 40 && w < 60) matched = true;
                            if (activeFilters.size.has('Oversized') && w >= 60) matched = true;
                            if (!matched) return false;
                        }

                        // Style Check
                        if (activeFilters.style.size > 0) {
                            if (!item.styles) return false;
                            const itemStyles = item.styles.split(',').map(s => s.trim());
                            const hasStyle = itemStyles.some(s => activeFilters.style.has(s));
                            if (!hasStyle) return false;
                        }

                        // Color Check
                        if (activeFilters.color.size > 0) {
                            if (!item.detected_colors) return false;
                            const hasColor = item.detected_colors.some(c => activeFilters.color.has(c));
                            if (!hasColor) return false;
                        }

                        return true;
                    });

                    renderGrid(results);
                    updateCount(results.length);
                }

                function renderGrid(items) {
                    const grid = document.getElementById('artwork-grid');
                    grid.innerHTML = '';

                    if (items.length === 0) {
                        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; color: #999; margin-top: 3rem;">No artworks match your filters.</div>';
                        return;
                    }

                    items.forEach(item => {
                        const el = document.createElement('div');
                        el.className = 'card';

                        // Helper to safe-encode
                        const safeTitle = item.title.replace(/"/g, '&quot;');
                        const slug = item.slug || safeTitle.toLowerCase().replace(/ /g, '-');
                        const specUrl = `/downloads/spec_sheets/${safeTitle.replace(/ /g, '%20')}_spec.pdf`; // Try Title first
                        const zipUrl = `/downloads/high_res/${safeTitle.replace(/ /g, '%20')}_HighRes.zip`;

                        el.innerHTML = `
                    <div class="card-img-wrap">
                        <img src="${item.image_url}" class="card-img" loading="lazy" alt="${safeTitle}">
                        <div class="card-overlay">
                            <a href="${item.link}" class="btn-dl ghost" target="_blank">View Details</a>
                            <a href="${specUrl}" download class="btn-dl">Spec Sheet</a>
                        </div>
                    </div>
                    <div class="card-info">
                        <h3 class="card-title">${item.title}</h3>
                        <div class="card-meta">${item.dimensions || ''}</div>
                        <div class="card-meta" style="color:#888">${item.styles || ''}</div>
                    </div>
                `;
                        grid.appendChild(el);
                    });
                }

                function updateCount(count) {
                    document.getElementById('count-display').innerText = `Showing ${count} Artworks`;
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