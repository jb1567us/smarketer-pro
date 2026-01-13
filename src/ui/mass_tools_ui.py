import streamlit as st
import pandas as pd
import time
import asyncio
import json
from database import add_lead, load_data
from agents import ResearcherAgent, SEOExpertAgent
from agents.comment_agent import CommentAgent
from workflow import run_outreach
from config import config
from ui.components import render_enhanced_table, render_data_management_bar, render_page_chat

def render_mass_tools_page():
    st.header("🛠️ Mass Power Tools")
    st.info("Scrapebox / SEnuke style bulk utilities.")
    tool_type = st.selectbox("Select Tool", ["Mass Harvester", "Footprint Scraper", "Mass Commenter", "Backlink Hunter", "Bulk Domain Checker", "Indexing Booster"])
    
    if tool_type == "Mass Commenter":
        st.subheader("💬 Automated Blog Commenter")
        st.caption("Post comments to relevant blogs to build backlinks and traffic. Supports Spintax/LLM variation.")
        
        with st.form("commenter_form"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                c_name = st.text_input("Name", "John Doe")
                c_email = st.text_input("Email", "john@example.com")
            with col_c2:
                c_website = st.text_input("Website", "https://mysite.com")
            
            c_seed = st.text_area("Seed Comment (LLM will spin this)", height=100, placeholder="Great article! I really enjoyed the part about...")
            c_targets = st.text_area("Target URLs (One per line)", height=150, placeholder="https://blog1.com/post\nhttps://blog2.com/article")
            
            if st.form_submit_button("Start Commenting Campaign"):
                if c_seed and c_targets:
                    target_list = [t.strip() for t in c_targets.split("\n") if t.strip()]
                    
                    from agents.comment_agent import CommentAgent
                    agent = CommentAgent()
                    
                    st.session_state['comment_results'] = []
                    with st.status("Running Commenter...") as status:
                        for idx, url in enumerate(target_list):
                            status.write(f"Processing {url}...")
                            # Spin
                            spun_comment = asyncio.run(agent.spin_comment(c_seed, context=url))
                            # Post
                            res = asyncio.run(agent.post_comment(url, c_name, c_email, c_website, spun_comment))
                            
                            st.session_state['comment_results'].append({
                                "url": url,
                                "status": res.get("status"),
                                "detail": res.get("detail") or res.get("reason"),
                                "comment_used": spun_comment
                            })
                        status.update(label="Campaign Complete!", state="complete")
                        
        if 'comment_results' in st.session_state and st.session_state['comment_results']:
            st.divider()
            st.subheader("Results")
            res_df = pd.DataFrame(st.session_state['comment_results'])
            
            render_data_management_bar(st.session_state['comment_results'], filename_prefix="comment_results")
            render_enhanced_table(res_df, key="comment_res_table")
    elif tool_type == "Footprint Scraper":
        st.subheader("🐾 Advanced Footprint Scraper")
        st.caption("Find specific targets using search operators (e.g. \"powered by wordpress\" keyword).")
        
        with st.form("footprint_form"):
            fp_inputs = st.text_area("Footprints (One per line)", height=150, placeholder="\"powered by wordpress\" digital marketing\n\"leave a reply\" tech blog")
            fp_limit = st.slider("Max Results per Footprint", 10, 500, 50)
            
            if st.form_submit_button("Start Scraping"):
                if fp_inputs:
                    footprints = [f.strip() for f in fp_inputs.split("\n") if f.strip()]
                    st.session_state['fp_results'] = []
                    
                    agent = ResearcherAgent()
                    with st.status("Running Footprint Scraper...") as status:
                        all_found = []
                        for fp in footprints:
                            status.write(f"Scraping for: {fp}")
                            # Run harvesting
                            found = asyncio.run(agent.mass_harvest(fp, num_results=fp_limit))
                            all_found.extend(found)
                        
                        st.session_state['fp_results'] = all_found
                        status.update(label="Scraping Complete!", state="complete")
                        
        if 'fp_results' in st.session_state and st.session_state['fp_results']:
            results = st.session_state['fp_results']
            st.success(f"Found {len(results)} potential targets.")
            
            # 1. Bar
            render_data_management_bar(results, filename_prefix="footprint_results")

            # 2. Table
            df = pd.DataFrame(results)
            if not df.empty:
                render_enhanced_table(df[['url', 'platform', 'title']] if 'platform' in df.columns else df, key="fp_res_table")
        
    elif tool_type == "Mass Harvester":
        st.subheader("🌾 Bulk Link Harvester")
        st.caption("Enter keywords to find lists and business websites at scale.")
        
        with st.form("harvester_form"):
            h_keywords = st.text_area("Keywords (One per line)", height=150, placeholder="marketing agencies austin\ncommercial plumbers dallas")
            h_limit = st.slider("Max Targets per Keyword", 1, 100, 20)
            
            if st.form_submit_button("Start Harvesting", use_container_width=True):
                if h_keywords:
                    keywords = [k.strip() for k in h_keywords.split("\n") if k.strip()]
                    st.session_state['harvest_results'] = []
                    
                    harvester_status = st.status("Harvesting in progress...")
                    agent = ResearcherAgent()
                    
                    for kw in keywords:
                        harvester_status.write(f"Scouting for: {kw}")
                        # Use a simplified search for speed in harvester
                        res = asyncio.run(run_outreach(
                            kw, 
                            max_results=h_limit,
                            status_callback=lambda m: harvester_status.write(f"  > {m}")
                        ))
                        # Results are saved to leads.db by run_outreach, 
                        # but we want to show them here too or just fetch recent ones
                    
                    harvester_status.update(label="Harvesting Complete!", state="complete")
                    st.success(f"Harvested targets for {len(keywords)} keywords. Check CRM Dashboard for new leads.")
                    st.rerun()
        
        # Show Recent Harvested (last 50 leads added via 'search')
        st.divider()
        st.subheader("Recent Harvested Targets")
        leads = load_data("leads")
        if not leads.empty:
            # Filter by those typically harvested (source='search')
            harvested = leads[leads['source'] == 'search'].tail(50)
            if not harvested.empty:
                st.dataframe(harvested[['company_name', 'email', 'url', 'industry']], hide_index=True)
            else:
                st.info("No harvested leads found yet.")
        else:
            st.info("Lead database is empty.")
    
    elif tool_type == "Backlink Hunter":
        st.subheader("🔍 Automated Backlink Discovery")
        hb_niche = st.text_input("Niche", key="hb_niche")
        m_url = st.text_input("Your Money Site URL", key="hb_money_url")
        hb_comp = st.text_area("Competitor URLs (Optional, one per line)", key="hb_comp")
        
        if st.button("Hunt for Links"):
            agent = SEOExpertAgent()
            with st.spinner("Scouting high-authority targets..."):
                results = asyncio.run(agent.hunt_backlinks(hb_niche, hb_comp))
                st.session_state['last_hunt_results'] = results
                st.rerun()
        if 'last_hunt_results' in st.session_state:
            results = st.session_state['last_hunt_results']
            st.write(f"Found {len(results.get('targets', []))} targets.")
            
            # Display targets in a grid/list
            for i, target in enumerate(results.get('targets', [])):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{target['url']}** ({target['type']})")
                with col2:
                    st.caption(f"Auth: {target['authority_est']}")
                with col3:
                    if st.button("Auto-Submit", key=f"submit_{i}"):
                        agent = SEOExpertAgent()
                        with st.spinner(f"Submitting to {target['url']}..."):
                            submission_res = agent.auto_submit_backlink(target['url'], m_url, context=hb_niche)
                            st.session_state[f"sub_res_{i}"] = submission_res
                
                if f"sub_res_{i}" in st.session_state:
                    res = st.session_state[f"sub_res_{i}"]
                    if res.get('status') == 'success':
                        st.success(f"Submitted! Method: {res.get('method_used')}")
                    elif res.get('status') == 'task_created':
                        st.info(f"📍 {res.get('method_used')}: Check 'Tasks' page.")
                    else:
                        st.error(f"Failed: {res.get('raw', 'Unknown error')}")
            if st.button("🚀 Auto-Submit All Targets"):
                st.info("Batch automation started... (Simulated)")
                agent = SEOExpertAgent()
                for target in results.get('targets', []):
                    st.write(f"Processing {target['url']}...")
                    # In a real app, we'd do this async or with a progress bar
                    agent.auto_submit_backlink(target['url'], m_url, context=hb_niche)
                st.success("Batch submission complete!")
    
    elif tool_type == "Bulk Domain Checker":
        st.subheader("🌐 Bulk Domain Availability & Health")
        st.caption("Check hundreds of domains for uptime, HTTP status, and metadata.")
        
        d_list = st.text_area("Domains (One per line)", height=200, placeholder="example.com\ngoogle.com\nmy-niche-site.net")
        
        if st.button("Analyze Domains"):
            if d_list:
                domains = [d.strip() for d in d_list.split("\n") if d.strip()]
                agent = SEOExpertAgent()
                
                st.session_state['domain_results'] = []
                
                with st.status("Analyzing domains...") as status:
                   results = asyncio.run(agent.bulk_analyze_domains(
                       domains, 
                       status_callback=lambda m: status.write(m)
                   ))
                   st.session_state['domain_results'] = results
                   status.update(label="Analysis Complete!", state="complete")
                
                st.rerun()
        if 'domain_results' in st.session_state and st.session_state['domain_results']:
            results = st.session_state['domain_results']
            st.success(f"Analyzed {len(results)} domains.")
            
            # 1. Bar
            render_data_management_bar(results, filename_prefix="domain_health")

            # 2. Table
            df_dom = pd.DataFrame(results)
            render_enhanced_table(df_dom, key="domain_res_table")
    elif tool_type == "Indexing Booster":
        st.subheader("🚀 High-Power Indexing Booster")
        st.caption("Push your URLs to RSS aggregators and social hubs for faster discovery.")
        
        ib_niche = st.text_input("Niche / Category", "Technology")
        urls_to_boost = st.text_area("URLs to Boost (One per line)", height=200, placeholder="https://myweb20.com/post-1\nhttps://myweb20.com/post-2")
        
        if st.button("Start Boosting"):
            if urls_to_boost:
                url_list = [u.strip() for u in urls_to_boost.split("\n") if u.strip()]
                agent = SEOExpertAgent()
                
                with st.status("Executing Indexing Boost (RSS + Bookmarks)...") as status:
                    # 1. RSS
                    status.write("📡 Pinging RSS Aggregators...")
                    rss_res = asyncio.run(agent.rss_manager.run_rss_mission(url_list, ib_niche))
                    
                    # 2. Bookmarks
                    status.write("🔖 Distributing Social Bookmarks...")
                    bm_res = asyncio.run(agent.bookmark_manager.run_bookmark_mission(url_list, ib_niche))
                    
                    st.session_state['ib_results'] = {"rss": rss_res, "bookmarks": bm_res}
                    status.update(label="Indexation Boost Complete!", state="complete")
                st.rerun()
        if 'ib_results' in st.session_state:
            res = st.session_state['ib_results']
            st.success("Indexing Boost Complete!")
            col1, col2 = st.columns(2)
            with col1:
                st.write("**RSS Distribution:**")
                st.json(res['rss'].get('distribution_results', []))
            with col2:
                st.write("**Social Bookmarks:**")
                st.json(res['bookmarks'])

    # 3. Page Level Chat
    render_page_chat(
        "Mass Tools Analysis", 
        ResearcherAgent(), 
        "Bulk Utility Results for Mass Marketing"
    )

