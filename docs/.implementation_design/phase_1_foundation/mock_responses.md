# Mock Response Templates - Phase 1 Foundation

## Overview

This document provides detailed mock response templates for Phase 1 testing, ensuring realistic responses that demonstrate mode-specific behavior differences.

## Response Format Standard

All responses should follow this consistent JSON format:

```json
{
    "result": "Research response content",
    "mode": "instant|quick|standard|deep",
    "sources": ["source1", "source2", ...],
    "status": "success|error",
    "timestamp": "2024-01-01T00:00:00Z",
    "metadata": {
        "rounds_completed": 1,
        "sources_used": 10,
        "execution_time": "15s"
    }
}
```

## Mode-Specific Response Templates

### Instant Research Responses

**Characteristics**: 1-2 sentences, direct facts, essential information

**Template**:
```python
INSTANT_RESPONSES = [
    "Based on available information, {question} can be answered as follows: [Concise 1-2 sentence response with key facts]",
    "Quick answer to {question}: [Direct response with essential information]",
    "Direct response to {question}: [Brief, factual answer]"
]
```

**Example Responses**:
```python
# Question: "What is AI?"
"Based on available information, What is AI? can be answered as follows: Artificial Intelligence (AI) refers to computer systems that can perform tasks typically requiring human intelligence, such as learning, reasoning, and problem-solving."

# Question: "How does machine learning work?"
"Quick answer to How does machine learning work?: Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed, using algorithms to identify patterns in data."

# Question: "What is the capital of France?"
"Direct response to What is the capital of France?: The capital of France is Paris, located in the north-central part of the country."
```

### Quick Research Responses

**Characteristics**: 2-3 paragraphs, enhanced context, relevant details

**Template**:
```python
QUICK_RESPONSES = [
    "Enhanced analysis of {question}: [2-3 paragraph response with context and relevant details]",
    "Comprehensive answer to {question}: [Medium-length response with insights and context]",
    "Detailed response to {question}: [Enhanced response with additional information]"
]
```

**Example Responses**:
```python
# Question: "How does machine learning work?"
"Enhanced analysis of How does machine learning work?: 

Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed. The process involves feeding large amounts of data into algorithms that can identify patterns and make predictions or decisions based on that data.

There are three main types of machine learning: supervised learning (using labeled data to train models), unsupervised learning (finding patterns in unlabeled data), and reinforcement learning (learning through trial and error with rewards and penalties). Common applications include image recognition, natural language processing, recommendation systems, and predictive analytics.

The effectiveness of machine learning depends on the quality and quantity of data, the choice of algorithms, and the computational resources available. Modern machine learning systems can process vast amounts of data and achieve human-level or superior performance in many specific tasks."
```

### Standard Research Responses

**Characteristics**: 4-5 paragraphs, comprehensive analysis, multiple perspectives

**Template**:
```python
STANDARD_RESPONSES = [
    "Thorough analysis of {question}: [4-5 paragraph response with comprehensive coverage]",
    "In-depth research on {question}: [Detailed response with multiple perspectives]",
    "Comprehensive study of {question}: [Thorough analysis with detailed findings]"
]
```

**Example Responses**:
```python
# Question: "What are the latest developments in AI research?"
"Thorough analysis of What are the latest developments in AI research?:

The field of artificial intelligence has seen remarkable progress in recent years, with several key developments shaping the current landscape. Large language models (LLMs) like GPT-4, Claude, and Gemini have revolutionized natural language processing, demonstrating capabilities in text generation, translation, and reasoning that were previously thought to be years away.

In the realm of computer vision, multimodal AI systems are becoming increasingly sophisticated, able to process and understand images, text, and audio simultaneously. These systems are being applied in areas such as autonomous vehicles, medical imaging, and content moderation. The integration of vision and language models has opened new possibilities for AI assistants that can understand and interact with the world in more human-like ways.

Machine learning research has also focused on improving efficiency and reducing computational requirements. Techniques like model compression, quantization, and knowledge distillation are making it possible to deploy powerful AI models on smaller devices and with lower energy consumption. This democratization of AI technology is enabling more widespread adoption across industries.

Ethical AI and AI safety have become central concerns in the research community. Researchers are developing methods for AI alignment, ensuring that AI systems behave according to human values and intentions. This includes work on interpretability, robustness, and fairness in AI systems. The development of AI safety frameworks and guidelines is becoming increasingly important as AI systems become more powerful and widespread.

Looking ahead, the convergence of AI with other technologies like quantum computing, biotechnology, and robotics promises to unlock new possibilities. Research in areas such as artificial general intelligence (AGI), neuromorphic computing, and brain-computer interfaces continues to push the boundaries of what's possible with AI technology."
```

### Deep Research Responses

**Characteristics**: 6+ paragraphs, academic-level analysis, clarification questions, detailed findings

**Template**:
```python
DEEP_RESPONSES = [
    "Exhaustive research on {question}: [6+ paragraph response with academic-level analysis]",
    "Comprehensive analysis of {question}: [Detailed response with clarification questions]",
    "Detailed investigation of {question}: [Exhaustive coverage with detailed findings]"
]
```

**Example Responses**:
```python
# Question: "Comprehensive analysis of AI ethics"
"Exhaustive research on Comprehensive analysis of AI ethics:

The ethical implications of artificial intelligence represent one of the most critical challenges of our time, requiring careful consideration of multiple dimensions including fairness, transparency, accountability, privacy, and human autonomy. This comprehensive analysis examines the current state of AI ethics, emerging challenges, and potential solutions.

**Fairness and Bias in AI Systems**: One of the most pressing ethical concerns is the potential for AI systems to perpetuate or amplify existing biases. Machine learning models trained on historical data often reflect societal prejudices, leading to discriminatory outcomes in areas such as hiring, lending, and criminal justice. Research has shown that facial recognition systems can have significantly higher error rates for certain demographic groups, while algorithmic decision-making in healthcare can lead to disparities in treatment recommendations. Addressing these issues requires diverse training data, bias detection algorithms, and ongoing monitoring of AI system outputs.

**Transparency and Explainability**: The "black box" nature of many AI systems raises questions about transparency and explainability. When AI systems make decisions that affect people's lives, there is a growing demand for explanations of how those decisions were reached. This is particularly important in high-stakes applications like medical diagnosis, financial decisions, and legal proceedings. Researchers are developing techniques for explainable AI, including attention mechanisms, feature importance analysis, and counterfactual explanations. However, there is often a trade-off between model performance and explainability, requiring careful balance.

**Privacy and Data Protection**: AI systems often require large amounts of personal data to function effectively, raising concerns about privacy and data protection. The collection, storage, and use of personal information must comply with regulations like GDPR and CCPA, while also considering the potential for data breaches and misuse. Techniques like differential privacy, federated learning, and homomorphic encryption are being developed to enable AI systems to learn from data without compromising individual privacy. The challenge lies in implementing these techniques without significantly degrading system performance.

**Accountability and Responsibility**: Determining who is responsible when AI systems cause harm is a complex ethical question. Traditional legal frameworks may not adequately address cases where AI systems make autonomous decisions. Questions arise about whether responsibility lies with the developers, the users, the organizations deploying the systems, or the AI systems themselves. This has led to discussions about AI personhood, liability frameworks, and the need for new legal and regulatory structures.

**Human Autonomy and Agency**: As AI systems become more capable, there are concerns about their impact on human autonomy and agency. The delegation of decision-making to AI systems could lead to a loss of human skills and judgment. There are also concerns about AI systems being used to manipulate human behavior, as seen in social media algorithms and recommendation systems. Maintaining human agency requires careful design of AI systems that augment rather than replace human capabilities.

**Future Considerations**: As AI technology continues to advance, new ethical challenges will emerge. The development of artificial general intelligence (AGI) could raise questions about AI rights and consciousness. The integration of AI with other technologies like brain-computer interfaces and genetic engineering could create new ethical dilemmas. Ongoing research, public discourse, and international cooperation will be essential to address these challenges and ensure that AI technology benefits humanity while minimizing potential harms."
```

## Error Response Templates

### Common Error Scenarios

**Network Timeout**:
```json
{
    "result": "Error conducting instant research: Network timeout - unable to connect to external services",
    "mode": "instant",
    "sources": [],
    "status": "error",
    "timestamp": "2024-01-01T00:00:00Z",
    "metadata": {
        "error_type": "network_timeout",
        "execution_time": "30s"
    }
}
```

**Invalid Input**:
```json
{
    "result": "Error conducting quick research: Invalid input - question cannot be empty",
    "mode": "quick",
    "sources": [],
    "status": "error",
    "timestamp": "2024-01-01T00:00:00Z",
    "metadata": {
        "error_type": "validation_error",
        "execution_time": "1s"
    }
}
```

**Service Unavailable**:
```json
{
    "result": "Error conducting standard research: Service unavailable - LLM service is temporarily down",
    "mode": "standard",
    "sources": [],
    "status": "error",
    "timestamp": "2024-01-01T00:00:00Z",
    "metadata": {
        "error_type": "service_unavailable",
        "execution_time": "5s"
    }
}
```

## Implementation Guidelines

### 1. Response Length Validation
- **Instant**: 50-200 characters
- **Quick**: 200-800 characters
- **Standard**: 800-2000 characters
- **Deep**: 2000+ characters

### 2. Source Generation
- Generate 1-3 mock sources for instant
- Generate 3-5 mock sources for quick
- Generate 5-8 mock sources for standard
- Generate 8-12 mock sources for deep

### 3. Metadata Generation
- Include realistic execution times
- Set appropriate rounds completed
- Include relevant metadata fields

### 4. Error Simulation
- Randomly simulate errors for testing
- Include realistic error messages
- Maintain consistent error format

## Testing Strategy

### 1. Response Quality Testing
- Verify response lengths match mode expectations
- Check that responses contain relevant content
- Ensure sources are generated appropriately

### 2. Error Handling Testing
- Test all error scenarios
- Verify error messages are user-friendly
- Check error response format consistency

### 3. Mode Differentiation Testing
- Compare responses across modes
- Verify clear differences in depth and length
- Test mode selection logic

This mock response system provides a solid foundation for Phase 1 testing while demonstrating the expected behavior differences between research modes.
