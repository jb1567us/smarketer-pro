
import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def verify():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("Navigating to Trade Portal...")
        driver.get("https://elliotspencermorgan.com/trade/?v=verify_auto")
        
        # Wait for grid
        print("Waiting for grid...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card"))
        )
        
        # Click first visualize button
        print("Clicking Visualize button...")
        buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Visualize in Room')]")
        if not buttons:
            print("❌ No 'Visualize in Room' buttons found")
            return
            
        driver.execute_script("arguments[0].click();", buttons[0])
        
        # Wait for modal
        print("Waiting for modal...")
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "visualizer-modal"))
        )
        
        # Wait for image
        time.sleep(3)
        
        # Check image src
        img = driver.find_element(By.ID, "room-image-layer")
        src = img.get_attribute("src")
        print(f"Room Image Source: {src}")
        
        if "istockphoto" in src:
            print("✅ Verification Successful: Default image loaded!")
        else:
            print(f"❌ Verification Failed: Image source is {src}")
            
        # Screenshot
        driver.save_screenshot("c:\\sandbox\\esm\\verify_proof.png")
        print("Screenshot saved to c:\\sandbox\\esm\\verify_proof.png")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    verify()
