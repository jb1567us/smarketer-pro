from .base import BaseAgent
import json
from utils.agent_registry import list_available_agents
from memory import Memory
try:
    from src.flow.flow_engine import flow_engine
except ImportError:
    from flow.flow_engine import flow_engine
import os

class ManagerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Manager & Orchestrator",
            goal="Oversee the outreach process, execute tasks via tools, and manage workflows.",
            backstory=(
                "You are the Manager & Orchestrator (Python Coder Variant), inspired by LOLLMS 'coding_python'. "
                "Unlike a passive chat bot, you actively plan, delegate, and when necessary, write self-contained "
                "Python scripts to solve complex logic. Your primary mode of operation is: Plan -> Delegate -> Code -> Execute. "
                "You are precise, ensuring all tools and scripts are error-free and robust."
            ),
            provider=provider
        )
        self.memory = Memory()

    def _classify_intent(self, user_input):
        """
        Classifies the user's intent to route to the correct specialist or tool.
        Categories:
        - CREATE_ASSET: Generating new content (Image, Reference, Video, Code).
        - RETRIEVE_INFO: Searching the web, DB, or memory (Find, Search, Get).
        - EXECUTE_ACTION: Running a workflow, mission, or complex task.
        - CHAT: General conversation, logic, planning.
        """
        classification_prompt = (
            "You are an Intent Classifier. Analyze the user request.\n"
            "Categories:\n"
            "1. CREATE_ASSET: User wants to generate/create something new (e.g., 'generate image', 'write email', 'draw', 'make').\n"
            "   - Entity: What is being created? (e.g., 'Image', 'Email', 'Video')\n"
            "2. RETRIEVE_INFO: User wants to find existing info (e.g., 'find', 'search', 'look up', 'get').\n"
            "   - Entity: What is being searched for? (e.g., 'Information', 'Image', 'Lead')\n"
            "3. EXECUTE_ACTION: User wants to run a process (e.g., 'run workflow', 'start mission', 'install wordpress', 'build site').\n"
            "4. CHAT: General conversation or question.\n\n"
            f"Request: '{user_input}'\n\n"
            "Return JSON: {'intent': str, 'entity': str, 'instructions': str}"
        )
        
        # We use a separate cheap call for this if possible, or just the main provider
        try:
            res = self.provider.generate_json(classification_prompt)
            if isinstance(res, list):
                res = res[0]
            if not isinstance(res, dict):
                raise ValueError("Deep seek returned non-dict")
            return res
        except Exception as e:
            self.logger.warning(f"[Manager] Intent classification failed: {e}")
            return {"intent": "CHAT", "entity": "None", "instructions": user_input}

    def think(self, user_input, intent_history=None, available_tools=None):
        """
        Decides on the next action based on user input.
        """
        from utils.agent_registry import AGENT_METADATA
        from workflow_manager import list_workflows
        
        # 1. Classify Intent
        self.logger.info(f"Analyzing user input: '{user_input}'...")
        
        # --- AGGRESSIVE PRE-THINKING GUARDRAIL ---
        u_in = user_input.lower()
        is_site_build = ("build" in u_in or "install" in u_in or "create" in u_in) and ("site" in u_in or "wordpress" in u_in or "wp" in u_in)
        if is_site_build:
            self.logger.info("Site build request detected. Intercepting before LLM call.")
            domain = "lookoverhere.xyz"
            directory = ""
            import re
            match = re.search(r'([a-z0-9.-]+\.[a-z]{2,})(/[a-z0-9_-]+)?', u_in)
            if match:
                domain = match.group(1)
                if match.group(2):
                    directory = match.group(2).lstrip('/')
            
            return {
                "tool": "build_wordpress_site",
                "params": {
                    "goal": user_input,
                    "domain": domain,
                    "directory": directory
                },
                "reply": f"Understood. I'm initiating the WordPress site build for you at {domain}/{directory} now."
            }

        classification = self._classify_intent(user_input)
        intent = classification.get("intent", "CHAT")
        entity = classification.get("entity", "")
        self.logger.info(f"Classified Intent: {intent} (Entity: {entity})")
        
        # 2. Build Context
        expertise_lines = []
        for name, meta in AGENT_METADATA.items():
            if name == "manager": continue
            expertise_lines.append(f"- {name.upper()}: {meta['role']}. Expertise: {meta['expertise']}. Capabilities: {', '.join(meta['capabilities'])}")
        agent_expertise = "\n".join(expertise_lines)
        available_workflows = ", ".join(list_workflows()) if list_workflows() else "None"
        memory_context = self.memory.get_context()

        tools_desc = (
            "1. run_search(query, niche, profile): Search for leads.\n"
            "2. save_workflow(name): Save current steps as a workflow.\n"
            "3. list_workflows(): List available saved workflows.\n"
            "4. run_workflow(name): Load and execute a saved workflow.\n"
            "5. delegate_task(agent_name, instructions): Delegate to a specialized agent. agent_name must match one of the Available Specialists listed above (e.g. 'RESEARCHER').\n"
            "6. conductor_mission(goal, sequence): Launch a full-automation mission.\n"
            "7. learn_insight(insight): Save a learned pattern or user preference to memory for future proactivity.\n"
            "8. chat(message): Just reply to the user.\n"
            "9. run_flow_mission(workflow_name, inputs): Execute a graph-based workflow (found in src/workflows).\n"
            "10. build_wordpress_site(goal, domain, directory): Directly trigger a WordPress installation and site setup. Use this for requests like 'build a site about X'.\n"
            "11. list_available_nodes(): List all registered nodes in the Engine.\n"
            "12. design_workflow(goal, nodes_description): Create a new workflow JSON file based on a goal.\n"
            "13. execute_workflow(workflow_name, payload): Execute a specific workflow by name via the Engine.\n"
        )
        
        # 3. Dynamic Prompt Injection based on Intent
        intent_instruction = ""
        if intent == "CREATE_ASSET":
            if "Image" in entity or "Picture" in entity:
                 intent_instruction = "Matches Intent: CREATE_ASSET (Image). MUST delegate to 'IMAGE' agent."
            elif "Video" in entity:
                 intent_instruction = "Matches Intent: CREATE_ASSET (Video). MUST delegate to 'VIDEO' agent."
            elif "Email" in entity or "Copy" in entity:
                 intent_instruction = "Matches Intent: CREATE_ASSET (Copy). MUST delegate to 'COPYWRITER'."
            elif "Idea" in entity or "Strategy" in entity or "Concept" in entity:
                 intent_instruction = "Matches Intent: CREATE_ASSET (Idea). MUST delegate to 'BRAINSTORMER'."
            elif "Agent" in entity:
                 intent_instruction = "Matches Intent: CREATE_ASSET (Custom Agent). MUST delegate to 'CHAT' (Manager handles this) or 'BRAINSTORMER' for ideas."

        elif intent == "EXECUTE_ACTION":
            if "wordpress" in user_input.lower() or "site" in user_input.lower():
                intent_instruction = "Matches Intent: EXECUTE_ACTION (WordPress). You MUST use `build_wordpress_site`."
            else:
                intent_instruction = "Matches Intent: EXECUTE_ACTION. Use `execute_workflow` or `run_flow_mission`."

        elif intent == "RETRIEVE_INFO":
            if "Image" in entity:
                 intent_instruction = "Matches Intent: RETRIEVE_INFO (Image Search). MUST delegate to 'RESEARCHER' with instruction 'Find images of...'."
            else:
                 intent_instruction = "Matches Intent: RETRIEVE_INFO. MUST delegate to 'RESEARCHER' or use 'run_search'."

        system_prompt = (
            "You are the Manager Agent (CONDUCTOR). You orchestrate specialists and string workflows. "
            "CRITICAL: Be proactive and contemplative. Don't just follow orders; think about the goal.\n"
            "rules:\n"
            f"0. INTENT DETECTED: {intent} ({entity}). {intent_instruction}\n"
            "1. DELEGATE: If a task requires a specialist (e.g., 'generate image' -> IMAGE, 'find/search for X' -> RESEARCHER, 'write email' -> COPYWRITER, 'ideas/strategy' -> BRAINSTORMER), you MUST use `delegate_task`.\n"
            "2. NO LAZY REPLIES: NEVER just reply 'Done' or 'Okay'. If you did not call a tool, you have NOT done the task.\n"
            "3. LEARN: Notice patterns in user requests.\n"
            "4. SUGGEST: Proactively suggest tools or workflows.\n"
            "5. STYLE: Adopt the user's communication style. Be a thought partner.\n"
            "6. WORKFLOW ARCHITECT: If the user asks to create/design a workflow, use `design_workflow`. If asking to run one, use `execute_workflow`.\n"
            "7. PROACTIVE EXECUTION: If the user says 'build', 'install', 'create site', or 'run', you MUST use a tool. DO NOT JUST CHAT.\n\n"
            "Available Specialists:\n"
            f"{agent_expertise}\n"
            "Note: When delegating, use the EXACT capitalized name (e.g. 'RESEARCHER', 'IMAGE') as the agent_name identifier.\n\n"
            f"Available Workflows: {available_workflows}\n\n"
            "Context (Memory & Feedback):\n"
            f"{memory_context}\n\n"
            "Tools:\n"
            f"{tools_desc}\n\n"
            "CRITICAL RESPONSE FORMAT:\n"
            "You MUST return valid JSON matching this schema exactly:\n"
            "{\n"
            "  \"tool\": \"string (name of the tool to use, e.g. 'delegate_task', 'chat', 'run_search')\",\n"
            "  \"params\": {\n"
            "    \"arg_name\": \"value\" \n"
            "  },\n"
            "  \"reply\": \"string (explanation of what you are doing)\"\n"
            "}\n"
            "Do not return markdown blocks or plain text. JUST the JSON."
        )
        
        history_str = ""
        if intent_history:
            history_str = f"History:\n{json.dumps(intent_history, indent=2)}\n\n"

        full_prompt = (
            f"{system_prompt}\n\n"
            f"{history_str}"
            f"User Input: {user_input}\n"
        )
        
        self.logger.debug(f"Generating execution plan (LLM Call)...")
        try:
            response = self.provider.generate_json(full_prompt)
            if isinstance(response, list):
                response = response[0]
            
            # --- FALLBACK: Intent-Based Override ---
            # If LLM refuses (returns None/Empty) but we know the intent is Retrieval/Creation, force it.
            tool_name = response.get('tool') if response else None
            
            if not tool_name:
                self.logger.warning(f"LLM returned no tool (likely safety refusal). Falling back to Intent: {intent}")
                if intent == "RETRIEVE_INFO":
                    response = {
                        "tool": "delegate_task",
                        "params": {
                            "agent_name": "RESEARCHER",
                            "instructions": user_input
                        },
                        "reply": "Executing search (Fallback)..."
                    }
                elif intent == "CREATE_ASSET":
                     # Dynamic Fallback based on Entity keywords
                     agent = "IMAGE" # Default only if truly ambiguous
                     u_in = user_input.lower()
                     
                     if "idea" in u_in or "strategy" in u_in or "concept" in u_in or "plan" in u_in:
                         agent = "BRAINSTORMER"
                     elif "agent" in u_in:
                         # Fallback to chat for agent discussions
                         return {"tool": "chat", "reply": "Let's discuss your custom agent idea. What constraints do you have?"}
                     elif "copy" in u_in or "email" in u_in or "write" in u_in: 
                         agent = "COPYWRITER"
                         
                     response = {
                        "tool": "delegate_task",
                        "params": {
                            "agent_name": agent,
                            "instructions": user_input
                        },
                        "reply": f"Generating content via {agent} (Fallback)..."
                    }

            self.logger.info(f"Plan generated: {response.get('tool')} -> {str(response.get('params'))[:50]}...")
            return response
        except Exception as e:
            self.logger.error(f"Error generating plan: {e}")
            return {"tool": "chat", "reply": "I encountered an error while thinking.", "error": str(e)}

    async def run_mission(self, goal, context=None, plan_override=None, status_callback=None):
        """
        Executes a mission, typically a search strategy.
        """
        if status_callback:
            status_callback(f"🤖 ManagerAgent received mission: {goal}")

        from .researcher import ResearcherAgent
        from database import add_lead

        # Default plan if not provided
        if not plan_override:
            plan_override = {"search_queries": []}

        queries = plan_override.get("search_queries", [])
        collected_leads = []

        researcher = ResearcherAgent(self.provider)

        for q in queries:
            if status_callback:
                status_callback(f"🔎 Delegating search for '{q}' to ResearcherAgent...")
            
            # Use Researcher to process the search
            # We treat the query as a "footprint" or direct search
            results = await researcher.mass_harvest(q, num_results=plan_override.get('limit', 10), status_callback=status_callback)
            
            if status_callback:
                status_callback(f"📥 Received {len(results)} raw results. Saving to DB...")

            for res in results:
                # Add to DB
                # res is dict with url, platform, title, etc.
                lid = add_lead(
                    url=res.get('url'),
                    email=None, # Researcher doesn't find emails in mass_harvest usually, separate step
                    source="autonomous_mission",
                    category="prospect",
                    company_name=res.get('title'),
                    relevance_reason=f"Matched query: {q}"
                )
                if lid:
                    res['id'] = lid
                    collected_leads.append(res)
        
        return {"status": "complete", "leads": collected_leads}

    async def run_flow_mission(self, workflow_name, inputs=None, status_callback=None):
        """
        Executes a graph-based workflow from a JSON file.
        """
        if status_callback:
            status_callback(f"🤖 ManagerAgent processing flow: {workflow_name}")

        workflow_path = os.path.join(os.getcwd(), 'src', 'workflows', f"{workflow_name}.json")
        if not os.path.exists(workflow_path):
             return {"error": f"Workflow {workflow_name} not found."}
        
        try:
            with open(workflow_path, 'r') as f:
                graph_data = json.load(f)
            
            results = await flow_engine.run_flow(graph_data, initial_inputs=inputs or {}, status_callback=status_callback)
            self.save_work(results, artifact_type="workflow_execution_log", metadata={"workflow": workflow_name})
            return {"status": "complete", "results": results}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # === NEW CAPABILITIES ===

    def list_available_nodes(self):
        """
        Returns a list of all registered nodes in the engine's registry.
        """
        import src.nodes # Trigger auto-registration
        from src.nodes.registry import NODE_REGISTRY
        nodes = []
        for node_type, node_inst in NODE_REGISTRY.items():
            nodes.append({
                "type": node_type,
                "name": node_inst.display_name
            })
        return nodes

    async def execute_workflow(self, workflow_name, payload=None, status_callback=None, wait=False):
        """
        Trigger the new Engine to run a workflow.
        """
        from src.engine.core import WorkflowEngine
        from src.engine.loader import WorkflowLoader
        import src.nodes # Register nodes

        if status_callback:
            status_callback(f"🚀 Triggering Workflow Engine: {workflow_name} (Wait: {wait})")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # b2b_outreach_tool/src
        workflow_path = os.path.join(base_dir, "workflows", f"{workflow_name}.json")
        
        if not os.path.exists(workflow_path):
             return {"error": f"Workflow file {workflow_name}.json not found."}

        try:
            engine = WorkflowEngine()
            workflow_def = WorkflowLoader.load_from_file(workflow_path)
            execution_id = await engine.run_workflow(workflow_def, payload or {}, status_callback=status_callback, wait=wait)
            
            if status_callback and not wait:
                status_callback(f"✅ Workflow spawned. Execution ID: {execution_id}")

            return {"status": "running" if not wait else "complete", "execution_id": execution_id}
        except Exception as e:
            self.logger.error(f"Execution failed: {e}")
            if status_callback:
                status_callback(f"❌ Execution failed: {e}")
            return {"status": "error", "error": str(e)}

    def design_workflow(self, goal, nodes_description=None):
        """
        Uses the LLM to generate a valid workflow JSON file.
        """
        import uuid
        available_nodes = self.list_available_nodes()
        
        system_prompt = (
            "You are a Workflow Architect. Your goal is to design a JSON workflow definition based on the user's goal.\n"
            "You must output ONLY valid JSON.\n\n"
            "Schema Structure:\n"
            "{\n"
            "  \"id\": \"workflow_unique_name\",\n"
            "  \"name\": \"Readable Name\",\n"
            "  \"nodes\": [ \n"
            "      { \"id\": \"node_1\", \"type\": \"trigger.manual\" }, \n"
            "      { \"id\": \"node_2\", \"type\": \"action.search\", \"params\": { \"query\": \"...\" } } \n"
            "  ],\n"
            "  \"edges\": [ \n"
            "      { \"source\": \"node_1\", \"target\": \"node_2\" } \n"
            "  ]\n"
            "}\n\n"
            f"Available Node Types: {json.dumps(available_nodes, indent=2)}\n"
            "Note: Always start with a 'trigger.manual' node if no specific trigger is asked for."
        )
        
        user_prompt = f"Goal: {goal}\nExtra Context: {nodes_description or ''}"
        
        try:
            res = self.provider.generate_json(f"{system_prompt}\n\n{user_prompt}")
            if not res:
                return {"error": "LLM returned empty design."}
            
            # Save the design
            wf_name = res.get("id", f"workflow_{uuid.uuid4().hex[:8]}")
            # Sanitize
            wf_name = "".join([c for c in wf_name if c.isalnum() or c in ['_', '-']])
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            save_path = os.path.join(base_dir, "workflows", f"{wf_name}.json")
            
            with open(save_path, "w") as f:
                json.dump(res, f, indent=2)
                
            return {"status": "success", "file": save_path, "design": res}
            
        except Exception as e:
            self.logger.error(f"Design failed: {e}")
            return {"error": str(e)}
