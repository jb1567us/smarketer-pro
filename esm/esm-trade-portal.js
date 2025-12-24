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
    if (el) el.textContent = text;
}

function safeSetVal(id, val) {
    const el = document.getElementById(id);
    if (el) el.value = val;
}

function toggleSidebar() {
    const aside = document.querySelector('aside');
    if (aside) aside.classList.toggle('active');
}

async function init() {
    try {
        console.log("Portal Init v1.4.2 - ArtMap Active");
        // Parallel fetch with cache busting
        const [artRes, collRes] = await Promise.all([
            fetch(ART_DATA_URL, { cache: "no-store" }),
            fetch(COLL_DATA_URL, { cache: "no-store" })
        ]);

        if (!artRes.ok || !collRes.ok) throw new Error("Failed to fetch data assets");

        const artRaw = await artRes.json();
        collections = await collRes.json();

        // Create a reverse lookup for membership
        const artToCollections = {};
        Object.values(collections).forEach(coll => {
            if (coll.artworks) {
                coll.artworks.forEach(a => {
                    if (!artToCollections[a.title]) artToCollections[a.title] = [];
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
                    if (a.slug && val.slug && a.slug === val.slug) {
                        duplicateFound = true;
                        // If new one has dims and old one doesn't, REPLACE the old key
                        const valHasDims = (val.width && val.height && val.width !== 'undefined' && val.height !== 'undefined');
                        if (hasDims && !valHasDims) {
                            artMap.delete(key); // Remove old entry
                            artMap.set(a.image_url, a); // Add new one
                        }
                        break;
                    }
                }

                if (!duplicateFound) {
                    artMap.set(a.image_url, a);
                }
            }

            // Ensure link is present
            if (a.type === 'page') {
                if (a.slug) a.link = '/' + a.slug + '/';
            } else {
                if (a.slug) a.link = '/' + a.slug + '/';
                else if (a.title) a.link = '/' + a.title.toLowerCase().replace(/ /g, '-').replace(/[^\w-]+/g, '') + '/';
            }
        });

        artworks = Array.from(artMap.values());

        renderFilters();
        applyFilters();

        // Check for Preview Request (from Artwork Page)
        const urlParams = new URLSearchParams(window.location.search);
        const previewTitle = urlParams.get('preview');

        if (previewTitle) {
            const decoded = decodeURIComponent(previewTitle).toLowerCase();
            const targetArt = artworks.find(a => a.title.toLowerCase() === decoded);

            if (targetArt) {
                console.log("Auto-launching visualizer for:", targetArt.title);
                openVisualizer(targetArt);

                // Clean URL without refresh
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

        // Initialize Gestures
        setupGestures();

    } catch (err) {
        console.error("Portal Init Error:", err);
        const grid = document.getElementById('artwork-grid');
        if (grid) {
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
    if (collContainer) {
        collContainer.innerHTML = ''; // Clear first
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

    // Render Colors
    const colorContainer = document.getElementById('color-filters');
    if (colorContainer) {
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
                if (div.classList.contains('active')) activeFilters.colors.add(color);
                else activeFilters.colors.delete(color);
                applyFilters();
            });
            colorContainer.appendChild(div);
        });
    }

    // Search listener
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
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
            if (e.target.checked) activeFilters.sizes.add(e.target.value);
            else activeFilters.sizes.delete(e.target.value);
            applyFilters();
        });
    });
}

function applyFilters() {
    const filtered = artworks.filter(art => {
        // Search
        if (activeFilters.search) {
            const matchTitle = art.title.toLowerCase().includes(activeFilters.search);
            const matchColl = art.membership && art.membership.some(m => m.toLowerCase().includes(activeFilters.search));
            if (!matchTitle && !matchColl) return false;
        }

        // Collection
        if (activeFilters.collections.size > 0) {
            if (!art.membership || !art.membership.some(m => activeFilters.collections.has(m))) return false;
        }

        // Size
        if (activeFilters.sizes.size > 0) {
            const w = parseFloat(art.width);
            let sizeMatch = false;
            if (activeFilters.sizes.has('Small') && w < 20) sizeMatch = true;
            if (activeFilters.sizes.has('Medium') && w >= 20 && w < 40) sizeMatch = true;
            if (activeFilters.sizes.has('Large') && w >= 40 && w < 60) sizeMatch = true;
            if (activeFilters.sizes.has('Oversized') && w >= 60) sizeMatch = true;
            if (!sizeMatch) return false;
        }

        // Color
        if (activeFilters.colors.size > 0) {
            if (!art.detected_colors?.some(c => activeFilters.colors.has(c))) return false;
        }

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
    if (art) openVisualizer(art);
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
    if (modal) modal.classList.add('active');

    // Load art into overlay
    const artImg = document.getElementById('art-overlay-img');
    if (artImg) artImg.src = art.image_url;

    if (!vizState.roomLoaded) {
        setRoomImage(DEFAULT_ROOM);
    } else {
        addArtToRoom();
    }
}

function closeVisualizer() {
    const modal = document.getElementById('visualizer-modal');
    if (modal) modal.classList.remove('active');
    stopCamera();
}

function switchVizTab(tabName) {
    document.querySelectorAll('.viz-tab').forEach(t => t.classList.remove('active'));

    // Fix: more robust selection
    const buttons = document.querySelectorAll('.viz-tab');
    buttons.forEach(b => {
        if (b.textContent.toLowerCase().includes(tabName)) b.classList.add('active');
    });

    const uploadTab = document.getElementById('viz-tab-upload');
    const unsplashTab = document.getElementById('viz-tab-unsplash');
    const cameraTab = document.getElementById('viz-tab-camera');

    if (uploadTab) uploadTab.style.display = 'none';
    if (unsplashTab) unsplashTab.style.display = 'none';
    if (cameraTab) cameraTab.style.display = 'none';

    stopCamera(); // Ensure camera stops when switching away

    if (tabName === 'upload' && uploadTab) uploadTab.style.display = 'block';
    if (tabName === 'unsplash' && unsplashTab) unsplashTab.style.display = 'block';
    if (tabName === 'camera' && cameraTab) cameraTab.style.display = 'block';
}

// Camera Logic
let cameraStream = null;

async function startCamera() {
    const errorEl = document.getElementById('camera-error');
    const video = document.getElementById('camera-stream');
    const btnStart = document.querySelector('#camera-controls button'); // Start button
    const btnCapture = document.getElementById('btn-capture');

    if (errorEl) errorEl.style.display = 'none';

    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });

        if (video) {
            video.srcObject = cameraStream;
            video.style.display = 'block';
        }

        if (btnStart) btnStart.style.display = 'none';
        if (btnCapture) btnCapture.style.display = 'block';

    } catch (err) {
        console.error("Camera Error:", err);
        if (errorEl) {
            errorEl.textContent = "Could not access camera. Please allow permissions.";
            errorEl.style.display = 'block';
        }
    }
}

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop());
        cameraStream = null;
    }

    const video = document.getElementById('camera-stream');
    if (video) video.style.display = 'none';

    const btnStart = document.querySelector('#camera-controls button');
    if (btnStart) btnStart.style.display = 'block';

    const btnCapture = document.getElementById('btn-capture');
    if (btnCapture) btnCapture.style.display = 'none';
}

function capturePhoto() {
    const video = document.getElementById('camera-stream');
    if (!video || !cameraStream) return;

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
if (roomInput) {
    // Remove old listener to avoid dupes
    const newRoomInput = roomInput.cloneNode(true);
    roomInput.parentNode.replaceChild(newRoomInput, roomInput);

    newRoomInput.addEventListener('change', function (e) {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
                setRoomImage(e.target.result);
            }
            reader.readAsDataURL(e.target.files[0]);
        }
    });
}

function setRoomImage(src) {
    const roomImg = document.getElementById('room-image-layer');
    if (!roomImg) return;

    roomImg.onload = function () {
        const ph = document.getElementById('viz-placeholder');
        if (ph) ph.style.display = 'none';
        roomImg.style.display = 'block';
        vizState.roomLoaded = true;
        addArtToRoom(); // Auto-add art once room is ready
    };
    roomImg.src = src;
}

function addArtToRoom() {
    if (!vizState.roomLoaded || !vizState.art) return;

    const overlay = document.getElementById('art-overlay-layer');
    if (overlay) {
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
    if (!queryEl) return;
    const query = queryEl.value;
    if (!query) return;

    const container = document.getElementById('unsplash-results');
    if (!container) return;

    container.innerHTML = '<div style="color:#888; padding:10px;">Searching...</div>';

    try {
        const res = await fetch(`https://api.unsplash.com/search/photos?query=${encodeURIComponent(query + ' interior')}&per_page=10&client_id=${UNSPLASH_KEY}`);
        const data = await res.json();

        container.innerHTML = '';
        if (!data.results || data.results.length === 0) {
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

    } catch (e) {
        console.error(e);
        container.innerHTML = '<div style="color:var(--text-secondary);">Error loading photos.</div>';
    }
}

// Controls Logic
const scaleRange = document.getElementById('viz-scale');
const rotRange = document.getElementById('viz-rot');

if (scaleRange) {
    // Avoid dupes
    const newScale = scaleRange.cloneNode(true);
    scaleRange.parentNode.replaceChild(newScale, scaleRange);

    newScale.addEventListener('input', (e) => {
        safeSetText('scale-val', e.target.value + '%');
        updateArtTransform();
    });
}

if (rotRange) {
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
    if (!overlay) return;

    const scaleRange = document.getElementById('viz-scale');
    const rotRange = document.getElementById('viz-rot');

    const scale = scaleRange ? scaleRange.value / 100 : 0.7;
    const rot = rotRange ? rotRange.value : 0;

    if (vizState.art) {
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
    } catch (e) {
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
    if (btn.textContent === "Preparing...") return;

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
                    if (typeof ClipboardItem !== "undefined") {
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


// Draggable & Gesture Logic
function setupGestures() {
    const dragItem = document.getElementById('art-overlay-layer');
    if (!dragItem) return;

    let isDragging = false;
    let startX, startY;

    // Pinch / Rotate state
    let initialDist = 0;
    let initialScale = 70;
    let initialAngle = 0;
    let startRotation = 0;
    let isGesturing = false;

    // Avoid dupes - cloneNode kills event listeners
    const newDrag = dragItem.cloneNode(true);
    dragItem.parentNode.replaceChild(newDrag, dragItem);

    const getDist = (t1, t2) => Math.hypot(t2.clientX - t1.clientX, t2.clientY - t1.clientY);
    const getAngle = (t1, t2) => Math.atan2(t2.clientY - t1.clientY, t2.clientX - t1.clientX) * 180 / Math.PI;

    // Mouse Events
    newDrag.addEventListener('mousedown', e => {
        isDragging = true;
        startX = e.clientX - newDrag.offsetLeft;
        startY = e.clientY - newDrag.offsetTop;
        newDrag.style.cursor = 'grabbing';
        e.preventDefault();
    });

    document.addEventListener('mouseup', () => {
        isDragging = false;
        if (newDrag) newDrag.style.cursor = 'grab';
    });

    document.addEventListener('mousemove', e => {
        if (!isDragging) return;
        e.preventDefault();
        newDrag.style.left = (e.clientX - startX) + 'px';
        newDrag.style.top = (e.clientY - startY) + 'px';
    });

    // Touch Events
    newDrag.addEventListener('touchstart', e => {
        if (e.touches.length === 1) {
            isDragging = true;
            isGesturing = false;
            startX = e.touches[0].clientX - newDrag.offsetLeft;
            startY = e.touches[0].clientY - newDrag.offsetTop;
        } else if (e.touches.length === 2) {
            isDragging = false;
            isGesturing = true;
            initialDist = getDist(e.touches[0], e.touches[1]);
            initialAngle = getAngle(e.touches[0], e.touches[1]);

            const scaleEl = document.getElementById('viz-scale');
            const rotEl = document.getElementById('viz-rot');
            initialScale = scaleEl ? parseFloat(scaleEl.value) : 70;
            startRotation = rotEl ? parseFloat(rotEl.value) : 0;
        }
    }, { passive: false });

    // Use document for touchmove to prevent scrolling while gesturing
    // Note: This effectively disables scrolling while touching the art element if we prevent default
    const dragHandler = (e) => {
        if (!isDragging && !isGesturing) return;

        // Only prevent default if we are actively dragging or gesturing
        if (e.cancelable) e.preventDefault();

        if (isDragging && e.touches.length === 1) {
            newDrag.style.left = (e.touches[0].clientX - startX) + 'px';
            newDrag.style.top = (e.touches[0].clientY - startY) + 'px';
        } else if (isGesturing && e.touches.length === 2) {
            // Pinch to Zoom
            const currentDist = getDist(e.touches[0], e.touches[1]);
            const scaleFactor = currentDist / initialDist;
            let newScale = initialScale * scaleFactor;

            // Constrain scale (matches slider 20-150)
            newScale = Math.min(Math.max(newScale, 20), 150);

            const scaleEl = document.getElementById('viz-scale');
            if (scaleEl) {
                scaleEl.value = newScale;
                safeSetText('scale-val', Math.round(newScale) + '%');
            }

            // Two-finger Rotation
            const currentAngle = getAngle(e.touches[0], e.touches[1]);
            const angleDiff = currentAngle - initialAngle;
            let newRot = startRotation + angleDiff;

            // Constrain rotation (matches slider -15 to 15)
            newRot = Math.min(Math.max(newRot, -15), 15);

            const rotEl = document.getElementById('viz-rot');
            if (rotEl) {
                rotEl.value = newRot;
                safeSetText('rot-val', Math.round(newRot) + '°');
            }

            updateArtTransform();
        }
    };

    // Attach to the element itself for movement, or document?
    // Attaching to document ensures we don't lose it if finger slides off, 
    // but preventing default on document interferes with scroll.
    // The previous code attached to document. Let's stick with that but be careful.
    document.addEventListener('touchmove', dragHandler, { passive: false });

    document.addEventListener('touchend', () => {
        isDragging = false;
        isGesturing = false;
    });
}

// Wait for DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
