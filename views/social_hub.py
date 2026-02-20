import reflex as rx
from ..states.outreach import SocialState
from ..styles import *

def platform_badge(platform: str):
    return rx.button(
        rx.hstack(
            rx.icon("check-circle", size=14) if SocialState.selected_platforms.contains(platform) else rx.icon("circle", size=14),
            rx.text(platform),
            spacing="2",
        ),
        on_click=lambda: SocialState.toggle_platform(platform),
        variant=rx.cond(SocialState.selected_platforms.contains(platform), "solid", "outline"),
        color_scheme=rx.cond(SocialState.selected_platforms.contains(platform), "indigo", "gray"),
        size="2",
        border_radius="full",
    )

def scheduled_post_card(post: dict):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.badge(post["status"], color_scheme="blue", variant="surface"),
                rx.spacer(),
                rx.text(f"Scheduled for: {rx.moment(post['scheduled_ts'] * 1000).format('LLL')}", font_size="0.8em", color="gray.400"),
                rx.button(
                    rx.icon("trash-2", size=14),
                    on_click=lambda: SocialState.delete_post(post["id"]),
                    variant="ghost",
                    color_scheme="red",
                    size="1",
                ),
                width="100%",
                align_items="center",
            ),
            rx.text(post["content"], font_size="0.95em", margin_top="2"),
            rx.hstack(
                rx.foreach(post["platforms"], lambda p: rx.badge(p, variant="outline", color_scheme="indigo")),
                margin_top="3",
                spacing="2",
            ),
            spacing="1",
            align_items="start",
        ),
        padding="4",
        border_radius="md",
        bg="slate.800/40",
        border="1px solid",
        border_color="slate.700/50",
        width="100%",
    )

def social_hub_view():
    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading("📱 Social Hub", size="8", color="indigo.300"),
                rx.text("Manage and schedule your multi-platform outreach content.", color="gray.400"),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(rx.icon("refresh-cw", size=16), rx.text("Sync Data")),
                on_click=SocialState.load_posts,
                variant="soft",
                color_scheme="indigo",
            ),
            width="100%",
            margin_bottom="6",
        ),

        rx.grid(
            # Left Column: Composer
            rx.vstack(
                rx.box(
                    rx.vstack(
                        rx.heading("Create Post", size="4", margin_bottom="4"),
                        rx.text_area(
                            placeholder="What's the update? Use #outreach #b2b",
                            value=SocialState.post_content,
                            on_change=SocialState.set_post_content,
                            height="200px",
                            width="100%",
                            variant="surface",
                        ),
                        rx.text("Select Platforms", font_size="0.8em", font_weight="bold", color="gray.500", margin_top="4"),
                        rx.hstack(
                            rx.foreach(SocialState.platforms, platform_badge),
                            wrap="wrap",
                            spacing="2",
                        ),
                        rx.grid(
                            rx.vstack(
                                rx.text("Date", font_size="0.8em", color="gray.500"),
                                rx.input(type="date", value=SocialState.scheduled_date, on_change=SocialState.set_scheduled_date, width="100%"),
                                align_items="start",
                            ),
                            rx.vstack(
                                rx.text("Time", font_size="0.8em", color="gray.500"),
                                rx.input(type="time", value=SocialState.scheduled_time, on_change=SocialState.set_scheduled_time, width="100%"),
                                align_items="start",
                            ),
                            columns="2",
                            spacing="4",
                            width="100%",
                            margin_top="4",
                        ),
                        rx.button(
                            rx.hstack(rx.icon("calendar-plus"), rx.text("Schedule Post")),
                            on_click=SocialState.schedule_post,
                            width="100%",
                            size="3",
                            margin_top="6",
                            color_scheme="indigo",
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
                ),
                width="100%",
            ),

            # Right Column: Queue
            rx.vstack(
                rx.heading("Upcoming Posts", size="4"),
                rx.cond(
                    SocialState.is_loading,
                    rx.center(rx.spinner(size="3"), width="100%", height="200px"),
                    rx.vstack(
                        rx.foreach(SocialState.scheduled_posts, scheduled_post_card),
                        rx.cond(
                            SocialState.scheduled_posts.length() == 0,
                            rx.center(
                                rx.vstack(
                                    rx.icon("calendar", size=40, color="gray.600"),
                                    rx.text("No posts scheduled", color="gray.500"),
                                    spacing="2",
                                ),
                                height="300px",
                                width="100%",
                            ),
                        ),
                        width="100%",
                        spacing="4",
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
