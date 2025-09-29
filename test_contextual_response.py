#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced contextual response in deep research.
"""

from research_agent.research_agent.core import ResearchAgent


def test_contextual_response():
    """Test the contextual response generation."""
    print("🧠 Testing Enhanced Contextual Response")
    print("=" * 50)

    agent = ResearchAgent()

    # Test different clarification scenarios
    test_cases = [
        {
            "query": "What are AI developments?",
            "clarification": "1 year only. computer vision. academic research. expert level, AI for semiconductors",
        },
        {
            "query": "What is machine learning?",
            "clarification": "Recent advances, practical applications, beginner level",
        },
        {
            "query": "How does AI work?",
            "clarification": "Technical details, neural networks, deep learning focus",
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Query: {test_case['query']}")
        print(f"Clarification: {test_case['clarification']}")

        response = agent._generate_contextual_response(
            test_case["query"], test_case["clarification"]
        )

        print(f"Contextual Response: {response}")
        print("-" * 30)


if __name__ == "__main__":
    test_contextual_response()
