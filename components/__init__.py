
import reflex as rx
from ..state import State

def log_console_component() -> rx.Component:
    """Floating log console component."""
    return rx.box(
        rx.cond(
            State.show_logs,
            rx.box(
                rx.hstack(
                    rx.text("System Logs", font_weight="bold", color="white"),
                    rx.spacer(),
                    rx.icon(tag="download", on_click=State.download_logs, cursor="pointer", color="white", margin_right="2"),
                    rx.icon(tag="copy", on_click=rx.set_clipboard(State.logs_text), cursor="pointer", color="white", margin_right="2"),
                    rx.icon(tag="trash-2", on_click=State.clear_logs, cursor="pointer", color="red.400", margin_right="2"),
                    rx.icon(tag="minus", on_click=State.toggle_logs, cursor="pointer", color="white"),
                    width="100%",
                    padding="2",
                    bg="gray.800",
                    border_bottom="1px solid gray",
                ),
                rx.vstack(
                    rx.foreach(
                        State.server_logs,
                        lambda log: rx.text(log, font_family="monospace", font_size="10px", color="green.200")
                    ),
                    spacing="0",
                    overflow_y="auto",
                    height="300px",
                    width="100%",
                    padding="2",
                    bg="black",
                    align_items="start",
                ),
                width="600px",
                border="1px solid #333",
                border_radius="md",
                box_shadow="lg",
                position="fixed",
                bottom="0",
                right="20px",
                z_index="9999",
            ),
            rx.button(
                "System Logs",
                on_click=State.toggle_logs,
                position="fixed",
                bottom="0",
                right="20px",
                z_index="9999",
                size="2",
                color_scheme="gray",
                border_top_radius="md",
                border_bottom_radius="0",
            ),
        )
    )
