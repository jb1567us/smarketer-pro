import reflex as rx
from .base import BaseState

class NavState(BaseState):
    """Navigation and UI shell state."""
    tool_type: str = "Mass Harvester"
    filters_open: bool = False
    ai_assistant_open: bool = False
    ai_assistant_history: list[dict] = []
    ai_assistant_input: str = ""
    is_assistant_thinking: bool = False
    sidebar_expand: bool = False
    sidebar_width_px: int = 280
    
    # Voice Synthesis
    voice_enabled: bool = False
    available_voices: list[str] = ["Default"]
    selected_voice: str = "Default"
    speech_rate: float = 0.9
    speech_pitch: float = 1.0

    @rx.var
    def sidebar_width(self) -> str:
        return f"{self.sidebar_width_px}px"
        
    def set_sidebar_width_px(self, width: str):
        try:
            w = int(float(width))
            self.sidebar_width_px = max(200, min(800, w))
        except (ValueError, TypeError):
            pass

    def toggle_sidebar_expand(self):
        if self.sidebar_width_px == 280:
            self.sidebar_width_px = 500
        else:
            self.sidebar_width_px = 280

    def stop_speech(self):
        """Immediately stops any ongoing TTS."""
        return rx.call_script("window.speechSynthesis.cancel();")

    def set_selected_voice(self, voice: str):
        self.selected_voice = voice

    async def set_tool(self, tool: str):
        if not isinstance(tool, str):
            return
        self.tool_type = tool
    
    def toggle_filters(self):
        self.filters_open = not self.filters_open
    
    def toggle_ai_assistant(self):
        self.ai_assistant_open = not self.ai_assistant_open

    async def send_ai_assistant_message(self):
        """Send a message to the AI assistant (Eugene)."""
        if not self.ai_assistant_input:
            return
        
        user_msg = {"role": "user", "content": self.ai_assistant_input}
        self.ai_assistant_history.append(user_msg)
        query = self.ai_assistant_input
        self.ai_assistant_input = ""
        self.is_assistant_thinking = True
        yield
        
        if DB_AVAILABLE:
            try:
                from backend.automation_engine import AutomationEngine
                engine = AutomationEngine()
                response = await asyncio.to_thread(engine.chat, query)
                self.ai_assistant_history.append({"role": "AI", "content": response})
            except Exception as e:
                self.handle_error(e, "AI Assistant")
                self.ai_assistant_history.append({"role": "AI", "content": f"Error: {e}"})
        else:
            await asyncio.sleep(1)
            self.ai_assistant_history.append({"role": "AI", "content": "Database/AI not available in this environment."})
            
        self.is_assistant_thinking = False

    def clear_ai_assistant_history(self):
        self.ai_assistant_history = []
        self.add_log("AI Assistant history cleared")

    def download_assistant_history(self):
        import json
        return rx.download(
            data=json.dumps(self.ai_assistant_history),
            filename="assistant_history.json"
        )
    
    def set_ai_assistant_input(self, val: str):
        self.ai_assistant_input = val

    def set_available_voices_raw(self, voices_json: str):
        """Special handler for voices from browser script."""
        import json
        try:
            voices = json.loads(voices_json)
            self.available_voices = voices
        except:
            pass
    
    def load_voices(self):
        """Trigger browser to list voices."""
        return rx.call_script(
            """
            (function() {
                const voices = window.speechSynthesis.getVoices().map(v => v.name);
                const syncInput = document.getElementById('voice-list-sync');
                if (syncInput) {
                    syncInput.value = JSON.stringify(voices);
                    syncInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            })();
            """
        )

    def speak(self, text: str):
        """Speak text using browser TTS."""
        if not self.voice_enabled:
            return
        
        safe_text = text.replace("'", "\\'").replace("\\n", " ")
        return rx.call_script(
            f"""
            (function() {{
                const utterance = new SpeechSynthesisUtterance('{safe_text}');
                utterance.pitch = {self.speech_pitch};
                utterance.rate = {self.speech_rate};
                window.speechSynthesis.speak(utterance);
            }})();
            """
        )

