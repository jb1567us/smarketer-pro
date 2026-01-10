import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def create_spec_sheet(artwork, output_dir):
    """Create a professional spec sheet PDF for an artwork"""
    
    # Clean filename
    filename = artwork.get('title', 'Untitled').replace('/', '-').replace('\\', '-')
    filename = f"{filename}_spec.pdf"
    filepath = os.path.join(output_dir, filename)
    
    # Create PDF
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawString(1*inch, height - 1*inch, "ARTWORK SPECIFICATION")
    
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, height - 1.3*inch, "Elliot Spencer Morgan | Contemporary Abstract Art")
    
    # Line separator
    c.setStrokeColor(colors.black)
    c.setLineWidth(2)
    c.line(1*inch, height - 1.5*inch, width - 1*inch, height - 1.5*inch)
    
    # Artwork Title
    c.setFont("Helvetica-Bold", 18)
    title = artwork.get('title', 'Untitled')
    c.drawString(1*inch, height - 2*inch, title)
    
    # Specifications section
    y_position = height - 2.5*inch
    line_height = 0.25*inch
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_position, "SPECIFICATIONS")
    y_position -= line_height
    
    c.setFont("Helvetica", 11)
    
    # Dimensions
    dims = artwork.get('dimensions', 'Not specified')
    c.drawString(1.2*inch, y_position, f"Dimensions: {dims}")
    y_position -= line_height
    
    # Medium
    medium = artwork.get('mediumsDetailed') or artwork.get('medium', 'Mixed Media')
    c.drawString(1.2*inch, y_position, f"Medium: {medium}")
    y_position -= line_height
    
    # Year
    year = artwork.get('year', 'N/A')
    c.drawString(1.2*inch, y_position, f"Year: {year}")
    y_position -= line_height
    
    # Frame
    frame = artwork.get('frame', 'Not Framed')
    c.drawString(1.2*inch, y_position, f"Frame: {frame}")
    y_position -= line_height
    
    # Ready to Hang
    ready = artwork.get('readyToHang', 'Not Applicable')
    c.drawString(1.2*inch, y_position, f"Ready to Hang: {ready}")
    y_position -= line_height * 1.5
    
    # Shipping section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_position, "SHIPPING & PACKAGING")
    y_position -= line_height
    
    c.setFont("Helvetica", 11)
    packaging = artwork.get('packaging', 'Ships carefully packaged')
    c.drawString(1.2*inch, y_position, f"Packaging: {packaging}")
    y_position -= line_height
    
    ships_from = artwork.get('shippingFrom', 'United States')
    c.drawString(1.2*inch, y_position, f"Ships From: {ships_from}")
    y_position -= line_height * 1.5
    
    # Style section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_position, "STYLE & THEME")
    y_position -= line_height
    
    c.setFont("Helvetica", 11)
    styles = artwork.get('styles', 'Abstract')
    # Wrap long styles text
    if len(styles) > 70:
        styles_short = styles[:70] + "..."
    else:
        styles_short = styles
    c.drawString(1.2*inch, y_position, f"Styles: {styles_short}")
    y_position -= line_height * 1.5
    
    # Purchase section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, y_position, "AVAILABILITY")
    y_position -= line_height
    
    c.setFont("Helvetica", 11)
    saatchi = artwork.get('saatchi_url', '')
    if saatchi:
        c.drawString(1.2*inch, y_position, "View on Saatchi Art:")
        y_position -= line_height * 0.8
        c.setFillColor(colors.blue)
        c.drawString(1.2*inch, y_position, saatchi)
        c.setFillColor(colors.black)
    y_position -= line_height * 1.5
    
    # Footer - Contact Info
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1*inch, 1.5*inch, "TRADE INQUIRIES")
    c.setFont("Helvetica", 9)
    c.drawString(1*inch, 1.3*inch, "For designer pricing and availability, please contact:")
    c.drawString(1*inch, 1.1*inch, "Website: elliotspencermorgan.com")
    c.drawString(1*inch, 0.9*inch, "Trade Portal: elliotspencermorgan.com/trade")
    
    # Bottom line
    c.setLineWidth(1)
    c.line(1*inch, 0.7*inch, width - 1*inch, 0.7*inch)
    
    c.setFont("Helvetica", 8)
    c.drawString(1*inch, 0.5*inch, "© Elliot Spencer Morgan | All Rights Reserved")
    
    # Save PDF
    c.save()
    return filepath

# Main execution
if __name__ == "__main__":
    # Load artwork data
    with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
        artworks = json.load(f)
    
    # Create output directory
    output_dir = r'C:\sandbox\esm\spec_sheets'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating spec sheets for {len(artworks)} artworks...")
    
    generated = 0
    errors = 0
    
    for artwork in artworks:
        if not artwork.get('saatchi_url'):
            continue
            
        try:
            filepath = create_spec_sheet(artwork, output_dir)
            generated += 1
            if generated % 10 == 0:
                print(f"  Generated {generated} spec sheets...")
        except Exception as e:
            errors += 1
            print(f"  Error for {artwork.get('title')}: {e}")
    
    print(f"\n=== COMPLETE ===")
    print(f"Generated: {generated} spec sheets")
    print(f"Errors: {errors}")
    print(f"Location: {output_dir}")
