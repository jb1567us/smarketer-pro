from typing import Any, Dict
from nodes.base import BaseNode, NodeContext
from nodes.registry import register_node
from agents.wordpress import WordPressAgent
import traceback

class WordPressNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "domain.wordpress"

    @property
    def display_name(self) -> str:
        return "WordPress Action"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a WordPress action (install, post, etc).
        Params:
            action (str): cpanel_install, create_post, create_page, generate_app_password.
            ... (action specific params)
        """
        action = params.get("action")
        if not action:
            raise ValueError("WordPressNode requires 'action'.")

        context.logger.info(f"[WordPressNode] Executing action: {action}")
        
        try:
            agent = WordPressAgent()
            
            if action == "cpanel_install":
                result = await agent.cpanel_install_wp(
                    cpanel_url=params.get("cpanel_url"),
                    cp_user=params.get("cp_user"),
                    cp_pass=params.get("cp_pass"),
                    domain=params.get("domain"),
                    directory=params.get("directory", "")
                )
            elif action == "create_post":
                result = await agent.manage_content(
                    site_url=params.get("site_url"),
                    username=params.get("username"),
                    app_password=params.get("app_password"),
                    action="create_post",
                    data=params.get("data")
                )
            elif action == "create_page":
                result = await agent.manage_content(
                    site_url=params.get("site_url"),
                    username=params.get("username"),
                    app_password=params.get("app_password"),
                    action="create_page",
                    data=params.get("data")
                )
            elif action == "generate_app_password":
                result = await agent.automate_app_password(
                    admin_url=params.get("admin_url"),
                    username=params.get("username"),
                    password=params.get("password")
                )
            else:
                raise ValueError(f"Unsupported WordPress action: {action}")
            
            context.logger.info(f"[WordPressNode] Completed {action}.")
            return result
            
        except Exception as e:
            error_msg = f"WordPress Execution Failed: {str(e)}"
            context.logger.error(error_msg)
            return {"error": str(e), "traceback": traceback.format_exc()}

# Register logic
register_node(WordPressNode())
