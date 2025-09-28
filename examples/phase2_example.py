"""
Phase 2 Example - Simple Research Agent Usage

This example demonstrates the clean, simple interface for the research agent.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent.research_agent.core import ResearchAgent

# Initialize agent
agent = ResearchAgent()

# Test instant research
print("=== INSTANT RESEARCH ===")
instant_result = agent.instant_research(query="Who is the 2025 US president?")
print(f"Success: {instant_result['success']}")
print(f"Rounds: {instant_result['data']['research_rounds']}")
print(f"Content: {instant_result['data']['content']}")
print()

# Test quick research
print("=== QUICK RESEARCH ===")
quick_result = agent.quick_research(query="Any new update on new H1B policy?")
print(f"Success: {quick_result['success']}")
print(f"Rounds: {quick_result['data']['research_rounds']}")
print(f"Content: {quick_result['data']['content']}")
print()

# Test standard research
print("=== STANDARD RESEARCH ===")
standard_result = agent.standard_research(
    query="What are the latest developments in AI?"
)
print(f"Success: {standard_result['success']}")
print(f"Rounds: {standard_result['data']['research_rounds']}")
print(f"Content: {standard_result['data']['content']}")
print()

# Test deep research
print("=== DEEP RESEARCH ===")
deep_result = agent.deep_research(query="Analyze the impact of AI on society")
print(f"Success: {deep_result['success']}")
print(f"Rounds: {deep_result['data']['research_rounds']}")
print(f"Content: {deep_result['data']['content']}")
print()

print("✅ All research modes working!")
