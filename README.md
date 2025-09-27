# Deep Research Agent

An intelligent research orchestrator that conducts comprehensive research using multiple tools, analyzes retrieved data, identifies gaps, and decides next research moves.

## Overview

The Deep Research Agent is designed to function both as an independent agent and as a member of multi-agent systems. It provides four research modes with progressive complexity and comprehensive source tracking to prevent duplicate information.

## Research Modes

- **Instant Research**: Query → Tools → Data → Answer (1 round, 10 sources, 15-30 sec)
- **Quick Research**: Query → Tools → Data → Analyze → More Tools → Enhanced Answer (2 rounds, 20 sources, 1-2 min)
- **Standard Research**: Query → Tools → Data → Analyze → Iterate → Comprehensive Answer (2-5 rounds, 20-50 sources, 8-15 min)
- **Deep Research**: Query → Clarify → Refine Strategy → Comprehensive Research → Exhaustive Answer (5-12 rounds, 50-120 sources, 20-30 min)

## Key Features

- **Progressive Enhancement**: Adapts complexity based on selected mode
- **Source Tracking**: Prevents duplicate sources across research rounds
- **Context-Aware Analysis**: Identifies gaps and generates follow-up queries
- **Clarification System**: Deep mode includes user/agent clarification for refined research
- **Multi-Agent Support**: Compatible with team workflows and independent usage
- **Tool Integration**: Seamlessly integrates with external tools

## Architecture

The agent follows an object-oriented design with:
- **BaseAgent**: Common agent capabilities shared across all agents
- **ResearchAgent**: Specialized research functionality inheriting from BaseAgent
- **Research Orchestrator**: Intelligent coordination of tools, analysis, and decision-making

## Usage

### Via AgentHub
```python
import agenthub as ah

# Load agent with external tools
agent = ah.load_agent("agentplug/research-agent", external_tools=["web_search", "document_retrieval"])

# Specific research modes
result = agent.instant_research("Research question")
result = agent.quick_research("Research question")
result = agent.standard_research("Research question")
result = agent.deep_research("Research question")

# Auto mode selection
result = agent.solve("Research question")
```


## Development

This project is designed to be compatible with the AgentHub framework through standard `agent.py` and `agent.yaml` files.

## Documentation

- [Requirement Analysis](docs/.requirement_analysis/deep_research_agent_requirements.md)
- [Architecture Design](docs/.architecture_design/deep_research_agent_architecture.md)
