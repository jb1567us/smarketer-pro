import asyncio
import threading
import time
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

    def start_mission(self, strategy, manager_agent):
        """
        Starts the automation loop in a separate thread.
        strategy: Dict containing the PM's strategy (queries, niched, etc.)
        manager_agent: Instance of ManagerAgent
        """
        if self._is_running:
            self.log("⚠️ Automation is already running.")
            return

        self._is_running = True
        self.current_mission = strategy.get('strategy_name', 'Unnamed Strategy')
        self.stats["start_time"] = time.time()
        self._stop_event.clear()

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
            # self._stop_event.set() # If we use async events

    def _run_loop(self, strategy, manager_agent):
        """
        The main execution loop running in a background thread.
        Needs its own event loop since it's a new thread.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Execute the mission
            # We wrap the async call
            loop.run_until_complete(self._execute_mission_logic(strategy, manager_agent))
        except Exception as e:
            self.log(f"💥 Critical Error in Automation Loop: {e}")
        finally:
            self._is_running = False
            self.log("🏁 Automation Finished.")
            loop.close()

    async def _execute_mission_logic(self, strategy, manager_agent):
        """
        The actual logic that runs indefinitely or until goal met.
        """
        queries = strategy.get('queries', [])
        icp = strategy.get('icp_refined', '')
        
        self.log(f"🎯 Strategy Loaded. {len(queries)} operational queries queued.")
        
        for q in queries:
            if not self._is_running: break
            
            self.log(f"🔎 Executing Search Phase: '{q}'")
            
            # Construct a "Plan" object that ManagerAgent accepts
            # We override the Manager's internal planning by passing this directly
            # Note: We need to modify ManagerAgent to accept this override
            
            mission_goal = f"Execute strategy for {q}"
            mission_plan_override = {
                "search_queries": [q], # Process one by one in this loop
                "icp_criteria": icp,
                "value_proposition": strategy.get('value_prop', 'Standard Outreach'), # You might want to add this to PM output
                "channels": ["email"], # Defaulting for now
                "limit": 10 # Batch size per query
            }
            
            # Call Manager Agent
            # usage: await manager.run_mission(goal, plan_override=...)
            res = await manager_agent.run_mission(
                goal=mission_goal, 
                context=None, 
                plan_override=mission_plan_override,
                status_callback=self.log
            )
            
            leads_count = len(res.get('leads', []))
            self.stats['leads_found'] += leads_count
            self.log(f"✅ Batch Complete. Found {leads_count} qualified leads.")
            
            # Sleep between batches to simulate human pace / safety
            if self._is_running:
                self.log("⏳ Cooling down for 10s...")
                await asyncio.sleep(10)

        self.log("🌟 All strategic queries processed.")

    @property
    def is_running(self):
        return self._is_running
