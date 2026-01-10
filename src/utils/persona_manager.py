import yaml
import os
import json
from pathlib import Path

class PersonaManager:
    def __init__(self, personas_dir=None):
        self.personas_dir = Path(personas_dir or os.path.join('src', 'data', 'personas'))
        self.personas_dir.mkdir(parents=True, exist_ok=True)
        self.personas = {}
        self._load_personas()

    def _load_personas(self):
        """Loads all personas from the personas directory."""
        for persona_file in self.personas_dir.glob('*.yaml'):
            try:
                with open(persona_file, 'r', encoding='utf-8') as f:
                    persona_data = yaml.safe_load(f)
                    if persona_data and 'name' in persona_data:
                        self.personas[persona_data['name'].lower()] = persona_data
            except Exception as e:
                print(f"[PersonaManager] Error loading persona {persona_file}: {e}")

    def get_persona(self, name):
        """Retrieves a persona by name."""
        return self.personas.get(name.lower())

    def list_personas(self):
        """Lists all available persona names."""
        return list(self.personas.keys())

    def create_persona(self, name, role, goal, backplane_prompt="", style_instructions="", icon=None):
        """Creates and saves a new persona."""
        persona_data = {
            "name": name,
            "role": role,
            "goal": goal,
            "backplane_prompt": backplane_prompt,
            "style_instructions": style_instructions,
            "icon": icon
        }
        file_path = self.personas_dir / f"{name.lower().replace(' ', '_')}.yaml"
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(persona_data, f, default_flow_style=False)
        
        self.personas[name.lower()] = persona_data
        return persona_data

    def get_system_prompt(self, persona_name):
        """Constructs a system prompt from a persona."""
        persona = self.get_persona(persona_name)
        if not persona:
            return None
        
        return (
            f"Role: {persona.get('role')}\n"
            f"Goal: {persona.get('goal')}\n"
            f"Context: {persona.get('backplane_prompt', '')}\n"
            f"Style: {persona.get('style_instructions', '')}"
        )

persona_manager = PersonaManager()
