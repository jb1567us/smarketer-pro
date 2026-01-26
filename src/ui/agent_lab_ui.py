import streamlit as st
import json
import time
import functools
from agents import (
    ResearcherAgent, QualifierAgent, CopywriterAgent, ManagerAgent,
    GraphicsDesignerAgent, WordPressAgent, ProductManagerAgent, LinkedInAgent,
    ReviewerAgent, SyntaxAgent, UXAgent, SEOExpertAgent, VideoAgent,
    ContactFormAgent, InfluencerAgent
)

# Registry of Standard Agents
AGENTS = {
    "Researcher": ResearcherAgent,
    "Qualifier": QualifierAgent,
    "Copywriter": CopywriterAgent,
    "Manager": ManagerAgent,
    "Graphics Designer": GraphicsDesignerAgent,
    "WordPress": WordPressAgent,
    "Product Manager": ProductManagerAgent,
    "LinkedIn": LinkedInAgent,
    "Reviewer": ReviewerAgent,
    "Syntax": SyntaxAgent,
    "UX": UXAgent,
    "SEO Expert": SEOExpertAgent,
    "Video": VideoAgent,
    "Contact Form": ContactFormAgent,
    "Influencer Scout": InfluencerAgent,
}

from database import (
    get_influencer_candidates, delete_influencer_candidates,
    add_influencer_candidate, add_lead, update_influencer_candidate_status,
    get_leads, delete_leads,
    add_creative_content, get_creative_content, delete_creative_content,
    get_agent_work_products, delete_agent_work_products, save_agent_work_product
)
import pandas
from ui.components import premium_header, safe_action_wrapper, confirm_action

# Categorized Mapping
AGENT_CATEGORIES = {
    "Research & Leads": ["Researcher", "Qualifier", "Persona Analyst", "LinkedIn Specialist", "Contact Form Specialist", "Influencer Scout"],
    "Marketing & Content": ["Copywriter", "Graphics Designer", "Social Media Strategist", "Ad Copywriter", "Video Director", "Brainstormer"],
    "SEO & Growth": ["SEO Expert", "WordPress Expert", "UX Designer"],
    "System & Admin": ["Manager", "Product Manager", "Reviewer", "Syntax Validator"]
}

def render_agent_lab():
    """
    Renders the Agent Lab UI for interacting with standard agents.
    Includes 'System Prompt / Instructions' tweak.
    """
    premium_header("🧪 Agent Lab", "Directly interact with specialized agents organized by capability.")

    # 1. Category Tabs
    cat_names = list(AGENT_CATEGORIES.keys())
    tabs = st.tabs(cat_names)
    
    # Global Active Agent State
    if 'active_lab_agent' not in st.session_state:
        st.session_state['active_lab_agent'] = "Researcher" 

    for i, tab in enumerate(tabs):
        with tab:
            category = cat_names[i]
            agents_in_cat = AGENT_CATEGORIES[category]
            
            # Find index of current active agent if it belongs to this category
            try:
                curr_index = agents_in_cat.index(st.session_state['active_lab_agent'])
            except ValueError:
                curr_index = 0
            
            # Agent Selector
            selection = st.radio(
                f"Select {category} Agent", 
                options=agents_in_cat, 
                horizontal=True,
                label_visibility="collapsed",
                index=curr_index if st.session_state['active_lab_agent'] in agents_in_cat else 0,
                key=f"cat_{i}_selector"
            )
            
            # Update global state on selection
            if selection != st.session_state['active_lab_agent'] and selection in agents_in_cat:
                st.session_state['active_lab_agent'] = selection
            
            if selection:
                 render_agent_interaction_area(selection)


def render_agent_interaction_area(agent_name):
    """
    Renders the interaction area for the specifically selected agent.
    """

    if not agent_name: 
        return

    agent_class = AGENTS.get(agent_name)
    if not agent_class:
        st.error(f"Agent class not found for {agent_name}")
        return
        
    # Instantiate the agent
    try:
        agent = agent_class()
    except Exception:
        agent = agent_class(provider=None) 
    
    st.divider()
    
    # Header for the specific agent area
    c1, c2 = st.columns([1, 4])
    with c1:
        st.write("") # Spacer or Icon
        st.markdown(f"### 🤖") 
    with c2:
        st.markdown(f"**{agent_name}**")
        st.caption(f"{agent.role} • {agent.goal[:100]}...")

    # Special UI for Influencer Scout
    platform_selection = None
    if agent_name == "Influencer Scout":
        platform_selection = st.selectbox(
            "Select Target Platform",
            ["instagram", "tiktok", "youtube", "twitter", "linkedin"],
            key=f"platform_{agent_name}"
        )
        
        limit_selection = st.slider(
            "Max Results Goal",
            min_value=10,
            max_value=2000,
            value=50,
            step=10,
            help="Target number of influencers to discover.",
            key=f"limit_{agent_name}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            min_followers = st.text_input("Min Followers (e.g. 10k)", key=f"min_f_{agent_name}")
        with col2:
            max_followers = st.text_input("Max Followers", key=f"max_f_{agent_name}")


    # Input Area - TABS for Single vs Batch
    tab_single, tab_batch = st.tabs(["Single Task", "Batch Mode"])
    
    # --- TAB 1: SINGLE TASK ---
    with tab_single:
        context = st.text_area(
            "Context / Input Data", 
            height=200, 
            placeholder=f"Enter information for the {agent_name}...",
            help="The main content the agent will process.",
            key=f"input_{agent_name}" 
        )
        
        # SYSTEM PROMPT TWEAK (Single)
        with st.expander("🛠️ Advanced: System Instructions"):
            st.info("💡 Inject additional rules, persona tweaks, or constraints.")
            user_instructions = st.text_area(
                "Additional Instructions", 
                height=100, 
                placeholder="e.g., 'Be extremely sarcastic.', 'Output as CSV only.'",
                key=f"instr_{agent_name}"
            )
        
        # Run Button (Single)
        if st.button(f"Run {agent_name}", type="primary", key=f"run_{agent_name}", width="stretch"):
            if not context:
                st.error("Please provide context to run the agent.")
            else:
                 # Logic Wrapper
                 def _execute_agent():
                    # Prepend platform if applicable
                    final_context = context
                    if platform_selection:
                        final_context = f"Target Platform: {platform_selection}\n"
                        
                    if agent_name == "Influencer Scout" and 'limit_selection' in locals():
                         final_context += f"Target Limit: {limit_selection}\n"
                         if 'min_followers' in locals() and min_followers: final_context += f"Min Followers: {min_followers}\n"
                         if 'max_followers' in locals() and max_followers: final_context += f"Max Followers: {max_followers}\n"
                    
                    final_context += f"\n{context}"

                    with st.spinner(f"{agent.role} is thinking..."):
                         return agent.think(final_context, instructions=user_instructions if user_instructions else None)
                
                 response = safe_action_wrapper(_execute_agent, "Agent Execution")
                 
                 if response:
                    st.session_state['last_lab_response'] = response
                    st.session_state['last_lab_agent_instance'] = agent 
                    st.session_state['last_lab_context'] = context
                    st.session_state['last_lab_agent_name'] = agent_name 
                    st.balloons()
                    st.success("Agent finished successfully!")
                    time.sleep(1)
                    st.rerun()

    # --- TAB 2: BATCH MODE ---
    with tab_batch:
        st.info("Upload a CSV/JSON and run the agent for each row.")
        
        batch_file = st.file_uploader("Batch File (CSV/JSON)", type=['csv', 'json'], key=f"batch_up_{agent_name}")
        batch_template = st.text_area(
            "Prompt Template",
            height=150,
            placeholder="Example: Search for {Company} in {City} and find their contact info.",
            help="Use {ColumnName} to insert data from your file.",
            key=f"batch_tmpl_{agent_name}"
        )
        
        if st.button(f"Run Batch {agent_name}", type="primary", key=f"run_batch_{agent_name}", width="stretch"):
            if not batch_file or not batch_template:
                st.error("Please upload a file and provide a template.")
            else:
                # 1. Parse File
                rows = []
                try:
                    if batch_file.name.endswith('.csv'):
                        rows = pandas.read_csv(batch_file).to_dict(orient='records')
                    else:
                        import json
                        rows = json.load(batch_file)
                        if not isinstance(rows, list): raise ValueError("JSON must be a list")
                except Exception as e:
                    st.error(f"Failed to parse file: {e}")
                    rows = []

                if rows:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    results_log = []
                    
                    for i, row in enumerate(rows):
                        status_text.text(f"Processing item {i+1}/{len(rows)}...")
                        
                        # 2. Interpolate Template
                        try:
                            task_input = batch_template.format(**row)
                        except KeyError as e:
                             st.error(f"Template Error: Column {e} not found in row {i}.")
                             break
                        
                        # 3. Run Agent
                        try:
                            # Prepend platform if applicable (reusing logic)
                            final_input = task_input
                            if platform_selection:
                                final_input = f"Target Platform: {platform_selection}\n" + final_input
                                
                            result = agent.think(final_input)
                            
                            # 4. Auto-Save Result
                            # Determine category for saving
                            cat = next((k for k, v in AGENT_CATEGORIES.items() if agent_name in v), "System & Admin")
                            
                            # Save Logic
                            if cat == "Research & Leads":
                                # Try to parse result as lead if possible, else just save as work log?
                                # Actually, user wanted to upload cities and search. The output might be text.
                                # Unless the agent returns structured data, we can't easily add_lead().
                                # BUT `ResearcherAgent` usually returns text.
                                # Let's save to Work Logs primarily, OR try to extract leads if it's structured.
                                # For safety/generality in V1 batch, let's save to Agent Work Products 
                                # but tag it heavily, so it's not lost. 
                                # OR if we want to be fancy, we try to add_lead if it looks like a lead.
                                # Let's stick to Work Logs for batch safety for now, or if it's text, Creative Content?
                                # Actually, "Work Logs" is the safest bucket for generic outputs.
                                save_agent_work_product(
                                    agent_role=agent_name,
                                    input_task=task_input,
                                    output_content=result,
                                    tags=["batch_run", batch_file.name],
                                    metadata=row
                                )
                            elif cat == "Marketing & Content":
                                add_creative_content({
                                    "agent_type": agent_name,
                                    "content_type": "text",
                                    "title": f"Batch: {str(row.values())[:30]}...",
                                    "body": str(result),
                                    "metadata": row
                                })
                            else:
                                save_agent_work_product(
                                    agent_role=agent_name,
                                    input_task=task_input,
                                    output_content=result,
                                    tags=["batch_run"],
                                    metadata=row
                                )
                                
                        except Exception as e:
                            st.error(f"Error on row {i}: {e}")
                        
                        progress_bar.progress((i + 1) / len(rows))
                    
                    status_text.success("Batch Processing Complete!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()

    # --- INFLUENCER MANAGEMENT UI ---
    if agent_name == "Influencer Scout":
        st.divider()
        st.subheader("📋 Candidate Management")
        
        # 1.a Manual Add
        with st.expander("➕ Add Manually", expanded=False):
            with st.form("manual_inf_add_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    m_handle = st.text_input("Handle (@username)")
                    m_niche = st.text_input("Niche (e.g. fitness)")
                with col_b:
                    m_platform = st.selectbox("Platform", ["instagram", "tiktok", "youtube", "twitter", "linkedin"])
                    m_followers = st.number_input("Followers (Approx)", min_value=0, step=1000)
                
                m_url = st.text_input("Profile URL (Required)")
                if st.form_submit_button("Add Candidate"):
                    if m_url and m_handle:
                         new_cand = {
                             "handle": m_handle,
                             "url": m_url,
                             "platform": m_platform,
                             "niche": m_niche,
                             "follower_count": m_followers,
                             "status": "new"
                         }
                         if add_influencer_candidate(new_cand):
                             st.success(f"Added {m_handle}!")
                             time.sleep(1)
                             st.rerun()
                         else:
                             st.error("Could not add candidate (possible duplicate URL).")
                    else:
                        st.error("Handle and URL are required.")

        # 1.b Import
        with st.expander("📤 Import Candidates (CSV/JSON)"):
            up_file = st.file_uploader("Upload File", type=['csv', 'json'], key="inf_import_up")
            if up_file:
                if st.button("Process Import", key="btn_process_imp"):
                    try:
                        candidates_to_add = []
                        
                        if up_file.name.endswith('.csv'):
                            df_imp = pandas.read_csv(up_file)
                            for _, row in df_imp.iterrows():
                                candidates_to_add.append(row.to_dict())
                        elif up_file.name.endswith('.json'):
                            import json
                            data = json.load(up_file)
                            if isinstance(data, list):
                                candidates_to_add = data
                            else:
                                st.error("JSON must be a list of candidate objects.")
                        
                        # Process and Map
                        success_count = 0
                        for row in candidates_to_add:
                            # Flexible mapping
                            c = {
                                "handle": row.get('handle', row.get('Username', '')),
                                "url": row.get('url', row.get('URL', '')),
                                "platform": row.get('platform', 'instagram'),
                                "niche": row.get('niche', 'imported'),
                                "follower_count": row.get('followers', row.get('follower_count', 0)),
                                "status": "new"
                            }
                            if c['url'] and add_influencer_candidate(c):
                                success_count += 1
                        
                        if success_count > 0:
                            st.success(f"Imported {success_count} candidates!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("No valid new candidates found (check for duplicates or missing URL).")
                    except Exception as e:
                        st.error(f"Import failed: {e}")

        # 2. View & Manage
        candidates = get_influencer_candidates(limit=1000)
        if candidates:
            inf_df = pandas.DataFrame(candidates)
            
            # Selection Column
            inf_df.insert(0, "Select", False)
            
            # Display
            st.caption(f"Showing {len(inf_df)} candidates.")
            
            # Editor (Editable)
            edited_inf = st.data_editor(
                inf_df,
                column_config={
                    "Select": st.column_config.CheckboxColumn(required=True),
                    "url": st.column_config.LinkColumn("Profile"),
                    "created_at": st.column_config.DatetimeColumn("Discovered", disabled=True),
                    "follower_count": st.column_config.NumberColumn("Followers", step=100),
                    "niche": st.column_config.TextColumn("Niche"),
                    "metadata": None, # Hide
                    "id": None # Hide
                },
                hide_index=True,
                key="inf_editor_main",
                width="stretch",
                num_rows="fixed" 
            )
            
            # Actions
            selected_rows = edited_inf[edited_inf['Select'] == True]
            
            # Calculate Changes (Naive check)
            # For complex edits, we can assume the user wants to save what is in the editor if they click Save.
            # But verifying row-by-row is safer for specific field updates.
            
            ac1, ac2, ac3, ac4 = st.columns(4)
            
            with ac1:
                # CRUD: Save Changes
                if st.button("💾 Save Edits", type="primary", key="save_edits_inf"):
                    updated_count = 0
                    current_data = inf_df.set_index('id')
                    
                    for index, row in edited_inf.iterrows():
                        rid = row['id']
                        # Compare critical fields
                        original = current_data.loc[rid] if rid in current_data.index else None
                        
                        if original is not None:
                            updates = {}
                            if row['follower_count'] != original['follower_count']:
                                updates['follower_count'] = row['follower_count']
                            if row['niche'] != original['niche']:
                                updates['niche'] = row['niche']
                            
                            # Update DB if changed
                            # Note: We don't have a generic update_influencer_candidate yet, just status.
                            # But wait, I only implemented update_status in the plan.
                            # I better assume the plan only covered status updates or add a generic update?
                            # Re-reading plan: "Implement update_influencer_candidate_status (Update)"
                            # Ah, I might have missed generic field updates in the plan.
                            # I will interpret 'update_influencer_candidate_status' as the primary update needed for workflow.
                            # However, editing 'Niche' or 'Followers' in the grid implies those should save too.
                            # I should probably quickly patch database.py to allow generic updates or just stick to status loop if strict.
                            # For now, I'll comment out field updates to stick to the approved plan strictly, 
                            # OR just use the status update function if I added generic logic? No I didn't.
                            # Actually, sticking to the plan: I only have status update.
                            # I will skip field updates for now to avoid breaking changes, or just support Status via button.
                            pass

                    st.info("Field editing not fully enabled in backend yet. Use Actions below.")
                    
            with ac2:
                 if st.button(f"🗑️ Delete ({len(selected_rows)})", key="del_inf_btn", disabled=selected_rows.empty):
                     def _delete_flow():
                         ids_to_del = selected_rows['id'].tolist()
                         delete_influencer_candidates(ids_to_del)
                         st.success(f"Deleted {len(ids_to_del)} candidates!")
                         time.sleep(0.5)
                         st.rerun()
                     confirm_action("Confirm Delete", "Delete selected candidates?", _delete_flow, key="conf_del_inf")
                
            with ac3:
                 if st.button(f"🚀 Promote to Leads ({len(selected_rows)})", key="save_lead_btn", disabled=selected_rows.empty):
                     success_c = 0
                     for _, row in selected_rows.iterrows():
                        try:
                            # Construct email/name
                            handle = row.get('handle') or "unknown"
                            email = f"{handle}@social.tmp" # Temporary placeholder
                            add_lead(
                                url=row.get('url'),
                                email=email,
                                company_name=handle,
                                source=f"Influencer Scout: {row.get('platform')}",
                                contact_person=handle,
                                industry=row.get('niche')
                            )
                            # Mark as promoted
                            update_influencer_candidate_status(row['id'], 'promoted')
                            success_c += 1
                        except Exception as e:
                            print(f"Failed to add lead: {e}")
                     
                     if success_c > 0:
                         st.success(f"Promoted {success_c} candidates to CRM!")
                         time.sleep(1)
                         st.rerun()

            
            with ac3:
                # Export
                st.caption("Export")
                csv_data = edited_inf.drop(columns=['Select']).to_csv(index=False)
                st.download_button("📄 CSV", csv_data, "influencer_candidates.csv", "text/csv")
                
                json_data = edited_inf.drop(columns=['Select']).to_json(orient="records", indent=2)
                st.download_button("Values JSON", json_data, "influencer_candidates.json", "application/json")
                
            with ac4:
                # Top 3 Selection shortcut
                if st.button("🏆 Pick Top 3", help="Selects top 3 by follower count"):
                    # Logic to auto-select top 3 (Visualization only, user must save)
                    # Actually, we can't easily modify the 'Select' state of the data_editor from here 
                    # without reloading with prepared data. 
                    # Detailed flow: Sort by followers, take top 3 IDs, update status to 'selected' or just Notify.
                    
                    top_3 = inf_df.sort_values(by='follower_count', ascending=False).head(3)
                    st.session_state['inf_top_3_msg'] = f"Top 3 by followers:\n" + "\n".join([f"- {r['handle']} ({r['follower_count']})" for _, r in top_3.iterrows()])
                    
            if 'inf_top_3_msg' in st.session_state:
                st.info(st.session_state['inf_top_3_msg'])

        else:
            st.info("No candidates discovered yet. Run the agent to find some!")

    # Result & Tuning Section
    if 'last_lab_response' in st.session_state:
        if st.session_state.get('last_lab_agent_name') == agent_name:
            st.divider()
            st.subheader("Result")
            
            response = st.session_state['last_lab_response']
            
            if isinstance(response, (dict, list)):
                 st.json(response)
            else:
                 st.write(response)
                 
            # Export / Persistence
            st.markdown("#### Export")
            res_str = json.dumps(response, indent=2) if isinstance(response, (dict, list)) else str(response)
            
            c_ex1, c_ex2 = st.columns(2)
            with c_ex1:
                 st.download_button(
                      label="📥 Download Result (JSON)",
                      data=res_str,
                      file_name=f"{agent_name}_result_{int(time.time())}.json",
                      mime="application/json"
                 )
            with c_ex2:
                 # Generic Save to History
                 if st.button("💾 Save to History", key=f"save_hist_{agent_name}"):
                     # Determine category
                     cat = next((k for k, v in AGENT_CATEGORIES.items() if agent_name in v), "System & Admin")
                     
                     if cat == "Marketing & Content":
                         add_creative_content({
                             "agent_type": agent_name,
                             "content_type": "text", # Default
                             "title": f"Output from {agent_name}",
                             "body": res_str,
                             "metadata": {"context": st.session_state.get('last_lab_context')}
                         })
                         st.success("Saved to Creative Content Library!")
                     else:
                         save_agent_work_product(
                             agent_role=agent_name,
                             input_task=st.session_state.get('last_lab_context', ''),
                             output_content=res_str,
                             tags=[agent_name]
                         )
                         st.success("Saved to Work Logs!")
                     time.sleep(1)
                     st.rerun()

            # Tuning / Discussion
            render_agent_chat('last_lab_response', st.session_state['last_lab_agent_instance'], 'last_lab_context')


    # --- UNIFIED HISTORY & CRUD SECTION ---
    # Determine which history view to show
    st.divider()
    cat = next((k for k, v in AGENT_CATEGORIES.items() if agent_name in v), "System & Admin")
    
    # 1. SPECIAL CASE: Influencer Scout (Already handled above, but we can show recent saves if we want. 
    #    The above section handles it well enough. We skip it here to avoid duplication.)
    if agent_name == "Influencer Scout":
        pass 
        
    # 2. RESEARCHERS -> Leads Table
    elif cat == "Research & Leads":
        st.subheader("🗄️ Recent Leads / Findings")
        
        # 2.a Import
        with st.expander("📤 Import Leads (CSV/JSON)"):
            up_leads = st.file_uploader("Upload File", type=['csv', 'json'], key=f"leads_up_{agent_name}")
            if up_leads:
                if st.button("Process Import", key=f"proc_leads_{agent_name}"):
                    try:
                        leads_to_add = []
                        if up_leads.name.endswith('.csv'):

                            leads_to_add = pandas.read_csv(up_leads).to_dict(orient='records')
                        elif up_leads.name.endswith('.json'):
                            import json
                            leads_to_add = json.load(up_leads)
                            if not isinstance(leads_to_add, list):
                                st.error("JSON must be a list of objects.")
                                leads_to_add = []
                        
                        added_count = 0
                        for l in leads_to_add:
                            try:
                                # Safe map
                                add_lead(
                                    url=l.get('url'),
                                    email=l.get('email', f"unknown_{int(time.time())}@temp.com"),
                                    company_name=l.get('company_name', l.get('Company', 'Unknown')),
                                    contact_person=l.get('contact_person', l.get('Name', '')),
                                    source=l.get('source', f"Imported via {agent_name}"),
                                    category=l.get('category'),
                                    industry=l.get('industry')
                                )
                                added_count += 1
                            except Exception as ex:
                                print(f"Lead import skip: {ex}")
                        
                        if added_count > 0:
                            st.success(f"Imported {added_count} leads!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("No valid leads processed.")
                            
                    except Exception as e:
                        st.error(f"Import failed: {e}")

        rec_leads = get_leads(limit=20)
        
        # 2.b View & Export
        # Better Implementation with IDs
        rec_leads_full = get_leads(limit=50) # fresh fetch
        if rec_leads_full:
             full_df = pandas.DataFrame(rec_leads_full)
             full_df.insert(0, "Select", False)
             
             # Configure columns to hide ID but keep it available
             e_leads = st.data_editor(
                 full_df,
                 column_config={
                     "Select": st.column_config.CheckboxColumn(required=True),
                     "id": None, # HIDE
                     "workspace_id": None,
                     "created_at": st.column_config.DatetimeColumn(disabled=True)
                 },
                 hide_index=True,
                 key=f"full_leads_edit_{agent_name}"
             )
             
             # Actions Row
             ac_l1, ac_l2, ac_l3 = st.columns([1, 1, 2])
             
             to_del = e_leads[e_leads["Select"]]
             
             with ac_l1:
                 if st.button(f"🗑️ Delete ({len(to_del)})", key=f"btn_del_leads_{agent_name}", disabled=to_del.empty):
                       delete_leads(to_del['id'].tolist())
                       st.success("Deleted!")
                       time.sleep(0.5)
                       st.rerun()
             
             with ac_l2:
                 # Clean export data
                 export_df = e_leads.drop(columns=['Select'])
                 csv_leads = export_df.to_csv(index=False)
                 st.download_button("📄 CSV", csv_leads, "leads_export.csv", "text/csv", key=f"dl_csv_{agent_name}")
                 
             with ac_l3:
                 json_leads = export_df.to_json(orient="records", indent=2)
                 st.download_button("Values JSON", json_leads, "leads_export.json", "application/json", key=f"dl_json_{agent_name}")

        else:
            st.info("No recent leads found.")

    # 3. CREATIVES -> Creative Content
    elif cat == "Marketing & Content":
        st.subheader("🎨 Creative Library")
        
        # 3.a Import
        with st.expander("📤 Import Creative (JSON)"):
            up_cont = st.file_uploader("Upload JSON", type=['json'], key=f"cont_up_{agent_name}")
            if up_cont and st.button("Process Import", key=f"proc_cont_{agent_name}"):
                try:
                    import json
                    items = json.load(up_cont)
                    if isinstance(items, list):
                        c = 0
                        for i in items:
                            if add_creative_content(i): c+=1
                        st.success(f"Imported {c} items!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("JSON must be a list.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # 3.b View
        content_items = get_creative_content(limit=10, agent_type=agent_name)
        
        if content_items:
             c_df = pandas.DataFrame(content_items)
             c_df.insert(0, "Select", False)
             
             e_content = st.data_editor(
                 c_df,
                 column_config={
                     "Select": st.column_config.CheckboxColumn(required=True),
                     "id": None,
                     "body": st.column_config.TextColumn("Content Preview", width="large"),
                     "metadata": None,
                     "created_at": st.column_config.DatetimeColumn(disabled=True)
                 },
                 hide_index=True,
                 key=f"content_edit_{agent_name}"
             )
             
             ac_c1, ac_c2 = st.columns([1, 3])
             c_del = e_content[e_content["Select"]]
             
             with ac_c1:
                 if st.button(f"🗑️ Delete ({len(c_del)})", key=f"btn_del_cont_{agent_name}", disabled=c_del.empty):
                       delete_creative_content(c_del['id'].tolist())
                       st.success("Deleted!")
                       time.sleep(0.5)
                       st.rerun()
             
             with ac_c2:
                 export_c = e_content.drop(columns=['Select'])
                 json_c = export_c.to_json(orient="records", indent=2)
                 st.download_button("📥 Export JSON", json_c, "creative_export.json", "application/json", key=f"dl_cont_{agent_name}")
        
        else:
             st.info("No creative content saved yet.")

    # 4. GENERIC / SYSTEM -> Agent Work Products
    else:
        st.subheader("📜 Work Logs")
        
        # 4.a Import
        with st.expander("📤 Import Logs (JSON)"):
            up_log = st.file_uploader("Upload JSON", type=['json'], key=f"log_up_{agent_name}")
            if up_log and st.button("Process Import", key=f"proc_log_{agent_name}"):
                try:
                    import json
                    items = json.load(up_log)
                    if isinstance(items, list):
                        c = 0
                        for i in items:
                            try:
                                save_agent_work_product(
                                    agent_role=i.get('agent_role', agent_name),
                                    input_task=i.get('input_task'),
                                    output_content=i.get('output_content'),
                                    tags=i.get('tags'),
                                    start_time=i.get('start_time'),
                                    completion_time=i.get('completion_time'),
                                    metadata=i.get('metadata')
                                )
                                c += 1
                            except: pass
                        st.success(f"Imported {c} logs!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("JSON must be a list.")
                except Exception as e:
                    st.error(f"Error: {e}")

        # 4.b View
        logs = get_agent_work_products(limit=20, agent_role=agent_name)
        
        if logs:
             w_df = pandas.DataFrame(logs)
             w_df.insert(0, "Select", False)
             
             e_logs = st.data_editor(
                 w_df,
                 column_config={
                     "Select": st.column_config.CheckboxColumn(required=True),
                     "id": None,
                     "output_content": st.column_config.TextColumn("Output", width="large"),
                     "tags": None,
                     "start_time": None,
                     "completion_time": None,
                     "created_at": st.column_config.DatetimeColumn(disabled=True)
                 },
                 hide_index=True,
                 key=f"logs_edit_{agent_name}"
             )
             
             ac_w1, ac_w2 = st.columns([1, 3])
             l_del = e_logs[e_logs["Select"]]
             
             with ac_w1:
                 if st.button(f"🗑️ Delete ({len(l_del)})", key=f"btn_del_logs_{agent_name}", disabled=l_del.empty):
                       delete_agent_work_products(l_del['id'].tolist())
                       st.success("Deleted!")
                       time.sleep(0.5)
                       st.rerun()
             
             with ac_w2:
                 export_l = e_logs.drop(columns=['Select'])
                 json_l = export_l.to_json(orient="records", indent=2)
                 st.download_button("📥 Export JSON", json_l, "logs_export.json", "application/json", key=f"dl_logs_{agent_name}")

        else:
             st.info("No work logs found.")


def render_agent_chat(response_key, agent_instance, context_key):
    """
    Renders a chat interface for tuning/discussing with an agent after a result.
    """
    if response_key not in st.session_state:
        return

    st.divider()
    st.subheader("💬 Discussion & Tuning")
    st.caption("Not satisfied? Ask the agent to refine, rewrite, or explain.")

    # Initialize chat history for this session if needed
    history_key = f"chat_history_{response_key}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    # Mode Selection
    mode = st.radio(
        "Action:", 
        ["Discuss (Chat)", "Refine (Update Output)"], 
        horizontal=True, 
        key=f"mode_{response_key}",
        help="'Discuss' just asks questions. 'Refine' asks the agent to rewrite the output."
    )

    # Display History
    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"]) 

    # Chat Input
    if user_input := st.chat_input(f"Message the {agent_instance.role}..."):
        # Add user message
        st.session_state[history_key].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Agent Action
        with st.chat_message("assistant"):
            with st.spinner(f"{'Refining' if 'Refine' in mode else 'Thinking'}..."):
                original_context = st.session_state.get(context_key, "")
                previous_response = st.session_state.get(response_key)
                
                # Retrieve history string for context
                hist_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state[history_key]])
                
                try:
                    new_response = None
                    display_content = ""
                    
                    if "Refine" in mode:
                        # TUNE / ITERATE
                        new_response = agent_instance.tune(original_context, previous_response, user_input, history=hist_text)
                        
                        # Update the Main Result State
                        st.session_state[response_key] = new_response
                        
                        if isinstance(new_response, (dict, list)):
                            display_content = f"**Refined Output:**\n```json\n{json.dumps(new_response, indent=2)}\n```"
                        else:
                            display_content = f"**Refined Output:**\n{new_response}"
                            
                    else:
                        # DISCUSS
                        new_response = agent_instance.discuss(original_context, previous_response, user_input, history=hist_text)
                        display_content = new_response

                    st.markdown(display_content)
                    st.session_state[history_key].append({"role": "assistant", "content": display_content})
                    
                    if "Refine" in mode:
                        st.success("Output updated!")
                        time.sleep(1) # Brief pause to show success
                        st.rerun() # Rerun to update the main view above
                    
                except Exception as e:
                    st.error(f"Agent failed: {str(e)}")

# Alias for backwards compatibility if app.py imports it
render_tuning_dialog = render_agent_chat
