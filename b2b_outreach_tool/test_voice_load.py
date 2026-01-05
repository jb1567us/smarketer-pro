
try:
    import speech_recognition as sr
    print("SpeechRecognition imported")
    import pyttsx3
    print("pyttsx3 imported")
    import pyaudio
    print("pyaudio imported")
    from src.utils.voice_manager import VoiceManager
    print("VoiceManager imported")
    
    vm = VoiceManager()
    print("VoiceManager instantiated")
    vm.stop_listening()
    print("Success")
except Exception as e:
    print(f"Error: {e}")
