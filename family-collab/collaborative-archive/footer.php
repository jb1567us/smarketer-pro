</main><!-- .site-main -->

<footer class="site-footer">
    <div class="footer-container">
        <div class="footer-section">
            <h4>About the Project</h4>
            <p>The Collaborative Archive documents the life and work of José Sancha Padrós (1908-1994), Spanish artist, exile, and historical figure.</p>
            <p>This project brings together family history, artistic legacy, and historical research.</p>
        </div>
        
        <div class="footer-section">
            <h4>Quick Links</h4>
            <?php
            wp_nav_menu(array(
                'theme_location' => 'footer',
                'menu_class' => 'footer-menu',
                'container' => false,
                'fallback_cb' => false,
            ));
            ?>
        </div>
        
        <div class="footer-section">
            <h4>Research Areas</h4>
            <ul>
                <li><a href="<?php echo get_term_link('art-culture', 'narrative_arc'); ?>">Art & Culture</a></li>
                <li><a href="<?php echo get_term_link('political-life', 'narrative_arc'); ?>">The Political Life</a></li>
                <li><a href="<?php echo get_term_link('intelligence-file', 'narrative_arc'); ?>">The Intelligence File</a></li>
            </ul>
        </div>
    </div>
    
    <div class="footer-bottom">
        <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?>. All rights reserved.</p>
        <p>Built with the Collaborative Archive WordPress Theme</p>
    </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>