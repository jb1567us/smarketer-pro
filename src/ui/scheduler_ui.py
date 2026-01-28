"""
Scheduler management UI for viewing and managing scheduled jobs.
"""
import streamlit as st
import pandas as pd
from scheduler.jobs import JobScheduler

scheduler = JobScheduler()

def render_scheduler_ui():
    """Render the job scheduler management interface."""
    st.title("📅 Job Scheduler")
    
    # Start scheduler if not running
    if not scheduler.scheduler.running:
        scheduler.start()
    
    st.info("✅ Scheduler is running and processing scheduled jobs.")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 All Jobs", "➕ Add Job", "📊 Job History"])
    
    with tab1:
        st.subheader("Scheduled Jobs")
        
        jobs = scheduler.get_jobs()
        
        if jobs:
            # Convert to DataFrame for display
            df_jobs = pd.DataFrame(jobs)
            
            # Format for display
            display_cols = ['id', 'name', 'job_type', 'schedule', 'function_name', 
                          'is_active', 'run_count', 'last_run', 'next_run']
            available_cols = [col for col in display_cols if col in df_jobs.columns]
            
            # Add action column
            for idx, row in df_jobs.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    status = "🟢 Active" if row['is_active'] else "🔴 Inactive"
                    st.write(f"**{row['name']}** - {status}")
                    st.caption(f"Type: {row['job_type']} | Schedule: {row['schedule']} | Runs: {row['run_count']}")
                
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_{row['id']}"):
                        scheduler.remove_job(row['id'])
                        st.success(f"Removed job: {row['name']}")
                        st.rerun()
                
                with col3:
                    if st.button("▶️ Run Now", key=f"run_{row['id']}", disabled=not row['is_active']):
                        # Trigger immediate execution
                        st.info(f"Triggering job: {row['name']}")
                
                st.divider()
        else:
            st.info("No scheduled jobs yet. Create one below!")
    
    with tab2:
        st.subheader("Create New Job")
        
        with st.form("add_job_form"):
            job_name = st.text_input("Job Name", placeholder="Daily Lead Enrichment")
            
            job_type = st.selectbox("Job Type", ["cron", "interval"])
            
            if job_type == "cron":
                st.caption("Cron format: minute hour day month day_of_week")
                st.caption("Examples: '0 9 * * *' (daily at 9 AM), '0 */6 * * *' (every 6 hours)")
                schedule = st.text_input("Cron Schedule", placeholder="0 9 * * *")
            else:
                schedule = st.number_input("Interval (minutes)", min_value=1, value=60)
                schedule = str(schedule)
            
            function_options = {
                "Daily Enrichment": "daily_enrichment",
                "Weekly Report": "weekly_report",
                "Proxy Health Check": "proxy_health_check"
            }
            
            selected_function = st.selectbox("Function to Run", list(function_options.keys()))
            function_name = function_options[selected_function]
            
            # Parameters (optional)
            st.caption("Parameters (optional, JSON format)")
            parameters_text = st.text_area("Parameters", value="{}", height=100)
            
            submitted = st.form_submit_button("Create Job", type="primary")
            
            if submitted:
                try:
                    import json
                    parameters = json.loads(parameters_text)
                    
                    job_id = scheduler.add_job(
                        name=job_name,
                        job_type=job_type,
                        schedule=schedule,
                        function_name=function_name,
                        parameters=parameters
                    )
                    
                    st.success(f"✅ Job created successfully! ID: {job_id}")
                    st.rerun()
                
                except json.JSONDecodeError:
                    st.error("Invalid JSON in parameters field")
                except Exception as e:
                    st.error(f"Error creating job: {e}")
    
    with tab3:
        st.subheader("Job Execution History")
        
        jobs = scheduler.get_jobs()
        
        if jobs:
            # Show execution statistics
            active_jobs = [j for j in jobs if j['is_active']]
            total_runs = sum(j.get('run_count', 0) for j in jobs)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Jobs", len(jobs))
            col2.metric("Active Jobs", len(active_jobs))
            col3.metric("Total Executions", total_runs)
            
            st.divider()
            
            # Show recent executions
            st.write("**Recent Job Executions**")
            
            recent_jobs = [j for j in jobs if j.get('last_run')]
            recent_jobs.sort(key=lambda x: x.get('last_run', ''), reverse=True)
            
            for job in recent_jobs[:10]:
                st.write(f"**{job['name']}** - Last run: {job.get('last_run', 'Never')}")
                st.caption(f"Executions: {job.get('run_count', 0)}")
        else:
            st.info("No job history available yet.")
