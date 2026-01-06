<?php
$host = 'localhost';
$user = 'elliotspencermor_wp645';
$pass = '5p[.6G3HiS2[.P@0';
$db   = 'elliotspencermor_wp645';

$mysqli = new mysqli($host, $user, $pass, $db);

if ($mysqli->connect_error) {
    die("Connection failed: " . $mysqli->connect_error . " (Code: " . $mysqli->connect_errno . ")");
}
echo "Connected successfully to DB version: " . $mysqli->server_info;
$mysqli->close();
?>
