
import re
import os

def prepare_v3():
    # 1. READ JS
    js_path = r"c:\sandbox\esm\esm-trade-portal.js" # This is the base file, which has most logic
    # BUT wait, the previous turn I said I would update v2? 
    # Actually esm-trade-portal.js IS the master file in sandbox.
    
    with open(js_path, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # 2. DEFINE NEW GESTURE LOGIC REPLACEMENT
    # We replace the entire setupGestures function.
    
    new_methods = r"""    setupGestures: function () {
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
    },"""

    # Replace setupGestures... up to openAR
    # We find the range from 'setupGestures: function' to 'openAR: function'
    # And replace it with new_methods
    
    start_marker = "setupGestures: function"
    end_marker = "openAR: function"
    
    start_idx = js_content.find(start_marker)
    end_idx = js_content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("ERROR: Could not find gesture block")
        return

    # Keep everything before setupGestures
    # Keep openAR and everything after
    # Insert new_methods in between (and a trailing comma if needed)
    
    # Check if there's a comma before openAR
    # In my view_file output, setupGestures block ends with }, then empty lines, then openAR.
    # The regex approach is safer if I can construct it well, but manual splicing works if markers are unique.
    
    # Actually, new_methods ends with '},' which is perfect.
    # We need to remove the old block cleanly.
    
    js_v3_content = js_content[:start_idx] + new_methods + "\n\n    " + js_content[end_idx:]
    
    with open(r"c:\sandbox\esm\esm-trade-portal-v3.js", 'w', encoding='utf-8') as f:
        f.write(js_v3_content)
        
    print("SUCCESS: Created esm-trade-portal-v3.js")

    # 3. UPDATE PHP CSS
    with open(r"c:\sandbox\esm\esm-trade-portal.php", 'r', encoding='utf-8') as f:
        php_content = f.read()

    # Add Mobile CSS Fix
    css_fix = """
        @media (max-width: 992px) {
            .swatch-grid { 
                grid-template-columns: repeat(5, 1fr) !important; 
                display: grid !important; 
                width: 100% !important;
            }
            .swatch {
                width: 100% !important;
                aspect-ratio: 1;
                display: block !important;
            }
            #color-filters {
                min-height: 40px;
                margin-bottom: 20px;
            }
        }
    """
    php_v3 = php_content.replace('</style>', css_fix + '</style>')

    # Update Script Source (Handle both original and already modified versions)
    # We look for "esm-trade-portal-v2.js" OR "esm-trade-portal.js"
    php_v3 = re.sub(r'esm-trade-portal(-v2)?\.js\?v=[\d\.]+', 'esm-trade-portal-v3.js?v=3.0.0', php_v3)

    # WRITE php V3
    with open(r"c:\sandbox\esm\esm-trade-portal-v3.php", 'w', encoding='utf-8') as f:
        f.write(php_v3)

    print("SUCCESS: Created esm-trade-portal-v3.php")

if __name__ == "__main__":
    prepare_v3()
