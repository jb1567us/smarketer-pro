
import sys
import os
import time
from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print("Navigating to Trade Portal...")
            page.goto("https://elliotspencermorgan.com/trade/?v=verify_auto")
            
            # Wait for grid
            print("Waiting for grid...")
            page.wait_for_selector(".card", timeout=20000)
            
            # Click first visualize button
            print("Clicking Visualize button...")
            # Use a robust selector for the button
            button = page.locator("button:has-text('Visualize in Room')").first
            if not button.count():
                print("❌ No 'Visualize in Room' buttons found")
                return
            
            button.click()
            
            # Wait for modal
            print("Waiting for modal...")
            page.wait_for_selector("#visualizer-modal.active", timeout=10000)
            
            # Wait for image
            print("Waiting for image to populate...")
            # We specifically want to check if the src *changes* or is set to the default
            # Let's wait a moment for JS to fire
            time.sleep(3) 
            
            img = page.locator("#room-image-layer")
            src = img.get_attribute("src")
            print(f"Room Image Source: {src}")
            
            if src and "istockphoto" in src:
                print("✅ Verification Successful: Default image loaded!")
            else:
                print(f"❌ Verification Failed: Image source is {src}")
                
            # Screenshot
            page.screenshot(path="c:\\sandbox\\esm\\verify_proof.png")
            print("Screenshot saved to c:\\sandbox\\esm\\verify_proof.png")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    verify()
