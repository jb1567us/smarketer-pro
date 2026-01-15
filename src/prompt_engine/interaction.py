import os
import jinja2
from .models import PromptContext

class PromptEngine:
    """
    The Genesis Prompt Engine.
    Render high-fidelity prompts using Jinja2 templates and the Kernel Context.
    """
    def __init__(self, template_dir=None):
        if not template_dir:
            # Default to 'templates' directory relative to this file
            base_dir = os.path.dirname(os.path.abspath(__file__))
            template_dir = os.path.join(base_dir, 'templates')
        
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register standard filters if needed
        self.template_env.filters['bullet_list'] = self._filter_bullet_list

    def _filter_bullet_list(self, value):
        if not value:
            return ""
        if isinstance(value, list):
            return "\n".join([f"- {item}" for item in value])
        return str(value)

    def get_prompt(self, template_name: str, context: PromptContext, **kwargs) -> str:
        """
        Render a specific template with the given context.
        
        :param template_name: Path to template relative to templates root (e.g. 'copywriter/email_cold.j2')
        :param context: The PromptContext (The Kernel)
        :param kwargs: Additional one-off variables for this specific render (e.g. 'recipient_name')
        :return: Rendered prompt string
        """
        try:
            template = self.template_env.get_template(template_name)
            
            # Combine generic context vars with specific kwargs
            render_vars = context.to_dict()
            render_vars.update(kwargs)
            
            return template.render(**render_vars)
        except jinja2.TemplateNotFound:
            return f"ERROR: Template '{template_name}' not found."
        except Exception as e:
            return f"ERROR rendering template '{template_name}': {str(e)}"
