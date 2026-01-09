import sys
from pathlib import Path

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import model_client
from model_client import ModelClientError

def test_team_generation():
    """Test the exact call the web UI makes"""
    system_prompt = (
        "You are an AI project architect.\n"
        "Given a project idea, you must:\n"
        "- Create a list of roles.\n"
        "- For each role, include 3–7 high-value questions.\n"
        "- Include 3–10 global questions.\n"
        "Return ONLY valid JSON.\n"
    )

    user_prompt = (
        "Project idea:\n"
        "----------------------\n"
        "I want to build a simple task management app\n"
        "----------------------\n\n"
        "Return JSON in this shape:\n\n"
        "{\n"
        '  \"project_title\": \"string\",\n'
        '  \"summary\": \"string\",\n'
        '  \"roles\": [\n'
        "    {\n"
        '      \"id\": \"snake_case\",\n'
        '      \"label\": \"string\",\n'
        '      \"purpose\": \"string\",\n'
        '      \"questions\": [\n'
        "        {\"id\": \"string\", \"text\": \"string\", \"priority\": 1}\n"
        "      ]\n"
        "    }\n"
        "  ],\n"
        '  \"global_questions\": [\n'
        "    {\"id\": \"string\", \"text\": \"string\", \"priority\": 1}\n"
        "  ]\n"
        "}\n"
    )

    try:
        print("Testing team generation (this may take 30-60 seconds)...")
        response = model_client.generate_text(system_prompt, user_prompt, task="planning")
        print("✓ Team generation SUCCESS!")
        print(f"Response length: {len(response)} characters")
        print(f"First 200 chars: {response[:200]}...")
        return True
    except ModelClientError as e:
        print(f"✗ Team generation FAILED: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_team_generation()
    if not success:
        print("\nThe web UI will fail with this error.")
        print("Let's check which model is being used...")
        
        # Check which model is configured for planning
        import json
        config_path = Path("model_config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            planning_model = config.get('tasks', {}).get('planning', 'unknown')
            print(f"Planning task model: {planning_model}")