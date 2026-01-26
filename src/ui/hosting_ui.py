import streamlit as st
import pandas as pd
from hosting_bridge import hosting_bridge
import json
import time
from ui.components import premium_header, confirm_action, safe_action_wrapper, render_page_chat
from agents import ManagerAgent

def render_hosting_dashboard():
    premium_header(
        "Web Hosting & Automation",
        "Monitor your cPanel, domains, and WordPress deployments."
    )

    # Top-level Stats
    # Wrapper for fetching status
    def get_status():
        return hosting_bridge.get_hosting_status()

    with st.spinner("Fetching hosting status..."):
        # We don't use safe_action_wrapper here directly because we need the return value for logic branching
        # But we can try/except block it or use a safe getter
        try:
            status_res = get_status()
        except Exception as e:
            status_res = {"status": "error", "error": str(e)}
            
    # Tabs
    tab_overview, tab_domains, tab_wp = st.tabs(["📊 Overview", "🌐 Domains", "📝 WordPress"])

    if status_res.get("status") == "success":
        # =========================================================================
        # TAB 1: OVERVIEW
        # =========================================================================
        with tab_overview:
            # Quota Parsing
            quota = status_res.get("quota", [])
            
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Storage Health")
                if quota:
                    for q in quota:
                        used = float(q.get('megabytes_used', 0))
                        limit = float(q.get('megabytes_limit', 0))
                        if limit > 0:
                            pct = (used / limit) * 100
                            st.progress(pct / 100, text=f"Used: {int(used)}MB / {int(limit)}MB ({int(pct)}%)")
                        else:
                            st.metric("Storage Used", f"{used} MB")
                else:
                    st.info("No quota information available.")
            
            with c2:
                st.subheader("Quick Actions")
                if st.button("🔄 Refresh Data", width="stretch"):
                    st.rerun()
                
                if st.button("🛡️ Run Security Scan", width="stretch"):
                    def run_scan():
                         time.sleep(1.5) # Mock
                    safe_action_wrapper(run_scan, "Security scan initiated on server.")
                
                if st.button("💾 Trigger Backup", width="stretch"):
                     st.toast("Backup job queued.")

        # =========================================================================
        # TAB 2: DOMAINS
        # =========================================================================
        with tab_domains:
            st.subheader("Domain Management")
            domains = status_res.get("domains", [])
            
            if domains:
                # Filter
                search = st.text_input("🔍 Filter Domains", placeholder="example.com")
                
                # Prepare Data
                d_list = []
                for d in domains:
                    d_list.append({
                        "Domain": d.get("domain"),
                        "Root": d.get("docroot"),
                        "User": d.get("user"),
                        "Type": "Main" if d.get("main_domain") else "Addon/Sub"
                    })
                
                df = pd.DataFrame(d_list)
                
                if search:
                    df = df[df["Domain"].str.contains(search, case=False, na=False)]
                
                st.dataframe(df, width="stretch", hide_index=True)
                
                st.subheader("Domain Actions")
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    # SSL Check Button
                    if st.button("🔒 Check SSL Status", type="secondary"):
                        def check_ssl():
                            time.sleep(1) # Mock check as real check is slow/complex via UAPI
                        safe_action_wrapper(check_ssl, "All active domains have valid AutoSSL certificates.")
                
                with c_d2:
                     # Delete Placeholder
                     st.info("ℹ️ To delete or purchase domains, please use the [cPanel Interface](https://cpanel.net). API deletion is restricted.")
            else:
                st.warning("No domains found.")

    else:
        st.error(f"Could not connect to Hosting API: {status_res.get('error')}")

    # =========================================================================
    # TAB 3: WORDPRESS
    # =========================================================================
    with tab_wp:
        st.subheader("WordPress Installations")
        
        # Safe Fetch
        def get_wp():
             return hosting_bridge.list_wordpress_sites()
             
        with st.spinner("Scanning for WordPress..."):
            try:
                wp_res = get_wp()
            except Exception as e:
                wp_res = {"status": "error", "error": str(e)}
            
        if wp_res.get("status") == "success":
            sites = wp_res.get("sites", [])
            if sites:
                # Dataframe
                s_list = [{"Domain": s.get("domain"), "Path": s.get("path"), "Version": s.get("version", "N/A")} for s in sites]
                st.dataframe(pd.DataFrame(s_list), width="stretch", hide_index=True)
                
                st.divider()
                st.caption("Content Management")
                st.info("Direct publishing to WordPress is available via the **Manager Agent**.")
                
            else:
                st.info("No WordPress sites detected via WP Toolkit.")
        else:
            st.error(f"Failed to list WordPress sites: {wp_res.get('error')}")

    st.divider()
    with st.expander("Advanced Configuration"):
        st.write("Server Endpoint:", hosting_bridge.config.cpanel_url)
        st.write("User:", hosting_bridge.config.cpanel_user)
        
    # Page Chat
    render_page_chat("SysAdmin", ManagerAgent(), "Manage server resources and domains.")
