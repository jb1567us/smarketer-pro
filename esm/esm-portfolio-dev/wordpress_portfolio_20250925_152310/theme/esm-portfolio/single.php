<?php
/**
 * The template for displaying single posts
 * Note: This template redirects to Saatchi Art
 */
get_header();

// Redirect to Saatchi Art
$saatchi_url = get_post_meta(get_the_ID(), 'saatchi_url', true);
if ($saatchi_url) {
    wp_redirect($saatchi_url, 301);
    exit;
}
?>

<!-- Fallback content -->
<div class="container">
    <article>
        <h1><?php the_title(); ?></h1>
        <p>Redirecting to Saatchi Art...</p>
    </article>
</div>

<?php get_footer(); ?>
