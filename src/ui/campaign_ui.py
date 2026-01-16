import streamlit as st
import pandas as pd
import time
import asyncio
import json
from datetime import datetime
from ui.components import render_step_progress, premium_header
from database import (
    get_all_campaigns, get_campaign, create_campaign, save_campaign_state, 
    get_campaign_state, update_campaign_step, save_lead_search_result,
    get_leads_by_source, add_lead, get_campaign_leads, mark_contacted,
    create_dsr, update_dsr_wp_info, get_dsrs_for_campaign, get_dsr_by_lead,
    create_sequence, add_sequence_step, enroll_lead_in_sequence, get_due_enrollments, 
    get_sequence_steps, get_campaign_sequences, update_enrollment_progress,
    update_campaign_pain_point, add_lead_to_campaign, delete_campaign
)
from agents import (
    ResearcherAgent, CopywriterAgent, ReviewerAgent, ManagerAgent
)
from dsr_manager import DSRManager
from cadence_manager import CadenceManager
from mailer import Mailer
from config import config

def render_campaign_page():
    from ui.components import render_step_progress, premium_header
    
    premium_header("Smart Nurture Campaigns", "Create personalised email sequences using AI research.")
    # --- CAMPAIGN PERSISTENCE LOGIC ---
    if 'active_campaign_id' not in st.session_state:
        st.divider()
        st.subheader("📁 Your Campaigns")
        
        existing_campaigns = get_all_campaigns()
        
        if not existing_campaigns:
            st.info("No active campaigns. Start a new one below!")
        else:
            # 1. Data Management Bar
            render_data_management_bar(existing_campaigns, filename_prefix="campaigns")

            # Show table of existing campaigns
            camp_df = pd.DataFrame(existing_campaigns)
            camp_df['updated_at'] = pd.to_datetime(camp_df['updated_at'], unit='s').dt.strftime('%Y-%m-%d %H:%M')
            
            display_cols = ['id', 'name', 'niche', 'status', 'updated_at']
            st.write("Select a campaign to manage:")
            
            # 2. Enhanced Table
            edited_camps = render_enhanced_table(camp_df[display_cols], key="camp_selector_grid")
            
            selected_camps = edited_camps[edited_camps['Select'] == True]
            
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if not selected_camps.empty and st.button("🚀 Resume/Open Selection", type="primary"):
                    cid = selected_camps.iloc[0]['id']
                    # ... reload logic as before
                    c_data = get_campaign(cid)
                    st.session_state['active_campaign_id'] = cid
                    st.session_state['campaign_step'] = c_data['current_step']
                    st.session_state['niche_input'] = c_data['niche']
                    st.session_state['product_name'] = c_data['product_name']
                    st.session_state['product_context'] = c_data['product_context']
                    st.rerun()
            with col_c2:
                if not selected_camps.empty and st.button("🗑️ Delete Selection", type="secondary"):
                    for cid in selected_camps['id'].tolist():
                        delete_campaign(cid)
                    st.warning("Selected campaigns deleted.")
                    st.rerun()

            # 3. Page Level Chat
            render_page_chat(
                "Campaign Strategy", 
                ManagerAgent(), 
                json.dumps(existing_campaigns, indent=2)
            )
        st.divider()
        st.subheader("✨ Start New Campaign")
        new_camp_name = st.text_input("Campaign Name", placeholder="e.g. Q4 Outreach for Realtors")
        if st.button("Create Campaign"):
            if new_camp_name:
                # Initialize empty campaign in DB
                cid = create_campaign(new_camp_name, "", "", "")
                st.session_state['active_campaign_id'] = cid
                st.session_state['campaign_step'] = 0
                st.rerun()
            else:
                st.warning("Please name your campaign.")
        return # Exit early if no campaign active
    # If we are here, a campaign IS active
    campaign_id = st.session_state['active_campaign_id']
    campaign_data = get_campaign(campaign_id)
    
    st.sidebar.info(f"📍 Active Campaign: **{campaign_data['name']}**")
    if st.sidebar.button("🔌 Exit Campaign Session"):
        del st.session_state['active_campaign_id']
        # Clear related states
        for k in ['niche_input', 'product_name', 'product_context', 'pain_points', 'sequence', 'campaign_step']:
            st.session_state.pop(k, None)
        st.rerun()

    # --- CAMPAIGN WORKSPACE (Tabbed Interface) ---
    st.title(f"Campaign: {campaign_data['name']}")
    
    # Check if setup is needed
    if campaign_data['current_step'] == 0:
        st.warning("⚠️ This campaign is in Setup mode. Complete the wizard to unlock the full workspace.")
        # ... (Keep existing Setup/Research/Strategy wizard for initial creation if preferred, OR move that into Tabs too)
        # For "Final Polish", let's keep the wizard for CREATION, but once they hit "Content", we treat it as "Active".
        # Actually, user feedback says "Turn Campaigns into a real campaign list + campaign workspace".
        # Let's unify it all into tabs to be "one product".
    
    # TABS
    tab_overview, tab_leads, tab_sequence, tab_settings = st.tabs(["📊 Overview", "👥 Leads", "📧 Sequence", "⚙️ Settings"])
    
    with tab_overview:
        st.markdown("### Campaign Pulse")
        c_leads = get_campaign_leads(campaign_id)
        valid_leads = [l for l in c_leads if l['email']] # Basic filter
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Leads", len(c_leads))
        m2.metric("Enrolled in Sequence", "0") # Placeholder for now until enrollment logic allows query
        m3.metric("Status", campaign_data.get('status', 'Draft').upper())
        
        st.divider()
        st.markdown("#### 🚀 Actions")
        if st.button("Generate Email Sequence (AI)", type="primary"):
            st.session_state['active_tab'] = "Sequence" # Can't control tabs programmatically easily in Streamlit yet without extra hacks, just notify
            st.info("Go to the 'Sequence' tab to generate or view content.")
            
        if st.button("🚀 Launch Campaign"):
             st.info("Initializing Launch Sequence...")
             mailer = Mailer()
             # Fetch leads linked to this specific campaign
             target_leads = get_campaign_leads(campaign_id)
             # Filter for ones that are still 'new'
             new_target_leads = [l for l in target_leads if l['status'] == 'new']
             
             if not new_target_leads:
                 st.warning("No new leads found for this campaign.")
             else:
                 if 'sequence' not in st.session_state:
                      st.error("No sequence defined! Go to Sequence tab.")
                 else:
                     progress_bar = st.progress(0)
                     for i, row in enumerate(new_target_leads):
                         email_addr = row['email']
                         # Personalization
                         subject = st.session_state['sequence'][0]['subject']
                         body = st.session_state['sequence'][0]['body']
                         
                         contact = row.get('contact_person') or "there"
                         biz = row.get('business_type') or "your business"
                         
                         subject = subject.replace("{contact_person}", str(contact)).replace("{business_name}", str(biz))
                         body = body.replace("{contact_person}", str(contact)).replace("{business_name}", str(biz))
                         
                         try:
                            if mailer.send_email(email_addr, subject, body):
                                mark_contacted(email_addr)
                         except Exception as e:
                            print(f"Send error: {e}")
                            
                         time.sleep(0.5)
                         progress_bar.progress((i+1)/len(new_target_leads))
                     # Mark campaign as active
                     conn = get_connection()
                     conn.cursor().execute("UPDATE campaigns SET status = 'active' WHERE id = ?", (campaign_id,))
                     conn.commit()
                     conn.close()
                     st.balloons()
                     st.success("Campaign Complete!")

    with tab_leads:
        st.markdown("### 🎯 Target Audience")
        c_leads = get_campaign_leads(campaign_id)
        
        if not c_leads:
            st.info("No leads yet. Import or add them.")
        else:
            ldf = pd.DataFrame(c_leads)
            st.dataframe(ldf[['company_name', 'contact_person', 'email', 'status']], use_container_width=True)
            
        st.divider()
        with st.expander("📥 Import Leads to Campaign"):
             camp_upload = st.file_uploader("Upload CSV", type=['csv'], key="camp_csv_tab")
             if camp_upload and st.button("Import"):
                success = process_csv_upload(camp_upload, default_source=f"camp_{campaign_id}", default_category=f"campaign_{campaign_data['name']}")
                if success:
                   conn = get_connection()
                   c = conn.cursor()
                   c.execute("SELECT id FROM leads WHERE source = ?", (f"camp_{campaign_id}",))
                   lead_ids = [r[0] for r in c.fetchall()]
                   for lid in lead_ids:
                       add_lead_to_campaign(campaign_id, lid)
                   conn.close()
                   st.success(f"Linked {len(lead_ids)} leads.")
                   st.rerun()

    with tab_sequence:
        st.markdown("### 📧 Outreach Sequence")
        
        # UI for Generation
        if 'sequence' not in st.session_state:
             st.info("No sequence generated yet.")
             if st.button("✨ Draft Sequence with AI"):
                 # Needs Inputs
                 if not campaign_data['niche'] or not campaign_data['product_name']:
                     st.error("Please configure Niche and Product in 'Settings' tab first.")
                 else:
                    with st.spinner("AI Copywriter is thinking..."):
                        # We need 'pain_points' logic or similar. 
                        # For now, simplify: direct generation
                        # We'll re-use the function but need search data? 
                        # Let's assume simpler generation for now or prompt for it.
                        pass
        else:
            for i, email in enumerate(st.session_state['sequence']):
                with st.expander(f"Step {i+1}: {email['subject']}", expanded=True):
                    st.markdown(email['body'], unsafe_allow_html=True)

    with tab_settings:
        st.markdown("### ⚙️ Configuration")
        
        new_niche = st.text_input("Target Niche", value=campaign_data['niche'] or "")
        new_prod = st.text_input("Product Name", value=campaign_data['product_name'] or "")
        new_ctx = st.text_area("Context", value=campaign_data['product_context'] or "")
        
        if st.button("Save Settings"):
            conn = get_connection()
            c = conn.cursor()
            c.execute('''
               UPDATE campaigns 
               SET niche = ?, product_name = ?, product_context = ?
               WHERE id = ?
            ''', (new_niche, new_prod, new_ctx, campaign_id))
            conn.commit()
            conn.close()
            st.success("Settings Saved!")
            st.rerun()
