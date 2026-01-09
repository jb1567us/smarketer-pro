from .base import BaseAgent
import json
from utils.agent_registry import list_available_agents
from memory import Memory
from flow.flow_engine import flow_engine
import os

class ManagerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Manager & Orchestrator",
            goal="Oversee the outreach process, execute tasks via tools, and manage workflows.",
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
            "3. EXECUTE_ACTION: User wants to run a process (e.g., 'run workflow', 'start mission').\n"
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
            print(f"[Manager] Intent classification failed: {e}")
            return {"intent": "CHAT", "entity": "None", "instructions": user_input}

    def think(self, user_input, intent_history=None, available_tools=None):
        """
        Decides on the next action based on user input.
        """
        from utils.agent_registry import AGENT_METADATA
        from workflow_manager import list_workflows
        
        # 1. Classify Intent
        print(f"\n[Manager] 🤔 Analyzing user input: '{user_input}'...")
        classification = self._classify_intent(user_input)
        intent = classification.get("intent", "CHAT")
        entity = classification.get("entity", "")
        print(f"[Manager] 🧠 Classified Intent: {intent} (Entity: {entity})")
        
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
            "5. STYLE: Adopt the user's communication style. Be a thought partner.\n\n"
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
        
        print(f"[Manager] 💭 Generating execution plan (LLM Call)...")
        try:
            response = self.provider.generate_json(full_prompt)
            if isinstance(response, list):
                response = response[0]
            
            # --- FALLBACK: Intent-Based Override ---
            # If LLM refuses (returns None/Empty) but we know the intent is Retrieval/Creation, force it.
            tool_name = response.get('tool') if response else None
            
            if not tool_name:
                print(f"[Manager] ⚠️ LLM returned no tool (likely safety refusal). Falling back to Intent: {intent}")
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

            print(f"[Manager] 💡 Plan generated: {response.get('tool')} -> {str(response.get('params'))[:50]}...")
            return response
        except Exception as e:
            print(f"[Manager] ❌ Error generating plan: {e}")
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
