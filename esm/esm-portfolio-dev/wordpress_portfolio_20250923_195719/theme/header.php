
        <!DOCTYPE html>
        <html <?php language_attributes(); ?>>
        <head>
            <meta charset="<?php bloginfo('charset'); ?>">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title><?php bloginfo('name'); ?> - <?php bloginfo('description'); ?></title>
            <?php wp_head(); ?>
        </head>
        <body <?php body_class(); ?>>
        
        <header class="site-header">
            <div class="container">
                <div class="header-container">
                    <div class="site-title">
                        <a href="<?php echo home_url(); ?>">Elliot Spencer Morgan</a>
                    </div>
                    <nav class="main-navigation">
                        <?php
                        wp_nav_menu(array(
                            'theme_location' => 'primary',
                            'menu_class' => 'nav-menu',
                            'container' => false,
                            'fallback_cb' => false
                        ));
                        ?>
                    </nav>
                </div>
            </div>
        </header>
        
        <main class="site-main">
        