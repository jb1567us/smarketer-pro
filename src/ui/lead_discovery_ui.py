import streamlit as st
import pandas as pd
import asyncio
import json
import time
from workflow import run_outreach
from config import config
from database import load_data, get_all_campaigns, add_lead_to_campaign
from ui.components import render_enhanced_table, render_data_management_bar, render_page_chat
from agents import ResearcherAgent

def render_lead_discovery():
    """Renders the Lead Discovery UI component."""
    st.subheader("🔍 Find New Leads")
    with st.form("search_form"):
        query = st.text_input("Search Query", "marketing agencies in Austin")
        col_search_1, col_search_2 = st.columns(2)
        with col_search_1:
            niche = st.text_input("Target Niche Filter (Optional)", "Marketing")
        with col_search_2:
            # Default to config value, but allow override
            search_conf = config.get("search") or {}
            default_max = search_conf.get("max_results", 50)
            limit = st.number_input("Max Results", min_value=1, max_value=10000, value=default_max, help="Limit the number of leads to fetch.")
        
        # Load available profiles from config
        search_config = config.get("search") or {}
        available_profiles = list(search_config.get("profiles", {}).keys())
        if not available_profiles:
            available_profiles = ["default"]
            
        selected_profiles = st.multiselect("Search Profiles", available_profiles, default=["default"])
        
        with st.expander("🚫 Domain Filters (Exclusions)"):
            st.caption("URLs containing these patterns will be ignored.")
            # Load defaults
            default_exclusions = search_conf.get("exclude_patterns", [])
            
            # CSV Upload
            exclusion_csv = st.file_uploader("Upload CSV Exclusion List", type=["csv"], help="One domain/pattern per line")
            if exclusion_csv:
                 try:
                     df_uploaded = pd.read_csv(exclusion_csv)
                     # Assume first column is what we want if no standard name
                     col_name = df_uploaded.columns[0]
                     new_patterns = df_uploaded[col_name].astype(str).tolist()
                     # Merge unique
                     default_exclusions = list(set(default_exclusions + new_patterns))
                     st.success(f"Added {len(new_patterns)} patterns from CSV.")
                 except Exception as e:
                     st.error(f"Error reading CSV: {e}")

            # Convert to df for editor with explicit types to avoid StreamlitAPIException
            df_exclude = pd.DataFrame({
                'Active': [True] * len(default_exclusions),
                'Pattern': default_exclusions
            }).astype({'Active': bool, 'Pattern': str})
            
            edited_exclusions = st.data_editor(
                df_exclude, 
                num_rows="dynamic", 
                key="exclusion_editor",
                column_config={
                    "Active": st.column_config.CheckboxColumn(required=True, default=True),
                    "Pattern": st.column_config.TextColumn(required=True)
                }
            )
            
            # Filter only Active patterns
            if not edited_exclusions.empty:
                current_exclusions = edited_exclusions[edited_exclusions["Active"] == True]["Pattern"].tolist()
            else:
                current_exclusions = []

        
        with st.expander("🎯 Enhanced ICP Filters"):
            st.caption("Filter leads by specific business characteristics.")
            
            col_icp1, col_icp2 = st.columns(2)
            
            with col_icp1:
                industry_options = [
                    "Any",
                    "Technology/SaaS",
                    "E-commerce/Retail",
                    "Professional Services",
                    "Healthcare",
                    "Finance/Insurance",
                    "Manufacturing",
                    "Real Estate",
                    "Education",
                    "Non-Profit"
                ]
                selected_industries = st.multiselect(
                    "Industry",
                    industry_options,
                    default=["Any"],
                    help="Target specific industries"
                )
                
                company_size_options = [
                    "Any",
                    "Startup (1-10)",
                    "Small (11-50)",
                    "Medium (51-200)",
                    "Large (201-1000)",
                    "Enterprise (1000+)"
                ]
                selected_sizes = st.multiselect(
                    "Company Size",
                    company_size_options,
                    default=["Any"],
                    help="Filter by employee count"
                )
            
            with col_icp2:
                location_filter = st.text_input(
                    "Location/Geography",
                    placeholder="e.g., USA, California, Austin",
                    help="Filter by city, state, or country"
                )
                
                revenue_options = [
                    "Any",
                    "< $1M",
                    "$1M - $10M",
                    "$10M - $50M",
                    "$50M - $100M",
                    "> $100M"
                ]
                selected_revenue = st.selectbox(
                    "Revenue Range",
                    revenue_options,
                    help="Filter by annual revenue"
                )
            
            # Save filter template
            col_save1, col_save2 = st.columns(2)
            with col_save1:
                template_name = st.text_input("Save as Template", placeholder="e.g., Tech Startups")
            with col_save2:
                if st.button("💾 Save Filters", disabled=not template_name):
                    # Save to session state or config
                    if 'saved_icp_templates' not in st.session_state:
                        st.session_state['saved_icp_templates'] = {}
                    
                    st.session_state['saved_icp_templates'][template_name] = {
                        'industries': selected_industries,
                        'sizes': selected_sizes,
                        'location': location_filter,
                        'revenue': selected_revenue
                    }
                    st.success(f"Saved template: {template_name}")
            
            # Build ICP filter criteria for Quality Gate
            icp_filter_criteria = []
            if "Any" not in selected_industries:
                icp_filter_criteria.append(f"Industry: {', '.join(selected_industries)}")
            if "Any" not in selected_sizes:
                icp_filter_criteria.append(f"Company Size: {', '.join(selected_sizes)}")
            if location_filter:
                icp_filter_criteria.append(f"Location: {location_filter}")
            if selected_revenue != "Any":
                icp_filter_criteria.append(f"Revenue: {selected_revenue}")

        with st.expander("🛡️ Quality Gate (ICP Criteria)"):
            st.caption("AI will filter out leads that do not match these criteria.")
            enable_gate = st.toggle("Enable Quality Gate", value=True)
            
            # Safe config access
            qg_config = config.get("quality_gate") or {}
            
            # Pre-populate with ICP filter criteria if set
            default_must = "\n".join(qg_config.get("must_haves", []))
            if icp_filter_criteria:
                default_must = "\n".join(icp_filter_criteria) + "\n" + default_must
            
            col_icp1, col_icp2 = st.columns(2)
            with col_icp1:
                must_have = st.text_area("Must Haves", 
                    value=default_must,
                    placeholder="e.g. B2B Software, Uses Shopify, Based in USA",
                    help="Leads MUST match these to pass.")
            with col_icp2:
                default_breakers = "\n".join(qg_config.get("deal_breakers", []))
                deal_breakers = st.text_area("Deal Breakers", 
                    value=default_breakers,
                    placeholder="e.g. Agencies, Non-profits, Students",
                    help="Leads matching these will be rejected (0 score).")
            
            icp_criteria = None
            if enable_gate and (must_have.strip() or deal_breakers.strip()):
                icp_criteria = f"Must Haves:\n{must_have}\n\nDeal Breakers:\n{deal_breakers}"

        with st.expander("🚀 Deep Intelligence (Enrichment)"):
            st.caption("Automatically find social profiles and hiring intent signals.")
            auto_enrich = st.checkbox("Auto-Enrich Leads (LinkedIn, Twitter, Intent)", value=False)


        st.warning("⚠️ Do not leave this page while the search is running. It will stop the process.")
        
        st.divider()
        submitted = st.form_submit_button("Start Search 🚀", type="primary", width="stretch")
        
        if submitted:
            # Check for empty Quality Gate
            if enable_gate and not icp_criteria:
                 st.warning("⚠️ Quality Gate enabled but criteria fields are empty. Proceeding without filtering (All leads will pass).")

            st.info("Agent is running... (See logs below)")

            # Log Container
            if not selected_profiles:
                selected_profiles = ["default"]

            # Modern Status UI
            with st.status("🕵️‍♂️ Agent is scouting the web...", expanded=True) as status:
                def update_log(msg):
                    status.write(msg)
                    if "Found:" in msg:
                        st.toast(msg, icon="🎉")
                
                # Async wrapper - CAPTURE RESULTS
                results = asyncio.run(run_outreach(
                    query, 
                    profile_names=selected_profiles, 
                    target_niche=niche, 
                    status_callback=update_log,
                    exclusions=current_exclusions,
                    icp_criteria=icp_criteria,
                    max_results=limit,
                    auto_enrich=auto_enrich
                ))
                
                status.update(label=f"Search Mission Complete! {len(results) if results else 0} Leads Found.", state="complete", expanded=False)
            
            if results:
                st.session_state['last_search_results'] = results
                st.success(f"Successfully found and saved {len(results)} new leads!")
            else:
                st.warning("Search complete, but no new unique leads were found.")
        
    # --- RESULTS DISPLAY AREA (Outside the form) ---
    if st.session_state.get('last_search_results'):
        st.divider()
        st.subheader("📋 Latest Search Results")

        results_data = st.session_state['last_search_results']
        
        # Flatten for display
        display_list = []
        for r in results_data:
            display_list.append({
                "Company": r.get('details', {}).get('business_name') or r.get('url'),
                "Emails": ", ".join(r.get('emails', [])),
                "Industry": r.get('details', {}).get('industry') or niche,
                "Score": r.get('analysis', {}).get('score', 0),
                "URL": r.get('url'),
                "ID": r.get('id')
            })
        
        df_res = pd.DataFrame(display_list)
        
        # 1. Standard Data Management Bar
        def clear_results():
            st.session_state['last_search_results'] = None
            st.rerun()

        render_data_management_bar(
            display_list, 
            filename_prefix="leads_discovery", 
            on_delete=clear_results
        )

        # 2. Enhanced Table
        edited_df = render_enhanced_table(df_res, key="lead_discovery_table")
        
        # --- NEW: Lead Drill-Down Panel ---
        # Get selected indices from the edited dataframe
        # In render_enhanced_table, it adds a 'Select' column
        if 'Select' in edited_df.columns:
            selected_indices = edited_df[edited_df['Select'] == True].index.tolist()
        else:
            selected_indices = []

        if selected_indices:
            st.divider()
            st.subheader("🔎 Lead Inspector")
            
            # If multiple selected, showing the first one as "Deep Dive Focus"
            # but bulk actions still apply to all.
            focus_idx = selected_indices[0]
            # Safety check for index out of bounds
            if focus_idx < len(results_data):
                focus_lead = results_data[focus_idx]
                
                with st.container(border=True):
                    d_col1, d_col2 = st.columns([2, 1])
                    with d_col1:
                        st.markdown(f"### {focus_lead.get('details', {}).get('business_name') or focus_lead.get('url')}")
                        st.caption(f"🌐 {focus_lead.get('url')}")
                        
                        st.markdown("#### 📧 Contact Info")
                        emails = focus_lead.get('emails', [])
                        if emails:
                            for e in emails:
                                st.code(e, language="text")
                        else:
                            st.warning("No emails found yet.")
                        
                        st.markdown("#### 🧠 AI Analysis")
                        st.write(focus_lead.get('analysis', {}).get('reasoning', 'No deep analysis available.'))
                        
                    with d_col2:
                        st.metric("Match Score", f"{focus_lead.get('analysis', {}).get('score', 0)}/100")
                        
                        st.markdown("#### Socials")
                        socials = focus_lead.get('social_links', {})
                        if socials:
                            for plat, link in socials.items():
                                st.markdown(f"[{plat.capitalize()}]({link})")
                        else:
                            st.caption("No socials found.")
                            
                        st.divider()
                        if st.button("✨ Enrich This Lead", key=f"enrich_{focus_lead.get('id')}"):
                            with st.spinner("Enriching..."):
                                # Dummy placeholder for enrichment hook
                                time.sleep(1) 
                                st.toast("Enrichment Request Queued (Demo)")
        
        # --- NEW: Bulk Action: Add to Campaign ---
        st.divider()
        st.subheader("⚡ Bulk Actions")
        col_bulk1, col_bulk2 = st.columns([2, 1])
        
        with col_bulk1:
            campaigns = get_all_campaigns()
            if campaigns:
                camp_options = {c['name']: c['id'] for c in campaigns}
                target_camp = st.selectbox("Select Target Campaign", list(camp_options.keys()))
            else:
                st.warning("No active campaigns found. Create one first.")
                target_camp = None
        
        with col_bulk2:
            if 'Select' in edited_df.columns:
                selected_leads = edited_df[edited_df['Select'] == True]
            else:
                selected_leads = pd.DataFrame()

            if st.button(f"📥 Add {len(selected_leads)} to Campaign", type="primary", disabled=not target_camp or selected_leads.empty):
                camp_id = camp_options[target_camp]
                added_count = 0
                for _, row in selected_leads.iterrows():
                    # We need the ID from results_data or row['ID'] if it's there
                    # In display_list, we added "ID": r.get('id')
                    lead_id = row['ID']
                    if add_lead_to_campaign(camp_id, lead_id):
                        added_count += 1
                st.success(f"Successfully added {added_count} leads to '{target_camp}'!")
                time.sleep(1)
        
        st.divider()
        
        # 3. Page Level Chat
        render_page_chat(
            "Lead Results", 
            ResearcherAgent(), 
            json.dumps(display_list, indent=2)
        )

        st.info("💡 These leads are now saved in your CRM. You can find them in the 'CRM Dashboard'.")
