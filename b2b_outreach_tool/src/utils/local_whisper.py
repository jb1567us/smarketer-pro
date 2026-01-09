import os
import asyncio
import aiohttp
import tempfile
import whisper
import torch
import shutil
import subprocess
from static_ffmpeg import add_paths as add_ffmpeg_paths

class LocalWhisperSolver:
    _instance = None
    _model = None

    def __new__(cls, model_name="tiny"):
        if cls._instance is None:
            cls._instance = super(LocalWhisperSolver, cls).__new__(cls)
            cls._model_name = model_name
        return cls._instance

    def _check_ffmpeg(self):
        """Checks if ffmpeg is available in the system path, and try to add static-ffmpeg paths."""
        if shutil.which("ffmpeg") is not None:
            return True
        
        # Try to add static-ffmpeg paths
        try:
            add_ffmpeg_paths()
            if shutil.which("ffmpeg") is not None:
                print("  [LocalWhisper] FFmpeg found via static-ffmpeg paths.")
                return True
        except:
            pass
            
        return False

    async def _load_model(self):
        """Lazy loads the Whisper model."""
        if self._model is None:
            print(f"  [LocalWhisper] Loading Whisper model: {self._model_name}...")
            # Run in thread to avoid blocking loop
            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(None, lambda: whisper.load_model(self._model_name))
            print("  [LocalWhisper] Model loaded successfully.")

    async def solve_audio(self, audio_url):
        """
        Downloads a captcha audio file and transcribes it using local Whisper.
        """
        if not self._check_ffmpeg():
            return {"error": "ffmpeg not found on system. Local Whisper requires ffmpeg installed and in PATH."}

        await self._load_model()

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(audio_url) as response:
                    if response.status != 200:
                        return {"error": f"Failed to download audio: HTTP {response.status}"}
                    
                    content = await response.read()
                    
                    # Create temporary file
                    fd, path = tempfile.mkstemp(suffix=".mp3")
                    try:
                        with os.fdopen(fd, 'wb') as tmp:
                            tmp.write(content)
                        
                        # Transcribe
                        print(f"  [LocalWhisper] Transcribing audio from {audio_url}...")
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, lambda: self._model.transcribe(path))
                        
                        text = result.get("text", "").strip()
                        # Captcha audio usually contains digits separated by spaces or noise
                        # Clean up punctuation and non-alphanumeric if needed
                        cleaned_text = "".join(filter(str.isalnum, text))
                        
                        print(f"  [LocalWhisper] Transcription result: {cleaned_text}")
                        return {"status": "success", "token": cleaned_text}
                        
                    finally:
                        if os.path.exists(path):
                            os.remove(path)
            except Exception as e:
                return {"error": f"Local Whisper error: {str(e)}"}
