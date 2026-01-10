<?php
define('WP_CACHE', true); // WP-Optimize Cache

/**
 * The base configuration for WordPress
 *
 * The wp-config.php creation script uses this file during installation.
 * You don't have to use the website, you can copy this file to "wp-config.php"
 * and fill in the values.
 *
 * This file contains the following configurations:
 *
 * * Database settings
 * * Secret keys
 * * Database table prefix
 * * ABSPATH
 *
 * @link https://developer.wordpress.org/advanced-administration/wordpress/wp-config/
 *
 * @package WordPress
 */

// ** Database settings - You can get this info from your web host ** //
/** The name of the database for WordPress */
define( 'DB_NAME', 'elliotspencermor_wp645' );

/** Database username */
define( 'DB_USER', 'elliotspencermor_wp645' );

/** Database password */
define( 'DB_PASSWORD', '5p[.6G3HiS2[.P@0' );

/** Database hostname */
define( 'DB_HOST', 'localhost' );

/** Database charset to use in creating database tables. */
define( 'DB_CHARSET', 'utf8' );

/** The database collate type. Don't change this if in doubt. */
define( 'DB_COLLATE', '' );

/**#@+
 * Authentication unique keys and salts.
 *
 * Change these to different unique phrases! You can generate these using
 * the {@link https://api.wordpress.org/secret-key/1.1/salt/ WordPress.org secret-key service}.
 *
 * You can change these at any point in time to invalidate all existing cookies.
 * This will force all users to have to log in again.
 *
 * @since 2.6.0
 */
define( 'AUTH_KEY',         'p0jkglf1a8cxlv494uupcb7rhgyok0gzhzro5xzgpfy6kaxgdf0kgyv4k10x1ivx' );
define( 'SECURE_AUTH_KEY',  'hzupto3qj6w3dlbdyclroxzxl0aiwbn3by1q3uw4ny4dqdzus0th8tcwefijfkxm' );
define( 'LOGGED_IN_KEY',    'c6goevorctilvubgtkic014c28903qoslx8qgg9g2qy7l8bgqfe9ox0coe2vsyly' );
define( 'NONCE_KEY',        'ua16aaaguppqfcrfvbnay8r3mxscgrbmodhlkxntqfs7l3okag6r0pa6lnmm5hdk' );
define( 'AUTH_SALT',        'ckqkzkh94ltkcafpj5yilrg2v8bta1lwj0ycenouudb7ea2beizex6hzb2fz2lir' );
define( 'SECURE_AUTH_SALT', '0rrd8oqls0ri9p4fzvh6il2cgu0wedjs4vhgteewcoiyfrsexbntz4jlmnwpjoli' );
define( 'LOGGED_IN_SALT',   'juwq7zqv5mtiwqxufzf2hscp3gfneselewcc8hzkpbweg1kcnmid2vszyqdox7y1' );
define( 'NONCE_SALT',       'u9cxk2ctp5b3ibbgwitqycvgi3ak4krvxbxj610rkjkeatu2l8qn27khrhy5afbb' );
/**#@-*/

/**
 * WordPress database table prefix.
 *
 * You can have multiple installations in one database if you give each
 * a unique prefix. Only numbers, letters, and underscores please!
 */
$table_prefix = 'wpja_';

/**
 * For developers: WordPress debugging mode.
 *
 * Change this to true to enable the display of notices during development.
 * It is strongly recommended that plugin and theme developers use WP_DEBUG
 * in their development environments.
 */
if ( ! defined( 'WP_DEBUG' ) ) {
    define( 'WP_DEBUG', true );
    define( 'WP_DEBUG_LOG', true );
    define( 'WP_DEBUG_DISPLAY', false );
}

/* Add any custom values between this line and the "stop editing" line. */

/* That's all, stop editing! Happy publishing. */

/** Absolute path to the WordPress directory. */
if ( ! defined( 'ABSPATH' ) ) {
    define( 'ABSPATH', __DIR__ . '/' );
}

/** Sets up WordPress vars and included files. */
require_once ABSPATH . 'wp-settings.php';