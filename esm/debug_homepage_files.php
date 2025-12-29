<?php
echo "<h1>Diagnostic</h1>";
echo "Document Root: " . $_SERVER['DOCUMENT_ROOT'] . "<br>";
$file = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/themes/caviar-premium/front-page.php';
echo "Checking file: $file<br>";

if (file_exists($file)) {
    echo "File exists.<br>";
    echo "Last modified: " . date("F d Y H:i:s", filemtime($file)) . "<br>";
    $content = file_get_contents($file);
    if (strpos($content, 'saatchi_url') !== false) {
        echo "✅ FOUND 'saatchi_url' in file content. (My changes are present)<br>";
    } else {
        echo "❌ 'saatchi_url' NOT FOUND in file content. (Old version?)<br>";
    }
} else {
    echo "File does not exist.<br>";
}

echo "<h2>Style.css check</h2>";
$style = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/themes/caviar-premium/style.css';
if (file_exists($style)) {
     $content = file_get_contents($style);
     if (strpos($content, 'flex-direction: column') !== false) {
         echo "✅ FOUND 'flex-direction: column' in style.css.<br>";
     } else {
         echo "❌ 'flex-direction: column' NOT FOUND in style.css.<br>";
     }
}
?>
