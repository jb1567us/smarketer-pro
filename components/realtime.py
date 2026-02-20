"""
Real-time UI Components

Toast notifications, progress bars, and live indicators
"""
import reflex as rx
from ..states.realtime import RealtimeState


def toast_notification(notification: Dict) -> rx.Component:
    """Individual toast notification"""
    type_colors = {
        "info": "blue",
        "success": "green",
        "warning": "yellow",
        "error": "red"
    }
    
    type_icons = {
        "info": "info",
        "success": "check-circle",
        "warning": "alert-triangle",
        "error": "x-circle"
    }
    
    color = type_colors.get(notification["type"], "gray")
    icon = type_icons.get(notification["type"], "bell")
    
    return rx.box(
        rx.hstack(
            rx.icon(icon, size=20, color=f"{color}.500"),
            rx.vstack(
                rx.text(
                    notification["title"],
                    font_weight="bold",
                    color="white",
                    font_size="sm"
                ),
                rx.text(
                    notification["message"],
                    color="gray.300",
                    font_size="xs"
                ),
                spacing="1",
                align_items="start"
            ),
            rx.spacer(),
            rx.button(
                rx.icon("x", size=16),
                on_click=lambda: RealtimeState.mark_notification_read(
                    notification["id"]
                ),
                variant="ghost",
                size="sm",
                color_scheme="gray"
            ),
            spacing="3",
            align_items="start"
        ),
        bg=f"{color}.900",
        border_left=f"4px solid",
        border_color=f"{color}.500",
        padding="3",
        border_radius="md",
        margin_bottom="2",
        width="100%",
        max_width="400px"
    )


def notification_center() -> rx.Component:
    """Notification center dropdown"""
    return rx.box(
        rx.button(
            rx.icon("bell", size=20),
            rx.cond(
                RealtimeState.unread_count > 0,
                rx.badge(
                    RealtimeState.unread_count,
                    color_scheme="red",
                    position="absolute",
                    top="-1",
                    right="-1"
                ),
                rx.box()
            ),
            variant="ghost",
            color_scheme="gray",
            position="relative"
        ),
        
        # Dropdown (would need proper modal/popover in real implementation)
        position="relative"
    )


def live_progress_bar(operation_id: str, operation: Dict) -> rx.Component:
    """Live progress bar for an operation"""
    progress_percent = (
        operation["progress"] / operation["total"] * 100
        if operation["total"] > 0 else 0
    )
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(
                    operation["type"],
                    font_weight="bold",
                    color="white",
                    font_size="sm"
                ),
                rx.spacer(),
                rx.text(
                    f"{operation['progress']}/{operation['total']}",
                    color="gray.400",
                    font_size="xs"
                ),
                width="100%"
            ),
            rx.progress(
                value=progress_percent,
                width="100%",
                height="6px",
                color_scheme="blue"
            ),
            rx.text(
                operation.get("status", "Processing..."),
                color="gray.400",
                font_size="xs"
            ),
            spacing="2",
            width="100%"
        ),
        bg="gray.800",
        padding="3",
        border_radius="md",
        border="1px solid",
        border_color="gray.700",
        margin_bottom="2"
    )


def active_operations_panel() -> rx.Component:
    """Panel showing all active operations"""
    return rx.cond(
        RealtimeState.has_active_operations,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("activity", size=16, color="blue.400"),
                    rx.text(
                        "Active Operations",
                        font_weight="bold",
                        color="white",
                        font_size="sm"
                    ),
                    rx.badge(
                        RealtimeState.active_operation_count,
                        color_scheme="blue"
                    ),
                    spacing="2"
                ),
                rx.foreach(
                    RealtimeState.active_operations,
                    lambda item: live_progress_bar(item[0], item[1])
                ),
                spacing="3",
                width="100%"
            ),
            bg="gray.900",
            padding="4",
            border_radius="lg",
            border="1px solid",
            border_color="gray.700",
            margin_bottom="4"
        ),
        rx.box()
    )


def live_stat_card(icon: str, label: str, value: str, color: str = "blue") -> rx.Component:
    """Live updating stat card"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=24, color=f"{color}.400"),
                rx.text(value, font_size="2xl", font_weight="bold", color="white"),
                spacing="2"
            ),
            rx.text(label, color="gray.400", font_size="sm"),
            rx.hstack(
                rx.icon("activity", size=12, color="green.400"),
                rx.text("Live", color="green.400", font_size="xs"),
                spacing="1"
            ),
            spacing="2",
            align_items="start"
        ),
        bg="gray.800",
        padding="4",
        border_radius="lg",
        border="1px solid",
        border_color="gray.700",
        width="100%"
    )


def live_dashboard_stats() -> rx.Component:
    """Live dashboard statistics"""
    return rx.vstack(
        rx.hstack(
            rx.text(
                "Live Dashboard",
                font_size="xl",
                font_weight="bold",
                color="white"
            ),
            rx.spacer(),
            rx.hstack(
                rx.icon(
                    "wifi" if RealtimeState.is_connected else "wifi-off",
                    size=16,
                    color="green.400" if RealtimeState.is_connected else "red.400"
                ),
                rx.text(
                    f"Updated: {RealtimeState.last_update}",
                    color="gray.400",
                    font_size="xs"
                ),
                spacing="2"
            ),
            width="100%"
        ),
        
        rx.grid(
            live_stat_card(
                "target",
                "Total Campaigns",
                RealtimeState.live_campaign_count,
                "blue"
            ),
            live_stat_card(
                "users",
                "Total Leads",
                RealtimeState.live_lead_count,
                "purple"
            ),
            live_stat_card(
                "loader",
                "Processing",
                RealtimeState.live_processing_count,
                "orange"
            ),
            columns="3",
            spacing="4",
            width="100%"
        ),
        
        spacing="4",
        width="100%"
    )


def realtime_demo_controls() -> rx.Component:
    """Demo controls to trigger realtime events"""
    return rx.box(
        rx.vstack(
            rx.heading("Realtime Demo Controls", size="5", color="white"),
            rx.text(
                "Trigger events to see real-time updates",
                color="gray.400",
                margin_bottom="4"
            ),
            
            rx.hstack(
                rx.button(
                    "Simulate Enrichment",
                    on_click=lambda: simulate_lead_enrichment(RealtimeState),
                    color_scheme="blue"
                ),
                rx.button(
                    "Launch Campaign",
                    on_click=lambda: simulate_campaign_launch(RealtimeState),
                    color_scheme="green"
                ),
                rx.button(
                    "Send Notification",
                    on_click=lambda: RealtimeState.add_notification(
                        "Test Notification",
                        "This is a test notification",
                        type="info"
                    ),
                    color_scheme="purple"
                ),
                spacing="3"
            ),
            
            spacing="3",
            width="100%"
        ),
        bg="gray.800",
        padding="4",
        border_radius="lg",
        margin_top="6"
    )
