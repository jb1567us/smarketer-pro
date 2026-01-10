<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Product Insights Analysis</title>
    <!-- Tailwind CSS via CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .animation-fade-in { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen flex flex-col items-center p-8 md:p-24 selection:bg-blue-100">

    <!-- Header -->
    <div class="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm lg:flex mb-10">
        <p class="fixed left-0 top-0 flex w-full justify-center border-b border-gray-300 bg-white pb-6 pt-8 backdrop-blur-2xl lg:static lg:w-auto lg:rounded-xl lg:border lg:bg-gray-200 lg:p-4">
            Product Insights Analysis
        </p>
    </div>

    <!-- Hero -->
    <div class="relative flex place-items-center mb-10 text-center">
        <h1 class="text-4xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-cyan-500 pb-2">
            Unlock Product Potential
        </h1>
    </div>

    <!-- Main Content -->
    <div class="w-full max-w-2xl grid gap-6">
        
        <!-- Input Card -->
        <div class="bg-white p-6 rounded-2xl shadow-xl border border-gray-100">
            <label class="block text-sm font-medium mb-2 text-gray-700">
                Product Description / Data
            </label>
            <textarea id="productInput"
                class="w-full h-40 p-4 rounded-xl border border-gray-200 bg-gray-50 focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-none"
                placeholder="Paste your product details here..."></textarea>
            
            <button id="analyzeBtn" onclick="analyzeProduct()"
                class="mt-4 w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed">
                <i data-lucide="sparkles" class="w-5 h-5"></i>
                <span>Generate Insights</span>
            </button>
        </div>

        <!-- Result Card -->
        <div id="resultCard" class="bg-white p-8 rounded-2xl shadow-xl border border-blue-100 hidden animation-fade-in">
            <h3 class="text-xl font-semibold mb-4 flex items-center gap-2 text-blue-600">
                <i data-lucide="sparkles" class="w-5 h-5"></i> AI Analysis
            </h3>
            <div id="resultContent" class="prose max-w-none whitespace-pre-wrap text-gray-700 leading-relaxed"></div>
        </div>
    </div>

    <script>
        // Initialize Icons
        lucide.createIcons();

        async function analyzeProduct() {
            const input = document.getElementById('productInput').value;
            const btn = document.getElementById('analyzeBtn');
            const btnText = btn.querySelector('span');
            const resultCard = document.getElementById('resultCard');
            const resultContent = document.getElementById('resultContent');

            if (!input.trim()) return;

            // Loading State
            btn.disabled = true;
            btnText.innerText = "Analyzing...";
            resultCard.classList.add('hidden');
            resultContent.innerText = "";

            try {
                const response = await fetch('api.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ productData: input })
                });

                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                // Show Result
                resultContent.innerText = data.insights;
                resultCard.classList.remove('hidden');

            } catch (error) {
                alert("Error: " + error.message);
            } finally {
                // Reset State
                btn.disabled = false;
                btnText.innerText = "Generate Insights";
            }
        }
    </script>
</body>
</html>
