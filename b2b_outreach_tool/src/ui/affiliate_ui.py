import streamlit as st
import pandas as pd
from affiliate_system import AffiliateManager

def render_affiliate_ui():
    st.title("Affiliate Command Center")
    
    manager = AffiliateManager()
    
    tabs = st.tabs(["💎 My Vault (Publisher)", "🤝 Partner Center (Brand)", "📊 Attribution"])
    
    # =========================================================================
    # TAB 1: PUBLISHER VAULT (My Links)
    # =========================================================================
    with tabs[0]:
        st.header("My Affiliate Programs & Links")
        st.info("Manage the affiliate programs you belong to and your tracking links.")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Add New Program")
            with st.form("add_program_form"):
                prog_name = st.text_input("Program Name", placeholder="e.g. Amazon Associates")
                login_url = st.text_input("Login URL")
                username = st.text_input("My Username/ID")
                dashboard_url = st.text_input("Dashboard URL")
                notes = st.text_area("Notes")
                submitted = st.form_submit_button("Add Program")
                
                if submitted and prog_name:
                    pid = manager.add_my_program(prog_name, login_url, username, dashboard_url, notes)
                    if pid:
                        st.success(f"Added {prog_name}")
                        st.rerun()

        with col2:
            st.subheader("Existing Programs")
            programs = manager.get_my_programs()
            if programs:
                df_progs = pd.DataFrame(programs)
                st.dataframe(df_progs, use_container_width=True, hide_index=True)
            else:
                st.write("No programs added yet.")

        st.divider()
        
        st.subheader("My Tracking Links")
        
        # Add Link Form
        with st.expander("➕ Add New Tracking Link"):
            if not programs:
                st.warning("Please add an Affiliate Program above first.")
            else:
                with st.form("add_link_form"):
                    prog_options = {p['program_name']: p['id'] for p in programs}
                    selected_prog_name = st.selectbox("Program", list(prog_options.keys()))
                    target_url = st.text_input("Target URL", placeholder="https://example.com/product")
                    cloaked_slug = st.text_input("Cloaked Slug", placeholder="shopify-deal")
                    category = st.selectbox("Category", ["Software", "Host/VPN", "Course", "E-com", "Other"])
                    commission_rate = st.text_input("Commission Rate", placeholder="20%")
                    
                    submit_link = st.form_submit_button("Save Link")
                    
                    if submit_link and target_url and cloaked_slug:
                        pid = prog_options[selected_prog_name]
                        lid = manager.add_my_link(pid, target_url, cloaked_slug, category, commission_rate)
                        if lid:
                            st.success("Link saved!")
                            st.rerun()

        # List Links
        links = manager.get_my_links()
        if links:
            df_links = pd.DataFrame(links)
            # Reorder cols for display
            display_cols = ['program_name', 'cloaked_slug', 'target_url', 'category', 'click_count', 'status']
            st.dataframe(df_links[display_cols], use_container_width=True, hide_index=True)
            
            # Action Buttons
            st.caption("Quick Actions")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔗 Copy Selected Link (Simulated)"):
                    st.info("Link copying functionality would integrate with clipboard here.")
            with c2:
                if st.button("❤️ Run Health Check"):
                    with st.spinner("Pinging target URLs..."):
                        all_good = True
                        for l in links:
                            res = manager.check_link_health(l['id'])
                            if not res['is_alive']:
                                st.error(f"❌ Broken: {l['cloaked_slug']} ({res['status_code']})")
                                all_good = False
                        if all_good:
                            st.success("✅ All links are healthy!")
                        time.sleep(1)
                        st.rerun()
        else:
            st.write("No links in vault.")

    # =========================================================================
    # TAB 2: PARTNER CENTER (Brand)
    # =========================================================================
    with tabs[1]:
        st.header("Partner Ecosystem")
        st.info("Manage the affiliates and partners who promote YOU.")
        
        col_p1, col_p2 = st.columns([1, 2])
        
        with col_p1:
            st.subheader("Onboard Partner")
            with st.form("add_partner"):
                p_name = st.text_input("Partner Name", placeholder="Jane Doe")
                p_email = st.text_input("Email")
                p_site = st.text_input("Website/Social URL", placeholder="twitch.tv/janedoe")
                p_pay = st.text_input("Payment Info", placeholder="PayPal Email")
                
                if st.form_submit_button("Add Partner"):
                    if p_name and p_email:
                        pid = manager.add_partner(p_name, p_email, p_site, payment_info=p_pay)
                        if pid:
                            st.success(f"Onboarded {p_name}")
                            st.rerun()
                        else:
                            st.error("Failed to add partner (duplicate email?)")

        with col_p2:
            st.subheader("Active Partners")
            partners = manager.get_partners()
            if partners:
                df_partners = pd.DataFrame(partners)
                st.dataframe(df_partners[['name', 'email', 'website', 'status', 'created_at']], use_container_width=True, hide_index=True)
                
                # Context Menu for Partner
                st.divider()
                st.write("🔧 **Partner Operations**")
                
                p_options = {p['name']: p['id'] for p in partners}
                sel_p_name = st.selectbox("Select Partner", list(p_options.keys()))
                sel_pid = p_options[sel_p_name]
                
                c1, c2 = st.columns(2)
                with c1:
                    st.caption("Create Contract")
                    with st.form(f"contract_{sel_pid}"):
                        c_type = st.selectbox("Type", ["RevShare", "CPA"])
                        c_terms = st.text_input("Terms (e.g. 20 for 20%)", "20")
                        if st.form_submit_button("Assign Contract"):
                            manager.create_contract(sel_pid, c_type, c_terms)
                            st.success(f"Contract assigned to {sel_p_name}")

                with c2:
                    st.caption("Partner Assets")
                    if st.button("Generate Welcome Kit"):
                        from agents.copywriter import CopywriterAgent
                        agent = CopywriterAgent()
                        
                        with st.spinner(f"Drafting onboarding for {sel_p_name}..."):
                            # Simple context
                            context = {
                                "partner_name": sel_p_name,
                                "contract_terms": "Standard Terms", # Could lookup active contract
                                "program_name": "Smarketer Partner Program"
                            }
                            # Hacky direct call or assume discuss method
                            prompt = f"Write a warm welcome email to new affiliate partner {sel_p_name}. Include login details placeholder and excitement about our partnership."
                            res = agent.think(prompt)
                            
                        st.info("Draft Generated:")
                        st.text_area("Welcome Email", value=res, height=200)
            else:
                st.info("No partners found. Add one on the left.")

    # =========================================================================
    # TAB 3: ATTRIBUTION
    # =========================================================================
    with tabs[2]:
        st.header("Attribution & Financials")
        
        col_a1, col_a2 = st.columns([1, 2])
        
        with col_a1:
            st.subheader("Log Event (Manual)")
            st.caption("Use this when you confirm a sale/lead from Stripe/CRM manually.")
            
            partners = manager.get_partners()
            if not partners:
                st.warning("No partners to attribute to.")
            else:
                p_options = {p['name']: p['id'] for p in partners}
                attr_p_name = st.selectbox("Attributable Partner", list(p_options.keys()), key="attr_p")
                attr_pid = p_options[attr_p_name]
                
                e_type = st.selectbox("Event", ["sale", "click", "sign_up"])
                e_val = st.number_input("Event Value ($)", value=0.0)
                e_src = st.text_input("Source URL", placeholder="e.g. checkout_session_123")
                
                if st.button("Log & Calculate Commission", type="primary"):
                    comm = manager.log_partner_event(attr_pid, e_type, e_val, e_src)
                    st.toast(f"Event logged! Commission generated: ${comm:.2f}")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()

        with col_a2:
            st.subheader("Performance Ledger")
            
            # Aggregate stats
            # We can pull raw events for now
            conn = manager.conn # Access connection directly for reading
            c = conn.cursor()
            c.execute('''
                SELECT p.name, pe.event_type, pe.event_value, pe.commission_generated, pe.timestamp 
                FROM partner_events pe
                JOIN partners p ON pe.partner_id = p.id
                ORDER BY pe.timestamp DESC
            ''')
            events = c.fetchall()
            conn.close() # Actually manager.conn in init creates a connection but we should probably use a fresh one or the method
            # Wait, manager.conn is opened in init.
            # Let's just use a fresh read for safety since we are inside a UI function
            from database import get_connection
            conn = get_connection()
            df_events = pd.read_sql_query('''
                SELECT p.name as Partner, pe.event_type as Type, pe.event_value as "Sale Value", 
                       pe.commission_generated as "Comm. Earned", datetime(pe.timestamp, 'unixepoch') as Time
                FROM partner_events pe
                JOIN partners p ON pe.partner_id = p.id
                ORDER BY pe.timestamp DESC
            ''', conn)
            conn.close()
            
            if not df_events.empty:
                st.dataframe(df_events, use_container_width=True, hide_index=True)
                
                st.divider()
                st.subheader("Payouts Due")
                # Group by Partner
                payouts = df_events.groupby("Partner")["Comm. Earned"].sum().reset_index()
                st.dataframe(payouts, use_container_width=True)
            else:
                st.info("No events recorded yet.")
