import streamlit as st
import json
import pandas as pd
from database import get_campaign_analytics, get_daily_engagement
from agents import CopywriterAgent, ManagerAgent
from ui.components import render_page_chat

def render_analytics_page():
    """Renders the Performance Reports / Analytics UI component."""
    st.header("📊 Performance Reports")
    st.caption("Detailed analytics and AI-powered campaign optimization.")
    
    analytics = get_campaign_analytics()
    
    # Top-level metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Leads Contacted", analytics['leads_contacted'])
    m2.metric("Emails Sent", analytics['sent'])
    m3.metric("Opened", analytics['open'])
    m4.metric("Clicked", analytics['click'])
    
    st.divider()
    
    # Funnel Chart
    st.subheader("Conversion Funnel")
    funnel_data = {
        "Stage": ["Sent", "Opened", "Clicked"],
        "Count": [analytics['sent'], analytics['open'], analytics['click']]
    }
    st.bar_chart(funnel_data, x="Stage", y="Count")
    
    # Engagement Timeline
    st.subheader(" Engagement Over Time (Last 30 Days)")
    daily_data = get_daily_engagement(days=30)
    
    # Transform for chart (list of dicts)
    chart_rows = []
    for day, metrics in daily_data.items():
        row = {'Day': day, 'Sent': metrics['sent'], 'Opens': metrics['open'], 'Clicks': metrics['click']}
        chart_rows.append(row)
        
    if chart_rows:
        st.line_chart(chart_rows, x="Day", y=["Sent", "Opens", "Clicks"])
    else:
        st.info("No activity recorded yet.")

    st.divider()
    st.subheader("💡 AI Optimization Insights")
    
    # Simulated Campaign Data for Optimization
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        st.info("Analyzing Campaign: **'SaaS Founders Outreach Q3'**")
        current_stats = {"open_rate": 0.18, "click_rate": 0.02} # Simulated low performance
        st.metric("Open Rate", "18%", "-7% vs avg", delta_color="inverse")
        st.metric("Click Rate", "2.0%", "-3% vs avg", delta_color="inverse")
        
    with col_opt2:
        if st.button("✨ Auto-Optimize Campaign"):
            agent = CopywriterAgent()
            
            # Mock current copy
            current_copy = {
                "subject": "Quick question",
                "body": "Hi there, I saw your profile and thought..."
            }
            
            with st.spinner("AI is analyzing performance and rewriting copy..."):
                # Call the optimization method
                res = agent.optimize_campaign(current_copy, current_stats)
                
                st.success("Optimization Complete!")
                st.json(res)
                if "optimized_variants" in res:
                    st.subheader("Suggested Variants:")
                    for v in res['optimized_variants']:
                        st.code(v, language="text")

    # 3. Page Level Chat
    render_page_chat(
        "Campaign Analytics", 
        ManagerAgent(), 
        json.dumps(analytics, indent=2)
    )
