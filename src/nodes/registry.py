from typing import Dict
from nodes.base import BaseNode

NODE_REGISTRY: Dict[str, BaseNode] = {}

def register_node(node: BaseNode):
    NODE_REGISTRY[node.node_type] = node
