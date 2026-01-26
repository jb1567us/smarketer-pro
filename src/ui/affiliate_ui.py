import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from database import get_db_session
from affiliates.manager import OfferManager
from affiliates.merchant import ProgramManager
from affiliates.models import AffiliateLink, Partner, TrackingEvent
from ui.components import (
    premium_header, confirm_action, safe_action_wrapper, 
    render_enhanced_table, render_page_chat, render_data_management_bar
)
from agents import ManagerAgent

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
            
            # Add New Offer
            with st.expander("➕ Add New Offer", expanded=False):
                with st.form("add_offer_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("Product Name", placeholder="e.g. ConvertKit")
                        program_name = st.text_input("Program Name", placeholder="PartnerStack")
                    with col2:
                        target_url = st.text_input("Target URL (Your Affiliate Link)")
                        slug = st.text_input("Cloaked Slug", placeholder="convertkit")
                    
                    commission_rate = st.text_input("Commission Rate", placeholder="30%")
                    
                    if st.form_submit_button("Save Offer", type="primary", width="stretch"):
                        def _save_offer():
                            if not name or not target_url or not slug:
                                raise ValueError("Name, Target URL, and Slug are required.")
                            offer_mgr.add_offer(name, target_url, slug, program_name, commission_rate)
                            return f"Added {name} to your vault."

                        safe_action_wrapper(_save_offer, "success_toast")
                        st.rerun()

            st.divider()
            
            # List Offers
            offers = offer_mgr.list_offers()
            if offers:
                st.subheader(f"Active Offers ({len(offers)})")
                
                # Filter
                q_offer = st.text_input("🔍 Search Offers", placeholder="Name, Program, or Slug")
                
                # Prepare DataFrame
                data = [{"id": o.id, "Name": o.name, "Slug": o.slug, "Program": o.program_name, "Target": o.target_url} for o in offers]
                
                if q_offer:
                    term = q_offer.lower()
                    data = [d for d in data if term in d['Name'].lower() or term in d['Program'].lower()]
                
                df_offers = pd.DataFrame(data)
                
                # Enhanced Table
                edited_offers = render_enhanced_table(df_offers, key="affiliate_offers_table")
                
                # Bulk Actions
                selected_ids = edited_offers[edited_offers['Select'] == True]['id'].tolist() if 'Select' in edited_offers.columns else []
                
                if selected_ids:
                    def _delete_offers():
                        for oid in selected_ids:
                            offer_mgr.delete_offer(oid)
                            
                    confirm_action(
                        "🗑️ Delete Selected",
                        f"Permanently delete {len(selected_ids)} offers?",
                        lambda: [_delete_offers(), st.rerun()],
                        key="del_offers_btn"
                    )
            else:
                 st.info("No offers available. Add one above.")

        # =========================================================================
        # TAB 2: PARTNER CENTER (Brand)
        # =========================================================================
        with tabs[1]:
            st.header("Partner Ecosystem")
            st.caption("Manage the affiliates and partners who promote YOU.")
            
            active_action = st.radio("Action", ["Manage Partners", "Register New"], horizontal=True, label_visibility="collapsed")
            
            if active_action == "Register New":
                with st.container(border=True):
                    st.subheader("Register New Partner")
                    with st.form("add_partner_form"):
                        p_name = st.text_input("Partner Name")
                        p_email = st.text_input("Email")
                        p_user_id = st.text_input("User ID (Optional)", placeholder="local_user_1")
                        
                        if st.form_submit_button("Register Partner", type="primary"):
                            def _register_partner():
                                if not p_name or not p_email:
                                    raise ValueError("Name and Email are required.")
                                uid = p_user_id if p_user_id else p_email
                                p = prog_mgr.register_partner(uid, p_email, p_name)
                                return f"Registered {p.name}. Code: {p.referral_code}"
                                
                            safe_action_wrapper(_register_partner, "Partner Registered!")
            
            else: # Manage
                partners = db.query(Partner).all()
                if partners:
                    q_partner = st.text_input("🔍 Search Partners", placeholder="Name, Email, or Code")
                    
                    p_data = [{"id": p.id, "Name": p.name, "Email": p.email, "Code": p.referral_code, "Status": p.status, "Joined": p.created_at} for p in partners]
                    
                    if q_partner:
                        term = q_partner.lower()
                        p_data = [d for d in p_data if term in d['Name'].lower() or term in d['Email'].lower()]
                        
                    df_partners = pd.DataFrame(p_data)
                    
                    # Enhanced Table
                    edited_partners = render_enhanced_table(df_partners, key="partners_table")
                    
                    # CSV Export logic included in render_enhanced_table usually, but if not:
                    # We can add a custom export button here if needed, but the wrapper is preferred.
                    # Let's add explicit bulk delete.
                    
                    sel_p_ids = edited_partners[edited_partners['Select'] == True]['id'].tolist() if 'Select' in edited_partners.columns else []
                    
                    if sel_p_ids:
                        confirm_action(
                             "🗑️ Delete Partners",
                             f"Remove {len(sel_p_ids)} partners? This cannot be undone.",
                             lambda: [prog_mgr.delete_partner(pid) for pid in sel_p_ids] and st.rerun(),
                             key="del_partners_btn"
                        )
                else:
                    st.info("No partners found.")

        # =========================================================================
        # TAB 3: ATTRIBUTION
        # =========================================================================
        with tabs[2]:
            st.header("Ledger & Attribution")
            
            col_f1, col_f2 = st.columns([1, 2])
            with col_f1:
                days_back = st.slider("📅 Days Back", 1, 365, 30)
            with col_f2:
                q_event = st.text_input("🔍 Search Events", placeholder="Source ID or Event Type")
            
            cutoff_date = datetime.now() - timedelta(days=days_back)
            cutoff_ts = cutoff_date.timestamp()
            
            events = db.query(TrackingEvent).filter(TrackingEvent.timestamp >= cutoff_ts).order_by(TrackingEvent.timestamp.desc()).all()
            
            if events:
                 st.metric("Total Events (Period)", len(events))
                 e_data = [{"Type": e.event_type, "Source": e.source_id, "Value": e.value, "Time": datetime.fromtimestamp(e.timestamp).strftime('%Y-%m-%d %H:%M:%S')} for e in events]
                 
                 if q_event:
                     term = q_event.lower()
                     e_data = [d for d in e_data if term in str(d['Source']).lower() or term in d['Type'].lower()]
                 
                 df_events = pd.DataFrame(e_data)
                 render_enhanced_table(df_events, key="attribution_table") # Just view
            else:
                st.info(f"No events recorded in the last {days_back} days.")
    
    # Page Level Chat
    render_page_chat("Affiliate Manager", ManagerAgent(), "Manage Affiliate offers and partners.")
