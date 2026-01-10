<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<a class="ttp-skip" href="#content">Skip to content</a>

<header class="ttp-header">
	<div class="ttp-container ttp-header__inner">
		<div class="ttp-brand">
			<?php if ( has_custom_logo() ) : ?>
				<?php the_custom_logo(); ?>
			<?php endif; ?>
			<a class="ttp-brand__text" href="<?php echo esc_url( home_url('/') ); ?>"><?php echo esc_html( get_bloginfo('name') ); ?></a>
		</div>

		<nav class="ttp-nav" aria-label="Primary">
			<?php
			wp_nav_menu( array(
				'theme_location' => 'primary',
				'container'      => false,
				'menu_class'     => 'ttp-nav__menu',
				'fallback_cb'    => '__return_false',
			) );
			?>
		</nav>

		<div class="ttp-header__actions">
			<?php echo do_shortcode('[ttp_lead_cta class="ttp-btn ttp-btn--sm" show_secondary="false"]'); ?>
			<button class="ttp-navtoggle" type="button" data-ttp-navtoggle aria-expanded="false" aria-controls="ttp-mobilemenu">
				<span class="screen-reader-text">Menu</span>
				<span class="ttp-navtoggle__bar"></span><span class="ttp-navtoggle__bar"></span><span class="ttp-navtoggle__bar"></span>
			</button>
		</div>
	</div>

	<div id="ttp-mobilemenu" class="ttp-mobilemenu" data-ttp-mobilemenu>
		<nav class="ttp-container" aria-label="Mobile">
			<?php
			wp_nav_menu( array(
				'theme_location' => 'primary',
				'container'      => false,
				'menu_class'     => 'ttp-mobilemenu__menu',
				'fallback_cb'    => '__return_false',
			) );
			?>
		</nav>
	</div>
</header>

<main id="content" class="ttp-main">
