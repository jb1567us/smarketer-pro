
        <?php get_header(); ?>
        
        <div class="artwork-detail-page">
            <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                
                <div class="artwork-gallery">
                    <?php if (has_post_thumbnail()) : ?>
                        <?php the_post_thumbnail('artwork-large', array('class' => 'artwork-image')); ?>
                    <?php endif; ?>
                </div>
                
                <div class="artwork-info">
                    <h1 class="artwork-title"><?php the_title(); ?></h1>
                    
                    <div class="artwork-meta">
                        <div class="artwork-price"><?php echo get_artwork_meta('artwork_price'); ?></div>
                        <div class="artwork-medium"><?php echo get_artwork_meta('artwork_medium'); ?></div>
                        <div class="artwork-dimensions"><?php echo get_artwork_meta('artwork_dimensions'); ?></div>
                    </div>
                    
                    <div class="artwork-description">
                        <?php the_content(); ?>
                    </div>
                    
                    <div class="artwork-details">
                        <h3>Artwork Details</h3>
                        <ul>
                            <li><strong>Year Created:</strong> <?php echo get_artwork_meta('artwork_year'); ?></li>
                            <li><strong>Subject:</strong> <?php echo get_artwork_meta('artwork_subject'); ?></li>
                            <li><strong>Styles:</strong> <?php echo get_artwork_meta('artwork_styles'); ?></li>
                            <li><strong>Rarity:</strong> <?php echo get_artwork_meta('artwork_rarity'); ?></li>
                            <li><strong>Ready to Hang:</strong> <?php echo get_artwork_meta('artwork_ready_to_hang'); ?></li>
                            <li><strong>Framing:</strong> <?php echo get_artwork_meta('artwork_framing'); ?></li>
                            <li><strong>Authenticity:</strong> <?php echo get_artwork_meta('artwork_authenticity'); ?></li>
                            <li><strong>Packaging:</strong> <?php echo get_artwork_meta('artwork_packaging'); ?></li>
                        </ul>
                    </div>
                </div>
                
            </article>
        </div>
        
        <?php get_footer(); ?>
        