"""
Webhook management UI for registering and monitoring webhooks.
"""
import streamlit as st
import pandas as pd
from webhooks.manager import WebhookManager, EVENTS

manager = WebhookManager()

def render_webhooks_ui():
    """Render the webhook management interface."""
    st.title("🔔 Webhooks")
    
    st.markdown("""
    Webhooks allow external systems to receive real-time notifications when events occur.
    """)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Webhooks", "➕ Register Webhook", "📊 Deliveries"])
    
    with tab1:
        st.subheader("Registered Webhooks")
        
        webhooks = manager.get_webhooks()
        
        if webhooks:
            for webhook in webhooks:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**ID**: {webhook['id']}")
                        st.write(f"**URL**: {webhook['url']}")
                        
                        import json
                        events = json.loads(webhook['events'])
                        st.write(f"**Events**: {', '.join(events)}")
                        
                        status = "🟢 Active" if webhook['is_active'] else "🔴 Inactive"
                        st.write(f"**Status**: {status}")
                    
                    with col2:
                        if st.button("🗑️ Deactivate", key=f"deactivate_{webhook['id']}"):
                            manager.deactivate_webhook(webhook['id'])
                            st.success("Webhook deactivated")
                            st.rerun()
                        
                        if st.button("🧪 Test", key=f"test_{webhook['id']}"):
                            # Send test webhook
                            manager.deliver_webhook(
                                webhook['id'],
                                'test.event',
                                {'message': 'Test webhook delivery', 'timestamp': 'now'}
                            )
                            st.success("Test webhook sent!")
        else:
            st.info("No webhooks registered yet.")
    
    with tab2:
        st.subheader("Register New Webhook")
        
        with st.form("register_webhook"):
            webhook_url = st.text_input(
                "Webhook URL",
                placeholder="https://your-app.com/webhook"
            )
            
            # Event selection
            st.write("**Select Events**")
            selected_events = []
            
            for event, description in EVENTS.items():
                if st.checkbox(f"{event}", help=description):
                    selected_events.append(event)
            
            # Subscribe to all events option
            if st.checkbox("Subscribe to all events (*)", value=False):
                selected_events = ['*']
            
            # Optional secret for signature verification
            with st.expander("🔐 Security Settings (Optional)"):
                secret = st.text_input(
                    "Webhook Secret",
                    type="password",
                    help="Used to generate HMAC signature for webhook verification"
                )
            
            submitted = st.form_submit_button("Register Webhook", type="primary")
            
            if submitted:
                if not webhook_url:
                    st.error("Webhook URL is required")
                elif not selected_events:
                    st.error("Please select at least one event")
                else:
                    try:
                        webhook_id = manager.register_webhook(
                            url=webhook_url,
                            events=selected_events,
                            secret=secret if secret else None
                        )
                        
                        st.success(f"✅ Webhook registered successfully! ID: {webhook_id}")
                        
                        if secret:
                            st.info("🔐 Webhook will include X-Webhook-Signature header for verification")
                        
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error registering webhook: {e}")
    
    with tab3:
        st.subheader("Webhook Deliveries")
        
        from database import get_connection
        import sqlite3
        
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            # Get recent deliveries
            c.execute("""
                SELECT wd.*, w.url 
                FROM webhook_deliveries wd
                JOIN webhooks w ON wd.webhook_id = w.id
                ORDER BY wd.created_at DESC
                LIMIT 50
            """)
            
            deliveries = [dict(row) for row in c.fetchall()]
            
            if deliveries:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                
                success_count = len([d for d in deliveries if d['status'] == 'success'])
                failed_count = len([d for d in deliveries if d['status'] == 'failed'])
                pending_count = len([d for d in deliveries if d['status'] == 'pending'])
                
                col1.metric("Successful", success_count)
                col2.metric("Failed", failed_count)
                col3.metric("Pending", pending_count)
                
                st.divider()
                
                # Deliveries table
                for delivery in deliveries:
                    status_icon = {
                        'success': '✅',
                        'failed': '❌',
                        'pending': '⏳'
                    }.get(delivery['status'], '❓')
                    
                    with st.expander(f"{status_icon} {delivery['event_type']} - {delivery['created_at']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Webhook URL**: {delivery['url']}")
                            st.write(f"**Event Type**: {delivery['event_type']}")
                            st.write(f"**Status**: {delivery['status']}")
                        
                        with col2:
                            st.write(f"**Attempts**: {delivery['attempts']}")
                            st.write(f"**Response Code**: {delivery.get('response_code', 'N/A')}")
                            st.write(f"**Last Attempt**: {delivery.get('last_attempt', 'N/A')}")
                        
                        st.write("**Payload**:")
                        st.code(delivery['payload'], language='json')
            else:
                st.info("No webhook deliveries yet.")
        
        finally:
            conn.close()
