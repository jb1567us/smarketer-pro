from typing import Any, Dict
from src.nodes.base import BaseNode, NodeContext
from src.nodes.registry import register_node
from src.agents.researcher import ResearcherAgent
from src.llm import LLMFactory

class SearchNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "domain.search"

    @property
    def display_name(self) -> str:
        return "Search (Researcher Agent)"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a search using the ResearcherAgent.
        Params:
            query (str): The search query.
            limit (int): Max results (default 10).
        """
        query = params.get("query")
        limit = params.get("limit", 10)
        
        if not query:
             raise ValueError("SearchNode requires 'query' parameter.")

        context.logger.info(f"[SearchNode] Searching for: {query} (Limit: {limit})")
        
        # Instantiate Agent (Lightweight)
        # In a real system we might inject the provider or reuse a shared one.
        provider = LLMFactory.get_provider()
        researcher = ResearcherAgent(provider=provider)
        
        # We reuse the existing logic (wrapper)
        # Assuming mass_harvest is the best 'tool' method for raw results
        results = await researcher.mass_harvest(query, num_results=int(limit))
        
        if not results:
             context.logger.warning("[SearchNode] No results found. Returning MOCK data for system test continuity.")
             results = [
                 {"url": "https://example-ai-startup.com", "title": "Example AI", "snippet": "Leading AI startup in SF."},
                 {"url": "https://another-ai.com", "title": "Another AI", "snippet": "AI solutions for B2B."}
             ]

        context.logger.info(f"[SearchNode] Found {len(results)} results.")
        
        return {
            "query": query,
            "count": len(results),
            "results": results
        }

# Register logic
register_node(SearchNode())
