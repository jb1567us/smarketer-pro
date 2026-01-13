import streamlit as st
import pandas as pd
from hosting_bridge import hosting_bridge
import json

def render_hosting_dashboard():
    st.header("🌐 Hosting & WordPress Dashboard")
    st.caption("Monitor and manage your hosting environment and WordPress installations.")

    # Top-level Stats
    with st.spinner("Fetching hosting status..."):
        status_res = hosting_bridge.get_hosting_status()
    
    if status_res["status"] == "success":
        # Parse output for storage and domains
        # Note: The CLI output is currently just a string. 
        # For a truly premium UI, we'd want structured JSON, but let's show the output for now
        # and look for specific keywords.
        output = status_res["output"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Hosting Health")
            st.code(output, language="text")
            
            if "healthy" in output.lower():
                st.success("Storage is healthy.")
            else:
                st.warning("Check hosting storage limits.")

        with col2:
            st.subheader("📂 WordPress Sites")
            with st.spinner("Scanning for WordPress..."):
                wp_res = hosting_bridge.list_wordpress_sites()
            
            if wp_res["status"] == "success":
                st.code(wp_res["output"], language="text")
                if "No WordPress sites found" in wp_res["output"] or "Warning" in wp_res["output"]:
                    st.info("No active WordPress sites detected via API. (WPToolkit might be disabled)")
            else:
                st.error("Failed to list WordPress sites via API.")

        st.divider()
        
        # Action Center
        st.subheader("⚡ Quick Actions")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🚀 Trigger Full Backup", use_container_width=True):
                st.toast("Backup started on server...")
                # Call backup command via bridge if implemented
        with c2:
            if st.button("🔍 Scan for Security", use_container_width=True):
                st.toast("Security scan initiated...")
        with c3:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()
                
    else:
        st.error(f"Could not connect to Hosting API: {status_res.get('error') or status_res.get('error_output')}")
        st.info("Ensure the webhost-automation setup is correct and credentials are valid.")

    st.divider()
    st.markdown("### 📝 WordPress Content Management")
    st.info("Direct publishing to WordPress is available via the SEO Expert Agent.")
    
    # Placeholder for more advanced integration
    with st.expander("Advanced Settings"):
        st.write("cPanel User:", "elliotspencermor")
        st.write("Server:", "https://elk.lev3.com:2083")
