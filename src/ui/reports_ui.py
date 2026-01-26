
import pandas as pd
import altair as alt
import streamlit as st
import json
import os
from reporting.pdf_generator import PDFReportGenerator
from database import get_connection, get_all_campaigns
from ui.components import premium_header, safe_action_wrapper, confirm_action

PRESETS_FILE = "report_presets.json"

def load_presets():
    if os.path.exists(PRESETS_FILE):
        try:
             with open(PRESETS_FILE, 'r') as f:
                 return json.load(f)
        except: return {}
    return {}

def save_preset(name, config):
    presets = load_presets()
    presets[name] = config
    with open(PRESETS_FILE, 'w') as f:
        json.dump(presets, f)
    st.toast(f"Preset '{name}' saved!")

def render_reports_page():
    premium_header("📄 Report Generator", "Generate professional analytics and status reports.")

    with st.expander("ℹ️ Guide", expanded=False):
        st.info("Select data sources, visualize metrics, and export to PDF or CSV.")

    # Load Presets
    presets = load_presets()
    selected_preset_name = "None"
    
    if presets:
        c_ex, c_load = st.columns([3, 1])
        with c_ex:
             selected_preset_name = st.selectbox("Load Configuration Preset", ["None"] + list(presets.keys()))

    if selected_preset_name != "None":
        p_data = presets[selected_preset_name]
        default_title = p_data.get('title', "Campaign Summary")
        default_client = p_data.get('client', "My Client")
    else:
        default_title = "Campaign Outreach Summary"
        default_client = "My Company"

    # 1. Configuration
    with st.container(border=True):
        st.subheader("1. Configuration")
        col1, col2 = st.columns(2)
        with col1:
            report_title = st.text_input("Report Title", value=default_title)
            client_name = st.text_input("Client/Project Name", value=default_client)
        
        with col2:
            report_type = st.selectbox("Report Type", ["Campaign Summary", "Lead Status Report", "Comparative Analysis"])
            
            # Campaign Selector
            campaigns = get_all_campaigns()
            camp_opts = ["All Campaigns"] + [f"{c['id']}: {c['campaign_name']}" for c in campaigns]
            selected_camp = st.selectbox("Filter by Campaign", camp_opts)

        # Save Preset UI
        with st.expander("Save Current Config as Preset"):
            new_preset_name = st.text_input("Preset Name")
            if st.button("Save Preset"):
                if new_preset_name:
                    save_preset(new_preset_name, {
                        "title": report_title,
                        "client": client_name,
                        "type": report_type
                    })

    # 2. Data Selection & Analytics
    st.subheader("2. Analytics & Data")
    
    # Persistent Date Filter
    if 'report_days_back' not in st.session_state:
        st.session_state['report_days_back'] = 30
        
    d_col1, d_col2 = st.columns([1, 4])
    with d_col1:
         days_back = st.number_input("Days Back", min_value=1, value=st.session_state['report_days_back'])
         st.session_state['report_days_back'] = days_back
    
    conn = get_connection()
    
    # Build Query
    base_query = "SELECT first_name, last_name, company, email, status, campaign_id, created_at, source FROM leads"
    params = []
    conditions = []
    
    # Campaign Filter
    if selected_camp != "All Campaigns":
        cid = selected_camp.split(":")[0]
        conditions.append("campaign_id = ?")
        params.append(cid)
    
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    # No limit for analytics ideally, but cap for performance if needed
    base_query += " ORDER BY created_at DESC LIMIT 1000" 
    
    try:
        df = pd.read_sql_query(base_query, conn, params=params)
    except Exception as e:
        st.error(f"Data Fetch Error: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
    
    # Date Filter in Python
    if not df.empty and 'created_at' in df.columns:
         df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
         cutoff = pd.Timestamp.now() - pd.Timedelta(days=days_back)
         df = df[df['created_at'] > cutoff]

    if df.empty:
        st.warning("No data found for the selected criteria.")
    else:
        st.success(f"Loaded {len(df)} records.")
        
        # --- CHARTS ---
        st.markdown("### 📈 Visual Insights")
        c1, c2 = st.columns(2)
        
        with c1:
            st.caption("Leads by Status")
            if 'status' in df.columns:
                chart_status = alt.Chart(df).mark_bar().encode(
                    x='status',
                    y='count()',
                    color='status'
                ).interactive()
                st.altair_chart(chart_status, width="stretch")
                
        with c2:
            st.caption("Leads Over Time")
            if 'created_at' in df.columns:
                # Bin by day
                chart_time = alt.Chart(df).mark_line(point=True).encode(
                    x='yearmonthdate(created_at)',
                    y='count()',
                    tooltip=['yearmonthdate(created_at)', 'count()']
                ).interactive()
                st.altair_chart(chart_time, width="stretch")

        if report_type == "Comparative Analysis" and 'campaign_id' in df.columns:
            st.caption("Comparison by Campaign")
            st.bar_chart(df['campaign_id'].value_counts())

        # Data Preview
        with st.expander("Show Data Table", expanded=False):
            st.dataframe(df, width="stretch")

    st.divider()
    
    # 3. Actions / Export
    st.subheader("3. Actions")
    
    ac1, ac2, ac3 = st.columns(3)
    
    with ac1:
        if not df.empty:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download CSV",
                data=csv_data,
                file_name="report_data.csv",
                mime="text/csv",
                type="secondary",
                width="stretch"
            )
            
    with ac2:
         if st.button("📄 Generate PDF Report", type="primary", width="stretch", disabled=df.empty):
             def _gen_pdf():
                generator = PDFReportGenerator()
                data = df.to_dict('records')
                
                safe_title = "".join([c for c in report_title if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
                filename = f"report_{safe_title}_{client_name.replace(' ', '_')}.pdf"
                output_path = filename 
                
                # Check for charts to embed? (Advanced feature, skipping for now)
                
                generator.generate_campaign_report(data, report_title, client_name, output_path)
                return output_path, filename

             res = safe_action_wrapper(_gen_pdf, "PDF Generation")
             if res:
                 path, fname = res
                 with open(path, "rb") as f:
                     st.download_button(
                         label="⬇️ Download PDF",
                         data=f,
                         file_name=fname,
                         mime="application/pdf",
                         key="dl_pdf_btn"
                     )
                     
    with ac3:
        if st.button("✉️ Email Report", disabled=df.empty, width="stretch"):
            st.info("Email feature: In Production, this would send an email with the PDF attached to the configured client address.")
            # Mock success
            st.toast("Report queued for dispatch!", icon="📧")
