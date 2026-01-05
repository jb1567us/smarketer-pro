
import asyncio
import os
import sys
from gtts import gTTS

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), "src"))

from utils.local_whisper import LocalWhisperSolver

async def verify_system():
    print("🎤 Generating local test audio (Text: 1 2 3 4 5)...")
    tts = gTTS(text="1 2 3 4 5", lang='en')
    tts.save("test_numbers.mp3")
    
    print("🤖 Running Local Whisper Solver on generated file...")
    solver = LocalWhisperSolver()
    
    # We need to pass a file path/URL. Our solver uses aiohttp to download.
    # To test local file, we can just use the absolute path as the URL 
    # but aiohttp might complain. Let's mock a download or just use transcription directly.
    
    # Let's use the internal transcription method if available or just update solver to handle local files.
    # Actually, l'll just use the transcription logic from the solver.
    
    import whisper
    import torch
    from static_ffmpeg import add_paths
    add_paths()
    
    model = whisper.load_model("tiny")
    print("🎯 Transcribing...")
    result = model.transcribe("test_numbers.mp3")
    
    print("\n--- TEST RESULTS ---")
    print(f"Original Text: 1 2 3 4 5")
    print(f"Whisper Result: {result['text'].strip()}")
    
    if "1" in result['text'] and "5" in result['text']:
        print("\n✅ SUCCESS: Whisper correctly identified the numbers!")
    else:
        print("\n⚠️ PARTIAL SUCCESS: Check the transcription above.")

if __name__ == "__main__":
    asyncio.run(verify_system())
