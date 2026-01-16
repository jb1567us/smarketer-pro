from .base import BaseAgent
import json
from utils.agent_registry import list_available_agents
from memory import Memory
try:
    from flow.flow_engine import flow_engine
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
        - CREATE_ASSET: Generating new content.
        - RETRIEVE_INFO: Searching the web, DB, or memory.
        - EXECUTE_ACTION: Running a workflow, mission, or complex task.
        - CHAT: General conversation.
        """
        classification_prompt = (
            "You are an Intent Classifier. Analyze the user request.\n"
            "Strictly categorize into one of these 4 intents:\n"
            "1. CREATE_ASSET (e.g. 'write email', 'generate image', 'draft post')\n"
            "   - Entity: What is being created? (Image, Email, Video, Idea)\n"
            "2. RETRIEVE_INFO (e.g. 'find leads', 'search for X', 'get info')\n"
            "   - Entity: What is being searched? (Information, Dataset, People)\n"
            "3. EXECUTE_ACTION (e.g. 'run workflow', 'build site', 'start campaign', 'recruit affiliates')\n"
            "   - Entity: What action? (Workflow, Site Build, Optimization)\n"
            "4. CHAT (e.g. 'how are you', 'explain X', 'what should we do')\n\n"
            f"Request: '{user_input}'\n\n"
            "Return Valid JSON ONLY: {'intent': 'ENUM_VALUE', 'entity': 'string', 'reasoning': 'brief explanation'}"
        )
        
        try:
            res = self.provider.generate_json(classification_prompt)
            if isinstance(res, list): res = res[0]
            if not isinstance(res, dict): raise ValueError("Non-dict response")
            return res
        except Exception as e:
            self.logger.warning(f"[Manager] Intent classification failed: {e}")
            return {"intent": "CHAT", "entity": "None", "reasoning": "Fallback due to error"}

    def think(self, user_input, intent_history=None, available_tools=None):
        """
        Decides on the next action based on user input, with strict validation and logging.
        """
        from utils.agent_registry import AGENT_METADATA
        from workflow_manager import list_workflows
        from database import log_agent_decision
        
        # 1. Classify Intent
        classification = self._classify_intent(user_input)
        intent = classification.get("intent", "CHAT")
        entity = classification.get("entity", "")
        reasoning = classification.get("reasoning", "")
        
        self.logger.info(f"Classified Intent: {intent} ({entity})")

        # --- GUARDRAILS ---
        # 1. WordPress Site Build
        u_in = user_input.lower()
        if ("build" in u_in or "install" in u_in) and ("site" in u_in or "wordpress" in u_in or "wp" in u_in):
            domain, directory = "lookoverhere.xyz", ""
            import re
            match = re.search(r'([a-z0-9.-]+\.[a-z]{2,})(/[a-z0-9_-]+)?', u_in)
            if match:
                domain = match.group(1)
                directory = match.group(2).lstrip('/') if match.group(2) else ""
            
            tool = "build_wordpress_site"
            params = {"goal": user_input, "domain": domain, "directory": directory}
            log_agent_decision("Manager", intent, user_input, tool, params, "Guardrail: Site Build")
            return {"tool": tool, "params": params, "reply": f"Initiating WordPress build for {domain}..."}

        # 2. Affiliate Requests
        if "affiliate" in u_in:
            if "recruit" in u_in:
                tool, params = "execute_workflow", {"workflow_name": "recruit_partners", "payload": {"goal": user_input}}
                log_agent_decision("Manager", intent, user_input, tool, params, "Guardrail: Affiliate Recruitment")
                return {"tool": tool, "params": params, "reply": "Starting Affiliate Recruitment Workflow."}
            elif "setup" in u_in or "add" in u_in or "offer" in u_in:
                tool, params = "execute_workflow", {"workflow_name": "setup_offer", "payload": {"goal": user_input}}
                log_agent_decision("Manager", intent, user_input, tool, params, "Guardrail: Affiliate Offer Setup")
                return {"tool": tool, "params": params, "reply": "Starting Affiliate Offer Setup Workflow."}
        
        # 2. Prepare Context for LLM
        expertise_lines = [f"- {k.upper()}: {v['role']}" for k, v in AGENT_METADATA.items() if k != "manager"]
        agent_list = "\n".join(expertise_lines)
        workflows = ", ".join(list_workflows()) if list_workflows() else "None"
        memory = self.memory.get_context()

        # Dynamic Instructions based on Intent
        guidance = ""
        if intent == "CREATE_ASSET":
            guidance = "User wants to CREATE. Delegate to [IMAGE/VIDEO/COPYWRITER]."
        elif intent == "RETRIEVE_INFO":
            guidance = "User wants INFO. Delegate to [RESEARCHER] or use [run_search]."
        elif intent == "EXECUTE_ACTION":
            guidance = "User wants ACTION. Use [execute_workflow] or [delegate_task]."

        system_prompt = (
            "You are the Manager Agent (CONDUCTOR). Your job is to ORCHESTRATE, not just chat.\n"
            f"Current Intent: {intent} ({entity})\n"
            f"Guidance: {guidance}\n\n"
            "AVAILABLE TOOLS:\n"
            "1. delegate_task(agent_name, instructions): Handoff to specialist (Image, Video, Copywriter, Researcher).\n"
            "2. execute_workflow(workflow_name, payload): Run a defined process (e.g. recruit_partners, seo_campaign).\n"
            "3. run_search(query): Quick web search.\n"
            "4. design_workflow(goal): Create a new workflow file.\n"
            "5. build_wordpress_site(goal, domain, directory): For site creation tasks.\n"
            "6. chat(message): Only for clarifications or general discussion.\n\n"
            f"Specialists: {agent_list}\n"
            f"Workflows: {workflows}\n"
            f"Memory: {memory}\n\n"
            "CRITICAL: Return strictly valid JSON. No markdown.\n"
            "Schema: {\"tool\": \"tool_name\", \"params\": {\"arg\": \"val\"}, \"reply\": \"user_msg\"}"
        )

        try:
            response = self.provider.generate_json(f"{system_prompt}\n\nUser Input: {user_input}")
            if isinstance(response, list): response = response[0]
            
            # Validation
            tool_name = response.get("tool")
            tool_params = response.get("params", {})
            
            # Persist Decision
            log_agent_decision("Manager", intent, user_input, tool_name, tool_params, reasoning)
            
            return response
        except Exception as e:
            self.logger.error(f"Manager think error: {e}")
            return {"tool": "chat", "reply": "I encountered a brain freeze.", "error": str(e)}

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
        import nodes # Trigger auto-registration
        from nodes.registry import NODE_REGISTRY
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
        from engine.core import WorkflowEngine
        from engine.loader import WorkflowLoader
        import nodes # Register nodes

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
