<?php
// debug_filter_isolation.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$slug = 'anemones';
$page = get_page_by_path($slug, OBJECT, 'page');
$content = $page->post_content;

echo "<h1>Filter Debug: Anemones</h1>";
echo "Initial Length: " . strlen($content) . "<br>";

global $wp_filter;
$tag = 'the_content';

if (!isset($wp_filter[$tag])) {
    die("No filters found for $tag");
}

$callbacks = [];
foreach ($wp_filter[$tag] as $priority => $formats) {
    foreach ($formats as $idx => $data) {
        $callbacks[$priority][] = $data['function'];
    }
}
ksort($callbacks);

$current = $content;
foreach ($callbacks as $prio => $funcs) {
    echo "<h3>Priority $prio</h3>";
    foreach ($funcs as $func) {
        // Get name
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

        try {
            $current = call_user_func($func, $current);
        } catch (Exception $e) {
            echo "❌ CRASH in $name: " . $e->getMessage() . "<br>";
        }

        $newLen = strlen($current);

        echo " - Run <b>$name</b>: ";
        if ($newLen == 0 && $prevLen > 0) {
            echo "<span style='color:red; font-weight:bold;'>EMPTY RESULT! (Culprit Found?)</span><br>";
        } elseif ($newLen < 100 && $prevLen > 1000) {
            echo "<span style='color:orange;'>Massive Truncation! ($prevLen -> $newLen)</span><br>";
        } else {
            echo "OK ($prevLen -> $newLen)<br>";
        }
    }
}

echo "<h3>Final Result Length: " . strlen($current) . "</h3>";
?>