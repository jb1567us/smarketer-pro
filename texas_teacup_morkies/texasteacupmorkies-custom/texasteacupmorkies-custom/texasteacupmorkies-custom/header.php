<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
$phone = ttp_get_option( 'phone', '' );
$call_href = $phone ? ttp_format_phone_href( $phone ) : '';
$text_href = $phone ? ttp_format_sms_href( $phone ) : '';
$primary_cta = ttp_get_option( 'lead_mode', 'referral' );
$has_available = (bool) ttp_get_available_puppy_id();
?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<a class="ttp-skip" href="#content"><?php esc_html_e( 'Skip to content', 'ttp' ); ?></a>

<header class="ttp-header">
	<div class="ttp-container ttp-header__inner">
		<div class="ttp-brand">
			<?php if ( has_custom_logo() ) { the_custom_logo(); } else { ?>
				<a class="ttp-brand__text" href="<?php echo esc_url( home_url( '/' ) ); ?>"><?php bloginfo( 'name' ); ?></a>
			<?php } ?>
		</div>

		<nav class="ttp-nav" aria-label="<?php esc_attr_e( 'Primary menu', 'ttp' ); ?>">
			<?php wp_nav_menu( array('theme_location'=>'primary','container'=>false,'menu_class'=>'ttp-nav__menu','fallback_cb'=>'__return_false','depth'=>2) ); ?>
		</nav>

		<div class="ttp-header__actions">
			<?php if ( $phone && $text_href ) : ?><a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( $text_href ); ?>"><?php esc_html_e( 'Text', 'ttp' ); ?></a><?php endif; ?>
			<?php if ( $phone && $call_href ) : ?><a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( $call_href ); ?>"><?php esc_html_e( 'Call', 'ttp' ); ?></a><?php endif; ?>

			<?php
			$cta_url = '';
			$cta_label = '';
			if ( $has_available ) {
				$puppy_id = ttp_get_available_puppy_id();
				$cta_url = ttp_get_apply_url_for_puppy( $puppy_id );
				$cta_label = __( 'Apply', 'ttp' );
			} else {
				if ( 'waitlist' === $primary_cta ) {
					$apply_page = absint( ttp_get_option( 'apply_page_id', 0 ) );
					$cta_url = $apply_page ? get_permalink( $apply_page ) : (string) ttp_get_option( 'waitlist_form_url', '' );
					$cta_label = __( 'Waitlist', 'ttp' );
				} else {
					$ref_page = absint( ttp_get_option( 'referral_page_id', 0 ) );
					$cta_url = $ref_page ? get_permalink( $ref_page ) : (string) ttp_get_option( 'referral_form_url', '' );
					$cta_label = __( 'Referral', 'ttp' );
				}
			}
			if ( $cta_url ) : ?><a class="ttp-btn" href="<?php echo esc_url( $cta_url ); ?>"><?php echo esc_html( $cta_label ); ?></a><?php endif; ?>
		</div>

		<button class="ttp-navtoggle" aria-expanded="false" aria-controls="ttp-mobilemenu">
			<span class="ttp-navtoggle__bar"></span><span class="ttp-navtoggle__bar"></span><span class="ttp-navtoggle__bar"></span>
			<span class="screen-reader-text"><?php esc_html_e( 'Menu', 'ttp' ); ?></span>
		</button>
	</div>

	<div id="ttp-mobilemenu" class="ttp-mobilemenu" hidden>
		<div class="ttp-container">
			<?php wp_nav_menu( array('theme_location'=>'primary','container'=>false,'menu_class'=>'ttp-mobilemenu__menu','fallback_cb'=>'__return_false','depth'=>2) ); ?>
		</div>
	</div>
</header>

<main id="content" class="ttp-main">
