import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

async def test_whisper():
    try:
        from utils.local_whisper import LocalWhisperSolver
        print("--- Local Whisper Test ---")
        solver = LocalWhisperSolver(model_name="tiny")
        
        # Check ffmpeg
        if not solver._check_ffmpeg():
            print("❌ Error: ffmpeg not found. Please install ffmpeg and add to PATH.")
            return

        # Use a dummy audio URL to test loading and initial GET
        # In a real test, you'd use a known captcha audio link
        test_url = "https://www.google.com/recaptcha/api2/payload?p=dummy"
        
        print("Testing model loading...")
        await solver._load_model()
        print("✅ Model loaded.")
        
        print("\nNote: To fully test, you need a valid reCAPTCHA audio URL.")
        print("The solver is ready for integration once dependencies are finished.")
        
    except ImportError as e:
        print(f"❌ Dependencies not ready: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_whisper())
