from typing import Any, Dict
from src.nodes.base import BaseNode, NodeContext
from src.nodes.registry import register_node
from src.agents.researcher import ResearcherAgent
from src.llm import LLMFactory

class EnrichNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "domain.enrich"

    @property
    def display_name(self) -> str:
        return "Enrich (Scrape & Analyze)"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriches a URL by scraping and extracting signals.
        Params:
            url (str): The URL to enrich.
        """
        url = params.get("url")
        
        # Handle dynamic input (which might be a list from SearchNode)
        # If 'url' is not directly string, check if it's a dict or list
        if not isinstance(url, str) and url:
            if isinstance(url, list) and len(url) > 0:
                # Take first result for now (simple pipeline)
                item = url[0]
                url = item.get("url") if isinstance(item, dict) else str(item)
            elif isinstance(url, dict):
                 url = url.get("url")

        if not url:
             # Fallback: check if 'input' matches (N8N style default handle)
             input_val = params.get("input")
             
             # Unpack dict wrapper if present (e.g. {'results': [...]})
             if isinstance(input_val, dict) and "results" in input_val:
                 input_val = input_val["results"]
                 
             if isinstance(input_val, list) and len(input_val) > 0:
                  item = input_val[0]
                  url = item.get("url") if isinstance(item, dict) else str(item)
        
        if not url:
             raise ValueError(f"EnrichNode requires 'url' parameter. Got input: {str(params.get('input'))[:100]}")

        context.logger.info(f"[EnrichNode] Enriching: {url}")
        
        # Instantiate Agent
        provider = LLMFactory.get_provider()
        researcher = ResearcherAgent(provider=provider)
        
        # Use the deep enrichment logic
        data = await researcher.enrich_lead_data(url)
        
        context.logger.info(f"[EnrichNode] Enriched data for {url}")
        
        return {
            "url": url,
            "enrichment": data
        }

# Register logic
register_node(EnrichNode())
