<?php
session_start();
$ip = $_SERVER['REMOTE_ADDR'];
$key = 'last_access_' . $ip;
$now = time();
if (isset($_SESSION[$key]) && $now - $_SESSION[$key] < 60) {
    http_response_code(429);
    die('Rate limit exceeded. Please wait a bit before trying again.');
}
$_SESSION[$key] = $now;
?>