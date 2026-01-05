
import asyncio
import os
import sys
import aiohttp

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from utils.local_whisper import LocalWhisperSolver

async def test_transcription():
    sample_url = "https://github.com/skylot/recaptcha-solver/raw/master/samples/audio_1.mp3"
    print(f"📥 Downloading sample audio from: {sample_url}")
    
    solver = LocalWhisperSolver()
    result = await solver.solve_audio(sample_url)
    
    print("\n--- Whisper Result ---")
    if result.get("status") == "success":
        print(f"✅ Transcription: {result['token']}")
        print("📊 (Expected result should be a sequence of numbers or words)")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(test_transcription())
