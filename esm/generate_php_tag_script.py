import json

# Load the data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

items_payload = []

for item in data:
    if not item.get('wordpress_id'):
        continue
    
    tags = set()
    
    # 1. Colors
    if 'detected_colors' in item:
        for c in item['detected_colors']:
            tags.add(c)
            
    # 2. Styles
    if item.get('styles'):
        for s in item['styles'].split(','):
             tags.add(s.strip())
             
    # 3. Mediums
    if item.get('mediumsDetailed'):
        for m in item['mediumsDetailed'].split(','):
            tags.add(m.strip())
            
    # 4. Dimensions logic
    try:
        w = float(item.get('width', 0))
        h = float(item.get('height', 0))
        if w >= 48 or h >= 48: 
            tags.add('Large')
            tags.add('Statement Piece')
        if w > 0 and h > 0 and abs(w - h) < 1:
            tags.add('Square')
    except:
        pass
        
    clean_tags = [t for t in tags if t and len(t) > 1]
    
    if clean_tags:
        items_payload.append({
            'id': item['wordpress_id'],
            'title': item['title'],
            'tags': list(clean_tags)
        })

# Generate PHP Array String
php_data = "[\n"
for item in items_payload:
    # Escape quotes in title/tags for PHP string
    safe_title = item['title'].replace("'", "\\'")
    # Convert list to PHP array syntax: ['tag1', 'tag2']
    safe_tags = ", ".join([f"'{t.replace("'", "\\'")}'" for t in item['tags']])
    
    php_data += f"    ['id' => {item['id']}, 'title' => '{safe_title}', 'tags' => [{safe_tags}]],\n"
php_data += "];"

php_script = f"""<?php
// AUTO-GENERATED TAG UPDATE SCRIPT
// PURPOSE: Apply tags to Pages programmatically
// LOAD WORDPRESS
require_once('wp-load.php');

// Increase time limit for batch processing
set_time_limit(300);

$items = {php_data}

echo "<pre>";
echo "Starting Batch Tag Update for " . count($items) . " pages...\\n";

$updated = 0;
$errors = 0;

foreach ($items as $item) {{
    $page_id = $item['id'];
    $tag_names = $item['tags'];
    
    if (empty($tag_names)) continue;
    
    // 1. Ensure Tags Exist (and get IDs)
    $tag_ids = [];
    foreach ($tag_names as $name) {{
        // Check if exists
        $term = term_exists($name, 'post_tag');
        
        if ($term !== 0 && $term !== null) {{
             $tag_ids[] = (int)$term['term_id'];
        }} else {{
            // Create it
            $new_term = wp_insert_term($name, 'post_tag');
            if (!is_wp_error($new_term)) {{
                $tag_ids[] = (int)$new_term['term_id'];
            }}
        }}
    }}
    
    // 2. Assign to Page
    // Note: 'page' post type must support 'post_tag' taxonomy (enabled via functions.php previously)
    if (!empty($tag_ids)) {{
        $result = wp_set_post_tags($page_id, $tag_ids, false); // true = append, false = replace/set
        
        if (is_wp_error($result)) {{
            echo "❌ Error setting tags for Page {{$page_id}}: " . $result->get_error_message() . "\\n";
            $errors++;
        }} else {{
            // wp_set_post_tags returns array of term IDs on success
            echo "✅ Updated Page {{$page_id}} ({{$item['title']}}) with " . count($tag_ids) . " tags.\\n";
            $updated++;
        }}
    }}
}}

echo "\\n-----------------------------------\\n";
echo "COMPLETED.\\n";
echo "Updated: $updated\\n";
echo "Errors: $errors\\n";
echo "</pre>";
?>
"""

with open(r'C:\sandbox\esm\apply_tags_server.php', 'w', encoding='utf-8') as f:
    f.write(php_script)

print("Generated C:\\sandbox\\esm\\apply_tags_server.php with " + str(len(items_payload)) + " items.")
