# Additional Workshop Tasks for the DeepResearch Agent

Based on the current implementation of a research agent that uses BAML for structured LLM interactions, here are suggested additional tasks for workshop attendees:

## 1. Add a New Tool/Action

**Task**: Extend the agent with a new action type for data analysis.

### Implementation Steps:

- Add a new class `Analyze` in `main.baml`:

```baml
class Analyze {
  action "analyze_data" @description("analyze and summarize data from search results")
  data string
  analysis_type "statistical" | "comparative" | "summary"
}
```

- Update the `Chat` function to return this new action type
- Implement the handler in `agent.py` to process analysis requests

## 2. Change/Experiment with Different Models

**Task**: Modify the LLM models used and compare performance.

### Options to Try:

- **Change the main Chat model**:
  - Current: `openai/gpt-4o-mini-2024-07-18`
  - Try: `openai/gpt-4o`, `anthropic/claude-3-haiku`, `anthropic/claude-3-sonnet`
- **Change the supervisor Thinking model**:

  - Current: `openai/gpt-4.1`
  - Try: `openai/gpt-4-turbo`, `anthropic/claude-3-opus`

- **Add model fallback logic**:
  ```baml
  client "primary" {
    provider "openai"
    model "gpt-4o"
  }
  client "fallback" {
    provider "anthropic"
    model "claude-3-sonnet"
  }
  ```

## 3. Add Memory/Context Management

**Task**: Implement a memory system to remember previous conversations.

### Implementation:

- Add a `Memory` class to store important facts
- Create a function to summarize conversations
- Implement context window management when state gets too large

## 4. Add a New Data Source

**Task**: Integrate another API beyond web search.

### Suggestions:

- **Wikipedia API**: For factual information
- **News API**: For current events
- **Academic API** (like arXiv): For research papers
- **Weather API**: For location-based queries

Example implementation:

```python
def get_wikipedia_summary(topic: str) -> str:
    # Implement Wikipedia API call
    pass

# Add to agent loop:
if isinstance(action, WikiSearch):
    wiki_result = get_wikipedia_summary(action.topic)
    # Process and add to state
```

## 5. Enhance the Supervisor Logic

**Task**: Make the supervisor more intelligent with specific guidelines.

### Improvements:

- Add quality checks for search results
- Implement fact-checking logic
- Add citation requirements
- Create specialized supervisors for different domains

## 6. Create Custom Prompts for Specific Domains

**Task**: Specialize the agent for a specific use case.

### Domain Examples:

- **Travel Planning Agent**: Modify prompts for travel research
- **Academic Research Agent**: Focus on scholarly sources
- **Product Comparison Agent**: Emphasize reviews and specifications
- **Medical Information Agent**: Add disclaimers and focus on reputable sources

## 7. Implement Multi-Agent Collaboration

**Task**: Create multiple specialized agents that work together.

### Architecture:

```python
class ResearchTeam:
    def __init__(self):
        self.searcher = SearchAgent()
        self.analyzer = AnalysisAgent()
        self.writer = WriterAgent()

    def collaborate(self, task):
        # Orchestrate agents
        pass
```
