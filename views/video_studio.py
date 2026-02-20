import reflex as rx
from ..states.creative import CreativeState
from ..styles import *

def video_card(vid: dict):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("video", size=20, color="orange.400"),
                rx.text(vid.get("prompt")[:30] + "...", font_size="0.9em", font_weight="bold"),
                rx.spacer(),
                rx.badge(vid.get("status"), color_scheme="green" if vid.get("status") == "completed" else "orange"),
                width="100%",
                align_items="center",
            ),
            rx.cond(
                vid.get("url"),
                rx.box(
                    rx.video(src=vid.get("url"), width="100%", height="150px"),
                    border_radius="md",
                    overflow="hidden",
                    width="100%",
                ),
                rx.center(
                    rx.text("Rendering...", color="gray.500", font_size="0.8em"),
                    height="150px",
                    width="100%",
                    bg="slate.900/40",
                    border_radius="md",
                )
            ),
            rx.text(f"ID: {vid.get('job_id')}", font_size="0.7em", color="gray.600"),
            spacing="2",
        ),
        padding="4",
        bg="slate.800/40",
        border="1px solid",
        border_color="slate.700/50",
        border_radius="lg",
    )

def video_studio_view():
    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading("🎬 Video Studio", size="8", color="orange.300"),
                rx.text("Generate and record cinematic outreach content.", color="gray.400"),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            width="100%",
            margin_bottom="6",
        ),

        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("✨ AI Generator", value="gen"),
                rx.tabs.trigger("🎞️ Gallery", value="gal"),
            ),
            rx.tabs.content(
                rx.grid(
                    # Settings
                    rx.box(
                        rx.vstack(
                            rx.heading("Configuration", size="4"),
                            rx.text("Model Provider", font_size="0.8em", color="gray.500"),
                            rx.select(
                                ["OpenAI Sora", "Luma Dream Machine", "Runway Gen-3"],
                                default_value="OpenAI Sora",
                                width="100%",
                            ),
                            rx.text("Visual Style", font_size="0.8em", color="gray.500"),
                            rx.select(
                                ["Cinematic", "3D Animation", "Photorealistic", "Cyberpunk"],
                                value=CreativeState.video_style,
                                on_change=CreativeState.set_video_style,
                                width="100%",
                            ),
                            spacing="4",
                            align_items="start",
                        ),
                        padding="6",
                        bg="slate.900/60",
                        border="1px solid",
                        border_color="orange.500/20",
                        border_radius="xl",
                    ),
                    
                    # Prompt & Render
                    rx.vstack(
                        rx.heading("Prompt Engineering", size="4"),
                        rx.text_area(
                            placeholder="Describe your video idea...",
                            value=CreativeState.video_prompt,
                            on_change=CreativeState.set_video_prompt,
                            height="150px",
                            width="100%",
                            border_color="orange.500/20",
                        ),
                        rx.button(
                            rx.hstack(rx.icon("video"), rx.text("Generate Video")),
                            on_click=CreativeState.generate_video,
                            loading=CreativeState.is_generating_video,
                            width="100%",
                            size="3",
                            variant="solid",
                            color_scheme="orange",
                        ),
                        rx.cond(
                            CreativeState.last_video_job,
                            rx.box(
                                rx.vstack(
                                    rx.text("Active Job Triggered", weight="bold"),
                                    rx.text(f"Job ID: {CreativeState.last_video_job.get('job', {}).get('job_id')}", font_size="0.8em"),
                                    rx.progress(value=30, width="100%", color_scheme="orange"),
                                    align_items="start",
                                ),
                                padding="4",
                                bg="orange.900/20",
                                border="1px solid",
                                border_color="orange.500/30",
                                border_radius="md",
                                width="100%",
                                margin_top="4",
                            )
                        ),
                        width="100%",
                        align_items="start",
                    ),
                    columns="2",
                    spacing="8",
                    width="100%",
                    margin_top="6",
                ),
                value="gen",
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.heading("Video Library", size="4", margin_top="4"),
                    rx.grid(
                        rx.foreach(CreativeState.video_library, video_card),
                        columns="3",
                        spacing="4",
                        width="100%",
                    ),
                    width="100%",
                ),
                value="gal",
            ),
            default_value="gen",
            width="100%",
        ),
        width="100%",
        spacing="6",
    )
