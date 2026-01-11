
# conv_debug.py
import asyncio

class MockStrategy:
    def get(self, key, default=None):
        if key == 'sequence':
            # SIMULATING THE ERROR: A list containing a list
            # This mimics what happens if LLM returns [[...]] and we take it as is
            return [[{"type": "agent", "name": "test"}]] 
        return default

async def test_loop():
    strategy = MockStrategy()
    sequence = strategy.get('sequence', [])
    print(f"Sequence: {sequence}")
    
    for step in sequence:
        print(f"Processing step: {step} (Type: {type(step)})")
        try:
            step_type = step.get('type')
            print(f"Step Type: {step_type}")
        except AttributeError as e:
            print(f"Caught expected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_loop())
