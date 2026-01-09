
(function () {
    // 1. DATA
    const artworkLinks = [
        {
            "id": 1109,
            "title": "A Day at the Lake Painting",
            "slug": "a_day_at_the_lakePainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-A-day-at-the-lake/1295487/6105151/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/A_Day_at_the_LakePainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 1108,
            "title": "A day at the park Painting",
            "slug": "a_day_at_the_parkPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-A-day-at-the-park/1295487/6105309/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/A_day_at_the_ParkPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 1107,
            "title": "A day at the beach Painting",
            "slug": "a_day_at_the_beachPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-A-day-at-the-beach/1295487/6105263/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/A_day_at_the_BeachPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 1106,
            "title": "Gold Series 011 Painting",
            "slug": "gold_series_011Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-011/1295487/6131379/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Gold_Series_011Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 1105,
            "title": "Gold Series 010 Painting",
            "slug": "gold_series_010Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-010/1295487/6131393/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Gold_Series_010Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 1104,
            "title": "Gold Series 009 Painting",
            "slug": "gold_series_009Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-009/1295487/6131427/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Gold_Series_009Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 1103,
            "title": "Gold Series 008 Painting",
            "slug": "gold_series_008Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-008/1295487/6131441/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Gold_Series_008Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 1102,
            "title": "Gold Series 007 Painting",
            "slug": "gold_series_007Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-007/1295487/6131477/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Gold_Series_007Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 1101,
            "title": "Red Planet Painting",
            "slug": "red_planetPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Red-Planet/1295487/6131365/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Red_PlanetPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 1100,
            "title": "Portal Painting",
            "slug": "portalPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal/1295487/6483753/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/PortalPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 249,
            "title": "Golden Rule Painting",
            "slug": "golden_rulePainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Golden-Rule/1295487/6105307/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Golden_RulePainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 248,
            "title": "Transformation Painting",
            "slug": "transformationPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Transformation/1295487/6105295/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/TransformationPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 247,
            "title": "Bloom Painting",
            "slug": "bloomPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Bloom/1295487/6105251/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/BloomPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 246,
            "title": "Blue Glacier Painting",
            "slug": "blue_glacierPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Blue-Glacier/1295487/6105221/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Blue_GlacierPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 245,
            "title": "Blue Storm Painting",
            "slug": "blue_stormPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Blue-Storm/1295487/6105159/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Blue_StormPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 244,
            "title": "Waves Painting",
            "slug": "wavesPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Waves/1295487/6105147/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/WavesPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 243,
            "title": "GOLD SERIES 001 Painting",
            "slug": "gold_series_001Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-001/1295487/6105121/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/GOLD_SERIES_001Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 242,
            "title": "GOLD SERIES 002 Painting",
            "slug": "gold_series_002Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-002/1295487/6098253/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/GOLD_SERIES_002Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 241,
            "title": "GOLD SERIES 003 Painting",
            "slug": "gold_series_003Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-003/1295487/6098213/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/GOLD_SERIES_003Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 240,
            "title": "GOLD SERIES 004 Painting",
            "slug": "gold_series_004Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-004/1295487/6098191/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/GOLD_SERIES_004Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 239,
            "title": "GOLD SERIES 005 Painting",
            "slug": "gold_series_005Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-005/1295487/6098179/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/GOLD_SERIES_005Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 238,
            "title": "GOLD SERIES 006 Painting",
            "slug": "gold_series_006Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-006/1295487/6412863/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/GOLD_SERIES_006Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 134,
            "title": "Abstract Art Painting",
            "slug": "abstract_artPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Abstract-Art/1295487/8106198/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Abstract_ArtPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 133,
            "title": "White Minimal Painting Painting",
            "slug": "white_minimal_paintingPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-White-Minimal-Painting/1295487/8106206/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/White_Minimal_PaintingPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 132,
            "title": "Minimal Abstract Painting",
            "slug": "minimal_abstractPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Minimal-Abstract/1295487/8106214/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Minimal_AbstractPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 131,
            "title": "Ocean Abstract Painting",
            "slug": "ocean_abstractPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Ocean-Abstract/1295487/8106216/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Ocean_AbstractPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 130,
            "title": "Abstract Oil Painting",
            "slug": "abstract_oilPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Abstract-Oil-Painting/1295487/8123281/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Abstract_OilPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 129,
            "title": "Abstract Seascape Painting",
            "slug": "abstract_seascapePainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Abstract-Seascape/1295487/8123307/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Abstract_SeascapePainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 128,
            "title": "Minimal White Painting Painting",
            "slug": "minimal_white_paintingPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Minimal-White-Painting/1295487/8123315/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Minimal_White_PaintingPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 127,
            "title": "Modern Art Painting",
            "slug": "modern_artPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Modern-Art/1295487/8123321/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Modern_ArtPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 126,
            "title": "Abstract Ocean Painting",
            "slug": "abstract_oceanPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Abstract-Ocean/1295487/8123447/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Abstract_OceanPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 125,
            "title": "Abstract Landscape Painting",
            "slug": "abstract_landscapePainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Abstract-Landscape/1295487/8123730/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Abstract_LandscapePainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 124,
            "title": "Modern Minimal Painting",
            "slug": "modern_minimalPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Modern-Minimal/1295487/8124953/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Modern_MinimalPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 123,
            "title": "Modern Painting Painting",
            "slug": "modern_paintingPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Modern-Painting/1295487/8124976/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Modern_PaintingPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 112,
            "title": "Unity Painting",
            "slug": "unityPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Unity/1295487/8125409/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/UnityPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 111,
            "title": "Morning Joe Painting",
            "slug": "morning_joePainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Morning-Joe/1295487/8125458/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Morning_JoePainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 110,
            "title": "self portrait 1 Painting",
            "slug": "self_portrait_1Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Self-Portrait-1/1295487/8125469/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/self_portrait_1Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 109,
            "title": "Portal 1 Painting",
            "slug": "portal_1Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-1/1295487/8146533/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Portal_1Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 108,
            "title": "Portal 2 Painting",
            "slug": "portal_2Painting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-2/1295487/8146546/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Portal_2Painting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 107,
            "title": "Heart Work Painting",
            "slug": "heart_workPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Heart-Work/1295487/8146572/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Heart_WorkPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 106,
            "title": "Puzzled Painting",
            "slug": "puzzledPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Puzzled/1295487/8146584/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/PuzzledPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 105,
            "title": "Sheet Music Painting",
            "slug": "sheet_musicPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Sheet-Music/1295487/8146759/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Sheet_MusicPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 104,
            "title": "Finger print Painting",
            "slug": "finger_printPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Finger-Print/1295487/8754025/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Finger_printPainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 103,
            "title": "Meeting in the Middle Painting",
            "slug": "meeting_in_the_middlePainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Meeting-In-The-Middle/1295487/8754042/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/Meeting_in_the_MiddlePainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 102,
            "title": "Convergence Painting",
            "slug": "convergencePainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Convergence/1295487/8754060/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/ConvergencePainting.jpg",
            "date": "2025-09-25T15:30:02"
        },
        {
            "id": 101,
            "title": "Caviar Painting",
            "slug": "caviarPainting",
            "saatchi_url": "https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view",
            "image_url": "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/CaviarPainting.jpg",
            "date": "2025-09-25T15:30:02"
        }
    ];

    // 2. LOGIC
    window.scrapeSaatchi = async function (links) {
        const results = [];
        const errors = [];

        // Helper: Fetch with retry and delay
        const fetchWithDelay = (url, delay) => new Promise(resolve => setTimeout(() => {
            console.log(`Fetching ${url}...`);
            fetch(url).then(res => res.text()).then(resolve).catch(e => resolve(null));
        }, delay));

        // Process in chunks to avoid overwhelming the browser network
        const chunkSize = 10;
        for (let i = 0; i < links.length; i += chunkSize) {
            const chunk = links.slice(i, i + chunkSize);
            console.log(`Processing chunk ${i / chunkSize + 1} of ${Math.ceil(links.length / chunkSize)}...`);

            await Promise.all(chunk.map(async (item) => {
                try {
                    // Start with proxy
                    const proxyUrl = 'https://api.allorigins.win/raw?url=' + encodeURIComponent(item.saatchi_url);
                    const html = await fetchWithDelay(proxyUrl, Math.random() * 2000);

                    if (!html) throw new Error("Fetch failed");

                    // Parse HTML
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');

                    // Extract Data
                    const jsonLd = Array.from(doc.querySelectorAll('script[type="application/ld+json"]'))
                        .map(s => { try { return JSON.parse(s.innerText); } catch (e) { return null; } })
                        .find(j => j && (j['@type'] === 'VisualArtwork' || j['@type'] === 'Product'));

                    let extracted = { ...item };

                    if (jsonLd) {
                        extracted.price = jsonLd.offers?.price || extractPrice(doc);
                        extracted.width = jsonLd.width?.value || extractDimension(doc, 'width');
                        extracted.height = jsonLd.height?.value || extractDimension(doc, 'height');
                        extracted.medium = jsonLd.artMedium || extractMedium(doc);
                        extracted.year = jsonLd.dateCreated || extractYear(doc);
                    } else {
                        // Fallback manual scraping
                        extracted.price = extractPrice(doc);
                        extracted.medium = extractMedium(doc);
                        extracted.dimensions = extractDimensionsString(doc); // "48 x 48 in"
                    }

                    // Additional Cleanup
                    // Remove "Painting" suffix from title if present
                    extracted.cleanTitle = item.title.replace(/ Painting$/i, '');

                    results.push(extracted);

                } catch (err) {
                    console.error(`Failed ${item.title}:`, err);
                    errors.push({ id: item.id, error: err.message });
                    // Keep the item but mark as failed data
                    results.push({ ...item, scrape_failed: true });
                }
            }));

            // Wait a bit between chunks
            await new Promise(r => setTimeout(r, 1000));
        }

        console.log("Scraping Complete!");
        console.log("DATA_START");
        console.log(JSON.stringify(results, null, 2));
        console.log("DATA_END");
        return results;
    };

    function extractPrice(doc) {
        // Look for $ symbol
        const el = Array.from(doc.querySelectorAll('*')).find(e => e.innerText && e.innerText.includes('$') && e.innerText.length < 20);
        return el ? el.innerText.trim().replace(/[^0-9.]/g, '') : null;
    }
    function extractMedium(doc) { return "Mixed Media"; }
    function extractYear(doc) { return "2024"; }
    function extractDimension(doc, type) { return ""; }
    function extractDimensionsString(doc) { return ""; }

    // 3. EXECUTE
    window.scrapeSaatchi(artworkLinks);
})();
