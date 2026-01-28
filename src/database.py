"""
Database Facade Module
This module acts as a backward-compatible entry point for the database package.
Logic has been moved to specialized modules in the src/db/ package.
"""

from db.base import (
    get_connection, 
    init_db, 
    get_current_workspace_id,
    get_db_session,
    create_all_tables,
    Base,
    engine,
    SessionLocal,
    DB_PATH
)
from db.leads import (
    add_lead,
    lead_exists,
    mark_contacted,
    get_leads_by_status,
    get_lead_by_id,
    update_lead_enrichment,
    clear_all_leads,
    delete_leads,
    save_agent_work_product,
    get_agent_work_products,
    log_agent_decision,
    update_lead
)
from db.chat import (
    create_chat_session,
    save_chat_message,
    get_chat_history,
    get_chat_sessions,
    update_session_title,
    delete_chat_session
)
from db.campaigns import (
    create_campaign,
    get_campaign,
    get_all_campaigns,
    delete_campaign,
    update_campaign_step,
    update_campaign_pain_point,
    save_pain_points,
    get_pain_points,
    save_template,
    get_templates,
    log_campaign_event,
    get_campaign_analytics,
    get_daily_engagement,
    save_link_wheel,
    get_link_wheels,
    delete_link_wheel,
    create_sequence,
    add_sequence_step,
    enroll_lead_in_sequence,
    update_enrollment_progress,
    get_due_enrollments,
    get_sequence_steps,
    get_campaign_sequences,
    create_dsr,
    update_dsr_wp_info,
    get_dsrs_for_campaign,
    get_dsr_by_lead
)
from db.crm import (
    create_deal,
    get_deals,
    update_deal_stage,
    delete_deals_bulk,
    create_task,
    update_task,
    get_tasks,
    mark_task_completed,
    delete_task,
    add_lead_to_campaign,
    get_campaign_leads,
    save_creative_content,
    get_creative_library,
    delete_creative_item
)
from db.proxies import (
    save_proxies,
    get_best_proxies,
    update_proxy_health,
    update_proxy_source_status,
    clear_proxies,
    get_proxy_sources,
    add_proxy_source,
    invalidate_proxy_cache
)
from db.influencers import (
    save_influencer_candidate,
    bulk_save_influencers,
    get_influencer_candidates,
    update_influencer_status,
    delete_influencer_candidates,
    get_influencer_stats
)
from db.config import (
    save_setting,
    get_setting,
    save_platform_credential,
    get_platform_credentials,
    delete_platform_credential,
    save_captcha_settings,
    get_captcha_settings,
    save_wp_site,
    get_wp_sites,
    delete_wp_site,
    create_custom_agent,
    get_custom_agents,
    delete_custom_agent,
    save_strategy_preset,
    get_strategy_presets,
    get_strategy_preset,
    update_strategy_preset,
    save_managed_account,
    get_managed_accounts,
    update_managed_account,
    update_managed_account_status,
    delete_managed_account,
    add_registration_task,
    get_registration_tasks,
    mark_registration_task_completed,
    save_registration_macro,
    get_registration_macro
)
from db.video import (
    save_video_job,
    get_video_history,
    update_video_job_status
)
from db.stats import (
    get_dashboard_stats,
    load_table_as_df
)

# Unified aliases used in legacy code
def save_agent_work(agent_role, content, artifact_type="text", metadata=None):
    return save_agent_work_product(
        agent_role=agent_role,
        input_task=f"Work Product ({artifact_type})",
        output_content=content,
        metadata=metadata,
        artifact_type=artifact_type
    )

def get_agent_work(agent_role=None, limit=50):
    return get_agent_work_products(agent_role, limit)

def update_lead(lead_id, data):
    """Facade for update_lead logic (currently in leads.py or crm.py)"""
    # Note: Need to implement a generic update_lead in leads.py if not already there.
    # For now, we'll import it from leads.py if it exists.
    from .db.leads import update_lead_enrichment
    # If a generic update is needed, it can be added to leads.py
    pass
