<?php
// Simple configuration
// In production, you might want to load this from a real system environment variable or a file outside public_html

return [
    'gemini_api_key' => getenv('GEMINI_API_KEY') ?: 'AIzaSyBbjG2u56kVoh7fFKZ-nf5yEAsIOJh_UbI',
];
