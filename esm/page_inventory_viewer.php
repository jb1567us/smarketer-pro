<?php
require_once('wp-load.php');

$args = array(
    'post_type' => 'page',
    'posts_per_page' => -1,
    'post_status' => array('publish', 'draft', 'private', 'pending', 'future')
);

$query = new WP_Query($args);
$pages = $query->posts;

// Helper to detect potential duplicate slugs (ending in -Number)
function is_potential_duplicate($slug)
{
    return preg_match('/-\d+$/', $slug);
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Inventory & Duplicate Check</title>
    <style>
        body {
            font-family: -apple-system, sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        h1 {
            margin-top: 0;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 14px;
        }

        th,
        td {
            padding: 10px;
            border-bottom: 1px solid #ddd;
            text-align: left;
        }

        th {
            background: #eee;
        }

        tr:hover {
            background: #f9f9f9;
        }

        .badge {
            padding: 3px 6px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        }

        .status-publish {
            background: #d4edda;
            color: #155724;
        }

        .status-draft {
            background: #fff3cd;
            color: #856404;
        }

        .status-private {
            background: #cce5ff;
            color: #004085;
        }

        .warning {
            background: #fff3cd;
        }

        /* Row highlight */
        .flag {
            color: red;
            font-weight: bold;
        }

        .actions a {
            margin-right: 10px;
            text-decoration: none;
            color: #007bff;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>WordPress Page Inventory (<?php echo count($pages); ?> pages)</h1>
        <p>Use this list to manually compare pages and verify if any "Potential Duplicates" (highlighted in yellow) are
            actually unwanted.</p>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Title</th>
                    <th>Slug (URL)</th>
                    <th>Status</th>
                    <th>Date</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <?php foreach ($pages as $p):
                    $is_suspect = is_potential_duplicate($p->post_name);
                    $row_class = $is_suspect ? 'warning' : '';
                    ?>
                    <tr class="<?php echo $row_class; ?>">
                        <td><?php echo $p->ID; ?></td>
                        <td>
                            <?php echo htmlspecialchars($p->post_title); ?>
                            <?php if ($is_suspect): ?>
                                <br><span class="flag">⚠️ Check Slug</span>
                            <?php endif; ?>
                        </td>
                        <td><?php echo $p->post_name; ?></td>
                        <td><span class="badge status-<?php echo $p->post_status; ?>"><?php echo $p->post_status; ?></span>
                        </td>
                        <td><?php echo get_the_date('Y-m-d', $p->ID); ?></td>
                        <td class="actions">
                            <a href="<?php echo get_permalink($p->ID); ?>" target="_blank">View</a>
                            <a href="/wp-admin/post.php?post=<?php echo $p->ID; ?>&action=edit" target="_blank">Edit</a>
                        </td>
                    </tr>
                <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</body>

</html>