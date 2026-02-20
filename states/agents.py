import reflex as rx
import asyncio
import typing
from .base import BaseState, engine, DB_AVAILABLE

class AgentState(BaseState):
    """AI and Agent management state."""
    # AI Assistant
    ai_assistant_input: str = ""
    ai_assistant_history: list[dict] = []
    is_assistant_thinking: bool = False
    
    # Agent Lab
    lab_input: str = ""
    active_lab_agent: str = "Researcher"
    last_lab_response: dict = {}
    last_lab_context: str = ""
    refinement_instruction: str = ""
    is_agent_thinking: bool = False
    
    # Specialized Agent Inputs
    agent_platform: str = "instagram"
    agent_limit: int = 10
    agent_min_followers: str = ""
    agent_max_followers: str = ""
    agent_mode: str = "Single Task"
    
    # Agent Factory
    new_agent_name: str = ""
    new_agent_role: str = ""
    new_agent_goal: str = ""
    
    # Morning Briefing
    morning_briefing_content: str = ""
    is_loading_briefing: bool = False
    is_generating_workflow: bool = False

    # Strategy War Room
    war_room_input: str = ""
    war_room_messages: list[dict] = [
        {"role": "assistant", "content": "Welcome to the Strategy War Room. I am Eugene. Pitch your idea, and I'll help you refine it into a high-performance SOP."}
    ]
    is_war_room_thinking: bool = False
    war_room_audio_url: str = ""

    async def send_war_room_message(self):
        """Send a message to Eugene in the War Room for collaborative strategy."""
        if not self.war_room_input: return
        
        user_input = self.war_room_input
        user_msg = {"role": "user", "content": user_input}
        self.war_room_messages.append(user_msg)
        self.war_room_input = ""
        self.is_war_room_thinking = True
        yield
        
        try:
            from backend.agents.manager import ManagerAgent
            manager = ManagerAgent()
            
            # Use multi-turn collaboration logic
            result = await manager.collaborate_on_strategy(self.war_room_messages[:-1], user_input)
            
            response_text = result.get("response", "I'm processing that strategy.")
            self.war_room_messages.append({"role": "assistant", "content": response_text})
            
            # If a physical workflow file was generated, inform the user
            if result.get("file"):
                self.add_log(f"Eugene drafted a base workflow: {result['file']}")
                
        except Exception as e:
            self.war_room_messages.append({"role": "assistant", "content": f"Error consulting Eugene: {e}"})
        finally:
            # 3. GIVE EUGENE A VOICE (ElevenLabs Integration)
            try:
                from backend.utils.audio_engine import audio_engine
                from backend.config import project_root
                import os
                import time

                last_msg = self.war_room_messages[-1]["content"]
                # Only speak first 500 chars to save quota and time
                speech_text = last_msg[:500] 
                
                audio_filename = f"eugene_voice_{int(time.time())}.mp3"
                assets_path = os.path.join(project_root, "assets", audio_filename)
                
                # Cleanup old voice files? (Optional, but good practice)
                # For now just generate new one
                audio_data = await audio_engine.speak(speech_text, output_path=assets_path)
                
                if audio_data:
                    self.war_room_audio_url = f"/{audio_filename}"
                    self.add_log("🔊 Eugene is speaking...")
            except Exception as audio_err:
                print(f"Audio generation error: {audio_err}")

            self.is_war_room_thinking = False
            yield

    def clear_ai_assistant_history(self):
        self.ai_assistant_history = []
        self.add_log("AI Assistant history cleared.")

    def download_assistant_history(self):
        """Downloads the current AI Assistant chat history as JSON."""
        import json
        history_json = json.dumps(self.ai_assistant_history, indent=2)
        return rx.download(data=history_json, filename="assistant_history.json")

    def download_last_lab_response(self):
        """Downloads the last Agent Lab response."""
        if not self.last_lab_response:
            return rx.window_alert("No response to download.")
        return rx.download(data=self.last_lab_response, filename="agent_result.json")

    @rx.var
    def is_response_json(self) -> bool:
        if isinstance(self.last_lab_response, dict):
            return True
        if not isinstance(self.last_lab_response, str):
            return False
        return self.last_lab_response.strip().startswith("{")

    @rx.var
    def results_list(self) -> list[dict]:
        """Returns the results list if available, or empty list."""
        if isinstance(self.last_lab_response, dict) and "results" in self.last_lab_response:
            return self.last_lab_response["results"]
        return []

    async def run_agent_task(self, agent_name: str, task: str):
        """Run a specific agent task from the Lab."""
        if not task: return
        
        async with self:
            self.is_agent_thinking = True
            self.add_log(f"Running {agent_name} task: {task[:50]}...")
        yield
        
        try:
            from backend.agents.researcher import ResearcherAgent
            from backend.agents.copywriter import CopywriterAgent
            from backend.agents.manager import ManagerAgent
            from backend.agents.influencer_agent import InfluencerAgent
            
            agent_map = {
                "Researcher": ResearcherAgent,
                "Copywriter": CopywriterAgent,
                "Manager": ManagerAgent,
                "Influencer Scout": InfluencerAgent,
                "SEO Expert": ResearcherAgent,
            }
            
            agent_class = agent_map.get(agent_name, ResearcherAgent)
            agent = agent_class()
            
            # Add UI logging callback for agents that support it
            agent.status_callback = lambda msg: self.add_log(msg)
            
            # Intelligently handle sync/async agents
            # For Influencer Scout, pass structured data from UI state
            if agent_name == "Influencer Scout":
                task_payload = {
                    "niche": task,  # The text input is the niche
                    "platform": self.agent_platform,
                    "limit": self.agent_limit,
                    "min_followers": self.agent_min_followers,
                    "max_followers": self.agent_max_followers,
                    # Optional: City/Audience could be parsed from task or added to UI later
                }
                if hasattr(agent, "think_async"):
                    response = await agent.think_async(task_payload)
                elif hasattr(agent, "think"):
                    response = await asyncio.to_thread(agent.think, task_payload)
                else:
                    response = await asyncio.to_thread(agent.run, task_payload)
            elif agent_name == "Researcher":
                # Pass structured payload to Researcher
                task_payload = {
                    "query": task,
                    "limit": self.agent_limit,
                    "mode": self.agent_mode
                }
                if hasattr(agent, "think_async"):
                    response = await agent.think_async(task_payload)
                elif hasattr(agent, "think"):
                    response = await asyncio.to_thread(agent.think, task_payload)
                else:
                    # Fallback for old agents
                    response = await asyncio.to_thread(agent.run, task)
            else:
                # Standard Agent Behavior
                if hasattr(agent, "think_async"):
                    response = await agent.think_async(task)
                elif hasattr(agent, "think"):
                    response = await asyncio.to_thread(agent.think, task)
                else:
                    response = await asyncio.to_thread(agent.run, task)
            
            async with self:
                # Normalize response format (some agents return lists, others dicts)
                if isinstance(response, list):
                    self.last_lab_response = {"results": response, "count": len(response)}
                elif isinstance(response, dict):
                    self.last_lab_response = response
                else:
                    self.last_lab_response = {"result": str(response)}
                
                self.last_lab_context = task
                self.add_log(f"{agent_name} task complete.")
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            async with self:
                self.add_log(f"Agent error: {str(e)}")
                print(f"[AgentLab] Full error:\n{error_details}")  # Print to console for debugging
        finally:
            self.is_agent_thinking = False
            yield

    async def refine_agent_output(self):
        """Refine the last agent output based on feedback."""
        if not self.refinement_instruction or not self.last_lab_response:
            return
            
        async with self:
            self.is_agent_thinking = True
            self.add_log(f"Refining output with: {self.refinement_instruction}")
        yield
        
        try:
            from backend.agents.researcher import ResearcherAgent
            from backend.agents.copywriter import CopywriterAgent
            from backend.agents.manager import ManagerAgent
            from backend.agents.influencer_agent import InfluencerAgent
            
            agent_map = {
                "Researcher": ResearcherAgent,
                "Copywriter": CopywriterAgent,
                "Manager": ManagerAgent,
                "Influencer Scout": InfluencerAgent,
                "SEO Expert": ResearcherAgent,
            }
            
            agent_class = agent_map.get(self.active_lab_agent, ResearcherAgent)
            agent = agent_class()
            
            new_response = await asyncio.to_thread(
                agent.tune,
                context=self.last_lab_context,
                previous_response=self.last_lab_response,
                instructions=self.refinement_instruction
            )
            
            async with self:
                self.last_lab_response = new_response
                self.refinement_instruction = ""
                self.add_log("Refinement complete.")
        except Exception as e:
            async with self:
                self.add_log(f"Refinement error: {str(e)}")
        finally:
            self.is_agent_thinking = False
            yield

    async def run_morning_briefing(self):
        """Ask Eugene for a morning briefing."""
        from backend.agents.manager import ManagerAgent
        
        self.is_loading_briefing = True
        yield
        
        try:
            manager = ManagerAgent()
            niche = "AI Automation & B2B Sales" 
            briefing = await asyncio.to_thread(manager.report_morning_briefing, niche)
            
            self.morning_briefing_content = briefing
            self.add_log("☀️ Eugene delivered the Morning Briefing.")
            self.show_success("Morning Briefing Ready")
        except Exception as e:
            self.handle_error(e, "Morning Briefing")
        finally:
            # GIVE EUGENE A VOICE (ElevenLabs Integration)
            if self.morning_briefing_content:
                try:
                    from backend.utils.audio_engine import audio_engine
                    from backend.config import project_root
                    import os
                    import time

                    # Speak the first 500 chars of the briefing
                    speech_text = self.morning_briefing_content[:500]
                    
                    audio_filename = f"eugene_briefing_{int(time.time())}.mp3"
                    assets_path = os.path.join(project_root, "assets", audio_filename)
                    
                    await audio_engine.speak(speech_text, output_path=assets_path)
                    self.war_room_audio_url = f"/{audio_filename}?" + str(int(time.time())) # Append timestamp to force reload
                    self.add_log("🔊 Eugene is delivering the briefing audio...")
                except Exception as e:
                    print(f"Briefing audio error: {e}")

            self.is_loading_briefing = False

    async def create_custom_agent(self):
        """Create a new custom agent configuration and persist to DB."""
        if not self.new_agent_name or not self.new_agent_role:
            return
            
        self.add_log(f"Architecting custom agent: {self.new_agent_name}...")
        
        try:
            from backend.database import create_custom_agent
            
            # Persist to database
            agent_id = await asyncio.to_thread(
                create_custom_agent,
                name=self.new_agent_name,
                role=self.new_agent_role,
                goal=self.new_agent_goal,
                system_prompt=f"You are {self.new_agent_name}, {self.new_agent_role}. Your goal: {self.new_agent_goal}"
            )
            
            if agent_id:
                self.show_success(f"Agent '{self.new_agent_name}' Created")
                self.add_log(f"Custom agent '{self.new_agent_name}' saved to registry (ID: {agent_id}).")
                
                # Reset fields
                self.new_agent_name = ""
                self.new_agent_role = ""
                self.new_agent_goal = ""
            else:
                self.handle_error("Database insertion failed", "Agent Factory")
        except Exception as e:
            self.handle_error(e, "Agent Factory")

    async def draft_strategic_workflow(self):
        """Convert briefing insights into a functional draft workflow."""
        if not self.morning_briefing_content: return
        self.is_generating_workflow = True
        yield
        
        try:
            from backend.agents.manager import ManagerAgent
            manager = ManagerAgent()
            
            # Ask Eugene to design a workflow based on the briefing
            result = await manager.propose_strategic_workflows(self.morning_briefing_content)
            
            if result.get("status") == "success":
                from .system import SystemState
                system_state = await self.get_state(SystemState)
                
                # Convert JSON design to a readable markdown for the builder
                import json
                design_json = json.dumps(result.get("design", {}), indent=2)
                
                system_state.current_workflow_content = design_json
                system_state.current_workflow_name = f"strategic_{result.get('goal', 'mission')[:20].replace(' ', '_')}.json"
                
                self.add_log(f"✅ Drafted strategic workflow: {system_state.current_workflow_name}")
                yield rx.redirect("/workflow-builder")
            else:
                self.handle_error(result.get("error", "Drafting failed"), "Strategy Architect")
        except Exception as e:
            self.handle_error(e, "Strategy Architect")
        finally:
            self.is_generating_workflow = False
            yield
