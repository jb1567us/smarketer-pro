<?php
require_once('wp-load.php');

// 2. UPDATE LINKS
// Use sheets.zip
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$zipFile = __DIR__ . '/sheets.zip';
$extractPath = __DIR__ . '/downloads/spec_sheets/';

if (!file_exists($extractPath)) mkdir($extractPath, 0755, true);

if (file_exists($zipFile)) {
    echo "Found sheets.zip (" . filesize($zipFile) . " bytes).\n";
    $zip = new ZipArchive;
    if ($zip->open($zipFile) === TRUE) {
        $zip->extractTo($extractPath);
        $zip->close();
        echo "✅ Extracted ZIP (sheets.zip) to $extractPath\n";
    } else {
        echo "❌ Failed to open ZIP (sheets.zip). Code: " . $zip->getStatusString() . "\n";
    }
} else {
    echo "❌ sheets.zip NOT FOUND in " . __DIR__ . "\n";
}

// Verify Extraction
$filesCount = count(glob($extractPath . "*.pdf"));
echo "📂 PDF Files in $extractPath: $filesCount\n";

$map = [
    'red_planet' => 'Red-Planet_Sheet.pdf',
    'portal-2' => 'Portal_Sheet.pdf',
    'portal_2-2' => 'Portal-2_Sheet.pdf',
    'abstract_landscape' => 'Abstract-Landscape_Sheet.pdf',
    'self_portrait_1' => 'self-portrait-1_Sheet.pdf',
    'convergence' => 'Convergence_Sheet.pdf',
    'puzzled' => 'Puzzled_Sheet.pdf',
    'finger_print' => 'Finger-print_Sheet.pdf',
    'sheet_music' => 'Sheet-Music_Sheet.pdf',
    'meeting_in_the_middle' => 'Meeting-in-the-Middle_Sheet.pdf',
    'caviarpainting' => 'Caviar_Sheet.pdf',
    'heart_workpainting' => 'Heart-Work-Painting_Sheet.pdf',
    'portal_1painting-3' => 'Portal-1-Painting_Sheet.pdf',
    'morning_joepainting' => 'Morning-Joe-Painting_Sheet.pdf',
    'unitypainting' => 'Unity-Painting_Sheet.pdf',
    'dog_on_a_bikepainting' => 'Dog-on-a-bike-Painting_Sheet.pdf',
    'water_peoplepainting' => 'Water-People-Painting_Sheet.pdf',
    'towerspainting' => 'Towers-Painting_Sheet.pdf',
    'granularpainting' => 'Granular-Painting_Sheet.pdf',
    'puzzle_2painting' => 'Puzzle-2-Painting_Sheet.pdf',
    'puzzle_1painting' => 'Puzzle-1-Painting_Sheet.pdf',
    'trichomepainting' => 'Trichome-Painting_Sheet.pdf',
    'trichomespainting' => 'Trichomes-Painting_Sheet.pdf',
    'grillpainting' => 'Grill-Painting_Sheet.pdf',
    'quiltedpainting' => 'Quilted-Painting_Sheet.pdf',
    'interactionspainting' => 'Interactions-Painting_Sheet.pdf',
    'rushpainting' => 'Rush-Painting_Sheet.pdf',
    'yorkiepainting' => 'Yorkie-Painting_Sheet.pdf',
    'night_skypainting' => 'Night-Sky-Painting_Sheet.pdf',
    'boldpainting-4' => 'Bold-Painting_Sheet.pdf',
    'climbingpainting' => 'Climbing-Painting_Sheet.pdf',
    'dancepainting' => 'Dance-Painting_Sheet.pdf',
    'smokepainting' => 'Smoke-Painting_Sheet.pdf',
    'motionpainting' => 'Motion-Painting_Sheet.pdf',
    'listeningpainting' => 'Listening-Painting_Sheet.pdf',
    'synapsespainting' => 'Synapses-Painting_Sheet.pdf',
    'microscope_7painting-4' => 'Microscope-7-Painting_Sheet.pdf',
    'microscope_6painting-4' => 'Microscope-6-Painting_Sheet.pdf',
    'microscope_5painting-4' => 'Microscope-5-Painting_Sheet.pdf',
    'microscope_4painting-4' => 'Microscope-4-Painting_Sheet.pdf',
    'microscope_3painting-4' => 'Microscope-3-Painting_Sheet.pdf',
    'microscope_2painting-4' => 'Microscope-2-Painting_Sheet.pdf',
    'microscope_1painting-4' => 'Microscope-1-Painting_Sheet.pdf',
    'pieces_of_redcollage' => 'Pieces-of-Red-Collage_Sheet.pdf',
    'paper_peacecollage' => 'Paper-Peace-Collage_Sheet.pdf',
    'business_mulchcollage' => 'Business-Mulch-Collage_Sheet.pdf',
    'office_work_mulchcollage' => 'Office-Work-Mulch-Collage_Sheet.pdf',
    'in_the_darkpainting-3' => 'In-the-Dark-Painting_Sheet.pdf',
    'portal_006painting' => 'Portal-006-Painting_Sheet.pdf',
    'portal_005painting' => 'Portal-005-Painting_Sheet.pdf',
    'portal_004painting' => 'Portal-004-Painting_Sheet.pdf',
    'portal_003painting' => 'Portal-003-Painting_Sheet.pdf',
    'portal_002painting' => 'Portal-002-Painting_Sheet.pdf',
    'portal_001painting' => 'Portal-001-Painting_Sheet.pdf',
    'blue-glacier' => 'Blue-Glacier-Painting_Sheet.pdf',
    'warm_glacierpainting' => 'Warm-Glacier-Painting_Sheet.pdf',
    'sunset_glacierpainting' => 'Sunset-Glacier-Painting_Sheet.pdf',
    'waves' => 'Waves-Painting_Sheet.pdf',
    'meeting_in_the_middle' => 'Meeting-in-the-Middle_Sheet.pdf',
    'finger_print' => 'Finger-print_Sheet.pdf',
    'self_portrait_1' => 'self-portrait-1_Sheet.pdf',
    'dog_on_a_bikepainting' => 'Dog-on-a-bike_Sheet.pdf',
    'city-at-night-mulch-series' => 'City-at-Night-Mulch-Series_Sheet.pdf',
    'close-up-mulch-series' => 'Close-up-Mulch-Series_Sheet.pdf',
    'pieces_of_redcollage' => 'Pieces-of-Red_Sheet.pdf',
    'red-and-black-mulch-series' => 'Red-and-Black-Mulch-Series_Sheet.pdf',
    'jaguar' => 'Jaguar_Sheet.pdf',
    'megapixels' => 'Megapixels_Sheet.pdf',
    'esm-s17' => 'ESM-S17_Sheet.pdf',
    'fire-flow' => 'Fire-Flow_Sheet.pdf',
    'owls-in-fall' => 'Owls-in-Fall_Sheet.pdf',
    'connectivity' => 'Connectivity_Sheet.pdf',
    'atomic-flow' => 'Atomic-Flow_Sheet.pdf',
    'trees' => 'Trees_Sheet.pdf',
    'animal-kingdom' => 'Animal-Kingdom_Sheet.pdf',
    'clean-hands' => 'Clean-Hands_Sheet.pdf',
    'reflection' => 'Reflection_Sheet.pdf',
    'eggs-and-eyes' => 'Eggs-and-Eyes_Sheet.pdf',
    'moon-dance' => 'Moon-Dance_Sheet.pdf',
    'floating-leaves' => 'Floating-Leaves_Sheet.pdf',
    'arrowheads' => 'Arrowheads_Sheet.pdf',
    'campground' => 'campground_Sheet.pdf',
    'puzzle' => 'Puzzle_Sheet.pdf',
    'streams-and-ponds' => 'Streams-and-Ponds_Sheet.pdf',
    'cluster-of-caps' => 'Cluster-of-Caps_Sheet.pdf',
    'duck-pond' => 'Duck-pond_Sheet.pdf',
    'creek-bottom' => 'Creek-Bottom_Sheet.pdf',
    'organic-mushrooms' => 'Organic-Mushrooms_Sheet.pdf',
    'stones' => 'Stones_Sheet.pdf',
    'cubes' => 'Cubes_Sheet.pdf',
    'seed-pods' => 'Seed-pods_Sheet.pdf',
    'excited-bird' => 'Excited-Bird_Sheet.pdf',
    'mushroom-exclamation' => 'Mushroom-Exclamation_Sheet.pdf',
    'snake-and-rocks' => 'Snake-and-Rocks_Sheet.pdf',
    'shapeshifter' => 'Shapeshifter_Sheet.pdf',
    'coiled-snake' => 'Coiled-Snake_Sheet.pdf',
    'avacado-snack' => 'Avacado-Snack_Sheet.pdf',
    'gold-shapes' => 'Gold-Shapes_Sheet.pdf',
    'musical-embrace' => 'Musical-Embrace_Sheet.pdf',
    'organic-food' => 'Organic-food_Sheet.pdf',
    'snake-eggs' => 'Snake-Eggs_Sheet.pdf',
    'brush-strokes' => 'Brush-Strokes_Sheet.pdf',
    'blanket' => 'Blanket_Sheet.pdf',
    'dancepainting' => 'Dance_Sheet.pdf',
    'bloom' => 'Bloom_Sheet.pdf',
    'organic-shapes' => 'Organic-Shapes_Sheet.pdf',
    'silver' => 'Silver_Sheet.pdf',
    'fortune' => 'Fortune_Sheet.pdf',
    'transformation' => 'Transformation_Sheet.pdf',
    'golden-nugget' => 'Golden-Nugget_Sheet.pdf',
    'golden-rule' => 'Golden-Rule_Sheet.pdf',
    'feather-trees' => 'Feather-trees_Sheet.pdf',
    'magic-carpet' => 'Magic-Carpet_Sheet.pdf',
    'screen' => 'Screen_Sheet.pdf',
    'spring-blooms' => 'Spring-Blooms_Sheet.pdf',
    'celebrate' => 'Celebrate_Sheet.pdf',
    'anemones' => 'Anemones_Sheet.pdf',
    'coral' => 'Coral_Sheet.pdf',
    'existance' => 'Existance_Sheet.pdf',
    'fireworks' => 'Fireworks_Sheet.pdf',
    'synapse' => 'Synapse_Sheet.pdf',
    'stick-men' => 'Stick-men_Sheet.pdf',
    'descending' => 'Descending_Sheet.pdf',
    'lifeforce' => 'lifeforce_Sheet.pdf',
    'turquoise-and-peppers' => 'Turquoise-and-Peppers_Sheet.pdf',
    'turquoise-blend' => 'Turquoise-blend_Sheet.pdf',
    'turquoise-stretch' => 'Turquoise-stretch_Sheet.pdf',
    'turquoise-circuit-board' => 'Turquoise-Circuit-board_Sheet.pdf',
    'blast-of-blue-on-red' => 'Blast-of-Blue-on-Red_Sheet.pdf',
    'blue-gold' => 'Blue-Gold_Sheet.pdf',
    'blue-glacier' => 'Blue-Glacier_Sheet.pdf',
    'blue-wave' => 'Blue-Wave_Sheet.pdf',
    'blue-mesh' => 'Blue-Mesh_Sheet.pdf',
    'cold-blue' => 'Cold-Blue_Sheet.pdf',
    'blue-storm' => 'Blue-Storm_Sheet.pdf',
    'no-public-shrooms-limited-edition-of-1' => 'No-Public-Shrooms-Limited-Edition-of-1_Sheet.pdf',
    'no-public-shrooms-limited-edition-of-1' => 'No-Public-Shrooms-Limited-Edition-of-1_Sheet.pdf',
    'start-sign-limited-edition-of-1' => 'Start-Sign-Limited-Edition-of-1_Sheet.pdf',
    'right-way-limited-edition-of-1' => 'Right-Way-Limited-Edition-of-1_Sheet.pdf',
    'no-porking' => 'NO-PORKING_Sheet.pdf',
    'gold-series-006' => 'GOLD-SERIES-006_Sheet.pdf',
    'gold-series-005' => 'GOLD-SERIES-005_Sheet.pdf',
    'gold-series-004' => 'GOLD-SERIES-004_Sheet.pdf',
    'gold-series-003' => 'GOLD-SERIES-003_Sheet.pdf',
    'gold-series-002' => 'GOLD-SERIES-002_Sheet.pdf',
    'gold-series-001' => 'GOLD-SERIES-001_Sheet.pdf',
    'waves' => 'waves_Sheet.pdf',
    'waves' => 'Waves_Sheet.pdf',
    'blue-storm' => 'Blue-Storm_Sheet.pdf',
    'blue-glacier' => 'Blue-Glacier_Sheet.pdf',
    'golden-rule' => 'Golden-Rule_Sheet.pdf',
    'transformation' => 'Transformation_Sheet.pdf',
    'bloom' => 'Bloom_Sheet.pdf',
];

echo "<pre>Updating Content Links (Debug V3)...\n";

$count = 0;
foreach ($map as $slug => $filename) {
    // echo "Checking slug: '$slug'... ";
    
    // Lookup by Slug
    $post = get_page_by_path($slug, OBJECT, 'page');
    
    if (!$post) { 
        // Force check 'portal-2' specifically to debug my data
        if ($slug == 'portal-2' || $slug == 'portal') {
            echo "DEBUG: Slug '$slug' not found via get_page_by_path. Trying Query...\n";
            $q = new WP_Query(['name' => $slug, 'post_type' => 'page']);
            if ($q->have_posts()) echo "  FOUND via WP_Query! ID: " . $q->posts[0]->ID . "\n";
            else echo "  NOT FOUND via WP_Query either.\n";
        }
        continue; 
    }
    
    $page_id = $post->ID;
    $content = $post->post_content;
    
    // Check if Caviar link exists
    if (strpos($content, 'caviar-spec-sheet.pdf') === false) {
        // echo "Page $slug ($page_id): No caviar link found.\n";
        continue;
    }
    
    $new_link = "https://elliotspencermorgan.com/downloads/spec_sheets/" . $filename;
    
    $pattern_spec = '/href="[^"]*caviar-spec-sheet\.pdf"/i';
    $replacement_spec = 'href="' . $new_link . '"';
    
    $pattern_hr = '/href="[^"]*caviar-high-res\.zip"/i';
    $replacement_hr = 'href="#" onclick="return false;" style="opacity:0.5; cursor:not-allowed;" title="High Res Coming Soon"';
    
    $new_content = preg_replace($pattern_spec, $replacement_spec, $content);
    $new_content = preg_replace($pattern_hr, $replacement_hr, $new_content);
    
    if ($new_content !== $content) {
        $res = wp_update_post([
            'ID' => $page_id,
            'post_content' => $new_content
        ]);
        if ($res) echo "✅ Updated Page $slug ($page_id) -> $filename\n";
        else echo "❌ Failed Update Page $slug ($page_id)\n";
        $count++;
    } else {
         echo "⚠️ Page $slug: Match failed despite strpos success.\n";
         // Fallback simple replace
         $simple = str_replace('caviar-spec-sheet.pdf', 'spec_sheets/' . $filename, $content);
         if ($simple !== $content) {
             wp_update_post(['ID' => $page_id, 'post_content' => $simple]);
             echo "✅ Simple Replace Page $slug\n";
             $count++;
         }
    }
}
echo "Done. Updated $count pages.</pre>";
?>
