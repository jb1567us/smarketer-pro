import json
import os
import qrcode
import requests
import io
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
# from sklearn.cluster import KMeans
# import numpy as np

# Cache directory for images
IMAGE_CACHE_DIR = r'C:\sandbox\esm\image_cache'
os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

def rgb_to_hex(rgb):
    """Converts (r, g, b) tuple to #RRGGBB string."""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2]).upper()

def download_image(url, local_filename):
    """Downloads image to cache if not exists. Tries local files and fallback paths."""
    path = os.path.join(IMAGE_CACHE_DIR, local_filename)
    if os.path.exists(path):
        if os.path.getsize(path) > 1000: # sanity check
            return path
        else:
            os.remove(path) # corrupt/empty
    
    # Logic to Try:
    # 0. Check local images directory (high-res source)
    local_source_dir = r'C:\sandbox\esm\images'
    # The local_filename is like "1674_Portal_Sheet.jpg", but source might be "PortalPainting.jpg"
    # Try to find a match in the local images folder if possible
    if os.path.exists(local_source_dir):
        # Heuristic: if cache name contains artwork specific part, we might need a better mapping
        # But let's check if the base filename from URL exists locally
        if url:
            url_filename = url.split('/')[-1]
            local_match = os.path.join(local_source_dir, url_filename)
            if os.path.exists(local_match):
                print(f"   Found local source: {url_filename}")
                # Copy to cache for consistency or just return local path
                return local_match

    # 1. Fallback URL (User specific high-res)
    # 2. Original URL (saatchi/wordpress)
    
    filename = url.split('/')[-1] if url else ""
    fallback_url = f"https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/{filename}" if filename else None
    
    attempts = [fallback_url, url]
    
    for try_url in attempts:
        if not try_url: continue
        try:
            print(f"   Attempting download from: {try_url}")
            h = requests.head(try_url, timeout=5)
            # Accept if 200 and seems like image OR if method not allowed (some servers block HEAD) try GET
            if h.status_code == 200 or h.status_code == 405: 
                response = requests.get(try_url, timeout=15)
                if response.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    print(f"   Downloaded: {local_filename}")
                    return path
            elif h.status_code == 404:
                print(f"   404 at {try_url}")
                continue 
        except Exception as e:
            print(f"   Failed to check {try_url}: {e}")
            
    print(f"❌ Could not download image for {local_filename}")
    return None

def extract_dominant_colors(image_path, n_colors=5):
    """Extracts dominant colors using PIL Quantization (No sklearn needed)."""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        
        # Resize to speed up
        img.thumbnail((150, 150))
        
        # Quantize to n_colors
        # method=1 (FastOctree) is default and good
        quantized = img.quantize(colors=n_colors + 2, method=1)
        quantized_rgb = quantized.convert('RGB')
        
        # Get colors (count, pixel)
        counts = quantized_rgb.getcolors(maxcolors=256)
        colors = []
        if counts:
            # Sort by count desc
            counts.sort(key=lambda x: x[0], reverse=True)
            for count, rgb in counts:
                 # Filter out pure white or pure black if they dominate background (optional)
                 # if rgb == (255, 255, 255) or rgb == (0, 0, 0): continue
                 if len(colors) >= n_colors: break
                 colors.append(rgb)
            
        return colors
    except Exception as e:
        print(f"Color extraction failed for {image_path}: {e}")
        return []

def create_spec_sheet_v3(artwork, output_dir):
    # Sanitize title for filename
    clean_title = artwork.get('title', 'Untitled').replace('/', '-').replace('\\', '-')
    filename = f"{clean_title}_Sheet.pdf"
    filepath = os.path.join(output_dir, filename)
    
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # 1. Branding Header
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.75*inch, height - 0.75*inch, "ELLIOT SPENCER MORGAN")
    c.setFont("Helvetica", 10)
    c.drawString(0.75*inch, height - 0.95*inch, "Contemporary Abstract Art | Austin, TX")
    
    c.setLineWidth(1)
    c.line(0.75*inch, height - 1.1*inch, width - 0.75*inch, height - 1.1*inch)
    
    # 2. Layout Setup
    left_x = 0.75*inch
    right_x = 4.5*inch
    right_y = height - 1.5*inch
    
    # 3. Handle Image & Colors
    img_url = artwork.get('image_url')
    # Use id for cache uniqueness
    cache_name = f"{artwork['id']}_{clean_title}.jpg"
    
    local_img_path = None
    extracted_colors = []
    
    if img_url or artwork.get('title'):
        # Pass artwork title-based filename if needed
        local_img_path = download_image(img_url, cache_name)
        if local_img_path:
            extracted_colors = extract_dominant_colors(local_img_path)
    
    # --- RIGHT COLUMN (Visuals) ---
    
    # Draw Image
    if local_img_path:
        try:
            img_obj = Image.open(local_img_path)
            iw, ih = img_obj.size
            aspect = ih / float(iw)
            
            draw_w = 3.25*inch
            draw_h = draw_w * aspect
            
            # Cap height
            max_h = 3.5*inch
            if draw_h > max_h:
                draw_h = max_h
                draw_w = draw_h / aspect
                
            c.drawImage(local_img_path, right_x, right_y - draw_h, width=draw_w, height=draw_h)
            
            # Update Y for swatches based on image height
            swatch_start_y = (right_y - draw_h) - 0.4*inch
        except Exception as e:
             c.drawString(right_x, right_y, f"Image Error: {e}")
             swatch_start_y = right_y - 3*inch
    else:
        # Placeholder
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.rect(right_x, right_y - 3*inch, 3*inch, 3*inch)
        c.setFont("Helvetica", 9)
        c.drawCentredString(right_x + 1.5*inch, right_y - 1.5*inch, "Image Not Available")
        swatch_start_y = right_y - 3.4*inch

    # Draw Color Swatches
    c.setFont("Helvetica-Bold", 10)
    c.drawString(right_x, swatch_start_y, "VERIFIED PALETTE (Source Pixels)")
    
    swatch_y = swatch_start_y - 0.3*inch
    
    if len(extracted_colors) > 0:
        for i, rgb in enumerate(extracted_colors):
            r, g, b = rgb
            rn, gn, bn = r/255.0, g/255.0, b/255.0
            hex_val = rgb_to_hex(rgb)
            
            # Border for visibility
            c.setStrokeColorRGB(0.9, 0.9, 0.9)
            c.setFillColorRGB(rn, gn, bn)
            c.rect(right_x, swatch_y, 0.3*inch, 0.3*inch, fill=1, stroke=1)
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica", 8)
            # Display RGB and HEX
            c.drawString(right_x + 0.4*inch, swatch_y + 0.18*inch, f"RGB: {r}, {g}, {b}")
            c.setFont("Helvetica-Bold", 8)
            c.drawString(right_x + 0.4*inch, swatch_y + 0.05*inch, f"HEX: {hex_val}")
            
            swatch_y -= 0.4*inch
            if i >= 4: break # Max 5 colors to fit well
    else:
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(right_x, swatch_y, "No color data available.")

    # --- LEFT COLUMN (Info) ---
    y_pos = height - 1.5*inch
    
    # Title
    title = artwork.get('title', 'Untitled')
    c.setFont("Helvetica-Bold", 22)
    if len(title) > 25:
        c.setFont("Helvetica-Bold", 18)
    c.drawString(left_x, y_pos, title)
    y_pos -= 0.4*inch
    
    c.setFont("Helvetica", 12)
    # Medium
    medium = artwork.get('medium', 'Mixed Media')
    c.drawString(left_x, y_pos, medium)
    y_pos -= 0.2*inch
    # Year
    c.drawString(left_x, y_pos, str(artwork.get('year', '2025')))
    y_pos -= 0.5*inch
    
    # Dimensions Block
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_x, y_pos, "DIMENSIONS")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 11)
    dims = artwork.get('dimensions', 'Not Specified')
    c.drawString(left_x, y_pos, f"{dims}")
    y_pos -= 0.2*inch
    
    # Metric
    try:
        w = float(artwork.get('width', 0))
        h = float(artwork.get('height', 0))
        if w > 0 and h > 0:
            w_cm = w * 2.54
            h_cm = h * 2.54
            c.drawString(left_x, y_pos, f"({w_cm:.1f} cm x {h_cm:.1f} cm)")
            y_pos -= 0.2*inch
    except: pass
         
    y_pos -= 0.3*inch
    
    # Finishing
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_x, y_pos, "FINISHING & INSTALLATION")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 10)
    c.drawString(left_x, y_pos, f"Frame: {artwork.get('frame', 'Not Framed')}")
    y_pos -= 0.2*inch
    c.drawString(left_x, y_pos, f"Ready to Hang: {artwork.get('readyToHang', 'Yes')}")
    y_pos -= 0.2*inch
    c.drawString(left_x, y_pos, f"Packaging: {artwork.get('packaging', 'Standard')}")
    y_pos -= 0.2*inch
    c.drawString(left_x, y_pos, f"Authentication: Signed with COA")

    y_pos -= 0.4*inch
    
    # Styles
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_x, y_pos, "STYLES & MOOD")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 10)
    styles = artwork.get('styles', '')
    if len(styles) > 60:
        c.drawString(left_x, y_pos, styles[:60] + "-")
        y_pos -= 0.15*inch
        c.drawString(left_x, y_pos, styles[60:120])
    else:
        c.drawString(left_x, y_pos, styles)
        
    y_pos -= 0.5*inch
    
    # Availability
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_x, y_pos, "AVAILABILITY")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 10)
    if artwork.get('price'):
        c.drawString(left_x, y_pos, f"Price: ${artwork['price']}")
        y_pos -= 0.2*inch
    c.drawString(left_x, y_pos, "Shipping: Worldwide")
    y_pos -= 0.25*inch
    
    # Clickable Saatchi Art Link
    saatchi_url = artwork.get('saatchi_url')
    if saatchi_url:
        c.setFont("Helvetica-Bold", 10)
        c.setFillColorRGB(0.1, 0.4, 0.8) # Professional Blue
        link_text = "VIEW ON SAATCHI ART"
        text_width = c.stringWidth(link_text, "Helvetica-Bold", 10)
        c.drawString(left_x, y_pos, link_text)
        # Add the clickable area
        c.linkURL(saatchi_url, (left_x, y_pos - 2, left_x + text_width, y_pos + 10), relative=0)
        # Underline
        c.setStrokeColorRGB(0.1, 0.4, 0.8)
        c.setLineWidth(0.5)
        c.line(left_x, y_pos - 2, left_x + text_width, y_pos - 2)
        y_pos -= 0.2*inch
    
    c.setFillColorRGB(0, 0, 0)

    # QR Code (Absolute Bottom Right)
    qr_url = artwork.get('link') or artwork.get('saatchi_url')
    if qr_url:
        try:
            qr = qrcode.QRCode(box_size=10, border=1)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            qr_filename = f"qr_{artwork['id']}.png"
            img.save(qr_filename)
            
            c.drawImage(qr_filename, width - 1.8*inch, 0.8*inch, width=1.1*inch, height=1.1*inch)
            c.setFont("Helvetica", 7)
            c.drawCentredString(width - 1.25*inch, 0.7*inch, "Scan to View Details")
            os.remove(qr_filename)
        except Exception as e:
            print(f"QR Error: {e}")

    # Footer
    c.setLineWidth(0.5)
    c.setStrokeColorRGB(0.7, 0.7, 0.7)
    c.line(0.75*inch, 0.5*inch, width - 0.75*inch, 0.5*inch)
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColorRGB(0.4, 0.4, 0.4)
    c.drawString(0.75*inch, 0.35*inch, "© 2025 Elliot Spencer Morgan Art. All Rights Reserved.")
    c.drawRightString(width - 0.75*inch, 0.35*inch, "Spec sheet for professional trade use.")

    c.save()

if __name__ == "__main__":
    json_path = r'C:\sandbox\esm\artwork_data.json'
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
    else:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        out = r'C:\sandbox\esm\spec_sheets_v3'
        os.makedirs(out, exist_ok=True)
        
        print(f"Generating Enhanced V3 Sheets for {len(data)} items...")
        count = 0
        
        # Determine items to process
        # For full run, use data. For testing, use data[:10]
        items_to_process = data
        
        for item in items_to_process:
            print(f"   [{count+1}/{len(items_to_process)}] Processing: {item.get('title')}...")
            try:
                create_spec_sheet_v3(item, out)
                count += 1
            except Exception as e:
                print(f"   ❌ ERROR on {item.get('title')}: {e}")
                
        print(f"\n✅ Done. {count} sheets created in {out}")
