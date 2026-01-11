
# conv_check.py

def normalize(conv_res):
    final_sequence = []
    if isinstance(conv_res, list):
        # Fix: Handle nested lists (LLM sometimes wraps result in [ [... ] ])
        if len(conv_res) > 0 and isinstance(conv_res[0], list):
            final_sequence = conv_res[0]
        else:
            final_sequence = conv_res
    return final_sequence

def test():
    # Case 1: Nested List (The bug)
    nested = [[{"type": "agent", "name": "researcher"}]]
    res = normalize(nested)
    print(f"Input: {nested}")
    print(f"Output: {res}")
    
    if len(res) == 1 and isinstance(res[0], dict):
        print("✅ Nested list handled correctly.")
    else:
        print("❌ Failed to flatten nested list.")

    # Case 2: Normal List
    normal = [{"type": "agent", "name": "writer"}]
    res2 = normalize(normal)
    print(f"Input: {normal}")
    print(f"Output: {res2}")
    
    if len(res2) == 1 and isinstance(res2[0], dict):
        print("✅ Normal list handled correctly.")
    else:
        print("❌ Normal list corrupted.")

if __name__ == "__main__":
    test()
