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
        if item['title'] == 'Portal':
             print(f"DEBUG PORTAL TAGS GENERATED: {clean_tags}")
        items_payload.append({
            'id': item['wordpress_id'],
            'title': item['title'],
            'tags': list(clean_tags)
        })

# Generate PHP Array String
php_data = "[\n"
for item in items_payload:
    safe_title = item['title'].replace("'", "\\'")
    safe_tags = ", ".join([f"'{t.replace("'", "\\'")}'" for t in item['tags']])
    php_data += f"    ['id' => {item['id']}, 'title' => '{safe_title}', 'tags' => [{safe_tags}]],\n"
php_data += "];"

php_script = f"""<?php
// ROBUST TAG RE-APPLICATION SCRIPT
require_once('wp-load.php');
set_time_limit(300);

// 1. FORCE REGISTRATION (Crucial Step)
global $wp_taxonomies;
if (taxonomy_exists('post_tag')) {{
    register_taxonomy_for_object_type('post_tag', 'page');
}}

$items = {php_data}

echo "<pre>";
echo "Starting ROBUST Tag Update for " . count($items) . " pages...\\n";

$updated = 0;
$errors = 0;

foreach ($items as $item) {{
    $page_id = $item['id'];
    $tag_names = $item['tags'];
    
    if (empty($tag_names)) continue;
    
    // Resolve IDs
    $tag_ids = [];
    foreach ($tag_names as $name) {{
        $term = term_exists($name, 'post_tag');
        if ($term) {{
             $tag_ids[] = (int)$term['term_id'];
        }} else {{
            $new_term = wp_insert_term($name, 'post_tag');
            if (!is_wp_error($new_term)) {{
                $tag_ids[] = (int)$new_term['term_id'];
            }}
        }}
    }}
    
    // 2. Set Object Terms (Directly)
    // We use wp_set_object_terms instead of wp_set_post_tags for better control
    $result = wp_set_object_terms($page_id, $tag_ids, 'post_tag');
    
    if (is_wp_error($result)) {{
        echo "❌ Error Page {{$page_id}}: " . $result->get_error_message() . "\\n";
        $errors++;
    }} else {{
        // VERIFY IMMEDIATELELY
        $check = wp_get_object_terms($page_id, 'post_tag');
        $count = count($check);
        if ($count > 0) {{
             echo "✅ Fixed Page {{$page_id}} ({{$item['title']}}) -> Now has $count tags.\\n";
             $updated++;
        }} else {{
             echo "⚠️ WARNING: Page {{$page_id}} returned success but has 0 tags upon check.\\n";
        }}
    }}
    
    // Clean cache to ensure updates stick in loop
    clean_post_cache($page_id);
}}

echo "\\n-----------------------------------\\n";
echo "COMPLETED.\\n";
echo "Effective Updates: $updated\\n";
echo "</pre>";
?>
"""

with open(r'C:\sandbox\esm\reapply_tags.php', 'w', encoding='utf-8') as f:
    f.write(php_script)

print("Generated C:\\sandbox\\esm\\reapply_tags.php")
