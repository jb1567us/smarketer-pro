import reflex as rx
from ..states.outreach import AffiliateState
from ..styles import *

def partner_card(partner: dict):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.avatar(name=partner["name"], size="3"),
                rx.vstack(
                    rx.text(partner["name"], font_weight="bold"),
                    rx.text(partner["email"], font_size="0.8em", color="gray.500"),
                    align_items="start",
                    spacing="0",
                ),
                rx.spacer(),
                rx.badge(partner["status"], color_scheme="green" if partner["status"] == "active" else "amber"),
                width="100%",
                align_items="center",
            ),
            rx.divider(margin_y="3"),
            rx.grid(
                rx.vstack(rx.text("Clicks", font_size="0.7em", color="gray.500"), rx.text("124"), align_items="start"),
                rx.vstack(rx.text("Sales", font_size="0.7em", color="gray.500"), rx.text("12"), align_items="start"),
                rx.vstack(rx.text("Comm.", font_size="0.7em", color="gray.500"), rx.text("$450"), align_items="start"),
                columns="3",
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

def affiliate_hub_view():
    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading("🤝 Affiliate Hub", size="8", color="indigo.300"),
                rx.text("Manage your revenue streams and partner networks.", color="gray.400"),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.button(
                rx.hstack(rx.icon("user-plus"), rx.text("Add Partner")),
                variant="solid",
                color_scheme="indigo",
            ),
            width="100%",
            margin_bottom="6",
        ),

        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("My Vault", value="vault"),
                rx.tabs.trigger("Partner Center", value="partners"),
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.text("Personal Link Portfolio", font_size="1.2em", font_weight="bold", margin_top="4"),
                    rx.grid(
                        rx.foreach(
                            AffiliateState.my_links,
                            lambda link: rx.box(rx.text(link["cloaked_slug"]), padding="4", bg="slate.800", border_radius="md")
                        ),
                        columns="3",
                        spacing="4",
                        width="100%",
                    ),
                    rx.cond(
                        AffiliateState.my_links.length() == 0,
                        rx.center(
                            rx.vstack(
                                rx.icon("link-2", size=40, color="gray.600"),
                                rx.text("No affiliate links found", color="gray.500"),
                                spacing="2",
                            ),
                            height="300px",
                            width="100%",
                        ),
                    ),
                    spacing="4",
                ),
                value="vault",
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.text("Registered Affiliates & Influencers", font_size="1.2em", font_weight="bold", margin_top="4"),
                    rx.grid(
                        rx.foreach(AffiliateState.partners, partner_card),
                        columns="3",
                        spacing="4",
                        width="100%",
                    ),
                    rx.cond(
                        AffiliateState.partners.length() == 0,
                        rx.center(
                            rx.vstack(
                                rx.icon("users", size=40, color="gray.600"),
                                rx.text("No partners registered yet", color="gray.500"),
                                spacing="2",
                            ),
                            height="300px",
                            width="100%",
                        ),
                    ),
                    spacing="4",
                ),
                value="partners",
            ),
            default_value="vault",
            width="100%",
        ),
        width="100%",
        spacing="6",
    )
