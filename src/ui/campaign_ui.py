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
    # Stepper State Management
    if 'campaign_step' not in st.session_state:
        st.session_state['campaign_step'] = campaign_data['current_step']
        
    steps = ["Setup", "Research", "Strategy", "Content", "Launch"]
    render_step_progress(steps, st.session_state['campaign_step'])
    
    current_step = st.session_state['campaign_step']
    
    # Helper to sync step to DB
    def sync_step(step):
        st.session_state['campaign_step'] = step
        update_campaign_step(campaign_id, step)
    
    if current_step == 0:
        with st.container():
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown("### 🎯 Campaign Goal")
                niche_input = st.text_input("Target Niche", value=st.session_state.get('niche_input', campaign_data['niche'] or "Interior Design"))
                product_name = st.text_input("Product Name", value=st.session_state.get('product_name', campaign_data['product_name'] or ""))
            
            with col2:
                st.markdown("### 📝 Context")
                product_context = st.text_area("Product & Service Details", 
                    value=st.session_state.get('product_context', campaign_data['product_context'] or ""),
                    height=150,
                    help="Describe your offering so the AI can map pain points to your solution.")
            
            st.session_state['niche_input'] = niche_input
            st.session_state['product_name'] = product_name
            st.session_state['product_context'] = product_context
            
            if st.button("Next: Research Pain Points ➡", type="primary"):
                if niche_input and product_context:
                     # Update DB metadata before moving on
                     conn = get_connection()
                     c = conn.cursor()
                     c.execute('''
                        UPDATE campaigns 
                        SET niche = ?, product_name = ?, product_context = ?
                        WHERE id = ?
                     ''', (niche_input, product_name, product_context, campaign_id))
                     conn.commit()
                     conn.close()
                     
                     sync_step(1)
                     st.rerun()
                else:
                    st.warning("Please fill in Niche and Context to proceed.")
    # --- STEP 2: RESEARCH ---
    elif current_step == 1:
        st.markdown("### 🧠 AI Analysis")
        st.info(f"Analyzing pain points for: **{st.session_state['niche_input']}**")
        
        if 'pain_points' not in st.session_state:
            with st.spinner("Deep Research Agent is analyzing market data..."):
                # Call backend
                points = start_campaign_step_research(
                    st.session_state['niche_input'], 
                    st.session_state['product_context']
                )
                st.session_state['pain_points'] = points
                st.rerun()
        
        else:
            # Display Results
            for p in st.session_state['pain_points']:
                with st.expander(f"📍 {p['title']}", expanded=True):
                    st.write(p['description'])
            
            col_back, col_next = st.columns([1, 5])
            with col_back:
                if st.button("⬅ Back"):
                    sync_step(0)
                    st.rerun()
            with col_next:
                if st.button("Next: Select Strategy ➡", type="primary"):
                    sync_step(2)
                    st.rerun()
                if st.button("🔄 Regenerate Research"):
                    del st.session_state['pain_points']
                    st.rerun()
    # --- STEP 3: STRATEGY ---
    elif current_step == 2:
        st.markdown("### 🏹 Select Attack Vector")
        st.write("Choose the most compelling angle for your campaign.")
        
        p_titles = [p['title'] for p in st.session_state['pain_points']]
        selected_pain_val = st.session_state.get('selected_pain', '')
        
        try:
            p_idx = p_titles.index(selected_pain_val) if selected_pain_val in p_titles else 0
        except:
            p_idx = 0
        selected_pain = st.radio(
            "Select Focus:", 
            p_titles,
            index=p_idx
        )
        
        st.markdown("#### Tuning Instructions (Optional)")
        refine_feedback = st.text_input("e.g., 'Make it friendlier' or 'Focus on ROI'")
        col_back, col_next = st.columns([1, 5])
        with col_back:
            if st.button("⬅ Back"):
                sync_step(1)
                st.rerun()
        with col_next:
            if st.button("Generate Email Sequence ➡", type="primary"):
                st.session_state['selected_pain'] = selected_pain
                st.session_state['refine_feedback'] = refine_feedback
                
                # Store selected pain point ID in DB
                pp_obj = next(p for p in st.session_state['pain_points'] if p['title'] == selected_pain)
                update_campaign_pain_point(campaign_id, pp_obj['id'])
                
                sync_step(3)
                st.rerun()
    # --- STEP 4: CONTENT ---
    elif current_step == 3:
        st.markdown("### ✍️ Content Generation")
        
        if 'sequence' not in st.session_state:
            with st.spinner("Copywriter Agent is drafting emails..."):
                pain_obj = next(p for p in st.session_state['pain_points'] if p['title'] == st.session_state['selected_pain'])
                seq = start_campaign_step_copy(
                    st.session_state['niche_input'], 
                    pain_obj, 
                    st.session_state['product_name'], 
                    st.session_state['product_context'],
                    campaign_id=campaign_id
                )
                st.session_state['sequence'] = seq
                st.rerun()
        else:
            for email in st.session_state['sequence']:
                with st.expander(f"📧 {email['stage'].upper()}: {email['subject']}", expanded=True):
                    st.markdown(email['body'], unsafe_allow_html=True)
            
            st.divider()
            st.markdown("#### ⚡ Cadence Engine")
            saved_cadences = get_campaign_sequences(campaign_id)
            if saved_cadences:
                st.success(f"Linked Cadence: **{saved_cadences[0]['name']}**")
                if st.button("🗑️ Reset Cadence"):
                    conn = get_connection()
                    conn.cursor().execute("DELETE FROM sequences WHERE campaign_id = ?", (campaign_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
            else:
                if st.button("💾 Save as Persistent Automated Cadence"):
                    with st.spinner("Saving to cadence engine..."):
                        cm = CadenceManager()
                        # Build context
                        pain_obj = next(p for p in st.session_state['pain_points'] if p['title'] == st.session_state['selected_pain'])
                        context = f"Niche: {st.session_state['niche_input']}\nProduct: {st.session_state['product_name']}\nPain Point: {pain_obj['title']}\nDetails: {pain_obj['description']}"
                        
                        # For now, let's use the sequence already in session if possible, 
                        # but CadenceManager.build_campaign_sequence expects to generate it.
                        # Let's adjust CadenceManager or just use its generation for best results.
                        cm.build_campaign_sequence(campaign_id, campaign_data['name'], context)
                        st.success("Automated Sequence Saved!")
                        st.rerun()
            col_back, col_next = st.columns([1, 5])
            with col_back:
                if st.button("⬅ Back"):
                    sync_step(2)
                    st.session_state.pop('sequence', None)
                    st.rerun()
            with col_next:
                 if st.button("Approved! Go to Launch ➡", type="primary"):
                     sync_step(4)
                     st.rerun()
                 if st.button("🔄 Regenerate Copy"):
                     st.session_state.pop('sequence', None)
                     st.rerun()
    # --- STEP 5: LAUNCH ---
    elif current_step == 4:
        st.markdown("### 🚀 Launch Control")
        with st.expander("📤 Import Leads for this Campaign"):
             st.info("Upload a CSV to add leads specifically to this campaign flow.")
             camp_upload = st.file_uploader("Upload CSV (Single Column Email or Standard Format)", type=['csv'], key="camp_csv")
             if camp_upload and st.button("Import to Campaign"):
                  # 1. Process standard import (adds to 'leads' table)
                  success = process_csv_upload(camp_upload, default_source=f"camp_{campaign_id}", default_category=f"campaign_{campaign_data['name']}")
                  if success:
                       # 2. Link these newly added leads to the campaign (based on source identifier)
                       conn = get_connection()
                       c = conn.cursor()
                       c.execute("SELECT id FROM leads WHERE source = ?", (f"camp_{campaign_id}",))
                       lead_ids = [r[0] for r in c.fetchall()]
                       for lid in lead_ids:
                           add_lead_to_campaign(campaign_id, lid)
                       conn.close()
                       st.success(f"Linked {len(lead_ids)} leads to this campaign.")
                       time.sleep(1)
                       st.rerun()
        
        st.success("Campaign Ready for Deployment")
        
        # Show leads associated with this campaign
        c_leads = get_campaign_leads(campaign_id)
        if c_leads:
            st.write(f"**Target Audience ({len(c_leads)} leads):**")
            # Show only first 5
            st.write(", ".join([l['email'] for l in c_leads[:5]]) + ("..." if len(c_leads) > 5 else ""))
        else:
            st.info("No leads linked to this campaign yet. Import them above or use 'Lead Discovery'.")
        
        st.markdown("#### 🧪 Test Flight")
        t_col1, t_col2 = st.columns([3,1])
        with t_col1:
            test_email = st.text_input("Test Email Address")
        with t_col2:
            st.write("")
            st.write("")
            if st.button("Send Test"):
                if test_email and 'sequence' in st.session_state:
                    mailer = Mailer()
                    first = st.session_state['sequence'][0]
                    mailer.send_email(test_email, f"[TEST] {first['subject']}", first['body'])
                    st.toast(f"Sent to {test_email}")
        st.divider()
        
        # --- DIGITAL SALES ROOM SECTION ---
        st.markdown("#### 🏠 Digital Sales Rooms (DSR)")
        st.info("Generate personalized landing pages for high-value leads.")
        
        with st.expander("🛠️ DSR Control Center", expanded=False):
            if not c_leads:
                st.warning("No leads found in this campaign to generate DSRs for.")
            else:
                target_lead_email = st.selectbox("Select Lead for DSR", [l['email'] for l in c_leads])
                target_lead = next(l for l in c_leads if l['email'] == target_lead_email)
                
                dsr_data = get_dsr_by_lead(campaign_id, target_lead['id'])
                
                if dsr_data:
                    st.success(f"DSR Status: {dsr_data['status'].upper()}")
                    if dsr_data['public_url']:
                        st.markdown(f"🔗 [View Live DSR]({dsr_data['public_url']})")
                    
                    col_dsr1, col_dsr2, col_dsr3 = st.columns([1, 1, 1])
                    with col_dsr1:
                        if st.button("👁️ Preview DSR", key=f"prev_{dsr_data['id']}"):
                            st.session_state['show_dsr_preview'] = dsr_data['id']
                    
                    with col_dsr2:
                        if dsr_data['status'] == 'draft':
                            # WP Site Selection
                            saved_sites = get_wp_sites()
                            if not saved_sites:
                                st.warning("No WordPress sites configured in Agent Lab.")
                            else:
                                site_names = [s['name'] for s in saved_sites]
                                selected_site_name = st.selectbox("Select Deployment Site", site_names, key=f"wp_sel_{dsr_data['id']}")
                                selected_site = next(s for s in saved_sites if s['name'] == selected_site_name)
                                
                                if st.button("🚀 Deploy to WordPress", key=f"dep_{dsr_data['id']}"):
                                    with st.spinner("Deploying..."):
                                        dsr_mgr = DSRManager()
                                        wp_agent = WordPressAgent()
                                        res = asyncio.run(dsr_mgr.deploy_dsr(dsr_data['id'], wp_agent, selected_site['id'], selected_site))
                                        if "success" in res:
                                            st.success("Deployed!")
                                            st.rerun()
                                        else:
                                            st.error(res.get('error', 'Failed'))
                    with col_dsr3:
                         if st.button("🗑️ Delete DSR", key=f"del_dsr_{dsr_data['id']}"):
                             conn = get_connection()
                             conn.cursor().execute("DELETE FROM digital_sales_rooms WHERE id = ?", (dsr_data['id'],))
                             conn.commit()
                             conn.close()
                             st.rerun()
                    
                    # Preview Panel
                    if st.session_state.get('show_dsr_preview') == dsr_data['id']:
                        st.divider()
                        st.subheader("🖼️ DSR Live Preview")
                        with st.container(border=True):
                            try:
                                content = json.loads(dsr_data['content_json'])
                                st.title(content.get('headline', 'Our Personalized Solution'))
                                st.markdown(f"### {content.get('subheadline', '')}")
                                st.divider()
                                col1, col2 = st.columns([1, 1])
                                with col1:
                                    st.write(content.get('body_text', ''))
                                with col2:
                                    if content.get('hero_image_url'):
                                        st.image(content['hero_image_url'], use_container_width=True)
                                st.divider()
                                st.button("Close Preview", on_click=lambda: st.session_state.pop('show_dsr_preview', None))
                            except Exception as e:
                                st.error(f"Could not render preview: {e}")
                    else:
                        if st.button("✨ Generate Personalized DSR Content"):
                            with st.spinner("AI is drafting copy and designing visuals..."):
                                dsr_mgr = DSRManager()
                                # Need to run async in streamlit
                                res = asyncio.run(dsr_mgr.generate_dsr_for_lead(campaign_id, target_lead))
                                if res:
                                    st.success("Draft Generated!")
                                    st.rerun()
        st.divider()
        st.divider()
        
        c_cadences = get_campaign_sequences(campaign_id)
        if c_cadences:
            st.markdown("#### ⚡ Cadence Enrollment")
            st.info(f"Active Cadence: **{c_cadences[0]['name']}**")
            if st.button("🚀 ENROLL ALL NEW LEADS IN CADENCE", type="primary"):
                new_leads = [l for l in c_leads if l['status'] == 'new']
                if not new_leads:
                    st.warning("No new leads to enroll.")
                else:
                    for lead in new_leads:
                        enroll_lead_in_sequence(lead['id'], c_cadences[0]['id'])
                    st.success(f"Enrolled {len(new_leads)} leads. Use 'Heartbeat' in sidebar to process.")
                    st.balloons()
            st.write("--- or ---")
        if st.button("🚀 LAUNCH CAMPAIGN (Immediate Send to All)", type="secondary"):
             st.info("Initializing Launch Sequence...")
             mailer = Mailer()
             # Fetch leads linked to this specific campaign
             target_leads = get_campaign_leads(campaign_id)
             # Filter for ones that are still 'new'
             new_target_leads = [l for l in target_leads if l['status'] == 'new']
             
             if not new_target_leads:
                 st.warning("No new leads found for this campaign.")
             else:
                 progress_bar = st.progress(0)
                 for i, row in enumerate(new_target_leads):
                     email_addr = row['email']
                     # status_text.text(f"Sending to {email_addr}...") # Optional: Add status text container
                     
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
                        else:
                            pass # Failed count handled in full impl if needed
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
        if st.button("Close Campaign and Return to List"):
             st.session_state.pop('active_campaign_id', None)
             st.rerun()
