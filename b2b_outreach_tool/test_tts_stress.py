
import time
from src.utils.voice_manager import VoiceManager

def test_tts_concurrency():
    print("Initializing VoiceManager...")
    vm = VoiceManager()
    
    print("Queueing multiple speech requests...")
    vm.speak("Test one.")
    vm.speak("Test two.")
    vm.speak("Test three.")
    
    print("Waiting for completion...")
    time.sleep(5) # Give it time to speak
    
    # Clean up (though VoiceManager doesn't have a full cleanup yet, simple exit is fine)
    print("Done.")

if __name__ == "__main__":
    test_tts_concurrency()
