import reflex as rx
from ..styles import *
from ..states.leads import LeadState
from ..states.campaigns import CampaignState
from ..states.agents import AgentState
from ..states.system import SystemState
from ..states.nav import NavState
from ..states.tools import ToolsState
from ..states.inbox import InboxState
from ..states.llm import LLMState
from ..states.portfolio import PortfolioState
from ..states.base import BaseState
from .settings import settings_view as settings_view_new

# This module contains all the view components for the B2B Outreach Tool.
# It is imported by the main b2b_outreach_proto.py file.

def dashboard_view():
    return rx.vstack(
        rx.heading("📍 Dashboard", size="8", margin_bottom="2", color="white"),
        rx.text("Welcome back! Here's what's happening in your workspace today.", color="gray.400", margin_bottom="6"),
        
        # Stats Grid
        rx.grid(
            rx.vstack(
                rx.text("Total Leads", font_size="0.9em", color="gray.400"),
                rx.text(LeadState.total_leads, font_size="2em", font_weight="bold", color="indigo.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Active Campaigns", font_size="0.9em", color="gray.400"),
                rx.text(CampaignState.active_campaigns_count, font_size="2em", font_weight="bold", color="green.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Avg Success Rate", font_size="0.9em", color="gray.400"),
                rx.text(CampaignState.success_rate, font_size="2em", font_weight="bold", color="blue.400"),
                class_name=CARD_STYLE,
            ),
            columns="3",
            spacing="4",
            width="100%",
            margin_bottom="6",
        ),
        
        # Quick Actions
        rx.vstack(
            rx.heading("Quick Actions", size="5", color="white", margin_bottom="4"),
            rx.grid(
                rx.button(
                    rx.hstack(rx.icon("plus"), rx.text("New Campaign"), spacing="2"),
                    class_name=PRIMARY_BUTTON_STYLE,
                    width="100%",
                    on_click=rx.redirect("/campaigns"),
                ),
                rx.button(
                    rx.hstack(rx.icon("search"), rx.text("Find Leads"), spacing="2"),
                    variant="outline",
                    width="100%",
                    on_click=rx.redirect("/leads"),
                ),
                rx.button(
                    rx.hstack(rx.icon("mail"), rx.text("Check Inbox"), spacing="2"),
                    variant="outline",
                    width="100%",
                    on_click=rx.redirect("/inbox"),
                ),
                columns="3",
                spacing="4",
                width="100%",
            ),
            align_items="start",
            width="100%",
            margin_bottom="10",
        ),
        
        # Performance Chart Placeholder
        rx.box(
            rx.vstack(
                rx.heading("Performance Forecast", size="5", color="white", margin_bottom="4"),
                rx.box(
                    rx.center(
                        rx.text("Chart visualization will appear here once campaigns are launched.", color="gray.500"),
                        height="200px",
                    ),
                    width="100%",
                    bg="slate.900/50",
                    border_radius="lg",
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
        ),
        width="100%",
    )

def leads_view():
    return rx.vstack(
        rx.heading("📍 Leads", size="8", margin_bottom="2", color="white"),
        rx.text("Manage your sales pipeline and prospect relationships.", color="gray.400", margin_bottom="4"),
        
        rx.cond(
            LeadState.leads_loaded,
            rx.vstack(
                rx.hstack(
                    rx.text("Total: ", LeadState.leads.length(), " leads", color="gray.400"),
                    rx.spacer(),
                    rx.button(
                        rx.hstack(rx.icon("download"), rx.text("Export CSV"), spacing="2"),
                        on_click=LeadState.export_leads_csv,
                        variant="outline",
                        size="2",
                    ),
                    rx.button(
                        rx.hstack(rx.icon("file-spreadsheet"), rx.text("Export Excel"), spacing="2"),
                        on_click=LeadState.export_leads_excel,
                        variant="outline",
                        size="2",
                    ),
                    width="100%",
                    margin_bottom="4",
                ),
                # Filter Bar
                rx.hstack(
                    rx.input(
                        placeholder="Search leads...",
                        on_change=LeadState.set_lead_search_query,
                        width="300px",
                        value=LeadState.lead_search_query,
                    ),
                    rx.select(
                        ["All", "New", "Qualified", "Closed"],
                        value=LeadState.lead_status_filter,
                        on_change=LeadState.set_lead_status_filter,
                        width="150px",
                    ),
                    rx.spacer(),
                    width="100%",
                    margin_bottom="4",
                ),
                rx.cond(
                    LeadState.leads.length() > 0,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Email"),
                                rx.table.column_header_cell("Company"),
                                rx.table.column_header_cell("Source"),
                                rx.table.column_header_cell("Status"),
                                rx.table.column_header_cell("Actions"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                LeadState.leads,
                                lambda lead: rx.table.row(
                                    rx.table.cell(lead.email),
                                    rx.table.cell(lead.company_name),
                                    rx.table.cell(lead.source),
                                    rx.table.cell(lead.status),
                                    rx.table.cell(
                                        rx.button(
                                            rx.icon("trash-2", size=16),
                                            size="1",
                                            variant="ghost",
                                            color_scheme="red",
                                            on_click=lambda: LeadState.delete_lead(lead.id),
                                            title="Delete Lead"
                                        )
                                    ),
                                ),
                            ),
                        ),
                        width="100%",
                    ),
                    rx.text("No leads found. Import CSV or add leads manually.", color="gray.500"),
                ),

                # Detail Modal
                rx.dialog.root(
                    rx.dialog.content(
                        rx.cond(
                            LeadState.selected_lead,
                            rx.vstack(
                                rx.dialog.title(rx.cond(LeadState.selected_lead.company_name, LeadState.selected_lead.company_name, "Lead Details")),
                                rx.dialog.description("Deep dive into prospect data."),
                                rx.grid(
                                    rx.vstack(rx.text("Email", font_weight="bold", color="gray.400"), rx.text(LeadState.selected_lead.email)),
                                    rx.vstack(rx.text("Contact", font_weight="bold", color="gray.400"), rx.text(rx.cond(LeadState.selected_lead.contact_person, LeadState.selected_lead.contact_person, "N/A"))),
                                    rx.vstack(rx.text("Tech Stack", font_weight="bold", color="gray.400"), rx.text(rx.cond(LeadState.selected_lead.tech_stack, LeadState.selected_lead.tech_stack, "Unknown"))),
                                    rx.vstack(rx.text("Signals", font_weight="bold", color="gray.400"), rx.text(rx.cond(LeadState.selected_lead.intent_signals, LeadState.selected_lead.intent_signals, "None"))),
                                    columns="2", spacing="4", width="100%"
                                ),
                                rx.text_area(value=rx.cond(LeadState.selected_lead.notes, LeadState.selected_lead.notes, ""), placeholder="Notes...", height="100px", width="100%", disabled=True),
                                rx.hstack(
                                    rx.button("Close", on_click=LeadState.close_detail),
                                    width="100%", justify_content="end"
                                ),
                                spacing="4",
                            ),
                            rx.text("No lead selected.")
                        ),
                    ),
                    open=LeadState.is_detail_open,
                    on_open_change=LeadState.close_detail,
                ),
            ),
            rx.text("Loading leads...", color="gray.500"),
        ),
        width="100%",
    )

def campaigns_view():
    return rx.vstack(
        rx.heading("📍 Campaigns", size="8", margin_bottom="2", color="white"),
        rx.text("Create personalized email sequences using AI research.", color="gray.400", margin_bottom="6"),
        
        # Campaign Stats
        rx.grid(
            rx.vstack(
                rx.hstack(
                    rx.text("📁", font_size="1.5em"),
                    rx.text("Total Campaigns", font_size="0.9em", color="gray.400", font_weight="bold"),
                    spacing="2",
                ),
                rx.text(CampaignState.campaigns.length(), font_size="2em", font_weight="bold", color="white"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.hstack(
                    rx.text("🚀", font_size="1.5em"),
                    rx.text("Active", font_size="0.9em", color="gray.400", font_weight="bold"),
                    spacing="2",
                ),
                rx.text(CampaignState.active_campaigns_count, font_size="2em", font_weight="bold", color="indigo.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.hstack(
                    rx.text("📧", font_size="1.5em"),
                    rx.text("Emails Sent", font_size="0.9em", color="gray.400", font_weight="bold"),
                    spacing="2",
                ),
                rx.text("0", font_size="2em", font_weight="bold", color="green.400"),
                class_name=CARD_STYLE,
            ),
            columns="3",
            spacing="4",
            width="100%",
            margin_bottom="6",
        ),
        
        # Create New Campaign Section
        rx.box(
            rx.vstack(
                rx.heading("✨ Start New Campaign", size="6", color="white", margin_bottom="4"),
                rx.vstack(
                    rx.input(
                        id="campaign-name-input",
                        name="campaign_name",
                        placeholder="Campaign Name (e.g., Q4 Outreach for Realtors)",
                        width="100%",
                        class_name=INPUT_STYLE,
                        value=CampaignState.new_campaign_name,
                        on_change=CampaignState.set_new_campaign_name,
                    ),
                    rx.input(
                        id="campaign-niche-input",
                        name="campaign_niche",
                        placeholder="Niche (e.g., Real Estate Agents in NYC)",
                        width="100%",
                        class_name=INPUT_STYLE,
                        value=CampaignState.new_campaign_niche,
                        on_change=CampaignState.set_new_campaign_niche,
                    ),
                    rx.input(
                        id="campaign-product-input",
                        name="campaign_product",
                        placeholder="Product Name (Optional)",
                        width="100%",
                        class_name=INPUT_STYLE,
                        value=CampaignState.new_campaign_product_name,
                        on_change=CampaignState.set_new_campaign_product_name,
                    ),
                    rx.text_area(
                        id="campaign-context-input",
                        name="campaign_context",
                        placeholder="Product Context (Optional - helps AI personalize messages)",
                        width="100%",
                        height="80px",
                        class_name=INPUT_STYLE,
                        value=CampaignState.new_campaign_product_context,
                        on_change=CampaignState.set_new_campaign_product_context,
                    ),
                    rx.cond(
                        CampaignState.campaign_creation_error != "",
                        rx.text(CampaignState.campaign_creation_error, color="red.400", font_size="0.9em"),
                    ),
                    rx.button(
                        rx.cond(
                            CampaignState.is_creating_campaign,
                            rx.hstack(rx.spinner(size="1"), rx.text("Creating..."), spacing="2"),
                            rx.hstack(rx.icon("plus"), rx.text("Create Campaign"), spacing="2"),
                        ),
                        size="3",
                        class_name=PRIMARY_BUTTON_STYLE,
                        on_click=CampaignState.create_new_campaign,
                        disabled=CampaignState.is_creating_campaign,
                        width="100%",
                    ),
                    width="100%",
                    spacing="3",
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
            margin_bottom="6",
        ),
        
        # Campaigns List
        rx.vstack(
            rx.heading("📁 Your Campaigns", size="6", color="white", margin_bottom="4"),
            rx.box(
                rx.cond(
                    CampaignState.campaigns.length() > 0,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Name"),
                                rx.table.column_header_cell("Niche"),
                                rx.table.column_header_cell("Status"),
                                rx.table.column_header_cell("Action"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                CampaignState.campaigns,
                                lambda campaign: rx.table.row(
                                    rx.table.cell(campaign["name"]),
                                    rx.table.cell(campaign["niche"]),
                                    rx.table.cell(rx.badge(campaign["status"], color_scheme=rx.cond(campaign["status"] == "active", "green", "gray"))),
                                    rx.table.cell(rx.button("Manage", size="1", variant="ghost", on_click=lambda: BaseState.handle_ui_action("Manage Campaign"))),
                                )
                            ),
                        ),
                        width="100%",
                    ),
                    rx.text(
                        "No campaigns yet. Create your first campaign above!",
                        color="gray.500",
                        text_align="center",
                        padding="8",
                    ),
                ),
                class_name=CARD_STYLE,
            ),
            width="100%",
        ),
        
        width="100%",
    )

def sequences_view():
    return rx.vstack(
        rx.heading("📍 Sequences", size="8", margin_bottom="2", color="white"),
        rx.text("Build automated email sequences.", color="gray.400", margin_bottom="6"),
        
        rx.box(
            rx.vstack(
                rx.text(
                    "Email sequences are managed within Campaigns.",
                    color="gray.400",
                    text_align="center",
                    margin_bottom="4",
                ),
                rx.text(
                    "Go to Campaigns → Select a campaign → Sequence tab to create and manage email sequences.",
                    color="gray.500",
                    text_align="center",
                    font_size="0.9em",
                ),
                rx.button(
                    rx.hstack(rx.icon("arrow-right"), rx.text("Go to Campaigns"), spacing="2"),
                    size="3",
                    class_name=PRIMARY_BUTTON_STYLE,
                    margin_top="6",
                    on_click=rx.redirect("/campaigns"),
                ),
                padding="12",
            ),
            class_name=CARD_STYLE,
        ),
        
        width="100%",
    )

def inbox_view():
    return rx.vstack(
        rx.heading("📍 Inbox", size="8", margin_bottom="2", color="white"),
        rx.text("Manage responses and conversations.", color="gray.400", margin_bottom="6"),
        
        rx.hstack(
            # Sidebar: Chat Sessions
            rx.vstack(
                rx.heading("Sessions", size="4", color="white", margin_bottom="2"),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(
                            InboxState.inbox_sessions,
                            lambda session: rx.button(
                                rx.hstack(
                                    rx.icon("message-square", size=16),
                                    rx.text(session["title"], overflow="hidden", text_overflow="ellipsis", white_space="nowrap"),
                                    width="100%",
                                    spacing="2",
                                ),
                                variant=rx.cond(InboxState.selected_session_id == session["id"], "solid", "ghost"),
                                width="100%",
                                justify_content="start",
                                on_click=lambda: InboxState.select_inbox_session(session["id"]),
                                padding="2",
                                border_radius="md",
                            )
                        ),
                        width="100%",
                        spacing="1",
                    ),
                    height="600px",
                    width="250px",
                ),
                padding="4",
                class_name=CARD_STYLE,
                height="100%",
                align_items="start",
            ),
            
            # Main: Messages
            rx.vstack(
                rx.cond(
                    InboxState.selected_session_id != 0,
                    rx.vstack(
                        rx.box(
                            rx.scroll_area(
                                rx.vstack(
                                    rx.foreach(
                                        InboxState.inbox_messages,
                                        lambda msg: rx.box(
                                            rx.text(msg["role"].upper(), font_weight="bold", font_size="0.7em", color="indigo.300", margin_bottom="1"),
                                            rx.text(msg["content"], color="gray.200"),
                                            bg=rx.cond(msg["role"] == "user", "slate.800/50", "indigo.900/30"),
                                            padding="3",
                                            border_radius="lg",
                                            margin_y="2",
                                            width="100%",
                                            align_self=rx.cond(msg["role"] == "user", "end", "start"),
                                            max_width="80%",
                                        )
                                    ),
                                    width="100%",
                                ),
                                height="500px",
                                width="100%",
                            ),
                            padding="4",
                            bg="slate.900/50",
                            border_radius="lg",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.input(
                                id="inbox-message-input",
                                name="inbox_message",
                                placeholder="Type a message...",
                                width="100%",
                                class_name=INPUT_STYLE,
                                value=InboxState.new_message_content,
                                on_change=InboxState.set_new_message_content,
                            ),
                            rx.button(
                                rx.cond(
                                    InboxState.is_sending_message,
                                    rx.spinner(size="1"),
                                    rx.icon("send")
                                ),
                                class_name=PRIMARY_BUTTON_STYLE,
                                on_click=InboxState.send_inbox_message,
                                disabled=InboxState.is_sending_message,
                            ),
                            width="100%",
                            spacing="3",
                        ),
                        width="100%",
                        spacing="4",
                    ),
                    rx.center(
                        rx.text("Select a session to view messages", color="gray.500"),
                        height="600px",
                        width="100%",
                    )
                ),
                flex="1",
                padding="4",
                class_name=CARD_STYLE,
                height="100%",
            ),
            width="100%",
            height="700px",
            spacing="4",
            align_items="stretch",
        ),
        
        width="100%",
    )

def pipeline_view():
    return rx.vstack(
        rx.heading("📍 Pipeline", size="8", margin_bottom="2", color="white"),
        rx.text("Track deals through your sales pipeline.", color="gray.400", margin_bottom="6"),
        
        # Pipeline Stages (Dynamic)
        rx.grid(
            rx.foreach(
                LeadState.pipeline_columns,
                lambda col: rx.vstack(
                    rx.heading(col["name"], size="4", color=f"{col['color']}.300", margin_bottom="3"),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text(f"{col['count']} Deals", color="white", font_weight="bold"),
                                rx.spacer(),
                                rx.text(f"${col['value']}", color="green.300", font_size="0.8em"),
                                width="100%",
                            ),
                            rx.text("View Details →", color="gray.500", font_size="0.8em", cursor="pointer"),
                            spacing="2",
                        ),
                        padding="4",
                        border_radius="md",
                        bg="slate.800",
                        border="1px solid",
                        border_color="slate.700",
                        width="100%",
                        _hover={"border_color": f"{col['color']}.500"},
                    ),
                    width="100%",
                ),
            ),
            columns="4",
            spacing="4",
            width="100%",
        ),
        
        # Create Deal Button
        rx.button(
            rx.hstack(rx.icon("plus"), rx.text("Create New Deal"), spacing="2"),
            size="3",
            class_name=PRIMARY_BUTTON_STYLE,
            margin_top="6",
            on_click=lambda: BaseState.handle_ui_action("Create New Deal"),
        ),
        
        width="100%",
    )

def tasks_view():
    return rx.vstack(
        rx.heading("📍 Tasks", size="8", margin_bottom="2", color="white"),
        rx.text("Manage your outreach tasks and follow-ups.", color="gray.400", margin_bottom="6"),
        
        # Task Stats
        rx.grid(
            rx.vstack(
                rx.text("Total Tasks", font_size="0.9em", color="gray.400"),
                rx.text("0", font_size="2em", font_weight="bold", color="white"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Pending", font_size="0.9em", color="gray.400"),
                rx.text("0", font_size="2em", font_weight="bold", color="orange.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Completed", font_size="0.9em", color="gray.400"),
                rx.text("0", font_size="2em", font_weight="bold", color="green.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Overdue", font_size="0.9em", color="gray.400"),
                rx.text("0", font_size="2em", font_weight="bold", color="red.400"),
                class_name=CARD_STYLE,
            ),
            columns="4",
            spacing="4",
            width="100%",
            margin_bottom="6",
        ),
        
        # Create Task Form
        rx.box(
            rx.vstack(
                rx.heading("➕ Create New Task", size="5", color="white", margin_bottom="4"),
                rx.grid(
                    rx.input(id="new-task-description", name="task_description", placeholder="Task Description", class_name=INPUT_STYLE),
                    rx.select(
                        ["Call", "Email", "Meeting", "Research", "Follow-up", "Task"],
                        placeholder="Type",
                        size="3",
                    ),
                    rx.select(
                        ["Low", "Medium", "High", "Urgent"],
                        placeholder="Priority",
                        size="3",
                    ),
                    rx.input(type="date", class_name=INPUT_STYLE),
                    columns="4",
                    spacing="3",
                    width="100%",
                ),
                rx.button(
                    rx.hstack(rx.icon("plus"), rx.text("Create Task"), spacing="2"),
                    size="3",
                    class_name=PRIMARY_BUTTON_STYLE,
                    margin_top="3",
                    on_click=lambda: BaseState.handle_ui_action("Create Task"),
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
            margin_bottom="6",
        ),
        
        # Tasks List
        rx.vstack(
            rx.heading("📋 Active Tasks", size="6", color="white", margin_bottom="4"),
            rx.box(
                rx.text(
                    "No active tasks. Time to relax! ☕",
                    color="gray.500",
                    text_align="center",
                    padding="8",
                ),
                class_name=CARD_STYLE,
            ),
            width="100%",
        ),
        
        width="100%",
    )

def analytics_view():
    return rx.vstack(
        rx.heading("📍 Analytics", size="8", margin_bottom="2", color="white"),
        rx.text("Performance metrics and insights.", color="gray.400", margin_bottom="6"),
        
        # Key Metrics
        rx.grid(
            rx.vstack(
                rx.text("Response Rate", font_size="0.9em", color="gray.400"),
                rx.text("0%", font_size="2em", font_weight="bold", color="indigo.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Conversion Rate", font_size="0.9em", color="gray.400"),
                rx.text("0%", font_size="2em", font_weight="bold", color="green.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Avg. Response Time", font_size="0.9em", color="gray.400"),
                rx.text("N/A", font_size="2em", font_weight="bold", color="blue.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Total Revenue", font_size="0.9em", color="gray.400"),
                rx.text("$0", font_size="2em", font_weight="bold", color="purple.400"),
                class_name=CARD_STYLE,
            ),
            columns="4",
            spacing="4",
            width="100%",
            margin_bottom="6",
        ),
        
        # Charts Placeholder
        rx.box(
            rx.vstack(
                rx.heading("📊 Performance Over Time", size="5", color="white", margin_bottom="4"),
                rx.text(
                    "Charts and graphs will appear here once you have campaign data.",
                    color="gray.500",
                    text_align="center",
                    padding="12",
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
        ),
        
        width="100%",
    )

def settings_view_legacy():
    """Legacy settings view - replaced by new production settings page"""
    return rx.vstack(
        rx.heading("📍 Settings", size="8", margin_bottom="2", color="white"),
        rx.text("Configure your workspace and integrations.", color="gray.400", margin_bottom="6"),
        
        # Settings Sections
        rx.vstack(
            # Email Configuration
            rx.box(
                rx.vstack(
                    rx.heading("📧 Email Configuration", size="5", color="white", margin_bottom="4"),
                    rx.grid(
                        rx.vstack(
                            rx.text("SMTP Server", font_size="0.9em", color="gray.400", margin_bottom="2"),
                            rx.input(id="settings-smtp-server", name="smtp_server", placeholder="smtp.gmail.com", class_name=INPUT_STYLE),
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Port", font_size="0.9em", color="gray.400", margin_bottom="2"),
                            rx.input(id="settings-smtp-port", name="smtp_port", placeholder="587", class_name=INPUT_STYLE),
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Email", font_size="0.9em", color="gray.400", margin_bottom="2"),
                            rx.input(id="settings-smtp-email", name="smtp_email", placeholder="your@email.com", class_name=INPUT_STYLE),
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Password", font_size="0.9em", color="gray.400", margin_bottom="2"),
                            rx.input(id="settings-smtp-password", name="smtp_password", type="password", placeholder="••••••••", class_name=INPUT_STYLE),
                            width="100%",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    rx.button(
                        rx.hstack(rx.icon("save"), rx.text("Save Email Settings"), spacing="2"),
                        size="3",
                        class_name=PRIMARY_BUTTON_STYLE,
                        margin_top="4",
                        on_click=lambda: BaseState.handle_ui_action("Save Email Settings"),
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
                margin_bottom="4",
            ),
            
            # API Keys
            rx.box(
                rx.vstack(
                    rx.heading("🔑 API Keys", size="5", color="white", margin_bottom="4"),
                    rx.vstack(
                        rx.text("OpenAI API Key", font_size="0.9em", color="gray.400", margin_bottom="2"),
                        rx.input(id="settings-openai-key", name="openai_key", type="password", placeholder="sk-...", class_name=INPUT_STYLE),
                        width="100%",
                    ),
                    rx.button(
                        rx.hstack(rx.icon("save"), rx.text("Save API Keys"), spacing="2"),
                        size="3",
                        class_name=PRIMARY_BUTTON_STYLE,
                        margin_top="4",
                        on_click=lambda: BaseState.handle_ui_action("Save API Keys"),
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
                margin_bottom="4",
            ),

            # UI & Accessibility Settings
            rx.box(
                rx.vstack(
                    rx.heading("🎨 UI & Accessibility", size="5", color="white", margin_bottom="4"),
                    rx.grid(
                        rx.vstack(
                            rx.text("Voice Synthesis", font_size="0.9em", color="gray.400"),
                            rx.hstack(
                                rx.text("Enabled", font_size="0.8em"),
                                rx.switch(is_checked=NavState.voice_enabled, on_change=NavState.set_voice_enabled),
                                spacing="2",
                            ),
                            align_items="start",
                        ),
                        rx.vstack(
                            rx.text("Default Sidebar Width", font_size="0.9em", color="gray.400"),
                            rx.button("Reset to Default (280px)", size="2", variant="soft", on_click=lambda: NavState.set_sidebar_width_px(280)),
                            align_items="start",
                        ),
                        rx.vstack(
                            rx.text("Speech Rate", font_size="0.9em", color="gray.400"),
                            rx.slider(value=[NavState.speech_rate], min=0.5, max=2.0, step=0.1, on_change=lambda v: NavState.set_speech_rate(v[0]), width="100%"),
                            align_items="start",
                        ),
                        rx.vstack(
                            rx.text("Speech Pitch", font_size="0.9em", color="gray.400"),
                            rx.slider(value=[NavState.speech_pitch], min=0.5, max=2.0, step=0.1, on_change=lambda v: NavState.set_speech_pitch(v[0]), width="100%"),
                            align_items="start",
                        ),
                        columns="2",
                        spacing="6",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Selected Voice", font_size="0.9em", color="gray.400"),
                            rx.spacer(),
                            rx.button(
                                rx.hstack(rx.icon("refresh-cw", size=14), rx.text("Refresh List", font_size="0.8em")),
                                variant="ghost",
                                size="1",
                                on_click=NavState.load_voices
                            ),
                            width="100%",
                            align_items="center",
                            margin_top="4"
                        ),
                        rx.select(
                            NavState.available_voices,
                            id="voice-select",
                            value=NavState.selected_voice,
                            on_change=NavState.set_selected_voice,
                            width="100%",
                        ),
                        width="100%",
                        align_items="start",
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
                margin_bottom="4",
            ),
            
            # Workspace Settings
            rx.box(
                rx.vstack(
                    rx.heading("⚙️ Workspace Settings", size="5", color="white", margin_bottom="4"),
                    rx.grid(
                        rx.vstack(
                            rx.text("Workspace Name", font_size="0.9em", color="gray.400", margin_bottom="2"),
                            rx.input(placeholder="My Workspace", class_name=INPUT_STYLE),
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Timezone", font_size="0.9em", color="gray.400", margin_bottom="2"),
                            rx.select(
                                ["UTC", "America/New_York", "America/Chicago", "America/Los_Angeles"],
                                placeholder="Select timezone",
                                size="3",
                            ),
                            width="100%",
                        ),
                        columns="2",
                        spacing="4",
                        width="100%",
                    ),
                    rx.button(
                        rx.hstack(rx.icon("save"), rx.text("Save Workspace Settings"), spacing="2"),
                        size="3",
                        class_name=PRIMARY_BUTTON_STYLE,
                        margin_top="4",
                        on_click=lambda: BaseState.handle_ui_action("Save Workspace Settings"),
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
            ),
            
            width="100%",
        ),
        
        width="100%",
    )

# Use new production settings view
settings_view = settings_view_new

def mass_tools_view():
    return rx.vstack(
        rx.heading("📍 Mass Power Tools", size="8", margin_bottom="2", color="white"),
        rx.text("ScrapeBox / SEnuke style bulk utilities for heavy lifting.", color="gray.400", margin_bottom="6"),
        
        # Tool Selector
        rx.box(
            rx.vstack(
                rx.heading("Select Tool", size="5", color="white", margin_bottom="4"),
                rx.grid(
                    rx.button(
                        rx.vstack(
                            rx.text("🔍", font_size="2em"),
                            rx.text("Mass Harvester", font_weight="bold"),
                            rx.text("Bulk lead discovery", font_size="0.8em", color="gray.400"),
                            spacing="2",
                        ),
                        on_click=lambda: ToolsState.set_tool("Mass Harvester"),
                        class_name=CARD_STYLE,
                        padding="6",
                        width="100%",
                    ),
                    rx.button(
                        rx.vstack(
                            rx.text("🐾", font_size="2em"),
                            rx.text("Footprint Scraper", font_weight="bold"),
                            rx.text("Find targets with search operators", font_size="0.8em", color="gray.400"),
                            spacing="2",
                        ),
                        on_click=lambda: ToolsState.set_tool("Footprint Scraper"),
                        class_name=CARD_STYLE,
                        padding="6",
                        width="100%",
                    ),
                    rx.button(
                        rx.vstack(
                            rx.text("💬", font_size="2em"),
                            rx.text("Mass Commenter", font_weight="bold"),
                            rx.text("Automated blog commenting", font_size="0.8em", color="gray.400"),
                            spacing="2",
                        ),
                        on_click=lambda: ToolsState.set_tool("Mass Commenter"),
                        class_name=CARD_STYLE,
                        padding="6",
                        width="100%",
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                rx.divider(margin_y="6"),
                rx.heading("Tool: ", ToolsState.tool_type, size="4", color="indigo.300", margin_bottom="4"),
                rx.match(
                    ToolsState.tool_type,
                    ("Mass Harvester", rx.vstack(
                        rx.text("Keywords (One per line)", font_size="0.9em", color="gray.400", margin_bottom="2"),
                        rx.text_area(
                            id="mass-harvester-keywords-input",
                            name="mass_keywords",
                            placeholder="marketing agencies nyc\nsoftware companies austin", 
                            width="100%", height="150px", 
                            class_name=INPUT_STYLE,
                            value=ToolsState.mass_tools_keywords,
                            on_change=lambda v: ToolsState.set_mass_tools_keywords(v),
                        ),
                        rx.hstack(
                            rx.text("Results per keyword:", color="gray.400"),
                            rx.input(
                                value=ToolsState.harvest_limit.to_string(),
                                on_change=ToolsState.set_harvest_limit,
                                width="80px",
                                type="number",
                                class_name=INPUT_STYLE,
                            ),
                            align_items="center",
                            margin_top="2",
                        ),
                        rx.button(
                            rx.cond(
                                ToolsState.is_harvesting,
                                rx.hstack(rx.spinner(size="1"), rx.text("Harvesting..."), spacing="2"),
                                rx.hstack(rx.icon("zap"), rx.text("Start Harvesting"), spacing="2"),
                            ),
                            class_name=PRIMARY_BUTTON_STYLE, 
                            margin_top="4",
                            on_click=lambda: ToolsState.run_mass_harvest(),
                            disabled=ToolsState.is_harvesting,
                        ),
                        rx.cond(
                            ToolsState.mass_harvest_results.length() > 0,
                            rx.box(
                                rx.text("Harvest Results Preview", font_weight="bold", color="white", margin_bottom="2"),
                                rx.table.root(
                                    rx.table.header(
                                        rx.table.row(
                                            rx.table.column_header_cell("Title"),
                                            rx.table.column_header_cell("Email"),
                                            rx.table.column_header_cell("URL"),
                                        ),
                                    ),
                                    rx.table.body(
                                        rx.foreach(
                                            ToolsState.mass_harvest_results,
                                            lambda res: rx.table.row(
                                                rx.table.cell(res["title"]),
                                                rx.table.cell(res["email"]),
                                                rx.table.cell(res["url"]),
                                            ),
                                        ),
                                    ),
                                    width="100%",
                                ),
                                max_height="300px",
                                overflow="auto",
                                margin_top="4",
                                padding="4",
                                bg="slate.900/50",
                                border_radius="md",
                            ),
                        ),
                        width="100%",
                    )),
                    ("Footprint Scraper", rx.vstack(
                        rx.text("Search Footprints (e.g. \"powered by vbulletin\")", font_size="0.9em", color="gray.400", margin_bottom="2"),
                        rx.text_area(
                            id="footprint-scraper-keywords-input",
                            name="footprint_keywords",
                            placeholder="\"guest book\" \"post comment\"\ninurl:/blog/ \"leave a comment\"", 
                            width="100%", height="150px", 
                            class_name=INPUT_STYLE,
                            value=ToolsState.footprint_keywords,
                            on_change=lambda v: ToolsState.set_footprint_keywords(v),
                        ),
                        rx.button(
                            rx.cond(
                                ToolsState.is_scraping_footprints,
                                rx.hstack(rx.spinner(size="1"), rx.text("Scraping..."), spacing="2"),
                                rx.hstack(rx.icon("search"), rx.text("Scrape Targets"), spacing="2"),
                            ),
                            class_name=PRIMARY_BUTTON_STYLE, 
                            margin_top="4", 
                            on_click=lambda: ToolsState.run_footprint_scrape(),
                            disabled=ToolsState.is_scraping_footprints,
                        ),
                        width="100%",
                    )),
                    ("Mass Commenter", rx.vstack(
                        rx.text("Comment Template", font_size="0.9em", color="gray.400", margin_bottom="2"),
                        rx.text_area(
                            id="mass-comment-template-input",
                            name="comment_template",
                            placeholder="Great post! Check out my site at {url}", 
                            width="100%", height="100px", 
                            class_name=INPUT_STYLE, 
                            margin_bottom="3",
                            value=ToolsState.comment_template,
                            on_change=ToolsState.set_comment_template,
                        ),
                        rx.text("Target URLs", font_size="0.9em", color="gray.400", margin_bottom="2"),
                        rx.text_area(
                            placeholder="http://example.com/blog1\nhttp://example.com/blog2", 
                            width="100%", height="100px", 
                            class_name=INPUT_STYLE,
                            value=ToolsState.comment_target_urls,
                            on_change=lambda v: ToolsState.set_comment_target_urls(v),
                        ),
                        rx.button(
                            rx.cond(
                                ToolsState.is_commenting,
                                rx.hstack(rx.spinner(size="1"), rx.text("Commenting..."), spacing="2"),
                                rx.hstack(rx.icon("message-square"), rx.text("Start Commenting"), spacing="2"),
                            ),
                            class_name=PRIMARY_BUTTON_STYLE, 
                            margin_top="4", 
                            on_click=lambda: ToolsState.run_mass_comment(),
                            disabled=ToolsState.is_commenting,
                        ),
                        width="100%",
                    )),
                    rx.text("Select a tool or section for common logic integration.", color="gray.500")
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
        ),
        width="100%",
    )

def morning_briefing_component():
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("sun", size=24, color="yellow.400"),
                rx.heading("Eugene's Morning Briefing", size="5", color="white"),
                spacing="3",
            ),
            rx.text("Ask Eugene to scan the news, analyze trends, and identify strategic opportunities.", color="gray.400"),
            
            rx.cond(
                AgentState.morning_briefing_content,
                rx.box(
                    rx.markdown(AgentState.morning_briefing_content),
                    padding="4",
                    bg="slate.900",
                    border="1px solid rgba(255,255,255,0.1)",
                    border_radius="md",
                    margin_y="4",
                    width="100%",
                ),
                rx.fragment(),
            ),

            rx.hstack(
                rx.button(
                    rx.cond(
                        AgentState.is_loading_briefing,
                        rx.hstack(rx.spinner(size="1"), rx.text("Scanning Global News..."), spacing="2"),
                        rx.hstack(rx.icon("sparkles"), rx.text("Generate Daily Briefing"), spacing="2"),
                    ),
                    on_click=AgentState.run_morning_briefing,
                    class_name=PRIMARY_BUTTON_STYLE,
                    disabled=AgentState.is_loading_briefing,
                ),
                rx.cond(
                    AgentState.morning_briefing_content,
                    rx.button(
                        rx.cond(
                            AgentState.is_generating_workflow,
                            rx.hstack(rx.spinner(size="1"), rx.text("Designing Strategy..."), spacing="2"),
                            rx.hstack(rx.icon("zap"), rx.text("Draft Workflow from Insights"), spacing="2"),
                        ),
                        on_click=AgentState.draft_strategic_workflow,
                        variant="outline",
                        color_scheme="yellow",
                        disabled=AgentState.is_generating_workflow,
                    ),
                    rx.fragment(),
                ),
                spacing="3",
                margin_top="2",
            ),
            width="100%",
            align_items="start",
        ),
        class_name=CARD_STYLE,
        margin_bottom="6",
        width="100%",
    )

def agent_lab_view():
    return rx.vstack(
        rx.heading("🧪 Strategy & Agent Lab", size="8", margin_bottom="2", color="white"),
        rx.text("Collaborate with Eugene (Manager) and specialized agents.", color="gray.400", margin_bottom="6"),
        
        morning_briefing_component(),
        
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Research & Leads", value="research"),
                rx.tabs.trigger("Marketing & Content", value="marketing"),
                rx.tabs.trigger("SEO & Growth", value="seo"),
                rx.tabs.trigger("System & Admin", value="system"),
                class_name="bg-slate-900/50 p-1 rounded-lg",
            ),
            rx.tabs.content(
                rx.grid(
                    agent_card("Researcher", "Deep web research and finding leads.", "Researcher"),
                    agent_card("Influencer Scout", "Identify and analyze social influencers.", "Influencer"),
                    agent_card("LinkedIn Specialist", "B2B networking and outreach.", "LinkedIn"),
                    columns="3", spacing="4", width="100%", padding_top="4"
                ),
                value="research",
            ),
            rx.tabs.content(
                rx.grid(
                    agent_card("Copywriter", "AI-powered conversion focused copy.", "Copywriter"),
                    agent_card("Graphics Designer", "Generate visual assets and UI mocks.", "Designer"),
                    agent_card("Video Director", "Script and produce video content.", "Video"),
                    columns="3", spacing="4", width="100%", padding_top="4"
                ),
                value="marketing",
            ),
            rx.tabs.content(
                rx.grid(
                    agent_card("SEO Expert", "Search engine optimization and audits.", "SEO"),
                    agent_card("WordPress Expert", "Website management and publishing.", "WordPress"),
                    agent_card("UX Designer", "User experience and interface optimization.", "UX"),
                    columns="3", spacing="4", width="100%", padding_top="4"
                ),
                value="seo",
            ),
            rx.tabs.content(
                rx.grid(
                    agent_card("Manager", "Mission oversight and strategy tuning.", "Manager"),
                    agent_card("Product Manager", "Product roadmapping and specs.", "PM"),
                    agent_card("Reviewer", "Quality assurance and content review.", "Reviewer"),
                    columns="3", spacing="4", width="100%", padding_top="4"
                ),
                value="system",
            ),
            default_value="research",
            width="100%",
        ),
        
        rx.divider(margin_y="8"),
        
        # Interaction Area
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.heading("🤖 ", AgentState.active_lab_agent, size="5", color="white"),
                    rx.spacer(),
                    rx.badge("Active", color_scheme="green"),
                ),
                
                # Dynamic Panel Selection
                rx.match(
                    AgentState.active_lab_agent,
                    ("Influencer Scout", influencer_scout_panel()),
                    ("Researcher", researcher_panel()),
                    generic_agent_panel(),
                ),

                rx.button(
                    rx.cond(
                        AgentState.is_agent_thinking,
                        rx.hstack(rx.spinner(size="1"), rx.text("Thinking..."), spacing="2"),
                        rx.hstack(rx.icon("play"), rx.text("Run "), rx.text(AgentState.active_lab_agent), spacing="2"),
                    ),
                    class_name=PRIMARY_BUTTON_STYLE,
                    margin_top="6",
                    on_click=AgentState.run_agent_task(AgentState.active_lab_agent, AgentState.lab_input),
                    disabled=AgentState.is_agent_thinking,
                    width="100%",
                ),
                rx.cond(
                    AgentState.last_lab_response != "",
                        rx.box(
                            rx.heading("Result", size="4", color="white", margin_bottom="2"),
                            
                            # Structured Data Table (if applicable)
                            rx.cond(
                                AgentState.is_response_json,
                                rx.box(
                                    rx.text("Structured Data Found", font_size="0.8em", color="green.400", margin_bottom="2"),
                                    rx.table.root(
                                        rx.table.header(
                                            rx.table.row(
                                                rx.table.column_header_cell("Handle"),
                                                rx.table.column_header_cell("Platform"),
                                                rx.table.column_header_cell("Followers"),
                                                rx.table.column_header_cell("Bio Snippet"),
                                                rx.table.column_header_cell("Action"),
                                            ),
                                        ),
                                        rx.table.body(
                                            rx.foreach(
                                                AgentState.results_list,  # Use typed computed var
                                                lambda item: rx.table.row(
                                                    rx.table.cell(item["handle"]),
                                                    rx.table.cell(item["platform"]),
                                                    rx.table.cell(item["estimated_followers"]),
                                                    rx.table.cell(item["bio_snippet"]),
                                                    rx.table.cell(
                                                        rx.link("Visit", href=item["url"], is_external=True, color="indigo.400")
                                                    ),
                                                )
                                            )
                                        ),
                                        width="100%",
                                        variant="surface",
                                    ),
                                    max_height="400px",
                                    overflow_y="auto",
                                    margin_bottom="4",
                                    border="1px solid rgba(255,255,255,0.1)",
                                    border_radius="md",
                                ),
                                rx.fragment(),
                            ),

                            rx.box(
                                rx.markdown(AgentState.last_lab_response, color="gray.300"),
                                padding="4",
                                bg="slate.800/40",
                                border_radius="md",
                                border="1px solid",
                                border_color="slate.700",
                                overflow_x="auto",
                            ),
                            
                            rx.divider(margin_y="4", opacity="0.3"),
                            rx.text("Refine Result", size="1", font_weight="bold", color="gray.500", margin_bottom="2", text_transform="uppercase"),
                            rx.hstack(
                                rx.input(
                                    placeholder="e.g. 'Make it more professional'...",
                                    value=AgentState.refinement_instruction,
                                    on_change=AgentState.set_refinement_instruction,
                                    width="100%",
                                    variant="surface"
                                ),
                                rx.button(
                                    rx.hstack(rx.icon("sparkles", size=16), rx.text("Refine")),
                                    on_click=AgentState.refine_agent_output,
                                    disabled=AgentState.is_agent_thinking,
                                    variant="soft",
                                    color_scheme="indigo"
                                ),
                                rx.button(
                                    rx.icon("volume-2", size=16),
                                    on_click=lambda: NavState.speak(AgentState.last_lab_response),
                                    variant="ghost",
                                    color_scheme="gray",
                                    title="Speak Response"
                                ),
                                rx.button(
                                    rx.icon("download", size=16),
                                    on_click=AgentState.download_last_lab_response,
                                    variant="ghost",
                                    color_scheme="gray",
                                    title="Save as JSON"
                                ),
                                rx.button(
                                    rx.hstack(rx.icon("square", size=14), rx.text("Stop Voice")),
                                    on_click=NavState.stop_speech,
                                    variant="soft",
                                    color_scheme="red",
                                    size="2",
                                ),
                                rx.cond(
                                    AgentState.is_response_json,
                                    rx.hstack(
                                        rx.button(
                                            rx.hstack(rx.icon("rocket", size=14), rx.text("Mission")),
                                            on_click=SystemState.launch_mission_from_response,
                                            variant="soft",
                                            color_scheme="green",
                                            size="2",
                                        ),
                                        rx.button(
                                            rx.hstack(rx.icon("file-code", size=14), rx.text("Workflow")),
                                            on_click=SystemState.draft_workflow_from_response,
                                            variant="soft",
                                            color_scheme="yellow",
                                            size="2",
                                        ),
                                        spacing="2",
                                    ),
                                    rx.fragment(),
                                ),
                                width="100%",
                                spacing="2"
                            ),
                            padding="4", bg="slate.900/80", border_radius="md", width="100%", margin_top="6",
                        ),
                    rx.fragment(),
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
            width="100%",
        ),
        width="100%",
    )

def influencer_scout_panel():
    return rx.vstack(
        rx.text("Target Platform", font_size="0.9em", color="gray.400", margin_top="4"),
        rx.select(
            ["instagram", "tiktok", "youtube", "linkedin", "twitter"],
            value=AgentState.agent_platform,
            on_change=AgentState.set_agent_platform,
            width="100%",
            size="3",
        ),
        rx.grid(
            rx.vstack(
                rx.text("Limit", font_size="0.9em", color="gray.400"),
                rx.hstack(
                    rx.slider(
                        min=1, max=2000,
                        value=[AgentState.agent_limit],
                        on_change=lambda v: AgentState.set_agent_limit(v[0]),
                        width="100%",
                    ),
                    rx.badge(AgentState.agent_limit, color_scheme="indigo"),
                    width="100%",
                ),
                width="100%",
            ),
            rx.vstack(
                rx.text("Min Followers (e.g. 10k)", font_size="0.9em", color="gray.400"),
                rx.input(
                    placeholder="10k", 
                    value=AgentState.agent_min_followers,
                    on_change=AgentState.set_agent_min_followers,
                    class_name=INPUT_STYLE
                ),
                width="100%",
            ),
            rx.vstack(
                rx.text("Max Followers", font_size="0.9em", color="gray.400"),
                rx.input(
                    placeholder="1m", 
                    value=AgentState.agent_max_followers,
                    on_change=AgentState.set_agent_max_followers,
                    class_name=INPUT_STYLE
                ),
                width="100%",
            ),
            columns="3",
            spacing="4",
            width="100%",
            margin_top="4",
        ),
        rx.text("Niche / Instructions", font_size="0.9em", color="gray.400", margin_top="4"),
        rx.text_area(
            placeholder="Enter niche or specific instructions (e.g. fitness influencers in London)...",
            width="100%", height="120px",
            class_name=INPUT_STYLE,
            value=AgentState.lab_input,
            on_change=AgentState.set_lab_input,
        ),
        width="100%",
        align_items="start",
    )

def researcher_panel():
    return rx.vstack(
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Single Task", value="Single Task"),
                rx.tabs.trigger("Batch Mode", value="Batch Mode"),
            ),
            on_change=AgentState.set_agent_mode,
            value=AgentState.agent_mode,
            width="100%",
            margin_top="4",
        ),
        rx.vstack(
            rx.text("Limit Results", font_size="0.9em", color="gray.400", margin_top="2"),
            rx.hstack(
                rx.slider(
                    min=1, max=2000,
                    value=[AgentState.agent_limit],
                    on_change=lambda v: AgentState.set_agent_limit(v[0]),
                    width="100%",
                ),
                rx.badge(AgentState.agent_limit, color_scheme="indigo"),
                width="100%",
            ),
            width="100%",
        ),
        rx.text("Context / Input Data", font_size="0.9em", color="gray.400", margin_top="4"),
        rx.text_area(
            placeholder="Enter information for the Researcher...",
            width="100%", height="150px",
            class_name=INPUT_STYLE,
            value=AgentState.lab_input,
            on_change=AgentState.set_lab_input,
        ),
        width="100%",
        align_items="start",
    )

def generic_agent_panel():
    return rx.vstack(
        rx.text("Instructions / Context", font_size="0.9em", color="gray.400", margin_top="4"),
        rx.text_area(
            placeholder="Enter instructions or context for the selected agent...",
            width="100%", height="200px",
            class_name=INPUT_STYLE,
            value=AgentState.lab_input,
            on_change=AgentState.set_lab_input,
        ),
        width="100%",
        align_items="start",
    )

def agent_card(name, desc, agent_key):
    return rx.vstack(
        rx.heading(name, size="4", color="white"),
        rx.text(desc, font_size="0.8em", color="gray.400"),
        rx.button(
            "Select Agent", 
            variant="outline", 
            size="2", 
            margin_top="2", 
            on_click=lambda: AgentState.set_active_lab_agent(name)
        ),
        class_name=rx.cond(
            AgentState.active_lab_agent == name,
            f"{CARD_STYLE} border-indigo-500/50",
            CARD_STYLE,
        ),
    )

def log_window():
    """Persistent background log window."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("terminal", size=18, color="indigo.400"),
                rx.text("System Logs", font_size="0.8em", font_weight="bold", color="gray.300"),
                rx.spacer(),
                rx.button(
                    rx.icon("copy", size=14),
                    variant="ghost",
                    size="1",
                    on_click=[
                        rx.set_clipboard(BaseState.logs_text),
                    ],
                    color_scheme="gray",
                    margin_right="2",
                ),
                rx.button(
                    rx.icon("trash-2", size=14),
                    variant="ghost",
                    size="1",
                    on_click=BaseState.clear_logs,
                    color_scheme="gray",
                ),
                rx.divider(orientation="vertical", height="12px", margin_x="1"),
                rx.hstack(
                    rx.icon("volume-2", size=14, color=rx.cond(NavState.voice_enabled, "indigo.400", "gray.600")),
                    rx.switch(
                        is_checked=NavState.voice_enabled,
                        on_change=NavState.set_voice_enabled,
                        size="1",
                    ),
                    rx.popover.root(
                        rx.popover.trigger(
                            rx.button(
                                rx.icon("settings", size=14),
                                variant="ghost",
                                size="1",
                                color_scheme="gray",
                                on_click=rx.console_log("Settings menu opened"),
                            ),
                        ),
                        rx.popover.content(
                            rx.vstack(
                                rx.text("Voice Settings", font_weight="bold", size="2"),
                                rx.vstack(
                                    rx.text("Pitch", font_size="0.7em"),
                                    rx.slider(
                                        default_value=[1.0],
                                        min=0.5,
                                        max=2.0,
                                        step=0.1,
                                        on_change=lambda v: NavState.set_speech_pitch(v[0]),
                                        size="1",
                                    ),
                                    rx.text("Rate", font_size="0.7em"),
                                    rx.slider(
                                        default_value=[0.9],
                                        min=0.5,
                                        max=2.0,
                                        step=0.1,
                                        on_change=lambda v: NavState.set_speech_rate(v[0]),
                                        size="1",
                                    ),
                                    rx.text("System Voice", font_size="0.7em"),
                                    rx.select(
                                        ["Default", "Google US English", "Microsoft David", "Microsoft Zira"],
                                        default_value="Default",
                                        on_change=NavState.set_selected_voice,
                                        size="1",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                spacing="3",
                                padding="3",
                            ),
                            style={"width": "200px"},
                        ),
                    ),
                    rx.button(
                        rx.hstack(rx.icon("square", size=12), rx.text("STOP", font_size="0.7em")),
                        on_click=NavState.stop_speech,
                        variant="soft",
                        size="1",
                        color_scheme="red",
                        padding_x="2",
                        title="Stop Speech",
                    ),
                    spacing="2",
                    align_items="center",
                ),
                width="100%",
                padding_x="3",
                padding_y="2",
                bg="slate.900",
                border_bottom="1px solid rgba(255,255,255,0.1)",
            ),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        SystemState.global_logs,
                        lambda log: rx.text(
                            log,
                            font_size="0.75em",
                            color="slate.400",
                            font_family="monospace",
                            padding_x="3",
                            padding_y="1",
                            width="100%",
                        )
                    ),
                    spacing="0",
                    width="100%",
                ),
                height="200px",
                width="100%",
            ),
            spacing="0",
        ),
        position="fixed",
        bottom="20px",
        right="20px",
        width="350px",
        bg="slate.950",
        border="1px solid rgba(255,255,255,0.1)",
        border_radius="lg",
        shadow="2xl",
        z_index="9999",
        pointer_events="auto",
        overflow="hidden",
    )

def proxy_lab_view():
    return rx.vstack(
        rx.heading("📍 Proxy Lab", size="8", margin_bottom="2", color="white"),
        rx.text("Advanced ScrapeBox-style proxy management.", color="gray.400", margin_bottom="6"),
        
        rx.grid(
            rx.vstack(
                rx.text("Active Elite", font_size="0.9em", color="gray.400"),
                rx.text(ToolsState.proxy_stats_elite, font_size="2em", font_weight="bold", color="green.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Total Working", font_size="0.9em", color="gray.400"),
                rx.text(ToolsState.proxy_stats_total, font_size="2em", font_weight="bold", color="blue.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Current Active Proxy", font_size="0.9em", color="gray.400"),
                rx.text(SystemState.current_proxy, font_size="1.2em", font_weight="bold", color="indigo.300", overflow="hidden"),
                rx.button(
                    rx.hstack(rx.icon("refresh-cw", size=14), rx.text("Rotate")),
                    on_click=SystemState.rotate_proxy,
                    size="1", variant="soft", color_scheme="indigo", margin_top="2"
                ),
                class_name=CARD_STYLE,
            ),
            columns="3",
            spacing="4",
            width="100%",
        ),
        rx.box(
            rx.vstack(
                rx.heading("Import Proxies", size="4", color="white", margin_bottom="4"),
                rx.text_area(
                    placeholder="Paste proxies (IP:PORT or http://user:pass@IP:PORT)...",
                    height="150px",
                    width="100%",
                    class_name=INPUT_STYLE,
                    value=ToolsState.proxy_import_text,
                    on_change=lambda v: ToolsState.set_proxy_import_text(v),
                ),
                rx.button(
                    rx.cond(
                        ToolsState.is_importing_proxies,
                        rx.hstack(rx.spinner(size="1"), rx.text("Importing..."), spacing="2"),
                        rx.hstack(rx.icon("upload"), rx.text("Import Proxy List"), spacing="2"),
                    ),
                    on_click=lambda: ToolsState.import_proxies_now(),
                    disabled=ToolsState.is_importing_proxies,
                    class_name=PRIMARY_BUTTON_STYLE,
                    margin_top="4",
                    width="100%",
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
            margin_top="6",
            width="100%",
        ),
        rx.button(
            rx.hstack(rx.icon("zap"), rx.text("Trigger Global Harvest"), spacing="2"),
            size="3",
            variant="outline",
            margin_top="6",
            on_click=lambda: ToolsState.run_mass_harvest(),
            disabled=ToolsState.is_harvesting,
        ),
        width="100%",
    )

# --- NEW VIEWS FOR MISSING POWER TOOLS ---

def automation_hub_view():
    return rx.vstack(
        rx.heading("📍 Automation Hub", size="8", margin_bottom="2", color="white"),
        rx.text("Autonomous mission control center. Monitor and manage long-running agent loops.", color="gray.400", margin_bottom="6"),
        
        rx.grid(
            rx.vstack(
                rx.text("Active Missions", font_size="0.9em", color="gray.400"),
                rx.text(SystemState.active_jobs.length(), font_size="2em", font_weight="bold", color="indigo.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Total Logs", font_size="0.9em", color="gray.400"),
                rx.text(SystemState.global_logs.length(), font_size="2em", font_weight="bold", color="green.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("System Load", font_size="0.9em", color="gray.400"),
                rx.text("Low", font_size="2em", font_weight="bold", color="blue.400"),
                class_name=CARD_STYLE,
            ),
            columns="3",
            spacing="4",
            width="100%",
            margin_bottom="6",
        ),
        
        rx.box(
            rx.vstack(
                rx.heading("Mission Control", size="5", color="white", margin_bottom="4"),
                rx.cond(
                    SystemState.active_jobs.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            SystemState.active_jobs,
                            lambda job: rx.hstack(
                                rx.text(job["name"], font_weight="bold"),
                                rx.badge(job["status"], color_scheme="green"),
                                rx.spacer(),
                                rx.button("View Logs", size="1", on_click=lambda: SystemState.select_job(job["id"])),
                                width="100%",
                                padding="2",
                                bg="slate.800/50",
                                border_radius="md",
                            )
                        ),
                        width="100%",
                    ),
                    rx.text("No active missions. Load a strategy from the Strategy Laboratory or run an SOP.", color="gray.500"),
                ),
                rx.button("🚀 Launch Autonomous Mission", class_name=PRIMARY_BUTTON_STYLE, margin_top="4", on_click=lambda: SystemState.start_mission(ToolsState.search_query)),
                
                # Night Shift Scheduler
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("moon", size=18, color="indigo.400"),
                            rx.text("Autonomous Night Shift", font_weight="bold", color="white"),
                            rx.spacer(),
                            rx.switch(
                                is_checked=SystemState.night_shift_enabled,
                                on_change=lambda v: SystemState.toggle_night_shift(),
                                color_scheme="indigo",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.text("Eugene will scan trends and draft strategies every night.", font_size="0.8em", color="gray.400"),
                        
                        rx.cond(
                            SystemState.scheduler_running,
                            rx.hstack(
                                rx.badge("Scheduler Active", color_scheme="green"),
                                rx.text("Next scan: ~1 hour", font_size="0.8em", color="gray.500"),
                                spacing="2", 
                                margin_top="2"
                            ),
                            rx.badge("Scheduler Inactive", color_scheme="gray", margin_top="2"),
                        ),
                        
                        rx.button(
                            "Trigger 'Night Shift' Protocol Now",
                            variant="outline",
                            size="1",
                            margin_top="3",
                            on_click=SystemState.trigger_night_shift_now,
                        ),
                    ),
                    bg="slate.900/40",
                    padding="4",
                    border_radius="md",
                    border="1px solid rgba(255, 255, 255, 0.1)",
                    margin_top="4",
                    width="100%",
                ),

                # Mission Control Panel
                rx.cond(
                    SystemState.selected_job_id != "",
                    rx.box(
                        rx.vstack(
                            rx.heading(f"📡 Job: {SystemState.selected_job_id}", size="3", color="white", margin_bottom="2"),
                            
                            # Logs
                            rx.box(
                                rx.scroll_area(
                                    rx.vstack(
                                        rx.foreach(
                                            SystemState.selected_job_logs,
                                            lambda l: rx.text(l, font_family="monospace", font_size="0.8em", color="gray.300")
                                        ),
                                    ),
                                    height="200px"
                                ),
                                bg="black", padding="2", border_radius="md", margin_bottom="4", width="100%"
                            ),
                            
                            rx.hstack(
                                rx.button("Stop Mission", color_scheme="red", variant="outline", on_click=lambda: SystemState.add_log("Stop mission not implemented")),
                                rx.spacer(),
                                rx.button(
                                    rx.cond(
                                        SystemState.is_analyzing_job,
                                        rx.hstack(rx.spinner(size="1"), rx.text("Consulting Eugene...")),
                                        rx.hstack(rx.icon("brain-circuit"), rx.text("Analyze Performance")),
                                    ),
                                    variant="soft", 
                                    color_scheme="indigo",
                                    on_click=SystemState.run_analysis_on_selected_job,
                                    disabled=SystemState.is_analyzing_job,
                                ),
                                width="100%",
                            ),
                            
                            # Eugene's Reflection Card
                            rx.cond(
                                SystemState.job_reflections.contains(SystemState.selected_job_id),
                                rx.box(
                                    rx.hstack(
                                        rx.icon("lightbulb", color="yellow", size=20),
                                        rx.text("Eugene's After-Action Report", font_weight="bold", color="white"),
                                        spacing="2", margin_bottom="2"
                                    ),
                                    rx.text(
                                        SystemState.job_reflections[SystemState.selected_job_id],
                                        color="gray.200",
                                        font_size="0.9em",
                                    ),
                                    bg="indigo.900/30",
                                    border="1px solid rgba(100, 100, 255, 0.2)",
                                    padding="4",
                                    border_radius="md",
                                    margin_top="4",
                                    width="100%",
                                ),
                            ),
                            
                            width="100%",
                        ),
                        bg="slate.800/50", padding="4", border_radius="md", margin_top="4", width="100%"
                    ),
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
            margin_bottom="6",
        ),
        
        rx.box(
            rx.vstack(
                rx.heading(
                    rx.cond(SystemState.selected_job_id, f"Live Logs: {SystemState.selected_job_id}", "Global Logs"),
                    size="5", color="white", margin_bottom="4"
                ),
                rx.box(
                    rx.vstack(
                        rx.foreach(
                            rx.cond(SystemState.selected_job_id, SystemState.selected_job_logs, SystemState.global_logs),
                            lambda log: rx.text(log, font_family="monospace", font_size="0.8em", color="gray.300")
                        ),
                        spacing="1",
                        align_items="start",
                    ),
                    bg="black",
                    padding="4",
                    border_radius="md",
                    width="100%",
                    height="300px",
                    overflow_y="auto",
                ),
                rx.button("Refresh Logs", variant="outline", size="2", on_click=SystemState.update_automation_state, margin_top="2"),
                width="100%",
            ),
            class_name=CARD_STYLE,
        ),
        width="100%",
    )

def workflow_builder_view():
    return rx.vstack(
        rx.heading("📍 Workflow Builder", size="8", margin_bottom="2", color="white"),
        rx.text("Design custom agent workflows using markdown.", color="gray.400", margin_bottom="6"),
        
        rx.grid(
            rx.vstack(
                rx.heading("My Workflows", size="5", color="white", margin_bottom="4"),
                rx.button("➕ New Workflow", variant="outline", width="100%", margin_bottom="4", on_click=lambda: SystemState.set_current_workflow_name("new_workflow.md")),
                rx.vstack(
                    rx.foreach(
                        SystemState.available_workflows,
                        lambda wf: rx.button(
                            rx.hstack(rx.icon("file-text", size=16), rx.text(wf), spacing="2"),
                            variant="ghost",
                            width="100%",
                            justify_content="start",
                            on_click=lambda: SystemState.select_workflow(wf),
                            color=rx.cond(SystemState.current_workflow_name == wf, "indigo.300", "gray.400"),
                            bg=rx.cond(SystemState.current_workflow_name == wf, "indigo.600/20", "transparent"),
                        )
                    ),
                    width="100%",
                ),
                width="100%",
            ),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("✏️ Manual Editor", value="editor"),
                    rx.tabs.trigger("✨ AI Designer", value="designer"),
                ),
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("Editor", size="5", color="white", margin_top="4", margin_bottom="4"),
                        rx.input(
                            id="workflow-filename-input",
                            name="workflow_filename",
                            placeholder="Filename (e.g. outreach_flow.md)", 
                            class_name=INPUT_STYLE, 
                            margin_bottom="3",
                            value=SystemState.current_workflow_name,
                            on_change=lambda v: SystemState.set_current_workflow_name(v),
                        ),
                        rx.input(
                            id="workflow-description-input",
                            name="workflow_description",
                            placeholder="JSON Inputs (e.g. {'target_domain': 'example.com'}) or Description", 
                            class_name=INPUT_STYLE, 
                            margin_bottom="3",
                            value=SystemState.current_workflow_description,
                            on_change=lambda v: SystemState.set_current_workflow_description(v),
                        ),
                        rx.text_area(
                            id="workflow-content-input",
                            name="workflow_content",
                            placeholder="Workflow Steps (Markdown)...", 
                            height="400px", 
                            width="100%", 
                            class_name=INPUT_STYLE,
                            value=SystemState.current_workflow_content,
                            on_change=lambda v: SystemState.set_current_workflow_content(v),
                        ),
                        rx.hstack(
                            rx.button("💾 Save", class_name=PRIMARY_BUTTON_STYLE, width="50%", on_click=lambda: SystemState.save_workflow()),
                            rx.button("🚀 Run", variant="outline", width="50%", on_click=lambda: SystemState.run_workflow_execution()),
                            margin_top="4",
                            width="100%",
                            spacing="3",
                        ),
                        width="100%",
                    ),
                    value="editor",
                    width="100%",
                ),
                rx.tabs.content(
                    rx.vstack(
                        rx.heading("⚔️ Strategy War Room", size="5", color="white", margin_top="4", margin_bottom="2"),
                        rx.text("Collaborate with Eugene to refine your strategy before building.", color="gray.400", margin_bottom="4"),
                        
                        # Chat Display Area
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    AgentState.war_room_messages,
                                    lambda msg: rx.box(
                                        rx.text(msg["content"], color=rx.cond(msg["role"] == "user", "white", "gray.200")),
                                        bg=rx.cond(msg["role"] == "user", "indigo.600", "slate.700"),
                                        padding="3",
                                        border_radius="lg",
                                        align_self=rx.cond(msg["role"] == "user", "end", "start"),
                                        max_width="80%",
                                        margin_bottom="2",
                                    )
                                ),
                                width="100%",
                                align_items="stretch", 
                            ),
                            height="300px",
                            width="100%",
                            padding="4",
                            bg="slate.900/50",
                            border_radius="md",
                            border="1px solid rgba(255,255,255,0.1)",
                        ),
                        
                        # Input Area
                        rx.hstack(
                            rx.input(
                                id="war-room-chat-input",
                                name="war_room_input",
                                placeholder="Pitch an idea (e.g. 'I want to target Yoga studios')...",
                                value=AgentState.war_room_input,
                                on_change=AgentState.set_war_room_input,
                                width="100%",
                                class_name=INPUT_STYLE,
                            ),
                            rx.button(
                                rx.cond(
                                    AgentState.is_war_room_thinking,
                                    rx.spinner(size="1"),
                                    rx.icon("send", size=18),
                                ),
                                on_click=AgentState.send_war_room_message,
                                class_name=PRIMARY_BUTTON_STYLE,
                                disabled=AgentState.is_war_room_thinking,
                                width="fit-content",
                            ),
                            width="100%",
                            spacing="2",
                            margin_top="3",
                        ),
                        
                        width="100%",
                        padding="4",
                        bg="slate.800/20",
                        border_radius="md",
                        border="1px dashed",
                        border_color="slate.700",
                    ),
                    value="designer",
                    width="100%",
                ),
                default_value="designer",
                width="100%",
            ),
            columns="1fr 3fr",
            spacing="6",
            width="100%",
        ),
        width="100%",
    )

def system_monitor_view():
    return rx.vstack(
        rx.heading("📍 System Monitor", size="8", margin_bottom="2", color="white"),
        rx.text("Live view of backend processes, agent thoughts, and system logs.", color="gray.400", margin_bottom="6"),
        
        rx.grid(
            rx.vstack(
                rx.text("CPU Usage", font_size="0.9em", color="gray.400"),
                rx.text(SystemState.cpu_usage, font_size="2em", font_weight="bold", color="indigo.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("RAM Usage", font_size="0.9em", color="gray.400"),
                rx.text(SystemState.ram_usage, font_size="2em", font_weight="bold", color="blue.400"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Worker Concurrency", font_size="0.9em", color="gray.400"),
                rx.text(SystemState.worker_concurrency.to_string(), font_size="2em", font_weight="bold", color="orange.400"),
                rx.text("Adaptive Scaling Active", font_size="0.7em", color="gray.500"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Captcha Queue", font_size="0.9em", color="gray.400"),
                rx.text(SystemState.captcha_queue_size.to_string(), font_size="2em", font_weight="bold", color="red.400"),
                rx.button("Heal Now", size="1", variant="soft", color_scheme="green", on_click=SystemState.heal_captchas),
                class_name=CARD_STYLE,
            ),
            columns="4",
            spacing="4",
            width="100%",
            margin_bottom="6",
        ),
        
        rx.box(
            rx.vstack(
                rx.heading("Stealth Scaling Actions", size="5", color="white", margin_bottom="4"),
                rx.hstack(
                    rx.button(
                        rx.hstack(rx.icon("shield-alert"), rx.text("Simulate CAPTCHA Hit")),
                        on_click=SystemState.add_mock_captcha,
                        variant="outline", color_scheme="red", size="3"
                    ),
                    rx.button(
                        rx.hstack(rx.icon("refresh-cw"), rx.text("Force Proxy Rotation")),
                        on_click=SystemState.rotate_proxy,
                        variant="outline", color_scheme="indigo", size="3"
                    ),
                    spacing="4",
                ),
                width="100%",
                padding="4",
                border="1px dashed rgba(255,255,255,0.1)",
                border_radius="md",
                margin_bottom="6",
            ),
        ),
        
        rx.box(
            rx.vstack(
                rx.heading("Live Engine Logs", size="5", color="white", margin_bottom="4"),
                rx.box(
                    rx.code("[INFO] System initialized\n[DEBUG] Proxy pool loaded (45 active)\n[INFO] Discovery engine started", language="log", width="100%"),
                    bg="black",
                    padding="4",
                    border_radius="md",
                    width="100%",
                ),
                rx.hstack(
                    rx.button(
                        rx.cond(
                            SystemState.is_auditing,
                            rx.hstack(rx.spinner(size="1"), rx.text("Auditing..."), spacing="2"),
                            rx.hstack(rx.icon("search"), rx.text("Run QA Audit"), spacing="2"),
                        ),
                        variant="outline", size="2",
                        on_click=lambda: SystemState.run_qa_audit(),
                        disabled=SystemState.is_auditing,
                    ),
                    rx.button("🗑️ Clear Logs", variant="outline", size="2", on_click=lambda: BaseState.clear_logs()),
                    spacing="4",
                    margin_top="4",
                ),
                rx.cond(
                    SystemState.qa_report,
                    rx.box(
                        rx.markdown(SystemState.qa_report),
                        bg="slate.900",
                        padding="4",
                        border_radius="md",
                        margin_top="4",
                        width="100%",
                    ),
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
        ),
        rx.box(
            llm_router_health_view(),
            class_name=CARD_STYLE,
            margin_top="6",
        ),
        width="100%",
    )

def llm_router_health_view():
    return rx.vstack(
        rx.heading("📡 Router Health (Tiered LLM)", size="5", color="white", margin_bottom="4"),
        rx.grid(
            rx.vstack(
                rx.text("Total Requests", font_size="0.8em", color="gray.400"),
                rx.text(LLMState.total_requests.to_string(), font_size="1.5em", font_weight="bold", color="white"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Failovers Safe", font_size="0.8em", color="gray.400"),
                rx.text(LLMState.failovers.to_string(), font_size="1.5em", font_weight="bold", color="green.400"),
                class_name=CARD_STYLE,
            ),
            columns="2", spacing="4", width="100%", margin_bottom="4"
        ),
        rx.box(
            rx.vstack(
                rx.text("Provider Pool", font_weight="bold", color="indigo.300", margin_bottom="2"),
                rx.foreach(
                    LLMState.provider_info_list,
                    lambda item: rx.hstack(
                        rx.text(item.name, font_weight="medium", width="120px"),
                        rx.badge(
                            item.tier.upper(), 
                            color_scheme=rx.cond(item.tier == "economy", "gray", "indigo")
                        ),
                        rx.spacer(),
                        rx.cond(
                            item.available,
                            rx.badge("ONLINE", color_scheme="green"),
                            rx.hstack(
                                rx.badge("COOLDOWN", color_scheme="red"),
                                rx.text(item.cooldown.to_string(), "s", font_size="0.8em", color="gray.500")
                            )
                        ),
                        rx.button(
                            rx.icon("zap-off", size=12),
                            on_click=lambda: LLMState.simulate_failure(item.name),
                            variant="ghost", size="1", color_scheme="red"
                        ),
                        width="100%", padding="2", bg="slate.800/40", border_radius="md", border="1px solid rgba(255,255,255,0.05)"
                    )
                ),
                width="100%", spacing="2"
            ),
            padding="4", bg="slate.900/50", border_radius="lg", width="100%"
        ),
        rx.hstack(
            rx.button("Test Economy", on_click=lambda: LLMState.run_test_request("Economy"), size="2", variant="outline"),
            rx.button("Test Performance", on_click=lambda: LLMState.run_test_request("Performance"), size="2", variant="outline"),
            rx.button("Reset All", on_click=LLMState.reset_blacklists, size="2", variant="soft", color_scheme="gray"),
            spacing="4", margin_top="4"
        ),
        rx.cond(
            LLMState.last_response != "",
            rx.box(
                rx.text("Last Router Output:", font_size="0.7em", color="gray.500", margin_bottom="1"),
                rx.text(LLMState.last_response, color="gray.300", font_family="monospace"),
                bg="black", padding="3", border_radius="md", margin_top="4", width="100%"
            )
        ),
        width="100%", align_items="start"
    )

def agent_factory_view():
    return rx.vstack(
        rx.heading("📍 Agent Factory", size="8", margin_bottom="2", color="white"),
        rx.text("Create and manage custom AI agents for specific tasks.", color="gray.400", margin_bottom="6"),
        
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("📂 My Agents", value="list"),
                rx.tabs.trigger("➕ Create Agent", value="create"),
                rx.tabs.trigger("🤖 Run Agent", value="run"),
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.text("No custom agents found. Create one in the next tab!", color="gray.500", padding="8"),
                    width="100%",
                ),
                value="list",
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.input(
                        id="factory-agent-name-input",
                        name="factory_agent_name",
                        placeholder="Agent Name", 
                        class_name=INPUT_STYLE, 
                        margin_bottom="3",
                        value=AgentState.new_agent_name,
                        on_change=lambda v: AgentState.set_new_agent_name(v),
                    ),
                    rx.input(
                        id="factory-agent-role-input",
                        name="factory_agent_role",
                        placeholder="Role (e.g. Senior SEO Consultant)", 
                        class_name=INPUT_STYLE, 
                        margin_bottom="3",
                        value=AgentState.new_agent_role,
                        on_change=lambda v: AgentState.set_new_agent_role(v),
                    ),
                    rx.text_area(
                        id="factory-agent-goal-input",
                        name="factory_agent_goal",
                        placeholder="Goal / Instructions...", 
                        class_name=INPUT_STYLE, 
                        height="150px", 
                        margin_bottom="3",
                        value=AgentState.new_agent_goal,
                        on_change=lambda v: AgentState.set_new_agent_goal(v),
                    ),
                    rx.button(
                        "Create Agent", 
                        class_name=PRIMARY_BUTTON_STYLE, 
                        width="100%",
                        on_click=lambda: AgentState.create_custom_agent(),
                    ),
                    width="100%",
                    padding_top="4",
                ),
                value="create",
            ),
            rx.tabs.content(
                rx.vstack(
                    rx.heading("Agent Templates (Workflows)", size="4", color="white", margin_top="4"),
                    rx.text("Select a predefined workflow to launch a specialized agent mission.", color="gray.500", font_size="0.9em", margin_bottom="4"),
                    rx.vstack(
                        rx.foreach(
                            SystemState.available_workflows,
                            lambda wf: rx.hstack(
                                rx.icon("zap", size=18, color="indigo.400"),
                                rx.text(wf, font_weight="bold"),
                                rx.spacer(),
                                rx.button("Launch", size="2", variant="outline", on_click=lambda: SystemState.select_workflow(wf)),
                                width="100%",
                                padding="3",
                                bg="slate.800/30",
                                border_radius="md",
                                border="1px solid",
                                border_color="slate.700/50",
                            )
                        ),
                        width="100%",
                        spacing="2",
                    ),
                    rx.cond(
                        SystemState.current_workflow_name,
                        rx.box(
                            rx.vstack(
                                rx.heading(f"Selected: {SystemState.current_workflow_name}", size="3", color="indigo.300"),
                                rx.text(SystemState.current_workflow_description, color="gray.400", font_size="0.9em"),
                                rx.button("🚀 Execute Autonomous Mission", class_name=PRIMARY_BUTTON_STYLE, width="100%", on_click=lambda: SystemState.run_workflow_execution()),
                                width="100%",
                                spacing="3",
                            ),
                            padding="4",
                            bg="indigo.900/10",
                            border="1px solid",
                            border_color="indigo.500/30",
                            border_radius="lg",
                            margin_top="6",
                            width="100%",
                        )
                    ),
                    width="100%",
                ),
                value="run",
            ),
            width="100%",
        ),
        width="100%",
    )

def direct_search_view():
    return rx.vstack(
        rx.heading("📍 Direct Search", size="8", margin_bottom="2", color="white"),
        rx.text("Bypass proxy checks and run high-intent browser searches.", color="gray.400", margin_bottom="6"),
        
        rx.box(
            rx.vstack(
                rx.heading("Human-Mode Browser Search", size="5", color="white", margin_bottom="4"),
                rx.input(
                    id="direct-search-query-input",
                    name="search_query",
                    placeholder="Search query (e.g. site:linkedin.com \"CEO\" \"SaaS\")", 
                    class_name=INPUT_STYLE, 
                    margin_bottom="4",
                    value=ToolsState.search_query,
                    on_change=lambda v: ToolsState.set_search_query(v),
                ),
                rx.hstack(
                    rx.text("Pages to Scrape", color="gray.400"),
                    rx.slider(
                        min=1, max=10, 
                        width="200px",
                        value=[ToolsState.search_pages],
                        on_change=lambda v: ToolsState.set_search_pages(v[0]),
                    ),
                    rx.badge(ToolsState.search_pages, color_scheme="indigo"),
                    spacing="4",
                ),
                rx.button(
                    rx.cond(
                        ToolsState.is_searching,
                        rx.hstack(rx.spinner(size="1"), rx.text("Searching..."), spacing="2"),
                        rx.hstack(rx.icon("search"), rx.text("Start Direct Search"), spacing="2"),
                    ),
                    class_name=PRIMARY_BUTTON_STYLE,
                    width="100%",
                    margin_top="6",
                    on_click=lambda: ToolsState.run_direct_search(),
                    disabled=ToolsState.is_searching,
                ),
                rx.cond(
                    ToolsState.search_results_count > 0,
                    rx.text(f"✅ Found {ToolsState.search_results_count} potential leads. Check the Leads view.", color="green.400", margin_top="4"),
                ),
                width="100%",
            ),
            class_name=CARD_STYLE,
        ),
        width="100%",
    )


def portfolio_strategy_view():
    return rx.vstack(
        rx.heading("🏰 3-Pillar Portfolio Strategy", size="8", margin_bottom="2", color="white"),
        rx.text("Orchestration of DSR, Authority, and Database Content Layers.", color="gray.400", margin_bottom="6"),
        
        rx.grid(
            rx.vstack(
                rx.text("Total Content Profiles", font_size="0.9em", color="gray.400"),
                rx.text(PortfolioState.total_profiles.to_string(), font_size="2em", font_weight="bold", color="indigo.400"),
                rx.text("Pillar 3 (Traffic)", font_size="0.7em", color="gray.500"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("High-Authority Assets", font_size="0.9em", color="gray.400"),
                rx.text(PortfolioState.high_authority_count.to_string(), font_size="2em", font_weight="bold", color="green.400"),
                rx.text("Pillar 2 (Trust)", font_size="0.7em", color="gray.500"),
                class_name=CARD_STYLE,
            ),
            rx.vstack(
                rx.text("Interlinking Score", font_size="0.9em", color="gray.400"),
                rx.text(f"{PortfolioState.interlinking_score}%", font_size="2em", font_weight="bold", color="blue.400"),
                rx.progress(value=PortfolioState.interlinking_score, size="1", color_scheme="blue", width="100%"),
                class_name=CARD_STYLE,
            ),
            columns="3", spacing="4", width="100%", margin_bottom="6"
        ),
        
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.heading("Pillar Distribution", size="4", color="white", margin_bottom="4"),
                    rx.foreach(
                        PortfolioState.pillar_distribution_list,
                        lambda p: rx.hstack(
                            rx.text(p["pillar"], width="100px", font_size="0.9em"),
                            rx.progress(value=p["percentage"], width="100%"),
                            rx.text(f"{p['percentage']}%", font_size="0.8em", color="gray.400"),
                            width="100%", spacing="2"
                        )
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
            ),
            rx.box(
                rx.vstack(
                    rx.heading("Recent Enriched Profiles", size="4", color="white", margin_bottom="4"),
                    rx.foreach(
                        PortfolioState.enriched_profiles,
                        lambda p: rx.hstack(
                            rx.text(p["name"], font_weight="bold", size="2"),
                            rx.spacer(),
                            rx.badge(p["city"], variant="soft"),
                            rx.badge(p["score"].to_string(), color_scheme="green"),
                            rx.button(
                                rx.icon("video"),
                                size="1",
                                on_click=lambda: PortfolioState.generate_video_for_lead(p["name"]),
                                variant="ghost"
                            ),
                            rx.button(
                                rx.icon("layout"),
                                size="1",
                                on_click=lambda: PortfolioState.design_carousel_for_lead(p["name"]),
                                variant="ghost"
                            ),
                            width="100%", border_bottom="1px solid rgba(255,255,255,0.05)", padding_y="2"
                        )
                    ),
                    rx.button(
                        "Sync Site Factory", 
                        loading=PortfolioState.is_generating_map,
                        on_click=PortfolioState.run_factory_sync,
                        width="100%", margin_top="4"
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
            ),
            # MarketMind Intelligence Feed (Phase 5)
            rx.box(
                rx.vstack(
                    rx.heading("🧠 MarketMind Intelligence", size="4", color="indigo.300", margin_bottom="4"),
                    rx.foreach(
                        PortfolioState.market_events,
                        lambda e: rx.vstack(
                            rx.hstack(
                                rx.text(e["headline"], font_weight="bold", size="2"),
                                rx.badge(e["sentiment"], color_scheme=rx.match(
                                    e["sentiment"],
                                    ("Positive", "green"),
                                    ("Negative", "red"),
                                    "gray"
                                )),
                            ),
                            rx.text(f"Hook: {e['hook']}", font_size="0.8em", color="gray.400", font_style="italic"),
                            width="100%", border_bottom="1px solid rgba(255,255,255,0.05)", padding_y="2", align_items="start"
                        )
                    ),
                    rx.button(
                        "Run Niche Scan",
                        loading=PortfolioState.is_scanning_market,
                        on_click=PortfolioState.run_market_scan_now,
                        width="100%", margin_top="4", variant="surface"
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
            ),
            # AutoPilot CRM (Phase 7)
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.heading("⚙️ AutoPilot CRM", size="4", color="blue.300"),
                        rx.spacer(),
                        rx.switch(
                            is_checked=CRMState.auto_sync_enabled,
                            on_change=CRMState.toggle_auto_sync,
                        ),
                        width="100%",
                    ),
                    rx.text("HubSpot + Zapier Active", font_size="0.75em", color="gray.500", margin_bottom="2"),
                    rx.foreach(
                        CRMState.sync_logs,
                        lambda l: rx.hstack(
                            rx.text(l["name"], font_weight="bold", size="1", color="gray.300"),
                            rx.spacer(),
                            rx.badge(l["status"], color_scheme="green", variant="outline", size="1"),
                            rx.text(l["provider"], size="1", color="gray.500"),
                            width="100%", border_bottom="1px solid rgba(255,255,255,0.05)", padding_y="1"
                        )
                    ),
                    rx.cond(
                        CRMState.is_syncing,
                        rx.hstack(
                            rx.spinner(size="1"),
                            rx.text("Syncing to HubSpot...", size="1", color="gray.500")
                        )
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
            ),
            # Escala Protocol (Phase 8)
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.heading("🛡️ Escala Protocol", size="4", color="red.300"),
                        rx.spacer(),
                        rx.badge(
                            EscalaState.pending_count.to_string() + " PENDING",
                            color_scheme=rx.match(EscalaState.has_pending, (True, "red"), "gray"),
                            variant="solid"
                        ),
                        width="100%",
                    ),
                    rx.text("Strategic Guardrails Enabled", font_size="0.75em", color="gray.500", margin_bottom="2"),
                    rx.foreach(
                        EscalaState.escalation_queue,
                        lambda e: rx.vstack(
                            rx.hstack(
                                rx.text(e["type"].upper(), size="1", font_weight="bold", color="red.400"),
                                rx.spacer(),
                                rx.button(
                                    "Approve", size="1", color_scheme="green",
                                    on_click=lambda: EscalaState.sign_off_request(e["id"], "allow")
                                ),
                                rx.button(
                                    "Reject", size="1", color_scheme="red", variant="outline",
                                    on_click=lambda: EscalaState.sign_off_request(e["id"], "deny")
                                ),
                            ),
                            rx.text(e["context"]["reason"], size="1", color="gray.400"),
                            width="100%", border_bottom="1px solid rgba(255,255,255,0.1)", padding_y="2", align_items="start"
                        )
                    ),
                    rx.cond(
                        ~EscalaState.has_pending,
                        rx.center(
                            rx.text("System Secured. All clear.", size="1", color="gray.600", italic=True),
                            width="100%", padding_y="4"
                        )
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE + " " + rx.cond(EscalaState.has_pending, "border-red-500", ""),
            ),
            # Content Factory (Phase 9)
            rx.box(
                rx.vstack(
                    rx.heading("🎨 Content Factory", size="4", color="pink.300", margin_bottom="4"),
                    rx.foreach(
                        ContentState.asset_gallery,
                        lambda a: rx.vstack(
                            rx.hstack(
                                rx.text(f"CAROUSEL: {a['type'].upper()}", size="1", font_weight="bold", color="gray.400"),
                                rx.spacer(),
                                rx.badge("LIVE PREVIEW", color_scheme="pink", variant="outline", size="1"),
                            ),
                            rx.scroll_area(
                                rx.hstack(
                                    rx.foreach(
                                        a["layout"],
                                        lambda s: rx.box(
                                            rx.vstack(
                                                rx.icon(s["icon"], color="white", size=20),
                                                rx.text(s["title"], font_weight="bold", size="1", color="white"),
                                                rx.text(s["body"], size="1", color="white", opacity=0.8, line_clamp=3),
                                                spacing="1", align_items="start"
                                            ),
                                            padding="3",
                                            border_radius="md",
                                            background=s["hex_color"],
                                            width="120px",
                                            height="120px",
                                            flex_shrink="0"
                                        )
                                    ),
                                    spacing="2",
                                ),
                                style={"width": "100%", "height": "140px"},
                                type="hover"
                            ),
                            width="100%", border_bottom="1px solid rgba(255,255,255,0.05)", padding_y="2"
                        )
                    ),
                    rx.cond(
                        ContentState.is_designing,
                        rx.hstack(
                            rx.spinner(size="1"),
                            rx.text("Vinci is sketching...", size="1", color="gray.500")
                        )
                    ),
                    rx.cond(
                        ContentState.total_assets == 0,
                        rx.center(
                            rx.text("No visual assets generated yet.", size="1", color="gray.600", italic=True),
                            width="100%", padding_y="4"
                        )
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
            ),
            # Video Lab (Phase 6)
            rx.box(
                rx.vstack(
                    rx.heading("📽️ Video Lab", size="4", color="purple.300", margin_bottom="4"),
                    rx.foreach(
                        VideoState.video_queue,
                        lambda v: rx.vstack(
                            rx.hstack(
                                rx.text(v["lead_name"], font_weight="bold", size="2"),
                                rx.badge(v["status"], color_scheme=rx.match(
                                    v["status"],
                                    ("completed", "green"),
                                    ("generating", "orange"),
                                    "gray"
                                )),
                            ),
                            rx.text(v["script"], font_size="0.75em", color="gray.400", line_clamp=2),
                            rx.cond(
                                v["url"],
                                rx.link("Download Video", href=v["url"], font_size="0.75em", color="blue.400")
                            ),
                            width="100%", border_bottom="1px solid rgba(255,255,255,0.05)", padding_y="2", align_items="start"
                        )
                    ),
                    rx.cond(
                        VideoState.is_processing,
                        rx.hstack(
                            rx.spinner(size="1"),
                            rx.text("Personalizing content...", size="1", color="gray.500")
                        )
                    ),
                    width="100%",
                ),
                class_name=CARD_STYLE,
            ),
            columns="2", spacing="4", width="100%"
        ),
        
        width="100%",
    )


from .social_hub import social_hub_view
from .affiliate_hub import affiliate_hub_view
from .dsr_manager import dsr_manager_view
from .creative_designer import creative_designer_view
from .video_studio import video_studio_view
from .seo_suite import seo_suite_view
