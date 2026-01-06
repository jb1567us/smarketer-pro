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
    ['id' => 1704, 'title' => 'Red Planet', 'tags' => ['Square', 'Large', 'Red', 'Brown', 'Expressionism', 'Geometric', 'Texture', 'Orange', 'Statement Piece', 'Black', 'Abstract']],
    ['id' => 1927, 'title' => 'Portal', 'tags' => ['Fine Art', 'Oil', 'Minimalist', 'Red', 'Brown', 'Expressionism', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Abstract']],
    ['id' => 1928, 'title' => 'Portal 2', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Conceptual', 'Grey', 'Paper', 'Pink', 'Gold', 'Abstract']],
    ['id' => 1708, 'title' => 'self portrait 1', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1629, 'title' => 'Convergence', 'tags' => ['Wood', 'Abstract', 'Brown', 'Abstract Expressionism', 'Expressionism', 'Ink', 'Conceptual', 'Grey', 'Silver']],
    ['id' => 1630, 'title' => 'Puzzled', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Structured', 'Luxury', 'Geometric', 'Ink', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1709, 'title' => 'Finger print', 'tags' => ['Wood', 'Large', 'Abstract', 'Brown', 'Abstract Expressionism', 'Expressionism', 'Ink', 'Conceptual', 'Grey', 'Statement Piece', 'Silver']],
    ['id' => 1710, 'title' => 'Sheet Music', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Pop Art', 'Paper', 'Gold', 'Abstract']],
    ['id' => 1711, 'title' => 'Meeting in the Middle', 'tags' => ['Wood', 'Abstract', 'Brown', 'Abstract Expressionism', 'Expressionism', 'Ink', 'Conceptual', 'Grey', 'Black', 'Silver']],
    ['id' => 1764, 'title' => 'Caviar', 'tags' => ['Abstract', 'Brown', 'Contemporary', 'Ink', 'Geometric', 'Pop Art', 'Paper', 'Grey', 'Beige', 'Black & White', 'Silver']],
    ['id' => 1852, 'title' => 'Heart Work Painting', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Grey', 'Modern', 'Gold', 'Abstract']],
    ['id' => 1945, 'title' => 'Portal 1 Painting', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Paper', 'Conceptual', 'Grey', 'Modern', 'Paint', 'Pink', 'Gold', 'Abstract']],
    ['id' => 1854, 'title' => 'Morning Joe Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1855, 'title' => 'Unity Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Modern', 'Gold', 'Abstract']],
    ['id' => 1856, 'title' => 'Dog on a bike Painting', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1857, 'title' => 'Water People Painting', 'tags' => ['Wood', 'Fine Art', 'Large', 'Square', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Fluid', 'Grey', 'Organic', 'Statement Piece', 'Modern', 'Black', 'Silver']],
    ['id' => 1858, 'title' => 'Towers Painting', 'tags' => ['Wood', 'Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Grey', 'Beige', 'Modern', 'Black', 'Abstract']],
    ['id' => 1859, 'title' => 'Granular Painting', 'tags' => ['Wood', 'Fine Art', 'Square', 'Abstract', 'Brown', 'Abstract Expressionism', 'Structured', 'Ink', 'Geometric', 'Grey', 'Modern', 'Black', 'Silver']],
    ['id' => 1860, 'title' => 'Puzzle 2 Painting', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Structured', 'Ink', 'Geometric', 'Grey', 'Modern', 'Black', 'Silver']],
    ['id' => 1861, 'title' => 'Puzzle 1 Painting', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Structured', 'Ink', 'Geometric', 'Figurative', 'Grey', 'Black', 'Silver']],
    ['id' => 1862, 'title' => 'Trichome Painting', 'tags' => ['Wood', 'Fine Art', 'Large', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Grey', 'Steel', 'Statement Piece', 'Modern', 'Pastel', 'Silver']],
    ['id' => 1863, 'title' => 'Trichomes Painting', 'tags' => ['Wood', 'Fine Art', 'Large', 'Brown', 'Abstract Expressionism', 'Ink', 'Grey', 'Steel', 'Statement Piece', 'Modern', 'Black', 'Pastel', 'Abstract']],
    ['id' => 1864, 'title' => 'Grill Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 1865, 'title' => 'Quilted Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 1866, 'title' => 'Interactions Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 1867, 'title' => 'Rush Painting', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Acrylic', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1868, 'title' => 'Yorkie Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Acrylic', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1869, 'title' => 'Night Sky Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2036, 'title' => 'Bold Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 1871, 'title' => 'Climbing Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Acrylic', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1872, 'title' => 'Dance Painting', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1873, 'title' => 'Smoke Painting', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Fluid', 'Acrylic', 'Organic', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1874, 'title' => 'Motion Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 1875, 'title' => 'Listening Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 1876, 'title' => 'Synapses Painting', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Acrylic', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2043, 'title' => 'Microscope 7 Painting', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Grey', 'Steel', 'Modern', 'Black', 'Silver']],
    ['id' => 2044, 'title' => 'Microscope 6 Painting', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Grey', 'Steel', 'Modern', 'Black', 'Silver']],
    ['id' => 2045, 'title' => 'Microscope 5 Painting', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Grey', 'Steel', 'Modern', 'Black', 'Silver']],
    ['id' => 2046, 'title' => 'Microscope 4 Painting', 'tags' => ['Wood', 'Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Grey', 'Steel', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2047, 'title' => 'Microscope 3 Painting', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Grey', 'Steel', 'Modern', 'Black', 'Silver']],
    ['id' => 2048, 'title' => 'Microscope 2 Painting', 'tags' => ['Wood', 'Fine Art', 'Oil', 'Brown', 'Abstract Expressionism', 'Grey', 'Steel', 'Modern', 'Black', 'Abstract']],
    ['id' => 2049, 'title' => 'Microscope 1 Painting', 'tags' => ['Wood', 'Fine Art', 'Minimalist', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Grey', 'Steel', 'Modern', 'Black', 'Silver']],
    ['id' => 1895, 'title' => 'Pieces of Red Collage', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Black', 'Silver']],
    ['id' => 1897, 'title' => 'Paper Peace Collage', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Pink', 'Silver']],
    ['id' => 1902, 'title' => 'Business Mulch Collage', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Expressionism', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Black', 'Silver']],
    ['id' => 1903, 'title' => 'Office Work Mulch Collage', 'tags' => ['Wood', 'Abstract', 'Brown', 'Abstract Expressionism', 'Paper', 'Pop Art', 'Acrylic', 'Grey', 'Modern', 'Black', 'Silver']],
    ['id' => 1605, 'title' => 'Blue Glacier Painting', 'tags' => ['Black', 'Brown', 'Grey']],
    ['id' => 1601, 'title' => 'Waves Painting', 'tags' => ['Brown', 'Fluid', 'Organic', 'Black', 'Pink', 'Silver']],
    ['id' => 1711, 'title' => 'Meeting in the Middle', 'tags' => ['Wood', 'Abstract', 'Brown', 'Abstract Expressionism', 'Expressionism', 'Ink', 'Conceptual', 'Grey', 'Black', 'Silver']],
    ['id' => 1709, 'title' => 'Finger print', 'tags' => ['Wood', 'Large', 'Abstract', 'Brown', 'Abstract Expressionism', 'Expressionism', 'Ink', 'Conceptual', 'Grey', 'Statement Piece', 'Silver']],
    ['id' => 1708, 'title' => 'self portrait 1', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1856, 'title' => 'Dog on a bike', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2077, 'title' => 'City at Night Mulch Series', 'tags' => ['Wood', 'Fine Art', 'Square', 'Abstract', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Black', 'Silver']],
    ['id' => 2078, 'title' => 'Close up Mulch Series', 'tags' => ['Wood', 'Fine Art', 'Square', 'White', 'Abstract', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Silver']],
    ['id' => 1895, 'title' => 'Pieces of Red', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Black', 'Silver']],
    ['id' => 2080, 'title' => 'Red and Black Mulch Series', 'tags' => ['Wood', 'Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Black', 'Silver']],
    ['id' => 2081, 'title' => 'Jaguar', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Beige', 'Modern', 'Black', 'Pink', 'Abstract']],
    ['id' => 2082, 'title' => 'Megapixels', 'tags' => ['Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Beige', 'Modern', 'Black', 'Silver']],
    ['id' => 2083, 'title' => 'ESM S17', 'tags' => ['Fine Art', 'Abstract', 'Abstract Expressionism', 'Beige', 'Modern', 'Black', 'Pink', 'Silver']],
    ['id' => 2084, 'title' => 'Fire Flow', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Fluid', 'Acrylic', 'Grey', 'Organic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2085, 'title' => 'Owls in Fall', 'tags' => ['Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Gold', 'Silver']],
    ['id' => 2086, 'title' => 'Connectivity', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2087, 'title' => 'Atomic Flow', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Fluid', 'Organic', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2088, 'title' => 'Trees', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Fluid', 'Grey', 'Organic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2089, 'title' => 'Animal Kingdom', 'tags' => ['Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Gold', 'Silver']],
    ['id' => 2090, 'title' => 'Clean Hands', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Conceptual', 'Acrylic', 'Grey', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2091, 'title' => 'Reflection', 'tags' => ['Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Gold', 'Silver']],
    ['id' => 2092, 'title' => 'Eggs and Eyes', 'tags' => ['Fine Art', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Silver']],
    ['id' => 2093, 'title' => 'Moon Dance', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Airbrush', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2094, 'title' => 'Floating Leaves', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2095, 'title' => 'Arrowheads', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2096, 'title' => 'campground', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2097, 'title' => 'Puzzle', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Structured', 'Luxury', 'Geometric', 'Ink', 'Paper', 'Grey', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2098, 'title' => 'Streams and Ponds', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Grey', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2099, 'title' => 'Cluster of Caps', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Grey', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2100, 'title' => 'Duck pond', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2101, 'title' => 'Creek Bottom', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Pop Art', 'Paper', 'Black', 'Gold', 'Abstract']],
    ['id' => 2102, 'title' => 'Organic Mushrooms', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Fluid', 'Organic', 'Airbrush', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2103, 'title' => 'Stones', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2104, 'title' => 'Cubes', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Structured', 'Luxury', 'Geometric', 'Ink', 'Paper', 'Grey', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2105, 'title' => 'Seed pods', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2106, 'title' => 'Excited Bird', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2107, 'title' => 'Mushroom Exclamation', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2108, 'title' => 'Snake and Rocks', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2109, 'title' => 'Shapeshifter', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2110, 'title' => 'Coiled Snake', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2111, 'title' => 'Avacado Snack', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Conceptual', 'Grey', 'Paper', 'Black', 'Gold', 'Abstract']],
    ['id' => 2112, 'title' => 'Gold Shapes', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Grey', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2113, 'title' => 'Musical Embrace', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Conceptual', 'Paper', 'Black', 'Gold', 'Abstract']],
    ['id' => 2114, 'title' => 'Organic food', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Fluid', 'Organic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2115, 'title' => 'Snake Eggs', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2116, 'title' => 'Brush Strokes', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2117, 'title' => 'Blanket', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Grey', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1872, 'title' => 'Dance', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Ink', 'Luxury', 'Paper', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 1608, 'title' => 'Bloom', 'tags' => ['Fine Art', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Fluid', 'Acrylic', 'Organic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 2120, 'title' => 'Organic Shapes', 'tags' => ['Fine Art', 'Minimalist', 'Brown', 'Abstract Expressionism', 'Luxury', 'Paper', 'Fluid', 'Acrylic', 'Organic', 'Modern', 'Black', 'Gold', 'Abstract']],
    ['id' => 2121, 'title' => 'Silver', 'tags' => ['Fine Art', 'Red', 'Abstract', 'Brown', 'Abstract Expressionism', 'Conceptual', 'Acrylic', 'Grey', 'Paper', 'Silver']],
    ['id' => 2122, 'title' => 'Fortune', 'tags' => ['Fine Art', 'Red', 'Abstract', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Grey', 'Beige', 'Modern', 'Silver']],
    ['id' => 1607, 'title' => 'Transformation', 'tags' => ['Fine Art', 'White', 'Red', 'Abstract', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Beige', 'Modern', 'Silver']],
    ['id' => 2124, 'title' => 'Golden Nugget', 'tags' => ['Fine Art', 'Minimalist', 'Red', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Modern', 'Gold', 'Abstract']],
    ['id' => 1606, 'title' => 'Golden Rule', 'tags' => ['Fine Art', 'Minimalist', 'Red', 'Abstract Expressionism', 'Paper', 'Acrylic', 'Modern', 'Pink', 'Gold', 'Abstract']],
    ['id' => 2126, 'title' => 'Feather trees', 'tags' => ['Fine Art', 'Minimalist', 'Red', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Fluid', 'Acrylic', 'Grey', 'Organic', 'Modern', 'Abstract']],
    ['id' => 2127, 'title' => 'Magic Carpet', 'tags' => ['Fine Art', 'Red', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Abstract']],
    ['id' => 2128, 'title' => 'Screen', 'tags' => ['Fine Art', 'Minimalist', 'Red', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Abstract']],
    ['id' => 2129, 'title' => 'Spring Blooms', 'tags' => ['Fine Art', 'Red', 'Abstract', 'Ink', 'Abstract Expressionism', 'Paper', 'Fluid', 'Acrylic', 'Grey', 'Organic', 'Modern', 'Silver']],
    ['id' => 2130, 'title' => 'Celebrate', 'tags' => ['Fine Art', 'Minimalist', 'Red', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Abstract']],
    ['id' => 2131, 'title' => 'Anemones', 'tags' => ['Fine Art', 'Red', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Silver']],
    ['id' => 2132, 'title' => 'Coral', 'tags' => ['Fine Art', 'Red', 'Abstract', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Silver']],
    ['id' => 2133, 'title' => 'Existance', 'tags' => ['Fine Art', 'Minimalist', 'Red', 'Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Abstract']],
    ['id' => 2134, 'title' => 'Fireworks', 'tags' => ['Fine Art', 'Red', 'Abstract', 'Brown', 'Abstract Expressionism', 'Expressionism', 'Ink', 'Paper', 'Acrylic', 'Grey', 'Modern', 'Silver']],
    ['id' => 2135, 'title' => 'Synapse', 'tags' => ['Red', 'Abstract', 'Brown', 'Ink', 'Acrylic', 'Grey', 'Paper', 'Silver']],
    ['id' => 2136, 'title' => 'Stick men', 'tags' => ['Minimalist', 'Red', 'Brown', 'Ink', 'Acrylic', 'Grey', 'Paper', 'Abstract']],
    ['id' => 2137, 'title' => 'Descending', 'tags' => ['Red', 'Brown', 'Acrylic', 'Grey', 'Paper', 'Black', 'Abstract']],
    ['id' => 2138, 'title' => 'lifeforce', 'tags' => ['Red', 'Brown', 'Silver', 'Acrylic', 'Grey', 'Paper', 'Abstract']],
    ['id' => 2139, 'title' => 'Turquoise and Peppers', 'tags' => ['Red', 'Brown', 'Acrylic', 'Grey', 'Paper', 'Black', 'Abstract']],
    ['id' => 2140, 'title' => 'Turquoise blend', 'tags' => ['Red', 'Brown', 'Acrylic', 'Grey', 'Paper', 'Abstract']],
    ['id' => 2141, 'title' => 'Turquoise stretch', 'tags' => ['Minimalist', 'Brown', 'Acrylic', 'Grey', 'Paper', 'Abstract']],
    ['id' => 2142, 'title' => 'Turquoise Circuit board', 'tags' => ['Minimalist', 'Red', 'Brown', 'Structured', 'Geometric', 'Acrylic', 'Grey', 'Paper', 'Abstract']],
    ['id' => 2143, 'title' => 'Blast of Blue on Red', 'tags' => ['Red', 'Abstract', 'Acrylic', 'Grey', 'Paper', 'Gold', 'Silver']],
    ['id' => 2144, 'title' => 'Blue Gold', 'tags' => ['Brown', 'Acrylic', 'Paper', 'Black', 'Abstract']],
    ['id' => 1605, 'title' => 'Blue Glacier', 'tags' => ['Minimalist', 'Brown', 'Acrylic', 'Grey', 'Paper', 'Black', 'Abstract']],
    ['id' => 2146, 'title' => 'Blue Wave', 'tags' => ['Minimalist', 'Brown', 'Fluid', 'Acrylic', 'Grey', 'Organic', 'Paper', 'Black', 'Abstract']],
    ['id' => 2147, 'title' => 'Blue Mesh', 'tags' => ['Minimalist', 'Brown', 'Acrylic', 'Grey', 'Paper', 'Black', 'Abstract']],
    ['id' => 2148, 'title' => 'Cold Blue', 'tags' => ['Minimalist', 'Brown', 'Acrylic', 'Grey', 'Paper', 'Black', 'Abstract']],
    ['id' => 1602, 'title' => 'Blue Storm', 'tags' => ['Minimalist', 'Brown', 'Acrylic', 'Grey', 'Paper', 'Black', 'Abstract']],
    ['id' => 2150, 'title' => 'No Public Shrooms Limited Edition of 1', 'tags' => ['Stainless Steel', 'Expressionism', 'Blue', 'Grey', 'Beige', 'Silver', 'Metal']],
    ['id' => 2150, 'title' => 'No Public Shrooms Limited Edition of 1', 'tags' => ['Stainless Steel', 'Expressionism', 'Blue', 'Grey', 'Beige', 'Silver', 'Metal']],
    ['id' => 2152, 'title' => 'Start Sign Limited Edition of 1', 'tags' => ['Square', 'Red', 'Brown', 'Stainless Steel', 'Expressionism', 'Gold', 'Silver', 'Metal']],
    ['id' => 2153, 'title' => 'Right Way Limited Edition of 1', 'tags' => ['Red', 'Stainless Steel', 'Expressionism', 'Gold', 'Silver', 'Metal']],
    ['id' => 2154, 'title' => 'NO PORKING', 'tags' => ['Minimalist', 'Stainless Steel', 'Expressionism', 'Grey', 'Black', 'Gold', 'Silver', 'Metal']],
    ['id' => 2155, 'title' => 'GOLD SERIES 006', 'tags' => ['Ink', 'Luxury', 'Grey', 'Paper', 'Black', 'Gold', 'Abstract']],
    ['id' => 2156, 'title' => 'GOLD SERIES 005', 'tags' => ['Minimalist', 'Brown', 'Ink', 'Luxury', 'Paper', 'Black', 'Gold', 'Abstract']],
    ['id' => 2157, 'title' => 'GOLD SERIES 004', 'tags' => ['Minimalist', 'Brown', 'Ink', 'Luxury', 'Paper', 'Black', 'Gold', 'Abstract']],
    ['id' => 2158, 'title' => 'GOLD SERIES 003', 'tags' => ['Minimalist', 'Brown', 'Ink', 'Luxury', 'Paper', 'Black', 'Gold', 'Abstract']],
    ['id' => 2159, 'title' => 'GOLD SERIES 002', 'tags' => ['Brown', 'Ink', 'Luxury', 'Paper', 'Black', 'Gold', 'Abstract']],
    ['id' => 2160, 'title' => 'GOLD SERIES 001', 'tags' => ['Brown', 'Ink', 'Luxury', 'Paper', 'Black', 'Gold', 'Abstract']],
    ['id' => 1601, 'title' => 'waves', 'tags' => ['Brown', 'Abstract Expressionism', 'Ink', 'Paper', 'Conceptual', 'Fluid', 'Figurative', 'Organic', 'Modern', 'Black', 'Pink', 'Silver']],
    ['id' => 1601, 'title' => 'Waves', 'tags' => ['Brown', 'Fluid', 'Organic', 'Black', 'Pink', 'Silver']],
    ['id' => 1602, 'title' => 'Blue Storm', 'tags' => ['Black', 'Brown', 'Minimalist', 'Grey']],
    ['id' => 1605, 'title' => 'Blue Glacier', 'tags' => ['Black', 'Brown', 'Grey']],
    ['id' => 1606, 'title' => 'Golden Rule', 'tags' => ['Pink', 'Gold', 'Red', 'Minimalist']],
    ['id' => 1607, 'title' => 'Transformation', 'tags' => ['Pink', 'Red', 'Silver', 'Beige']],
    ['id' => 1608, 'title' => 'Bloom', 'tags' => ['Brown', 'Luxury', 'Fluid', 'Organic', 'Gold']],
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
