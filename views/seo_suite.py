import reflex as rx
from ..states.outreach import SEOState
from ..styles import *

def keyword_row(item: dict):
    return rx.table.row(
        rx.table.cell(item.get("keyword")),
        rx.table.cell(rx.badge(item.get("difficulty"), color_scheme=rx.cond(item.get("difficulty") == "Low", "green", rx.cond(item.get("difficulty") == "Medium", "orange", "red")))),
        rx.table.cell(item.get("volume_est")),
    )

def audit_card(audit: dict):
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(audit.get("url"), weight="bold", font_size="0.9em", limit=1),
                rx.spacer(),
                rx.badge(f"Score: {audit.get('score')}", color_scheme="green" if audit.get("score") > 80 else "orange"),
                width="100%",
            ),
            rx.text(f"Created: {audit.get('created_at')}", font_size="0.7em", color="gray.500"),
            spacing="1",
        ),
        padding="3",
        bg="slate.800/40",
        border="1px solid",
        border_color="slate.700/50",
        border_radius="md",
    )

def seo_suite_view():
    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading("🚀 Deep SEO Suite", size="8", color="green.300"),
                rx.text("Advanced search optimization and authority building.", color="gray.400"),
                align_items="start",
                spacing="1",
            ),
            rx.spacer(),
            width="100%",
            margin_bottom="6",
        ),

        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("📈 Site Audit", value="audit"),
                rx.tabs.trigger("🔑 Keywords", value="kw"),
                rx.tabs.trigger("🎡 Link Wheel", value="lw"),
            ),
            # --- Audit Tab ---
            rx.tabs.content(
                rx.grid(
                    rx.vstack(
                        rx.heading("Technical Scrutiny", size="4"),
                        rx.text_area(
                            placeholder="Enter URL to audit (e.g. https://mysite.com)",
                            value=SEOState.audit_url,
                            on_change=SEOState.set_audit_url,
                            width="100%",
                            height="100px",
                        ),
                        rx.button(
                            rx.hstack(rx.icon("search-code"), rx.text("Start Deep Audit")),
                            on_click=SEOState.run_audit,
                            loading=SEOState.is_auditing,
                            width="100%",
                            color_scheme="green",
                        ),
                        rx.cond(
                            SEOState.last_audit_report,
                            rx.vstack(
                                rx.heading("Top Issues", size="3", margin_top="4"),
                                rx.list.root(
                                    rx.foreach(
                                        SEOState.last_audit_report["report"]["site_audit"]["top_issues"],
                                        lambda issue: rx.list.item(rx.text(issue, color="red.300", font_size="0.9em"))
                                    )
                                ),
                                rx.heading("Quick Fixes", size="3"),
                                rx.list.root(
                                    rx.foreach(
                                        SEOState.last_audit_report["report"]["site_audit"]["quick_fixes"],
                                        lambda fix: rx.list.item(rx.text(fix, color="green.300", font_size="0.9em"))
                                    )
                                ),
                                width="100%",
                                align_items="start",
                            )
                        ),
                        padding="6",
                        bg="slate.900/60",
                        border="1px solid",
                        border_color="green.500/20",
                        border_radius="xl",
                        align_items="start",
                    ),
                    rx.vstack(
                        rx.heading("Audit History", size="4"),
                        rx.grid(
                            rx.foreach(SEOState.audit_history, audit_card),
                            columns="1",
                            spacing="2",
                            width="100%",
                        ),
                        width="100%",
                        align_items="start",
                    ),
                    columns="2",
                    spacing="8",
                    width="100%",
                    margin_top="6",
                ),
                value="audit",
            ),
            # --- Keywords Tab ---
            rx.tabs.content(
                rx.vstack(
                    rx.hstack(
                        rx.input(
                            placeholder="Niche / Topic...",
                            value=SEOState.keyword_topic,
                            on_change=SEOState.set_keyword_topic,
                            width="100%",
                        ),
                        rx.button("Research", on_click=SEOState.research_keywords, loading=SEOState.is_researching, color_scheme="teal"),
                        width="100%",
                        spacing="4",
                        margin_top="6",
                    ),
                    rx.cond(
                        SEOState.last_keyword_report,
                        rx.vstack(
                            rx.text(SEOState.last_keyword_report["competition_analysis"], color="gray.400", italic=True),
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Keyword"),
                                        rx.table.column_header_cell("Difficulty"),
                                        rx.table.column_header_cell("Est. Volume"),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(SEOState.last_keyword_report["suggested_keywords"], keyword_row)
                                ),
                                width="100%",
                                variant="surface",
                            ),
                            width="100%",
                            spacing="4",
                            align_items="start",
                        )
                    ),
                    width="100%",
                    spacing="6",
                ),
                value="kw",
            ),
            # --- Link Wheel Tab ---
            rx.tabs.content(
                rx.grid(
                    rx.vstack(
                        rx.heading("Architect Config", size="4"),
                        rx.text("Money Site URL", font_size="0.8em"),
                        rx.input(value=SEOState.lw_money_site, on_change=SEOState.set_lw_money_site, placeholder="https://money.com", width="100%"),
                        rx.text("Target Niche", font_size="0.8em"),
                        rx.input(value=SEOState.lw_niche, on_change=SEOState.set_lw_niche, placeholder="Real Estate", width="100%"),
                        rx.text("Linking Strategy", font_size="0.8em"),
                        rx.select(["Standard Wheel", "Double Link Wheel", "Authority Funnel"], value=SEOState.lw_strategy, on_change=SEOState.set_lw_strategy, width="100%"),
                        rx.button("Design Structure", on_click=SEOState.design_link_wheel, color_scheme="blue", width="100%", margin_top="4"),
                        align_items="start",
                        spacing="2",
                        padding="6",
                        bg="slate.900/60",
                        border_radius="xl",
                    ),
                    rx.vstack(
                        rx.heading("Link Graph Visualization", size="4"),
                        rx.cond(
                            SEOState.last_lw_plan,
                            rx.vstack(
                                rx.box(
                                    rx.code_block(SEOState.last_lw_plan["diagram_instructions"], language="mermaid", width="100%"),
                                    width="100%",
                                ),
                                rx.text("Detection Avoidance Strategy:", weight="bold", font_size="0.9em"),
                                rx.text(SEOState.last_lw_plan["footprint_avoidance"], font_size="0.85em", color="gray.400"),
                                align_items="start",
                                width="100%",
                            ),
                            rx.center(rx.text("Design a strategy to see graph.", color="gray.600"), height="300px", width="100%", border="2px dashed", border_color="slate.700", border_radius="lg")
                        ),
                        width="100%",
                        align_items="start",
                    ),
                    columns="2",
                    spacing="8",
                    width="100%",
                    margin_top="6",
                ),
                value="lw",
            ),
            default_value="audit",
            width="100%",
        ),
        width="100%",
        spacing="6",
    )
