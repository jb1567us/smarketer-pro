import streamlit as st
import pandas as pd

def render_pipeline_visualizer():
    st.header("📂 Pipeline Visualizer")
    st.caption("Track your leads through the automated marketing funnel.")
    
    # Mock Data for Columns
    stages = ["Discovery", "Enrichment", "Nurturing", "Conversion"]
    
    # Generate some mock leads
    mock_leads = [
        {"name": "TechFlow Inc", "value": "$12k", "stage": "Discovery", "agent": "Researcher"},
        {"name": "SaaS Bright", "value": "$5k", "stage": "Discovery", "agent": "Researcher"},
        {"name": "Growth Matrix", "value": "$25k", "stage": "Enrichment", "agent": "DataMiner"},
        {"name": "Cloud Nine", "value": "$8k", "stage": "Nurturing", "agent": "Copywriter"},
        {"name": "Nexus Corp", "value": "$15k", "stage": "Conversion", "agent": "SalesBot"},
    ]
    
    # Layout using columns for Kanban board effect
    cols = st.columns(len(stages))
    
    for i, stage in enumerate(stages):
        with cols[i]:
            st.markdown(f"""
                <div style="background: rgba(30,30,40,0.4); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); padding: 12px; border-radius: 12px; border-bottom: 4px solid #8B5CF6; border-top: 1px solid rgba(255,255,255,0.05); border-left: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px;">
                    <h4 style="margin: 0; font-size: 1rem; color: #C4B5FD; text-align: center;">{stage}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            stage_leads = [l for l in mock_leads if l['stage'] == stage]
            for lead in stage_leads:
                st.markdown(f"""
                    <div class="css-card" style="padding: 15px; margin-bottom: 12px; border: 1px solid rgba(255,255,255,0.08); background: rgba(20,20,30,0.6); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); transition: transform 0.2s ease, box-shadow 0.2s ease;">
                        <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 5px; color: #E2E8F0;">{lead['name']}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                            <span style="font-size: 0.85rem; color: #34D399; font-weight: 600;">{lead['value']}</span>
                            <div style="display: flex; align-items: center; gap: 4px; font-size: 0.7rem; background: rgba(139,92,246,0.15); color: #C4B5FD; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(139,92,246,0.3);">
                                🤖 {lead['agent']}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            if not stage_leads:
                st.markdown("""
                    <div style="text-align: center; padding: 40px 20px; opacity: 0.2; border: 1px dashed rgba(128,128,128,0.3); border-radius: 8px;">
                        <span style="font-size: 0.8rem;">No Leads in Stage</span>
                    </div>
                """, unsafe_allow_html=True)
