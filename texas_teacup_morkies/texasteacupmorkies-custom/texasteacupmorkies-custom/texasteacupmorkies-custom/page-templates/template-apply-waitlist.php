<?php
/*
Template Name: Apply / Waitlist
*/
get_header();

$form_url = trim( (string) ttp_get_option( 'waitlist_form_url', '' ) );
$embedded = $form_url;
if ( $embedded && strpos( $embedded, 'embedded=true' ) === false ) {
	$embedded = add_query_arg( array( 'embedded' => 'true' ), $embedded );
}

$puppy_id = absint( $_GET['puppy'] ?? 0 );
$puppy_title = $puppy_id ? get_the_title( $puppy_id ) : '';
?>
<section class="ttp-section">
	<div class="ttp-container">
		<header class="ttp-pagehead">
			<h1 class="ttp-h1"><?php the_title(); ?></h1>
			<?php if ( $puppy_title ) : ?><p class="ttp-muted">Applying for: <strong><?php echo esc_html( $puppy_title ); ?></strong></p><?php else : ?><p class="ttp-muted">Use this short form so we can keep your info organized and follow up quickly.</p><?php endif; ?>
		</header>

		<div class="ttp-section__grid">
			<div class="ttp-card">
				<h2 class="ttp-h2">What happens next</h2>
				<ol class="ttp-steps"><li>We review your form.</li><li>We text/call to confirm fit and timing.</li><li>Pickup at our home in Austin.</li></ol>
				<p class="ttp-muted">Deposit is not required to join the waitlist. After approval, you may place a refundable deposit to hold a specific puppy.</p>
			</div>

			<div class="ttp-card">
				<?php if ( $embedded ) : ?>
					<div class="ttp-embed ttp-embed--form"><iframe title="Application form" src="<?php echo esc_url( $embedded ); ?>" loading="lazy"></iframe></div>
				<?php else : ?>
					<p><strong>Form not set.</strong> Go to Appearance → TTP Settings and paste your Apply/Waitlist Google Form URL.</p>
				<?php endif; ?>
			</div>
		</div>
	</div>
</section>
<?php get_footer(); ?>
