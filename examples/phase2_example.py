import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent import ResearchAgent


def main():
    """Demonstrate direct ResearchAgent usage."""
    print("🚀 Phase 2 Example - Direct ResearchAgent Usage")
    print("=" * 50)

    # Initialize agent directly
    agent = ResearchAgent()
    print("✅ ResearchAgent initialized directly")

    # # Test instant research
    # print("\n📝 Testing Instant Research:")
    # result = agent.instant_research("What is Python?")
    # print(f"Success: {result['success']}")
    # print(f"Content: {result['data']['content'][:100]}...")

    # # Test quick research
    # print("\n⚡ Testing Quick Research:")
    # result = agent.quick_research("What is machine learning?")
    # print(f"Success: {result['success']}")
    # print(f"Rounds: {result['data']['research_rounds']}")

    # # Test standard research
    # print("\n🔍 Testing Standard Research:")
    # result = agent.standard_research("What is artificial intelligence?")
    # print(f"Success: {result['success']}")
    # print(f"Rounds: {result['data']['research_rounds']}")

    # Test deep research with interactive clarification
    print("\n🧠 Testing Deep Research (Interactive Clarification):")
    result = agent.deep_research("What are AI developments?")
    print(f"\nFinal result - Success: {result['success']}")
    print(f"Research rounds: {result['data'].get('research_rounds', 0)}")

    # Display the research content properly
    content = result["data"].get("content", "")
    if isinstance(content, dict):
        print(f"\n📋 Research Summary:")
        print(f"Total rounds: {content.get('total_rounds', 0)}")
        print(f"Research summary: {content.get('research_summary', 'N/A')}")

        # Display each round's content
        rounds = content.get("rounds", [])
        for i, round_data in enumerate(rounds, 1):
            print(f"\n--- Round {i} ---")
            print(f"Query: {round_data.get('query', 'N/A')}")
            round_content = round_data.get("content", "")
            if isinstance(round_content, str):
                print(f"Content preview: {round_content[:200]}...")
            else:
                print(f"Content: {round_content}")
    elif isinstance(content, str):
        print(f"\n📋 Research Content:")
        print(f"Content preview: {content[:200]}...")
    else:
        print(f"\n📋 Research Content:")
        print(f"Content type: {type(content)}")
        print(f"Content: {content}")

    # Test agent status
    print("\n📊 Agent Status:")
    status = agent.get_agent_status()
    print(f"Agent type: {status['data']['agent_type']}")
    print(f"Available modes: {status['data']['available_modes']}")
    print(f"Total researches: {status['data']['research_history']['total_researches']}")

    print("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    main()
