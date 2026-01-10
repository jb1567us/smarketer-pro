import sys
import os
import asyncio
sys.path.append(os.path.join(os.getcwd(), 'src'))

from flow.flow_engine import flow_engine # mocked or real
from llm.factory import LLMFactory

async def test_flow_execution():
    print("Testing Flow Engine...")
    
    # Define a simple graph
    # Start -> Agent Task (Joke) -> Decision (Is it funny?) -> Output
    
    graph_data = {
        "nodes": [
            {
                "id": "1",
                "type": "input",
                "data": {}
            },
            {
                "id": "2",
                "type": "agent_task",
                "data": {
                    "agent_role": "CopywriterAgent",
                    "instruction": "Tell a short joke about {{topic}}."
                }
            },
            {
                "id": "3",
                "type": "decision",
                "data": {
                    "condition": "Is the joke funny?"
                }
            },
            {
                "id": "4",
                "type": "output",
                "data": {}
            }
        ],
        "edges": [
            {"source": "1", "target": "2", "sourceHandle": "topic"}, # Input topic to task
            {"source": "2", "target": "3"}, # Task output to decision
            {"source": "3", "target": "4"} # Decision output to end
        ]
    }
    
    inputs = {"topic": "AI programming"}
    
    try:
        results = await flow_engine.run_flow(graph_data, initial_inputs=inputs)
        print("Flow Execution Results:")
        for nid, RES in results.items():
            print(f"Node {nid}: {RES}")
            
    except Exception as e:
        print(f"Flow failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_flow_execution())
