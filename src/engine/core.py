import asyncio
import logging
import uuid
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict

from src.nodes.base import BaseNode, NodeContext
from src.nodes.registry import NODE_REGISTRY

class WorkflowEngine:
    """
    The Core DAG Runner.
    Executes a workflow definition step-by-step.
    """
    
    def __init__(self, db_path="workflow_state.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("AutomationEngine")
        self._init_db()

    def _init_db(self):
        """Initialize the State Store (SQLite)."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workflow_executions (
                execution_id TEXT PRIMARY KEY,
                workflow_id TEXT,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                current_step TEXT,
                state_json TEXT,
                error_message TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS step_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                execution_id TEXT,
                step_id TEXT,
                node_type TEXT,
                status TEXT,
                input_json TEXT,
                output_json TEXT,
                timestamp TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    async def run_workflow(self, workflow_def: Dict[str, Any], initial_payload: Dict[str, Any] = None, status_callback=None, wait=False) -> str:
        """
        Starts a workflow execution.
        """
        execution_id = str(uuid.uuid4())
        workflow_id = workflow_def.get("id", "unknown")
        
        # Persist Initial State
        self._save_execution_state(execution_id, workflow_id, "RUNNING", initial_payload)
        
        if status_callback:
            status_callback(f"⚙️ Workflow Engine initializing: {workflow_id}")

        # Async Worker
        task = asyncio.create_task(self._execute_dag(execution_id, workflow_def, initial_payload, status_callback))
        
        if wait:
            await task
            
        return execution_id

    def get_status(self, execution_id: str) -> Dict[str, Any]:
        """
        Retrieves the current status of an execution.
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        
        # Get Main Status
        cursor.execute('SELECT status, error_message FROM workflow_executions WHERE execution_id = ?', (execution_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"status": "UNKNOWN"}
            
        status, error = row
        
        # Get Steps
        cursor.execute('SELECT step_id, status FROM step_logs WHERE execution_id = ? ORDER BY timestamp ASC', (execution_id,))
        steps = [{"step_id": r[0], "status": r[1]} for r in cursor.fetchall()]
        
        conn.close()
        
        return {
            "execution_id": execution_id,
            "status": status,
            "error": error,
            "steps": steps
        }

    async def _execute_dag(self, execution_id: str, workflow_def: Dict[str, Any], payload: Dict[str, Any], status_callback=None):
        """
        The main loop.
        """
        context = NodeContext(
            execution_id=execution_id,
            workflow_id=workflow_def.get("id"),
            global_state=payload or {},
            steps_output={},
            logger=self.logger
        )

        nodes_map = {n["id"]: n for n in workflow_def.get("nodes", [])}
        edges = workflow_def.get("edges", [])
        
        # Determine Start Node (Node with no incoming edges or marked start)
        # For simplicity v1: We assume linear or explicitly linked flows.
        # We start with the node that has type "trigger" or the first node.
        
        start_node_id = None
        for n in workflow_def["nodes"]:
            if n.get("type", "").startswith("trigger"):
                start_node_id = n["id"]
                break
        
        if not start_node_id and workflow_def["nodes"]:
            start_node_id = workflow_def["nodes"][0]["id"]

        if not start_node_id:
            self.logger.error(f"Workflow {context.workflow_id} has no nodes.")
            self._update_status(execution_id, "FAILED", error="No nodes found")
            return

        current_node_id = start_node_id
        
        try:
            while current_node_id:
                self.logger.info(f"DEBUG: current_node_id={current_node_id} type={type(current_node_id)}")
                node_def = nodes_map.get(current_node_id)
                if not node_def:
                    break # Should not happen if edges are valid

                # Check dependencies & Collect Inputs
                incoming_edges = [e for e in edges if e['target'] == current_node_id]
                dependencies_met = True
                node_inputs = {}
                
                for edge in incoming_edges:
                    source_id = edge['source']
                    if source_id not in context.steps_output: # Check execution history
                         # If we are strictly DAG, we might wait? For now, we assume simple linear sequence in loop
                         # But since we traverse by next_node, dependencies *should* be met unless it's a join
                        dependencies_met = False
                        break
                    
                    source_output = context.steps_output[source_id]
                    # Map Handles (simplistic v1)
                    source_handle = edge.get('sourceHandle', 'output')
                    target_handle = edge.get('targetHandle', 'input')
                    
                    val = source_output if not isinstance(source_output, dict) else source_output.get(source_handle, source_output)
                    node_inputs[target_handle] = val

                if not dependencies_met:
                     # For v1 linear runner, this implies we hit a node that we jumped to but skipped its precursor?
                     # Or maybe a loop?
                     # We'll log warning and proceed (with empty inputs) or break?
                     self.logger.warning(f"Dependencies not fully met for {current_node_id}")

                # Execute Node
                node_type = node_def.get("type")
                params = node_def.get("params", {})
                
                self.logger.info(f"Executing Step {current_node_id} ({node_type})")
                
                # Load Node Class
                node_handler = NODE_REGISTRY.get(node_type)
                if not node_handler:
                    raise Exception(f"Unknown Node Type: {node_type}")

                # Merge dynamic inputs into params (Data Flow)
                # This allows previous nodes to override static params
                # e.g. input "url" from SearchNode overrides static "url" param
                execution_params = params.copy()
                execution_params.update(node_inputs)

                # Run Logic
                if status_callback:
                    status_callback(f"📝 Executing Node: {node_type} ({current_node_id})")
                
                result = await node_handler.execute(context, execution_params)
                
                # Store Output
                context.steps_output[current_node_id] = result
                self._log_step(execution_id, current_node_id, node_type, params, result)
                
                if status_callback:
                    status_callback(f"✅ Node {current_node_id} complete.")

                # Determine Next Node
                # 1. precise edge match (source -> target)
                # 2. logic flow (some nodes might return "branch" output)
                
                next_node_id = None
                
                # Simple Linear/Branch Logic
                # We look at edges where source == current_node_id
                possible_edges = [e for e in edges if e["source"] == current_node_id]
                
                if not possible_edges:
                    break # End of Line
                
                if len(possible_edges) == 1:
                    next_node_id = possible_edges[0]["target"]
                else:
                    # Logic Node Branching (e.g. if node returns "true" or "false")
                    # We expect the result to have a 'branch' key or similar, 
                    # OR the edge has a 'label' matching the result?
                    # Let's assume result['branch'] matches edge['label']
                    branch = result.get("branch") if isinstance(result, dict) else None
                    if branch:
                        for e in possible_edges:
                            if e.get("label") == branch:
                                next_node_id = e["target"]
                                break
                    else:
                        # Default to first if no specific logic (or run all? DAG engine complex part)
                        # v1: Take first
                        next_node_id = possible_edges[0]["target"]

                current_node_id = next_node_id

            self._update_status(execution_id, "COMPLETED")
            if status_callback:
                status_callback("🏁 Workflow Execution Fully Complete.")

        except Exception as e:
            self.logger.error(f"Workflow Failed: {e}", exc_info=True)
            self._update_status(execution_id, "FAILED", error=str(e))
            if status_callback:
                status_callback(f"💥 Workflow Failed: {e}")

    def _save_execution_state(self, execution_id, workflow_id, status, state):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO workflow_executions 
            (execution_id, workflow_id, status, start_time, state_json)
            VALUES (?, ?, ?, ?, ?)
        ''', (execution_id, workflow_id, status, datetime.now(), json.dumps(state, default=str)))
        conn.commit()
        conn.close()

    def _update_status(self, execution_id, status, error=None):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE workflow_executions 
            SET status = ?, end_time = ?, error_message = ?
            WHERE execution_id = ?
        ''', (status, datetime.now(), error, execution_id))
        conn.commit()
        conn.close()

    def _log_step(self, execution_id, step_id, node_type, input_data, output_data):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO step_logs 
            (execution_id, step_id, node_type, status, input_json, output_json, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            execution_id, step_id, node_type, "SUCCESS",
            json.dumps(input_data, default=str),
            json.dumps(output_data, default=str),
            datetime.now()
        ))
        conn.commit()
        conn.close()
