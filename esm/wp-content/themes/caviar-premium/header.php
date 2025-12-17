<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo( 'charset' ); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<!-- Fixed Hamburger (Always Visible) -->
<button class="hamburger-toggle" aria-label="Toggle Menu" onclick="document.querySelector('.nav-overlay').classList.toggle('active')">
    ☰
</button>

<!-- Navigation Overlay -->
<div class="nav-overlay">
    <?php
    wp_nav_menu( array(
        'theme_location' => 'primary',
        'container'      => false,
        'menu_class'     => '',
        'items_wrap'     => '%3$s', // Just the items, no UL helper 
        'depth'          => 1,
        'fallback_cb'    => false, // Do not fallback to listing pages if no menu assigned
    ) );
    ?>
    <!-- Hardcoded Fallback if menu is empty for dev -->
    <?php if ( ! has_nav_menu( 'primary' ) ) : ?>
        <a href="<?php echo home_url('/'); ?>">Portfolio</a>
        <a href="<?php echo home_url('/about/'); ?>">About</a>
        <a href="<?php echo home_url('/contact/'); ?>">Contact</a>
    <?php endif; ?>
</div>

<header id="masthead" class="site-header">
    <div class="wp-block-group">
        <div class="wp-block-site-title">
            <a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home">
                <?php bloginfo( 'name' ); ?>
            </a>
        </div>
    </div>
</header>
