import streamlit as st
import pandas as pd
from src.database import get_db_session
from src.affiliates.manager import OfferManager
from src.affiliates.merchant import ProgramManager
from src.affiliates.models import AffiliateLink, Partner, TrackingEvent

def render_affiliate_ui():
    st.title("Affiliate Command Center")
    
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
            st.info("Manage the affiliate programs you belong to and your tracking links.")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.subheader("Add New Offer")
                with st.form("add_offer_form"):
                    name = st.text_input("Product Name", placeholder="e.g. ConvertKit")
                    target_url = st.text_input("Target URL (Your Affiliate Link)")
                    slug = st.text_input("Cloaked Slug", placeholder="convertkit")
                    program_name = st.text_input("Program Name", placeholder="PartnerStack")
                    commission_rate = st.text_input("Commission Rate", placeholder="30%")
                    
                    submitted = st.form_submit_button("Add Offer")
                    
                    if submitted and name and target_url and slug:
                        try:
                            offer_mgr.add_offer(name, target_url, slug, program_name, commission_rate)
                            st.success(f"Added {name}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
    
            with col2:
                st.subheader("Active Offers")
                offers = offer_mgr.list_offers()
                if offers:
                    # Convert objects to dicts for dataframe
                    data = [{"Name": o.name, "Slug": o.slug, "Program": o.program_name, "Target": o.target_url} for o in offers]
                    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
                else:
                    st.write("No offers added yet.")
    
            st.divider()
            st.caption("Auto-Injection Guide: These offers will be automatically suggested by the Copywriter Agent when generating content about these topics.")
    
        # =========================================================================
        # TAB 2: PARTNER CENTER (Brand)
        # =========================================================================
        with tabs[1]:
            st.header("Partner Ecosystem")
            st.info("Manage the affiliates and partners who promote YOU.")
            
            p_col1, p_col2 = st.columns([1, 2])
            
            with p_col1:
                st.subheader("Register Partner")
                with st.form("add_partner_form"):
                    p_name = st.text_input("Partner Name")
                    p_email = st.text_input("Email")
                    p_user_id = st.text_input("User ID (Optional)", placeholder="local_user_1")
                    
                    if st.form_submit_button("Register Partner"):
                        if p_name and p_email:
                            try:
                                # Fallback user_id to email if empty
                                uid = p_user_id if p_user_id else p_email
                                p = prog_mgr.register_partner(uid, p_email, p_name)
                                st.success(f"Registered {p.name}. Code: {p.referral_code}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")

            with p_col2:
                st.subheader("Active Partners")
                partners = db.query(Partner).all()
                if partners:
                    p_data = [{"Name": p.name, "Email": p.email, "Code": p.referral_code, "Status": p.status} for p in partners]
                    st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
                else:
                    st.info("No partners yet.")

        # =========================================================================
        # TAB 3: ATTRIBUTION
        # =========================================================================
        with tabs[2]:
            st.header("Ledger")
            events = db.query(TrackingEvent).order_by(TrackingEvent.timestamp.desc()).limit(50).all()
            if events:
                 e_data = [{"Type": e.event_type, "Source": e.source_id, "Value": e.value, "Time": e.timestamp} for e in events]
                 st.dataframe(pd.DataFrame(e_data), use_container_width=True)
            else:
                st.write("No events recorded.")
