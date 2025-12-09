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
    <div class="container">
        <div class="header-container">
            <div class="site-title">
                <a href="<?php echo esc_url(home_url('/')); ?>">Elliot Spencer Morgan</a>
            </div>
            
            <nav class="main-navigation">
                
        <ul class="main-menu">
            <li><a href="https://lookoverhere.xyz/esm">Home</a></li>
        <li><a href="https://lookoverhere.xyz/esm/category/painting">Painting</a></li>
            <li><a href="https://lookoverhere.xyz/esm/about">About</a></li>
            <li><a href="https://lookoverhere.xyz/esm/contact">Contact</a></li>
        </ul>
        
            </nav>
        </div>
    </div>
</header>

<main class="site-main">
