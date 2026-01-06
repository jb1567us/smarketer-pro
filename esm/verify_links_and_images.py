import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://elliotspencermorgan.com")
        
        # Check if In the Dark is gone
        content = await page.content()
        if "In the Dark" not in content:
            print("SUCCESS: 'In the Dark' is absent.")
        else:
            print("FAILURE: 'In the Dark' is present.")

        # Check the 5 items
        items = [
            {"name": "Right Way", "link_part": "Printmaking-Right-Way"},
            {"name": "Start Sign", "link_part": "Printmaking-Start-Sign"},
            {"name": "No Public Shrooms", "link_part": "no-public-shrooms"},
            {"name": "Mushroom Exclamation", "link_part": "Painting-Mushroom-Exclamation"},
            {"name": "Excited Bird", "link_part": "Painting-Excited-Bird"},
        ]

        for item in items:
            print(f"Checking {item['name']}...")
            # Find closest link
            # We look for text that matches name
            locator = page.get_by_text(item['name'])
            count = await locator.count()
            if count > 0:
                # Assuming the text is inside or near the link
                # Try to find the link element
                # In the layout: <div class="artwork-card"><a href...><img...></a><div class="title">...</div></div>
                # So we go up from title to card, then find 'a'
                
                # We can verify via JS for robustness
                result = await page.evaluate(f"""
                    () => {{
                        const els = Array.from(document.querySelectorAll('.artwork-card-title')).filter(e => e.textContent.includes("{item['name']}"));
                        if (els.length === 0) return {{ found: false }};
                        const card = els[0].closest('.artwork-card');
                        const link = card.querySelector('a');
                        const img = link.querySelector('img');
                        return {{
                            found: true,
                            href: link.href,
                            imgSrc: img.src,
                            imgNaturalWidth: img.naturalWidth
                        }};
                    }}
                """)
                
                if result['found']:
                    if item['link_part'].lower() in result['href'].lower():
                        print(f"  -> Link OK: {result['href']}")
                    else:
                        print(f"  -> Link MISMATCH: {result['href']}")
                    
                    if result['imgNaturalWidth'] > 0:
                        print(f"  -> Image OK: {result['imgNaturalWidth']}px width")
                    else:
                        print(f"  -> Image BROKEN (0px width)")
                else:
                    print("  -> Not found in DOM")

            else:
                 print("  -> Text not found")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
