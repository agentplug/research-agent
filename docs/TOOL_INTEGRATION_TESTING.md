# 🧪 Tool Integration Testing Guide

## Overview

This guide provides multiple ways to test the tool integration functionality in the Research Agent.

## 🚀 Quick Start

### Method 1: Run Simple Test Suite
```bash
python examples/simple_tool_test.py
```

### Method 2: Run Enhanced Test Suite
```bash
python examples/simple_tool_test_v2.py
```

## 🔍 Manual Testing

### Test Web Search Tool
```bash
python agent.py '{"method": "instant_research", "parameters": {"query": "What is the latest news about AI?"}, "tool_context": {"available_tools": ["web_search"], "tool_descriptions": {"web_search": "Search the web for current information"}}}'
```

### Test Calculation Tool
```bash
python agent.py '{"method": "instant_research", "parameters": {"query": "Calculate 15% of 250"}, "tool_context": {"available_tools": ["calculate"], "tool_descriptions": {"calculate": "Perform mathematical calculations"}}}'
```

### Test Multiple Tools
```bash
python agent.py '{"method": "quick_research", "parameters": {"query": "What are AI developments and calculate market growth?"}, "tool_context": {"available_tools": ["web_search", "calculate"], "tool_descriptions": {"web_search": "Search the web", "calculate": "Calculate math"}}}'
```

### Test Agent Status
```bash
python agent.py '{"method": "get_agent_status", "parameters": {}, "tool_context": {"available_tools": ["web_search", "calculate"], "tool_descriptions": {"web_search": "Search the web", "calculate": "Calculate math"}}}'
```

### Test Tool Usage Stats
```bash
python agent.py '{"method": "get_tool_usage_stats", "parameters": {}, "tool_context": {"available_tools": ["web_search", "calculate"], "tool_descriptions": {"web_search": "Search the web", "calculate": "Calculate math"}}}'
```

## 🎯 What to Look For

### Successful Tool Integration Indicators:
1. **Tool Call Detection**: Look for `"tool_call"` in the response
2. **Tool Results**: Look for `"--- TOOL RESULTS ---"` section
3. **Tool Usage**: Check that tools are actually used in the content
4. **Agent Status**: Verify `tool_integration` section shows available tools

### Example Successful Response:
```json
{
  "result": {
    "success": true,
    "data": {
      "content": "{\"tool_call\": {\"tool_name\": \"web_search\", \"arguments\": {\"query\": \"latest AI news\"}}}\n\n--- TOOL RESULTS ---\nWeb search results for 'latest AI news':\n1. Search result for: latest AI news\n   This is a simulated search result...\n   URL: https://example.com/search?q=latest AI news"
    }
  }
}
```

## 🔧 Available Tools

### Web Search Tool
- **Name**: `web_search`
- **Purpose**: Search the web for current information
- **Usage**: Automatically triggered for queries about current events, news, recent developments

### Calculation Tool
- **Name**: `calculate`
- **Purpose**: Perform mathematical calculations
- **Usage**: Automatically triggered for mathematical expressions, percentages, calculations

### Document Retrieval Tool
- **Name**: `document_retrieval`
- **Purpose**: Extract and analyze documents
- **Usage**: Automatically triggered for document analysis requests

## 📊 Testing Different Research Modes

### Instant Research
- **Rounds**: 1
- **Tool Usage**: Single tool call per query
- **Best For**: Quick answers with tool assistance

### Quick Research
- **Rounds**: 2
- **Tool Usage**: Tools used in first round, analysis in second
- **Best For**: Enhanced research with tool integration

### Standard Research
- **Rounds**: 3
- **Tool Usage**: Tools used across multiple rounds
- **Best For**: Comprehensive research with tool assistance

### Deep Research
- **Rounds**: 4
- **Tool Usage**: Tools used with clarification system
- **Best For**: Exhaustive research with tool integration

## 🐛 Troubleshooting

### Common Issues:

1. **Tool Not Used**
   - Check if query triggers tool usage keywords
   - Verify tool context is properly formatted
   - Ensure tool descriptions are clear

2. **JSON Parsing Errors**
   - Check for proper escaping in command line
   - Use single quotes around JSON strings
   - Verify JSON structure

3. **Timeout Issues**
   - Increase timeout for complex queries
   - Check LLM service status
   - Verify network connectivity

### Debug Commands:

```bash
# Check agent status
python agent.py '{"method": "get_agent_status", "parameters": {}, "tool_context": {"available_tools": ["web_search"], "tool_descriptions": {"web_search": "Search the web"}}}'

# Test with minimal tool context
python agent.py '{"method": "instant_research", "parameters": {"query": "test"}, "tool_context": {"available_tools": [], "tool_descriptions": {}}}'
```

## 🎉 Success Criteria

A successful tool integration test should show:
- ✅ Tools are detected and available
- ✅ LLM generates appropriate tool calls
- ✅ Tools are executed successfully
- ✅ Tool results are integrated into research
- ✅ Agent status shows tool information
- ✅ Tool usage stats are tracked

## 📈 Performance Testing

### Load Testing
```bash
# Run multiple tests in parallel
for i in {1..5}; do
  python examples/simple_tool_test_v2.py &
done
wait
```

### Memory Testing
```bash
# Monitor memory usage during tool execution
python -m memory_profiler examples/simple_tool_test_v2.py
```

## 🔄 Continuous Testing

### Automated Testing Script
```bash
#!/bin/bash
# Run tests and report results
python examples/simple_tool_test_v2.py > test_results.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ All tests passed"
else
    echo "❌ Some tests failed"
    cat test_results.log
fi
```

This comprehensive testing approach ensures your tool integration is working correctly across all scenarios! 🚀
