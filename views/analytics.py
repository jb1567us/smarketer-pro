"""
Analytics View

Comprehensive analytics dashboard with charts and insights
"""
import reflex as rx
from ..states.analytics import AnalyticsState


def metric_card(icon: str, label: str, value: str, trend: Optional[str] = None, color: str = "blue") -> rx.Component:
    """Metric card component"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon(icon, size=20, color=f"{color}.400"),
                rx.spacer(),
                rx.cond(
                    trend,
                    rx.badge(trend, color_scheme="green" if "+" in trend else "red"),
                    rx.box()
                ),
                width="100%"
            ),
            rx.text(value, font_size="3xl", font_weight="bold", color="white"),
            rx.text(label, color="gray.400", font_size="sm"),
            spacing="2",
            align_items="start"
        ),
        bg="gray.800",
        padding="6",
        border_radius="lg",
        border="1px solid",
        border_color="gray.700",
        width="100%"
    )


def campaign_performance_table() -> rx.Component:
    """Campaign performance table"""
    return rx.box(
        rx.vstack(
            rx.heading("Campaign Performance", size="5", color="white"),
            
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Campaign"),
                        rx.table.column_header_cell("Leads"),
                        rx.table.column_header_cell("Sent"),
                        rx.table.column_header_cell("Open Rate"),
                        rx.table.column_header_cell("Response Rate"),
                        rx.table.column_header_cell("Status"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        AnalyticsState.campaign_metrics,
                        lambda campaign: rx.table.row(
                            rx.table.cell(campaign["name"]),
                            rx.table.cell(campaign["total_leads"]),
                            rx.table.cell(campaign["emails_sent"]),
                            rx.table.cell(
                                f"{campaign['open_rate']:.1f}%",
                                color="green.400" if campaign['open_rate'] > 40 else "white"
                            ),
                            rx.table.cell(
                                f"{campaign['response_rate']:.1f}%",
                                color="green.400" if campaign['response_rate'] > 5 else "white"
                            ),
                            rx.table.cell(
                                rx.badge(
                                    campaign["status"],
                                    color_scheme="green" if campaign["status"] == "active" else "gray"
                                )
                            ),
                        )
                    )
                ),
                variant="surface",
                size="3"
            ),
            
            spacing="4",
            width="100%"
        ),
        bg="gray.800",
        padding="6",
        border_radius="lg",
        border="1px solid",
        border_color="gray.700"
    )


def lead_distribution_charts() -> rx.Component:
    """Lead distribution pie charts"""
    return rx.hstack(
        # Status distribution
        rx.box(
            rx.vstack(
                rx.heading("Leads by Status", size="4", color="white"),
                rx.text(
                    "Distribution of lead statuses",
                    color="gray.400",
                    font_size="sm"
                ),
                # Placeholder for chart
                rx.box(
                    rx.foreach(
                        AnalyticsState.lead_status_distribution.items(),
                        lambda item: rx.hstack(
                            rx.box(
                                width="12px",
                                height="12px",
                                bg="blue.500",
                                border_radius="full"
                            ),
                            rx.text(item[0], color="white", font_size="sm"),
                            rx.spacer(),
                            rx.text(str(item[1]), color="gray.400", font_size="sm"),
                            width="100%"
                        )
                    ),
                    width="100%",
                    margin_top="4"
                ),
                spacing="3",
                align_items="start"
            ),
            bg="gray.800",
            padding="6",
            border_radius="lg",
            border="1px solid",
            border_color="gray.700",
            width="50%"
        ),
        
        # Source distribution
        rx.box(
            rx.vstack(
                rx.heading("Leads by Source", size="4", color="white"),
                rx.text(
                    "Where leads come from",
                    color="gray.400",
                    font_size="sm"
                ),
                # Placeholder for chart
                rx.box(
                    rx.foreach(
                        AnalyticsState.lead_source_distribution.items(),
                        lambda item: rx.hstack(
                            rx.box(
                                width="12px",
                                height="12px",
                                bg="purple.500",
                                border_radius="full"
                            ),
                            rx.text(item[0], color="white", font_size="sm"),
                            rx.spacer(),
                            rx.text(str(item[1]), color="gray.400", font_size="sm"),
                            width="100%"
                        )
                    ),
                    width="100%",
                    margin_top="4"
                ),
                spacing="3",
                align_items="start"
            ),
            bg="gray.800",
            padding="6",
            border_radius="lg",
            border="1px solid",
            border_color="gray.700",
            width="50%"
        ),
        
        spacing="4",
        width="100%"
    )


def cost_analytics() -> rx.Component:
    """LLM cost analytics"""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading("LLM Cost Analysis", size="5", color="white"),
                rx.spacer(),
                rx.vstack(
                    rx.text(
                        f"${AnalyticsState.total_llm_cost:.2f}",
                        font_size="2xl",
                        font_weight="bold",
                        color="white"
                    ),
                    rx.text(
                        "Total Spend",
                        color="gray.400",
                        font_size="xs"
                    ),
                    spacing="0",
                    align_items="end"
                ),
                width="100%"
            ),
            
            rx.divider(border_color="gray.700"),
            
            # Cost by provider
            rx.vstack(
                rx.foreach(
                    AnalyticsState.llm_cost_by_provider.items(),
                    lambda item: rx.hstack(
                        rx.text(item[0], color="white", font_weight="medium"),
                        rx.spacer(),
                        rx.text(
                            f"${item[1]:.2f}",
                            color="blue.400",
                            font_weight="bold"
                        ),
                        width="100%",
                        padding="2"
                    )
                ),
                width="100%"
            ),
            
            rx.divider(border_color="gray.700"),
            
            # Key metrics
            rx.grid(
                rx.vstack(
                    rx.text("Cost per Lead", color="gray.400", font_size="xs"),
                    rx.text(
                        f"${AnalyticsState.avg_cost_per_lead:.3f}",
                        color="white",
                        font_weight="bold"
                    ),
                    spacing="1"
                ),
                rx.vstack(
                    rx.text("Tokens Used", color="gray.400", font_size="xs"),
                    rx.text(
                        f"{AnalyticsState.llm_tokens_used:,}",
                        color="white",
                        font_weight="bold"
                    ),
                    spacing="1"
                ),
                rx.vstack(
                    rx.text("Est. ROI", color="gray.400", font_size="xs"),
                    rx.text(
                        f"{AnalyticsState.roi_estimate:.0f}%",
                        color="green.400" if AnalyticsState.roi_estimate > 0 else "red.400",
                        font_weight="bold"
                    ),
                    spacing="1"
                ),
                columns="3",
                spacing="4",
                width="100%"
            ),
            
            spacing="4",
            width="100%"
        ),
        bg="gray.800",
        padding="6",
        border_radius="lg",
        border="1px solid",
        border_color="gray.700"
    )


def export_buttons() -> rx.Component:
    """Export data buttons"""
    return rx.hstack(
        rx.button(
            rx.icon("download", margin_right="2"),
            "Export CSV",
            on_click=lambda: AnalyticsState.export_analytics_csv(),
            color_scheme="blue",
            variant="outline"
        ),
        rx.button(
            rx.icon("file-json", margin_right="2"),
            "Export JSON",
            on_click=lambda: AnalyticsState.export_analytics_json(),
            color_scheme="purple",
            variant="outline"
        ),
        spacing="3"
    )


def analytics_view() -> rx.Component:
    """Main analytics dashboard view"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading(
                    "📊 Analytics Dashboard",
                    size="8",
                    color="white"
                ),
                rx.spacer(),
                export_buttons(),
                width="100%",
                margin_bottom="6"
            ),
            
            # Load data button
            rx.button(
                rx.icon("refresh-cw", margin_right="2"),
                "Load Analytics",
                on_click=AnalyticsState.load_analytics,
                color_scheme="green",
                margin_bottom="6"
            ),
            
            # Overview metrics
            rx.grid(
                metric_card(
                    "target",
                    "Total Campaigns",
                    str(AnalyticsState.total_campaigns),
                    color="blue"
                ),
                metric_card(
                    "users",
                    "Total Leads",
                    str(AnalyticsState.total_leads),
                    color="purple"
                ),
                metric_card(
                    "mail",
                    "Emails Sent",
                    str(AnalyticsState.total_emails_sent),
                    color="green"
                ),
                metric_card(
                    "trending-up",
                    "Avg Response Rate",
                    f"{AnalyticsState.avg_response_rate:.1f}%",
                    trend="+2.3%",
                    color="orange"
                ),
                columns="4",
                spacing="4",
                width="100%",
                margin_bottom="6"
            ),
            
            # Charts row
            rx.hstack(
                cost_analytics(),
                rx.box(
                    rx.vstack(
                        rx.heading("Email Performance", size="5", color="white"),
                        rx.grid(
                            rx.vstack(
                                rx.text(
                                    f"{AnalyticsState.email_open_rate * 100:.1f}%",
                                    font_size="2xl",
                                    font_weight="bold",
                                    color="white"
                                ),
                                rx.text("Open Rate", color="gray.400", font_size="sm"),
                                spacing="1"
                            ),
                            rx.vstack(
                                rx.text(
                                    f"{AnalyticsState.email_click_rate * 100:.1f}%",
                                    font_size="2xl",
                                    font_weight="bold",
                                    color="white"
                                ),
                                rx.text("Click Rate", color="gray.400", font_size="sm"),
                                spacing="1"
                            ),
                            rx.vstack(
                                rx.text(
                                    f"{AnalyticsState.email_response_rate * 100:.1f}%",
                                    font_size="2xl",
                                    font_weight="bold",
                                    color="white"
                                ),
                                rx.text("Response Rate", color="gray.400", font_size="sm"),
                                spacing="1"
                            ),
                            columns="3",
                            spacing="6",
                            width="100%",
                            margin_top="4"
                        ),
                        spacing="4",
                        align_items="start"
                    ),
                    bg="gray.800",
                    padding="6",
                    border_radius="lg",
                    border="1px solid",
                    border_color="gray.700",
                    width="50%"
                ),
                spacing="4",
                width="100%",
                margin_bottom="6"
            ),
            
            # Distribution charts
            lead_distribution_charts(),
            
            # Campaign performance table
            campaign_performance_table(),
            
            width="100%",
            spacing="6"
        ),
        padding="8",
        bg="gray.900",
        min_height="100vh"
    )
