# Research Agent Examples

This folder contains the simplest possible example to demonstrate the Research Agent's maximum value.

## demo.py - Maximum Value Demo

**Purpose**: Show all core functionality in the simplest possible code
**What it demonstrates**:
- ✅ Agent initialization
- ✅ All 4 research modes (instant, quick, standard, deep)
- ✅ Response content and metadata
- ✅ Research metrics (rounds, sources)
- ✅ Agent capabilities
- ✅ Command-line usage hint

**Run with**: `python examples/demo.py`

## Expected Output

```
🔬 Research Agent Demo
==============================
✅ Agent ready!

⚡ Instant research:
   Based on the available information, What is artificial intel...
   📊 1 rounds, 0 sources

🚀 Quick research:
   Enhanced analysis of What is artificial intelligence? reveal...
   📊 1 rounds, 2 sources

📊 Standard research:
   Comprehensive research on What is artificial intelligence? s...
   📊 4 rounds, 8 sources

🔍 Deep research:
   Exhaustive research on What is artificial intelligence? demo...
   📊 4 rounds, 10 sources

🎯 Agent capabilities: 12
✅ All research modes working!

💡 Try: python agent.py --query 'Your question' --mode instant
```

## Quick Start

1. **Run the demo**:
   ```bash
   python examples/demo.py
   ```

2. **Try command-line interface**:
   ```bash
   python agent.py --query "What is machine learning?" --mode instant
   python agent.py --test
   ```

## What This Shows

- **Instant**: Fastest, single round, basic response
- **Quick**: Enhanced context, still single round  
- **Standard**: Multiple rounds, comprehensive analysis
- **Deep**: Most thorough, exhaustive research

Each mode shows different complexity levels and response quality, demonstrating the agent's flexibility for different use cases.