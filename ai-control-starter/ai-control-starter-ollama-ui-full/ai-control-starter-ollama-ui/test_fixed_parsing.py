import sys
from pathlib import Path

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Import the fixed function
from scripts.qna_web import generate_team_and_questions

def test_fixed_parsing():
    """Test that the fixed JSON parsing works"""
    idea = "I want to build a simple task management app"
    
    print("🧪 Testing fixed JSON parsing...")
    try:
        result = generate_team_and_questions(idea)
        
        print("✅ SUCCESS!")
        print(f"Project Title: {result.get('project_title')}")
        print(f"Summary: {result.get('summary')}")
        print(f"Roles: {len(result.get('roles', []))}")
        
        for role in result.get('roles', []):
            questions_count = len(role.get('questions', []))
            print(f"  - {role.get('label')}: {questions_count} questions")
            
        print(f"Global Questions: {len(result.get('global_questions', []))}")
        
        # Validate the structure
        required_fields = ['project_title', 'summary', 'roles', 'global_questions']
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
        else:
            print("✅ All required fields present")
            
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_fixed_parsing()
    if success:
        print("\n🎉 The fixed parsing is working! You can now run the web UI.")
    else:
        print("\n💥 There's still an issue that needs to be fixed.")