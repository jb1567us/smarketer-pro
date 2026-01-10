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

<header id="caviar-header-main" class="site-header">
    <div id="caviar-title-container" style="max-width: 550px; margin: 0 auto; padding: 0;">
        <h1 id="caviar-site-title">
            <a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home" style="font-size: 2.0rem; line-height: 1.2; display: block; letter-spacing: 1px;">
                <?php bloginfo( 'name' ); ?>
            </a>
        </h1>
        <div class="header-logo-injected" style="text-align: center; width: 100%; margin: 1rem 0 1.5rem 0;">
            <a href="<?php echo esc_url( home_url( '/' ) ); ?>" style="text-decoration:none; border:none;">
                <img src="https://elliotspencermorgan.com/logo.png" 
                     alt="<?php bloginfo( 'name' ); ?> Logo" 
                     width="299" height="234"
                     loading="eager" 
                     decoding="sync"
                     class="skip-lazy"
                     data-no-lazy="1"
                     style="width: 100%; max-width: 100%; height: auto; display: inline-block;" />
            </a>
        </div>
    </div>
</header>
