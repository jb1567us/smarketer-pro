"""
Settings State Management for Reflex UI
"""
import reflex as rx
from typing import Dict, Any


class SettingsState(rx.State):
    """State for settings page"""
    
    # API Keys (masked for display)
    openai_key_display: str = "••••••••"
    anthropic_key_display: str = "••••••••"
    groq_key_display: str = "••••••••"
    perplexity_key_display: str = "••••••••"
    
    # Email Provider Keys
    sendgrid_key_display: str = "••••••••"
    resend_key_display: str = "••••••••"
    default_email_provider: str = "sendgrid"
    
    # Rate Limits
    api_rate_limit: str = "100"
    llm_rate_limit: str = "50"
    scrape_rate_limit: str = "10"
    
    # Advanced Settings
    secrets_backend: str = "env"
    redis_url: str = "redis://localhost:6379"
    metrics_enabled: bool = True
    rate_limit_enabled: bool = True
    
    # UI State
    is_editing: bool = False
    current_section: str = "api_keys"
    save_status: str = ""
    test_result: str = ""
    
    def on_load(self):
        """Load settings from backend"""
        try:
            from backend.config.settings_manager import get_settings_manager
            manager = get_settings_manager()
            settings = manager.get_all()
            
            # Mask API keys for display
            self.openai_key_display = self._mask_key(settings.get("openai_api_key", ""))
            self.anthropic_key_display = self._mask_key(settings.get("anthropic_api_key", ""))
            self.groq_key_display = self._mask_key(settings.get("groq_api_key", ""))
            self.perplexity_key_display = self._mask_key(settings.get("perplexity_api_key", ""))
            self.sendgrid_key_display = self._mask_key(settings.get("sendgrid_api_key", ""))
            self.resend_key_display = self._mask_key(settings.get("resend_api_key", ""))
            
            # Load other settings
            self.default_email_provider = settings.get("default_email_provider", "sendgrid")
            self.api_rate_limit = settings.get("api_rate_limit", "100")
            self.llm_rate_limit = settings.get("llm_rate_limit", "50")
            self.scrape_rate_limit = settings.get("scrape_rate_limit", "10")
            self.secrets_backend = settings.get("secrets_backend", "env")
            self.redis_url = settings.get("redis_url", "redis://localhost:6379")
            self.metrics_enabled = settings.get("metrics_enabled", "true").lower() == "true"
            self.rate_limit_enabled = settings.get("rate_limit_enabled", "true").lower() == "true"
            
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def _mask_key(self, key: str) -> str:
        """Mask API key for display"""
        if not key or len(key) < 8:
            return "••••••••"
        return f"{key[:4]}••••{key[-4:]}"
    
    async def save_settings(self):
        """Save all settings"""
        try:
            from backend.config.settings_manager import get_settings_manager
            manager = get_settings_manager()
            
            # Only save non-masked values (actual implementation would handle this better)
            settings = {
                "default_email_provider": self.default_email_provider,
                "api_rate_limit": self.api_rate_limit,
                "llm_rate_limit": self.llm_rate_limit,
                "scrape_rate_limit": self.scrape_rate_limit,
                "secrets_backend": self.secrets_backend,
                "redis_url": self.redis_url,
                "metrics_enabled": str(self.metrics_enabled),
                "rate_limit_enabled": str(self.rate_limit_enabled),
            }
            
            success = manager.update_bulk(settings)
            
            if success:
                self.save_status = "✅ Settings saved successfully"
            else:
                self.save_status = "❌ Error saving settings"
                
        except Exception as e:
            self.save_status = f"❌ Error: {str(e)}"
    
    async def test_api_key(self, provider: str):
        """Test an API key"""
        try:
            from backend.config.settings_manager import get_settings_manager
            manager = get_settings_manager()
            
            # Get the actual key (in production, would retrieve from secrets)
            key = manager.get(f"{provider}_api_key", "")
            
            result = manager.test_api_key(provider, key)
            
            if result["success"]:
                self.test_result = f"✅ {result['message']}"
            else:
                self.test_result = f"❌ {result['message']}"
                
        except Exception as e:
            self.test_result = f"❌ Error testing key: {str(e)}"
    
    def set_section(self, section: str):
        """Change current section"""
        self.current_section = section
        self.save_status = ""
        self.test_result = ""
