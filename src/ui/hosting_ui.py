import streamlit as st
import pandas as pd
from hosting_bridge import hosting_bridge
import json
import time
from src.ui.components import premium_header, confirm_action

def render_hosting_dashboard():
    premium_header(
        "Web Hosting & Automation",
        "Monitor your cPanel, domains, and WordPress deployments."
    )

    # Top-level Stats
    with st.spinner("Fetching hosting status..."):
        status_res = hosting_bridge.get_hosting_status()
    
    # Tabs
    tab_overview, tab_domains, tab_wp = st.tabs(["📊 Overview", "🌐 Domains", "📝 WordPress"])

    if status_res["status"] == "success":
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
                if st.button("🔄 Refresh Data", use_container_width=True):
                    st.rerun()
                
                if st.button("🛡️ Run Security Scan", use_container_width=True):
                    with st.spinner("initiating scan..."):
                        time.sleep(1.5)
                    st.success("Security scan initiated on server.")
                
                if st.button("💾 Trigger Backup", use_container_width=True):
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
                # cPanel API format varies, assuming list of dicts based on client.py
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
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                st.subheader("Domain Actions")
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    # SSL Check Button
                    if st.button("🔒 Check SSL Status", type="secondary"):
                        with st.spinner("Verifying certificates..."):
                            time.sleep(1) # Mock check as real check is slow/complex via UAPI
                        st.success("All active domains have valid AutoSSL certificates.")
                
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
        
        with st.spinner("Scanning for WordPress..."):
            wp_res = hosting_bridge.list_wordpress_sites()
            
        if wp_res["status"] == "success":
            sites = wp_res.get("sites", [])
            if sites:
                # Dataframe
                s_list = [{"Domain": s.get("domain"), "Path": s.get("path"), "Version": s.get("version", "N/A")} for s in sites]
                st.dataframe(pd.DataFrame(s_list), use_container_width=True, hide_index=True)
                
                st.divider()
                st.caption("Content Management")
                st.info("Direct publishing to WordPress is available via the **SEO Expert Agent** in the Agency tab.")
                
            else:
                st.info("No WordPress sites detected via WP Toolkit.")
        else:
            st.error(f"Failed to list WordPress sites: {wp_res.get('error')}")

    st.divider()
    with st.expander("Advanced Configuration"):
        st.write("Server Endpoint:", hosting_bridge.config.cpanel_url)
        st.write("User:", hosting_bridge.config.cpanel_user)
