
import time
import traceback
from src.utils.voice_manager import VoiceManager

def test_voice_toggle():
    vm = None
    try:
        print("Initializing VoiceManager...")
        vm = VoiceManager()
        
        print("Starting listener...")
        vm.start_listening()
        if vm.listen_stopper is None:
            print("ERROR: listen_stopper is None after start")
            return
        print("Listener started.")
        time.sleep(1)
        
        print("Stopping listener...")
        vm.stop_listening()
        if vm.listen_stopper is not None:
             print("ERROR: listen_stopper is NOT None after stop")
             return
        print("Listener stopped.")
        time.sleep(1)
        
        print("Restarting listener...")
        vm.start_listening()
        if vm.listen_stopper is None:
            print("ERROR: listen_stopper is None after RESTART")
            return
        print("Listener restarted.")
        
        vm.stop_listening()
        print("Success.")
    except Exception as e:
        print(f"EXCEPTION: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_voice_toggle()
