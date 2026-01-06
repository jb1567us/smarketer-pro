
import streamlit as st
import asyncio
from agents.account_creator import AccountCreatorAgent
from config import get_cpanel_config, config

from proxy_manager import proxy_manager

def render_account_creator_ui():
    st.header("🤖 Automated Account Creator")
    st.caption("Create verified accounts on any platform using AI-driven form filling and cPanel email automation.")
    
    # 1. Config Check
    cpanel_conf = get_cpanel_config()
    if not cpanel_conf or not cpanel_conf.get('url'):
        st.error("cPanel is not configured. Please check your .env or config.yaml.")
        return

    # 2. Input Form
    col1, col2 = st.columns(2)
    with col1:
        platform_name = st.text_input("Platform Name", placeholder="e.g. Facebook")
        username = st.text_input("Desired Username (Optional)")

    with col2:
        reg_url = st.text_input("Registration URL", placeholder="https://facebook.com/r.php")
        
        # Proxy Section
        use_auto_proxy = st.checkbox("Auto-Select Proxy from Pool", value=True)
        if use_auto_proxy:
            st.info(f"Pool Size: {len(proxy_manager.proxies)} elites.")
            proxy_str = None # Will fetch on click
        else:
            proxy_str = st.text_input("Manual Proxy", placeholder="http://user:pass@host:port")

    # 3. Action
    if st.button("🚀 Create Account", type="primary"):
        if not platform_name or not reg_url:
            st.error("Please provide Platform Name and Registration URL.")
            return

        # Fetch Proxy if Auto
        if use_auto_proxy:
            proxy_str = proxy_manager.get_proxy()
            if not proxy_str:
                with st.spinner("Proxy pool empty. Harvesting fresh proxies..."):
                     asyncio.run(proxy_manager.fetch_proxies())
                     proxy_str = proxy_manager.get_proxy()
                
                if not proxy_str:
                    st.error("Failed to find a working proxy. Please check Proxy Lab.")
                    return
            st.success(f"Using Proxy: {proxy_str}")
            
        st.info("Starting Account Creation Agent...")
        
        # Prepare Agent
        # Update config with domain if explicitly set in UI? (Maybe later)
        agent = AccountCreatorAgent(cpanel_conf)
        
        details = {}
        if username:
            details['username'] = username
            
        proxy = None
        if proxy_str:
            # Parse proxy string simply
            proxy = {"server": proxy_str} 
            # If user/pass handling needed, user should format string or we parse
            
        with st.status("Agent Working...", expanded=True) as status:
            st.write("Initializing...")
            
            # Run async function
            async def run_agent():
                return await agent.create_account(
                    platform_name, 
                    reg_url, 
                    account_details=details,
                    proxy=proxy
                )
            
            try:
                result = asyncio.run(run_agent())
                status.update(label="Complete!", state="complete", expanded=False)
                
                if "verified" in str(result).lower():
                    st.success(f"Result: {result}")
                else:
                    st.warning(f"Result: {result}")
                    
            except Exception as e:
                st.error(f"Agent failed: {e}")

    st.divider()
    
    # 4. Managed Accounts View
    st.subheader("Managed Accounts")
    from database import get_managed_accounts
    accounts = get_managed_accounts()
    
    if accounts:
        st.dataframe(
            accounts, 
            column_config={
                "metadata": st.column_config.JsonColumn("Metadata")
            },
            use_container_width=True
        )
    else:
        st.info("No accounts created yet.")
