import reflex as rx
from .styles import *
from .state import State, NAVIGATION_ITEMS, DB_AVAILABLE
from .states.system import HeartbeatState
from .views import *
from .components import log_console_component
import sys
import os

def sidebar_chat_item(role: str, content: str):
    return rx.box(
        rx.vstack(
            rx.text(role, font_size="0.7em", font_weight="bold", color="indigo.300", text_transform="uppercase"),
            rx.markdown(content, color=rx.cond(role == "AI", "gray.200", "gray.300"), font_size="0.9em"),
            spacing="1",
            align_items="start",
        ),
        padding="3",
        border_radius="md",
        bg=rx.cond(role == "AI", "indigo.900/60", "slate.800/60"),
        margin_top="3",
        border="1px solid",
        border_color=rx.cond(role == "AI", "indigo.700/50", "slate.700/50"),
        width="100%",
    )

# Route mapping for navigation
ROUTE_MAP = {
    "Home": "/",
    "Leads": "/leads",
    "Campaigns": "/campaigns",
    "Sequences": "/sequences",
    "Inbox": "/inbox",
    "Pipeline": "/pipeline",
    "Tasks": "/tasks",
    "Analytics": "/analytics",
    "Settings": "/settings",
    "Mass Tools": "/mass-tools",
    "Agent Lab": "/agent-lab",
    "Proxy Lab": "/proxy-lab",
    "Automation Hub": "/automation-hub",
    "Workflow Builder": "/workflow-builder",
    "System Monitor": "/system-monitor",
    "Agent Factory": "/agent-factory",
    "Direct Search": "/direct-search",
    "Social Hub": "/social-hub",
    "Affiliate Hub": "/affiliate-hub",
    "DSR Manager": "/dsr-manager",
    "Designer": "/designer",
    "Video Studio": "/video-studio",
    "SEO Suite": "/seo-suite",
}

def sidebar():
    return rx.hstack(
        rx.vstack(
            rx.heading("🚀 Smarketer Pro", size="7", margin_bottom="8", color="indigo.400"),
            
            # Navigation section
            rx.text("Navigate", font_size="0.75em", font_weight="bold", color="gray.500", margin_bottom="2", text_transform="uppercase"),
            rx.vstack(
                *[
                    rx.link(
                        rx.button(
                            rx.hstack(rx.text(icon, font_size="1.1em"), rx.text(name), spacing="3"),
                            variant="ghost",
                            width="100%",
                            justify_content="start",
                            padding="2",
                            cursor="pointer",
                            border_radius="md",
                            color="gray.400",
                            _hover={"bg": "indigo.600/20", "color": "indigo.300"},
                        ),
                        href=ROUTE_MAP.get(name, "/"),
                        width="100%",
                        style={"textDecoration": "none"},
                    )
                    for icon, name in NAVIGATION_ITEMS
                ],
                width="100%",
                spacing="1",
                margin_bottom="4",
            ),
            
            # AI Assistant collapsible section
            rx.hstack(
                rx.button(
                    rx.hstack(
                        rx.cond(State.ai_assistant_open, rx.icon("chevron-down", size=16), rx.icon("chevron-right", size=16)),
                        rx.icon("bot", size=16),
                        rx.text("AI Assistant", font_weight="medium"),
                        spacing="2",
                    ),
                    on_click=lambda: State.toggle_ai_assistant(),
                    variant="ghost",
                    flex="1",
                    justify_content="start",
                    color="indigo.300",
                    padding="2",
                ),
                rx.cond(
                    State.ai_assistant_open,
                    rx.hstack(
                        rx.button(
                            rx.icon("square", size=14),
                            on_click=State.stop_speech,
                            variant="soft",
                            color_scheme="red",
                            title="Stop Speaking",
                            size="2",
                        ),
                        rx.button(
                            rx.icon("maximize-2", size=14),
                            on_click=State.toggle_sidebar_expand,
                            variant="ghost",
                            size="2",
                            color_scheme="gray",
                            title="Expand Sidebar",
                        ),
                        rx.button(
                            rx.icon("download", size=14),
                            on_click=State.download_assistant_history,
                            variant="ghost",
                            size="2",
                            color_scheme="gray",
                            title="Save Chat JSON",
                        ),
                        rx.button(
                            rx.icon("trash-2", size=14),
                            on_click=State.clear_ai_assistant_history,
                            variant="ghost",
                            size="2",
                            color_scheme="gray",
                            title="Clear History",
                        ),
                        spacing="2",
                        padding_right="2",
                    ),
                    rx.fragment(),
                ),
                width="100%",
            ),
            rx.cond(
                State.ai_assistant_open,
                rx.vstack(
                    rx.box(
                        rx.foreach(
                            State.ai_assistant_history,
                            lambda msg: sidebar_chat_item(msg["role"], msg["content"])
                        ),
                        rx.cond(
                            State.ai_assistant_history.length() == 0,
                            sidebar_chat_item("AI", "How can I help you today?"),
                            rx.fragment(),
                        ),
                        height="300px",
                        overflow_y="auto",
                        width="100%",
                        border="1px solid",
                        border_color="slate.700",
                        border_radius="md",
                        bg="slate.800",
                        padding="2",
                    ),
                    rx.hstack(
                        rx.input(
                            id="sidebar-ai-input",
                            name="sidebar_query",
                            placeholder="Ask manager...", 
                            variant="surface", 
                            size="2",
                            value=State.ai_assistant_input,
                            on_change=State.set_ai_assistant_input,
                            on_key_down=lambda key: rx.cond(
                                key == "Enter", 
                                State.send_ai_assistant_message(), 
                                rx.console_log("key: " + key)
                            ),
                            width="100%",
                        ),
                        rx.button(
                            rx.cond(
                                State.is_assistant_thinking,
                                rx.spinner(size="1"),
                                rx.icon("send", size=14),
                            ),
                            on_click=State.send_ai_assistant_message,
                            variant="soft",
                            size="2",
                            disabled=State.is_assistant_thinking,
                        ),
                        spacing="1",
                        width="100%",
                    ),
                    width="100%",
                    spacing="2",
                ),
                rx.fragment(),
            ),
            width="100%",
            height="100%",
            align_items="start",
            overflow_y="auto",
            position="relative",
            z_index="10",
            padding="4",
        ),
        # Draggable Resize Handle
        rx.box(
            width="6px",
            height="100vh",
            cursor="col-resize",
            bg="transparent",
            _hover={"bg": "indigo.500/50"},
            id="sidebar-resizer",
            on_mouse_down=rx.call_script(
                """
                (function() {
                    const resizer = document.getElementById('sidebar-resizer');
                    const sidebar = document.getElementById('sidebar-container');
                    
                    const onMouseMove = (e) => {
                        const newWidth = e.clientX;
                        if (newWidth > 150 && newWidth < 800) {
                            sidebar.style.width = newWidth + 'px';
                        }
                    };
                    
                    const onMouseUp = (e) => {
                        const finalWidth = e.clientX;
                        // Call the Reflex state to sync the final width
                        // We use the internal Reflex event trigger if we can find it, 
                        // but actually just clicking a hidden button is safer in this version.
                        const hiddenInput = document.getElementById('sidebar-width-sync');
                        if (hiddenInput) {
                            hiddenInput.value = finalWidth;
                            hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                        
                        document.removeEventListener('mousemove', onMouseMove);
                        document.removeEventListener('mouseup', onMouseUp);
                        document.body.style.cursor = 'default';
                    };
                    
                    document.addEventListener('mousemove', onMouseMove);
                    document.addEventListener('mouseup', onMouseUp);
                    document.body.style.cursor = 'col-resize';
                })();
                """
            ),
        ),
        rx.input(
            id="sidebar-width-sync",
            type="hidden",
            on_change=State.set_sidebar_width_px,
        ),
        rx.input(
            id="voice-list-sync",
            type="text",
            on_change=State.set_available_voices_raw,
            style={"position": "absolute", "opacity": "0", "pointer_events": "none", "height": "0", "width": "0"},
        ),
        id="sidebar-container",
        height="100vh",
        width=State.sidebar_width,
        bg="slate.950",
        border_right="1px solid",
        border_color="slate.800",
        spacing="0",
        transition="none", # Transition interferes with smooth drag
    )

def top_nav():
    return rx.box(
        rx.hstack(
            # Left side - Application branding
            rx.hstack(
                rx.text("📍 Smarketer Pro", font_weight="bold", color="indigo.300", font_size="1.1em"),
                rx.tooltip(
                    rx.box(
                        width="8px",
                        height="8px",
                        border_radius="full",
                        margin_left="2",
                        bg=rx.cond(
                            HeartbeatState.is_alive,
                            "green.500",
                            "red.500"
                        ),
                        box_shadow=rx.cond(
                            HeartbeatState.is_alive,
                            "0 0 5px #22c55e",
                            "0 0 5px #ef4444"
                        ),
                    ),
                    content="System Status: " + rx.cond(
                        HeartbeatState.is_alive,
                        "Operational",
                        "Connection Lost / Processing"
                    ),
                ),
                align_items="center",
            ),
            
            rx.spacer(),
            
            # Right side - Global CRUD & Tools
            rx.hstack(
                rx.button(
                    rx.hstack(rx.icon("plus"), rx.text("Create"), spacing="2"),
                    variant="ghost",
                    class_name=NAV_ITEM_STYLE,
                    on_click=lambda: State.handle_ui_action("Create"),
                ),
                rx.button(
                    rx.hstack(rx.icon("search"), rx.text("Search"), spacing="2"),
                    variant="ghost",
                    class_name=NAV_ITEM_STYLE,
                    on_click=lambda: State.handle_ui_action("Search"),
                ),
                rx.button(
                    rx.hstack(rx.icon("pencil"), rx.text("Edit"), spacing="2"),
                    variant="ghost",
                    class_name=NAV_ITEM_STYLE,
                    on_click=lambda: State.handle_ui_action("Edit"),
                ),
                rx.button(
                    rx.hstack(rx.icon("trash-2"), rx.text("Delete"), spacing="2"),
                    variant="ghost",
                    class_name=NAV_ITEM_STYLE,
                    on_click=lambda: State.handle_ui_action("Delete"),
                ),
                rx.divider(orientation="vertical", height="24px"),
                rx.button(
                    rx.hstack(rx.icon("filter"), rx.text("Filters"), spacing="2"),
                    variant="ghost",
                    class_name=NAV_ITEM_STYLE,
                    on_click=lambda: State.toggle_filters(),
                ),
                rx.button(
                    rx.hstack(rx.icon("settings"), rx.text("Settings"), spacing="2"),
                    variant="ghost",
                    class_name=NAV_ITEM_STYLE,
                    on_click=lambda: State.handle_ui_action("Settings"),
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.hstack(rx.icon("upload"), rx.text("Import"), spacing="2"),
                            variant="ghost",
                            class_name=NAV_ITEM_STYLE,
                            on_click=lambda: State.handle_ui_action("Import"),
                        ),
                    ),
                    rx.menu.content(
                        rx.menu.item(
                            rx.hstack(rx.icon("file-text"), rx.text("Import CSV"), spacing="2"),
                        ),
                        rx.menu.item(
                            rx.hstack(rx.icon("braces"), rx.text("Import JSON"), spacing="2"),
                        ),
                    ),
                ),
                rx.button(
                    rx.hstack(rx.icon("download"), rx.text("Export"), spacing="2"),
                    variant="ghost",
                    class_name=NAV_ITEM_STYLE,
                ),
                spacing="2",
            ),
            
            width="100%",
            align_items="center",
        ),
        class_name=TOP_NAV_STYLE,
    )

def notification_toast():
    """Global notification toast for errors, success, and info messages."""
    return rx.cond(
        State.global_error != "",
        rx.box(
            rx.hstack(
                rx.icon(
                    rx.match(
                        State.error_type,
                        ("error", "alert-circle"),
                        ("success", "check-circle"),
                        ("info", "info"),
                        "info"
                    ),
                    size=20,
                    color=rx.match(
                        State.error_type,
                        ("error", "red.400"),
                        ("success", "green.400"),
                        ("info", "blue.400"),
                        "gray.400"
                    )
                ),
                rx.text(State.global_error, flex="1", color="white"),
                rx.button(
                    "×",
                    on_click=State.clear_error,
                    variant="ghost",
                    size="1",
                    color="gray.400",
                    _hover={"color": "white"},
                ),
                align_items="center",
                spacing="3",
                width="100%",
            ),
            bg=rx.match(
                State.error_type,
                ("error", "red.900/80"),
                ("success", "green.900/80"),
                ("info", "blue.900/80"),
                "gray.900/80"
            ),
            border=rx.match(
                State.error_type,
                ("error", "1px solid"),
                ("success", "1px solid"),
                ("info", "1px solid"),
                "1px solid"
            ),
            border_color=rx.match(
                State.error_type,
                ("error", "red.600"),
                ("success", "green.600"),
                ("info", "blue.600"),
                "gray.600"
            ),
            padding="4",
            border_radius="lg",
            position="fixed",
            top="20px",
            right="20px",
            width="400px",
            max_width="90vw",
            z_index="9999",
            backdrop_filter="blur(10px)",
            box_shadow="0 8px 32px rgba(0, 0, 0, 0.4)",
        ),
        rx.fragment(),
    )

def page_layout(content: rx.Component) -> rx.Component:
    """Common layout wrapper for all pages."""
    return rx.hstack(
        sidebar(),
        rx.vstack(
            top_nav(),
            rx.cond(
                State.is_hydrated,
                rx.box(
                    content,
                    padding="8",
                    width="100%",
                    max_width="1200px",
                    margin="0 auto",
                    # Add a simple fade-in or slide-in animation
                    animation="fadeIn 0.5s ease-out",
                ),
                rx.center(
                    rx.vstack(
                        rx.spinner(size="3", color="indigo.500", thickness=2),
                        rx.text("Initializing Neural Interface...", color="indigo.300", font_size="0.9em"),
                        spacing="4",
                        align_items="center",
                    ),
                    height="80vh",
                    width="100%",
                ),
            ),
            width="100%",
            transition="padding-left 0.3s ease-in-out",
            overflow_y="auto",
            min_height="100vh",
            background="linear-gradient(to br, #0f172a, #1e1b4b)",
        ),
        notification_toast(),
        log_console_component(),
        # Global Agent Voice (Eugene)
        rx.cond(
            AgentState.war_room_audio_url != "",
            rx.audio(
                src=AgentState.war_room_audio_url,
                playing=True,
                controls=False,
                width="0",
                height="0",
            ),
            rx.fragment()
        ),
        width="100%",
        height="100vh",
        spacing="0",
    )

# Individual page functions for each route
def index() -> rx.Component:
    """Dashboard/Home page."""
    return page_layout(dashboard_view())

def leads_page() -> rx.Component:
    """Leads management page."""
    return page_layout(leads_view())

def campaigns_page() -> rx.Component:
    """Campaigns page."""
    return page_layout(campaigns_view())

def sequences_page() -> rx.Component:
    """Sequences page."""
    return page_layout(sequences_view())

def inbox_page() -> rx.Component:
    """Inbox/messaging page."""
    return page_layout(inbox_view())

def pipeline_page() -> rx.Component:
    """Pipeline page."""
    return page_layout(pipeline_view())

def tasks_page() -> rx.Component:
    """Tasks page."""
    return page_layout(tasks_view())

def analytics_page() -> rx.Component:
    """Analytics page."""
    return page_layout(analytics_view())

def settings_page() -> rx.Component:
    """Settings page."""
    return page_layout(settings_view())

def mass_tools_page() -> rx.Component:
    """Mass Tools page."""
    return page_layout(mass_tools_view())

def agent_lab_page() -> rx.Component:
    """Agent Laboratory page."""
    return page_layout(agent_lab_view())

def proxy_lab_page() -> rx.Component:
    """Proxy Laboratory page."""
    return page_layout(proxy_lab_view())

def automation_hub_page() -> rx.Component:
    """Automation Hub page."""
    return page_layout(automation_hub_view())

def workflow_builder_page() -> rx.Component:
    """Workflow Builder page."""
    return page_layout(workflow_builder_view())

def system_monitor_page() -> rx.Component:
    """System Monitor page."""
    return page_layout(system_monitor_view())

def agent_factory_page() -> rx.Component:
    """Agent Factory page."""
    return page_layout(agent_factory_view())

def direct_search_page() -> rx.Component:
    """Direct Search page."""
    return page_layout(direct_search_view())


app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="medium",
        accent_color="indigo",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)

# Health Check API Route
async def get_health(request=None):
    """Returns the health status of the application (Starlette compatible)."""
    import psutil
    import os
    
    # Check DB (basic check)
    db_status = "ok"
    try:
        from .state import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        
    return rx.responses.JSONResponse({
        "status": "ok" if "unhealthy" not in db_status else "error",
        "database": db_status,
        "ram_usage": f"{psutil.virtual_memory().percent}%",
        "cpu_usage": f"{psutil.cpu_percent()}%",
        "pid": os.getpid()
    })

# Register native Starlette route
app._api.add_route("/health", get_health, methods=["GET"])

# Register all routes
app.add_page(index, route="/", title="Dashboard - Smarketer Pro", on_load=State.on_load)
app.add_page(leads_page, route="/leads", title="Leads - Smarketer Pro", on_load=State.on_load)
app.add_page(campaigns_page, route="/campaigns", title="Campaigns - Smarketer Pro", on_load=State.on_load)
app.add_page(sequences_page, route="/sequences", title="Sequences - Smarketer Pro", on_load=State.on_load)
app.add_page(inbox_page, route="/inbox", title="Inbox - Smarketer Pro", on_load=State.on_load)
app.add_page(pipeline_page, route="/pipeline", title="Pipeline - Smarketer Pro", on_load=State.on_load)
app.add_page(tasks_page, route="/tasks", title="Tasks - Smarketer Pro", on_load=State.on_load)
app.add_page(analytics_page, route="/analytics", title="Analytics - Smarketer Pro", on_load=State.on_load)
app.add_page(settings_page, route="/settings", title="Settings - Smarketer Pro", on_load=State.on_load)
app.add_page(mass_tools_page, route="/mass-tools", title="Mass Tools - Smarketer Pro", on_load=State.on_load)
app.add_page(agent_lab_page, route="/agent-lab", title="Agent Lab - Smarketer Pro", on_load=State.on_load)
app.add_page(proxy_lab_page, route="/proxy-lab", title="Proxy Lab - Smarketer Pro", on_load=State.on_load)
app.add_page(automation_hub_page, route="/automation-hub", title="Automation Hub - Smarketer Pro", on_load=State.on_load)
app.add_page(workflow_builder_page, route="/workflow-builder", title="Workflow Builder - Smarketer Pro", on_load=State.on_load)
app.add_page(system_monitor_page, route="/system-monitor", title="System Monitor - Smarketer Pro", on_load=State.on_load)
app.add_page(agent_factory_page, route="/agent-factory", title="Agent Factory - Smarketer Pro", on_load=State.on_load)
app.add_page(direct_search_page, route="/direct-search", title="Direct Search - Smarketer Pro", on_load=State.on_load)
