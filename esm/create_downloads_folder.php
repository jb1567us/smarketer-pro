<?php
if (!file_exists('downloads')) {
    if (mkdir('downloads', 0755, true)) {
        echo "Directory 'downloads' created successfully.";
    } else {
        echo "Error: Failed to create directory.";
    }
} else {
    echo "Directory 'downloads' already exists.";
}
?>