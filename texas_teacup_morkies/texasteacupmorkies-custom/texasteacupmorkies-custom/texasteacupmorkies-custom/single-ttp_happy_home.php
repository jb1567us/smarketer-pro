<?php
get_header();
the_post();
$client = get_post_meta( get_the_ID(), '_ttp_client_name', true );
$loc = get_post_meta( get_the_ID(), '_ttp_client_location', true );
?>
<section class="ttp-section">
	<div class="ttp-container">
		<article class="ttp-card ttp-card--wide">
			<h1 class="ttp-h1"><?php the_title(); ?></h1>
			<p class="ttp-muted"><?php echo esc_html( trim( ($client ? $client : '') . ($client && $loc ? ' • ' : '') . ($loc ? $loc : '') ) ); ?></p>
			<?php if ( has_post_thumbnail() ) : ?><div class="ttp-product__image" style="margin-top:14px;"><?php the_post_thumbnail( 'large' ); ?></div><?php endif; ?>
			<div class="ttp-prose"><?php the_content(); ?></div>
		</article>
	</div>
</section>
<?php get_footer(); ?>
