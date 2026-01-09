<?php
/**
 * Logs list table view.
 *
 * @since 2.0.6
 * @package AIContentWriter/Admin/Views
 * @var object $list_table Logs list table.
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

?>
<div class="wrap aicw-wrap">
	<h2 class="wp-heading-inline">
		<?php esc_html_e( 'Logs', 'ai-content-writer' ); ?>
	</h2>
	<hr class="wp-header-end">
	<form id="aicw-logs-table" method="get" action="<?php echo esc_url( admin_url( 'admin.php' ) ); ?>">
		<?php
		$list_table->views();
		$list_table->display();
		?>
		<input type="hidden" name="page" value="aicw-logs">
	</form>
</div>
<?php
