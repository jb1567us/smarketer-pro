<?php
// debug_filter_isolation_v3.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

// 1. Get Content via SQL (Robust)
// We know ID 213 is Anemones from previous logs
$id = 213;
$row = $wpdb->get_row("SELECT post_content FROM {$wpdb->posts} WHERE ID = $id");

if (!$row)
    die("ID $id NOT FOUND");
$content = $row->post_content;

echo "<h1>Filter Debug V3 (Anemones ID $id)</h1>";
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
        // Catch errors
        try {
            $current = call_user_func($func, $current);
        } catch (Exception $e) {
            echo "❌ CRASH in $name: " . $e->getMessage() . "<br>";
        }
        $newLen = strlen($current);

        echo "[P$prio] $name: $prevLen -> $newLen<br>";

        if ($newLen < 100 && $prevLen > 1000) {
            echo "🚨🚨🚨 MASSIVE DROP ABOVE 🚨🚨🚨<br>";
        }
    }
}
?>