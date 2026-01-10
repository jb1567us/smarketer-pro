<?php
/*
Template Name: Apply / Waitlist
*/
get_header();
$waitlist_url = (string) ttp_get_option('waitlist_form_url', '');
$price_anchor = (string) ttp_get_option('price_anchor', '$2,000+');
$puppy_id = isset($_GET['puppy_id']) ? absint($_GET['puppy_id']) : 0;
$puppy_title = $puppy_id ? get_the_title($puppy_id) : '';
?>
<div class="ttp-container ttp-section">
	<header class="ttp-pagehead">
		<h1 class="ttp-h1"><?php the_title(); ?></h1>
		<p class="ttp-muted">Use this when you’re opening the waitlist (typically ~40 days before birth). City + State should be required on the form.</p>
	</header>

	<?php while ( have_posts() ) : the_post(); ?>
		<?php if ( trim( get_the_content() ) ) : ?>
			<div class="ttp-card ttp-card--wide" style="margin-bottom:16px;"><div class="ttp-prose"><?php the_content(); ?></div></div>
		<?php endif; ?>
	<?php endwhile; ?>

	<div style="display:grid;grid-template-columns:1.1fr .9fr;gap:16px;">
		<div class="ttp-card ttp-card--wide">
			<h2 class="ttp-h2">Application</h2>
			<?php if ( $puppy_title ) : ?><p class="ttp-muted">You’re applying for: <strong><?php echo esc_html($puppy_title); ?></strong></p><?php endif; ?>

			<?php if ( $waitlist_url ) : ?>
				<div class="ttp-embed ttp-embed--form"><iframe title="Waitlist form" loading="lazy" src="<?php echo esc_url($waitlist_url); ?>"></iframe></div>
			<?php else : ?>
				<p class="ttp-muted">Add your Google Form URL in <strong>Appearance → TTP Settings</strong>.</p>
			<?php endif; ?>
		</div>

		<div class="ttp-card">
			<h2 class="ttp-h2">Before you submit</h2>
			<ul class="ttp-prose">
				<li><strong>Pickup is local</strong> in Austin, TX.</li>
				<li><strong>Pricing is upfront</strong> (typically <?php echo esc_html($price_anchor); ?>).</li>
				<li><strong>No deposit required</strong> to join the waitlist. After approval, refundable deposits may be used to hold a puppy.</li>
			</ul>
			<hr>
			<?php echo do_shortcode('[ttp_lead_cta]'); ?>
		</div>
	</div>
</div>
<?php get_footer(); ?>
