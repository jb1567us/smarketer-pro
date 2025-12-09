class WordPressPortfolioGenerator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        })
        self.artworks = []
    
    def create_directory_structure(self):
        """Create directories for WordPress export"""
        # Method implementation
    
    def get_artwork_urls(self):
        """Return the list of artwork URLs"""
        # Method implementation
    
    def extract_artwork_data(self, url):
        """Extract detailed artwork information from Saatchi Art page"""
        # Method implementation
    
    # ... all other methods should be properly indented at this level
    
    def generate_wordpress_xml(self):
        """Generate WordPress WXR export file with detailed artwork information"""
        # Make sure this method is properly indented
        # Create XML structure as string with CDATA placeholders
        xml_template = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
    <title>Art Portfolio</title>
    <link>https://yourportfolio.com</link>
    <description>Artwork Portfolio</description>
    {terms}
    {items}
</channel>
</rss>'''
        
        # Generate terms XML
        terms_xml = ""
        for i, cat in enumerate(['Painting', 'Sculpture', 'Collage', 'Printmaking', 'Installation', 'Artwork'], 1):
            terms_xml += f'''
            <wp:term>
                <wp:term_id>{i}</wp:term_id>
                <wp:category_nicename>{cat.lower()}</wp:category_nicename>
                <wp:category_parent></wp:category_parent>
                <wp:cat_name>{cat}</wp:cat_name>
            </wp:term>'''
        
        # Generate items XML
        items_xml = ""
        for i, artwork in enumerate(self.artworks, 1):
            if artwork.get('images'):
                items_xml += self.create_post_xml_string(artwork, i)
        
        # Format the final XML
        final_xml = xml_template.format(terms=terms_xml, items=items_xml)
        
        # Save XML file
        xml_path = os.path.join(self.export_dir, "portfolio-export.xml")
        with open(xml_path, 'w', encoding='utf-8') as f:
            f.write(final_xml)
        
        print(f"✅ WordPress export file created: {xml_path}")
    
    def create_post_xml_string(self, artwork, post_id):
        """Create WordPress post as XML string with CDATA sections"""
        content_text = self.generate_wordpress_content(artwork)
        excerpt_text = artwork['description'][:200] + "..." if artwork['description'] else ""
        
        post_xml = f'''
        <item>
            <title>{artwork['title']}</title>
            <link>https://yourportfolio.com/artwork/{self.sanitize_filename(artwork['title'])}</link>
            <pubDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>
            <dc:creator>admin</dc:creator>
            <content:encoded><![CDATA[{content_text}]]></content:encoded>
            <excerpt:encoded><![CDATA[{excerpt_text}]]></excerpt:encoded>
            <wp:post_id>{post_id}</wp:post_id>
            <wp:post_date>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</wp:post_date>
            <wp:post_type>post</wp:post_type>
            <wp:status>publish</wp:status>
            <wp:post_parent>0</wp:post_parent>
            <wp:menu_order>0</wp:menu_order>
            <category domain="category" nicename="{self.determine_category(artwork['medium']).lower()}">{self.determine_category(artwork['medium'])}</category>
        </item>'''
        
        return post_xml
    
    # ... continue with the rest of your methods
    
    def run(self):
        """Main function to generate WordPress portfolio"""
        # Method implementation

# Make sure this is at the top level (not indented)
def main():
    """Main function"""
    try:
        generator = WordPressPortfolioGenerator()
        generator.run()
    except KeyboardInterrupt:
        print("\n⏹️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()