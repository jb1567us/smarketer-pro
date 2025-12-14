<?php
// ROBUST TAG RE-APPLICATION SCRIPT
require_once('wp-load.php');
set_time_limit(300);

// 1. FORCE REGISTRATION (Crucial Step)
global $wp_taxonomies;
if (taxonomy_exists('post_tag')) {
    register_taxonomy_for_object_type('post_tag', 'page');
}

$items = [
    ['id' => 1704, 'title' => 'Red Planet', 'tags' => ['Brown', 'Expressionism', 'Geometric', 'Black', 'Texture', 'Abstract', 'Large', 'Statement Piece', 'Orange', 'Square', 'Red']],
    ['id' => 1927, 'title' => 'Portal', 'tags' => ['Brown', 'Expressionism', 'Minimalist', 'Fine Art', 'Grey', 'Abstract', 'Oil', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 1928, 'title' => 'Portal 2', 'tags' => ['Brown', 'Conceptual', 'Fine Art', 'Grey', 'Abstract', 'Pink', 'Abstract Expressionism', 'Ink', 'Gold', 'Paper']],
    ['id' => 1708, 'title' => 'self portrait 1', 'tags' => ['Minimalist', 'Fine Art', 'Black', 'Abstract Expressionism', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1629, 'title' => 'Convergence', 'tags' => ['Brown', 'Expressionism', 'Conceptual', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Wood']],
    ['id' => 1630, 'title' => 'Puzzled', 'tags' => ['Geometric', 'Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Structured', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1709, 'title' => 'Finger print', 'tags' => ['Expressionism', 'Conceptual', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Large', 'Statement Piece', 'Wood']],
    ['id' => 1710, 'title' => 'Sheet Music', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Abstract Expressionism', 'Abstract', 'Ink', 'Pop Art', 'Gold', 'Paper']],
    ['id' => 1711, 'title' => 'Meeting in the Middle', 'tags' => ['Brown', 'Expressionism', 'Conceptual', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Wood']],
    ['id' => 1764, 'title' => 'Caviar', 'tags' => ['Geometric', 'Grey', 'Black & White', 'Silver', 'Abstract', 'Ink', 'Beige', 'Paper', 'Pop Art', 'White', 'Contemporary']],
    ['id' => 1852, 'title' => 'Heart Work Painting', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Abstract', 'Abstract Expressionism', 'Ink', 'Gold', 'Modern', 'Paper']],
    ['id' => 1945, 'title' => 'Portal 1 Painting', 'tags' => ['Brown', 'Conceptual', 'Fine Art', 'Paint', 'Grey', 'Abstract', 'Pink', 'Abstract Expressionism', 'Gold', 'Modern', 'Paper']],
    ['id' => 1854, 'title' => 'Morning Joe Painting', 'tags' => ['Minimalist', 'Fine Art', 'Black', 'Abstract Expressionism', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1855, 'title' => 'Unity Painting', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Abstract Expressionism', 'Abstract', 'Ink', 'Gold', 'Modern', 'Paper']],
    ['id' => 1856, 'title' => 'Dog on a bike Painting', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1857, 'title' => 'Water People Painting', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Black', 'Silver', 'Organic', 'Abstract', 'Abstract Expressionism', 'Ink', 'Large', 'Statement Piece', 'Fluid', 'Wood', 'Square', 'Modern']],
    ['id' => 1858, 'title' => 'Towers Painting', 'tags' => ['Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Wood', 'Modern']],
    ['id' => 1859, 'title' => 'Granular Painting', 'tags' => ['Geometric', 'Fine Art', 'Grey', 'Black', 'Abstract Expressionism', 'Silver', 'Abstract', 'Ink', 'Structured', 'Wood', 'Square', 'Modern']],
    ['id' => 1860, 'title' => 'Puzzle 2 Painting', 'tags' => ['Geometric', 'Fine Art', 'Grey', 'Black', 'Abstract Expressionism', 'Silver', 'Abstract', 'Ink', 'Structured', 'Wood', 'Modern']],
    ['id' => 1861, 'title' => 'Puzzle 1 Painting', 'tags' => ['Geometric', 'Fine Art', 'Grey', 'Black', 'Silver', 'Figurative', 'Abstract', 'Abstract Expressionism', 'Ink', 'Structured', 'Wood']],
    ['id' => 1862, 'title' => 'Trichome Painting', 'tags' => ['Steel', 'Fine Art', 'Purple', 'Grey', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Large', 'Pastel', 'Statement Piece', 'Wood', 'Modern']],
    ['id' => 1863, 'title' => 'Trichomes Painting', 'tags' => ['Brown', 'Steel', 'Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Large', 'Pastel', 'Statement Piece', 'Wood', 'Modern']],
    ['id' => 1864, 'title' => 'Grill Painting', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Gold', 'Modern', 'Paper']],
    ['id' => 1865, 'title' => 'Quilted Painting', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Gold', 'Modern', 'Paper']],
    ['id' => 1866, 'title' => 'Interactions Painting', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Gold', 'Modern', 'Paper']],
    ['id' => 1867, 'title' => 'Rush Painting', 'tags' => ['Brown', 'Fine Art', 'Acrylic', 'Black', 'Abstract', 'Abstract Expressionism', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1868, 'title' => 'Yorkie Painting', 'tags' => ['Minimalist', 'Fine Art', 'Acrylic', 'Black', 'Abstract Expressionism', 'Abstract', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1869, 'title' => 'Night Sky Painting', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Gold', 'Modern', 'Paper']],
    ['id' => 2036, 'title' => 'Bold Painting', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Gold', 'Modern', 'Paper']],
    ['id' => 1871, 'title' => 'Climbing Painting', 'tags' => ['Minimalist', 'Fine Art', 'Acrylic', 'Black', 'Abstract Expressionism', 'Abstract', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1872, 'title' => 'Dance Painting', 'tags' => ['Brown', 'Fine Art', 'Acrylic', 'Black', 'Abstract', 'Abstract Expressionism', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1873, 'title' => 'Smoke Painting', 'tags' => ['Brown', 'Fine Art', 'Acrylic', 'Black', 'Organic', 'Abstract', 'Abstract Expressionism', 'Luxury', 'Fluid', 'Gold', 'Modern', 'Paper']],
    ['id' => 1874, 'title' => 'Motion Painting', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Gold', 'Modern', 'Paper']],
    ['id' => 1875, 'title' => 'Listening Painting', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Gold', 'Modern', 'Paper']],
    ['id' => 1876, 'title' => 'Synapses Painting', 'tags' => ['Minimalist', 'Fine Art', 'Acrylic', 'Black', 'Abstract Expressionism', 'Abstract', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2043, 'title' => 'Microscope 7 Painting', 'tags' => ['Brown', 'Steel', 'Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Wood', 'Modern']],
    ['id' => 2044, 'title' => 'Microscope 6 Painting', 'tags' => ['Steel', 'Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Wood', 'Modern']],
    ['id' => 2045, 'title' => 'Microscope 5 Painting', 'tags' => ['Steel', 'Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Wood', 'Modern']],
    ['id' => 2046, 'title' => 'Microscope 4 Painting', 'tags' => ['Brown', 'Steel', 'Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Wood', 'Gold', 'Modern']],
    ['id' => 2047, 'title' => 'Microscope 3 Painting', 'tags' => ['Steel', 'Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Wood', 'Modern']],
    ['id' => 2048, 'title' => 'Microscope 2 Painting', 'tags' => ['Brown', 'Steel', 'Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Oil', 'Wood', 'Modern']],
    ['id' => 2049, 'title' => 'Microscope 1 Painting', 'tags' => ['Minimalist', 'Fine Art', 'Steel', 'Grey', 'Black', 'Abstract Expressionism', 'Abstract', 'Ink', 'Wood', 'Modern']],
    ['id' => 1895, 'title' => 'Pieces of Red Collage', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Beige', 'Wood', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 1897, 'title' => 'Paper Peace Collage', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Silver', 'Abstract', 'Abstract Expressionism', 'Wood', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 1902, 'title' => 'Business Mulch Collage', 'tags' => ['Expressionism', 'Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Wood', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 1903, 'title' => 'Office Work Mulch Collage', 'tags' => ['Brown', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Pop Art', 'Wood', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 1605, 'title' => 'Blue Glacier Painting', 'tags' => ['Grey', 'Black', 'Purple']],
    ['id' => 1601, 'title' => 'Waves Painting', 'tags' => ['Grey', 'Black', 'Silver', 'Pink', 'Organic', 'Fluid']],
    ['id' => 1711, 'title' => 'Meeting in the Middle', 'tags' => ['Brown', 'Expressionism', 'Conceptual', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Wood']],
    ['id' => 1709, 'title' => 'Finger print', 'tags' => ['Expressionism', 'Conceptual', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Large', 'Statement Piece', 'Wood']],
    ['id' => 1708, 'title' => 'self portrait 1', 'tags' => ['Minimalist', 'Fine Art', 'Black', 'Abstract Expressionism', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1856, 'title' => 'Dog on a bike', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2077, 'title' => 'City at Night Mulch Series', 'tags' => ['Brown', 'Square', 'Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Wood', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2078, 'title' => 'Close up Mulch Series', 'tags' => ['Brown', 'Square', 'Fine Art', 'Grey', 'Black', 'Abstract', 'Pink', 'Abstract Expressionism', 'Wood', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 1895, 'title' => 'Pieces of Red', 'tags' => ['Brown', 'Fine Art', 'Black', 'Silver', 'Pink', 'Abstract', 'Abstract Expressionism', 'Wood', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2080, 'title' => 'Red and Black Mulch Series', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Wood', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2081, 'title' => 'Jaguar', 'tags' => ['Fine Art', 'Grey', 'Black', 'Abstract', 'Pink', 'Abstract Expressionism', 'Beige', 'Modern']],
    ['id' => 2082, 'title' => 'Megapixels', 'tags' => ['Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Beige', 'Modern']],
    ['id' => 2083, 'title' => 'ESM S17', 'tags' => ['Fine Art', 'Grey', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Beige', 'Modern']],
    ['id' => 2084, 'title' => 'Fire Flow', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Organic', 'Abstract', 'Abstract Expressionism', 'Ink', 'Fluid', 'Gold', 'Modern', 'Paper']],
    ['id' => 2085, 'title' => 'Owls in Fall', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Acrylic', 'Abstract', 'Abstract Expressionism', 'Ink', 'Gold', 'Modern', 'Paper']],
    ['id' => 2086, 'title' => 'Connectivity', 'tags' => ['Minimalist', 'Fine Art', 'Black', 'Abstract Expressionism', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2087, 'title' => 'Atomic Flow', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Organic', 'Abstract', 'Abstract Expressionism', 'Ink', 'Fluid', 'Gold', 'Modern', 'Paper']],
    ['id' => 2088, 'title' => 'Trees', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Organic', 'Abstract', 'Abstract Expressionism', 'Ink', 'Fluid', 'Gold', 'Modern', 'Paper']],
    ['id' => 2089, 'title' => 'Animal Kingdom', 'tags' => ['Fine Art', 'Grey', 'Black', 'Acrylic', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2090, 'title' => 'Clean Hands', 'tags' => ['Conceptual', 'Fine Art', 'Minimalist', 'Grey', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Ink', 'Gold', 'Modern', 'Paper']],
    ['id' => 2091, 'title' => 'Reflection', 'tags' => ['Fine Art', 'Grey', 'Acrylic', 'Silver', 'Abstract', 'Abstract Expressionism', 'Green', 'Gold', 'Modern', 'Paper']],
    ['id' => 2092, 'title' => 'Eggs and Eyes', 'tags' => ['Brown', 'Fine Art', 'Black', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2093, 'title' => 'Moon Dance', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Airbrush', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2094, 'title' => 'Floating Leaves', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2095, 'title' => 'Arrowheads', 'tags' => ['Minimalist', 'Fine Art', 'Black', 'Abstract Expressionism', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2096, 'title' => 'campground', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2097, 'title' => 'Puzzle', 'tags' => ['Brown', 'Geometric', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Structured', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2098, 'title' => 'Streams and Ponds', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2099, 'title' => 'Cluster of Caps', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2100, 'title' => 'Duck pond', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2101, 'title' => 'Creek Bottom', 'tags' => ['Minimalist', 'Fine Art', 'Black', 'Abstract Expressionism', 'Abstract', 'Ink', 'Pop Art', 'Luxury', 'Gold', 'Paper']],
    ['id' => 2102, 'title' => 'Organic Mushrooms', 'tags' => ['Brown', 'Fine Art', 'Black', 'Organic', 'Abstract', 'Abstract Expressionism', 'Airbrush', 'Luxury', 'Fluid', 'Gold', 'Modern', 'Paper']],
    ['id' => 2103, 'title' => 'Stones', 'tags' => ['Minimalist', 'Fine Art', 'Black', 'Abstract Expressionism', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2104, 'title' => 'Cubes', 'tags' => ['Geometric', 'Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Structured', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2105, 'title' => 'Seed pods', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2106, 'title' => 'Excited Bird', 'tags' => ['Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2107, 'title' => 'Mushroom Exclamation', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Abstract Expressionism', 'Abstract', 'Ink', 'Gold', 'Modern', 'Paper']],
    ['id' => 2108, 'title' => 'Snake and Rocks', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2109, 'title' => 'Shapeshifter', 'tags' => ['Minimalist', 'Fine Art', 'Black', 'Abstract Expressionism', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2110, 'title' => 'Coiled Snake', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2111, 'title' => 'Avacado Snack', 'tags' => ['Brown', 'Conceptual', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Paper']],
    ['id' => 2112, 'title' => 'Gold Shapes', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2113, 'title' => 'Musical Embrace', 'tags' => ['Brown', 'Conceptual', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Paper']],
    ['id' => 2114, 'title' => 'Organic food', 'tags' => ['Fine Art', 'Grey', 'Black', 'Organic', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Fluid', 'Gold', 'Modern', 'Paper']],
    ['id' => 2115, 'title' => 'Snake Eggs', 'tags' => ['Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2116, 'title' => 'Brush Strokes', 'tags' => ['Brown', 'Fine Art', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 2117, 'title' => 'Blanket', 'tags' => ['Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1872, 'title' => 'Dance', 'tags' => ['Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Luxury', 'Gold', 'Modern', 'Paper']],
    ['id' => 1608, 'title' => 'Bloom', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Black', 'Acrylic', 'Organic', 'Abstract', 'Abstract Expressionism', 'Luxury', 'Fluid', 'Gold', 'Modern', 'Paper']],
    ['id' => 2120, 'title' => 'Organic Shapes', 'tags' => ['Minimalist', 'Fine Art', 'Acrylic', 'Black', 'Organic', 'Abstract', 'Abstract Expressionism', 'Luxury', 'Fluid', 'Gold', 'Modern', 'Paper']],
    ['id' => 2121, 'title' => 'Silver', 'tags' => ['Brown', 'Conceptual', 'Fine Art', 'Grey', 'Silver', 'Abstract', 'Abstract Expressionism', 'Acrylic', 'Paper']],
    ['id' => 2122, 'title' => 'Fortune', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Silver', 'Abstract', 'Abstract Expressionism', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 1607, 'title' => 'Transformation', 'tags' => ['Brown', 'Fine Art', 'Silver', 'Abstract', 'Abstract Expressionism', 'Beige', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2124, 'title' => 'Golden Nugget', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Gold', 'Modern', 'Paper']],
    ['id' => 1606, 'title' => 'Golden Rule', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Acrylic', 'Abstract Expressionism', 'Abstract', 'Gold', 'Modern', 'Paper']],
    ['id' => 2126, 'title' => 'Feather trees', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Grey', 'Organic', 'Abstract', 'Abstract Expressionism', 'Ink', 'Fluid', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2127, 'title' => 'Magic Carpet', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Black', 'Abstract', 'Abstract Expressionism', 'Ink', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2128, 'title' => 'Screen', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Grey', 'Abstract Expressionism', 'Abstract', 'Ink', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2129, 'title' => 'Spring Blooms', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Silver', 'Organic', 'Abstract', 'Abstract Expressionism', 'Ink', 'Fluid', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2130, 'title' => 'Celebrate', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Grey', 'Abstract Expressionism', 'Abstract', 'Ink', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2131, 'title' => 'Anemones', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2132, 'title' => 'Coral', 'tags' => ['Brown', 'Fine Art', 'Grey', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2133, 'title' => 'Existance', 'tags' => ['Brown', 'Minimalist', 'Fine Art', 'Grey', 'Abstract Expressionism', 'Abstract', 'Ink', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2134, 'title' => 'Fireworks', 'tags' => ['Brown', 'Expressionism', 'Fine Art', 'Grey', 'Silver', 'Abstract', 'Abstract Expressionism', 'Ink', 'Acrylic', 'Modern', 'Paper']],
    ['id' => 2135, 'title' => 'Synapse', 'tags' => ['Brown', 'Grey', 'Silver', 'Abstract', 'Ink', 'Acrylic', 'Paper']],
    ['id' => 2136, 'title' => 'Stick men', 'tags' => ['Brown', 'Minimalist', 'Grey', 'Abstract', 'Ink', 'Acrylic', 'Paper']],
    ['id' => 2137, 'title' => 'Descending', 'tags' => ['Brown', 'Grey', 'Black', 'Abstract', 'Acrylic', 'Paper']],
    ['id' => 2138, 'title' => 'lifeforce', 'tags' => ['Brown', 'Grey', 'Silver', 'Abstract', 'Acrylic', 'Paper']],
    ['id' => 2139, 'title' => 'Turquoise and Peppers', 'tags' => ['Brown', 'Grey', 'Black', 'Abstract', 'Acrylic', 'Paper']],
    ['id' => 2140, 'title' => 'Turquoise blend', 'tags' => ['Brown', 'Grey', 'Abstract', 'Green', 'Acrylic', 'Paper']],
    ['id' => 2141, 'title' => 'Turquoise stretch', 'tags' => ['Brown', 'Minimalist', 'Grey', 'Abstract', 'Acrylic', 'Paper']],
    ['id' => 2142, 'title' => 'Turquoise Circuit board', 'tags' => ['Brown', 'Geometric', 'Minimalist', 'Grey', 'Abstract', 'Structured', 'Acrylic', 'Paper']],
    ['id' => 2143, 'title' => 'Blast of Blue on Red', 'tags' => ['Grey', 'Silver', 'Abstract', 'Gold', 'Acrylic', 'Paper']],
    ['id' => 2144, 'title' => 'Blue Gold', 'tags' => ['Brown', 'Black', 'Abstract', 'Green', 'Acrylic', 'Paper']],
    ['id' => 1605, 'title' => 'Blue Glacier', 'tags' => ['Minimalist', 'Grey', 'Black', 'Abstract', 'Acrylic', 'Paper']],
    ['id' => 2146, 'title' => 'Blue Wave', 'tags' => ['Minimalist', 'Grey', 'Black', 'Organic', 'Abstract', 'Fluid', 'Acrylic', 'Paper']],
    ['id' => 2147, 'title' => 'Blue Mesh', 'tags' => ['Minimalist', 'Grey', 'Black', 'Abstract', 'Acrylic', 'Paper']],
    ['id' => 2148, 'title' => 'Cold Blue', 'tags' => ['Minimalist', 'Grey', 'Black', 'Abstract', 'Acrylic', 'Paper']],
    ['id' => 1602, 'title' => 'Blue Storm', 'tags' => ['Minimalist', 'Grey', 'Black', 'Abstract', 'Acrylic', 'Paper']],
    ['id' => 2150, 'title' => 'No Public Shrooms Limited Edition of 1', 'tags' => ['Expressionism', 'Metal', 'Grey', 'Silver', 'Beige', 'Blue', 'Stainless Steel']],
    ['id' => 2150, 'title' => 'No Public Shrooms Limited Edition of 1', 'tags' => ['Expressionism', 'Metal', 'Grey', 'Black', 'Silver', 'Stainless Steel']],
    ['id' => 2152, 'title' => 'Start Sign Limited Edition of 1', 'tags' => ['Brown', 'Expressionism', 'Metal', 'Grey', 'Silver', 'Stainless Steel', 'Square']],
    ['id' => 2153, 'title' => 'Right Way Limited Edition of 1', 'tags' => ['Brown', 'Expressionism', 'Metal', 'Silver', 'Stainless Steel', 'Gold']],
    ['id' => 2154, 'title' => 'NO PORKING', 'tags' => ['Brown', 'Expressionism', 'Metal', 'Minimalist', 'Silver', 'Stainless Steel']],
    ['id' => 2155, 'title' => 'GOLD SERIES 006', 'tags' => ['Brown', 'Black', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Paper']],
    ['id' => 2156, 'title' => 'GOLD SERIES 005', 'tags' => ['Minimalist', 'Black', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Paper']],
    ['id' => 2157, 'title' => 'GOLD SERIES 004', 'tags' => ['Minimalist', 'Black', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Paper']],
    ['id' => 2158, 'title' => 'GOLD SERIES 003', 'tags' => ['Minimalist', 'Black', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Paper']],
    ['id' => 2159, 'title' => 'GOLD SERIES 002', 'tags' => ['Grey', 'Black', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Paper']],
    ['id' => 2160, 'title' => 'GOLD SERIES 001', 'tags' => ['Brown', 'Black', 'Abstract', 'Ink', 'Luxury', 'Gold', 'Paper']],
    ['id' => 1601, 'title' => 'waves', 'tags' => ['Conceptual', 'Grey', 'Black', 'Silver', 'Pink', 'Figurative', 'Organic', 'Abstract Expressionism', 'Ink', 'Fluid', 'Modern', 'Paper']],
    ['id' => 1601, 'title' => 'Waves', 'tags' => ['Grey', 'Black', 'Silver', 'Pink', 'Organic', 'Fluid']],
    ['id' => 1602, 'title' => 'Blue Storm', 'tags' => ['Grey', 'Black', 'Minimalist']],
    ['id' => 1605, 'title' => 'Blue Glacier', 'tags' => ['Grey', 'Black', 'Purple']],
    ['id' => 1606, 'title' => 'Golden Rule', 'tags' => ['Brown', 'Minimalist', 'Gold']],
    ['id' => 1607, 'title' => 'Transformation', 'tags' => ['Brown', 'Silver', 'Beige']],
    ['id' => 1608, 'title' => 'Bloom', 'tags' => ['Brown', 'Grey', 'Black', 'Organic', 'Luxury', 'Fluid', 'Gold']],
];

echo "<pre>";
echo "Starting ROBUST Tag Update for " . count($items) . " pages...\n";

$updated = 0;
$errors = 0;

foreach ($items as $item) {
    $page_id = $item['id'];
    $tag_names = $item['tags'];
    
    if (empty($tag_names)) continue;
    
    // Resolve IDs
    $tag_ids = [];
    foreach ($tag_names as $name) {
        $term = term_exists($name, 'post_tag');
        if ($term) {
             $tag_ids[] = (int)$term['term_id'];
        } else {
            $new_term = wp_insert_term($name, 'post_tag');
            if (!is_wp_error($new_term)) {
                $tag_ids[] = (int)$new_term['term_id'];
            }
        }
    }
    
    // 2. Set Object Terms (Directly)
    // We use wp_set_object_terms instead of wp_set_post_tags for better control
    $result = wp_set_object_terms($page_id, $tag_ids, 'post_tag');
    
    if (is_wp_error($result)) {
        echo "❌ Error Page {$page_id}: " . $result->get_error_message() . "\n";
        $errors++;
    } else {
        // VERIFY IMMEDIATELELY
        $check = wp_get_object_terms($page_id, 'post_tag');
        $count = count($check);
        if ($count > 0) {
             echo "✅ Fixed Page {$page_id} ({$item['title']}) -> Now has $count tags.\n";
             $updated++;
        } else {
             echo "⚠️ WARNING: Page {$page_id} returned success but has 0 tags upon check.\n";
        }
    }
    
    // Clean cache to ensure updates stick in loop
    clean_post_cache($page_id);
}

echo "\n-----------------------------------\n";
echo "COMPLETED.\n";
echo "Effective Updates: $updated\n";
echo "</pre>";
?>
