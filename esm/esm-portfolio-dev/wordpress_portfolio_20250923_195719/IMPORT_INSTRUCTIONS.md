
        # WordPress Portfolio Import Instructions
        
        ## Files Generated:
        1. `portfolio-export.xml` - WordPress WXR import file with 3 pages
        2. `wp-content/uploads/` - All downloaded artwork images
        3. `theme/` - Custom WordPress theme
        
        ## Installation Steps:
        
        1. **Install WordPress** at: https://lookoverhere.xyz/esm
        
        2. **Upload Images** via FTP to: `/wp-content/uploads/`
        
        3. **Import XML File**:
           - Go to WordPress Admin → Tools → Import
           - Install "WordPress Importer" plugin
           - Upload and import `portfolio-export.xml`
           - Assign authors to 'admin' user
        
        4. **Install Theme**:
           - Zip the `theme/` folder
           - WordPress Admin → Appearance → Themes → Add New → Upload Theme
           - Upload and activate the theme
        
        5. **Set Up Navigation**:
           - Appearance → Menus
           - Create menu "Primary Navigation" with:
             * Home (custom link to https://lookoverhere.xyz/esm)
             * About (page link)
             * Contact (page link)
           - Set menu location to "Primary Menu"
        
        6. **Set Homepage** (should be auto-set):
           - Settings → Reading
           - "Your homepage displays" should be "A static page"
           - Homepage: "Home"
        
        ## Features:
        - Homepage with categorized artwork grid
        - Clickable images linking to Saatchi Art pages
        - About page with artist bio
        - Contact page with information
        - Mobile-responsive design
        - Fast loading with minimal code
        