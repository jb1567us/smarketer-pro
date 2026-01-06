import sys
from pathlib import Path
import time

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import model_client
from model_client import ModelClientError

def test_with_different_models():
    """Test team generation with different models to compare speed"""
    models_to_test = ["phi3:mini", "llama3:latest"]
    
    system_prompt = (
        "You are a project architect. Given an idea, create:\n"
        "- 3-5 roles with 3-5 questions each\n" 
        "- 3-5 global questions\n"
        "Return ONLY valid JSON.\n"
    )

    user_prompt = (
        "I want to build a simple task management app\n\n"
        "Return JSON:\n"
        "{\n"
        '  \"project_title\": \"string\",\n'
        '  \"summary\": \"string\",\n'  
        '  \"roles\": [{\"id\": \"snake_case\", \"label\": \"string\", \"purpose\": \"string\", \"questions\": [{\"id\": \"string\", \"text\": \"string\", \"priority\": 1}]}],\n'
        '  \"global_questions\": [{\"id\": \"string\", \"text\": \"string\", \"priority\": 1}]\n'
        "}"
    )

    for model_name in models_to_test:
        print(f"\n🧪 Testing model: {model_name}")
        start_time = time.time()
        
        try:
            response = model_client.generate_text(
                system_prompt, 
                user_prompt, 
                model=model_name  # Override with specific model
            )
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ SUCCESS in {duration:.1f}s")
            print(f"   Response length: {len(response)} chars")
            
            # Validate it's proper JSON
            import json
            data = json.loads(response)
            roles_count = len(data.get('roles', []))
            questions_count = sum(len(role.get('questions', [])) for role in data.get('roles', []))
            global_questions = len(data.get('global_questions', []))
            
            print(f"   Generated: {roles_count} roles, {questions_count} role questions, {global_questions} global questions")
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            print(f"❌ FAILED after {duration:.1f}s: {e}")

if __name__ == "__main__":
    test_with_different_models()