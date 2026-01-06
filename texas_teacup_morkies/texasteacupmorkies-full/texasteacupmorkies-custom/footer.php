<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }
$business_name = ttp_get_option( 'business_name', get_bloginfo( 'name' ) );
$phone = ttp_get_option( 'phone', '' );
$email = ttp_get_option( 'email', '' );
$addr1 = ttp_get_option( 'address_line1', '' );
$city = ttp_get_option( 'address_city', '' );
$state = ttp_get_option( 'address_state', '' );
$zip = ttp_get_option( 'address_zip', '' );
?>
</main>

<footer class="ttp-footer">
	<div class="ttp-container ttp-footer__inner">
		<div class="ttp-footer__col">
			<div class="ttp-footer__brand"><?php echo esc_html( $business_name ); ?></div>
			<?php if ( $addr1 || $city || $state || $zip ) : ?><div class="ttp-footer__meta"><?php echo esc_html( trim( $addr1 . ', ' . $city . ', ' . $state . ' ' . $zip ) ); ?></div><?php endif; ?>
			<?php if ( $phone ) : ?><div class="ttp-footer__meta"><a href="<?php echo esc_url( ttp_format_phone_href( $phone ) ); ?>"><?php echo esc_html( $phone ); ?></a></div><?php endif; ?>
			<?php if ( $email ) : ?><div class="ttp-footer__meta"><a href="<?php echo esc_url( 'mailto:' . $email ); ?>"><?php echo esc_html( $email ); ?></a></div><?php endif; ?>
		</div>

		<div class="ttp-footer__col">
			<?php wp_nav_menu( array('theme_location'=>'footer','container'=>false,'menu_class'=>'ttp-footer__menu','fallback_cb'=>'__return_false') ); ?>
		</div>

		<div class="ttp-footer__col">
			<div class="ttp-footer__meta">© <?php echo esc_html( date('Y') ); ?> <?php echo esc_html( $business_name ); ?></div>
			<div class="ttp-footer__meta"><?php esc_html_e( 'Austin, Texas', 'ttp' ); ?></div>
		</div>
	</div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
