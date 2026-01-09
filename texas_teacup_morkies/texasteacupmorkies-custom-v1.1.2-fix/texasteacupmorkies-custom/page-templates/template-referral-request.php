<?php
/*
Template Name: Referral Request
*/
get_header();
$form_url = (string) ttp_get_option('referral_form_url', '');
$disclosure = (string) ttp_get_option('commission_disclosure', 'Disclosure: We may receive a referral commission if you purchase through a breeder we refer you to.' );
?>
<div class="ttp-container ttp-section">
	<header class="ttp-pagehead">
		<h1 class="ttp-h1"><?php the_title(); ?></h1>
		<p class="ttp-muted">Between seasons, submit a referral request. We keep our breeder list private and refer selectively.</p>
	</header>

	<?php while ( have_posts() ) : the_post(); ?>
		<?php if ( trim( get_the_content() ) ) : ?>
			<div class="ttp-card ttp-card--wide" style="margin-bottom:16px;"><div class="ttp-prose"><?php the_content(); ?></div></div>
		<?php endif; ?>
	<?php endwhile; ?>

	<div style="display:grid;grid-template-columns:1.1fr .9fr;gap:16px;">
		<div class="ttp-card ttp-card--wide">
			<h2 class="ttp-h2">Referral request form</h2>
			<?php if ( $form_url ) : ?>
				<div class="ttp-embed ttp-embed--form"><iframe title="Referral request form" loading="lazy" src="<?php echo esc_url($form_url); ?>"></iframe></div>
			<?php else : ?>
				<p class="ttp-muted">Add your referral form URL in <strong>Appearance → TTP Settings</strong> when you’re ready.</p>
			<?php endif; ?>
		</div>

		<div class="ttp-card">
			<h2 class="ttp-h2">How referrals work</h2>
			<ul class="ttp-prose">
				<li>You tell us what you’re looking for and your timeline.</li>
				<li>We decide who to reach out to privately (no public list).</li>
				<li><em><?php echo esc_html($disclosure); ?></em></li>
			</ul>
			<hr>
			<?php echo do_shortcode('[ttp_lead_cta]'); ?>
		</div>
	</div>
</div>
<?php get_footer(); ?>
