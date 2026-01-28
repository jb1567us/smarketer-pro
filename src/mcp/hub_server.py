import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
from src.engine.strategy_factory import StrategyFactory
import sqlite3
import json
import os
import sys

# Ensure src modules are available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from directives.refactor_tools.golden_master import GoldenMaster
from directives.refactor_tools.legacy_keeper import LegacyKeeper

# Define Directives Path (Root/directives)
# __file__ = src/mcp/hub_server.py -> up 3 levels to Root
DIRECTIVES_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'directives'))

# Initialize MCP Server
server = Server("smarketer-pro-hub")

# --- Hub State Management ---
@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """Exposes the mission state and workflow logs."""
    base_resources = [
        types.Resource(
            uri="mission://state",
            name="Current Mission State",
            description="Active lead generation mission status",
            mimeType="application/json",
        ),
        types.Resource(
            uri="brand://kernel",
            name="Brand Identity Kernel",
            description="Core brand voice, niche, and product benefits",
            mimeType="application/json",
        )
    ]
    
    # Dynamically map Directives
    if os.path.exists(DIRECTIVES_PATH):
        for root, _, files in os.walk(DIRECTIVES_PATH):
            for file in files:
                 if file.endswith(('.md', '.txt', '.py', '.yaml', '.json')):
                    # Create relative path for URI (e.g. "smart_router/config.yaml")
                    rel_path = os.path.relpath(os.path.join(root, file), DIRECTIVES_PATH).replace("\\", "/")
                    base_resources.append(
                        types.Resource(
                            uri=f"directive://{rel_path}",
                            name=f"Directive: {rel_path}",
                            description=f"Standard Operating Procedure: {rel_path}",
                            mimeType="text/markdown" if file.endswith('.md') else "text/plain"
                        )
                    )
    return base_resources

async def fetch_resource_logic(uri: str) -> str:
    """Core logic for reading resources, separated for testability."""
    if uri == "mission://state":
        db_path = "workflow_state.db"
        if not os.path.exists(db_path):
            return json.dumps({"status": "NO_ACTIVE_MISSION"})
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workflow_executions ORDER BY start_time DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [col[0] for col in cursor.description]
            return json.dumps(dict(zip(columns, row)), default=str)
        return json.dumps({"status": "NO_DATA"})
    
    elif uri == "brand://kernel":
        kernel = {
            "niche": "B2B SaaS / Growth Marketing",
            "icp_role": "Marketing Director",
            "brand_voice": "Bold, results-oriented, professional",
            "product_name": "Smarketer-Pro",
            "product_benefits": [
                "Automated lead enrichment",
                "Polymorphic outreach strategies",
                "Self-correcting campaign loops"
            ]
        }
        return json.dumps(kernel)
    
    elif uri.startswith("directive://"):
        sub_path = uri.replace("directive://", "")
        # Safe path joining
        target_path = os.path.normpath(os.path.join(DIRECTIVES_PATH, sub_path))
        
        # Security: Ensure we haven't escaped the directives folder
        if not target_path.startswith(DIRECTIVES_PATH):
             return "ERROR: Access denied (Path Traversal)."
        
        if not os.path.exists(target_path):
             return "ERROR: Directive not found."
             
        try:
            with open(target_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"ERROR: Could not read directive. {str(e)}"

    raise ValueError(f"Unknown resource: {uri}")

@server.read_resource()
async def read_resource(uri: str) -> str:
    return await fetch_resource_logic(uri)

# --- Polymorphic Strategy Tools ---
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_outreach_strategy",
            description="Determines the polymorphic strategy (White/Gray/Black Hat) based on policy context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "risk_level": {"type": "string", "enum": ["WHITE_HAT", "GRAY_HAT", "BLACK_HAT"]},
                },
                "required": ["risk_level"],
            },
        ),
        types.Tool(
            name="get_brand_kernel",
            description="Fetches the core brand identity and niche context.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="report_mission_progress",
            description="Updates the Hub with the current status of a sub-task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "execution_id": {"type": "string"},
                    "step_id": {"type": "string"},
                    "status": {"type": "string"},
                    "details": {"type": "string"},
                },
                "required": ["execution_id", "status"],
            },
        ),
        types.Tool(
            name="archive_legacy_code",
            description="Archives code segments using LegacyKeeper.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "code_content": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["name", "code_content"],
            },
        ),
        types.Tool(
             name="golden_master_verify",
             description="Simulates a Golden Master verification (dry run as it requires object instances).",
             inputSchema={
                 "type": "object",
                 "properties": {
                     "function_name": {"type": "string"},
                     "snapshot_name": {"type": "string"},
                 },
                 "required": ["function_name", "snapshot_name"],
             },
        )
    ]

async def call_tool_logic(name: str, arguments: dict) -> list[types.TextContent]:
    """Core logic for calling tools, separated for testability."""
    if name == "get_outreach_strategy":
        risk = arguments.get("risk_level", "WHITE_HAT")
        class MockPolicy:
            def __init__(self, risk):
                self.risk_level = risk
        
        strategy = StrategyFactory.get_outreach_strategy(MockPolicy(risk))
        strategy_name = strategy.__class__.__name__
        
        return [
            types.TextContent(
                type="text",
                text=f"Switched to {strategy_name}. Strategy description: {strategy.__doc__.strip()}"
            )
        ]
    
    elif name == "get_brand_kernel":
        kernel_json = await fetch_resource_logic("brand://kernel")
        return [types.TextContent(type="text", text=kernel_json)]
    
        return [
            types.TextContent(
                type="text",
                text=f"Hub acknowledged: Execution {exec_id} is now {status}."
            )
        ]

    elif name == "archive_legacy_code":
        keeper = LegacyKeeper()
        path = keeper.archive_code(arguments["name"], arguments["code_content"], arguments.get("reason", ""))
        return [types.TextContent(type="text", text=f"Archived to {path}")]
        
    elif name == "golden_master_verify":
        # Since we can't easily pass python functions via JSON, this is a placeholder/wrapper
        # Real usage would imply running a script.
        return [types.TextContent(type="text", text="Golden Master Verification initialized (Stub). Use run_command to execute full verification scripts.")]

    raise ValueError(f"Tool not found: {name}")

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    return await call_tool_logic(name, arguments)

async def main():
    # In a real MCP setup, we'd use stdio transport for the host (Claude Code / Desktop)
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())
