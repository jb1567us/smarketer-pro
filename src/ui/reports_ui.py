import pandas as pd
from reporting.pdf_generator import PDFReportGenerator
from database import get_connection, get_all_campaigns
from ui.components import premium_header, safe_action_wrapper, confirm_action
import json
import os

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
    premium_header("📄 Report Generator", "Generate professional PDF reports for your clients or internal use.")

    with st.expander("ℹ️ How to use", expanded=False):
        st.info("Select a data source, configure the report details, and click 'Generate Report' to download a PDF.")

    # Load Presets
    presets = load_presets()
    if presets:
        selected_preset = st.selectbox("Load Preset", ["None"] + list(presets.keys()))
        if selected_preset != "None":
            p_data = presets[selected_preset]
            # Use session state to pre-fill if needed, or just set defaults below
            # For simplicity, we'll just use variables
            default_title = p_data.get('title', "Campaign Summary")
            default_client = p_data.get('client', "My Client")
        else:
            default_title = "Campaign Outreach Summary"
            default_client = "My Client"
    else:
        default_title = "Campaign Outreach Summary"
        default_client = "My Client"

    # 1. Configuration
    with st.container(border=True):
        st.subheader("1. Configuration")
        col1, col2 = st.columns(2)
        with col1:
            report_title = st.text_input("Report Title", value=default_title)
            client_name = st.text_input("Client/Project Name", value=default_client)
        
        with col2:
            report_type = st.selectbox("Report Type", ["Campaign Summary", "Lead Status Report"])
            
            # Campaign Selector
            campaigns = get_all_campaigns()
            camp_opts = ["All Campaigns"] + [f"{c['id']}: {c['campaign_name']}" for c in campaigns]
            selected_camp = st.selectbox("Filter by Campaign", camp_opts)

        # Save Preset UI
        with st.expander("Save Configuration as Preset"):
            new_preset_name = st.text_input("Preset Name")
            if st.button("Save Preset"):
                if new_preset_name:
                    save_preset(new_preset_name, {
                        "title": report_title,
                        "client": client_name,
                        "type": report_type
                    })
        
    # 2. Data Selection
    st.subheader("2. Data & Preview")
    
    # Date Range
    d_col1, d_col2 = st.columns([1, 4])
    with d_col1:
         days_back = st.number_input("Days Back", min_value=1, value=30)
    
    conn = get_connection()
    
    # Build Query
    base_query = "SELECT first_name, last_name, company, email, status, campaign_id, created_at FROM leads"
    params = []
    conditions = []
    
    # Campaign Filter
    if selected_camp != "All Campaigns":
        cid = selected_camp.split(":")[0]
        conditions.append("campaign_id = ?")
        params.append(cid)
    
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " ORDER BY created_at DESC LIMIT 200" # Cap for reports
    
    df = pd.read_sql_query(base_query, conn, params=params)
    conn.close()
    
    # Date Filter in Python (sqlite dates can be messy)
    if not df.empty and 'created_at' in df.columns:
         df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
         cutoff = pd.Timestamp.now() - pd.Timedelta(days=days_back)
         df = df[df['created_at'] > cutoff]

    st.caption(f"Found {len(df)} records matching criteria.")
    st.dataframe(df, use_container_width=True, height=200)
    
    st.divider()
    
    if st.button("Generate & Download Report", type="primary"):
        if df.empty:
            st.warning("No data matching your filters.")
        else:
            def _gen():
                generator = PDFReportGenerator()
                data = df.to_dict('records')
                
                safe_title = "".join([c for c in report_title if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
                filename = f"report_{safe_title}_{client_name.replace(' ', '_')}.pdf"
                output_path = filename # in root/cwd
                
                generator.generate_campaign_report(data, report_title, client_name, output_path)
                return output_path, filename

            res = safe_action_wrapper(_gen, "Report Generation")
            
            if res:
                path, fname = res
                with open(path, "rb") as f:
                    st.download_button(
                        label="⬇️ Click to Download PDF",
                        data=f,
                        file_name=fname,
                        mime="application/pdf"
                    )
                # Cleanup? Maybe keep for a bit.
