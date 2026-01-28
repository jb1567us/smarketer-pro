"""
Advanced analytics dashboard for campaign and system metrics.
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import get_connection
import sqlite3

def render_analytics_dashboard():
    """Render the analytics dashboard tab."""
    st.title("📊 Analytics Dashboard")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Metrics overview
    st.subheader("Key Metrics")
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    # Get metrics from database
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    try:
        # Total leads
        c.execute("SELECT COUNT(*) as count FROM leads")
        total_leads = c.fetchone()['count']
        
        # Enriched leads
        c.execute("SELECT COUNT(*) as count FROM leads WHERE enrichment_score > 0")
        enriched_leads = c.fetchone()['count']
        
        # Active proxies
        c.execute("SELECT COUNT(*) as count FROM proxies WHERE is_active = 1")
        active_proxies = c.fetchone()['count']
        
        # Success rate
        enrichment_rate = (enriched_leads / total_leads * 100) if total_leads > 0 else 0
        
        metrics_col1.metric("Total Leads", f"{total_leads:,}")
        metrics_col2.metric("Enriched Leads", f"{enriched_leads:,}")
        metrics_col3.metric("Active Proxies", f"{active_proxies:,}")
        metrics_col4.metric("Enrichment Rate", f"{enrichment_rate:.1f}%")
        
        # Lead sources breakdown
        st.subheader("Lead Sources")
        c.execute("""
            SELECT source, COUNT(*) as count 
            FROM leads 
            GROUP BY source 
            ORDER BY count DESC 
            LIMIT 10
        """)
        sources_data = [dict(row) for row in c.fetchall()]
        
        if sources_data:
            df_sources = pd.DataFrame(sources_data)
            st.bar_chart(df_sources.set_index('source'))
        else:
            st.info("No lead source data available yet.")
        
        # Proxy performance
        st.subheader("Proxy Performance")
        c.execute("""
            SELECT 
                anonymity,
                COUNT(*) as count,
                AVG(latency) as avg_latency,
                AVG(CAST(success_count AS REAL) / (success_count + fail_count + 1)) as success_rate
            FROM proxies 
            WHERE is_active = 1
            GROUP BY anonymity
        """)
        proxy_data = [dict(row) for row in c.fetchall()]
        
        if proxy_data:
            df_proxies = pd.DataFrame(proxy_data)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Proxy Count by Tier**")
                st.dataframe(df_proxies[['anonymity', 'count']])
            
            with col2:
                st.write("**Performance Metrics**")
                st.dataframe(df_proxies[['anonymity', 'avg_latency', 'success_rate']])
        else:
            st.info("No proxy performance data available yet.")
        
        # Campaign performance (if campaigns exist)
        st.subheader("Recent Activity")
        c.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as leads_added
            FROM leads 
            WHERE created_at >= date('now', '-30 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 30
        """)
        activity_data = [dict(row) for row in c.fetchall()]
        
        if activity_data:
            df_activity = pd.DataFrame(activity_data)
            df_activity['date'] = pd.to_datetime(df_activity['date'])
            st.line_chart(df_activity.set_index('date'))
        else:
            st.info("No recent activity data available.")
        
        # Export analytics data
        st.subheader("Export Analytics")
        if st.button("📥 Download Analytics Report"):
            # Compile analytics data
            report_data = {
                'metrics': {
                    'total_leads': total_leads,
                    'enriched_leads': enriched_leads,
                    'active_proxies': active_proxies,
                    'enrichment_rate': enrichment_rate
                },
                'sources': sources_data,
                'proxy_performance': proxy_data,
                'activity': activity_data
            }
            
            import json
            report_json = json.dumps(report_data, indent=2)
            st.download_button(
                label="Download JSON Report",
                data=report_json,
                file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    except Exception as e:
        st.error(f"Error loading analytics: {e}")
    
    finally:
        conn.close()
