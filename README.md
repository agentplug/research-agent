# Deep Research Agent

An intelligent research agent that conducts comprehensive research using LLM integration, analyzes retrieved data, identifies gaps, and decides next research moves.

## Overview

The Deep Research Agent provides four research modes with progressive complexity and comprehensive clarification system for deep research. Built with KISS & YAGNI principles - direct ResearchAgent interface with no unnecessary wrapper classes.

## Research Modes

- **Instant Research**: Quick answers (1 round, ~2 sec)
- **Quick Research**: Enhanced analysis (2 rounds, ~5 sec)
- **Standard Research**: Comprehensive research (3 rounds, ~10 sec)
- **Deep Research**: Exhaustive research with clarification (4 rounds + clarification, ~15 sec)

## Key Features

- **Progressive Enhancement**: Adapts complexity based on selected mode
- **Clarification System**: Deep mode includes user clarification for refined research
- **Contextual Responses**: LLM-generated natural responses that acknowledge user requirements
- **Multi-Round Analysis**: Intelligent gap analysis and follow-up queries
- **Direct Interface**: Simple ResearchAgent class - no wrapper complexity
- **LLM Integration**: Unified AISuite integration for multiple providers
- **KISS & YAGNI**: Clean, maintainable code following best practices

## Architecture

The agent follows a modular design with:
- **ResearchAgent**: Main interface with all research capabilities
- **Analysis Engine**: Mode-specific analysis and gap identification
- **Research Workflows**: Multi-round research orchestration
- **Clarification System**: Deep research clarification and intention generation
- **LLM Service**: Unified AISuite integration

## Usage

### Direct Usage
```python
from research_agent.research_agent.core import ResearchAgent

# Initialize agent directly
agent = ResearchAgent()

# Specific research modes
result = agent.instant_research("What is Python?")
result = agent.quick_research("What is machine learning?")
result = agent.standard_research("What is artificial intelligence?")

# Deep research with interactive clarification
result = agent.deep_research("What are AI developments?")
# This will automatically ask for clarification using input() and then proceed
# The system will generate a contextual response acknowledging your specific requirements

# Or provide clarification directly
result = agent.deep_research("What are AI developments?", "Focus on recent ML developments")

# Agent status and testing
status = agent.get_agent_status()
test_results = agent.test_agent()
```

### Command Line Interface
```bash
# Status check
python agent.py --status

# Instant research
python agent.py --mode instant --query "What is Python?"

# Deep research
python agent.py --mode deep --query "What are AI developments?"

# With clarification context
python agent.py --mode deep --query "What are AI developments?" --context '{"user_clarification": "Focus on recent ML developments"}'
```


## Development

This project is designed to be compatible with the AgentHub framework through standard `agent.py` and `agent.yaml` files.

## Documentation

- [Requirement Analysis](docs/.requirement_analysis/deep_research_agent_requirements.md)
- [Architecture Design](docs/.architecture_design/deep_research_agent_architecture.md)
