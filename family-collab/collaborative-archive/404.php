<?php
/**
 * 404 template
 */
get_header(); ?>

<div class="error-container">
    <div class="error-content">
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>Sorry, the page you are looking for does not exist.</p>
        <div class="error-actions">
            <a href="<?php echo home_url('/'); ?>" class="button">Return to Dashboard</a>
            <a href="<?php echo get_post_type_archive_link('book_chapter'); ?>" class="button button-secondary">Browse Chapters</a>
        </div>
    </div>
</div>

<?php get_footer(); ?>