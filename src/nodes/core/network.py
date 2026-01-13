import aiohttp
from typing import Any, Dict
from src.nodes.base import BaseNode, NodeContext
from src.nodes.registry import register_node

class HTTPRequestNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "core.http_request"
    
    @property
    def display_name(self) -> str:
        return "HTTP Request"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        url = params.get("url")
        method = params.get("method", "GET")
        headers = params.get("headers", {})
        body = params.get("body", {})
        
        if not url:
            raise ValueError("URL is required for HTTP Request")

        context.logger.info(f"[HTTP] {method} {url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=body) as response:
                try:
                    data = await response.json()
                except:
                    data = await response.text()
                
                return {
                    "status": response.status,
                    "data": data,
                    "headers": dict(response.headers)
                }

register_node(HTTPRequestNode())
