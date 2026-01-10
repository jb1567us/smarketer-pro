<?php
$content = file_get_contents('https://elliotspencermorgan.com/');
file_put_contents('remote_content.txt', $content);
echo "Saved content to remote_content.txt";
?>
