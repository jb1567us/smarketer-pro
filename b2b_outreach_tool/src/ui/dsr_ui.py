import streamlit as st
import pandas as pd
import asyncio
import json
from dsr_manager import DSRManager
from agents import WordPressAgent
from database import (
    get_all_campaigns, get_campaign_leads, get_wp_sites, get_connection
)

def render_dsr_page():
    st.header("💼 Digital Sales Room (DSR) Manager")
    st.caption("Create, personalize, and deploy microsites for your high-value leads.")

    # Initialize Manager
    dsr_manager = DSRManager()

    tab_gen, tab_manage, tab_sites = st.tabs(["✨ Generator", "📂 Manage DSRs", "🌐 WordPress Sites"])

    with tab_gen:
        st.subheader("Generate New DSR")
        
        # 1. Select Campaign
        campaigns = get_all_campaigns()
        if not campaigns:
            st.info("No campaigns found. Create a campaign first.")
            return

        camp_options = {f"{c['name']} (ID: {c['id']})": c['id'] for c in campaigns}
        selected_camp_label = st.selectbox("Select Campaign", list(camp_options.keys()))
        selected_camp_id = camp_options[selected_camp_label]

        # 2. Select Lead
        leads = get_campaign_leads(selected_camp_id)
        if not leads:
            st.warning("No leads found in this campaign.")
        else:
            lead_options = {f"{l['company_name']} - {l['contact_person']} ({l['email']})": l for l in leads}
            selected_lead_label = st.selectbox("Select Target Lead", list(lead_options.keys()))
            selected_lead = lead_options[selected_lead_label]

            st.divider()
            
            # Preview Lead Context
            with st.expander("View Lead Context"):
                st.json(selected_lead)

            if st.button("🚀 Generate DSR Content", type="primary"):
                with st.spinner("AI is crafting copy and designing assets..."):
                    # Run generation
                    result = asyncio.run(dsr_manager.generate_dsr_for_lead(selected_camp_id, selected_lead))
                    
                    st.success("DSR Content Generated!")
                    st.session_state['last_dsr_generated'] = result
                    
    # Display Generated Result
    if 'last_dsr_generated' in st.session_state:
        with tab_gen:
            res = st.session_state['last_dsr_generated']
            st.divider()
            st.subheader(f"Draft: {res['content']['copy'].get('headline', 'Untitled')}")
            
            c1, c2 = st.columns([1, 1])
            with c1:
                st.image(res['content']['hero_image'], caption="AI Generated Hero Image")
            with c2:
                st.markdown(f"**Headline:** {res['content']['copy'].get('headline')}")
                st.markdown(f"**Sub:** {res['content']['copy'].get('sub_headline')}")
                st.caption("Benefits:")
                for b in res['content']['copy'].get('benefits', []):
                    st.markdown(f"- {b}")
            
            st.info("Content saved as Draft. Go to 'Manage DSRs' to deploy.")

    with tab_manage:
        st.subheader("Manage & Deploy")
        
        # Load DSRs directly from DB for now
        conn = get_connection()
        dsrs = pd.read_sql_query("SELECT * FROM digital_sales_rooms ORDER BY created_at DESC", conn)
        conn.close()

        if dsrs.empty:
            st.info("No DSRs created yet.")
        else:
            # Filters
            status_filter = st.selectbox("Filter Status", ["All", "draft", "published"], index=0)
            if status_filter != "All":
                dsrs = dsrs[dsrs['status'] == status_filter]

            for index, row in dsrs.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1.5])
                    with c1:
                        st.markdown(f"**{row['title']}**")
                        st.caption(f"Lead ID: {row['lead_id']} | Campaign ID: {row['campaign_id']}")
                    with c2:
                        color = "green" if row['status'] == 'published' else "gray"
                        st.markdown(f":{color}[{row['status'].upper()}]")
                    with c3:
                        if row['status'] == 'published':
                            st.link_button("🔗 Visit Page", row['wp_url'])
                        else:
                            # Deploy Action
                            wp_sites = get_wp_sites()
                            if not wp_sites:
                                st.error("No WP Sites connected.")
                            else:
                                site_opts = {s['url']: s for s in wp_sites}
                                sel_site = st.selectbox("Deploy to:", list(site_opts.keys()), key=f"site_{row['id']}")
                                
                                if st.button("🚀 Deploy", key=f"deploy_{row['id']}"):
                                    site_data = site_opts[sel_site]
                                    wp_agent = WordPressAgent()
                                    with st.spinner(f"Deploying to {sel_site}..."):
                                        res = asyncio.run(dsr_manager.deploy_dsr(row['id'], wp_agent, site_data['id'], site_data))
                                        
                                        if "success" in res:
                                            st.success(f"Published! [View Link]({res['url']})")
                                            st.balloons()
                                            # Refresh manually
                                            # st.rerun() 
                                        else:
                                            st.error(f"Deployment Failed: {res.get('error')}")

    with tab_sites:
        from ui.styles import load_css # Just to ensure env
        # Reuse existing WP logic or just simple list
        st.subheader("Connected WordPress Sites")
        st.info("Manage your deployment targets here (credentials stored locally).")
        
        sites = get_wp_sites()
        if sites:
            st.dataframe(pd.DataFrame(sites)[['url', 'username', 'id']], hide_index=True)
        else:
            st.warning("No sites connected. Go to user settings or add one here.")
            
