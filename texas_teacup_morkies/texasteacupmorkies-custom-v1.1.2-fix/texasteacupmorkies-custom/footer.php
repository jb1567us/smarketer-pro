<?php if ( ! defined( 'ABSPATH' ) ) { exit; } ?>
</main>

<footer class="ttp-footer">
	<div class="ttp-container ttp-footer__inner">
		<div>
			<div class="ttp-footer__brand"><?php echo esc_html( get_bloginfo('name') ); ?></div>
			<div class="ttp-footer__meta">Boutique, family-raised puppies in Austin, TX. Pickup is local.</div>
			<div class="ttp-footer__meta"><?php echo esc_html( ttp_get_option('price_anchor', '$2,000+') ); ?> · Socialized with people &amp; pets · House training in progress</div>
		</div>

		<div>
			<strong>Menu</strong>
			<?php
			wp_nav_menu( array(
				'theme_location' => 'footer',
				'container'      => false,
				'menu_class'     => 'ttp-footer__menu',
				'fallback_cb'    => '__return_false',
			) );
			?>
		</div>

		<div>
			<strong>Contact</strong>
			<div class="ttp-footer__meta">
				<?php $phone = (string) ttp_get_option('phone',''); ?>
				<?php if ( $phone ) : ?><div><a href="<?php echo esc_url( ttp_format_phone_href($phone) ); ?>"><?php echo esc_html($phone); ?></a></div><?php endif; ?>
				<?php $email = (string) ttp_get_option('email',''); ?>
				<?php if ( $email ) : ?><div><a href="mailto:<?php echo esc_attr($email); ?>"><?php echo esc_html($email); ?></a></div><?php endif; ?>
				<div><?php echo esc_html( ttp_get_option('pickup_address','3800 Manorwood Rd, Austin, TX 78723') ); ?></div>
			</div>
		</div>
	</div>
	<div class="ttp-container ttp-muted" style="padding:10px 18px 24px;font-size:13px;">© <?php echo esc_html( date('Y') ); ?> <?php echo esc_html( get_bloginfo('name') ); ?>. All rights reserved.</div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
