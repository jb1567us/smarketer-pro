import sys
from pathlib import Path

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import model_client

def test_simple_control():
    """Test if we can generate a simple control doc"""
    system_prompt = "Create a simple project control document. Output ONLY markdown."
    user_prompt = "Create a control doc for a task management app with basic sections."
    
    print("Testing simple control generation with phi3:mini...")
    try:
        response = model_client.generate_text(
            system_prompt,
            user_prompt,
            model="phi3:mini"
        )
        print("✅ SUCCESS!")
        print(f"Generated {len(response)} characters")
        print("First 200 chars:", response[:200])
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    test_simple_control()