<?php
/*
Template Name: Referral Request
*/
get_header();

$form_url = trim( (string) ttp_get_option( 'referral_form_url', '' ) );
$embedded = $form_url;
if ( $embedded && strpos( $embedded, 'embedded=true' ) === false ) {
	$embedded = add_query_arg( array( 'embedded' => 'true' ), $embedded );
}
$disclosure = (string) ttp_get_option( 'commission_disclosure', '' );

$phone = ttp_get_option( 'phone', '' );
$call_href = $phone ? ttp_format_phone_href( $phone ) : '';
$text_href = $phone ? ttp_format_sms_href( $phone ) : '';
?>
<section class="ttp-section">
	<div class="ttp-container">
		<header class="ttp-pagehead">
			<h1 class="ttp-h1"><?php the_title(); ?></h1>
			<p class="ttp-muted">If we don’t have puppies available, submit a referral request. We keep our partner list private and review requests case-by-case.</p>
		</header>

		<div class="ttp-section__grid">
			<div class="ttp-card">
				<h2 class="ttp-h2">What to include</h2>
				<ul class="ttp-bullets"><li>City/state and pickup radius</li><li>Timing (ASAP vs flexible)</li><li>Budget range</li><li>What you’re hoping for (size, temperament, etc.)</li></ul>
				<p class="ttp-muted">Important: Please do your own due diligence with any third-party breeder.</p>
			</div>

			<div class="ttp-card">
				<?php if ( $embedded ) : ?>
					<div class="ttp-embed ttp-embed--form"><iframe title="Referral request form" src="<?php echo esc_url( $embedded ); ?>" loading="lazy"></iframe></div>
					<?php if ( $disclosure ) : ?><p class="ttp-disclosure"><?php echo esc_html( $disclosure ); ?></p><?php endif; ?>
				<?php else : ?>
					<p><strong>Referral form not added yet.</strong> For now, text or call and we’ll help if we can.</p>
					<div class="ttp-row"><?php if ( $text_href ) : ?><a class="ttp-btn" href="<?php echo esc_url( $text_href ); ?>">Text</a><?php endif; ?><?php if ( $call_href ) : ?><a class="ttp-btn ttp-btn--ghost" href="<?php echo esc_url( $call_href ); ?>">Call</a><?php endif; ?></div>
					<p class="ttp-muted">Add the Referral Google Form URL later in Appearance → TTP Settings.</p>
				<?php endif; ?>
			</div>
		</div>
	</div>
</section>
<?php get_footer(); ?>
