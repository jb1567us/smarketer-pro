<?php include_once '../../includes/header.php'; ?>
<div class="max-w-3xl mx-auto mt-10 bg-white p-6 rounded shadow">
  <h2 class="text-2xl font-bold mb-4">Discover Your Customers</h2>
  <form method="POST" action="../controllers/handle_product_input.php" onsubmit="showSpinner()">
    <label for="product_description" class="block font-medium mb-1">Describe your product:</label>
    <textarea name="product_description" rows="5" class="w-full p-3 border rounded mb-4" placeholder="e.g., AI-powered scheduling tool for fitness coaches"></textarea>

    <fieldset class="mb-4">
      <legend class="font-semibold mb-2">Select insights to generate:</legend>
      <label class="block mb-1"><input type="checkbox" name="sections[]" value="personas" checked> Customer Personas</label>
      <label class="block mb-1"><input type="checkbox" name="sections[]" value="journey" checked> Buyer Journey (AIDA)</label>
      <label class="block mb-1"><input type="checkbox" name="sections[]" value="channels" checked> Marketing Channels</label>
      <label class="block mb-1"><input type="checkbox" name="sections[]" value="content" checked> Content & SEO Strategy</label>
      <label class="block mb-1"><input type="checkbox" name="sections[]" value="competition" checked> Competitive Positioning</label>
    </fieldset>

    <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Generate Insights</button>
  </form>
</div>

<div id="spinner" class="fixed inset-0 bg-white bg-opacity-80 hidden items-center justify-center z-50">
  <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-blue-600"></div>
</div>
<script>
function showSpinner() {
  document.getElementById('spinner').classList.remove('hidden');
}
</script>
<?php include_once '../../includes/footer.php'; ?>