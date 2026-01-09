import traceback
import asyncio
from typing import Dict, Any, List, Optional
from agents.base import BaseAgent
from utils.agent_registry import get_agent_class

class FlowNode:
    def __init__(self, id, type, data, position=None):
        self.id = id
        self.type = type # e.g., 'agent_task', 'decision', 'input', 'output'
        self.data = data
        self.position = position

class FlowEngine:
    """
    Executes a graph-based workflow of connected nodes.
    Adapted from LOLLMS FlowEngine.
    """
    def __init__(self):
        self.results = {}
        self.status_callback = None

    async def execute_node(self, node: FlowNode, inputs: Dict[str, Any]):
        """Executes a single node based on its type."""
        print(f"[FlowEngine] Executing node {node.id} ({node.type})...")
        
        if node.type == 'agent_task':
            agent_role = node.data.get('agent_role')
            instruction = node.data.get('instruction')
            
            # Resolve inputs in instruction
            # Simple template: {{input_name}}
            for k, v in inputs.items():
                if isinstance(v, str):
                    instruction = instruction.replace(f"{{{{{k}}}}}", v)
            
            # Instantiate agent
            AgentClass = get_agent_class(agent_role) if agent_role else BaseAgent
            if not AgentClass and agent_role:
                 print(f"Warning: Agent role '{agent_role}' not found. Using BaseAgent.")
                 AgentClass = BaseAgent

            # We need a proper goal/role for the agent instance if generic
            agent = AgentClass(role=agent_role or "Worker", goal="Execute flow task")
            
            # Execute
            # Assuming agents have a 'think' or 'prompt' method we can use.
            # For BaseAgent, we use prompt.
            context = f"Inputs: {inputs}"
            result = await agent.generate_text_async(f"{context}\n\nTask: {instruction}")
            return {"output": result}

        elif node.type == 'decision':
            # Evaluates a condition using LLM or python logic
            condition = node.data.get('condition')
            context = f"Inputs: {inputs}"
            
            # Using a temporary agent to evaluate logic if complex
            # For this MVP, let's assume simple LLM check
            from llm.factory import LLMFactory
            provider = LLMFactory.get_provider()
            
            check_prompt = f"Context: {context}\n\nCondition: {condition}\n\nIs the condition met? Reply strictly 'YES' or 'NO'."
            res = await provider.generate_text_async(check_prompt)
            result = "true" if "YES" in res.upper() else "false"
            return {"output": result, "branch": result}

        elif node.type == 'input':
            return inputs # Pass through

        elif node.type == 'output':
            return inputs # Pass through final result

        else:
            print(f"Unknown node type: {node.type}")
            return {}

    async def run_flow(self, graph_data: Dict[str, Any], initial_inputs: Dict[str, Any] = None, status_callback=None):
        """
        Runs the flow defined by graph_data.
        graph_data structure: {'nodes': [...], 'edges': [...]}
        """
        self.status_callback = status_callback
        self.results = {}
        initial_inputs = initial_inputs or {}
        
        nodes_map = {n['id']: FlowNode(n['id'], n['type'], n['data']) for n in graph_data.get('nodes', [])}
        edges = graph_data.get('edges', [])
        
        # Topological execution or step-by-step
        # For simplicity in this async version, we'll wait for dependencies.
        
        executed_nodes = set()
        
        # Inject initial inputs into 'input' nodes results if any
        for nid, node in nodes_map.items():
            if node.type == 'input':
                self.results[nid] = initial_inputs
                executed_nodes.add(nid)

        loop_count = 0
        max_loops = len(nodes_map) * 2 # Safety break
        
        while len(executed_nodes) < len(nodes_map):
            loop_count += 1
            if loop_count > max_loops:
                raise RuntimeError("Flow execution stalled (possible cycle or missing dependency).")
            
            progress = False
            for nid, node in nodes_map.items():
                if nid in executed_nodes:
                    continue
                
                # Check dependencies
                incoming_edges = [e for e in edges if e['target'] == nid]
                dependencies_met = True
                node_inputs = {}
                
                for edge in incoming_edges:
                    source_id = edge['source']
                    if source_id not in self.results:
                        dependencies_met = False
                        break
                    
                    # Map output of source to input of target
                    # Edge structure might have handles, for now we just dump all source results
                    source_output = self.results[source_id]
                    # If specific handle mapping exists:
                    source_handle = edge.get('sourceHandle', 'output')
                    target_handle = edge.get('targetHandle', 'input')
                    
                    val = source_output if not isinstance(source_output, dict) else source_output.get(source_handle, source_output)
                    node_inputs[target_handle] = val

                if dependencies_met:
                    # Execute
                    try:
                        res = await self.execute_node(node, node_inputs)
                        self.results[nid] = res
                        executed_nodes.add(nid)
                        progress = True
                    except Exception as e:
                        print(f"Error executing node {nid}: {e}")
                        traceback.print_exc()
                        raise e
            
            if not progress:
                 # Check if we are done (remaining nodes might be unreachable)
                 # simple check: if no progress and we have unexecuted nodes that have dependencies that will NEVER be met
                 break

        print("[FlowEngine] Flow execution complete.")
        return self.results

flow_engine = FlowEngine()
