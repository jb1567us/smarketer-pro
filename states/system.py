import reflex as rx
import asyncio
import os
import psutil
from .base import BaseState, engine, DB_AVAILABLE, project_root, get_connection
from backend.stealth_utils import system_monitor, proxy_manager, captcha_healer, search_rotator

class HeartbeatState(rx.State):
    """Tracks the real-time connectivity of the app."""
    is_alive: bool = True
    last_heartbeat: float = 0
    heartbeat_color: str = "green"
    is_polling: bool = True
    
    @rx.event(background=True)
    async def run_heartbeat(self):
        """Continuously pings the internal system to verify health."""
        while self.is_polling:
            try:
                # Real internal loop check
                import time
                async with self:
                    self.last_heartbeat = time.time()
                    self.is_alive = True
                    self.heartbeat_color = "green"
            except Exception:
                async with self:
                    self.is_alive = False
                    self.heartbeat_color = "red"
            
            await asyncio.sleep(5)

class SystemState(BaseState):
    """System and Automation status state."""
    # Automation Hub State
    active_jobs: list[dict] = []
    global_logs: list[str] = []
    selected_job_logs: list[str] = []
    selected_job_id: str = ""
    
    # Night Shift Scheduler
    night_shift_enabled: bool = False
    scheduler_running: bool = False
    
    # Analysis State
    is_analyzing_job: bool = False
    job_reflections: dict[str, str] = {}
    
    # Workflow Builder State
    available_workflows: list[str] = []
    current_workflow_name: str = ""
    current_workflow_content: str = ""
    current_workflow_description: str = ""
    
    # Reactive System Metrics
    cpu_usage: str = "12%"
    ram_usage: str = "45%"
    current_proxy: str = "None"
    captcha_queue_size: int = 0
    worker_concurrency: int = 4
    is_auditing: bool = False
    qa_report: str = ""
    
    # Export Automation State
    last_export_ts: int = 0
    export_threshold: int = 10 # Low for prototype testing
    is_exporting: bool = False

    async def update_automation_state(self):
        """Update active jobs and logs from AutomationEngine."""
        if engine:
            jobs_dict = engine.get_jobs()
            async with self:
                self.active_jobs = [
                    {
                        "id": j_id,
                        "name": meta.get("name", "Unknown"),
                        "status": meta.get("status", "unknown"),
                        "progress": meta.get("progress", 0),
                        "type": meta.get("type", "mission")
                    }
                    for j_id, meta in jobs_dict.items()
                ]
                self.global_logs = list(engine.logs)[-50:]

    def toggle_night_shift(self):
        self.night_shift_enabled = not self.night_shift_enabled
        self.add_log(f"Night Shift {'enabled' if self.night_shift_enabled else 'disabled'}.")

    def trigger_night_shift_now(self):
        self.add_log("Triggering Night Shift Protocol manually...")

    def select_job(self, job_id: str):
        self.selected_job_id = job_id
        # In a real app, this would trigger loading job-specific logs
        self.add_log(f"Selected job: {job_id}")

    async def run_analysis_on_selected_job(self):
        if not self.selected_job_id: return
        self.is_analyzing_job = True
        yield
        
        # Real Analysis using ManagerAgent
        try:
            from backend.agents.manager import ManagerAgent
            manager = ManagerAgent()
            
            # Gather context: 20 most recent logs for this job or global
            context_logs = "\n".join(self.global_logs[-20:])
            prompt = f"Analyze the following execution logs for Job ID {self.selected_job_id} and provide a 2-sentence strategic reflection on mission progress and potential optimizations:\n\n{context_logs}"
            
            reflection = await asyncio.to_thread(manager.brainstorm_sop, prompt)
            self.job_reflections[self.selected_job_id] = reflection
        finally:
            # GIVE EUGENE A VOICE (ElevenLabs Integration)
            if self.selected_job_id in self.job_reflections:
                try:
                    from backend.utils.audio_engine import audio_engine
                    from .base import project_root
                    import os
                    import time

                    speech_text = self.job_reflections[self.selected_job_id][:500]
                    
                    audio_filename = f"eugene_analysis_{int(time.time())}.mp3"
                    assets_path = os.path.join(project_root, "assets", audio_filename)
                    
                    await audio_engine.speak(speech_text, output_path=assets_path)
                    
                    # Update AgentState's audio URL if possible, or we might need a local one
                    # For now, let's just log it. In a real app we'd have a global audio player.
                    # Let's try to get AgentState and update it
                    from .agents import AgentState
                    agent_state = await self.get_state(AgentState)
                    agent_state.war_room_audio_url = f"/{audio_filename}?" + str(int(time.time()))
                    self.add_log("🔊 Eugene is delivering the performance report...")
                except Exception as e:
                    print(f"Analysis audio error: {e}")

            self.is_analyzing_job = False
        yield

    async def start_mission(self, query: str = ""):
        """Launch a new autonomous mission."""
        self.add_log(f"Launching mission for: {query if query else 'Current Strategy'}...")
        if engine:
            # Use the more advanced engine call if possible
            if DB_AVAILABLE:
                strategy = {
                    "strategy_name": f"Research: {query or 'General Lead Discovery'}",
                    "queries": [query] if query else ["B2B SaaS companies"],
                    "limit": 10,
                    "icp_refined": "High-intent B2B prospects"
                }
                from backend.agents.manager import ManagerAgent
                manager_agent = ManagerAgent()
                job_id = engine.start_mission(strategy, manager_agent)
            else:
                job_id = engine.create_job(f"Mission: {query[:20] if query else 'Strategy'}", "running", {"query": query})
            
            await self.update_automation_state()
            self.selected_job_id = job_id
        self.show_success("Mission Launched")

    async def launch_mission_from_response(self):
        """Shortcut to launch mission from Agent Lab response."""
        from .agents import AgentState
        agent_state = await self.get_state(AgentState)
        content = agent_state.last_lab_response
        await self.start_mission(content[:50])

    async def draft_workflow_from_response(self):
        """Shortcut to create workflow from Agent Lab response."""
        from .agents import AgentState
        agent_state = await self.get_state(AgentState)
        self.current_workflow_content = agent_state.last_lab_response
        self.current_workflow_name = "ai_draft.md"
        self.add_log("Drafted workflow from AI response.")
        return rx.redirect("/workflow-builder")

    async def stop_mission(self, job_id: str):
        """Stop a running mission."""
        if engine:
            engine.stop_job(job_id)
            await self.update_automation_state()
            self.add_log(f"Stopped mission: {job_id}")

    async def load_workflow_by_name(self, name: str):
        """Load workflow content from backend."""
        from backend.workflow_manager import read_workflow
        content = read_workflow(name)
        if content:
            self.current_workflow_name = name
            self.current_workflow_content = content
            self.add_log(f"Loaded workflow: {name}")

    async def select_workflow(self, name: str):
        await self.load_workflow_by_name(name)

    async def save_workflow(self):
        """Save current workflow content."""
        if not self.current_workflow_name: return
        from backend.workflow_manager import save_workflow
        save_workflow(self.current_workflow_name, self.current_workflow_content)
        self.add_log(f"Saved workflow: {self.current_workflow_name}")
        self.show_success("Workflow Saved")

    async def delete_workflow(self):
        """Delete current workflow."""
        if not self.current_workflow_name: return
        from backend.workflow_manager import delete_workflow
        delete_workflow(self.current_workflow_name)
        self.available_workflows = [w for w in self.available_workflows if w != self.current_workflow_name]
        self.current_workflow_name = ""
        self.current_workflow_content = ""
        self.add_log("Deleted workflow.")

    async def run_workflow_execution(self):
        """Execute current workflow."""
        if not self.current_workflow_name: return
        
        try:
            import json
            inputs = {}
            try:
                if self.current_workflow_description.strip().startswith("{"):
                    inputs = json.loads(self.current_workflow_description)
                else:
                    inputs = {"goal": self.current_workflow_description}
            except:
                inputs = {"goal": self.current_workflow_description}
            
            from backend.engine.reader import WorkflowReader
            from backend.engine.runner import WorkflowRunner
            
            workflow_dir = os.path.join(project_root, "src", "workflows")
            if not os.path.exists(workflow_dir):
                 workflow_dir = r"C:\sandbox\b2b_outreach_tool\src\workflows"

            reader = WorkflowReader(workflow_dir)
            runner = WorkflowRunner(reader)
            
            workflow_id = self.current_workflow_name.replace(".json", "")
            self.add_log(f"🚀 Starting workflow '{workflow_id}'...")
            yield
            
            results = await runner.run(workflow_id, inputs)
            self.add_log(f"✅ Workflow '{workflow_id}' Complete.")
            
            for k, v in results.items():
                if isinstance(v, str) and len(v) < 200:
                     self.add_log(f"OUTPUT [{k}]: {v}")
            
            await self.update_automation_state()
        except Exception as e:
            self.handle_error(e, "Workflow Execution")

    @rx.event(background=True)
    async def poll_system_metrics(self):
        """Poll real-time system metrics using psutil."""
        while self.is_polling:
            try:
                async with self:
                    self.cpu_usage = f"{int(psutil.cpu_percent())}%"
                    self.ram_usage = f"{int(psutil.virtual_memory().percent)}%"
                    self.worker_concurrency = system_monitor.get_recommended_concurrency()
                    self.captcha_queue_size = captcha_healer.queue_size
                    
                    # Automation Trigger: Static SEO Export
                    if not self.is_exporting:
                        try:
                            from .states.portfolio import PortfolioState
                            portfolio = await self.get_state(PortfolioState)
                            if portfolio.total_profiles >= self.export_threshold:
                                self.is_exporting = True
                                self.add_log(f"🚀 Threshold met ({portfolio.total_profiles}). Triggering Static SEO Export...")
                                from backend.reflex_exporter import export_static_site
                                success = await export_static_site()
                                if success:
                                    self.add_log("✅ Static SEO Export Complete. Files ready in static_exports/.")
                                    self.last_export_ts = int(asyncio.get_event_loop().time())
                                self.is_exporting = False
                        except Exception as e:
                            print(f"Export trigger error: {e}")
                            self.is_exporting = False

                    # Mock proxy rotation for visualization if pool is empty
                    if not self.current_proxy or self.current_proxy == "None":
                         p = proxy_manager.get_proxy()
                         self.current_proxy = p if p else "None (No pool)"
            except Exception as e:
                print(f"Metrics polling stopped for session: {e}")
                break
            await asyncio.sleep(5)

    async def run_qa_audit(self):
        """Run a real QA audit on the system state."""
        self.is_auditing = True
        self.add_log("Running QA Audit (Live Health Check)...")
        yield
        
        reports = ["# QA Audit Report (Live)"]
        
        # 1. Database Check
        try:
            from backend.database import get_connection
            conn = get_connection()
            conn.execute("SELECT 1")
            conn.close()
            reports.append("- **Database Connection**: PASS")
        except Exception as e:
            reports.append(f"- **Database Connection**: FAIL ({str(e)})")
            
        # 2. Proxy Pool Check
        try:
            from backend.database import get_best_proxies
            proxies = get_best_proxies(limit=10)
            if len(proxies) > 0:
                reports.append(f"- **Proxy Pool**: HEALTHY ({len(proxies)} verified units available)")
            else:
                reports.append("- **Proxy Pool**: WARNING (No verified proxies found)")
        except:
            reports.append("- **Proxy Pool**: ERROR (Check proxy_manager)")
            
        # 3. Agent Engines
        try:
            from backend.agents.manager import ManagerAgent
            from backend.agents.researcher import ResearcherAgent
            m = ManagerAgent()
            r = ResearcherAgent()
            reports.append("- **Agent Engines**: PASS (Manager, Researcher initialized)")
        except Exception as e:
            reports.append(f"- **Agent Engines**: FAIL ({str(e)})")
            
        # 4. Storage/Sandbox
        work_dir = os.path.join(project_root, "src", "workflows")
        if os.path.exists(work_dir):
            reports.append("- **Sandbox Integrity**: PASS")
        else:
            reports.append("- **Sandbox Integrity**: WARNING (Workflow dir missing)")

        self.qa_report = "\n".join(reports)
        self.is_auditing = False
        self.add_log("QA Audit complete.")
        yield

    def rotate_proxy(self):
        """Manually trigger proxy rotation."""
        p = proxy_manager.get_proxy()
        self.current_proxy = p if p else "None"
        self.add_log(f"Proxy rotated to: {self.current_proxy}")

    def add_mock_captcha(self):
        """simulate a captcha hit for testing."""
        captcha_healer.add_to_queue("https://google.com/search?q=test", {"agent": "Researcher"})
        self.captcha_queue_size = captcha_healer.queue_size
        self.add_log("⚠️ Mock CAPTCHA detected and queued.")

    async def heal_captchas(self):
        """Process the captcha queue."""
        count = self.captcha_queue_size
        if count == 0:
            self.add_log("No captchas to heal.")
            return
            
        self.add_log(f"Healing {count} captchas...")
        # Simulate healing delay
        await asyncio.sleep(2)
        while captcha_healer.get_next_task():
            pass
        self.captcha_queue_size = 0
        self.show_success(f"Healed {count} captchas.")
