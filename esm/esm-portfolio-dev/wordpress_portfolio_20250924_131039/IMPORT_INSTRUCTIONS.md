
        # WordPress Portfolio Import Instructions
        
        ## Files Generated:
        1. `portfolio-export.xml` - WordPress WXR import file with posts and pages
        2. `wp-content/uploads/` - All downloaded artwork images
        3. `theme/esm-portfolio/` - Complete WordPress theme
        
        ## Structure:
        - **Homepage**: Static page with responsive grid (3 cards per row on desktop, 2 on tablet, 1 on mobile)
        - **Category Pages**: Dynamic pages showing filtered artwork posts with responsive grid
        - **About/Contact**: Static pages
        - **Navigation**: Includes category links to post archives
        
        ## Categories Found:
        Collage, Installation, Painting, Printmaking, Sculpture
        
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
           - The navigation menu automatically includes categories: Collage, Installation, Painting, Printmaking, Sculpture
           - Category links go to post archive pages
        
        6. **Set Homepage**:
           - Settings → Reading
           - "Your homepage displays" → "A static page"
           - Homepage: Select "Home"
        
        7. **Configure Permalinks**:
           - Settings → Permalinks
           - Choose "Post name" for clean URLs
           - Save changes
        
        ## Responsive Grid Features:
        - **Desktop (1024px+)**: 3 cards per row
        - **Tablet (768px-1024px)**: 2 cards per row
        - **Mobile (<768px)**: 1 card per row
        - Hover effects on cards
        - Consistent spacing and styling
        
        ## Theme Features:
        - Consistent navigation across all pages
        - Responsive grid layout on homepage and category pages
        - Fixed image display with proper aspect ratios
        - Mobile-responsive design
        - Automatic category-based filtering
        
        ## Important Notes:
        - Zip the 'esm-portfolio' folder (not the parent 'theme' folder)
        - Images are stored in custom fields for reliable display
        - All artwork thumbnails link directly to Saatchi Art
        - The grid system is fully responsive and will adapt to different screen sizes
        