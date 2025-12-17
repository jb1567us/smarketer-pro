<?php
/*
Plugin Name: ESM Artwork Master Template
Description: Registers [esm_artwork_layout] shortcode AND intercepts content to enforce Single Source of Truth.
Version: 1.2 (Content Filter Mode)
Author: ESM Dev
*/

// Prevent direct access
if (!defined('ABSPATH'))
    exit;

class ESM_Artwork_Template
{

    private $data_map_by_title = [];
    private $data_map_by_id = [];

    public function __construct()
    {
        // Legacy Shortcode
        add_shortcode('esm_artwork_layout', [$this, 'render_layout_shortcode']);

        // NUCLEAR OPTION: Content Interception
        // Priority 99 to ensure we run last and overwrite everything
        add_filter('the_content', [$this, 'intercept_content'], 99);

        $this->load_data();
    }

    private function load_data()
    {
        $file = __DIR__ . '/artwork_data.json';
        if (!file_exists($file))
            $file = ABSPATH . 'artwork_data.json';
        if (!file_exists($file))
            return;

        $json = file_get_contents($file);
        $data = json_decode($json, true);
        if ($data) {
            foreach ($data as $item) {
                // Map by Title
                if (isset($item['title'])) {
                    $key = strtolower(trim($item['title']));
                    $this->data_map_by_title[$key] = $item;
                }
                // Map by WordPress ID
                if (isset($item['wordpress_id'])) {
                    $this->data_map_by_id[$item['wordpress_id']] = $item;
                }
            }
        }
    }

    public function intercept_content($content)
    {
        // Only target Pages (or Posts if needed)
        if (!is_singular())
            return $content;

        $id = get_the_ID();

        // 1. Check ID Match
        if (isset($this->data_map_by_id[$id])) {
            return $this->render_layout_internal($this->data_map_by_id[$id]);
        }

        // 2. Check Title Match
        $title = strtolower(trim(get_the_title()));
        if (isset($this->data_map_by_title[$title])) {
            return $this->render_layout_internal($this->data_map_by_title[$title]);
        }

        // 3. Fallback: If content strictly equals shortcode, try to render even if not in JSON (unlikely path)
        if (trim($content) === '[esm_artwork_layout]') {
            // No data found but shortcode present? Render skeleton.
            // Actually, better to return content so shortcode handler runs if data fails.
        }

        return $content;
    }

    public function render_layout_shortcode($atts)
    {
        $id = get_the_ID();
        $data = [];

        if (isset($this->data_map_by_id[$id])) {
            $data = $this->data_map_by_id[$id];
        } else {
            $title = strtolower(trim(get_the_title()));
            if (isset($this->data_map_by_title[$title])) {
                $data = $this->data_map_by_title[$title];
            }
        }

        return $this->render_layout_internal($data);
    }

    private function render_layout_internal($data)
    {
        // Safe Title
        $title = isset($data['title']) ? $data['title'] : get_the_title();

        // --- 1. DATA PREP ---
        $price = isset($data['price']) ? '$' . number_format($data['price']) : 'Inquire';

        // Dimensions
        $dimensions = isset($data['dimensions']) ? $data['dimensions'] : '';
        if (!$dimensions && isset($data['width'], $data['height'])) {
            $dimensions = "{$data['width']} W x {$data['height']} H in";
        }

        $medium = isset($data['mediumsDetailed']) ? $data['mediumsDetailed'] : (isset($data['medium']) ? $data['medium'] : 'Mixed Media');
        $year = isset($data['year']) ? $data['year'] : '';
        $styles = isset($data['styles']) ? $data['styles'] : '';

        // Description Logic
        $desc = "Original {$medium} painting by Elliot Spencer Morgan.";
        if ($year)
            $desc .= " Created in {$year}.";
        if ($styles)
            $desc .= " Featuring elements of {$styles}.";
        $desc .= " Signed and delivered with a Certificate of Authenticity.";

        // Specs Defaults
        $installation = isset($data['readyToHang']) ? $data['readyToHang'] : "Wired & Ready to Hang";
        if ($installation === 'No')
            $installation = "Requires Framing";

        $framing = isset($data['frame']) ? $data['frame'] : "Unframed";
        $shipping = isset($data['shippingFrom']) ? $data['shippingFrom'] : "United States";

        // Files
        $slug = sanitize_title($title);
        $spec_file = $this->find_file(ABSPATH . 'downloads/spec_sheets/', [$title . '_spec.pdf', $slug . '_spec.pdf', $title . '.pdf']);
        $zip_file = $this->find_file(ABSPATH . 'downloads/high_res/', [$title . '_HighRes.zip', $slug . '_HighRes.zip', $title . '.zip']);

        // --- 2. CSS STYLES ---
        $css = <<<CSS
        <style>
            .esm-master-layout { font-family: 'Inter', sans-serif; color: #333; line-height: 1.6; max-width: 800px; margin: 0 auto; padding-bottom: 4rem; }
            .esm-title { font-family: 'Playfair Display', serif; font-size: 2.5rem; text-align: center; margin-bottom: 1rem; color: #111; font-weight: 400; }
            .esm-desc { font-size: 1.1rem; text-align: left; margin-bottom: 3rem; color: #555; max-width: 700px; margin-left: auto; margin-right: auto; }
            
            /* Box */
            .esm-specs-box { border: 1px solid #e5e5e5; border-radius: 8px; padding: 2.5rem; background: #fff; margin-top: 2rem; position: relative; }
            .esm-specs-header { font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-top: 0; margin-bottom: 1.5rem; color: #000; }
            .esm-specs-list { list-style: none; padding: 0; margin: 0; }
            .esm-specs-item { border-bottom: 1px solid #f0f0f0; padding: 0.75rem 0; display: flex; align-items: center; font-size: 0.95rem; }
            .esm-specs-item:last-child { border-bottom: none; }
            .esm-check { color: #27ae60; margin-right: 12px; font-weight: bold; }
            
            /* Buttons */
            .esm-btn-group { display: flex; flex-wrap: wrap; gap: 15px; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid #f0f0f0; }
            .esm-btn { 
                display: inline-block; 
                padding: 12px 24px; 
                text-decoration: none; 
                text-transform: uppercase; 
                font-size: 0.8rem; 
                letter-spacing: 1px; 
                font-weight: 600; 
                border: 1px solid #000; 
                color: #000; 
                background: transparent; 
                transition: all 0.2s ease; 
                text-align: center;
            }
            .esm-btn:hover { background: #000; color: #fff; }
            
            /* Schema Invisible */
            .esm-schema { display: none; }
        </style>
CSS;

        // --- 3. HTML RENDER ---
        ob_start();
        ?>
        <div class="esm-master-layout">
            <?php echo $css; ?>

            <h1 class="esm-title"><?php echo esc_html($title); ?></h1>

            <!-- Description -->
            <div class="esm-desc">
                <?php echo esc_html($desc); ?>
            </div>

            <!-- Specs Box -->
            <div class="esm-specs-box">
                <h3 class="esm-specs-header">Designer Specifications</h3>
                <ul class="esm-specs-list">
                    <li class="esm-specs-item"><span class="esm-check">✓</span> <strong>Installation:</strong>&nbsp;
                        <?php echo esc_html($installation); ?></li>
                    <li class="esm-specs-item"><span class="esm-check">✓</span> <strong>Framing:</strong>&nbsp;
                        <?php echo esc_html($framing); ?></li>
                    <li class="esm-specs-item"><span class="esm-check">✓</span> <strong>Dimensions:</strong>&nbsp;
                        <?php echo esc_html($dimensions); ?></li>
                    <li class="esm-specs-item"><span class="esm-check">✓</span> <strong>Shipping:</strong>&nbsp;
                        <?php echo esc_html($shipping); ?></li>
                </ul>

                <?php if ($spec_file || $zip_file): ?>
                    <div class="esm-btn-group">
                        <?php if ($spec_file): ?>
                            <a href="/downloads/spec_sheets/<?php echo esc_attr($spec_file); ?>" class="esm-btn" download>Download Spec
                                Sheet</a>
                        <?php endif; ?>

                        <?php if ($zip_file): ?>
                            <a href="/downloads/high_res/<?php echo esc_attr($zip_file); ?>" class="esm-btn" download>Download High Res
                                Images</a>
                        <?php endif; ?>
                    </div>
                <?php endif; ?>
            </div>

            <!-- JSON-LD Schema (Invisible) -->
            <script type="application/ld+json">
                    {
                        "@context": "https://schema.org",
                        "@type": "VisualArtwork",
                        "name": "<?php echo esc_js($title); ?>",
                        "image": "<?php echo esc_js($data['image_url'] ?? ''); ?>",
                        "artist": { "@type": "Person", "name": "Elliot Spencer Morgan" },
                        "description": "<?php echo esc_js($desc); ?>",
                        "material": "<?php echo esc_js($medium); ?>",
                        "width": { "@type": "Distance", "value": "<?php echo esc_js($data['width'] ?? 0); ?>", "unitCode": "INH" },
                        "height": { "@type": "Distance", "value": "<?php echo esc_js($data['height'] ?? 0); ?>", "unitCode": "INH" },
                        "offer": {
                            "@type": "Offer",
                            "price": "<?php echo esc_js($data['price'] ?? 0); ?>",
                            "priceCurrency": "USD",
                            "availability": "https://schema.org/InStock"
                        }
                    }
                    </script>
        </div>
        <?php
        return ob_get_clean();
    }

    private function find_file($dir, $candidates)
    {
        foreach ($candidates as $c) {
            if (file_exists($dir . $c))
                return $c;
        }
        if (!is_dir($dir))
            return false;
        $files = scandir($dir);
        $candidates_lower = array_map('strtolower', $candidates);
        foreach ($files as $f) {
            if ($f === '.' || $f === '..')
                continue;
            if (in_array(strtolower($f), $candidates_lower))
                return $f;
        }
        return false;
    }
}

new ESM_Artwork_Template();
?>