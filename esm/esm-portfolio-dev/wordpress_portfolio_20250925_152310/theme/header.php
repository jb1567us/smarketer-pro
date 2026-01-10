<?php
/**
 * The header for our theme
 */
?><!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="profile" href="https://gmpg.org/xfn/11">
    <?php wp_head(); ?>
</head>

<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="site-header">
    <div class="header-container">
        <div class="brand-container">
            <div class="site-title">
                <a href="<?php echo esc_url(home_url('/')); ?>">Elliot Spencer Morgan</a>
            </div>
            <div class="site-logo">
                <a href="<?php echo esc_url(home_url('/')); ?>" class="logo-link">
                    <img src="<?php echo esc_url(get_template_directory_uri() . '/wavesPainting_00.jpg'); ?>" alt="Elliot Spencer Morgan" class="site-logo-image">
                    <span class="sr-only">Elliot Spencer Morgan</span>
                </a>
            </div>
        </div>
        
        <button class="menu-toggle" aria-label="Toggle menu">
            <span class="hamburger"></span>
            <span class="sr-only">Menu</span>
        </button>
        
        <nav class="mobile-menu">
            <?php
            wp_nav_menu(array(
                'theme_location' => 'primary',
                'menu_class' => 'mobile-menu-list',
                'container' => false,
                'fallback_cb' => 'esm_portfolio_fallback_menu'
            ));
            ?>
        </nav>
    </div>
</header>

<main class="site-main">