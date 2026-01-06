
        # WordPress Portfolio Import Instructions
        
        ## Files Generated:
        1. `portfolio-export.xml` - WordPress WXR import file with posts and pages
        2. `wp-content/uploads/` - All downloaded artwork images
        3. `theme/esm-portfolio/` - Complete WordPress theme
        
        ## New Mobile-Centric Design:
        - **Single column layout** - Perfect for mobile browsing
        - **Hamburger menu** - Clean navigation that pops up
        - **Transparent header** - No background color, appears on scroll
        - **Full-screen images** - Artworks take the full viewport height
        - **Google Fonts** - Playfair Display for headings, Lato for body
        - **No categories** - Clean, simplified display
        
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
        
        5. **Menu Setup**:
           - Go to **Appearance → Menus**
           - Create a menu with: Home, About, Contact
           - Set as primary menu
        
        6. **Set Homepage**:
           - Settings → Reading → "A static page"
           - Homepage: Select "Home"
        
        ## Design Features:
        - Click the hamburger icon (three lines) to open navigation
        - Header becomes visible when scrolling down
        - Each artwork takes full screen height
        - Clean typography with premium Google Fonts
        - Mobile-optimized touch interactions
        
        ## Important Notes:
        - This is a mobile-first design - test on mobile devices
        - No categories are displayed in the frontend
        - All artwork images link directly to Saatchi Art
        - The transparent header provides a clean, modern look
        