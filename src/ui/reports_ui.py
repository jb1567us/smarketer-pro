import streamlit as st
import pandas as pd
from reporting.pdf_generator import PDFReportGenerator
from database import get_connection

def render_reports_page():
    st.title("📄 Report Generator")
    st.markdown("Generate professional PDF reports for your clients or internal use.")

    with st.expander("ℹ️ How to use", expanded=False):
        st.info("Select a data source, configure the report details, and click 'Generate Report' to download a PDF.")

    # 1. Configuration
    col1, col2 = st.columns(2)
    with col1:
        report_title = st.text_input("Report Title", value="Campaign Outreach Summary")
        client_name = st.text_input("Client/Project Name", value="My Client")
    
    with col2:
        report_type = st.selectbox("Report Type", ["Campaign Summary", "Lead Status Report"])
        # In a real app, we might select specific campaigns here
        
    # 2. Data Selection
    st.subheader("Data Source")
    
    # Simple placeholder for data selection
    # In a full implementation, we'd query the DB based on selection
    
    conn = get_connection()
    # Fetch all leads for now as a demo
    # Ideally filter by campaign date etc.
    query = "SELECT first_name, last_name, company, email, status, campaign_id FROM leads LIMIT 50"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)
    
    if st.button("Generate Report", type="primary"):
        if df.empty:
            st.warning("No data available to generate report.")
        else:
            generator = PDFReportGenerator()
            # Convert DF to list of dicts
            data = df.to_dict('records')
            
            # Create a filename
            safe_title = "".join([c for c in report_title if c.isalnum() or c in (' ', '_')]).strip().replace(' ', '_')
            filename = f"report_{safe_title}_{client_name.replace(' ', '_')}.pdf"
            
            try:
                # We need to save it to a path or use a temp file
                # Streamlit runs on the server, so we generate there then allow download
                output_path = filename
                generator.generate_campaign_report(data, report_title, client_name, output_path)
                
                with open(output_path, "rb") as f:
                    st.download_button(
                        label="Download PDF",
                        data=f,
                        file_name=filename,
                        mime="application/pdf"
                    )
                st.success("Report generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating report: {e}")
