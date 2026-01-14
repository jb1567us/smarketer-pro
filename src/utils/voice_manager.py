
import speech_recognition as sr
import pyttsx3
import threading
import time
import queue

class VoiceManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(VoiceManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, wake_word="hey stanley", sleep_word="stanley go to sleep"):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        
        self.wake_word = wake_word.lower()
        self.sleep_word = sleep_word.lower()
        self.is_listening = False
        self.is_awake = False 
        self.stop_event = threading.Event()
        self.command_queue = queue.Queue()
        
        # TTS Queue and Thread
        self.tts_queue = queue.Queue()
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()
        
        # Initialize STT
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        try:
            self.microphone = sr.Microphone()
        except Exception as e:
            print(f"[VoiceManager] Warning: No microphone found or error initializing: {e}")
        
        # Optimize recognizer
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.5
        self.recognizer.custom_phrase_time_limit = 5

        self.listen_stopper = None

    def _tts_worker(self):
        """Dedicated thread for TTS to avoid run loop errors."""
        import pythoncom
        pythoncom.CoInitialize() # Required for Windows COM in threads
        try:
            # Initialize engine within the thread that uses it
            engine = pyttsx3.init()
            self._setup_voice_engine(engine)
            
            while True:
                text = self.tts_queue.get()
                if text is None: break # Poison pill
                try:
                    engine.say(text)
                    engine.runAndWait()
                except Exception as e:
                    print(f"TTS Worker Error: {e}")
                self.tts_queue.task_done()
        except Exception as e:
            print(f"[VoiceManager] TTS thread crashed: {e}")
        finally:
            pythoncom.CoUninitialize()

    def _setup_voice_engine(self, engine):
        """Sets the voice to a British Male voice if available."""
        try:
            voices = engine.getProperty('voices')
            selected_voice = None
            for voice in voices:
                if "GB" in voice.id or "UK" in voice.id or "english-uk" in voice.id.lower():
                    if "male" in voice.name.lower() or "david" in voice.name.lower():
                        selected_voice = voice.id
                        break
            
            if not selected_voice:
                for voice in voices:
                    if "male" in voice.name.lower():
                        selected_voice = voice.id
                        break
            
            if selected_voice:
                engine.setProperty('voice', selected_voice)
        except Exception:
            pass # Ignore voice setup errors

    def setup_voice(self):
        # Deprecated: setup happens in worker now
        pass
            
    def speak(self, text):
        """Speaks the given text non-blocking via queue."""
        self.tts_queue.put(text)

    def start_listening(self):
        """Starts the background listening using speech_recognition's built-in background thread."""
        if self.listen_stopper:
            return
        
        if not self.microphone:
            print("[VoiceManager] Cannot start listening: No microphone initialized.")
            return
            
        try:
            # Adjust for noise once before starting
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except AttributeError:
             # Common PyAudio error if device is unavailable: 'NoneType' object has no attribute 'close'
             print("[VoiceManager] Error: Microphone seems inaccessible (PyAudio check failed). Voice disabled.")
             return
        except Exception as e:
            print(f"[VoiceManager] Noise adjustment skipped/failed: {e}")
            return

        try:
            # listen_in_background returns a function to call to stop listening
            self.listen_stopper = self.recognizer.listen_in_background(self.microphone, self._callback, phrase_time_limit=10)
        except Exception as e:
            print(f"[VoiceManager] Failed to start background listener: {e}")
            self.listen_stopper = None

    def stop_listening(self):
        """Stops the background listening."""
        self.is_awake = False
        if self.listen_stopper:
            self.listen_stopper(wait_for_stop=True)
            self.listen_stopper = None

    def _callback(self, recognizer, audio):
        """Called by the background thread when audio is captured."""
        try:
            # Recognize - This runs in a worker thread spawned by listen_in_background
            text = recognizer.recognize_google(audio).lower()
            print(f"Heard: {text}")
            
            # Emit transcription for UI
            self.command_queue.put({"type": "transcription", "payload": text})
            
            if self.is_awake:
                if self.sleep_word in text:
                    self.is_awake = False
                    self.speak("Going to sleep.")
                    self.command_queue.put({"type": "status", "payload": "sleeping"})
                else:
                    # It's a command
                    self.command_queue.put({"type": "command", "payload": text})
            else:
                if self.wake_word in text:
                    self.is_awake = True
                    self.speak("Yes?") 
                    self.command_queue.put({"type": "status", "payload": "listening"})
                    
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            print("STT Service Error")
        except Exception as e:
            print(f"Callback Error: {e}")

    def get_latest_event(self):
        """Returns the latest event from the queue if any."""
        try:
            return self.command_queue.get_nowait()
        except queue.Empty:
            return None
