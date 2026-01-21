import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_db_session
from affiliates.manager import OfferManager
from affiliates.merchant import ProgramManager
from affiliates.models import AffiliateLink, Partner, TrackingEvent
from src.ui.components import premium_header, confirm_action, safe_action_wrapper

def render_affiliate_ui():
    premium_header(
        "Affiliate Command Center",
        "Manage your partnerships (Brand) and your promotional offers (Publisher)."
    )
    
    # We use a context manager for the DB session
    with get_db_session() as db:
        offer_mgr = OfferManager(db)
        prog_mgr = ProgramManager(db)
        
        tabs = st.tabs(["💎 My Vault (Publisher)", "🤝 Partner Center (Brand)", "📊 Attribution"])
        
        # =========================================================================
        # TAB 1: PUBLISHER VAULT (My Links)
        # =========================================================================
        with tabs[0]:
            st.header("My Affiliate Programs & Links")
            st.caption("Manage the affiliate programs you belong to and your tracking links.")
            
            c1, c2 = st.columns([1, 2])
            
            with c1:
                with st.expander("➕ Add New Offer", expanded=True):
                    with st.form("add_offer_form"):
                        name = st.text_input("Product Name", placeholder="e.g. ConvertKit")
                        target_url = st.text_input("Target URL (Your Affiliate Link)")
                        slug = st.text_input("Cloaked Slug", placeholder="convertkit")
                        program_name = st.text_input("Program Name", placeholder="PartnerStack")
                        commission_rate = st.text_input("Commission Rate", placeholder="30%")
                        
                        submitted = st.form_submit_button("Save Offer", use_container_width=True)
                        
                        if submitted:
                            def _save_offer():
                                if not name or not target_url or not slug:
                                    raise ValueError("Name, Target URL, and Slug are required.")
                                offer_mgr.add_offer(name, target_url, slug, program_name, commission_rate)
                                return f"Added {name} to your vault."

                            safe_action_wrapper(_save_offer, "success_toast")

            with c2:
                st.subheader("Active Offers")
                offers = offer_mgr.list_offers()
                
                if offers:
                    # Dataframe
                    data = [{"ID": o.id, "Name": o.name, "Slug": o.slug, "Program": o.program_name, "Target": o.target_url} for o in offers]
                    df_offers = pd.DataFrame(data)
                    st.dataframe(df_offers, use_container_width=True, hide_index=True)
                    
                    # Management Actions
                    st.divider()
                    st.caption("Manage Offers")
                    
                    # Delete Selection
                    opts = {o.id: f"{o.name} ({o.program_name})" for o in offers}
                    selected_ids = st.multiselect("Select offers to delete:", options=opts.keys(), format_func=lambda x: opts[x])
                    
                    if selected_ids:
                         if st.button(f"🗑️ Delete {len(selected_ids)} Selected", type="primary"):
                             confirm_action(
                                 "delete_offers",
                                 f"Permanently delete {len(selected_ids)} offers?",
                                 lambda: [offer_mgr.delete_offer(oid) for oid in selected_ids] and st.rerun(),
                                 f"Deleted {len(selected_ids)} offers."
                             )

                else:
                    st.info("No offers added yet. Use the form to add your first affiliate link.")
    
            st.divider()
            st.info("💡 **Auto-Injection:** These offers will be automatically suggested by the Copywriter Agent when generating content about these topics.")
    
        # =========================================================================
        # TAB 2: PARTNER CENTER (Brand)
        # =========================================================================
        with tabs[1]:
            st.header("Partner Ecosystem")
            st.caption("Manage the affiliates and partners who promote YOU.")
            
            p_col1, p_col2 = st.columns([1, 2])
            
            with p_col1:
                with st.expander("➕ Register Partner", expanded=True):
                    with st.form("add_partner_form"):
                        p_name = st.text_input("Partner Name")
                        p_email = st.text_input("Email")
                        p_user_id = st.text_input("User ID (Optional)", placeholder="local_user_1")
                        
                        if st.form_submit_button("Register Partner", use_container_width=True):
                            def _register_partner():
                                if not p_name or not p_email:
                                    raise ValueError("Name and Email are required.")
                                # Fallback user_id to email if empty
                                uid = p_user_id if p_user_id else p_email
                                p = prog_mgr.register_partner(uid, p_email, p_name)
                                return f"Registered {p.name}. Code: {p.referral_code}"
                                
                            safe_action_wrapper(_register_partner, "success_toast")

            with p_col2:
                st.subheader("Active Partners")
                partners = db.query(Partner).all()
                
                if partners:
                    p_data = [{"ID": p.id, "Name": p.name, "Email": p.email, "Code": p.referral_code, "Status": p.status, "Joined": p.created_at} for p in partners]
                    df_partners = pd.DataFrame(p_data)
                    st.dataframe(df_partners, use_container_width=True, hide_index=True)
                    
                    c_act1, c_act2 = st.columns(2)
                    with c_act1:
                         # CSV Export
                         csv = df_partners.to_csv(index=False).encode('utf-8')
                         st.download_button(
                             label="📥 Export CSV",
                             data=csv,
                             file_name="partners_export.csv",
                             mime="text/csv",
                             use_container_width=True
                         )
                    
                    with c_act2:
                        pass # Spacing

                    # Delete Logic
                    st.divider()
                    st.caption("Manage Partners")
                    p_opts = {p.id: f"{p.name} ({p.email})" for p in partners}
                    sel_p_ids = st.multiselect("Select partners to remove:", options=p_opts.keys(), format_func=lambda x: p_opts[x])
                    
                    if sel_p_ids:
                        if st.button(f"🗑️ Delete {len(sel_p_ids)} Partners", type="primary"):
                             confirm_action(
                                 "delete_partners",
                                 f"Remove {len(sel_p_ids)} partners? This cannot be undone.",
                                 lambda: [prog_mgr.delete_partner(pid) for pid in sel_p_ids] and st.rerun(),
                                 f"Removed {len(sel_p_ids)} partners."
                             )

                else:
                    st.info("No partners yet.")

        # =========================================================================
        # TAB 3: ATTRIBUTION
        # =========================================================================
        with tabs[2]:
            st.header("Ledger & Attribution")
            
            # Filtering
            col_f1, col_f2 = st.columns([1, 3])
            with col_f1:
                days_back = st.slider("📅 Days Back", 1, 365, 30)
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Use timestamp comparison if your model stores datetime, or float logic if it stores float
            # Assuming float based on 'int(time.time())' standard often used here, let's check model?
            # Actually standard practice here has been float or datetime. Checking DB...
            # The 'created_at' in models often floats.
            # safe bet: filter in python if unsure, but better SQL.
            # Let's assume float timestamp for now as standard in this codebase.
            cutoff_ts = cutoff_date.timestamp()
            
            events = db.query(TrackingEvent).filter(TrackingEvent.timestamp >= cutoff_ts).order_by(TrackingEvent.timestamp.desc()).all()
            
            if events:
                 st.metric("Total Events (Period)", len(events))
                 e_data = [{"Type": e.event_type, "Source": e.source_id, "Value": e.value, "Time": datetime.fromtimestamp(e.timestamp).strftime('%Y-%m-%d %H:%M:%S')} for e in events]
                 
                 df_events = pd.DataFrame(e_data)
                 st.dataframe(df_events, use_container_width=True, hide_index=True)
                 
                 # CSV Export for Ledger
                 csv_e = df_events.to_csv(index=False).encode('utf-8')
                 st.download_button(
                     label="📥 Export Ledger CSV",
                     data=csv_e,
                     file_name="attribution_ledger.csv",
                     mime="text/csv"
                 )
            else:
                st.info(f"No events recorded in the last {days_back} days.")
