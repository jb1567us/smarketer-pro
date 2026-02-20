"""
Settings Page View
"""
import reflex as rx
from b2b_outreach_proto.states.settings import SettingsState


def settings_section_nav():
    """Navigation for settings sections"""
    return rx.vstack(
        rx.heading("Settings", size="7", color="indigo.400", margin_bottom="4"),
        
        rx.vstack(
            rx.button(
                rx.hstack(
                    rx.icon("key", size=18),
                    rx.text("API Keys"),
                    spacing="2"
                ),
                on_click=lambda: SettingsState.set_section("api_keys"),
                variant="ghost",
                width="100%",
                justify_content="start",
                color=rx.cond(SettingsState.current_section == "api_keys", "indigo.300", "gray.400"),
                bg=rx.cond(SettingsState.current_section == "api_keys", "indigo.900/30", "transparent"),
            ),
            rx.button(
                rx.hstack(
                    rx.icon("mail", size=18),
                    rx.text("Email Providers"),
                    spacing="2"
                ),
                on_click=lambda: SettingsState.set_section("email"),
                variant="ghost",
                width="100%",
                justify_content="start",
                color=rx.cond(SettingsState.current_section == "email", "indigo.300", "gray.400"),
                bg=rx.cond(SettingsState.current_section == "email", "indigo.900/30", "transparent"),
            ),
            rx.button(
                rx.hstack(
                    rx.icon("gauge", size=18),
                    rx.text("Rate Limits"),
                    spacing="2"
                ),
                on_click=lambda: SettingsState.set_section("rate_limits"),
                variant="ghost",
                width="100%",
                justify_content="start",
                color=rx.cond(SettingsState.current_section == "rate_limits", "indigo.300", "gray.400"),
                bg=rx.cond(SettingsState.current_section == "rate_limits", "indigo.900/30", "transparent"),
            ),
            rx.button(
                rx.hstack(
                    rx.icon("settings", size=18),
                    rx.text("Advanced"),
                    spacing="2"
                ),
                on_click=lambda: SettingsState.set_section("advanced"),
                variant="ghost",
                width="100%",
                justify_content="start",
                color=rx.cond(SettingsState.current_section == "advanced", "indigo.300", "gray.400"),
                bg=rx.cond(SettingsState.current_section == "advanced", "indigo.900/30", "transparent"),
            ),
            spacing="1",
            width="100%",
        ),
        
        width="250px",
        align_items="start",
        padding="4",
    )


def api_keys_section():
    """API keys configuration section"""
    return rx.vstack(
        rx.heading("API Keys", size="6", color="gray.100", margin_bottom="4"),
        
        # OpenAI
        rx.box(
            rx.vstack(
                rx.text("OpenAI API Key", font_weight="bold", color="gray.300"),
                rx.hstack(
                    rx.input(
                        value=SettingsState.openai_key_display,
                        type="password",
                        width="300px",
                        disabled=True,
                    ),
                    rx.button(
                        rx.icon("pencil", size=16),
                        variant="soft",
                        size="2",
                    ),
                    rx.button(
                        "Test",
                        on_click=lambda: SettingsState.test_api_key("openai"),
                        variant="soft",
                        size="2",
                        color_scheme="green",
                    ),
                    spacing="2",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        # Anthropic
        rx.box(
            rx.vstack(
                rx.text("Anthropic API Key", font_weight="bold", color="gray.300"),
                rx.hstack(
                    rx.input(
                        value=SettingsState.anthropic_key_display,
                        type="password",
                        width="300px",
                        disabled=True,
                    ),
                    rx.button(
                        rx.icon("pencil", size=16),
                        variant="soft",
                        size="2",
                    ),
                    rx.button(
                        "Test",
                        on_click=lambda: SettingsState.test_api_key("anthropic"),
                        variant="soft",
                        size="2",
                        color_scheme="green",
                    ),
                    spacing="2",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        # Groq
        rx.box(
            rx.vstack(
                rx.text("Groq API Key", font_weight="bold", color="gray.300"),
                rx.hstack(
                    rx.input(
                        value=SettingsState.groq_key_display,
                        type="password",
                        width="300px",
                        disabled=True,
                    ),
                    rx.button(
                        rx.icon("pencil", size=16),
                        variant="soft",
                        size="2",
                    ),
                    rx.button(
                        "Test",
                        on_click=lambda: SettingsState.test_api_key("groq"),
                        variant="soft",
                        size="2",
                        color_scheme="green",
                    ),
                    spacing="2",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        # Test Result
        rx.cond(
            SettingsState.test_result != "",
            rx.box(
                rx.text(SettingsState.test_result, color="gray.300"),
                padding="3",
                border_radius="md",
                bg="slate.800",
                border="1px solid",
                border_color="slate.700",
            ),
            rx.fragment(),
        ),
        
        spacing="4",
        width="100%",
        align_items="start",
    )


def email_providers_section():
    """Email providers configuration"""
    return rx.vstack(
        rx.heading("Email Providers", size="6", color="gray.100", margin_bottom="4"),
        
        rx.box(
            rx.vstack(
                rx.text("SendGrid API Key", font_weight="bold", color="gray.300"),
                rx.input(
                    value=SettingsState.sendgrid_key_display,
                    type="password",
                    width="300px",
                    disabled=True,
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        rx.box(
            rx.vstack(
                rx.text("Resend API Key", font_weight="bold", color="gray.300"),
                rx.input(
                    value=SettingsState.resend_key_display,
                    type="password",
                    width="300px",
                    disabled=True,
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        rx.box(
            rx.vstack(
                rx.text("Default Provider", font_weight="bold", color="gray.300"),
                rx.select(
                    ["sendgrid", "resend"],
                    value=SettingsState.default_email_provider,
                    on_change=SettingsState.set_default_email_provider,
                    width="200px",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        spacing="4",
        width="100%",
        align_items="start",
    )


def rate_limits_section():
    """Rate limits configuration"""
    return rx.vstack(
        rx.heading("Rate Limits", size="6", color="gray.100", margin_bottom="4"),
        
        rx.box(
            rx.vstack(
                rx.text("API Rate Limit (req/min)", font_weight="bold", color="gray.300"),
                rx.input(
                    value=SettingsState.api_rate_limit,
                    on_change=SettingsState.set_api_rate_limit,
                    type="number",
                    width="200px",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        rx.box(
            rx.vstack(
                rx.text("LLM Rate Limit (calls/min)", font_weight="bold", color="gray.300"),
                rx.input(
                    value=SettingsState.llm_rate_limit,
                    on_change=SettingsState.set_llm_rate_limit,
                    type="number",
                    width="200px",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        rx.box(
            rx.vstack(
                rx.text("Scrape Rate Limit (req/min)", font_weight="bold", color="gray.300"),
                rx.input(
                    value=SettingsState.scrape_rate_limit,
                    on_change=SettingsState.set_scrape_rate_limit,
                    type="number",
                    width="200px",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        spacing="4",
        width="100%",
        align_items="start",
    )


def advanced_section():
    """Advanced settings"""
    return rx.vstack(
        rx.heading("Advanced Settings", size="6", color="gray.100", margin_bottom="4"),
        
        rx.box(
            rx.vstack(
                rx.text("Secrets Backend", font_weight="bold", color="gray.300"),
                rx.select(
                    ["env", "vault", "aws"],
                    value=SettingsState.secrets_backend,
                    on_change=SettingsState.set_secrets_backend,
                    width="200px",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        rx.box(
            rx.vstack(
                rx.text("Redis URL", font_weight="bold", color="gray.300"),
                rx.input(
                    value=SettingsState.redis_url,
                    on_change=SettingsState.set_redis_url,
                    width="400px",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("Metrics Enabled", font_weight="bold", color="gray.300"),
                    rx.switch(
                        checked=SettingsState.metrics_enabled,
                        on_change=SettingsState.set_metrics_enabled,
                    ),
                    spacing="3",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("Rate Limiting Enabled", font_weight="bold", color="gray.300"),
                    rx.switch(
                        checked=SettingsState.rate_limit_enabled,
                        on_change=SettingsState.set_rate_limit_enabled,
                    ),
                    spacing="3",
                ),
                align_items="start",
                spacing="2",
            ),
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="slate.700",
            bg="slate.800/50",
        ),
        
        spacing="4",
        width="100%",
        align_items="start",
    )


def settings_view():
    """Main settings view"""
    return rx.vstack(
        rx.hstack(
            settings_section_nav(),
            
            rx.box(
                rx.vstack(
                    rx.cond(
                        SettingsState.current_section == "api_keys",
                        api_keys_section(),
                        rx.cond(
                            SettingsState.current_section == "email",
                            email_providers_section(),
                            rx.cond(
                                SettingsState.current_section == "rate_limits",
                                rate_limits_section(),
                                advanced_section(),
                            ),
                        ),
                    ),
                    
                    # Save Button
                    rx.hstack(
                        rx.button(
                            rx.hstack(
                                rx.icon("save", size=18),
                                rx.text("Save Settings"),
                                spacing="2",
                            ),
                            on_click=SettingsState.save_settings,
                            variant="solid",
                            color_scheme="indigo",
                        ),
                        rx.cond(
                            SettingsState.save_status != "",
                            rx.text(SettingsState.save_status, color="gray.300"),
                            rx.fragment(),
                        ),
                        spacing="3",
                        margin_top="6",
                    ),
                    
                    width="100%",
                    align_items="start",
                    padding="6",
                ),
                flex="1",
                border_left="1px solid",
                border_color="slate.800",
            ),
            
            width="100%",
            align_items="start",
            spacing="0",
            height="calc(100vh - 100px)",
        ),
        width="100%",
        on_mount=SettingsState.on_load,
    )
