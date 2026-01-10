<?php
// AUTO-GENERATED TAG UPDATE SCRIPT
// PURPOSE: Apply tags to Pages programmatically
// LOAD WORDPRESS
require_once('wp-load.php');

// Increase time limit for batch processing
set_time_limit(300);

$items = [
    ['id' => 1704, 'title' => 'Red Planet', 'tags' => ['Statement Piece', 'Square', 'Large']],
    ['id' => 1927, 'title' => 'Portal', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Expressionism', 'Grey', 'Black', 'Fine Art', 'Art Deco', 'Oil']],
    ['id' => 1928, 'title' => 'Portal 2', 'tags' => ['Paper', 'Pink', 'Abstract', 'Ink', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Conceptual', 'Art Deco']],
    ['id' => 1708, 'title' => 'self portrait 1', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1629, 'title' => 'Convergence', 'tags' => ['Abstract', 'Ink', 'Expressionism', 'Grey', 'Abstract Expressionism', 'Black', 'Wood', 'Conceptual', 'Art Deco']],
    ['id' => 1630, 'title' => 'Puzzled', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1709, 'title' => 'Finger print', 'tags' => ['Abstract', 'Large', 'Ink', 'Statement Piece', 'Expressionism', 'Grey', 'Abstract Expressionism', 'Black', 'Wood', 'Conceptual', 'Art Deco']],
    ['id' => 1710, 'title' => 'Sheet Music', 'tags' => ['Paper', 'Abstract', 'Brown', 'Ink', 'Abstract Expressionism', 'Fine Art', 'Gold', 'Art Deco', 'Pop Art']],
    ['id' => 1711, 'title' => 'Meeting in the Middle', 'tags' => ['Abstract', 'Ink', 'Expressionism', 'Grey', 'Abstract Expressionism', 'Black', 'Wood', 'Conceptual', 'Art Deco']],
    ['id' => 1764, 'title' => 'Caviar', 'tags' => ['Paper', 'Geometric', 'Abstract', 'Contemporary', 'Ink', 'White', 'Grey', 'Black & White', 'Pop Art']],
    ['id' => 1852, 'title' => 'Heart Work Painting', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1945, 'title' => 'Portal 1 Painting', 'tags' => ['Paper', 'Pink', 'Abstract', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Paint', 'Conceptual']],
    ['id' => 1854, 'title' => 'Morning Joe Painting', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1855, 'title' => 'Unity Painting', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1856, 'title' => 'Dog on a bike Painting', 'tags' => ['Paper', 'Abstract', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1857, 'title' => 'Water People Painting', 'tags' => ['Abstract', 'Large', 'Ink', 'Modern', 'Statement Piece', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Square', 'Art Deco']],
    ['id' => 1858, 'title' => 'Towers Painting', 'tags' => ['Abstract', 'Ink', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco', 'Beige']],
    ['id' => 1859, 'title' => 'Granular Painting', 'tags' => ['Abstract', 'Ink', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Square', 'Art Deco']],
    ['id' => 1860, 'title' => 'Puzzle 2 Painting', 'tags' => ['Abstract', 'Ink', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 1861, 'title' => 'Puzzle 1 Painting', 'tags' => ['Figurative', 'Abstract', 'Ink', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 1862, 'title' => 'Trichome Painting', 'tags' => ['Pink', 'Abstract', 'Large', 'Steel', 'Ink', 'Pastel', 'Modern', 'Statement Piece', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 1863, 'title' => 'Trichomes Painting', 'tags' => ['Abstract', 'Large', 'Brown', 'Ink', 'Steel', 'Pastel', 'Modern', 'Statement Piece', 'Wood', 'Abstract Expressionism', 'Grey', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 1864, 'title' => 'Grill Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1865, 'title' => 'Quilted Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Abstract Expressionism', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1866, 'title' => 'Interactions Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1867, 'title' => 'Rush Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1868, 'title' => 'Yorkie Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1869, 'title' => 'Night Sky Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Abstract Expressionism', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2036, 'title' => 'Bold Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1871, 'title' => 'Climbing Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1872, 'title' => 'Dance Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1873, 'title' => 'Smoke Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1874, 'title' => 'Motion Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1875, 'title' => 'Listening Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Abstract Expressionism', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1876, 'title' => 'Synapses Painting', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2043, 'title' => 'Microscope 7 Painting', 'tags' => ['Pink', 'Abstract', 'Steel', 'Ink', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2044, 'title' => 'Microscope 6 Painting', 'tags' => ['Pink', 'Abstract', 'Steel', 'Ink', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2045, 'title' => 'Microscope 5 Painting', 'tags' => ['Abstract', 'Steel', 'Ink', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2046, 'title' => 'Microscope 4 Painting', 'tags' => ['Abstract', 'Steel', 'Ink', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2047, 'title' => 'Microscope 3 Painting', 'tags' => ['Abstract', 'Steel', 'Ink', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2048, 'title' => 'Microscope 2 Painting', 'tags' => ['Abstract', 'Steel', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco', 'Oil']],
    ['id' => 2049, 'title' => 'Microscope 1 Painting', 'tags' => ['Abstract', 'Steel', 'Ink', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 1895, 'title' => 'Pieces of Red Collage', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco', 'Beige']],
    ['id' => 1897, 'title' => 'Paper Peace Collage', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 1902, 'title' => 'Business Mulch Collage', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Modern', 'Expressionism', 'Grey', 'Abstract Expressionism', 'Black', 'Wood', 'Fine Art']],
    ['id' => 1903, 'title' => 'Office Work Mulch Collage', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Art Deco', 'Pop Art']],
    ['id' => 1605, 'title' => 'Blue Glacier Painting', 'tags' => ['Grey', 'Black']],
    ['id' => 1601, 'title' => 'Waves Painting', 'tags' => ['Grey', 'Black', 'Pink']],
    ['id' => 1711, 'title' => 'Meeting in the Middle', 'tags' => ['Abstract', 'Ink', 'Expressionism', 'Grey', 'Abstract Expressionism', 'Black', 'Wood', 'Conceptual', 'Art Deco']],
    ['id' => 1709, 'title' => 'Finger print', 'tags' => ['Abstract', 'Large', 'Ink', 'Statement Piece', 'Expressionism', 'Grey', 'Abstract Expressionism', 'Black', 'Wood', 'Conceptual', 'Art Deco']],
    ['id' => 1708, 'title' => 'self portrait 1', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1856, 'title' => 'Dog on a bike', 'tags' => ['Paper', 'Abstract', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2077, 'title' => 'City at Night Mulch Series', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Square', 'Art Deco']],
    ['id' => 2078, 'title' => 'Close up Mulch Series', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Square', 'Art Deco']],
    ['id' => 1895, 'title' => 'Pieces of Red', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2080, 'title' => 'Red and Black Mulch Series', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Wood', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2081, 'title' => 'Jaguar', 'tags' => ['Pink', 'Abstract', 'Modern', 'White', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco', 'Beige']],
    ['id' => 2082, 'title' => 'Megapixels', 'tags' => ['Pink', 'Abstract', 'Modern', 'White', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2083, 'title' => 'ESM S17', 'tags' => ['Pink', 'Abstract', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco', 'Beige']],
    ['id' => 2084, 'title' => 'Fire Flow', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2085, 'title' => 'Owls in Fall', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2086, 'title' => 'Connectivity', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2087, 'title' => 'Atomic Flow', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2088, 'title' => 'Trees', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2089, 'title' => 'Animal Kingdom', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2090, 'title' => 'Clean Hands', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Fine Art', 'Gold', 'Conceptual']],
    ['id' => 2091, 'title' => 'Reflection', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2092, 'title' => 'Eggs and Eyes', 'tags' => ['Paper', 'Pink', 'Abstract', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2093, 'title' => 'Moon Dance', 'tags' => ['Paper', 'Abstract', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco', 'Airbrush']],
    ['id' => 2094, 'title' => 'Floating Leaves', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2095, 'title' => 'Arrowheads', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2096, 'title' => 'campground', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2097, 'title' => 'Puzzle', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2098, 'title' => 'Streams and Ponds', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2099, 'title' => 'Cluster of Caps', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2100, 'title' => 'Duck pond', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2101, 'title' => 'Creek Bottom', 'tags' => ['Paper', 'Abstract', 'Ink', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco', 'Pop Art']],
    ['id' => 2102, 'title' => 'Organic Mushrooms', 'tags' => ['Paper', 'Abstract', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco', 'Airbrush']],
    ['id' => 2103, 'title' => 'Stones', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2104, 'title' => 'Cubes', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2105, 'title' => 'Seed pods', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2106, 'title' => 'Excited Bird', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2107, 'title' => 'Mushroom Exclamation', 'tags' => ['Paper', 'Abstract', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2108, 'title' => 'Snake and Rocks', 'tags' => ['Paper', 'Abstract', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2109, 'title' => 'Shapeshifter', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2110, 'title' => 'Coiled Snake', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2111, 'title' => 'Avacado Snack', 'tags' => ['Paper', 'Abstract', 'Ink', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Conceptual', 'Art Deco']],
    ['id' => 2112, 'title' => 'Gold Shapes', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2113, 'title' => 'Musical Embrace', 'tags' => ['Paper', 'Abstract', 'Brown', 'Ink', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Conceptual', 'Art Deco']],
    ['id' => 2114, 'title' => 'Organic food', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2115, 'title' => 'Snake Eggs', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2116, 'title' => 'Brush Strokes', 'tags' => ['Paper', 'Abstract', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2117, 'title' => 'Blanket', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1872, 'title' => 'Dance', 'tags' => ['Paper', 'Abstract', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1608, 'title' => 'Bloom', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2120, 'title' => 'Organic Shapes', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Modern', 'Abstract Expressionism', 'Black', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2121, 'title' => 'Silver', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Abstract Expressionism', 'Grey', 'Fine Art', 'Conceptual', 'Art Deco']],
    ['id' => 2122, 'title' => 'Fortune', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Abstract Expressionism', 'Grey', 'Fine Art', 'Art Deco']],
    ['id' => 1607, 'title' => 'Transformation', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'White', 'Abstract Expressionism', 'Fine Art', 'Art Deco']],
    ['id' => 2124, 'title' => 'Golden Nugget', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Abstract Expressionism', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 1606, 'title' => 'Golden Rule', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Modern', 'Abstract Expressionism', 'Fine Art', 'Gold', 'Art Deco']],
    ['id' => 2126, 'title' => 'Feather trees', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2127, 'title' => 'Magic Carpet', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2128, 'title' => 'Screen', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Grey', 'Fine Art', 'Art Deco']],
    ['id' => 2129, 'title' => 'Spring Blooms', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Grey', 'Fine Art', 'Art Deco']],
    ['id' => 2130, 'title' => 'Celebrate', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Grey', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2131, 'title' => 'Anemones', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Grey', 'Fine Art', 'Art Deco']],
    ['id' => 2132, 'title' => 'Coral', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Fine Art', 'Art Deco']],
    ['id' => 2133, 'title' => 'Existance', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Abstract Expressionism', 'Grey', 'Fine Art', 'Art Deco']],
    ['id' => 2134, 'title' => 'Fireworks', 'tags' => ['Paper', 'Pink', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Modern', 'Expressionism', 'Abstract Expressionism', 'Grey', 'Fine Art']],
    ['id' => 2135, 'title' => 'Synapse', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Grey']],
    ['id' => 2136, 'title' => 'Stick men', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Ink', 'Grey', 'Black']],
    ['id' => 2137, 'title' => 'Descending', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Grey', 'Black']],
    ['id' => 2138, 'title' => 'lifeforce', 'tags' => ['Paper', 'Acrylic', 'Abstract', 'Brown', 'White', 'Grey']],
    ['id' => 2139, 'title' => 'Turquoise and Peppers', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Grey', 'Black']],
    ['id' => 2140, 'title' => 'Turquoise blend', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Grey', 'Black']],
    ['id' => 2141, 'title' => 'Turquoise stretch', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Grey', 'Black']],
    ['id' => 2142, 'title' => 'Turquoise Circuit board', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Brown', 'Grey', 'Black']],
    ['id' => 2143, 'title' => 'Blast of Blue on Red', 'tags' => ['Paper', 'Abstract', 'Acrylic', 'Grey', 'Gold']],
    ['id' => 2144, 'title' => 'Blue Gold', 'tags' => ['Paper', 'Acrylic', 'Abstract', 'Brown', 'Black']],
    ['id' => 1605, 'title' => 'Blue Glacier', 'tags' => ['Paper', 'Acrylic', 'Abstract', 'Grey', 'Black']],
    ['id' => 2146, 'title' => 'Blue Wave', 'tags' => ['Paper', 'Acrylic', 'Abstract', 'Grey', 'Black']],
    ['id' => 2147, 'title' => 'Blue Mesh', 'tags' => ['Paper', 'Acrylic', 'Abstract', 'Grey', 'Black']],
    ['id' => 2148, 'title' => 'Cold Blue', 'tags' => ['Paper', 'Acrylic', 'Abstract', 'Grey', 'Black']],
    ['id' => 1602, 'title' => 'Blue Storm', 'tags' => ['Paper', 'Acrylic', 'Abstract', 'Grey', 'Black']],
    ['id' => 2150, 'title' => 'No Public Shrooms Limited Edition of 1', 'tags' => ['Metal', 'Expressionism', 'Grey', 'White', 'Black', 'Stainless Steel']],
    ['id' => 2150, 'title' => 'No Public Shrooms Limited Edition of 1', 'tags' => ['Pink', 'Metal', 'Expressionism', 'Grey', 'Black', 'Stainless Steel']],
    ['id' => 2152, 'title' => 'Start Sign Limited Edition of 1', 'tags' => ['Pink', 'Metal', 'Brown', 'Expressionism', 'Grey', 'Gold', 'Square', 'Stainless Steel']],
    ['id' => 2153, 'title' => 'Right Way Limited Edition of 1', 'tags' => ['Pink', 'Metal', 'Brown', 'Expressionism', 'Gold', 'Stainless Steel']],
    ['id' => 2154, 'title' => 'NO PORKING', 'tags' => ['Pink', 'Metal', 'Expressionism', 'Black', 'Gold', 'Stainless Steel']],
    ['id' => 2155, 'title' => 'GOLD SERIES 006', 'tags' => ['Paper', 'Abstract', 'Brown', 'Ink', 'Black', 'Gold']],
    ['id' => 2156, 'title' => 'GOLD SERIES 005', 'tags' => ['Paper', 'Abstract', 'Ink', 'Black', 'Gold']],
    ['id' => 2157, 'title' => 'GOLD SERIES 004', 'tags' => ['Paper', 'Abstract', 'Ink', 'Black', 'Gold']],
    ['id' => 2158, 'title' => 'GOLD SERIES 003', 'tags' => ['Paper', 'Abstract', 'Ink', 'Black', 'Gold']],
    ['id' => 2159, 'title' => 'GOLD SERIES 002', 'tags' => ['Paper', 'Abstract', 'Ink', 'Grey', 'Black', 'Gold']],
    ['id' => 2160, 'title' => 'GOLD SERIES 001', 'tags' => ['Paper', 'Abstract', 'Ink', 'Black', 'Gold']],
    ['id' => 1601, 'title' => 'waves', 'tags' => ['Paper', 'Figurative', 'Pink', 'Ink', 'Modern', 'Grey', 'Abstract Expressionism', 'Black', 'Conceptual']],
    ['id' => 1601, 'title' => 'Waves', 'tags' => ['Grey', 'Black', 'Pink']],
    ['id' => 1602, 'title' => 'Blue Storm', 'tags' => ['Grey', 'Black']],
    ['id' => 1605, 'title' => 'Blue Glacier', 'tags' => ['Grey', 'Black']],
    ['id' => 1606, 'title' => 'Golden Rule', 'tags' => ['Brown', 'Gold']],
    ['id' => 1607, 'title' => 'Transformation', 'tags' => ['Brown', 'Pink', 'White']],
    ['id' => 1608, 'title' => 'Bloom', 'tags' => ['Grey', 'Black', 'Gold']],
];

echo "<pre>";
echo "Starting Batch Tag Update for " . count($items) . " pages...\n";

$updated = 0;
$errors = 0;

foreach ($items as $item) {
    $page_id = $item['id'];
    $tag_names = $item['tags'];
    
    if (empty($tag_names)) continue;
    
    // 1. Ensure Tags Exist (and get IDs)
    $tag_ids = [];
    foreach ($tag_names as $name) {
        // Check if exists
        $term = term_exists($name, 'post_tag');
        
        if ($term !== 0 && $term !== null) {
             $tag_ids[] = (int)$term['term_id'];
        } else {
            // Create it
            $new_term = wp_insert_term($name, 'post_tag');
            if (!is_wp_error($new_term)) {
                $tag_ids[] = (int)$new_term['term_id'];
            }
        }
    }
    
    // 2. Assign to Page
    // Note: 'page' post type must support 'post_tag' taxonomy (enabled via functions.php previously)
    if (!empty($tag_ids)) {
        $result = wp_set_post_tags($page_id, $tag_ids, false); // true = append, false = replace/set
        
        if (is_wp_error($result)) {
            echo "❌ Error setting tags for Page {$page_id}: " . $result->get_error_message() . "\n";
            $errors++;
        } else {
            // wp_set_post_tags returns array of term IDs on success
            echo "✅ Updated Page {$page_id} ({$item['title']}) with " . count($tag_ids) . " tags.\n";
            $updated++;
        }
    }
}

echo "\n-----------------------------------\n";
echo "COMPLETED.\n";
echo "Updated: $updated\n";
echo "Errors: $errors\n";
echo "</pre>";
?>
