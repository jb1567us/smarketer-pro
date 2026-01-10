<?php
// debug_filter_isolation_v2.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$slug = 'anemones';
$page = get_page_by_path($slug, OBJECT, 'page');
$content = $page->post_content;
echo "<h1>Filter Debug V2</h1>";
echo "Start Length: " . strlen($content) . "<br>";

global $wp_filter;
$tag = 'the_content';

$callbacks = [];
if (isset($wp_filter[$tag])) {
    foreach ($wp_filter[$tag] as $priority => $formats) {
        foreach ($formats as $idx => $data) {
            $callbacks[$priority][] = $data['function'];
        }
    }
}
ksort($callbacks);

$current = $content;
foreach ($callbacks as $prio => $funcs) {
    foreach ($funcs as $func) {
        // Name resolution
        if (is_string($func))
            $name = $func;
        elseif (is_array($func)) {
            $obj = $func[0];
            $method = $func[1];
            if (is_object($obj))
                $name = get_class($obj) . "->$method";
            else
                $name = "$obj::$method";
        } else {
            $name = "Closure";
        }

        $prevLen = strlen($current);
        $current = call_user_func($func, $current);
        $newLen = strlen($current);

        // Log ONLY if significant change
        if ($newLen < $prevLen * 0.5) {
            echo "<h2>🚨 CULPRIT FOUND: $name (Priority $prio)</h2>";
            echo "Reduced length form $prevLen to $newLen<br>";
            echo "Output Preview: " . htmlspecialchars(substr($current, 0, 200)) . "<br>";
        }
    }
}
?>