<?php
/**
 * Dashboard view.
 *
 * @package AIContentWriter/Admin/Views
 * @since 1.5.0
 */

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

?>
<div class="wrap aicw-wrap">
	<h2 class="wp-heading-inline">
		<?php esc_html_e( 'Dashboard', 'ai-content-writer' ); ?>
		<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-campaigns' ) ); ?>" class="page-title-action">
			<?php esc_html_e( 'All Campaigns', 'ai-content-writer' ); ?>
		</a>
		<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-settings' ) ); ?>" class="page-title-action">
			<?php esc_html_e( 'Settings', 'ai-content-writer' ); ?>
		</a>
		<a href="<?php echo esc_attr( admin_url( 'admin.php?page=aicw-help' ) ); ?>" class="page-title-action">
			<?php esc_html_e( 'Help', 'ai-content-writer' ); ?>
		</a>
	</h2>
	<hr class="wp-header-end">
	<div class="aicw__body">
		<div class="aicw__body__content">
			<div class="aicw-card">
				<div class="aicw-card__header d-flex flex-justify__space-between">
					<h3 class="aicw-card__title"><?php esc_html_e( 'Statistics', 'ai-content-writer' ); ?></h3>
					<div class="post-statistics-controls">
						<select id="campaigns_chart_timeframe">
							<option value="today"><?php esc_html_e( 'Today', 'ai-content-writer' ); ?></option>
							<option value="last7days" selected><?php esc_html_e( 'Last 7 Days', 'ai-content-writer' ); ?></option>
							<option value="last30days"><?php esc_html_e( 'Last 30 Days', 'ai-content-writer' ); ?></option>
							<option value="lastyear"><?php esc_html_e( 'Last Year', 'ai-content-writer' ); ?></option>
							<option value="alltime"><?php esc_html_e( 'All Time', 'ai-content-writer' ); ?></option>
						</select>
					</div>
				</div>
				<div class="aicw-card__body">
					<div class="aicw_campaigns_statistics" style="width: 100%; height: 400px;overflow-x: auto;">
						<canvas id="aicw_campaigns_statistics" style="height: 400px;"></canvas>
					</div>
				</div>
			</div>

			<div class="aicw-total-processed d-flex flex-justify__space-between gap-1">
				<div class="aicw-card w-100 text-center">
					<div class="aicw-card__header">
						<h4 class="aicw-card__title"><?php esc_html_e( 'Total Published Posts', 'ai-content-writer' ); ?></h4>
					</div>
					<div class="aicw-card__body published-posts">
						<p class="aicw-post-count">
							<?php
							echo esc_html(
								aicw_get_campaigns(
									array(
										'post_type'   => 'post',
										'post_status' => 'publish',
										'meta_query'  => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
											array(
												'key' => '_aicw_campaign_id',
											),
										),
									),
									true
								)
							);
							?>
						</p>
					</div>
				</div>
				<div class="aicw-card w-100 text-center">
					<div class="aicw-card__header">
						<h4 class="aicw-card__title"><?php esc_html_e( 'Total Pending Posts', 'ai-content-writer' ); ?></h4>
					</div>
					<div class="aicw-card__body pending-posts">
						<p class="aicw-post-count">
							<?php
							echo esc_html(
								aicw_get_campaigns(
									array(
										'post_type'   => 'post',
										'post_status' => 'pending',
										'meta_query'  => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
											array(
												'key' => '_aicw_campaign_id',
											),
										),
									),
									true
								)
							);
							?>
					</div>
				</div>
				<div class="aicw-card w-100 text-center">
					<div class="aicw-card__header">
						<h4 class="aicw-card__title"><?php esc_html_e( 'Total Draft Posts', 'ai-content-writer' ); ?></h4>
					</div>
					<div class="aicw-card__body draft-posts">
						<p class="aicw-post-count">
							<?php
							echo esc_html(
								aicw_get_campaigns(
									array(
										'post_type'   => 'post',
										'post_status' => 'draft',
										'meta_query'  => array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
											array(
												'key' => '_aicw_campaign_id',
											),
										),
									),
									true
								)
							);
							?>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
<?php
