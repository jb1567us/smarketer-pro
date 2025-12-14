<?php
// restore_header_footer.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();

$header = <<<'HTML'
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
<style>
/* Emergency CSS to Ensure Visibility */
body { background: white !important; color: black !important; }
.site-header { background: #eee; padding: 20px; }
.site-footer { background: #333; color: white; padding: 20px; }
</style>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<div id="page" class="site">
	<header id="masthead" class="site-header">
		<h1 class="site-title"><a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home"><?php bloginfo( 'name' ); ?></a></h1>
        <p>RESTORED HEADER</p>
	</header>
    <div id="content" class="site-content">
HTML;

$footer = <<<'HTML'
    </div><!-- #content -->
	<footer id="colophon" class="site-footer">
        <p>RESTORED FOOTER</p>
        <p>&copy; <?php echo date('Y'); ?> <?php bloginfo( 'name' ); ?></p>
	</footer>
</div><!-- #page -->
<?php wp_footer(); ?>
</body>
</html>
HTML;

$h = file_put_contents($dir . '/header.php', $header);
$f = file_put_contents($dir . '/footer.php', $footer);

if ($h && $f) {
    echo "✅ Restored header.php ($h bytes) and footer.php ($f bytes).";
} else {
    echo "❌ Failed to restore header/footer.";
}
?>