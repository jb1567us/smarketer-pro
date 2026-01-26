
import streamlit as st
import pandas as pd
import time
import asyncio
import json
from datetime import datetime
from ui.components import (
    render_step_progress, premium_header, render_data_management_bar, 
    render_enhanced_table, render_page_chat, confirm_action, safe_action_wrapper
)
from database import (
    get_all_campaigns, get_campaign, create_campaign, save_campaign_state, 
    get_campaign_state, update_campaign_step, save_lead_search_result,
    get_leads_by_source, add_lead, get_campaign_leads, mark_contacted,
    create_sequence, add_sequence_step, enroll_lead_in_sequence, get_due_enrollments, 
    get_sequence_steps, get_campaign_sequences, update_enrollment_progress,
    add_lead_to_campaign, delete_campaign,
    duplicate_campaign, update_campaign_status, get_connection
)
from agents import (
    ResearcherAgent, CopywriterAgent, ReviewerAgent, ManagerAgent
)
from mailer import Mailer

def render_campaign_page():
    premium_header("Smart Nurture Campaigns", "Create personalised email sequences using AI research.")
    
    # --- CAMPAIGN LIST / SELECTION ---
    if 'active_campaign_id' not in st.session_state:
        st.divider()
        st.subheader("📁 Your Campaigns")
        
        existing_campaigns = get_all_campaigns()
        
        if not existing_campaigns:
            st.info("No active campaigns. Start a new one below!")
        else:
            # 1. Data Management Bar
            render_data_management_bar(existing_campaigns, filename_prefix="campaigns")

            # 2. Enhanced Table
            camp_df = pd.DataFrame(existing_campaigns)
            camp_df['updated_at'] = pd.to_datetime(camp_df['updated_at'], unit='s').dt.strftime('%Y-%m-%d %H:%M')
            
            display_cols = ['id', 'name', 'niche', 'status', 'updated_at']
            
            edited_camps = render_enhanced_table(camp_df[display_cols], key="camp_selector_grid")
            
            selected_ids = edited_camps[edited_camps['Select'] == True]['id'].tolist() if 'Select' in edited_camps.columns else []
            
            if selected_ids:
                with st.container(border=True):
                    st.write(f"Selected **{len(selected_ids)}** campaigns")
                    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                    
                    with col_a1:
                        if st.button("🚀 Open Workspace", type="primary", width="stretch"):
                            cid = selected_ids[0]
                            c_data = get_campaign(cid)
                            if c_data:
                                st.session_state['active_campaign_id'] = cid
                                st.session_state['campaign_step'] = c_data['current_step']
                                st.rerun()
                    
                    with col_a2:
                        if st.button("👯 Clone", width="stretch"):
                            for cid in selected_ids:
                                safe_action_wrapper(lambda c=cid: duplicate_campaign(c), f"Campaign {cid} duplicated!")
                            st.rerun()
                            
                    with col_a3:
                        if st.button("▶️ Launch", width="stretch"):
                             for cid in selected_ids:
                                 safe_action_wrapper(lambda c=cid: update_campaign_status(c, 'active'), f"Campaign {cid} launched!")
                             st.rerun()
                    
                    with col_a4:
                        confirm_action("🗑️ Delete", f"Delete {len(selected_ids)} campaigns?", 
                                       lambda: [delete_campaign(cid) for cid in selected_ids], key="del_camps")

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
                cid = create_campaign(new_camp_name, "", "", "")
                st.session_state['active_campaign_id'] = cid
                st.session_state['campaign_step'] = 0
                st.rerun()
            else:
                st.warning("Please name your campaign.")
        return 

    # --- CAMPAIGN WORKSPACE ---
    campaign_id = st.session_state['active_campaign_id']
    campaign_data = get_campaign(campaign_id)
    
    if not campaign_data:
        st.warning("Active campaign not found. Returning to list.")
        del st.session_state['active_campaign_id']
        st.rerun()

    # Sidebar Info
    st.sidebar.markdown(f"### 📍 {campaign_data['name']}")
    st.sidebar.caption(f"Status: {campaign_data.get('status', 'Draft').upper()}")
    
    if st.sidebar.button("🔙 Back to Campaigns"):
        del st.session_state['active_campaign_id']
        st.rerun()

    if st.button("⬅️ Back to Campaigns", key="back_to_list_main"):
        del st.session_state['active_campaign_id']
        st.rerun()

    st.title(f"Workspace: {campaign_data['name']}")
    
    # TABS
    tab_overview, tab_settings, tab_sequence, tab_leads = st.tabs(["📊 Overview", "⚙️ Strategy & Settings", "📧 Sequence", "👥 Leads"])
    
    # --- TAB 1: OVERVIEW ---
    with tab_overview:
        st.subheader("Campaign Pulse")
        c_leads = get_campaign_leads(campaign_id)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Leads", len(c_leads))
        m2.metric("Enrolled", len([l for l in c_leads if l['status'] == 'contacted'])) 
        m3.metric("Status", campaign_data.get('status', 'Draft').upper())
        
        st.divider()
        st.markdown("#### 🚀 Actions")
        
        launch_col, pause_col = st.columns(2)
        with launch_col:
            # SAFETY GUARDRAIL: Launch Confirmation
            if campaign_data['status'] == 'active':
                 st.button("🚀 Launch Campaign", type="primary", width="stretch", disabled=True, help="Campaign is already active.")
            else:
                 def confirm_launch():
                     mailer = Mailer()
                     target_leads = get_campaign_leads(campaign_id)
                     new_target_leads = [l for l in target_leads if l['status'] == 'new']
                     
                     if not new_target_leads:
                         st.warning("No new leads to contact.")
                         return

                     if 'sequence' not in st.session_state and not get_campaign_sequences(campaign_id):
                          st.error("No sequences found. Please generate one in the 'Sequence' tab.")
                          return

                     # Launch Logic
                     progress_bar = st.progress(0)
                     sequences = get_campaign_sequences(campaign_id)
                     seq_steps = get_sequence_steps(sequences[0]['id']) if sequences else st.session_state.get('sequence', [])
                     
                     if not seq_steps: return
                     
                     step1 = seq_steps[0] 
                     success_count = 0
                     
                     for i, row in enumerate(new_target_leads):
                         try:
                             email_addr = row['email']
                             subject = step1.get('subject', 'Hello')
                             body = step1.get('body', 'Hi there')
                             
                             contact = row.get('contact_person') or "there"
                             biz = row.get('business_type') or "your business"
                             subject = subject.replace("{contact_person}", str(contact)).replace("{business_name}", str(biz))
                             body = body.replace("{contact_person}", str(contact)).replace("{business_name}", str(biz))
                             
                             if mailer.send_email(email_addr, subject, body):
                                  mark_contacted(email_addr)
                                  success_count += 1
                         except Exception: pass
                         
                         progress_bar.progress((i+1)/len(new_target_leads))
                         time.sleep(0.1) 
                         
                     conn = get_connection()
                     conn.cursor().execute("UPDATE campaigns SET status = 'active' WHERE id = ?", (campaign_id,))
                     conn.commit()
                     st.success(f"Launch Complete! Sent {success_count} emails.")
                     time.sleep(1)
                     st.rerun()

                 if 'launch_confirm_open' not in st.session_state: st.session_state['launch_confirm_open'] = False
                 
                 if st.button("🚀 Launch Campaign", type="primary", width="stretch"):
                     st.session_state['launch_confirm_open'] = True
                 
                 if st.session_state['launch_confirm_open']:
                     target_leads = get_campaign_leads(campaign_id)
                     new_count = len([l for l in target_leads if l['status'] == 'new'])
                     st.warning(f"⚠️ **CONFIRM LAUNCH**\n\nYou are about to send emails to **{new_count}** new leads.\nThis action cannot be undone.")
                     col_yes, col_no = st.columns(2)
                     if col_yes.button("✅ Yes, Launch Now", type="primary"):
                         confirm_launch()
                         st.session_state['launch_confirm_open'] = False
                     if col_no.button("❌ Cancel"):
                         st.session_state['launch_confirm_open'] = False
                         st.rerun()
                     
        with pause_col:
             if st.button("⏸️ Pause", width="stretch", disabled=campaign_data['status']!='active'):
                 conn = get_connection()
                 conn.cursor().execute("UPDATE campaigns SET status = 'paused' WHERE id = ?", (campaign_id,))
                 conn.commit()
                 st.rerun()

    # --- TAB 2: SETTINGS ---
    with tab_settings:
        st.subheader("Strategy Configuration")
        
        with st.form("camp_settings"):
            new_niche = st.text_input("Target Niche", value=campaign_data['niche'] or "", placeholder="e.g. Dentists in Chicago")
            new_prod = st.text_input("Product Name", value=campaign_data['product_name'] or "", placeholder="e.g. Dental CRM 3000")
            new_ctx = st.text_area("Product Context / UVP", value=campaign_data['product_context'] or "", placeholder="We help dentists get 20% more patients...")
            
            if st.form_submit_button("💾 Save Strategy"):
                conn = get_connection()
                c = conn.cursor()
                c.execute('UPDATE campaigns SET niche = ?, product_name = ?, product_context = ? WHERE id = ?', 
                          (new_niche, new_prod, new_ctx, campaign_id))
                conn.commit()
                st.success("Settings Saved!")
                st.rerun()

    # --- TAB 3: SEQUENCE ---
    with tab_sequence:
        st.subheader("Email Sequence")
        
        # Check if DB sequences exist
        existing_seqs = get_campaign_sequences(campaign_id)
        
        if not existing_seqs and 'sequence' not in st.session_state:
             st.info("No sequence found.")
             
             if st.button("✨ Generate Sequence with AI", type="primary"):
                 if not campaign_data['niche'] or not campaign_data['product_name']:
                     st.error("Please configure Niche and Product in 'Strategy & Settings' tab first.")
                 else:
                     agent = CopywriterAgent()
                     with st.spinner("Writing high-converting emails..."):
                         # Construct context strictly
                         ctx_str = f"Niche: {campaign_data['niche']}\nProduct: {campaign_data['product_name']}\nContext: {campaign_data.get('product_context', '')}"
                         
                         try:
                             # Call specific method instead of non-existent run()
                             res = agent.generate_sequence(ctx_str, steps=3)
                             
                             # Handle potential string return (if provider returns raw JSON string)
                             if isinstance(res, str):
                                 try:
                                     start = res.find('[')
                                     end = res.rfind(']')
                                     if start != -1 and end != -1:
                                         res = json.loads(res[start:end+1])
                                     else:
                                          res = [{"subject": "Error parsing output", "body": res}]
                                 except json.JSONDecodeError:
                                     res = [{"subject": "Error parsing output", "body": res}]
                             
                             # Smart Parse: Handle if LLM wrapped list in a dict key (e.g. {"emails": [...]})
                             if isinstance(res, dict):
                                 # Try to find the first list value
                                 found_list = None
                                 for val in res.values():
                                     if isinstance(val, list):
                                         found_list = val
                                         break
                                 
                                 if found_list:
                                     res = found_list
                                 else:
                                     # If no list found, maybe the dict IS a single step?
                                     res = [res]

                             # Ensure iterable list
                             if not isinstance(res, list):
                                  res = []
                             
                             # Validate keys and cleanup
                             cleaned_seq = []
                             for item in res:
                                 if isinstance(item, dict):
                                     cleaned_seq.append({
                                         "subject": item.get("subject", "No Subject"), 
                                         "body": item.get("body", "No Content")
                                     })
                             
                             if cleaned_seq:
                                 st.session_state['sequence'] = cleaned_seq
                                 st.success("Draft Generated!")
                                 st.rerun()
                             else:
                                 st.error("AI returned empty or invalid sequence.")
                                 
                         except Exception as e:
                             st.error(f"Generation failed: {str(e)}")
                         
        elif 'sequence' in st.session_state:
             st.write("### AI Draft (Unsaved)")
             for i, email in enumerate(st.session_state['sequence']):
                 with st.expander(f"Email {i+1}: {email.get('subject')}", expanded=True):
                     st.text_area("Subject", value=email.get('subject'), key=f"d_sub_{i}")
                     st.text_area("Body", value=email.get('body'), height=200, key=f"d_body_{i}")
             
             if st.button("💾 Save Sequence to Database"):
                 # Create sequence in DB
                 sid = create_sequence(campaign_id, f"Sequence for {campaign_data['name']}")
                 for i, email in enumerate(st.session_state['sequence']):
                     # Fix: Pack subject/body into content_json, pass 0 as delay (or intelligent delay)
                     content_payload = json.dumps({
                         "subject": email.get('subject'),
                         "body": email.get('body')
                     })
                     # args: sequence_id, step_number, touch_type, delay_days, content_json
                     delay_val = 0 if i == 0 else 3 # Default 3 day gap
                     add_sequence_step(sid, i+1, "Email", delay_val, content_payload)
                     
                 del st.session_state['sequence']
                 st.success("Sequence Saved!")
                 st.rerun()
        else:
             # Show saved sequences
             seq = existing_seqs[0] # Show first
             steps = get_sequence_steps(seq['id'])
             for step in steps:
                  with st.container(border=True):
                      # Fix: Unpack content_json and use correct column names
                      try:
                          content = json.loads(step['content_json'])
                          subject = content.get('subject', 'No Subject')
                          body = content.get('body', 'No Content')
                      except:
                          subject = "Error loading step"
                          body = str(step.get('content_json', ''))
                      
                      st.markdown(f"**Step {step['step_number']}: {subject}**")
                      st.markdown(body)

    # --- TAB 4: LEADS ---
    with tab_leads:
        st.subheader("Target Leads")
        c_leads = get_campaign_leads(campaign_id)
        
        if not c_leads:
            st.info("No leads linked. Import them.")
        else:
            ldf = pd.DataFrame(c_leads)
            
            # Filters
            f1, f2 = st.columns([1, 2])
            with f1:
                status_filter = st.multiselect("Status", ldf['status'].unique(), default=ldf['status'].unique())
            with f2:
                params_q = st.text_input("🔍 Search Leads", placeholder="Name, Company, or Email")
            
            filtered_df = ldf[ldf['status'].isin(status_filter)]
            if params_q:
                 mask = (
                    filtered_df['first_name'].astype(str).str.contains(params_q, case=False) |
                    filtered_df['company'].astype(str).str.contains(params_q, case=False) |
                    filtered_df['email'].astype(str).str.contains(params_q, case=False)
                 )
                 filtered_df = filtered_df[mask]
            
            # Interactive Table with Selection
            leads_edited = render_enhanced_table(filtered_df[['id', 'first_name', 'last_name', 'company', 'email', 'status', 'contacted_at']], key=f"camp_leads_{campaign_id}")
            
            # Bulk Actions
            selected_leads = leads_edited[leads_edited['Select'] == True]['id'].tolist() if 'Select' in leads_edited.columns else []
            
            if selected_leads:
                st.markdown(f"**Selected: {len(selected_leads)} leads**")
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("🗑️ Remove from Campaign"):
                        # Implement remove logic
                        st.warning("Remove logic pending implementation.")
                with b2:
                    new_st = st.selectbox("Market As", ["contacted", "dnc", "qualified"], key="bulk_camp_st")
                    if st.button("Update Status"):
                        # Implement update logic
                        st.info("Status update pending implementation.")
            
        st.divider()
        with st.expander("📥 Import CSV"):
             camp_upload = st.file_uploader("Upload CSV", type=['csv'], key="camp_csv_tab")

