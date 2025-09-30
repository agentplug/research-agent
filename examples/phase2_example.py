import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent import ResearchAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Demonstrate direct ResearchAgent usage."""
    logger.info("🚀 Phase 2 Example - Direct ResearchAgent Usage")
    logger.info("=" * 50)

    # Initialize agent directly
    agent = ResearchAgent()
    logger.info("✅ ResearchAgent initialized directly")

    # # Test instant research
    # logger.info("\n📝 Testing Instant Research:")
    # result = agent.instant_research("What is Python?")
    # logger.info(f"Success: {result['success']}")
    # logger.info(f"Content: {result['data']['content'][:100]}...")

    # # Test quick research
    # logger.info("\n⚡ Testing Quick Research:")
    # result = agent.quick_research("What is machine learning?")
    # logger.info(f"Success: {result['success']}")
    # logger.info(f"Rounds: {result['data']['research_rounds']}")

    # # Test standard research
    # logger.info("\n🔍 Testing Standard Research:")
    # result = agent.standard_research("What is artificial intelligence?")
    # logger.info(f"Success: {result['success']}")
    # logger.info(f"Rounds: {result['data']['research_rounds']}")

    # Test deep research with interactive clarification
    logger.info("\n🧠 Testing Deep Research (Interactive Clarification):")
    result = agent.deep_research("What are AI developments?")
    logger.info(f"\nFinal result - Success: {result['success']}")
    logger.info(f"Research rounds: {result['data'].get('research_rounds', 0)}")

    # Display the research content properly
    content = result["data"].get("content", "")
    if isinstance(content, dict):
        logger.info(f"\n📋 Research Summary:")
        logger.info(f"Total rounds: {content.get('total_rounds', 0)}")
        logger.info(f"Research summary: {content.get('research_summary', 'N/A')}")

        # Display each round's content
        rounds = content.get("rounds", [])
        for i, round_data in enumerate(rounds, 1):
            logger.info(f"\n--- Round {i} ---")
            logger.info(f"Query: {round_data.get('query', 'N/A')}")
            round_content = round_data.get("content", "")
            if isinstance(round_content, str):
                logger.info(f"Content preview: {round_content[:200]}...")
            else:
                logger.info(f"Content: {round_content}")
    elif isinstance(content, str):
        logger.info(f"\n📋 Research Content:")
        logger.info(f"Content preview: {content[:200]}...")
    else:
        logger.info(f"\n📋 Research Content:")
        logger.info(f"Content type: {type(content)}")
        logger.info(f"Content: {content}")

    # Test agent status
    logger.info("\n📊 Agent Status:")
    status = agent.get_agent_status()
    logger.info(f"Agent type: {status['data']['agent_type']}")
    logger.info(f"Available modes: {status['data']['available_modes']}")
    logger.info(f"Total researches: {status['data']['research_history']['total_researches']}")

    logger.info("\n✅ All tests completed successfully!")


if __name__ == "__main__":
    main()
