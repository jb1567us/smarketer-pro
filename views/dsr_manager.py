import reflex as rx
from ..states.outreach import DSRState
from ..styles import *

def dsr_card(dsr: dict):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(dsr["title"], font_weight="bold"),
                rx.spacer(),
                rx.badge(dsr["status"], color_scheme="blue" if dsr["status"] == "draft" else "green"),
                width="100%",
                align_items="center",
            ),
            rx.text(f"Created: {rx.moment(dsr['created_at'] * 1000).from_now()}", font_size="0.8em", color="gray.500"),
            rx.divider(margin_y="2"),
            rx.hstack(
                rx.button(rx.icon("eye"), variant="ghost", size="2"),
                rx.button(rx.icon("share-2"), variant="ghost", size="2"),
                rx.spacer(),
                rx.button("Deploy", variant="soft", color_scheme="indigo", size="2"),
                width="100%",
            ),
            spacing="1",
        ),
        padding="4",
        border_radius="md",
        bg="slate.800/40",
        border="1px solid",
        border_color="slate.700/50",
    )

def dsr_manager_view():
    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading("🏛️ DSR Manager", size="8", color="indigo.300"),
                rx.text("Personalized Digital Sales Rooms for high-value closing.", color="gray.400"),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(rx.icon("sparkles"), rx.text("New Room")),
                variant="solid",
                color_scheme="indigo",
            ),
            width="100%",
            margin_bottom="6",
        ),

        rx.grid(
            # Generator Tool
            rx.box(
                rx.vstack(
                    rx.heading("DSR Content Engine", size="4", margin_bottom="4"),
                    rx.text("Target dynamic microsites to specific leads to drastically increase engagement.", color="gray.400", font_size="0.9em"),
                    
                    rx.button(
                        rx.hstack(rx.icon("zap"), rx.text("Generate Room Content")),
                        on_click=lambda: DSRState.generate_dsr(1, 1), # Demo IDs
                        width="100%",
                        size="3",
                        margin_top="4",
                        color_scheme="indigo",
                        loading=DSRState.is_generating,
                    ),
                    spacing="3",
                    align_items="start",
                ),
                padding="6",
                border_radius="xl",
                bg="slate.900/60",
                border="1px solid",
                border_color="indigo.500/20",
                backdrop_filter="blur(10px)",
                height="fit-content",
            ),

            # Management
            rx.vstack(
                rx.heading("Personalized Rooms", size="4"),
                rx.foreach(DSRState.dsrs, dsr_card),
                rx.cond(
                    DSRState.dsrs.length() == 0,
                    rx.center(
                        rx.vstack(
                            rx.icon("layout", size=40, color="gray.600"),
                            rx.text("No rooms generated yet", color="gray.500"),
                            spacing="2",
                        ),
                        height="300px",
                        width="100%",
                    ),
                ),
                width="100%",
                align_items="start",
            ),
            columns="2",
            spacing="8",
            width="100%",
        ),
        width="100%",
        spacing="6",
    )
