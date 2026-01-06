import sys
from pathlib import Path
import json

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import model_client
from model_client import ModelClientError

def debug_ai_response():
    """See exactly what the AI is returning"""
    system_prompt = "Create project team JSON from idea. Be concise."
    
    user_prompt = (
        f"Idea: I want to build a simple task management app\n\n"
        "JSON format: {project_title, summary, roles: [{id, label, purpose, questions: [{id, text}]}], global_questions: [{id, text}]}"
    )

    try:
        print("🧪 Sending request to AI...")
        response = model_client.generate_text(system_prompt, user_prompt, model="phi3:mini")
        
        print("📨 RAW RESPONSE:")
        print("=" * 50)
        print(repr(response))  # Show exact characters including whitespace
        print("=" * 50)
        print(f"Response length: {len(response)}")
        print(f"First 500 chars: {response[:500]}")
        
        # Try to parse as JSON
        try:
            data = json.loads(response)
            print("✅ JSON parsing SUCCESS!")
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing FAILED: {e}")
            
            # Try to clean the response
            print("\n🔄 Trying to clean response...")
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.strip("`")
                if cleaned.lower().startswith("json"):
                    cleaned = cleaned[4:].strip()
            
            print(f"Cleaned response: {repr(cleaned)}")
            
            try:
                data = json.loads(cleaned)
                print("✅ Cleaned JSON parsing SUCCESS!")
                print(json.dumps(data, indent=2))
            except json.JSONDecodeError as e2:
                print(f"❌ Still failed after cleaning: {e2}")
                
    except ModelClientError as e:
        print(f"❌ Model error: {e}")

if __name__ == "__main__":
    debug_ai_response()