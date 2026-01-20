import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
from src.engine.strategy_factory import StrategyFactory
import sqlite3
import json
import os

# Initialize MCP Server
server = Server("smarketer-pro-hub")

# --- Hub State Management ---
@server.list_resources()
async def list_resources() -> list[types.Resource]:
    """Exposes the mission state and workflow logs."""
    return [
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
    
    elif name == "report_mission_progress":
        exec_id = arguments["execution_id"]
        status = arguments["status"]
        return [
            types.TextContent(
                type="text",
                text=f"Hub acknowledged: Execution {exec_id} is now {status}."
            )
        ]

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
