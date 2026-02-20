"""
Campaign Wizard View

Multi-step guided campaign creation
"""
import reflex as rx
from ..states.campaign_wizard import CampaignWizardState


def progress_bar() -> rx.Component:
    """Progress indicator"""
    return rx.vstack(
        rx.hstack(
            rx.foreach(
                [0, 1, 2, 3],
                lambda step: rx.box(
                    rx.cond(
                        CampaignWizardState.current_step >= step,
                        rx.icon("check-circle", size=24, color="green.500"),
                        rx.icon("circle", size=24, color="gray.400")
                    ),
                    width="25%",
                    text_align="center"
                )
            ),
            width="100%",
            spacing="4"
        ),
        rx.progress(
            value=CampaignWizardState.progress_percentage,
            width="100%",
            height="8px",
            color_scheme="green"
        ),
        rx.text(
            CampaignWizardState.step_title,
            font_size="xl",
            font_weight="bold",
            color="white",
            margin_top="4"
        ),
        width="100%",
        spacing="2",
        margin_bottom="6"
    )


def step_1_basics() -> rx.Component:
    """Step 1: Campaign Basics"""
    return rx.vstack(
        # Template selection
        rx.heading("Choose a Template", size="6", color="white", margin_bottom="3"),
        rx.hstack(
            rx.foreach(
                ["saas", "agency", "startup", "custom"],
                lambda tmpl: rx.button(
                    rx.vstack(
                        rx.icon("layout-template", size=32),
                        rx.text(
                            CampaignWizardState.templates[tmpl]["name"],
                            font_size="sm"
                        ),
                        spacing="2"
                    ),
                    variant="outline" if CampaignWizardState.selected_template != tmpl else "solid",
                    color_scheme="blue",
                    on_click=lambda: CampaignWizardState.apply_template(tmpl),
                    padding="4",
                    width="150px"
                )
            ),
            spacing="4",
            margin_bottom="6"
        ),
        
        # Basic fields
        rx.heading("Campaign Details", size="6", color="white", margin_bottom="3"),
        rx.form_control(
            rx.form_label("Campaign Name *", color="gray.300"),
            rx.input(
                value=CampaignWizardState.campaign_name,
                on_change=CampaignWizardState.set_campaign_name,
                placeholder="e.g., Q1 SaaS Outreach",
                bg="gray.800",
                color="white",
                border_color="gray.600"
            ),
            margin_bottom="4"
        ),
        
        rx.form_control(
            rx.form_label("Target Niche/Industry *", color="gray.300"),
            rx.input(
                value=CampaignWizardState.campaign_niche,
                on_change=CampaignWizardState.set_campaign_niche,
                placeholder="e.g., B2B SaaS Companies",
                bg="gray.800",
                color="white",
                border_color="gray.600"
            ),
            margin_bottom="4"
        ),
        
        rx.form_control(
            rx.form_label("Product/Service Name *", color="gray.300"),
            rx.input(
                value=CampaignWizardState.product_name,
                on_change=CampaignWizardState.set_product_name,
                placeholder="e.g., AI Outreach Platform",
                bg="gray.800",
                color="white",
                border_color="gray.600"
            ),
            margin_bottom="4"
        ),
        
        rx.form_control(
            rx.form_label("Product Description", color="gray.300"),
            rx.text_area(
                value=CampaignWizardState.product_context,
                on_change=CampaignWizardState.set_product_context,
                placeholder="Brief description of your product/service...",
                bg="gray.800",
                color="white",
                border_color="gray.600",
                height="100px"
            ),
            margin_bottom="4"
        ),
        
        # Error message
        rx.cond(
            CampaignWizardState.step_errors.get(0, "") != "",
            rx.text(
                CampaignWizardState.step_errors[0],
                color="red.400",
                font_size="sm"
            ),
            rx.box()
        ),
        
        width="100%",
        spacing="2"
    )


def step_2_criteria() -> rx.Component:
    """Step 2: Lead Criteria"""
    return rx.vstack(
        rx.heading("Target Lead Criteria", size="6", color="white", margin_bottom="4"),
        rx.text(
            "Define your ideal customer profile (all fields optional)",
            color="gray.400",
            margin_bottom="6"
        ),
        
        rx.form_control(
            rx.form_label("Company Size", color="gray.300"),
            rx.select(
                ["any", "startup", "small", "medium", "enterprise"],
                value=CampaignWizardState.target_company_size,
                on_change=CampaignWizardState.set_target_company_size,
                bg="gray.800",
                color="white",
                border_color="gray.600"
            ),
            margin_bottom="4"
        ),
        
        rx.form_control(
            rx.form_label("Employee Range", color="gray.300"),
            rx.hstack(
                rx.input(
                    type="number",
                    value=CampaignWizardState.min_employees,
                    on_change=CampaignWizardState.set_min_employees,
                    placeholder="Min",
                    bg="gray.800",
                    color="white",
                    border_color="gray.600",
                    width="120px"
                ),
                rx.text("to", color="gray.400"),
                rx.input(
                    type="number",
                    value=CampaignWizardState.max_employees,
                    on_change=CampaignWizardState.set_max_employees,
                    placeholder="Max",
                    bg="gray.800",
                    color="white",
                    border_color="gray.600",
                    width="120px"
                ),
                spacing="3"
            ),
            margin_bottom="4"
        ),
        
        rx.form_control(
            rx.form_label("Target Industries", color="gray.300"),
            rx.text_area(
                placeholder="e.g., Technology, Finance, Healthcare (one per line)",
                bg="gray.800",
                color="white",
                border_color="gray.600",
                height="80px"
            ),
            margin_bottom="4"
        ),
        
        rx.form_control(
            rx.form_label("Geographic Locations", color="gray.300"),
            rx.text_area(
                placeholder="e.g., United States, Europe, Remote (one per line)",
                bg="gray.800",
                color="white",
                border_color="gray.600",
                height="80px"
            ),
            margin_bottom="4"
        ),
        
        width="100%",
        spacing="2"
    )


def step_3_strategy() -> rx.Component:
    """Step 3: Message Strategy"""
    return rx.vstack(
        rx.heading("Message Strategy", size="6", color="white", margin_bottom="4"),
        
        rx.form_control(
            rx.form_label("Message Tone *", color="gray.300"),
            rx.select(
                ["professional", "casual", "technical", "friendly"],
                value=CampaignWizardState.message_tone,
                on_change=CampaignWizardState.set_message_tone,
                bg="gray.800",
                color="white",
                border_color="gray.600"
            ),
            margin_bottom="4"
        ),
        
        rx.form_control(
            rx.form_label("Key Points to Emphasize *", color="gray.300"),
            rx.text_area(
                value=CampaignWizardState.key_points,
                on_change=CampaignWizardState.set_key_points,
                placeholder="- Benefit 1\n- Benefit 2\n- Benefit 3",
                bg="gray.800",
                color="white",
                border_color="gray.600",
                height="150px"
            ),
            rx.text("List key benefits or talking points", color="gray.500", font_size="sm"),
            margin_bottom="4"
        ),
        
        rx.form_control(
            rx.form_label("Call-to-Action *", color="gray.300"),
            rx.input(
                value=CampaignWizardState.call_to_action,
                on_change=CampaignWizardState.set_call_to_action,
                placeholder="e.g., Book a 15-minute demo",
                bg="gray.800",
                color="white",
                border_color="gray.600"
            ),
            margin_bottom="4"
        ),
        
        rx.form_control(
            rx.form_label("Personalization Level", color="gray.300"),
            rx.select(
                ["high", "medium", "low"],
                value=CampaignWizardState.personalization_level,
                on_change=CampaignWizardState.set_personalization_level,
                bg="gray.800",
                color="white",
                border_color="gray.600"
            ),
            rx.text(
                "High = research each lead, Low = generic message",
                color="gray.500",
                font_size="sm"
            ),
            margin_bottom="4"
        ),
        
        # Error message
        rx.cond(
            CampaignWizardState.step_errors.get(2, "") != "",
            rx.text(
                CampaignWizardState.step_errors[2],
                color="red.400",
                font_size="sm"
            ),
            rx.box()
        ),
        
        width="100%",
        spacing="2"
    )


def step_4_review() -> rx.Component:
    """Step 4: Review & Launch"""
    return rx.vstack(
        rx.heading("Review Campaign", size="6", color="white", margin_bottom="4"),
        
        # Summary
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("Campaign:", font_weight="bold", color="gray.300"),
                    rx.text(CampaignWizardState.campaign_name, color="white"),
                    spacing="2"
                ),
                rx.hstack(
                    rx.text("Niche:", font_weight="bold", color="gray.300"),
                    rx.text(CampaignWizardState.campaign_niche, color="white"),
                    spacing="2"
                ),
                rx.hstack(
                    rx.text("Product:", font_weight="bold", color="gray.300"),
                    rx.text(CampaignWizardState.product_name, color="white"),
                    spacing="2"
                ),
                rx.hstack(
                    rx.text("Tone:", font_weight="bold", color="gray.300"),
                    rx.text(CampaignWizardState.message_tone, color="white"),
                    spacing="2"
                ),
                spacing="3"
            ),
            bg="gray.800",
            padding="4",
            border_radius="md",
            margin_bottom="6"
        ),
        
        # Preview
        rx.heading("Message Preview", size="5", color="white", margin_bottom="3"),
        rx.box(
            rx.text(
                CampaignWizardState.preview_message,
                color="gray.300",
                white_space="pre-wrap",
                font_family="mono",
                font_size="sm"
            ),
            bg="gray.900",
            padding="4",
            border_radius="md",
            border="1px solid",
            border_color="gray.700",
            margin_bottom="6"
        ),
        
        rx.button(
            "Generate Preview",
            on_click=CampaignWizardState.generate_preview,
            color_scheme="blue",
            variant="outline"
        ),
        
        width="100%",
        spacing="2"
    )


def wizard_navigation() -> rx.Component:
    """Navigation buttons"""
    return rx.hstack(
        rx.button(
            rx.icon("chevron-left", margin_right="2"),
            "Previous",
            on_click=CampaignWizardState.previous_step,
            variant="outline",
            color_scheme="gray",
            is_disabled=CampaignWizardState.current_step == 0
        ),
        
        rx.spacer(),
        
        rx.cond(
            CampaignWizardState.current_step < 3,
            rx.button(
                "Next",
                rx.icon("chevron-right", margin_left="2"),
                on_click=CampaignWizardState.next_step,
                color_scheme="blue"
            ),
            rx.button(
                rx.icon("rocket", margin_right="2"),
                "Create Campaign",
                on_click=CampaignWizardState.create_campaign,
                color_scheme="green"
            )
        ),
        
        width="100%",
        padding_top="6",
        border_top="1px solid",
        border_color="gray.700"
    )


def campaign_wizard_view() -> rx.Component:
    """Main campaign wizard view"""
    return rx.box(
        rx.vstack(
            rx.heading(
                "🚀 Campaign Wizard",
                size="8",
                margin_bottom="2",
                color="white"
            ),
            rx.text(
                "Create a new campaign in 4 easy steps",
                color="gray.400",
                margin_bottom="8"
            ),
            
            # Progress bar
            progress_bar(),
            
            # Step content
            rx.box(
                rx.cond(
                    CampaignWizardState.current_step == 0,
                    step_1_basics(),
                    rx.cond(
                        CampaignWizardState.current_step == 1,
                        step_2_criteria(),
                        rx.cond(
                            CampaignWizardState.current_step == 2,
                            step_3_strategy(),
                            step_4_review()
                        )
                    )
                ),
                min_height="400px",
                margin_bottom="6"
            ),
            
            # Navigation
            wizard_navigation(),
            
            width="100%",
            max_width="800px",
            spacing="4"
        ),
        padding="8",
        bg="gray.900",
        min_height="100vh"
    )
