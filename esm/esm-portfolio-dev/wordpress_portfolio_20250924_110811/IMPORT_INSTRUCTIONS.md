
        # WordPress Portfolio Import Instructions
        
        ## Files Generated:
        1. `portfolio-export.xml` - WordPress WXR import file with posts and pages
        2. `wp-content/uploads/` - All downloaded artwork images
        3. `theme/esm-portfolio/` - Complete WordPress theme
        
        ## Structure:
        - **Homepage**: Static page with 3 artwork thumbnails per row (fixed width)
        - **Category Pages**: Dynamic pages showing filtered artwork posts with proper images
        - **About/Contact**: Static pages
        - **Navigation**: Includes category links to post archives
        
        ## Categories Found:
        Painting
        
        ## Installation Steps:
        
        1. **Install WordPress** at: https://lookoverhere.xyz/esm
        
        2. **Upload Images** via FTP to: `/wp-content/uploads/`
        
        3. **Import XML File**:
           - Go to WordPress Admin → Tools → Import
           - Install "WordPress Importer" plugin
           - Upload and import `portfolio-export.xml`
           - Assign authors to 'admin' user
        
        4. **Install Theme**:
           - Zip the `esm-portfolio` folder (inside the theme folder)
           - WordPress Admin → Appearance → Themes → Add New → Upload Theme
           - Upload the zip file and activate the theme
        
        5. **Set Up Navigation** (Already configured in theme):
           - The navigation menu automatically includes categories: Painting
           - Category links go to post archive pages
        
        6. **Set Homepage**:
           - Settings → Reading
           - "Your homepage displays" → "A static page"
           - Homepage: Select "Home"
        
        7. **Configure Permalinks**:
           - Settings → Permalinks
           - Choose "Post name" for clean URLs
           - Save changes
        
        ## Fixes Applied:
        - **Homepage grid width**: Now properly constrained to 1200px max width
        - **Category page images**: Fixed image display using custom fields
        - **Image URLs**: Stored in custom fields for reliable display
        
        ## Theme Features:
        - Consistent navigation across all pages
        - 3-column grid layout on homepage (properly constrained)
        - Fixed image display on category pages
        - Mobile-responsive design
        - Automatic category-based filtering
        
        ## Important Notes:
        - Zip the 'esm-portfolio' folder (not the parent 'theme' folder)
        - Images are now stored in custom fields for reliable display
        - All artwork thumbnails link directly to Saatchi Art
        