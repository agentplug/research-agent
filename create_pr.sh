#!/bin/bash

# Create Pull Request for Architecture Design
# Run this script to create a PR from feat/architecture-design to main

echo "Creating Pull Request..."

# Check if gh CLI is available
if command -v gh &> /dev/null; then
    echo "Using GitHub CLI..."
    gh pr create \
        --title "feat: add comprehensive architecture design for deep research agent" \
        --body "## Overview
This PR adds comprehensive architecture design documentation for the deep research agent, including requirement analysis and detailed system architecture.

## Changes
- **Requirement Analysis**: Complete requirements document with research modes, AgentHub integration, and multi-agent support
- **Architecture Design**: C4 model diagrams (System Context, Container, Component) with detailed component descriptions
- **Research Algorithm**: Mode-specific workflows (instant, quick, standard, deep) with progressive enhancement
- **Source Tracking**: URL-based duplicate prevention mechanism
- **Clarification System**: LLM-powered clarification generation for deep research mode
- **Command-line Interface**: JSON input/output pattern for AgentHub integration
- **Temp File Management**: Replaced database requirements with temp file storage
- **OOP Design**: BaseAgent and ResearchAgent module structure

## Key Features
- **4 Research Modes**: Instant (15-30s), Quick (1-2min), Standard (8-15min), Deep (20-30min)
- **Progressive Enhancement**: Context-aware analysis and follow-up queries
- **Source Tracking**: Prevents duplicate URL scraping
- **Clarification System**: Deep mode includes user/agent clarification
- **Complete Data Return**: All retrieved data returned to output layer

## Architecture Highlights
- **C4 Model**: System Context, Container, and Component diagrams
- **Research Orchestrator**: Intelligent coordination of tools, analysis, and decision-making
- **Tool Ecosystem**: Integration with web search, academic sources, news, and external tools
- **Intelligence Layer**: Gap identification, query generation, and success criteria evaluation

## Technical Decisions
- **Temp Files**: Replaced database with temp file storage for simplicity
- **Command-line Interface**: JSON communication via command line arguments
- **Single Instance**: Focused on efficient single instance performance
- **Modular Design**: BaseAgent and ResearchAgent modules for reusability

## Documentation Structure
- \`docs/.requirement_analysis/\`: Comprehensive requirements analysis
- \`docs/.architecture_design/\`: Detailed architecture design with diagrams

This architecture provides a solid foundation for implementing the deep research agent with clear separation of concerns and scalable design patterns." \
        --base main \
        --head feat/architecture-design
else
    echo "GitHub CLI not found. Please create the PR manually:"
    echo ""
    echo "Title: feat: add comprehensive architecture design for deep research agent"
    echo "Base: main"
    echo "Head: feat/architecture-design"
    echo ""
    echo "URL: https://github.com/agentplug/research-agent/pull/new/feat/architecture-design"
    echo ""
    echo "Description:"
    cat << 'EOF'
## Overview
This PR adds comprehensive architecture design documentation for the deep research agent, including requirement analysis and detailed system architecture.

## Changes
- **Requirement Analysis**: Complete requirements document with research modes, AgentHub integration, and multi-agent support
- **Architecture Design**: C4 model diagrams (System Context, Container, Component) with detailed component descriptions
- **Research Algorithm**: Mode-specific workflows (instant, quick, standard, deep) with progressive enhancement
- **Source Tracking**: URL-based duplicate prevention mechanism
- **Clarification System**: LLM-powered clarification generation for deep research mode
- **Command-line Interface**: JSON input/output pattern for AgentHub integration
- **Temp File Management**: Replaced database requirements with temp file storage
- **OOP Design**: BaseAgent and ResearchAgent module structure

## Key Features
- **4 Research Modes**: Instant (15-30s), Quick (1-2min), Standard (8-15min), Deep (20-30min)
- **Progressive Enhancement**: Context-aware analysis and follow-up queries
- **Source Tracking**: Prevents duplicate URL scraping
- **Clarification System**: Deep mode includes user/agent clarification
- **Complete Data Return**: All retrieved data returned to output layer

## Architecture Highlights
- **C4 Model**: System Context, Container, and Component diagrams
- **Research Orchestrator**: Intelligent coordination of tools, analysis, and decision-making
- **Tool Ecosystem**: Integration with web search, academic sources, news, and external tools
- **Intelligence Layer**: Gap identification, query generation, and success criteria evaluation

## Technical Decisions
- **Temp Files**: Replaced database with temp file storage for simplicity
- **Command-line Interface**: JSON communication via command line arguments
- **Single Instance**: Focused on efficient single instance performance
- **Modular Design**: BaseAgent and ResearchAgent modules for reusability

## Documentation Structure
- `docs/.requirement_analysis/`: Comprehensive requirements analysis
- `docs/.architecture_design/`: Detailed architecture design with diagrams

This architecture provides a solid foundation for implementing the deep research agent with clear separation of concerns and scalable design patterns.
EOF
fi
