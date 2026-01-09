import re
import random

def parse_spintax(text):
    """
    Very simple spintax parser for testing.
    """
    while "{" in text:
        match = re.search(r"\{([^{}]*)\}", text)
        if not match: break
        options = match.group(1).split("|")
        text = text.replace(match.group(0), random.choice(options), 1)
    return text

def calculate_uniqueness(text1, text2):
    """
    Simple Jaccard similarity based uniqueness.
    """
    words1 = set(text1.split())
    words2 = set(text2.split())
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    similarity = len(intersection) / len(union) if union else 0
    return 1 - similarity

# Test Spintax
spintax_content = "{Hello|Hi|Greetings} {this is|here is|we have} a {sample|test|example} for {spintax|spinning|content}."

v1 = parse_spintax(spintax_content)
v2 = parse_spintax(spintax_content)

print(f"Version 1: {v1}")
print(f"Version 2: {v2}")

uniqueness = calculate_uniqueness(v1, v2)
print(f"Uniqueness: {uniqueness*100:.2f}%")

if uniqueness > 0.5:
    print("✅ Spintax verification passed!")
else:
    print("❌ Spintax variety too low.")
