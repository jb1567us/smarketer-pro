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

def download_image(url, local_filename):
    """Downloads image to cache if not exists. Tries fallback path."""
    path = os.path.join(IMAGE_CACHE_DIR, local_filename)
    if os.path.exists(path):
        # Optional: check if file is valid image?
        if os.path.getsize(path) > 1000: # sanity check
            return path
        else:
            os.remove(path) # corrupt/empty
    
    # Logic to Try:
    # 1. User's specific high-res folder (Prioritized as per request)
    # 2. Original URL
    
    # Construct fallback URL
    filename = url.split('/')[-1]
    fallback_url = f"https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/{filename}"
    
    # List of attempts
    attempts = [fallback_url, url]
    
    for try_url in attempts:
        try:
            # check headers first
            h = requests.head(try_url, timeout=5)
            if h.status_code == 200 and 'image' in h.headers.get('content-type', ''):
                # Download
                response = requests.get(try_url, timeout=15)
                if response.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {try_url}")
                    return path
            elif h.status_code == 404:
                continue # Try next
                
        except Exception as e:
            print(f"Failed to check {try_url}: {e}")
            
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
        quantized = img.quantize(colors=n_colors, method=1)
        
        # Get palette
        palette = quantized.getpalette() # [r, g, b, r, g, b, ...]
        
        # Extract tuples
        colors = []
        if palette:
            # palette length is often 768 (256 RGBs), but we only care about the first n_colors used
            # Actually getpalette returns the full 256 entries usually.
            # We should look at getcolors on the quantized image to see which are actually used, 
            # OR just take the palette entries corresponding to the indices used.
            # Simpler: convert quantized image BACK to RGB and get unique colors?
            # Or just take top unique colors from the image directly?
            
            # Better approach with PIL:
            # 1. Resize small
            # 2. Get colors (count, pixel)
            # 3. Sort by count
            
            # Re-open/resize to ensure we are scanning rgb
            # img was already RGB.
            # img.getcolors giving None means > 256 colors.
            # So reduce colors first.
            
            q_img = img.quantize(colors=n_colors + 2) # get a few more to filter background
            q_img = q_img.convert('RGB')
            # Now get colors (should be few)
            counts = q_img.getcolors(maxcolors=256)
            if counts:
                # Sort by count desc
                counts.sort(key=lambda x: x[0], reverse=True)
                
                for count, rgb in counts:
                     # Filter out near-white or near-black if desired?
                     # rgb is (r,g,b)
                     if len(colors) >= n_colors: break
                     colors.append(rgb)
            
        return colors
    except Exception as e:
        print(f"Color extraction failed for {image_path}: {e}")
        return []

def create_spec_sheet_v3(artwork, output_dir):
    filename = artwork.get('title', 'Untitled').replace('/', '-').replace('\\', '-')
    # Ensure filename matches V2 convention strictly
    filename = f"{filename}_Sheet.pdf"
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
    # Use title as reliable filename base for cache
    cache_name = f"{artwork['id']}_{filename.replace('.pdf', '.jpg')}"
    
    local_img_path = None
    extracted_colors = []
    
    if img_url:
        local_img_path = download_image(img_url, cache_name)
        if local_img_path:
            extracted_colors = extract_dominant_colors(local_img_path)
    
    # --- RIGHT COLUMN (Visuals) ---
    
    # Draw Image
    if local_img_path:
        try:
            # Fit image in 3x3 inch box
            # Use ReportLab's drawImage
            # Preserve aspect ratio
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
            # Normalize for ReportLab (0-1)
            r, g, b = rgb
            rn, gn, bn = r/255.0, g/255.0, b/255.0
            
            c.setFillColorRGB(rn, gn, bn)
            c.rect(right_x, swatch_y, 0.3*inch, 0.3*inch, fill=1, stroke=1)
            
            c.setFillColorRGB(0, 0, 0)
            c.setFont("Helvetica", 8)
            c.drawString(right_x + 0.4*inch, swatch_y + 0.1*inch, f"R:{r} G:{g} B:{b}")
            
            # Stack vertically for readability since we have text
            swatch_y -= 0.35*inch
            
            if i >= 5: break # Max 6 colors
    else:
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(right_x, swatch_y, "No color data available.")

    # --- LEFT COLUMN (Info) ---
    y_pos = height - 1.5*inch
    
    # Title
    c.setFont("Helvetica-Bold", 22)
    title = artwork.get('title', 'Untitled')
    # Wrap title if too long
    if len(title) > 20:
        c.setFont("Helvetica-Bold", 18)
    c.drawString(left_x, y_pos, title)
    y_pos -= 0.4*inch
    
    c.setFont("Helvetica", 12)
    # Medium
    medium = artwork.get('medium', 'Mixed Media')
    c.drawString(left_x, y_pos, medium)
    y_pos -= 0.2*inch
    # Year
    c.drawString(left_x, y_pos, artwork.get('year', '2025'))
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
    if artwork.get('width') and artwork.get('height'):
         try:
             w_cm = float(artwork['width']) * 2.54
             h_cm = float(artwork['height']) * 2.54
             c.drawString(left_x, y_pos, f"({w_cm:.1f} cm x {h_cm:.1f} cm)")
             y_pos -= 0.2*inch
         except: pass
         
    y_pos -= 0.3*inch
    
    # Finishing
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_x, y_pos, "FINISHING & INSTALLATION")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 10)
    c.drawString(left_x, y_pos, f"Frame: {artwork.get('frame', 'Unframed')}")
    y_pos -= 0.2*inch
    c.drawString(left_x, y_pos, f"Ready to Hang: {artwork.get('readyToHang', 'Yes')}")
    y_pos -= 0.2*inch
    c.drawString(left_x, y_pos, f"Packaging: {artwork.get('packaging', 'Standard')}")
    y_pos -= 0.2*inch
    c.drawString(left_x, y_pos, f"Sign: Signed with COA")

    y_pos -= 0.4*inch
    
    # Styles
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_x, y_pos, "STYLES & MOOD")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 10)
    styles = artwork.get('styles', '')
    if len(styles) > 50:
        c.drawString(left_x, y_pos, styles[:50] + "-")
        y_pos -= 0.15*inch
        c.drawString(left_x, y_pos, styles[50:100])
    else:
        c.drawString(left_x, y_pos, styles)
        
    y_pos -= 0.4*inch
    
    # Availability
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_x, y_pos, "AVAILABILITY")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 10)
    if artwork.get('price'):
        c.drawString(left_x, y_pos, f"Price: ${artwork['price']}")
        y_pos -= 0.2*inch
    c.drawString(left_x, y_pos, "Location: " + str(artwork.get('shippingFrom', 'Austin, TX')))

    # QR Code (Absolute Bottom Right)
    url = artwork.get('link') or artwork.get('saatchi_url')
    if url:
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_filename = f"qr_{artwork['id']}.png"
        img.save(qr_filename)
        
        c.drawImage(qr_filename, width - 2*inch, 1*inch, width=1.2*inch, height=1.2*inch)
        c.setFont("Helvetica", 8)
        c.drawCentredString(width - 1.4*inch, 0.8*inch, "Scan to View")
        os.remove(qr_filename)

    # Footer
    c.setLineWidth(1)
    c.line(0.75*inch, 0.6*inch, width - 0.75*inch, 0.6*inch)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(0.75*inch, 0.4*inch, "Spec sheet generated for professional use.")

    c.save()

if __name__ == "__main__":
    with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    out = r'C:\sandbox\esm\spec_sheets_v3'
    os.makedirs(out, exist_ok=True)
    
    print(f"Generating V3 Sheets (with Image Download) for {len(data)} items...")
    count = 0
    for item in data:
        # if not item.get('width'): continue
        # Debug: Run for first 5 first to test
        # if count >= 5: break 
        print(f"Processing {item.get('title')}...")
        try:
            create_spec_sheet_v3(item, out)
            count += 1
        except Exception as e:
            print(f"ERROR on {item.get('title')}: {e}")
            
    print(f"\nDone. {count} sheets created in {out}")
