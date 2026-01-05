
import time
from src.utils.voice_manager import VoiceManager

def test_voice_toggle():
    print("Initializing VoiceManager...")
    vm = VoiceManager()
    
    print("Starting listener...")
    vm.start_listening()
    assert vm.listen_stopper is not None
    print("Listener started.")
    
    print("Stopping listener...")
    vm.stop_listening()
    assert vm.listen_stopper is None
    print("Listener stopped.")
    
    print("Restarting listener...")
    vm.start_listening()
    assert vm.listen_stopper is not None
    print("Listener restarted.")
    
    vm.stop_listening()
    print("Success.")

if __name__ == "__main__":
    test_voice_toggle()
