<?php
/**
 * Campaigns list table view.
 *
 * @since 1.0.0
 * @package AIContentWriter/Admin/Views
 * @var object $list_table Campaigns list table.
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

?>
<div class="wrap aicw-wrap">
	<h2 class="wp-heading-inline">
		<?php esc_html_e( 'Campaigns', 'ai-content-writer' ); ?>
		<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-campaigns&add=yes' ) ); ?>" class="page-title-action">
			<?php esc_html_e( 'Add New Campaign', 'ai-content-writer' ); ?>
		</a>
	</h2>
	<hr class="wp-header-end">
	<form id="aicw-campaigns-table" method="get" action="<?php echo esc_url( admin_url( 'admin.php' ) ); ?>">
		<?php
		$list_table->views();
		$list_table->search_box( __( 'Search', 'ai-content-writer' ), 'search' );
		$list_table->display();
		?>
		<input type="hidden" name="page" value="aicw-campaigns">
	</form>
</div>
<?php
