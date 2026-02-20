import reflex as rx
from ..states.creative import CreativeState
from ..styles import *

def asset_card(asset: dict):
    return rx.box(
        rx.vstack(
            rx.image(src=asset.get("content_url"), width="100%", border_radius="md"),
            rx.text(asset.get("title"), font_size="0.8em", font_weight="bold", limit=1),
            rx.hstack(
                rx.badge("Image", color_scheme="blue"),
                rx.spacer(),
                rx.icon("reuse", size=16),
                width="100%",
                align_items="center",
            ),
            spacing="2",
        ),
        padding="3",
        bg="slate.800/40",
        border="1px solid",
        border_color="slate.700/50",
        border_radius="lg",
    )

def creative_designer_view():
    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading("🎨 Creative Designer", size="8", color="pink.300"),
                rx.text("AI-driven visual asset generation for campaigns.", color="gray.400"),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            width="100%",
            margin_bottom="6",
        ),

        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("🚀 Generate Assets", value="gen"),
                rx.tabs.trigger("📚 Creative Library", value="lib"),
            ),
            rx.tabs.content(
                rx.grid(
                    # Left: Composer
                    rx.box(
                        rx.vstack(
                            rx.heading("Visual Concept", size="4"),
                            rx.text_area(
                                placeholder="Describe the image you need...",
                                value=CreativeState.concept,
                                on_change=CreativeState.set_concept,
                                height="150px",
                                width="100%",
                                border_color="pink.500/20",
                            ),
                            rx.grid(
                                rx.vstack(
                                    rx.text("Style Preset", font_size="0.8em", color="gray.500"),
                                    rx.select(
                                        ["Modern Corporate Memphis", "Iso-Tech Gradient", "Photorealistic", "Minimalist Vector"],
                                        value=CreativeState.style,
                                        on_change=CreativeState.set_style,
                                        width="100%",
                                    ),
                                    align_items="start",
                                ),
                                rx.vstack(
                                    rx.text("Aspect Ratio", font_size="0.8em", color="gray.500"),
                                    rx.select(
                                        ["16:9 (Blog Header)", "1:1 (Social Post)", "9:16 (Story/Shorts)"],
                                        value=CreativeState.aspect_ratio,
                                        on_change=CreativeState.set_aspect_ratio,
                                        width="100%",
                                    ),
                                    align_items="start",
                                ),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            rx.button(
                                rx.hstack(rx.icon("sparkles"), rx.text("Generate AI Visual")),
                                on_click=CreativeState.generate_image,
                                loading=CreativeState.is_generating_image,
                                width="100%",
                                size="3",
                                variant="solid",
                                color_scheme="pink",
                            ),
                            spacing="4",
                            align_items="start",
                        ),
                        padding="6",
                        bg="slate.900/60",
                        border="1px solid",
                        border_color="pink.500/20",
                        border_radius="xl",
                        backdrop_filter="blur(10px)",
                    ),
                    
                    # Right: Preview
                    rx.vstack(
                        rx.heading("👁️ Design Preview", size="4"),
                        rx.cond(
                            CreativeState.last_design,
                            rx.vstack(
                                rx.image(src=CreativeState.last_design["image_url"], border_radius="lg", width="100%"),
                                rx.box(
                                    rx.text(CreativeState.last_design["revised_prompt"], font_size="0.8em", italic=True, color="gray.500"),
                                    padding="3",
                                    bg="slate.800/50",
                                    border_radius="md",
                                    width="100%",
                                ),
                                width="100%",
                            ),
                            rx.center(
                                rx.text("Generate something to see preview", color="gray.600"),
                                height="300px",
                                width="100%",
                                border="2px dashed",
                                border_color="slate.700",
                                border_radius="lg",
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
                    rx.heading("Creative Archives", size="4", margin_top="4"),
                    rx.grid(
                        rx.foreach(CreativeState.image_library, asset_card),
                        columns="4",
                        spacing="4",
                        width="100%",
                    ),
                    width="100%",
                ),
                value="lib",
            ),
            default_value="gen",
            width="100%",
        ),
        width="100%",
        spacing="6",
    )
