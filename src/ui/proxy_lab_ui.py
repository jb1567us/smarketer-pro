import streamlit as st
import pandas as pd
import asyncio
import time
from database import get_best_proxies
from proxy_manager import proxy_manager
from config import config, update_config

def render_proxy_lab():
    """Renders the Proxy Lab UI component."""
    st.header("🌐 Proxy Harvester Lab")
    st.caption("Advanced ScrapeBox-style proxy management and elite harvesting.")

    # Dashboard Stats
    col1, col2, col3, col4 = st.columns(4)
    # Fetching counts from DB for accuracy
    elites = len(get_best_proxies(limit=1000, min_anonymity='elite'))
    standards = len(get_best_proxies(limit=1000, min_anonymity='standard'))
    
    col1.metric("Active Elite", elites)
    col2.metric("Active Standard", standards)
    col3.metric("Bad Blocked", len(proxy_manager.bad_proxies))
    col4.metric("Usage", "Enabled" if proxy_manager.enabled else "Disabled")
    
    st.divider()
    
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        st.subheader("Proxy Pool (Active)")
        all_best = get_best_proxies(limit=1000)
        if all_best:
            proxy_df = pd.DataFrame(all_best)
            # Ensure correct columns displayed
            display_cols = ["address", "anonymity", "latency"]
            existing_cols = [c for c in display_cols if c in proxy_df.columns]
            st.dataframe(proxy_df[existing_cols], hide_index=True, width="stretch")
        else:
            st.warning("No active proxies found. Start a harvest to populate the pool.")
        
    with col_side:
        st.subheader("Control Panel")
        
        # Concurrency Slider
        curr_conc = config.get("proxies", {}).get("harvest_concurrency", 50)
        new_conc = st.slider("Harvest Concurrency", min_value=1, max_value=400, value=curr_conc, step=10, help="Max concurrent connections for proxy harvesting.")
        
        if new_conc != curr_conc:
            update_config("proxies", "harvest_concurrency", new_conc)
            st.toast(f"Concurrency updated to {new_conc}!")
            time.sleep(0.5)
            st.rerun()

        # Check state change
        new_state = st.toggle("Enable Upstream Proxies", value=proxy_manager.enabled, key="proxy_toggle")
        
        if new_state != proxy_manager.enabled:
            if new_state:
                with st.spinner("Enabling proxies and refreshing... (Restarts SearXNG)"):
                    success, cx_msg = asyncio.run(proxy_manager.enable_proxies())
                    if success: 
                        st.success(cx_msg)
                        time.sleep(2)
                        st.rerun()
                    else: st.error(cx_msg)
            else:
                with st.spinner("Disabling proxies... (Restarts SearXNG)"):
                    success, cx_msg = asyncio.run(proxy_manager.disable_proxies())
                    if success: 
                        st.success(cx_msg)
                        time.sleep(2)
                        st.rerun()
                    else: st.error(cx_msg)
        
        st.divider()

        if st.button("🚀 Trigger Mass Harvest", width="stretch", type="primary"):
            success, msg = proxy_manager.start_harvest_bg()
            if success:
                st.success("🛰️ Background harvest initiated. Observe progress above.")
                time.sleep(1)
                st.rerun()
            else: 
                st.error(msg)
        
        if st.button("🧹 Clear Bad Proxies", width="stretch"):
            proxy_manager.bad_proxies.clear()
            st.success("Bad proxy list cleared.")
            st.rerun()

        with st.expander("📥 Import Custom Proxies"):
            import_text = st.text_area("Paste Proxy List (IP:Port)", height=100, placeholder="192.168.1.1:8080\n10.0.0.1:3128")
            if st.button("Import Peers"):
                if import_text:
                    count, new_p = asyncio.run(proxy_manager.import_proxies(import_text))
                    st.success(f"Imported {count} unique proxies.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("Paste some proxies first!")

        st.divider()
        
        st.markdown("#### 🔗 SearXNG Integration")
        if st.button("💉 Inject Proxies into SearXNG", width="stretch", help="Updates SearXNG settings.yml and restarts the container."):
            if not proxy_manager.proxies:
                st.error("No proxies to inject! Harvest some first.")
            else:
                with st.spinner("Injecting proxies and restarting SearXNG Docker container..."):
                    success, cx_msg = asyncio.run(proxy_manager.update_searxng_config())
                    if success:
                        st.success(cx_msg)
                    else:
                        st.error(cx_msg)
        
        st.divider()
        st.info("The Proxy Harvester automatically performs L3 anonymity checks and rotates every request by default.")
