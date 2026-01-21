
import streamlit as st
import asyncio
import json
import pandas as pd
from agents.account_creator import AccountCreatorAgent
from config import get_cpanel_config, config
from proxy_manager import proxy_manager
from ui.components import render_enhanced_table, render_data_management_bar, render_page_chat, premium_header, safe_action_wrapper, confirm_action
from agents import ManagerAgent
import time
from database import get_managed_accounts, delete_managed_account, update_managed_account

def render_account_creator_ui():
    premium_header("🤖 Automated Account Creator", "Create verified accounts on any platform using AI-driven form filling.")
    
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
    st.markdown("### 🚀 Launch Creation")
    create_col1, create_col2 = st.columns([1, 4])
    with create_col1:
        if st.button("Start Agent", type="primary", use_container_width=True):
            if not platform_name or not reg_url:
                st.error("Missing Platform/URL.")
            else:
                 def _run_creation():
                    # Fetch Proxy if Auto
                    p_str = proxy_str
                    if use_auto_proxy:
                        p_str = proxy_manager.get_proxy()
                        if not p_str:
                             asyncio.run(proxy_manager.fetch_proxies())
                             p_str = proxy_manager.get_proxy()
                    
                    if not p_str and use_auto_proxy: raise Exception("No proxies available.")
                    
                    agent = AccountCreatorAgent(cpanel_conf)
                    details = {'username': username} if username else {}
                    t_proxy = {"server": p_str} if p_str else None
                    
                    st.info(f"Agent Active. Target: {platform_name}")
                    return asyncio.run(agent.create_account(platform_name, reg_url, details, t_proxy))

                 res = safe_action_wrapper(_run_creation, "Account Creation")
                 if res:
                     st.balloons()
                     st.success(f"Outcome: {res}")

    st.divider()
    
    st.divider()
    
    # 4. Manual Interventions
    st.subheader("⚠️ Manual Intervention Needed")
    from database import get_registration_tasks, delete_registration_task, save_registration_macro, mark_registration_task_completed
    from utils.browser_manager import BrowserManager
    
    manual_tasks = get_registration_tasks(status='pending')
    if manual_tasks:
        for task in manual_tasks:
            with st.expander(f"Task: {task['platform']} - {task['url']}", expanded=True):
                col_t1, col_t2 = st.columns([3, 1])
                with col_t1:
                    st.write(f"**Registration URL:** {task['url']}")
                    # Parse details to show error if present
                    try:
                        details_data = json.loads(task['details'])
                        if 'error' in details_data:
                            st.error(f"Reason: {details_data['error']}")
                        st.write(f"**Details:** {task['details']}")
                    except:
                        st.write(f"**Details:** {task['details']}")
                with col_t2:
                    if st.button("🔴 Record Macro", key=f"rec_{task['id']}"):
                        # Recording Logic
                        async def record_macro_flow(platform, url):
                            bm = BrowserManager(session_id=f"record_{platform}")
                            page = await bm.launch(headless=False)
                            await page.goto(url)
                            await bm.start_recording()
                            
                            st.info("🔴 **RECORDING ACTIVE**")
                            st.write("Perform your actions in the opened browser window.")
                            st.warning("Once finished, **CLOSE THE BROWSER WINDOW** to save the macro.")
                            
                            # Use a placeholder for status
                            status_area = st.empty()
                            
                            while True:
                                await asyncio.sleep(0.5)
                                if bm.page.is_closed():
                                    status_area.success("Browser closed. Processing events...")
                                    break
                            
                            events = await bm.stop_recording()
                            if events:
                                save_registration_macro(platform, events)
                                mark_registration_task_completed(task['id'])
                                st.success(f"Macro saved for {platform}!")
                            else:
                                st.error("No events captured.")
                            
                            await bm.close()

                        asyncio.run(record_macro_flow(task['platform'], task['url']))
                        st.rerun()
                    
                    if st.button("🗑️ Delete Task", key=f"del_{task['id']}"):
                        delete_registration_task(task['id'])
                        st.rerun()
    else:
        st.info("No manual tasks pending.")

    st.divider()
    
    # 5. Managed Accounts View
    # 5. Managed Accounts View
    st.subheader("Managed Accounts")
    
    # Filters
    f_col1, f_col2 = st.columns([1, 4])
    with f_col1:
        f_days = st.number_input("Days Back", min_value=1, value=30, key="ma_days")
    
    accounts = get_managed_accounts()
    
    if accounts:
        # Date Filter
        adf = pd.DataFrame(accounts)
        if 'created_at' in adf.columns:
             adf['created_at'] = pd.to_datetime(adf['created_at'], errors='coerce')
             cutoff = pd.Timestamp.now() - pd.Timedelta(days=f_days)
             adf = adf[adf['created_at'] > cutoff]
        
        # Edit Handler
        if 'edit_acc_id' not in st.session_state: st.session_state['edit_acc_id'] = None
        
        if not adf.empty:
            edited_df = render_enhanced_table(adf, key="managed_accounts_table")
            
            # Action Buttons
            sel_rows = edited_df[edited_df['Select'] == True]
            if not sel_rows.empty:
                s_col1, s_col2 = st.columns(2)
                with s_col1:
                    # Edit Logic (Single Select)
                    if len(sel_rows) == 1:
                         if st.button("✏️ Edit Selected"):
                             st.session_state['edit_acc_id'] = sel_rows.iloc[0]['id']
                             st.rerun()
                with s_col2:
                    # Delete Logic
                    selected_ids = sel_rows['id'].tolist()
                    confirm_action("🗑️ Bulk Delete", f"Delete {len(selected_ids)} accounts?", 
                                   lambda: [delete_managed_account(aid) for aid in selected_ids], key="del_accs")

        # Edit Form
        if st.session_state['edit_acc_id']:
             with st.form("edit_acc_form"):
                 st.write("Edit Account")
                 row = next(a for a in accounts if a['id'] == st.session_state['edit_acc_id'])
                 e_plat = st.text_input("Platform", value=row['platform'])
                 e_user = st.text_input("Username", value=row['username'])
                 e_stat = st.selectbox("Status", ["active", "suspended", "verified"], index=0 if row['status'] not in ["active", "suspended", "verified"] else ["active", "suspended", "verified"].index(row['status']))
                 
                 if st.form_submit_button("Update"):
                     update_managed_account(row['id'], e_plat, e_user, e_stat)
                     st.session_state['edit_acc_id'] = None
                     st.success("Updated!")
                     st.rerun()
    else:
        st.info("No accounts created yet in this period.")

    # 3. Page Level Chat
    render_page_chat(
        "Account Automation", 
        ManagerAgent(), 
        json.dumps(accounts, indent=2) if accounts else "No accounts yet."
    )
