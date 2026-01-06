<?php
if ( ! defined( 'ABSPATH' ) ) { exit; }

function ttp_find_page_by_slug( $slug ) {
	$page = get_page_by_path( $slug );
	return $page ? (int) $page->ID : 0;
}

function ttp_create_or_update_page( $slug, $title, $content, $template = '' ) {
	$existing_id = ttp_find_page_by_slug( $slug );

	$postarr = array(
		'post_title'   => $title,
		'post_name'    => $slug,
		'post_type'    => 'page',
		'post_status'  => 'publish',
		'post_content' => $content,
	);

	if ( $existing_id ) {
		$postarr['ID'] = $existing_id;
		$page_id = wp_update_post( $postarr, true );
	} else {
		$page_id = wp_insert_post( $postarr, true );
	}

	if ( is_wp_error( $page_id ) ) return 0;

	if ( $template ) {
		update_post_meta( $page_id, '_wp_page_template', $template );
	}

	return (int) $page_id;
}

function ttp_seed_default_pages_on_activation() {
	$done = get_option( 'ttp_onboarding_done', false );
	if ( $done ) return;

	// Set option defaults needed by shortcodes/templates.
	$opts = get_option( 'ttp_theme_options', array() );
	if ( ! is_array( $opts ) ) { $opts = array(); }
	if ( empty( $opts['locality_center'] ) ) { $opts['locality_center'] = 'Austin, TX'; }
	if ( empty( $opts['pickup_address'] ) ) { $opts['pickup_address'] = '3800 Manorwood Rd, Austin, TX 78723'; }
	if ( empty( $opts['price_anchor'] ) ) { $opts['price_anchor'] = '$2,000+'; }
	if ( empty( $opts['commission_disclosure'] ) ) {
		$opts['commission_disclosure'] = 'Disclosure: We may receive a referral commission if you purchase through a breeder we refer you to.';
	}
	if ( empty( $opts['lead_mode'] ) ) { $opts['lead_mode'] = 'referral'; }

	$apply_content = <<<HTML
<p><strong>When we’re in season</strong>, we open the waitlist so we can keep serious inquiries organized and respond quickly.</p>
<ul>
<li><strong>Pickup is local</strong> at our home in Austin, TX.</li>
<li><strong>Pricing is upfront</strong> (typically {$opts['price_anchor']}).</li>
<li><strong>No deposit is required</strong> to join the waitlist. After approval, you may place a <strong>refundable</strong> deposit if you want us to hold a specific puppy.</li>
</ul>
<p>For quick questions, text/call—then please submit the form so we have your name, email, phone, and <strong>city/state</strong>.</p>
<p>[ttp_lead_cta]</p>
HTML;

	$referral_content = <<<HTML
<p>Between breeding seasons, we can sometimes refer you to other breeders. We <strong>do not list breeders publicly</strong>—you submit a request, and we choose who to contact based on what you want and what’s realistic right now.</p>
<ul>
<li>We keep our partner list private to protect everyone’s time.</li>
<li>We may receive a commission if you purchase through a breeder we refer you to.</li>
</ul>
<p><em>{$opts['commission_disclosure']}</em></p>
<p>[ttp_lead_cta]</p>
HTML;

	$reviews_content = <<<HTML
<p>We’re small by design—so trust matters. We invite questions, provide vet references when requested, and share what we know openly.</p>
<p>Below you can link out to Google reviews and keep a small “happy homes” gallery right on this page (add photos using the WordPress editor).</p>
HTML;

	$process_content = <<<HTML
<h2>Our placement process</h2>
<ol>
<li><strong>Availability</strong>: we typically have puppies once a year (often fall; sometimes spring).</li>
<li><strong>Apply</strong>: submit the short form so we have accurate contact info.</li>
<li><strong>Call/Text</strong>: we confirm timing, lifestyle fit, and expectations. We’re happy to talk on the phone.</li>
<li><strong>Reserve (optional)</strong>: no deposit required for the waitlist. After approval, we may accept a refundable deposit to hold a puppy.</li>
<li><strong>Go-home</strong>: puppies are typically ready after ~8 weeks with mom. You pick up at our home in Austin.</li>
</ol>

<h2>FAQ</h2>
<h3>Do you deliver?</h3>
<p>Typically, no. <strong>Pickup is local</strong> at our home in Austin.</p>

<h3>Why list prices upfront?</h3>
<p>Because time matters. Boutique, family-raised puppies are a commitment; pricing usually starts around <strong>{$opts['price_anchor']}</strong>.</p>

<h3>Which breeds do you have?</h3>
<p>Most seasons we have <strong>one breed at a time</strong>. Right now it’s Maltipoms. We keep Morkie info available for future planning.</p>

<p style="margin-top:16px;">[ttp_lead_cta]</p>
HTML;

	$contact_content = <<<HTML
<p>Pickup is typically at our home in Austin (78723). If you’re coming from out of town, we recommend planning a calm drive home and a quiet first night.</p>

<div class="ttp-card" style="margin:14px 0;">
<p class="ttp-muted" style="margin:0 0 8px;"><strong>Pickup address</strong></p>
<p style="margin:0;"><strong>3800 Manorwood Rd</strong><br>Austin, TX 78723</p>
</div>

<p>[ttp_map_directions from="Austin, TX" to="3800 Manorwood Rd, Austin, TX 78723" height="420"]</p>

<h3>Best way to reach us</h3>
<ul>
<li><strong>Text or call</strong> for quick questions.</li>
<li>Please still submit the form (apply or referral) so we can keep your info organized.</li>
</ul>

<p>[ttp_lead_cta]</p>
HTML;

	$maltipom_content = <<<HTML
<p><strong>Maltipoms</strong> (typically Maltese + Pomeranian) are affectionate companion dogs with a bright, friendly temperament. In our home, puppies are raised around normal day-to-day life in Austin—handled gently, socialized with people and pets, and introduced to routines early.</p>

<h2>What families usually love about Maltipoms</h2>
<ul>
<li><strong>Companion temperament</strong>: sweet, attentive, and people-focused.</li>
<li><strong>Small size</strong>: a great fit for many Austin households.</li>
<li><strong>Routine-friendly</strong>: early house-training habits begin right away.</li>
</ul>

<h2>Care & grooming</h2>
<ul>
<li>Coats vary. Regular brushing prevents tangles and matting.</li>
<li>A consistent grooming schedule keeps things comfortable long-term.</li>
</ul>

<h2>Availability</h2>
<p>If a Maltipom is available, you’ll see them on <a href="/available-puppies/">Available Puppies</a>. Otherwise, use the button below to apply (when waitlist is open) or request a referral.</p>

<p>[ttp_lead_cta]</p>
HTML;

	$morkie_content = <<<HTML
<p><strong>Morkies</strong> (commonly Maltese + Yorkie) are small companion dogs with a lively spark—curious, social, and often deeply attached to their people. We keep this page up for education and future planning, even when we’re not actively breeding Morkies.</p>

<h2>What families usually love about Morkies</h2>
<ul>
<li><strong>Bright + engaged</strong>: they notice everything and love interaction.</li>
<li><strong>Small companion size</strong>: great for households that want a close “shadow dog.”</li>
<li><strong>Personality</strong>: confident, playful, expressive.</li>
</ul>

<h2>Care & grooming</h2>
<ul>
<li>Regular brushing and a grooming routine keep coats manageable.</li>
<li>Training and boundaries early help them thrive.</li>
</ul>

<h2>Availability</h2>
<p>We don’t always have Morkies. When we do, they’ll appear on <a href="/available-puppies/">Available Puppies</a>. In the meantime, you can request a referral if you’re looking sooner.</p>

<p>[ttp_lead_cta]</p>

	// --- Local SEO pages (Austin metro) ---
	// Keep copy accurate and consistent: pickup is in Austin at our home.
	$area_intro = 'We’re an in-home boutique breeder with local pickup in Austin (78723). If you live nearby, these pages outline what the pickup process looks like and how to get to us. We typically have one breed at a time—check Available Puppies for the current season.';

	$local_pages = array(
		array(
			'slug'  => 'round-rock-puppies',
			'title' => 'Maltipom Puppies Near Round Rock, TX (Austin Pickup)',
			'from'  => 'Round Rock, TX',
		),
		array(
			'slug'  => 'cedar-park-puppies',
			'title' => 'Maltipom Puppies Near Cedar Park, TX (Austin Pickup)',
			'from'  => 'Cedar Park, TX',
		),
		array(
			'slug'  => 'bastrop-puppies',
			'title' => 'Maltipom Puppies Near Bastrop, TX (Austin Pickup)',
			'from'  => 'Bastrop, TX',
		),
		array(
			'slug'  => 'pflugerville-puppies',
			'title' => 'Maltipom Puppies Near Pflugerville, TX (Austin Pickup)',
			'from'  => 'Pflugerville, TX',
		),
		array(
			'slug'  => 'georgetown-puppies',
			'title' => 'Maltipom Puppies Near Georgetown, TX (Austin Pickup)',
			'from'  => 'Georgetown, TX',
		),
	);

	$local_page_ids = array();
	foreach ( $local_pages as $lp ) {
		$city = $lp['from'];
		$local_content = '<p><strong>For families in ' . esc_html( $city ) . ':</strong> ' . esc_html( $area_intro ) . '</p>'
			. '<ul>'
			. '<li><strong>Pickup:</strong> at our home in Austin (near 78723).</li>'
			. '<li><strong>Focus:</strong> family-raised, gently socialized, and started on early routines.</li>'
			. '<li><strong>Pricing:</strong> typically ' . esc_html( $opts['price_anchor'] ) . ' (listed upfront).</li>'
			. '</ul>'
			. '<p>When a puppy is available, you’ll see them on <a href="/available-puppies/">Available Puppies</a>. For breed education, see <a href="/maltipom/">Maltipom</a> (current focus) and <a href="/morkie/">Morkie</a> (future planning). If we’re between litters, you can request a private referral.</p>'
			. '<p>[ttp_lead_cta]</p>'
			. '<h2>Directions for pickup</h2>'
			. '<p class="ttp-muted">These are driving directions from the center of ' . esc_html( $city ) . ' to our pickup address.</p>'
			. '<p>[ttp_map_directions from="' . esc_attr( $city ) . '" to="' . esc_attr( $opts['pickup_address'] ) . '" height="420"]</p>'
			. '<hr>'
			. '<h2>Local notes</h2>'
			. '<p>We recommend planning a calm ride home (a small carrier, water, and a quiet first evening). If you have questions about transition, feeding, or supplies, just ask—our goal is to set you up for a smooth first week.</p>';

		$local_page_ids[ $lp['slug'] ] = ttp_create_or_update_page( $lp['slug'], $lp['title'], $local_content );
	}

HTML;

	// Create pages
	$home_id = ttp_create_or_update_page( 'home', 'Home', '<p>This page is the site homepage and is rendered by the theme’s front-page template.</p>' );

	$apply_id = ttp_create_or_update_page( 'apply', 'Apply / Waitlist', $apply_content, 'page-templates/template-apply-waitlist.php' );
	$ref_id   = ttp_create_or_update_page( 'referral-request', 'Referral Request', $referral_content, 'page-templates/template-referral-request.php' );

	$reviews_id = ttp_create_or_update_page( 'reviews', 'Reviews & Happy Homes', $reviews_content, 'page-templates/template-reviews-happyhomes.php' );

	$process_id = ttp_create_or_update_page( 'process', 'Process / FAQ', $process_content );
	$contact_id = ttp_create_or_update_page( 'contact', 'Contact', $contact_content );
	$maltipom_id = ttp_create_or_update_page( 'maltipom', 'Maltipom Puppies (Austin, TX)', $maltipom_content );
	$morkie_id   = ttp_create_or_update_page( 'morkie', 'Morkie Puppies (Austin, TX)', $morkie_content );

	$opts['apply_page_id'] = $apply_id;
	$opts['referral_page_id'] = $ref_id;
	update_option( 'ttp_theme_options', $opts );

	// Set Home as static front page if not set.
	if ( ! get_option( 'page_on_front' ) ) {
		update_option( 'show_on_front', 'page' );
		update_option( 'page_on_front', $home_id );
	}

	// Create Primary/Footer menus if not assigned.
	$locations = get_theme_mod( 'nav_menu_locations', array() );
	$primary_loc = 'primary';
	$footer_loc  = 'footer';

	if ( empty( $locations[ $primary_loc ] ) ) {
		$menu_id = wp_create_nav_menu( 'Primary' );
		if ( ! is_wp_error( $menu_id ) ) {
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Home', 'menu-item-object' => 'page', 'menu-item-object-id' => $home_id, 'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ) );
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Available Puppies', 'menu-item-url' => get_post_type_archive_link( 'ttp_puppy' ), 'menu-item-type' => 'custom', 'menu-item-status' => 'publish' ) );
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Maltipom (Austin)', 'menu-item-object' => 'page', 'menu-item-object-id' => $maltipom_id, 'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ) );
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Morkie (Info)', 'menu-item-object' => 'page', 'menu-item-object-id' => $morkie_id, 'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ) );
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Reviews', 'menu-item-object' => 'page', 'menu-item-object-id' => $reviews_id, 'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ) );
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Process / FAQ', 'menu-item-object' => 'page', 'menu-item-object-id' => $process_id, 'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ) );
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Contact', 'menu-item-object' => 'page', 'menu-item-object-id' => $contact_id, 'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ) );
			$locations[ $primary_loc ] = $menu_id;
			set_theme_mod( 'nav_menu_locations', $locations );
		}
	}

	if ( empty( $locations[ $footer_loc ] ) ) {
		$menu_id = wp_create_nav_menu( 'Footer' );
		if ( ! is_wp_error( $menu_id ) ) {
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Available Puppies', 'menu-item-url' => get_post_type_archive_link( 'ttp_puppy' ), 'menu-item-type' => 'custom', 'menu-item-status' => 'publish' ) );
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Apply / Waitlist', 'menu-item-object' => 'page', 'menu-item-object-id' => $apply_id, 'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ) );
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Referral Request', 'menu-item-object' => 'page', 'menu-item-object-id' => $ref_id, 'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ) );
			wp_update_nav_menu_item( $menu_id, 0, array( 'menu-item-title' => 'Contact', 'menu-item-object' => 'page', 'menu-item-object-id' => $contact_id, 'menu-item-type' => 'post_type', 'menu-item-status' => 'publish' ) );
			$locations = get_theme_mod( 'nav_menu_locations', array() );
			$locations[ $footer_loc ] = $menu_id;
			set_theme_mod( 'nav_menu_locations', $locations );
		}
	}

	update_option( 'ttp_onboarding_done', true );
}
add_action( 'after_switch_theme', 'ttp_seed_default_pages_on_activation' );
