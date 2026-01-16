from typing import Any, Dict
from nodes.base import BaseNode, NodeContext
from src.nodes.registry import register_node
import traceback

class CodeNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "core.code"

    @property
    def display_name(self) -> str:
        return "Code Execution (Python)"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes arbitrary Python code.
        Params:
            code (str): The Python code to run.
            input_data (any): Optional data to pass as 'input' to the script.
        
        The code has access to:
        - input: params.get('input_data')
        - context: The NodeContext
        - print: Redirected to log
        
        The code MUST set a variable named 'output' to return data.
        """
        code = params.get("code")
        input_data = params.get("input_data")
        
        if not code:
             raise ValueError("CodeNode requires 'code' parameter.")
        
        # Prepare execution environment
        local_scope = {
            "input": input_data,
            "context": context,
            "output": None,  # Helper for return value
            "log": context.logger.info
        }
        
        context.logger.info("[CodeNode] Executing custom script...")
        
        try:
            # We use exec. In a production environment this needs strict sandboxing.
            # For a local tool, this is acceptable but powerful.
            exec(code, {}, local_scope)
            
            result = local_scope.get('output')
            context.logger.info("[CodeNode] Execution Success.")
            return {"result": result}
            
        except Exception as e:
            error_msg = f"Code Execution Failed: {str(e)}\n{traceback.format_exc()}"
            context.logger.error(error_msg)
            return {"error": str(e), "traceback": traceback.format_exc()}

# Register logic
register_node(CodeNode())
