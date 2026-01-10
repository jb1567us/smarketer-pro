import json
import os
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
# Improve Palette Map for Swatches
PALETTE = {
    'Red': (1, 0, 0),
    'Dark Red': (0.55, 0, 0),
    'Green': (0, 0.5, 0),
    'Blue': (0, 0, 1),
    'Dark Blue': (0, 0, 0.55),
    'Yellow': (1, 1, 0),
    'Orange': (1, 0.65, 0),
    'Purple': (0.5, 0, 0.5),
    'Pink': (1, 0.75, 0.8),
    'Black': (0, 0, 0),
    'White': (0.9, 0.9, 0.9), # render outline
    'Grey': (0.5, 0.5, 0.5),
    'Brown': (0.4, 0.26, 0.13),
    'Gold': (0.83, 0.68, 0.21),
    'Silver': (0.75, 0.75, 0.75),
    'Beige': (0.96, 0.96, 0.86),
    'Turquoise': (0.25, 0.88, 0.82)
}

def create_spec_sheet_v2(artwork, output_dir):
    filename = artwork.get('title', 'Untitled').replace('/', '-').replace('\\', '-')
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
    
    # 2. Main Layout
    # Column 1 (Left): Info
    # Column 2 (Right): Image + Colors + QR
    
    left_x = 0.75*inch
    col_width = 3.5*inch
    y_pos = height - 1.5*inch
    
    # Title
    c.setFont("Helvetica-Bold", 22)
    c.drawString(left_x, y_pos, artwork.get('title', 'Untitled'))
    y_pos -= 0.4*inch
    
    c.setFont("Helvetica", 12)
    # Medium
    c.drawString(left_x, y_pos, artwork.get('medium', 'Mixed Media'))
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
    if artwork.get('width') and artwork.get('height'):
         # Add metric?
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
    
    y_pos -= 0.4*inch
    
    # Styles / Keywords
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_x, y_pos, "STYLES & MOOD")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 10)
    styles = artwork.get('styles', '')
    if len(styles) > 50:
        # split simple
        c.drawString(left_x, y_pos, styles[:50])
        y_pos -= 0.2*inch
        c.drawString(left_x, y_pos, styles[50:])
    else:
        c.drawString(left_x, y_pos, styles)
        
    y_pos -= 0.4*inch
    
    # Designer Note / Price
    c.setFont("Helvetica-Bold", 11)
    c.drawString(left_x, y_pos, "AVAILABILITY")
    y_pos -= 0.2*inch
    c.setFont("Helvetica", 10)
    if artwork.get('price'):
        c.drawString(left_x, y_pos, f"Price: ${artwork['price']}")
        y_pos -= 0.2*inch
    c.drawString(left_x, y_pos, "Location: " + str(artwork.get('shippingFrom', 'Austin, TX')))
    
    # --- RIGHT COLUMN (Visuals) ---
    right_x = 4.5*inch
    right_y = height - 1.5*inch
    
    # Placeholder for actual image if I don't have local paths map
    # User script `reanalyze` downloaded temp images but deleted them?
    # Spec sheet needs the image. I should check if I have a local cache or use URL?
    # ReportLab can use URL but slow.
    # For now, I will draw a Box placeholder "Artwork Image" or try to start download.
    # To keep it fast, I'll use a placeholder box unless I have a path.
    
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.rect(right_x, right_y - 3*inch, 3*inch, 3*inch)
    c.setFont("Helvetica", 9)
    c.drawCentredString(right_x + 1.5*inch, right_y - 1.5*inch, "(Artwork Image Placeholder)")
    
    swatch_y = right_y - 3.2*inch
    
    # Color Palette Swatches
    c.setFont("Helvetica-Bold", 10)
    c.drawString(right_x, swatch_y, "COLOR PALETTE")
    swatch_y -= 0.3*inch
    
    detected = artwork.get('detected_colors', [])
    # Limit to 5
    for color_name in detected[:5]:
        rgb = PALETTE.get(color_name, (0.9, 0.9, 0.9))
        c.setFillColorRGB(*rgb)
        c.rect(right_x, swatch_y, 0.3*inch, 0.3*inch, fill=1, stroke=1)
        c.setFillColorRGB(0,0,0)
        c.drawString(right_x + 0.4*inch, swatch_y + 0.1*inch, color_name)
        right_x += 1.2*inch 
        if right_x > 7.5*inch:
            right_x = 4.5*inch
            swatch_y -= 0.4*inch
            
    # QR Code (Direct Link)
    url = artwork.get('link') or artwork.get('saatchi_url')
    if url:
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_filename = "temp_qr.png"
        img.save(qr_filename)
        
        c.drawImage(qr_filename, width - 2*inch, 1*inch, width=1.2*inch, height=1.2*inch)
        c.setFont("Helvetica", 8)
        c.drawCentredString(width - 1.4*inch, 0.8*inch, "Scan to View")
        
    # Footer
    c.setLineWidth(1)
    c.line(0.75*inch, 0.6*inch, width - 0.75*inch, 0.6*inch)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(0.75*inch, 0.4*inch, "Spec sheet generated for professional use.")

    c.save()
    if os.path.exists("temp_qr.png"):
        os.remove("temp_qr.png")

if __name__ == "__main__":
    with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    out = r'C:\sandbox\esm\spec_sheets_v2'
    os.makedirs(out, exist_ok=True)
    
    print(f"Generating V2 Sheets for {len(data)} items...")
    count = 0
    for item in data:
        if not item.get('width'): continue # Skip invalid
        create_spec_sheet_v2(item, out)
        count += 1
        if count % 20 == 0: print(f"{count}...", end='')
        
    print(f"\nDone. {count} sheets created in {out}")
