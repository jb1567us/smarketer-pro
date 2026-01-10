const ART_DATA_URL = '/artwork_data.json';
const COLL_DATA_URL = '/collections_data.json';
const UNSPLASH_KEY = '8gzaWlidpscOoUenn-sYrdR-UxdI_kPcxvYgnHfq8l0'; // Public Demo Key - Replace with own if needed
const DEFAULT_ROOM = '/istockphoto-1535511484-1024x1024.jpg';

// Data Structures
const ROOM_TEMPLATES = {
    modern: [
        { name: "Modern Living Room", query: "modern minimalist living room white walls" },
        { name: "Scandinavian Interior", query: "scandinavian living room bright natural light" },
        { name: "Contemporary Bedroom", query: "contemporary bedroom neutral tones" },
        { name: "Modern Office", query: "modern home office workspace" },
    ],
    traditional: [
        { name: "Classic Living Room", query: "traditional living room elegant furniture" },
        { name: "Cozy Study", query: "traditional study room library books" },
        { name: "Formal Dining", query: "traditional dining room chandelier" },
        { name: "Master Bedroom", query: "traditional bedroom luxurious decor" },
    ],
    industrial: [
        { name: "Loft Space", query: "industrial loft exposed brick concrete" },
        { name: "Urban Studio", query: "industrial studio apartment metal fixtures" },
        { name: "Warehouse Style", query: "industrial warehouse interior high ceilings" },
        { name: "Modern Industrial", query: "modern industrial living room" },
    ],
    gallery: [
        { name: "White Gallery", query: "art gallery white walls spotlights" },
        { name: "Museum Space", query: "museum gallery exhibition space" },
        { name: "Gallery Wall", query: "gallery wall multiple artworks display" },
        { name: "Contemporary Gallery", query: "contemporary art gallery minimal" },
    ]
};

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

function safeSetText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}

function safeSetVal(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val;
}

async function init() {
    try {
        console.log("Portal Init v2.1 - ESM Visualizer Upgrade");
        const [artRes, collRes] = await Promise.all([
            fetch(ART_DATA_URL, { cache: "no-store" }),
            fetch(COLL_DATA_URL, { cache: "no-store" })
        ]);

        if (!artRes.ok || !collRes.ok) throw new Error("Failed to fetch data assets");

        const artRaw = await artRes.json();
        collections = await collRes.json();

        // Process Artworks - Deduplicate logic
        const artToCollections = {};
        Object.values(collections).forEach(coll => {
            if (coll.artworks) {
                coll.artworks.forEach(a => {
                    if (!artToCollections[a.title]) artToCollections[a.title] = [];
                    artToCollections[a.title].push(coll.title);
                });
            }
        });

        const artMap = new Map();
        artRaw.forEach(a => {
            if (!a.image_url) return;
            a.membership = artToCollections[a.title] || [];

            // Dedupe logic
            if (!artMap.has(a.image_url)) {
                if (a.type === 'page') {
                    if (a.slug) a.link = '/' + a.slug + '/';
                } else {
                    if (a.slug) a.link = '/' + a.slug + '/';
                    else if (a.title) a.link = '/' + a.title.toLowerCase().replace(/ /g, '-').replace(/[^\w-]+/g, '') + '/';
                }
                artMap.set(a.image_url, a);
            }
        });

        artworks = Array.from(artMap.values());
        renderFilters();
        applyFilters();

        // Initialize Visualizer Logic
        ESM_Visualizer.init();

        // Check for Preview Request
        const urlParams = new URLSearchParams(window.location.search);
        const previewTitle = urlParams.get('preview');
        const sessionData = urlParams.get('session');

        if (sessionData) {
            ESM_Visualizer.loadFromURL(sessionData);
        } else if (previewTitle) {
            const decoded = decodeURIComponent(previewTitle).toLowerCase();
            const targetArt = artworks.find(a => a.title.toLowerCase() === decoded);
            if (targetArt) {
                ESM_Visualizer.open(targetArt);
                const newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
                window.history.pushState({ path: newUrl }, '', newUrl);
            }
        }

        // Remove loader
        setTimeout(() => {
            const loader = document.getElementById('loader-overlay');
            if (loader) {
                loader.style.opacity = '0';
                setTimeout(() => loader.remove(), 500);
            }
        }, 800);

    } catch (err) {
        console.error("Portal Init Error:", err);
    }
}

// ============================================
// FILTER & GRID LOGIC
// ============================================

function renderFilters() {
    const collContainer = document.getElementById('collection-filters');
    if (collContainer) {
        collContainer.innerHTML = '';
        Object.values(collections).sort((a, b) => a.title.localeCompare(b.title)).forEach(coll => {
            const label = document.createElement('label');
            label.className = 'checkbox-item';
            label.innerHTML = `<input type="checkbox" value="${coll.title}"> ${coll.title}`;
            label.querySelector('input').addEventListener('change', (e) => {
                if (e.target.checked) activeFilters.collections.add(coll.title);
                else activeFilters.collections.delete(coll.title);
                applyFilters();
            });
            collContainer.appendChild(label);
        });
    }

    const colorContainer = document.getElementById('color-filters');
    if (colorContainer) {
        colorContainer.innerHTML = '';
        const uniqueColors = new Set();
        artworks.forEach(a => a.detected_colors?.forEach(c => uniqueColors.add(c)));
        Array.from(uniqueColors).sort().forEach(color => {
            const div = document.createElement('div');
            div.className = 'swatch';
            div.style.backgroundColor = colorMap[color] || '#ccc';
            div.title = color;
            div.onclick = () => {
                div.classList.toggle('active');
                if (div.classList.contains('active')) activeFilters.colors.add(color);
                else activeFilters.colors.delete(color);
                applyFilters();
            };
            colorContainer.appendChild(div);
        });
    }

    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        const newSearch = searchInput.cloneNode(true);
        searchInput.parentNode.replaceChild(newSearch, searchInput);
        newSearch.addEventListener('input', (e) => {
            activeFilters.search = e.target.value.toLowerCase().trim();
            applyFilters();
        });
    }

    document.querySelectorAll('input[name="size"]').forEach(el => {
        el.addEventListener('change', (e) => {
            if (e.target.checked) activeFilters.sizes.add(e.target.value);
            else activeFilters.sizes.delete(e.target.value);
            applyFilters();
        });
    });
}

function applyFilters() {
    const filtered = artworks.filter(art => {
        if (activeFilters.search) {
            const matchTitle = art.title.toLowerCase().includes(activeFilters.search);
            const matchColl = art.membership && art.membership.some(m => m.toLowerCase().includes(activeFilters.search));
            if (!matchTitle && !matchColl) return false;
        }
        if (activeFilters.collections.size > 0 && (!art.membership || !art.membership.some(m => activeFilters.collections.has(m)))) return false;
        if (activeFilters.sizes.size > 0) {
            const w = parseFloat(art.width);
            let sizeMatch = false;
            if (activeFilters.sizes.has('Small') && w < 20) sizeMatch = true;
            if (activeFilters.sizes.has('Medium') && w >= 20 && w < 40) sizeMatch = true;
            if (activeFilters.sizes.has('Large') && w >= 40 && w < 60) sizeMatch = true;
            if (activeFilters.sizes.has('Oversized') && w >= 60) sizeMatch = true;
            if (!sizeMatch) return false;
        }
        if (activeFilters.colors.size > 0 && (!art.detected_colors?.some(c => activeFilters.colors.has(c)))) return false;
        return true;
    });

    renderGrid(filtered);
    safeSetText('count-display', `${filtered.length} Works Identified`);
}

function renderGrid(items) {
    const grid = document.getElementById('artwork-grid');
    if (!grid) return;
    grid.innerHTML = '';
    items.forEach((item, index) => {
        const card = document.createElement('div');
        card.className = 'card';
        const specUrl = `/downloads/spec_sheets/${item.title}_Sheet.pdf`;
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
    if (art) ESM_Visualizer.open(art);
}


// ============================================
// ESM VISUALIZER (Upgraded v2.1)
// ============================================

const ESM_Visualizer = {
    canvas: null,
    ctx: null,
    container: null,
    state: {
        roomImage: DEFAULT_ROOM,
        roomImgObj: null,
        artworks: [],
        wallColor: null,
        brightness: 100,
        contrast: 100,
        spotlight: false,
        showScaleReference: false,
        showDimensions: false,
        selectedArtId: null,
        isPlayingAR: false,
        compareMode: false,
        selectedForCompare: []
    },
    dragState: {
        isDragging: false,
        startX: 0,
        startY: 0
    },

    init: function () {
        this.canvas = document.getElementById('viz-canvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.container = document.getElementById('viz-canvas-container');

        this.setupGestures();
        this.setupTemplates();

        new ResizeObserver(() => this.render()).observe(this.container);

        const img = new Image();
        img.src = this.state.roomImage;
        img.onload = () => {
            this.state.roomImgObj = img;
            if (this.isOpen) this.render();
        };
    },

    setupTemplates: function () {
        const container = document.getElementById('room-templates-container');
        if (!container) return;
        container.innerHTML = '';

        Object.keys(ROOM_TEMPLATES).forEach(category => {
            const h4 = document.createElement('h4');
            h4.style.color = '#888';
            h4.style.fontSize = '0.75rem';
            h4.style.textTransform = 'uppercase';
            h4.style.marginTop = '15px';
            h4.style.marginBottom = '8px';
            h4.textContent = category;
            container.appendChild(h4);

            const grid = document.createElement('div');
            grid.style.display = 'grid';
            grid.style.gridTemplateColumns = '1fr 1fr';
            grid.style.gap = '8px';

            ROOM_TEMPLATES[category].forEach(temp => {
                const btn = document.createElement('div');
                btn.className = 'viz-photo';
                // Placeholder using unsplash source
                btn.style.background = '#333';
                btn.style.height = '60px'; // Compact
                btn.style.display = 'flex';
                btn.style.alignItems = 'center';
                btn.style.justifyContent = 'center';
                btn.style.fontSize = '0.7rem';
                btn.style.textAlign = 'center';
                btn.style.color = '#fff';
                btn.innerHTML = `<span>${temp.name}</span>`;
                btn.onclick = () => this.loadRoomTemplate(temp.query);
                grid.appendChild(btn);
            });
            container.appendChild(grid);
        });
    },

    loadRoomTemplate: function (query) {
        // Use placeholder service
        const url = `https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1200&q=80`; // Fallback static for stability
        // Ideally search unsplash API but keeping simple
        // Using a set of known good images would be better.
        // For now, let's use the query to pick a deterministic placeholder if possible, or just a generic one.
        // Since we don't have a secure backend proxy for Unsplash API here, we use a few hardcoded high quality ones.

        const map = {
            'modern': 'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=1200',
            'traditional': 'https://images.unsplash.com/photo-1513584685908-22dd98797f8f?w=1200',
            'industrial': 'https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=1200',
            'gallery': 'https://images.unsplash.com/photo-1577720643272-265f09367436?w=1200'
        };

        let src = map['modern'];
        if (query.includes('traditional')) src = map['traditional'];
        if (query.includes('industrial')) src = map['industrial'];
        if (query.includes('gallery')) src = map['gallery'];

        this.setRoomImage(src);
    },

    open: function (art) {
        document.getElementById('visualizer-modal').classList.add('active');
        this.isOpen = true;

        if (this.state.artworks.length === 0 || (this.state.artworks.length === 1 && this.state.artworks[0].id !== art.id)) {
            this.state.artworks = [{
                id: Date.now().toString(),
                data: art,
                x: 50,
                y: 40,
                scale: 0.7,
                rotation: 0
            }];
            this.state.selectedArtId = this.state.artworks[0].id;
        }

        this.updateUI();
        if (this.state.roomImgObj) this.render();
        else this.setRoomImage(this.state.roomImage);
    },

    close: function () {
        document.getElementById('visualizer-modal').classList.remove('active');
        this.isOpen = false;
        this.closeAR();
    },

    updateUI: function () {
        const art = this.state.artworks.find(a => a.id === this.state.selectedArtId);
        if (art) {
            safeSetText('viz-art-title', art.data.title);
            safeSetText('viz-art-dims', art.data.dimensions || `${art.data.width} x ${art.data.height} in`);
            safeSetVal('viz-scale', Math.round(art.scale * 100));
            safeSetVal('viz-rot', art.rotation);
            safeSetText('scale-val', Math.round(art.scale * 100) + '%');
            safeSetText('rot-val', art.rotation + '°');
        }

        // Show/Hide buttons
        const multiControls = document.getElementById('multi-art-controls');
        if (multiControls) {
            multiControls.style.display = this.state.artworks.length > 0 ? 'flex' : 'none';
        }
    },

    addArtwork: function () {
        const art = this.state.artworks.find(a => a.id === this.state.selectedArtId);
        if (art) {
            const newArt = JSON.parse(JSON.stringify(art));
            newArt.id = Date.now().toString();
            newArt.x += 10;
            newArt.y += 10;
            this.state.artworks.push(newArt);
            this.state.selectedArtId = newArt.id;
            this.updateUI();
            this.render();
        }
    },

    removeArtwork: function () {
        if (this.state.artworks.length <= 1) return alert("Must have at least one artwork.");
        this.state.artworks = this.state.artworks.filter(a => a.id !== this.state.selectedArtId);
        this.state.selectedArtId = this.state.artworks[0].id;
        this.updateUI();
        this.render();
    },

    setRoomImage: function (src) {
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = src;
        img.onload = () => {
            this.state.roomImage = src;
            this.state.roomImgObj = img;
            this.render();
        };
    },

    handleRoomUpload: function (input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => this.setRoomImage(e.target.result);
            reader.readAsDataURL(input.files[0]);
        }
    },

    // ----------------------
    // RENDER LOOP
    // ----------------------
    render: function () {
        if (!this.canvas || !this.ctx || !this.state.roomImgObj) return;

        const rect = this.container.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = rect.height;

        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        ctx.clearRect(0, 0, w, h);

        const rW = this.state.roomImgObj.width;
        const rH = this.state.roomImgObj.height;
        const rRatio = rW / rH;
        const cRatio = w / h;

        let drawW, drawH, drawX, drawY;

        if (rRatio > cRatio) {
            drawW = w;
            drawH = w / rRatio;
            drawX = 0;
            drawY = (h - drawH) / 2;
        } else {
            drawH = h;
            drawW = h * rRatio;
            drawY = 0;
            drawX = (w - drawW) / 2;
        }

        ctx.drawImage(this.state.roomImgObj, drawX, drawY, drawW, drawH);

        // Wall Color / Lighting
        if (this.state.wallColor || this.state.brightness !== 100 || this.state.contrast !== 100) {
            ctx.save();
            if (this.state.brightness !== 100) {
                ctx.fillStyle = this.state.brightness < 100 ? `rgba(0,0,0,${(100 - this.state.brightness) / 200})` : `rgba(255,255,255,${(this.state.brightness - 100) / 200})`;
                ctx.fillRect(drawX, drawY, drawW, drawH);
            }
            if (this.state.wallColor) {
                ctx.globalCompositeOperation = 'multiply';
                ctx.fillStyle = this.state.wallColor;
                ctx.fillRect(drawX, drawY, drawW, drawH);
                ctx.globalCompositeOperation = 'source-over';
            }
            ctx.restore();
        }

        this.state.artworks.forEach(art => {
            const img = new Image();
            img.src = art.data.image_url;
            if (img.complete) {
                const baseSize = Math.min(w, h) * 0.4;
                const aspect = (parseFloat(art.data.width) || 1) / (parseFloat(art.data.height) || 1);

                let artW = baseSize * art.scale;
                let artH = artW / aspect;

                const cx = (art.x / 100) * w;
                const cy = (art.y / 100) * h;

                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(art.rotation * Math.PI / 180);

                if (this.state.spotlight) {
                    ctx.shadowColor = 'rgba(0,0,0,0.8)';
                    ctx.shadowBlur = 40;
                    ctx.shadowOffsetY = 20;
                } else {
                    ctx.shadowColor = 'rgba(0,0,0,0.5)';
                    ctx.shadowBlur = 15;
                    ctx.shadowOffsetY = 10;
                }

                ctx.drawImage(img, -artW / 2, -artH / 2, artW, artH);

                if (this.state.selectedArtId === art.id) {
                    ctx.shadowColor = 'transparent';
                    ctx.strokeStyle = '#3498db';
                    ctx.lineWidth = 2;
                    ctx.strokeRect(-artW / 2, -artH / 2, artW, artH);
                }

                ctx.restore();

                if (this.state.showDimensions && this.state.selectedArtId === art.id) {
                    ctx.fillStyle = 'rgba(0,0,0,0.7)';
                    ctx.font = '12px sans-serif';
                    const txt = art.data.dimensions || `${art.data.width}x${art.data.height}`;
                    const tw = ctx.measureText(txt).width;
                    ctx.fillRect(cx - tw / 2 - 4, cy - artH / 2 - 25, tw + 8, 20);
                    ctx.fillStyle = '#fff';
                    ctx.fillText(txt, cx - tw / 2, cy - artH / 2 - 11);
                }
            }
        });

        if (this.state.showScaleReference) {
            const refH = Math.min(w, h) * 0.25;
            const refX = w - 50;
            const refY = h - 50;
            ctx.fillStyle = 'rgba(255,255,255,0.8)';
            ctx.fillRect(refX, refY - refH, 10, refH);
            ctx.fillText("6ft", refX - 10, refY + 15);
        }
    },

    switchTab: function (tab) {
        document.querySelectorAll('.viz-tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('[id^="viz-tab-"]').forEach(d => d.style.display = 'none');
        const tabs = { 'controls': 0, 'room': 1, 'lighting': 2 };
        document.querySelectorAll('.viz-tab')[tabs[tab]].classList.add('active');
        document.getElementById('viz-tab-' + tab).style.display = 'block';
    },

    setWallColor: function (color) {
        this.state.wallColor = color;
        this.render();
    },

    updateLighting: function () {
        this.state.brightness = parseInt(document.getElementById('viz-bright').value);
        this.state.contrast = parseInt(document.getElementById('viz-contrast').value);
        safeSetText('bright-val', this.state.brightness + '%');
        safeSetText('contrast-val', this.state.contrast + '%');
        this.render();
    },

    toggleSpotlight: function (val) {
        this.state.spotlight = val;
        this.render();
    },

    toggleDimensions: function (val) {
        this.state.showDimensions = val;
        this.render();
    },

    toggleScaleRef: function (val) {
        this.state.showScaleReference = val;
        this.render();
    },

    updateTransform: function () {
        const scale = document.getElementById('viz-scale').value;
        const rot = document.getElementById('viz-rot').value;
        const art = this.state.artworks.find(a => a.id === this.state.selectedArtId);

        if (art) {
            art.scale = scale / 100;
            art.rotation = rot;
            safeSetText('scale-val', scale + '%');
            safeSetText('rot-val', rot + '°');
            this.render();
        }
    },

        setupGestures: function () {
        const canvas = this.canvas;

        const getTouchPos = (t) => {
            const rect = canvas.getBoundingClientRect();
            return { x: t.clientX - rect.left, y: t.clientY - rect.top };
        };

        const getDist = (t1, t2) => {
            return Math.hypot(t1.clientX - t2.clientX, t1.clientY - t2.clientY);
        };

        const getAngle = (t1, t2) => {
            return Math.atan2(t2.clientY - t1.clientY, t2.clientX - t1.clientX) * 180 / Math.PI;
        };

        // MOUSE EVENTS
        canvas.addEventListener('mousedown', e => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const mx = e.clientX - rect.left;
            const my = e.clientY - rect.top;
            this.handleStart(mx, my);
        });

        window.addEventListener('mousemove', e => {
             if(this.dragState.isDragging && !this.dragState.isPinching) {
                 e.preventDefault();
                 const rect = canvas.getBoundingClientRect();
                 const mx = e.clientX - rect.left;
                 const my = e.clientY - rect.top;
                 this.handleMove(mx, my);
             }
        });

        window.addEventListener('mouseup', () => {
            this.dragState.isDragging = false;
        });

        // TOUCH EVENTS
        canvas.addEventListener('touchstart', e => {
            if (e.cancelable) e.preventDefault(); // Prevent scrolling
            if (e.touches.length === 1) {
                const pos = getTouchPos(e.touches[0]);
                this.handleStart(pos.x, pos.y);
            } else if (e.touches.length === 2) {
                 if (this.state.selectedArtId) {
                    this.dragState.isPinching = true;
                    this.dragState.isDragging = false;
                    this.dragState.initialDist = getDist(e.touches[0], e.touches[1]);
                    this.dragState.initialAngle = getAngle(e.touches[0], e.touches[1]);
                    
                    const art = this.state.artworks.find(a => a.id === this.state.selectedArtId);
                    if(art) {
                        this.dragState.startScale = art.scale;
                        this.dragState.startRotation = art.rotation;
                    }
                }
            }
        }, { passive: false });

        canvas.addEventListener('touchmove', e => {
            if (e.cancelable) e.preventDefault();
            if (e.touches.length === 1 && this.dragState.isDragging && !this.dragState.isPinching) {
                const pos = getTouchPos(e.touches[0]);
                this.handleMove(pos.x, pos.y);
            } else if (e.touches.length === 2 && this.dragState.isPinching) {
                const currentDist = getDist(e.touches[0], e.touches[1]);
                const currentAngle = getAngle(e.touches[0], e.touches[1]);

                const scaleFactor = getDist(e.touches[0], e.touches[1]) / (this.dragState.initialDist || 1);
                const angleDelta = currentAngle - (this.dragState.initialAngle || 0);

                const art = this.state.artworks.find(a => a.id === this.state.selectedArtId);
                if (art) {
                    art.scale = Math.max(0.2, Math.min(2.0, this.dragState.startScale * scaleFactor));
                    art.rotation = this.dragState.startRotation + angleDelta;
                    
                    // Update UI Controls
                    const scaleInput = document.getElementById('viz-scale');
                    if(scaleInput) scaleInput.value = Math.round(art.scale * 100);
                    
                    const rotInput = document.getElementById('viz-rot');
                    if(rotInput) rotInput.value = Math.round(art.rotation);
                    
                    // Helper to safely set text
                    const setTxt = (id, txt) => { 
                        const el = document.getElementById(id); 
                        if(el && el.textContent !== undefined) el.textContent = txt; 
                    };
                    setTxt('scale-val', Math.round(art.scale * 100) + '%');
                    setTxt('rot-val', Math.round(art.rotation) + '°');
                    
                    this.render();
                }
            }
        }, { passive: false });

        canvas.addEventListener('touchend', (e) => {
            if (e.touches.length < 2) this.dragState.isPinching = false;
            if (e.touches.length === 0) this.dragState.isDragging = false;
        });
    },

    handleStart: function(mx, my) {
         const w = this.canvas.width;
         const h = this.canvas.height;
         for (let i = this.state.artworks.length - 1; i >= 0; i--) {
            const art = this.state.artworks[i];
            const cx = (art.x / 100) * w;
            const cy = (art.y / 100) * h;
            const baseSize = Math.min(w, h) * 0.4;
            const aspect = (parseFloat(art.data.width) || 1) / (parseFloat(art.data.height) || 1);
            let artW = baseSize * art.scale;
            let artH = artW / aspect;

            if (mx >= cx - artW / 2 && mx <= cx + artW / 2 && my >= cy - artH / 2 && my <= cy + artH / 2) {
                this.state.selectedArtId = art.id;
                this.updateUI();
                this.render();
                this.dragState.isDragging = true;
                this.dragState.startX = mx;
                this.dragState.startY = my;
                this.dragState.artStartX = art.x;
                this.dragState.artStartY = art.y;
                return;
            }
        }
    },

    handleMove: function(mx, my) {
         if (this.state.selectedArtId) {
             const art = this.state.artworks.find(a => a.id === this.state.selectedArtId);
             if (art) {
                 const dx = mx - this.dragState.startX;
                 const dy = my - this.dragState.startY;
                 const rect = this.canvas.getBoundingClientRect();
                 art.x = this.dragState.artStartX + (dx / rect.width) * 100;
                 art.y = this.dragState.artStartY + (dy / rect.height) * 100;
                 this.render();
             }
         }
    },

    openAR: function () {
        const modal = document.getElementById('ar-preview-modal');
        modal.style.display = 'block';
        this.startCamera();

        const arCanvas = document.getElementById('ar-canvas');
        const arCtx = arCanvas.getContext('2d');
        const video = document.getElementById('ar-video');

        const arLoop = () => {
            if (modal.style.display === 'none') return;

            arCanvas.width = video.videoWidth || window.innerWidth;
            arCanvas.height = video.videoHeight || window.innerHeight;

            arCtx.drawImage(video, 0, 0, arCanvas.width, arCanvas.height);

            const art = this.state.artworks.find(a => a.id === this.state.selectedArtId);
            if (art && art.data.image_url) {
                const img = new Image();
                img.src = art.data.image_url;
                if (img.complete) {
                    const scale = document.getElementById('ar-scale').value;
                    const targetW = arCanvas.width * 0.5 * scale;
                    const aspect = (parseFloat(art.data.width) || 1) / (parseFloat(art.data.height) || 1);
                    const targetH = targetW / aspect;

                    arCtx.drawImage(img, (arCanvas.width - targetW) / 2, (arCanvas.height - targetH) / 2, targetW, targetH);
                }
            }
            requestAnimationFrame(arLoop);
        };
        requestAnimationFrame(arLoop);
    },

    closeAR: function () {
        document.getElementById('ar-preview-modal').style.display = 'none';
        this.stopCamera();
    },

    startCamera: async function () {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
            const video = document.getElementById('ar-video');
            video.srcObject = stream;
            video.play();
        } catch (e) {
            alert("Camera access denied or unavailable.");
        }
    },

    stopCamera: function () {
        const video = document.getElementById('ar-video');
        if (video.srcObject) {
            video.srcObject.getTracks().forEach(t => t.stop());
            video.srcObject = null;
        }
    },
    updateARScale: function (val) {
        safeSetText('ar-scale-val', Math.round(val * 100) + '%');
    },

    openSaveModal: function () {
        document.getElementById('save-session-modal').style.display = 'block';
    },

    confirmSaveSession: function () {
        const name = document.getElementById('session-name-input').value;
        if (!name) return alert("Enter a name");

        const session = {
            id: Date.now(),
            name: name,
            timestamp: Date.now(),
            state: JSON.parse(JSON.stringify(this.state))
        };
        session.state.roomImgObj = null;

        const saves = JSON.parse(localStorage.getItem('esm_viz_saves') || '[]');
        saves.push(session);
        localStorage.setItem('esm_viz_saves', JSON.stringify(saves));

        document.getElementById('save-session-modal').style.display = 'none';
        alert("Session Saved!");
    },

    openLoadModal: function () {
        const modal = document.getElementById('load-session-modal');
        const list = document.getElementById('sessions-list');
        list.innerHTML = '';

        // Add Compare Mode Toggle
        const header = modal.querySelector('h3');
        if (!document.getElementById('compare-mode-toggle')) {
            const toggleDiv = document.createElement('div');
            toggleDiv.style.fontSize = '0.8rem';
            toggleDiv.style.display = 'flex';
            toggleDiv.style.alignItems = 'center';
            toggleDiv.style.gap = '5px';
            toggleDiv.innerHTML = `<input type="checkbox" id="compare-mode-toggle" onchange="ESM_Visualizer.toggleCompareMode(this.checked)"> <label for="compare-mode-toggle">Compare Mode</label>`;
            header.insertBefore(toggleDiv, header.lastElementChild);
        }

        const saves = JSON.parse(localStorage.getItem('esm_viz_saves') || '[]');
        if (saves.length === 0) list.innerHTML = '<div style="color:#aaa; text-align:center;">No saved sessions found.</div>';

        saves.forEach(s => {
            const div = document.createElement('div');
            div.className = 'card';
            div.style.flexDirection = 'row';
            div.style.padding = '10px';
            div.style.alignItems = 'center';

            let actionHtml = '';
            if (this.state.compareMode) {
                const isSelected = this.state.selectedForCompare.includes(s.id);
                actionHtml = `<input type="checkbox" ${isSelected ? 'checked' : ''} onchange="ESM_Visualizer.toggleSelectCompare(${s.id})">`;
            } else {
                actionHtml = `
                    <button class="btn-premium accent" onclick="ESM_Visualizer.loadSession(${s.id})">Load</button>
                    <button class="btn-premium outline" style="margin-left:5px;" onclick="ESM_Visualizer.deleteSession(${s.id})">Del</button>
                `;
            }

            div.innerHTML = `
                <div style="flex:1;">
                    <div style="font-weight:bold; color:white;">${s.name}</div>
                    <div style="font-size:0.8rem; color:#aaa;">${new Date(s.timestamp).toLocaleDateString()}</div>
                </div>
                ${actionHtml}
             `;
            list.appendChild(div);
        });

        // Add Compare Button if in compare mode
        if (this.state.compareMode) {
            const btn = document.createElement('button');
            btn.className = 'btn-premium accent';
            btn.style.marginTop = '10px';
            btn.textContent = 'Compare Selected (2)';
            btn.onclick = () => this.launchComparison();
            list.appendChild(btn);
        }

        modal.style.display = 'block';
    },

    toggleCompareMode: function (val) {
        this.state.compareMode = val;
        this.state.selectedForCompare = [];
        this.openLoadModal(); // refresh
    },

    toggleSelectCompare: function (id) {
        if (this.state.selectedForCompare.includes(id)) {
            this.state.selectedForCompare = this.state.selectedForCompare.filter(x => x !== id);
        } else {
            if (this.state.selectedForCompare.length >= 2) this.state.selectedForCompare.shift(); // Max 2
            this.state.selectedForCompare.push(id);
        }
        this.openLoadModal();
    },

    launchComparison: function () {
        if (this.state.selectedForCompare.length !== 2) return alert("Select exactly 2 sessions.");

        const saves = JSON.parse(localStorage.getItem('esm_viz_saves') || '[]');
        const s1 = saves.find(x => x.id === this.state.selectedForCompare[0]);
        const s2 = saves.find(x => x.id === this.state.selectedForCompare[1]);

        document.getElementById('load-session-modal').style.display = 'none';
        document.getElementById('comparison-modal').style.display = 'flex';

        this.renderStatic('compare-canvas-1', s1);
        this.renderStatic('compare-canvas-2', s2);
        safeSetText('compare-meta-1', s1.name);
        safeSetText('compare-meta-2', s2.name);
    },

    renderStatic: function (canvasId, session) {
        const canvas = document.getElementById(canvasId);
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.src = session.state.roomImage;
        img.onload = () => {
            canvas.width = 600;
            canvas.height = 400;
            ctx.clearRect(0, 0, 600, 400);

            // Draw Room
            const rW = img.width;
            const rH = img.height;
            const rRatio = rW / rH;
            const cRatio = 600 / 400;
            let drawW, drawH, drawX, drawY;

            if (rRatio > cRatio) {
                drawW = 600; drawH = 600 / rRatio; drawX = 0; drawY = (400 - drawH) / 2;
            } else {
                drawH = 400; drawW = 400 * rRatio; drawY = 0; drawX = (600 - drawW) / 2;
            }
            ctx.drawImage(img, drawX, drawY, drawW, drawH);

            // Draw Arts
            session.state.artworks.forEach(art => {
                const aImg = new Image();
                aImg.crossOrigin = "anonymous";
                aImg.src = art.data.image_url;
                aImg.onload = () => {
                    const baseSize = Math.min(600, 400) * 0.4;
                    const aspect = (parseFloat(art.data.width) || 1) / (parseFloat(art.data.height) || 1);
                    let artW = baseSize * art.scale;
                    let artH = artW / aspect;
                    const cx = (art.x / 100) * 600;
                    const cy = (art.y / 100) * 400;

                    ctx.save();
                    ctx.translate(cx, cy);
                    ctx.rotate(art.rotation * Math.PI / 180);
                    ctx.shadowColor = 'rgba(0,0,0,0.5)';
                    ctx.shadowBlur = 10;
                    ctx.drawImage(aImg, -artW / 2, -artH / 2, artW, artH);
                    ctx.restore();
                };
            });
        };
    },

    loadSession: function (id) {
        const saves = JSON.parse(localStorage.getItem('esm_viz_saves') || '[]');
        const s = saves.find(x => x.id === id);
        if (s) {
            this.state = s.state;
            this.state.roomImgObj = null;
            this.setRoomImage(this.state.roomImage);
            if (this.state.artworks.length > 0) {
                // this.state.selectedArtId = this.state.artworks[0].id; // Persisted
            }
            document.getElementById('viz-bright').value = this.state.brightness;
            document.getElementById('viz-contrast').value = this.state.contrast;
            document.getElementById('load-session-modal').style.display = 'none';
            this.open({ id: 'restoring' });
        }
    },

    deleteSession: function (id) {
        let saves = JSON.parse(localStorage.getItem('esm_viz_saves') || '[]');
        saves = saves.filter(s => s.id !== id);
        localStorage.setItem('esm_viz_saves', JSON.stringify(saves));
        this.openLoadModal();
    },

    downloadPDF: function () {
        const canvas = this.canvas;
        const link = document.createElement('a');
        link.download = `esm-visualizer-${Date.now()}.png`;
        link.href = canvas.toDataURL();
        link.click();
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
