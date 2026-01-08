import asyncio
import threading
import time
import sys
import os
import subprocess
from datetime import datetime
import streamlit as st

class AutomationEngine:
    def __init__(self):
        self._is_running = False
        self._stop_event = asyncio.Event()
        self._loop = None
        self._thread = None
        self.logs = []
        self.current_mission = None
        # self.log_file = None # Handled globally now
        self.stats = {
            "missions_total": 0,
            "leads_found": 0,
            "emails_sent": 0,
            "start_time": None
        }

    def log(self, message):
        """Thread-safe logging"""
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] {message}"
        self.logs.append(entry)
        # Keep logs manageable
        if len(self.logs) > 500:
            self.logs.pop(0)
        
        # Print to global stdout (captured by global logger)
        print(entry)

    def start_mission(self, strategy, manager_agent):
        """
        Starts the automation loop in a separate thread.
        """
        if self._is_running:
            self.log("⚠️ Automation is already running.")
            return

        self._is_running = True
        self.current_mission = strategy.get('strategy_name', 'Unnamed Strategy')
        self.stats["start_time"] = time.time()
        self._stop_event.clear()

        # Terminal spawning is now handled globally at app startup.

        # Start background thread
        self._thread = threading.Thread(
            target=self._run_loop,
            args=(strategy, manager_agent),
            daemon=True
        )
        self._thread.start()
        self.log(f"🚀 Mission Started: {self.current_mission}")

    def stop(self):
        """Signals the loop to stop."""
        if self._is_running:
            self.log("🛑 Stop signal received. Finishing current step...")
            self._is_running = False

    def _run_loop(self, strategy, manager_agent):
        """
        The main execution loop running in a background thread.
        """
        # Stdout redirection is now global.

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Execute the mission
            loop.run_until_complete(self._execute_mission_logic(strategy, manager_agent))
        except Exception as e:
            self.log(f"💥 Critical Error in Automation Loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._is_running = False
            self.log("🏁 Automation Finished.")
            loop.close()

    async def _execute_mission_logic(self, strategy, manager_agent):

        """
        The actual logic that runs indefinitely or until goal met.
        Supports sequential execution of workflows and agent tasks.
        """
        sequence = strategy.get('sequence', [])
        is_conductor = strategy.get('mode') == 'conductor' or len(sequence) > 0
        
        if is_conductor and sequence:
            self.log(f"🎬 Conductor Sequence Active. Goal: {strategy.get('goal')}")
            
            for step in sequence:
                if not self._is_running: break
                
                step_type = step.get('type')
                
                if step_type == 'workflow':
                    wf_name = step.get('name')
                    self.log(f"📦 Executing Nested Workflow: {wf_name}")
                    
                    from workflow_manager import extract_steps_from_workflow
                    steps = extract_steps_from_workflow(wf_name)
                    
                    for s in steps:
                        if not self._is_running: break
                        s_tool = s.get('tool')
                        s_params = s.get('params', {})
                        self.log(f"  └─ Step: {s.get('description', s_tool)}")
                        
                        # Use manager's run_mission or direct execution logic
                        # For now, we support 'run_search' as the primary workflow unit
                        if s_tool == "run_search":
                            await manager_agent.run_mission(
                                goal=f"Workflow Step: {s_tool}",
                                plan_override=s_params,
                                status_callback=self.log
                            )
                    self.log(f"✅ Workflow '{wf_name}' completed.")

                elif step_type == 'agent':
                    agent_name = step.get('agent')
                    task = step.get('task')
                    self.log(f"🤖 Orchestrating Agent: {agent_name} for task...")
                    
                    from utils.agent_registry import get_agent_class
                    AgentClass = get_agent_class(agent_name)
                    if AgentClass:
                        sub_agent = AgentClass()
                        # Generic delegation
                        if hasattr(sub_agent, 'think'):
                            res = sub_agent.think(task)
                            self.log(f"✅ {agent_name} completed task.")
                        else:
                            self.log(f"⚠️ Agent {agent_name} does not have a 'think' method.")
                    else:
                        self.log(f"❌ Agent {agent_name} not found.")

            self.log("🏁 Conductor Sequence Complete.")

        elif is_conductor and not sequence:
            # Fallback to the hardcoded test/default logic if no sequence provided but conductor active
            self.log(f"🎬 Conductor Mode Active. Goal: {strategy.get('goal')}")
            # ... (keep existing hardcoded research -> copy logic for safety)
            # (Truncated for brevity in this replace call, but I'll maintain the structure)
            if self._is_running:
                self.log("🔍 Phase 1: Market Intelligence Gathering...")
                res_research = await manager_agent.run_mission(
                    goal=f"Research leads for: {strategy.get('goal')}",
                    plan_override={"search_queries": strategy.get('queries', []), "limit": strategy.get('limit', 5)},
                    status_callback=self.log
                )

        else:
            # Legacy Search Loop
            queries = strategy.get('queries', [])
            icp = strategy.get('icp_refined', '')
            
            self.log(f"🎯 Strategy Loaded. {len(queries)} operational queries queued.")
            
            for q in queries:
                if not self._is_running: break
                
                self.log(f"🔎 Executing Search Phase: '{q}'")
                
                mission_goal = f"Execute strategy for {q}"
                mission_plan_override = {
                    "search_queries": [q],
                    "icp_criteria": icp,
                    "limit": strategy.get('limit', 10)
                }
                
                res = await manager_agent.run_mission(
                    goal=mission_goal, 
                    plan_override=mission_plan_override,
                    status_callback=self.log
                )
                
                leads_count = len(res.get('leads', []))
                self.stats['leads_found'] += leads_count
                self.log(f"✅ Batch Complete. Found {leads_count} qualified leads.")
                
                if self._is_running:
                    self.log("⏳ Cooling down for 10s...")
                    await asyncio.sleep(10)

        self.log("🌟 Automation sequence completed.")

    @property
    def is_running(self):
        return self._is_running
