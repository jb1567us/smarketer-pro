<?php
/**
 * Placeholder images and fallback content for the theme
 * 
 * @package Collaborative_Archive
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}

/**
 * Get placeholder image URL
 */
function ca_get_placeholder_image($size = 'medium') {
    $sizes = array(
        'thumbnail' => array(150, 150),
        'medium' => array(300, 200),
        'large' => array(600, 400),
        'full' => array(800, 600)
    );
    
    $dimensions = isset($sizes[$size]) ? $sizes[$size] : $sizes['medium'];
    
    // Create a simple SVG placeholder
    $width = $dimensions[0];
    $height = $dimensions[1];
    
    $svg = '<svg width="' . $width . '" height="' . $height . '" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#f8f9fa"/>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" 
              font-family="Arial, sans-serif" font-size="14" fill="#6c757d">
              Chapter Image
        </text>
        <text x="50%" y="65%" dominant-baseline="middle" text-anchor="middle" 
              font-family="Arial, sans-serif" font-size="12" fill="#adb5bd">
              ' . $width . '×' . $height . '
        </text>
    </svg>';
    
    return 'data:image/svg+xml;base64,' . base64_encode($svg);
}

/**
 * Default family tree data for Sancha Padrós
 */
function ca_get_default_family_data() {
    return array(
        'name' => 'Sancha Padrós Family',
        'members' => array(
            array(
                'name' => 'José María Sancha Padrós',
                'years' => '1908-1994',
                'role' => 'Artist, Illustrator, Exile',
                'description' => 'Spanish artist who lived and worked in multiple countries after the Civil War'
            ),
            array(
                'name' => 'Francisco Sancha Lengo',
                'years' => '1874-1936',
                'role' => 'Father - Illustrator',
                'description' => 'Prominent Spanish illustrator and painter'
            ),
            array(
                'name' => 'Matilde Padrós',
                'years' => '?',
                'role' => 'Mother',
                'description' => ''
            ),
            array(
                'name' => 'Anelia Stoyanova',
                'years' => '?',
                'role' => 'Wife',
                'description' => 'Bulgarian national, married in Sofia'
            ),
            array(
                'name' => 'Soledad Sancha',
                'years' => '?',
                'role' => 'Sister',
                'description' => 'Also exiled after the Civil War'
            )
        )
    );
}

/**
 * Render simple family tree
 */
function ca_render_simple_family_tree() {
    $family_data = ca_get_default_family_data();
    ?>
    <div class="simple-family-tree">
        <h4><?php echo esc_html($family_data['name']); ?></h4>
        <div class="family-members">
            <?php foreach ($family_data['members'] as $member): ?>
            <div class="family-member">
                <div class="member-name"><?php echo esc_html($member['name']); ?></div>
                <?php if ($member['years']): ?>
                <div class="member-years"><?php echo esc_html($member['years']); ?></div>
                <?php endif; ?>
                <?php if ($member['role']): ?>
                <div class="member-role"><?php echo esc_html($member['role']); ?></div>
                <?php endif; ?>
                <?php if ($member['description']): ?>
                <div class="member-description"><?php echo esc_html($member['description']); ?></div>
                <?php endif; ?>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
    <?php
}

/**
 * Get timeline data for José Sancha Padrós
 */
function ca_get_timeline_data() {
    return array(
        array(
            'year' => '1908',
            'title' => 'Birth in Spain',
            'description' => 'Born in San Lorenzo de El Escorial, Madrid province',
            'type' => 'life'
        ),
        array(
            'year' => '1912-1923',
            'title' => 'Childhood in London',
            'description' => 'Lived with family in London during formative years',
            'type' => 'life'
        ),
        array(
            'year' => '1931',
            'title' => 'Paris Scholarship',
            'description' => 'Received scholarship to study art in Paris',
            'type' => 'art'
        ),
        array(
            'year' => '1936-1939',
            'title' => 'Spanish Civil War',
            'description' => 'Fought for the Republican side',
            'type' => 'politics'
        ),
        array(
            'year' => '1939',
            'title' => 'Exile to Moscow',
            'description' => 'Forced into exile after Republican defeat',
            'type' => 'politics'
        ),
        array(
            'year' => '1940s',
            'title' => 'VENONA Project',
            'description' => 'Codenamed "REMBRANDT" in Soviet intelligence',
            'type' => 'intelligence'
        ),
        array(
            'year' => '1951',
            'title' => 'Satire Theater Sofia',
            'description' => 'Co-founded Aleko Konstantinov Satire Theater',
            'type' => 'art'
        ),
        array(
            'year' => '1958',
            'title' => 'Move to East Berlin',
            'description' => 'Worked in film production and art education',
            'type' => 'art'
        ),
        array(
            'year' => '1966',
            'title' => 'Return to Madrid',
            'description' => 'Permanently returned to Spain',
            'type' => 'life'
        ),
        array(
            'year' => '1994',
            'title' => 'Death in Madrid',
            'description' => 'Died in Madrid at age 86',
            'type' => 'life'
        )
    );
}

/**
 * Render interactive timeline
 */
function ca_render_interactive_timeline() {
    $timeline_data = ca_get_timeline_data();
    ?>
    <div class="interactive-timeline">
        <div class="timeline-filter">
            <button class="filter-btn active" data-filter="all">All Events</button>
            <button class="filter-btn" data-filter="art">Art & Culture</button>
            <button class="filter-btn" data-filter="politics">Political Life</button>
            <button class="filter-btn" data-filter="intelligence">Intelligence</button>
            <button class="filter-btn" data-filter="life">Personal Life</button>
        </div>
        
        <div class="timeline-events">
            <?php foreach ($timeline_data as $event): ?>
            <div class="timeline-event" data-type="<?php echo esc_attr($event['type']); ?>">
                <div class="event-year"><?php echo esc_html($event['year']); ?></div>
                <div class="event-content">
                    <h5><?php echo esc_html($event['title']); ?></h5>
                    <p><?php echo esc_html($event['description']); ?></p>
                </div>
                <div class="event-type type-<?php echo esc_attr($event['type']); ?>">
                    <?php echo ucfirst($event['type']); ?>
                </div>
            </div>
            <?php endforeach; ?>
        </div>
    </div>
    <?php
}