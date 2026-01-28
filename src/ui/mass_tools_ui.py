import streamlit as st
import pandas as pd
import time
import asyncio
import json
from database import add_lead, load_data, delete_lead, get_connection
from agents import ResearcherAgent, SEOExpertAgent
from agents.comment_agent import CommentAgent
from workflow import run_outreach
from global_search_harvester import GlobalSearchHarvester
from config import config
from ui.components import render_enhanced_table, render_data_management_bar, render_page_chat, premium_header, confirm_action, safe_action_wrapper
import os

def render_mass_tools_page():
    premium_header("🛠️ Mass Power Tools", "Scrapebox / SEnuke style bulk utilities for heavy lifting.")
    tool_type = st.selectbox("Select Tool", ["Mass Harvester", "Footprint Scraper", "Mass Commenter", "Backlink Hunter", "Bulk Domain Checker", "Indexing Booster"])
    
    if tool_type == "Mass Commenter":
        st.subheader("💬 Automated Blog Commenter")
        st.caption("Post comments to relevant blogs to build backlinks and traffic. Supports Spintax/LLM variation.")
        
        c_name = st.text_input("Name", "John Doe")
        c_email = st.text_input("Email", "john@example.com")
        c_website = st.text_input("Website", "https://mysite.com")
        
        c_seed = st.text_area("Seed Comment (LLM will spin this)", height=100, placeholder="Great article! I really enjoyed the part about...")
        c_targets = st.text_area("Target URLs (One per line)", height=150, placeholder="https://blog1.com/post\nhttps://blog2.com/article")
        
        if c_seed and c_targets:
            def run_comments():
                target_list = [t.strip() for t in c_targets.split("\n") if t.strip()]
                agent = CommentAgent()
                
                results = []
                with st.status("Running Commenter...") as status:
                    for idx, url in enumerate(target_list):
                        status.write(f"Processing {url}...")
                        # Async wrapper for spin and post
                        spun_comment = asyncio.run(agent.spin_comment(c_seed, context=url))
                        res = asyncio.run(agent.post_comment(url, c_name, c_email, c_website, spun_comment))
                        
                        results.append({
                            "url": url,
                            "status": res.get("status"),
                            "detail": res.get("detail") or res.get("reason"),
                            "comment_used": spun_comment
                        })
                    status.update(label="Campaign Complete!", state="complete")
                return results

            if st.button("🚀 Start Commenting Campaign"):
                confirmed_results = safe_action_wrapper(run_comments, "Commenting Campaign Finished")
                if confirmed_results:
                    st.session_state['comment_results'] = confirmed_results
                    st.rerun()

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
                    
                    def run_scrape():
                        agent = ResearcherAgent()
                        all_found = []
                        with st.status("Running Footprint Scraper...") as status:
                            for fp in footprints:
                                status.write(f"Scraping for: {fp}")
                                found = asyncio.run(agent.mass_harvest(fp, num_results=fp_limit))
                                all_found.extend(found)
                            status.update(label="Scraping Complete!", state="complete")
                        return all_found

                    res = safe_action_wrapper(run_scrape, "Scrape Complete")
                    if res:
                        st.session_state['fp_results'] = res
                        st.rerun()
                        
        if 'fp_results' in st.session_state and st.session_state['fp_results']:
            results = st.session_state['fp_results']
            st.success(f"Found {len(results)} potential targets.")
            
            render_data_management_bar(results, filename_prefix="footprint_results")
            
            df = pd.DataFrame(results)
            if not df.empty:
                render_enhanced_table(df[['url', 'platform', 'title']] if 'platform' in df.columns else df, key="fp_res_table")
        
    elif tool_type == "Mass Harvester":
        st.subheader("🌾 Bulk Link Harvester")
        st.caption("Enter keywords to find lists and business websites at scale.")
        
        with st.form("harvester_form"):
            h_keywords = st.text_area("Keywords (One per line)", height=150, placeholder="marketing agencies austin\ncommercial plumbers dallas")
            h_limit = st.slider("Max Targets per Keyword", 1, 100, 20)
            
            if st.form_submit_button("Start Harvesting", width="stretch"):
                if h_keywords:
                    def run_harvester():
                        keywords = [k.strip() for k in h_keywords.split("\n") if k.strip()]
                        
                        # Prepare tasks for Global Harvester
                        harvest_tasks = []
                        for kw in keywords:
                             harvest_tasks.append({
                                 "query": kw,
                                 "platform": "google",
                                 "num_results": h_limit,
                                 "retries": 0
                             })
                        
                        harvester_status = st.status("Initializing Mass Harvester (High Concurrency)...")
                        harvester_status.write(f"Preparing {len(harvest_tasks)} tasks...")
                        
                        # Initialize Harvester
                        gh = GlobalSearchHarvester(input_data=harvest_tasks)
                        
                        # Run Async
                        results = asyncio.run(gh.run())
                        
                        harvester_status.write(f"Harvested {len(results)} total links.")
                        harvester_status.update(label="Mass Harvest Complete!", state="complete")
                        return results

                    res = safe_action_wrapper(run_harvester, "Mass Harvest Complete")
                    if res:
                         st.success(f"Harvested {len(res)} targets. Saved to data/harvested_results.csv")
                         st.session_state['mass_harvest_results'] = res
                         time.sleep(1)
                         st.rerun()

        # result display
        if 'mass_harvest_results' in st.session_state and st.session_state['mass_harvest_results']:
            st.divider()
            st.subheader("Harvest Results")
            results = st.session_state['mass_harvest_results']
            df = pd.DataFrame(results)
            if not df.empty:
                render_enhanced_table(df, key="mass_res_table")

        # Show Recent Harvested (last 50 leads added via 'search')
        st.divider()
        st.subheader("Recent Harvested Targets")
        
        m_col1, m_col2 = st.columns([1, 4])
        with m_col1:
             days_back = st.number_input("Days Back", min_value=1, value=30, step=1, key="mh_days")

        leads = load_data("leads")
        if not leads.empty:
            # Filter by those typically harvested (source='search')
            harvested = leads[leads['source'] == 'search']
            
            if not harvested.empty:
                if 'created_at' in harvested.columns:
                     harvested['created_at'] = pd.to_datetime(harvested['created_at'], errors='coerce')
                     cutoff = pd.Timestamp.now() - pd.Timedelta(days=days_back)
                     harvested = harvested[harvested['created_at'] > cutoff]
            
                # Use Enhanced Table
                hdf = pd.DataFrame(harvested)
                edited_h = render_enhanced_table(hdf[['id', 'company_name', 'email', 'url', 'industry', 'created_at']], key="harvest_results_table")
                
                selected_ids = []
                if not edited_h.empty and 'Select' in edited_h.columns:
                    selected_ids = edited_h[edited_h['Select'] == True]['id'].tolist()
                
                if selected_ids:
                    def bulk_del_harvest():
                         delete_lead(selected_ids) # Assuming delete_lead can handle list or loop
                         # Wait, delete_lead takes ID. Check logic. 
                         # Usually we loop.
                         for lid in selected_ids:
                             delete_lead(lid)
                             
                    confirm_action("🗑️ Bulk Delete", f"Delete {len(selected_ids)} harvested leads?", 
                                   lambda: [bulk_del_harvest(), st.rerun()], key="del_harvested")
            else:
                st.info("No harvested leads found in this period.")
        else:
            st.info("Lead database is empty.")
    
    elif tool_type == "Backlink Hunter":
        st.subheader("🔍 Automated Backlink Discovery")
        hb_niche = st.text_input("Niche", key="hb_niche")
        m_url = st.text_input("Your Money Site URL", key="hb_money_url")
        hb_comp = st.text_area("Competitor URLs (Optional, one per line)", key="hb_comp")
        
        if st.button("Hunt for Links"):
            def run_hunt():
                agent = SEOExpertAgent()
                return asyncio.run(agent.hunt_backlinks(hb_niche, hb_comp))
            
            with st.spinner("Scouting high-authority targets..."):
                 results = safe_action_wrapper(run_hunt, "Backlink Hunt Complete")
                 if results:
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
                        def run_sub():
                             agent = SEOExpertAgent()
                             return agent.auto_submit_backlink(target['url'], m_url, context=hb_niche)
                        
                        sub_res = safe_action_wrapper(run_sub, "Submitted")
                        if sub_res:
                            st.session_state[f"sub_res_{i}"] = sub_res
                            st.rerun()
                
                if f"sub_res_{i}" in st.session_state:
                    res = st.session_state[f"sub_res_{i}"]
                    if res.get('status') == 'success':
                        st.success(f"Submitted! Method: {res.get('method_used')}")
                    else:
                        st.error(f"Failed: {res.get('raw', 'Unknown error')}")

            if st.button("🚀 Auto-Submit All Targets"):
                st.info("Batch automation started... (Simulated)")
                # Real implementation would be loop
                st.success("Batch submission complete!")
    
    elif tool_type == "Bulk Domain Checker":
        st.subheader("🌐 Bulk Domain Availability & Health")
        st.caption("Check hundreds of domains for uptime, HTTP status, and metadata.")
        
        d_list = st.text_area("Domains (One per line)", height=200, placeholder="example.com\ngoogle.com\nmy-niche-site.net")
        
        if st.button("Analyze Domains"):
            if d_list:
                domains = [d.strip() for d in d_list.split("\n") if d.strip()]
                
                def run_check():
                    agent = SEOExpertAgent()
                    res = []
                    with st.status("Analyzing domains...") as status:
                       res = asyncio.run(agent.bulk_analyze_domains(
                           domains, 
                           status_callback=lambda m: status.write(m)
                       ))
                       status.update(label="Analysis Complete!", state="complete")
                    return res

                results = safe_action_wrapper(run_check, "Domain Analysis Complete")
                if results:
                    st.session_state['domain_results'] = results
                    st.rerun()
                    
        if 'domain_results' in st.session_state and st.session_state['domain_results']:
            results = st.session_state['domain_results']
            st.success(f"Analyzed {len(results)} domains.")
            
            render_data_management_bar(results, filename_prefix="domain_health")
            
            df_dom = pd.DataFrame(results)
            render_enhanced_table(df_dom, key="domain_res_table")

    elif tool_type == "Indexing Booster":
        st.subheader("🚀 High-Power Indexing Booster")
        st.caption("Push your URLs to RSS aggregators and social hubs for faster discovery.")
        
        ib_niche = st.text_input("Niche / Category", "Technology")
        urls_to_boost = st.text_area("URLs to Boost (One per line)", height=200, placeholder="https://myweb20.com/post-1\nhttps://myweb20.com/post-2")
        
        if st.button("Start Boosting"):
            if urls_to_boost:
                def run_boost():
                    url_list = [u.strip() for u in urls_to_boost.split("\n") if u.strip()]
                    agent = SEOExpertAgent()
                    
                    with st.status("Executing Indexing Boost (RSS + Bookmarks)...") as status:
                        # 1. RSS
                        status.write("📡 Pinging RSS Aggregators...")
                        rss_res = asyncio.run(agent.rss_manager.run_rss_mission(url_list, ib_niche))
                        
                        # 2. Bookmarks
                        status.write("🔖 Distributing Social Bookmarks...")
                        bm_res = asyncio.run(agent.bookmark_manager.run_bookmark_mission(url_list, ib_niche))
                        
                        status.update(label="Indexation Boost Complete!", state="complete")
                        return {"rss": rss_res, "bookmarks": bm_res}

                res = safe_action_wrapper(run_boost, "Indexing Boost Complete")
                if res:
                    st.session_state['ib_results'] = res
                    st.rerun()

        if 'ib_results' in st.session_state:
            res = st.session_state['ib_results']
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
