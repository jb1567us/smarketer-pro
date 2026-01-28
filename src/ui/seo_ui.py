import streamlit as st
import asyncio
import json
from agents import SEOExpertAgent
from database import save_creative_content

def render_seo_audit():
    """Renders the SEO Site Audit UI component."""
    st.header("📈 SEO Site Audit")
    url_to_audit = st.text_input("Website URL", placeholder="https://example.com")
    if st.button("Run Audit"):
        agent = SEOExpertAgent()
        with st.spinner("Analyzing site..."):
            report = asyncio.run(agent.audit_site(url_to_audit))
            st.session_state['last_seo_report'] = report
            st.rerun()

    if 'last_seo_report' in st.session_state:
        report = st.session_state['last_seo_report']
        st.json(report)
        
        if st.button("📝 Generate & Publish SEO Blog Post"):
            agent = SEOExpertAgent()
            with st.spinner("Drafting content and publishing..."):
                # Basic logic: Generate a title and content from the audit report
                title = f"SEO Analysis for {url_to_audit}"
                content = f"Site Audit Report:\n{json.dumps(report, indent=2)}"
                
                res = agent.publish_to_wordpress(title, content)
                if res["status"] == "success":
                    st.success("Successfully published to WordPress!")
                else:
                    st.error(f"Publishing failed: {res.get('error')}")

def render_keyword_research():
    """Renders the Keyword Research UI component."""
    st.header("🔑 Keyword Strategy")
    topic = st.text_input("Niche / Topic", placeholder="commercial plumbing repairs")
    if st.button("Research Keywords"):
        agent = SEOExpertAgent()
        with st.spinner("Finding high-intent keywords..."):
            report = agent.research_keywords(topic)
            st.json(report)

def render_link_wheel_builder():
    """Renders the Link Wheel Architect UI component."""
    st.header("🎡 Link Wheel Architect")
    st.caption("Design authority-funneling structures (SEnuke Style).")
    
    m_site = st.text_input("Money Site URL", placeholder="https://your-main-site.com")
    lw_niche = st.text_input("Niche", placeholder="Roofing")
    lw_strategy = st.selectbox("Strategy", ["Standard Wheel", "Double Link Wheel", "The Authority Funnel"])
    
    if st.button("Design Structure"):
        agent = SEOExpertAgent()
        with st.spinner("Calculating PageRank flow and tier structures..."):
            plan = agent.design_link_wheel(m_site, lw_niche, strategy=lw_strategy)
            st.session_state['last_lw_plan'] = plan
            st.rerun()

    if 'last_lw_plan' in st.session_state:
        plan = st.session_state['last_lw_plan']
        st.subheader(f"Strategy: {plan.get('strategy_name')}")
        
        # Render Mermaid from Agent Output
        st.info("Visualizing Link Graph...")
        mermaid_code = plan.get('diagram_instructions', "")
        if "graph " in mermaid_code:
            st.markdown(f"```mermaid\n{mermaid_code}\n```")
        else:
            # Fallback to a dynamic structure based on the plan
            st.markdown(f"```mermaid\ngraph TD\nMS[{m_site}]\n" + \
                "\n".join([f"T1_{i}[Tier 1 Property] --> MS" for i in range(3)]) + \
                "\n```")
        
        st.json(plan)
        
        if st.button("💾 Save Plan to Library"):
            save_creative_content(
                "SEO Expert", "json", 
                f"Link Wheel Plan: {plan.get('strategy_name')}", 
                json.dumps(plan)
            )
            st.toast("Plan saved to library!")
        
        st.divider()
        col_lw1, col_lw2 = st.columns([1, 1])
        with col_lw1:
            if st.button("🚀 Execute Autonomous Mission", type="primary"):
                with st.status("SEO Expert is executing Link Wheel mission...") as status:
                    agent = SEOExpertAgent()
                    results = asyncio.run(agent.run_link_wheel_mission(
                        m_site, 
                        lw_niche, 
                        strategy=lw_strategy,
                        status_callback=lambda m: status.write(m)
                    ))
                    st.session_state['last_lw_results'] = results
                    status.update(label="Link Wheel Execution & Indexation Boost Complete!", state="complete")
        
        if 'last_lw_results' in st.session_state:
            st.success("Mission Complete! Check the execution logs above.")
            with st.expander("View Execution Details"):
                results = st.session_state['last_lw_results']
                st.json(results)
                
                if 'indexing_boost' in results:
                    st.subheader("📡 Indexing Status")
                    ib = results['indexing_boost']
                    c_rss, c_bm = st.columns(2)
                    with c_rss:
                        st.write(f"✅ RSS Feeds: {len(ib.get('rss', {}).get('distribution_results', []))} Pings sent.")
                    with c_bm:
                        st.write(f"✅ Bookmarks: {len(ib.get('bookmarks', {}))} URLs processed.")

                if st.button("💾 Save Results to Library"):
                    save_creative_content(
                        "SEO Expert", "json", 
                        f"Link Wheel Results: {plan.get('strategy_name', 'Unnamed')}", 
                        json.dumps(st.session_state['last_lw_results'])
                    )
                    st.toast("Results saved to library!")
