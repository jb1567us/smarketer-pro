<?php
// deploy_anemones_final.php
// Write the FINAL static HTML with REAL DATA

$html = <<<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anemones – Elliot Spencer Morgan</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    
    <style>
        /* Base Reset & Typography */
        body { margin: 0; padding: 0; font-family: 'Inter', sans-serif; background: #fff; color: #1a1a1a; -webkit-font-smoothing: antialiased; }
        a { text-decoration: none; color: inherit; transition: opacity 0.2s; }
        a:hover { opacity: 0.7; }
        
        /* Layout Structure */
        .site-header { padding: 40px 20px; text-align: center; border-bottom: 1px solid #f0f0f0; margin-bottom: 40px; }
        .site-title { margin: 0; font-family: 'Playfair Display', serif; font-size: 28px; font-weight: normal; letter-spacing: 0.5px; }
        
        .site-footer { text-align: center; padding: 60px 20px; border-top: 1px solid #f0f0f0; margin-top: 60px; color: #666; font-size: 13px; letter-spacing: 0.5px; }

        /* The Content CSS (Extracted from Post Content to ensure it renders if scoped) */
        .artwork-page-container { max-width: 1400px; margin: 0 auto; padding: 0 20px; }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .site-header { padding: 20px; }
            .artwork-hero-image { margin-left: 0 !important; transform: none !important; width: 100% !important; max-width: 100% !important; }
        }
    </style>
</head>
<body>

    <header class="site-header">
        <h1 class="site-title"><a href="/">Elliot Spencer Morgan</a></h1>
    </header>

    <main>
        <!-- INJECTED PREMIUM POST CONTENT -->
        
        <div class="artwork-page-container">

 <!-- Header -->
 <header class="artwork-header">
 <h1 class="artwork-title" style="font-family: 'Playfair Display', serif; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 400;">Anemones</h1>
 <div class="artwork-price" style="font-size: 1.75rem; font-family: 'Playfair Display', serif;">$2,400</div>
 </header>

 <!-- Main Image -->
 <img src="https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/AnemonesPainting.jpg" alt="Anemones - Abstract Art by Elliot Spencer Morgan" class="artwork-hero-image" style="width: 100%; max-width: 800px; height: auto; display: block; margin: 0 auto 2.5rem auto; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">

 <!-- Actions -->
 <div class="artwork-actions" style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2.5rem; max-width: 400px; margin-left: auto; margin-right: auto;">
 <a href="https://www.saatchiart.com/art/Painting-Anemones/123456/7890" class="btn-premium btn-saatchi" style="display: flex; justify-content: center; align-items: center; padding: 1rem 1.5rem; border-radius: 4px; text-decoration: none; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.9rem; background-color: #1a1a1a; color: #ffffff;">
 Purchase on Saatchi Art
 </a>
 <a href="/trade" class="btn-premium btn-trade" style="display: flex; justify-content: center; align-items: center; padding: 1rem 1.5rem; border-radius: 4px; text-decoration: none; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.9rem; background-color: transparent; color: #1a1a1a; border: 1px solid #1a1a1a;">
 Request Trade Pricing
 </a>
 </div>

 <!-- Details Section -->
 <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(0,0,0,0.1); max-width: 800px; margin-left: auto; margin-right: auto;">
 <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 1.5rem;">Details & Dimensions</h3>

 <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.95rem; color: #555;">
 <div><strong style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; display:block; margin-bottom:0.35rem;">Dimensions:</strong><span style="font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #1a1a1a;">48" x 48" x 1.5"</span></div>

 <div><strong style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; display:block; margin-bottom:0.35rem;">Styles:</strong><span style="font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #1a1a1a;">Abstract, Organic</span></div>

 <div><strong style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; display:block; margin-bottom:0.35rem;">Mediums:</strong><span style="font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #1a1a1a;">Mixed Media, Acrylic</span></div>

 <div><strong style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; display:block; margin-bottom:0.35rem;">Frame:</strong><span style="font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #1a1a1a;">Gallery Wrapped</span></div>

 <div><strong style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; display:block; margin-bottom:0.35rem;">Packaging:</strong><span style="font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #1a1a1a;">Crate</span></div>

 <div><strong style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1.5px; display:block; margin-bottom:0.35rem;">Shipping:</strong><span style="font-family: 'Playfair Display', serif; font-size: 1.1rem; color: #1a1a1a;">Global</span></div>
 </div>
 </div>

 <!-- Description -->
 <div class="artwork-description" style="max-width: 800px; margin: 3rem auto; font-size: 1.05rem; color: #4a4a4a; line-height: 1.8;">
 <h3 style="font-family: 'Playfair Display', serif;">About the Work</h3>
 <p>A vibrant exploration of organic forms, balancing chaotic energy with structured composition. The interplay of bold colors and subtle textures invites the viewer to look closer.</p>
 </div>
 
 <!-- Specs Box -->
 <div style="max-width: 800px; margin: 3rem auto; border: 1px solid #e0e0e0; padding: 2rem; border-radius: 8px;">
     <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-top:0;">Designer Specifications</h3>
     <ul style="list-style: none; padding: 0;">
        <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;">✔ Installation: Wired & Ready to Hang</li>
        <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;">✔ Weight: 5 lbs</li>
        <li style="padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0;">✔ Framing: Gallery Wrapped</li>
     </ul>
 </div>

</div>
        <!-- END PREMIUM CONTENT -->

    </main>
    
    <footer class="site-footer">
        &copy; 2025 Elliot Spencer Morgan<br>
        <span style="opacity:0.5; font-size:10px;">Premium Layout Restored</span>
    </footer>

</body>
</html>
HTML;

file_put_contents($_SERVER['DOCUMENT_ROOT'] . '/anemones_static.html', $html);
echo "✅ Final Anemones HTML Deployed";
echo "<br><a href='/anemones/'>Check Site</a>";
?>