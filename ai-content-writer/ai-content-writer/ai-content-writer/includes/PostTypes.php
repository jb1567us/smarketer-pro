<?php

namespace AIContentWriter;

defined( 'ABSPATH' ) || exit; // Exit if accessed directly.

/**
 * Class PostTypes.
 * Responsible for registering custom post types.
 *
 * @since 1.4.0
 * @package AIContentWriter
 */
class PostTypes {

	/**
	 * CPT constructor.
	 */
	public function __construct() {
		add_action( 'init', array( $this, 'register_cpt' ) );
		add_action( 'init', array( $this, 'register_temp_cpt' ) );
		add_action( 'init', array( $this, 'register_log_cpt' ) );
	}

	/**
	 * Register custom post types.
	 * This will register the campaign post type.
	 *
	 * @since 1.4.0
	 * @return void
	 */
	public function register_cpt() {
		$labels = array(
			'name'               => _x( 'Campaigns', 'post type general name', 'ai-content-writer' ),
			'singular_name'      => _x( 'Campaign', 'post type singular name', 'ai-content-writer' ),
			'menu_name'          => _x( 'Campaigns', 'admin menu', 'ai-content-writer' ),
			'name_admin_bar'     => _x( 'Campaign', 'add new on admin bar', 'ai-content-writer' ),
			'add_new'            => _x( 'Add New', 'campaign', 'ai-content-writer' ),
			'add_new_item'       => __( 'Add New Campaign', 'ai-content-writer' ),
			'new_item'           => __( 'New Campaign', 'ai-content-writer' ),
			'edit_item'          => __( 'Edit Campaign', 'ai-content-writer' ),
			'view_item'          => __( 'View Campaign', 'ai-content-writer' ),
			'all_items'          => __( 'All Campaigns', 'ai-content-writer' ),
			'search_items'       => __( 'Search Campaigns', 'ai-content-writer' ),
			'parent_item_colon'  => __( 'Parent Campaigns:', 'ai-content-writer' ),
			'not_found'          => __( 'No campaigns found.', 'ai-content-writer' ),
			'not_found_in_trash' => __( 'No campaigns found in Trash.', 'ai-content-writer' ),
		);

		$args = array(
			'labels'              => apply_filters( 'aicw_campaign_post_type_labels', $labels ),
			'public'              => false,
			'publicly_queryable'  => false,
			'exclude_from_search' => true,
			'show_ui'             => false,
			'show_in_menu'        => false,
			'show_in_nav_menus'   => false,
			'query_var'           => false,
			'can_export'          => false,
			'rewrite'             => false,
			'capability_type'     => 'post',
			'has_archive'         => false,
			'hierarchical'        => false,
			'menu_position'       => null,
			'supports'            => array(),
		);

		register_post_type( 'aicw_campaign', apply_filters( 'aicw_campaign_post_type_args', $args ) );
	}

	/**
	 * Register temporary custom post types.
	 * This will register the temporary post type for the generated posts.
	 *
	 * @since 1.4.0
	 * @return void
	 */
	public function register_temp_cpt() {
		$labels = array(
			'name'               => _x( 'Temporary Posts', 'post type general name', 'ai-content-writer' ),
			'singular_name'      => _x( 'Temporary Post', 'post type singular name', 'ai-content-writer' ),
			'menu_name'          => _x( 'Temporary Posts', 'admin menu', 'ai-content-writer' ),
			'name_admin_bar'     => _x( 'Temporary Post', 'add new on admin bar', 'ai-content-writer' ),
			'add_new'            => _x( 'Add New', 'temporary post', 'ai-content-writer' ),
			'add_new_item'       => __( 'Add New Temporary Post', 'ai-content-writer' ),
			'new_item'           => __( 'New Temporary Post', 'ai-content-writer' ),
			'edit_item'          => __( 'Edit Temporary Post', 'ai-content-writer' ),
			'view_item'          => __( 'View Temporary Post', 'ai-content-writer' ),
			'all_items'          => __( 'All Temporary Posts', 'ai-content-writer' ),
			'search_items'       => __( 'Search Temporary Posts', 'ai-content-writer' ),
			'parent_item_colon'  => __( 'Parent Temporary Posts:', 'ai-content-writer' ),
			'not_found'          => __( 'No temporary posts found.', 'ai-content-writer' ),
			'not_found_in_trash' => __( 'No temporary posts found in Trash.', 'ai-content-writer' ),
		);

		$args = array(
			'labels'              => apply_filters( 'aicw_temp_post_type_labels', $labels ),
			'public'              => false,
			'publicly_queryable'  => false,
			'exclude_from_search' => true,
			'show_ui'             => false,
			'show_in_menu'        => false,
			'show_in_nav_menus'   => false,
			'query_var'           => false,
			'can_export'          => false,
			'rewrite'             => false,
			'capability_type'     => 'post',
			'has_archive'         => false,
			'hierarchical'        => false,
			'menu_position'       => null,
			'supports'            => array(),
		);

		register_post_type( 'aicw_post', apply_filters( 'aicw_temp_post_type_args', $args ) );
	}

	/**
	 * Register log custom post types.
	 * This will register the log post type for the generated posts.
	 *
	 * @since 2.0.6
	 * @return void
	 */
	public function register_log_cpt() {
		$labels = array(
			'name'               => _x( 'Logs', 'post type general name', 'ai-content-writer' ),
			'singular_name'      => _x( 'Log', 'post type singular name', 'ai-content-writer' ),
			'menu_name'          => _x( 'Logs', 'admin menu', 'ai-content-writer' ),
			'name_admin_bar'     => _x( 'Log', 'add new on admin bar', 'ai-content-writer' ),
			'add_new'            => _x( 'Add New', 'log', 'ai-content-writer' ),
			'add_new_item'       => __( 'Add New Log', 'ai-content-writer' ),
			'new_item'           => __( 'New Log', 'ai-content-writer' ),
			'edit_item'          => __( 'Edit Log', 'ai-content-writer' ),
			'view_item'          => __( 'View Log', 'ai-content-writer' ),
			'all_items'          => __( 'All Logs', 'ai-content-writer' ),
			'search_items'       => __( 'Search Logs', 'ai-content-writer' ),
			'parent_item_colon'  => __( 'Parent Logs:', 'ai-content-writer' ),
			'not_found'          => __( 'No logs found.', 'ai-content-writer' ),
			'not_found_in_trash' => __( 'No logs found in Trash.', 'ai-content-writer' ),
		);

		$args = array(
			'labels'              => apply_filters( 'aicw_log_post_type_labels', $labels ),
			'public'              => false,
			'publicly_queryable'  => false,
			'exclude_from_search' => true,
			'show_ui'             => false,
			'show_in_menu'        => false,
			'show_in_nav_menus'   => false,
			'query_var'           => false,
			'can_export'          => false,
			'rewrite'             => false,
			'capability_type'     => 'post',
			'has_archive'         => false,
			'hierarchical'        => false,
			'menu_position'       => null,
			'supports'            => array(),
		);

		register_post_type( 'aicw_log', apply_filters( 'aicw_log_post_type_args', $args ) );
	}
}
