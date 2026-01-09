<?php

class GeminiService
{
    private $apiKey;
    private $baseUrl = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent';

    public function __construct($apiKey)
    {
        $this->apiKey = $apiKey;
    }

    public function generateInsights($productData, $sections = [])
    {
        $url = $this->baseUrl . '?key=' . $this->apiKey;

        // Prompt Mapping
        $promptMap = [
            'personas' => "**1. Ideal Customer Personas**\nDescribe 2–3 ideal customer types. For each include:\n- Name and persona label (e.g. “Tech-Savvy Tina”)\n- Demographics (age, job title, industry, location)\n- Psychographics (values, motivations, personality traits)\n- Behavioral traits (buying style, research habits, tech use)\n- Key pain points and core goals\n- Their role in purchasing decisions (user, decision-maker, etc.)\n",
            'journey' => "**2. Buyer Journey Mapping**\nOutline how each persona goes from Awareness → Consideration → Decision. Include their thoughts, feelings, content needs, and likely actions at each stage.\n",
            'channels' => "**3. Marketing Channel & Outreach Strategy**\nList the most effective online/offline places to reach them (Reddit, forums, newsletters, social platforms, etc.). **Crucially, include a strategy for hyper-targeted direct emails to B2B prospects**, including finding leads and drafting opening lines. Suggest outreach tactics or messaging styles.\n",
            'content' => "**4. Content & SEO Strategy**\nSuggest blog or video content ideas that match their journey and pain points. Include relevant SEO keywords and top-of-funnel vs. bottom-of-funnel content.\n",
            'competition' => "**5. Competitive Positioning**\nName 2–3 potential alternatives or competitor tools they might consider. For each, explain what it offers and how to position this product differently (unique angle or missing feature).\n"
        ];

        // Build dynamic prompt
        $instructions = "";
        
        // DEBUG: Write received sections to file
        file_put_contents('debug_sections.log', date('Y-m-d H:i:s') . ' - Received: ' . json_encode($sections) . "\n", FILE_APPEND);

        // If no sections provided, default to all (or handle as error)
        if (empty($sections)) {
            // Fallback: If strictly empty, user might want general summary, or we default to all.
            // Let's default to all for now but logging will tell us if it WAS empty.
            $sections = array_keys($promptMap);
        }

        foreach ($sections as $key) {
             if (isset($promptMap[$key])) {
                 $instructions .= $promptMap[$key] . "\n";
             }
        }

        $instructions .= "Format output with bold section headers and paragraph-style descriptions under each.\n";
        $instructions .= "CRITICAL INSTRUCTION: ONLY generate the sections listed above. Do NOT generate any other sections (like 'Competitive Positioning' or 'Channels') unless explicitly asked for in the list above.";

        $fullPrompt = "You are a customer discovery assistant. The user is building a product and has described the following product: '$productData'.\n\nPlease analyze and return the following sections in detailed Markdown format:\n\n" . $instructions;

        $data = [
            'contents' => [
                [
                    'parts' => [
                        ['text' => $fullPrompt]
                    ]
                ]
            ]
        ];

        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json'
        ]);

        $response = curl_exec($ch);

        if (curl_errno($ch)) {
            throw new Exception('Curl error: ' . curl_error($ch));
        }

        curl_close($ch);

        $json = json_decode($response, true);

        if (isset($json['error'])) {
            throw new Exception('API Error: ' . json_encode($json['error']));
        }

        // Extract text from response
        if (isset($json['candidates'][0]['content']['parts'][0]['text'])) {
            return $json['candidates'][0]['content']['parts'][0]['text'];
        }

        return "No insights generated. Raw response: " . substr($response, 0, 200) . "...";
    }
}
