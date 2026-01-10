<?php
// Scan recursively for images and return JSON map of filename -> full path
$root = __DIR__ . '/wp-content/uploads';
$files = [];

$iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root));

foreach ($iterator as $file) {
    if ($file->isFile()) {
        $ext = strtolower($file->getExtension());
        if (in_array($ext, ['jpg', 'jpeg', 'png', 'webp'])) {
            $path = str_replace(__DIR__ . '/', '', $file->getPathname());
            $files[] = [
                'name' => $file->getFilename(),
                'path' => $path,
                'size' => $file->getSize()
            ];
        }
    }
}

header('Content-Type: application/json');
echo json_encode($files);
?>