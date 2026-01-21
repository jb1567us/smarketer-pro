import asyncio
import threading
import time
import sys
import os
import subprocess
from datetime import datetime
import streamlit as st

class AutomationEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutomationEngine, cls).__new__(cls)
            cls._instance.jobs = {} # {job_id: {thread, status, logs, meta}}
            cls._instance.logs = [] # Global logs for UI
            cls._instance.lock = threading.Lock()
        return cls._instance

    def __init__(self):
        # Init called every time? Singleton handling usually prevents re-init or we check generic
        pass

    def start_mission(self, strategy, manager_agent, workspace_id=1):
        """Starts a research mission job."""
        import uuid
        job_id = str(uuid.uuid4())[:8]
        
        with self.lock:
            # Basic concurrency limit (optional, for now allow parallel)
            # if any(j['status'] == 'running' for j in self.jobs.values()):
            #     return None # Busy
            
            job_meta = {
                "id": job_id,
                "type": "mission",
                "name": strategy.get('strategy_name', 'Unnamed Mission'),
                "status": "running",
                "logs": [],
                "start_time": time.time(),
                "workspace_id": workspace_id,
                "progress": 0
            }
            self.jobs[job_id] = job_meta
            
            thread = threading.Thread(
                target=self._run_mission_thread,
                args=(job_id, strategy, manager_agent),
                daemon=True
            )
            self.jobs[job_id]['thread'] = thread
            thread.start()
            
        return job_id

    def log(self, message):
        """Legacy global log."""
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] [Global] {message}"
        self.logs.append(entry)
        print(entry)

    def start_workflow(self, workflow_id, inputs, manager_agent, workspace_id=1):
        """Starts a workflow job."""
        import uuid
        job_id = str(uuid.uuid4())[:8]
        
        with self.lock:
            job_meta = {
                "id": job_id,
                "type": "workflow",
                "name": f"Workflow: {workflow_id}",
                "status": "running",
                "logs": [],
                "start_time": time.time(),
                "workspace_id": workspace_id,
                "progress": 0
            }
            self.jobs[job_id] = job_meta
            
            thread = threading.Thread(
                target=self._run_workflow_thread,
                args=(job_id, workflow_id, inputs, manager_agent),
                daemon=True
            )
            self.jobs[job_id]['thread'] = thread
            thread.start()
            
        return job_id

    def _run_workflow_thread(self, job_id, workflow_id, inputs, manager_agent):
        """Thread wrapper for workflow logic."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            self.custom_log(job_id, f"⚡ Executing Workflow Graph: {workflow_id}")
            # Use wait=True equivalent
            # ManagerAgent.execute_workflow is async.
            def log_cb(msg):
                self.custom_log(job_id, msg)

            loop.run_until_complete(manager_agent.execute_workflow(
                workflow_id, 
                inputs, 
                status_callback=log_cb
            ))
            self.jobs[job_id]['status'] = "completed"
            self.custom_log(job_id, f"✅ Workflow {workflow_id} execution finished.")
        except Exception as e:
            self.jobs[job_id]['status'] = "failed"
            self.jobs[job_id]['error'] = str(e)
            self.custom_log(job_id, f"💥 Error executing workflow {workflow_id}: {e}")
            import traceback
            traceback.print_exc()
        finally:
            loop.close()

    def custom_log(self, job_id, message):
        """Append log to specific job."""
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {message}"
        if job_id in self.jobs:
            self.jobs[job_id]['logs'].append(entry)
        self.logs.append(entry) # Also add to global
        print(f"[Job {job_id}] {entry}")

    def _run_mission_thread(self, job_id, strategy, manager_agent):
        """Thread wrapper for mission logic."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            self.custom_log(job_id, "🚀 Mission Started")
            loop.run_until_complete(self._execute_mission_logic(job_id, strategy, manager_agent))
            self.jobs[job_id]['status'] = "completed"
            self.custom_log(job_id, "🏁 Mission Completed Successfully")
        except Exception as e:
            self.jobs[job_id]['status'] = "failed"
            self.jobs[job_id]['error'] = str(e)
            self.custom_log(job_id, f"💥 Critical Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            loop.close()

    async def _execute_mission_logic(self, job_id, strategy, manager_agent):
        """
        The actual logic that runs indefinitely or until goal met.
        Supports sequential execution of workflows and agent tasks.
        """
        sequence = strategy.get('sequence', [])
        is_conductor = strategy.get('mode') == 'conductor' or len(sequence) > 0
        
        # Inject custom logger into manager_agent for this run?
        # A simple callback adapter
        def log_cb(msg):
            self.custom_log(job_id, msg)

        if is_conductor and sequence:
            self.custom_log(job_id, f"🎬 Conductor Sequence Active. Goal: {strategy.get('goal')}")
            
            for step in sequence:
                if self.jobs[job_id]['status'] == 'stopped': break
                
                step_type = step.get('type')
                
                if step_type == 'workflow':
                    wf_name = step.get('name')
                    self.custom_log(job_id, f"📦 Executing Nested Workflow: {wf_name}")
                    
                    from workflow_manager import extract_steps_from_workflow
                    steps = extract_steps_from_workflow(wf_name)
                    
                    for s in steps:
                        if self.jobs[job_id]['status'] == 'stopped': break
                        s_tool = s.get('tool')
                        s_params = s.get('params', {})
                        self.custom_log(job_id, f"  └─ Step: {s.get('description', s_tool)}")
                        
                        if s_tool == "run_search":
                            await manager_agent.run_mission(
                                goal=f"Workflow Step: {s_tool}",
                                plan_override=s_params,
                                status_callback=log_cb
                            )
                    self.custom_log(job_id, f"✅ Workflow '{wf_name}' completed.")

                elif step_type == 'agent':
                    agent_name = step.get('agent')
                    task = step.get('task')
                    self.custom_log(job_id, f"🤖 Orchestrating Agent: {agent_name} for task...")
                    
                    from utils.agent_registry import get_agent_class
                    AgentClass = get_agent_class(agent_name)
                    if AgentClass:
                        sub_agent = AgentClass()
                        if hasattr(sub_agent, 'think_async'):
                            res = await sub_agent.think_async(task)
                            self.custom_log(job_id, f"✅ {agent_name} done.")
                        elif hasattr(sub_agent, 'think'):
                            res = sub_agent.think(task)
                            self.custom_log(job_id, f"✅ {agent_name} done.")
                    else:
                        self.custom_log(job_id, f"❌ Agent {agent_name} not found.")

        else:
            # Legacy Search Loop
            queries = strategy.get('queries', [])
            icp = strategy.get('icp_refined', '')
            limit = strategy.get('limit', 10)
            
            self.custom_log(job_id, f"🎯 Strategy Loaded. {len(queries)} operational queries queued.")
            
            for q in queries:
                if self.jobs[job_id]['status'] == 'stopped': break
                
                self.custom_log(job_id, f"🔎 Executing Search Phase: '{q}'")
                
                mission_plan_override = {
                    "search_queries": [q],
                    "icp_criteria": icp,
                    "limit": limit
                }
                
                # We need to make sure run_mission uses the workspace_id for DB inserts
                # ManagerAgent calls 'add_lead' somewhere. 
                # Currently ManagerAgent doesn't accept workspace_id in run_mission args easily unless we inject it into plan?
                # or we modify ManagerAgent.
                # For now, we rely on the fact that database calls default to 1 if we can't pass it.
                # But we want it to be the correct workspace.
                # Solution: Add workspace_id to plan_override, and update ManagerAgent to respect it?
                # Or use contextvar?
                
                res = await manager_agent.run_mission(
                    goal=f"Execute strategy for {q}", 
                    plan_override=mission_plan_override,
                    status_callback=log_cb
                )
                
                leads_count = len(res.get('leads', []))
                self.custom_log(job_id, f"✅ Batch Complete. Found {leads_count} qualified leads.")
                
                # Simple Manual Sleep for demo
                time.sleep(2)

    def get_jobs(self):
        """Returns list of jobs."""
        return self.jobs

    def get_logs(self, job_id):
        if job_id in self.jobs:
            return self.jobs[job_id]['logs']
        return []

    def stop_job(self, job_id):
        if job_id in self.jobs:
            self.jobs[job_id]['status'] = 'stopped'
            self.custom_log(job_id, "🛑 Stop signal sent.")

    @property
    def is_running(self):
        """Returns True if any job is currently running."""
        return any(j['status'] == 'running' for j in self.jobs.values())
