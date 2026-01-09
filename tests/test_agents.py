import sys
import os

# Appends src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agents import ReviewerAgent, SyntaxAgent, UXAgent, ResearcherAgent, QualifierAgent, CopywriterAgent

def test_agents():
    print("Initializing Agents...")
    reviewer = ReviewerAgent()
    syntax = SyntaxAgent()
    ux = UXAgent()
    researcher = ResearcherAgent()
    qualifier = QualifierAgent()
    copywriter = CopywriterAgent()

    print("Agents Initialized.")
    print(f"Reviewer Role: {reviewer.role}")
    print(f"Syntax Role: {syntax.role}")
    print(f"UX Role: {ux.role}")
    print(f"Researcher Role: {researcher.role}")
    print(f"Qualifier Role: {qualifier.role}")
    print(f"Copywriter Role: {copywriter.role}")

    # We won't make actual API calls here to save time/cost unless requested, 
    # but we verify imports and instantiation work.
    
if __name__ == "__main__":
    test_agents()
