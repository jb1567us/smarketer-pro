<?php
require_once __DIR__ . '/../../includes/ip_throttle.php';
require_once __DIR__ . '/../../config.php';

function getBestFreeModel() {
    $cacheFile = __DIR__ . '/../../cache/best_model.txt';
    if (file_exists($cacheFile) && time() - filemtime($cacheFile) < 86400) {
        return trim(file_get_contents($cacheFile));
    }

    $ch = curl_init('https://openrouter.ai/api/v1/models');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $result = curl_exec($ch);
    curl_close($ch);

    $data = json_decode($result, true);
    $priority = ['llama3', 'openchat', 'mistral', 'gemma'];

    $bestModel = null;
    foreach ($priority as $preferred) {
        foreach ($data['data'] as $model) {
            if (strpos($model['id'], $preferred) !== false && $model['pricing']['prompt'] == 0) {
                $bestModel = $model['id'];
                break 2;
            }
        }
    }

    if ($bestModel) {
        file_put_contents($cacheFile, $bestModel);
        return $bestModel;
    }

    return 'openchat';
}

function getCustomerInsightsFromProduct($product_description) {
    $model = getBestFreeModel();
    $hash = sha1($product_description);
    $cache_file = __DIR__ . '/../../cache/' . $hash . '.txt';

    if (file_exists($cache_file)) {
        return file_get_contents($cache_file);
    }

    $prompt = "You are a SaaS customer discovery assistant.

The user is building a SaaS product and has described the following product: '$product_description'.

Please analyze and return the following sections in detailed Markdown format:

1. **Ideal Customer Personas**  
Describe 2–3 ideal customer types. For each include:  
- Name and persona label (e.g. “Tech-Savvy Tina”)  
- Demographics (age, job title, industry, location)  
- Psychographics (values, motivations, personality traits)  
- Behavioral traits (buying style, research habits, tech use)  
- Key pain points and core goals  
- Their role in purchasing decisions (user, decision-maker, etc.)

2. **Buyer Journey Mapping**  
Outline how each persona goes from Awareness → Consideration → Decision. Include their thoughts, feelings, content needs, and likely actions at each stage.

3. **Marketing Channel & Outreach Strategy**  
List the most effective online/offline places to reach them (Reddit, forums, newsletters, social platforms, etc.). Include example subreddits or influencers where relevant. Suggest outreach tactics or messaging styles.

4. **Content & SEO Strategy**  
Suggest blog or video content ideas that match their journey and pain points. Include relevant SEO keywords and top-of-funnel vs. bottom-of-funnel content.

5. **Competitive Positioning**  
Name 2–3 potential alternatives or competitor tools they might consider. For each, explain what it offers and how to position this product differently (unique angle or missing feature).

Format output with bold section headers and paragraph-style descriptions under each.
";
    $data = [
        'model' => $model,
        'messages' => [
            ['role' => 'system', 'content' => 'You are a customer research assistant.'],
            ['role' => 'user', 'content' => $prompt]
        ],
        'max_tokens' => 3000
    ];

    $ch = curl_init('https://openrouter.ai/api/v1/chat/completions');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Authorization: Bearer ' . OPENROUTER_API_KEY,
        'HTTP-Referer: ' . SITE_URL,
        'X-Title: Product Discovery Tool'
    ]);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    $result = curl_exec($ch);
    curl_close($ch);
    $response = json_decode($result, true);
    $output = $response['choices'][0]['message']['content'] ?? 'Error retrieving insights.';
    file_put_contents($cache_file, $output);
    return $output;
}
?>