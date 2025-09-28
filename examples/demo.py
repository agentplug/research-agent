"""
Research Agent - Maximum Value Demo

The simplest code to demonstrate all core functionality.
Just run: python examples/demo.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import ResearchAgentHub


def main():
    """One simple demo showing maximum value."""
    print("🔬 Research Agent Demo")
    print("=" * 30)
    
    # Initialize agent
    agent = ResearchAgentHub()
    if not agent.initialize_agent():
        print("❌ Failed to initialize")
        return
    
    print("✅ Agent ready!")
    
    # Test all modes with one question
    question = "What is artificial intelligence?"
    
    modes = [
        ("instant", "⚡"),
        ("quick", "🚀"), 
        ("standard", "📊"),
        ("deep", "🔍")
    ]
    
    for mode, icon in modes:
        print(f"\n{icon} {mode.title()} research:")
        
        if mode == "instant":
            result = agent.instant_research(question)
        elif mode == "quick":
            result = agent.quick_research(question)
        elif mode == "standard":
            result = agent.standard_research(question)
        elif mode == "deep":
            result = agent.deep_research(question)
        
        if result['success']:
            content = result['data']['response']['data']['content']
            print(f"   {content[:60]}...")
            
            # Show key metrics
            rounds = result['data']['research_rounds']
            sources = result['data']['sources_used']
            print(f"   📊 {rounds} rounds, {sources} sources")
        else:
            print(f"   ❌ Failed: {result['message']}")
    
    # Show agent capabilities
    print(f"\n🎯 Agent capabilities: {len(agent.get_agent_status()['capabilities'])}")
    print("✅ All research modes working!")
    print("\n💡 Try: python agent.py --query 'Your question' --mode instant")


if __name__ == "__main__":
    main()
