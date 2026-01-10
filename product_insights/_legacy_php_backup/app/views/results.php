<?php
session_start();
include_once '../../includes/header.php';

$product = $_SESSION['product'] ?? '';
$sections = $_SESSION['sections'] ?? [];
$insights = $_SESSION['insights'] ?? '';
?>

<div class="max-w-4xl mx-auto mt-10 bg-white p-6 rounded shadow">
  <h2 class="text-2xl font-bold mb-6">Customer Discovery Results</h2>

  <?php if (!$insights): ?>
    <p class="text-red-600">No insights found. Please start a new search.</p>
  <?php else: ?>
    <article class="prose prose-lg max-w-none whitespace-pre-wrap"><?= htmlspecialchars($insights) ?></article>
  <?php endif; ?>

  <form method="POST" action="../controllers/handle_product_input.php" class="mt-8 bg-gray-50 p-4 rounded">
    <input type="hidden" name="product_description" value="<?= htmlspecialchars($product) ?>">
    <p class="font-semibold mb-2">Want to explore more? Select additional sections:</p>
    <?php
      $all_sections = [
        'personas' => 'Customer Personas',
        'journey' => 'Buyer Journey (AIDA)',
        'channels' => 'Marketing Channels',
        'content' => 'Content & SEO Strategy',
        'competition' => 'Competitive Positioning'
      ];
      foreach ($all_sections as $key => $label):
    ?>
      <label class="block mb-1">
        <input type="checkbox" name="sections[]" value="<?= $key ?>" <?= in_array($key, $sections) ? 'checked' : '' ?>> <?= $label ?>
      </label>
    <?php endforeach; ?>
    <button type="submit" class="mt-3 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Regenerate Insights</button>
  </form>

  <div class="mt-4">
    <a href="input_product.php" class="text-blue-600 hover:underline">← Analyze a different product</a>
  </div>
</div>

<?php include_once '../../includes/footer.php'; ?>
