# Architecture

This document explains the design principles, component relationships, and data flow in Yaduha.

## Overview

Yaduha is built on a modular architecture with four main layers:

```
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│                  (User Scripts & Workflows)                   │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                     Translator Layer                          │
│         (PipelineTranslator, AgenticTranslator)              │
└───────────────┬───────────────────────────┬─────────────────┘
                │                           │
     ┌──────────▼──────────┐     ┌─────────▼──────────┐
     │    Agent Layer      │     │    Tool Layer       │
     │  (OpenAIAgent)      │◄────│  (Search, Dict,     │
     │                     │     │   Translation)      │
     └──────────┬──────────┘     └─────────┬──────────┘
                │                           │
                └───────────┬───────────────┘
                            │
                 ┌──────────▼──────────┐
                 │   Language Layer    │
                 │  (Sentence Types,   │
                 │   Vocabulary)       │
                 └─────────────────────┘
```

## Design Principles

### 1. Type Safety First

Every component uses Python type hints extensively:

- **Generic Types**: Tools and translators are parameterized by sentence types
- **Pydantic Models**: Runtime validation for all data structures
- **Overloaded Methods**: Multiple type signatures for better IDE support

```python
# Generic tool parameterized by sentence type
class EnglishToSentencesTool(Tool, Generic[TSentenceType]):
    def _run(self, text: str) -> AgentResponse[SentenceList[TSentenceType]]:
        ...

# Overloaded agent method for different response types
@overload
def get_response(self, messages: List[...], response_format: Type[str]) -> AgentResponse[str]: ...

@overload
def get_response(self, messages: List[...], response_format: Type[T]) -> AgentResponse[T]: ...
```

### 2. Composability

Components can be mixed and matched:

```python
# Use a translator as a tool inside another translator
agentic_translator = AgenticTranslator(
    agent=agent,
    tools=[
        DictionaryTool(),
        PipelineTranslator(agent=agent, SentenceType=MySentence)
    ]
)
```

### 3. Extensibility

Easy to add new components:

- **New Agents**: Implement `Agent` abstract class
- **New Tools**: Extend `Tool` base class
- **New Translators**: Extend `Translator` base class
- **New Languages**: Define `Sentence` subclasses

### 4. Observability

Every operation tracks metrics:

```python
result = translator("Hello")
print(f"Time: {result.translation_time}s")
print(f"Tokens: {result.prompt_tokens + result.completion_tokens}")
print(f"Confidence: {result.metadata['confidence_level']}")
```

## Core Components

### Agent Layer

**Purpose**: Abstract AI model interaction

**Key Classes**:
- `Agent` - Abstract base class defining interface
- `OpenAIAgent` - OpenAI implementation with tool calling support
- `AgentResponse[T]` - Generic response container with metrics

**Responsibilities**:
- Managing API calls to LLMs
- Handling tool calling loops
- Tracking token usage and response times
- Supporting both text and structured outputs

**Data Flow**:
```
messages → Agent.get_response() → [Tool Calling Loop] → AgentResponse[T]
```

**Tool Calling Loop**:
1. Send messages to LLM with available tools
2. If LLM returns text → return response
3. If LLM calls tool → execute tool, append result to messages, goto 1

### Tool Layer

**Purpose**: Extend agent capabilities with callable functions

**Key Classes**:
- `Tool` - Abstract base class with validation
- `EnglishToSentencesTool[T]` - Parse English into structured sentences
- `SentenceToEnglishTool[T]` - Convert sentences back to English
- Custom tools: `SearchEnglishTool`, `DictionaryTool`, etc.

**Responsibilities**:
- Type validation at class definition time
- OpenAI function schema generation
- Automatic BaseModel parameter parsing
- Example-based few-shot learning support

**Schema Generation**:
```python
class MyTool(Tool):
    name = "my_tool"
    description = "Does something useful"

    def _run(self, query: str, limit: int = 5) -> List[str]:
        ...

# Automatically generates:
{
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "Does something useful",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer"}
            },
            "required": ["query", "limit"]
        }
    }
}
```

### Translator Layer

**Purpose**: High-level translation orchestration

**Key Classes**:
- `Translator` - Abstract base class
- `PipelineTranslator[T]` - Structured translation pipeline
- `AgenticTranslator` - Free-form translation with tools
- `Translation` - Result container with metrics
- `BackTranslation` - Verification details

**Two Translation Approaches**:

#### Pipeline Translator (Structured)
```
English Text
    ↓
[EnglishToSentencesTool]
    ↓
Structured Sentences (Pydantic models)
    ↓
[__str__() method]
    ↓
Target Language Text
    ↓
[SentenceToEnglishTool] (verification)
    ↓
Back-translation
```

**Advantages**:
- Guaranteed grammatical correctness
- Explicit structure mapping
- Type-safe sentence representation
- Easy to debug

**Disadvantages**:
- Limited to defined sentence structures
- Requires comprehensive grammar model
- May not handle idiomatic expressions

#### Agentic Translator (Free-form)
```
English Text
    ↓
[Agent with Tools]
    ↓ ↑ (iterative tool calling)
Tools: Dictionary, Search, Pipeline, etc.
    ↓
Target Language Text + Confidence + Evidence
```

**Advantages**:
- Flexible, can handle any input
- Can use external resources
- Provides confidence scores
- Tracks evidence/reasoning

**Disadvantages**:
- No structural guarantees
- Depends on LLM quality
- Higher token usage

### Language Layer

**Purpose**: Define target language grammar and vocabulary

**Key Classes**:
- `Sentence` - Abstract base class for sentence structures
- `VocabEntry` - English ↔ Target word mappings
- Language-specific implementations (e.g., OVP)

**Responsibilities**:
- Define grammatical structures as Pydantic models
- Implement `__str__()` for target language rendering
- Provide training examples via `get_examples()`
- Store vocabulary mappings

**Example Language Definition**:
```python
class SubjectVerbSentence(Sentence):
    subject: Pronoun | SubjectNoun
    verb: IntransitiveVerb | TransitiveVerb

    def __str__(self) -> str:
        # Render to target language
        return f"{self.subject} {self.verb}"

    @classmethod
    def get_examples(cls) -> List[Tuple[str, "SubjectVerbSentence"]]:
        return [
            ("I sleep", SubjectVerbSentence(subject=..., verb=...)),
            ("You run", SubjectVerbSentence(subject=..., verb=...)),
        ]
```

## Data Flow Examples

### Example 1: Pipeline Translation

```python
translator = PipelineTranslator(
    agent=OpenAIAgent(model="gpt-4o-mini", api_key="..."),
    SentenceType=(SubjectVerbSentence, SubjectVerbObjectSentence)
)

result = translator("The dog sleeps.")
```

**Step-by-step flow**:

1. **Input**: `"The dog sleeps."`

2. **EnglishToSentencesTool called**:
   - Agent receives: `{"text": "The dog sleeps."}`
   - Agent returns: `SentenceList[SubjectVerbSentence]` containing:
     ```python
     SubjectVerbSentence(
         subject=SubjectNoun(head="dog", proximity=Proximity.proximal),
         verb=IntransitiveVerb(lemma="sleep", tense_aspect=TenseAspect.present_simple)
     )
     ```

3. **Sentence rendering**:
   - Call `sentence.__str__()`
   - Returns: `"Ishapugu-uu üwi-dü"`

4. **Back-translation** (verification):
   - SentenceToEnglishTool called with sentence
   - Returns: `"The dog sleeps."`

5. **Result**:
   ```python
   Translation(
       source="The dog sleeps.",
       target="Ishapugu-uu üwi-dü",
       back_translation=BackTranslation(source="The dog sleeps.", ...),
       translation_time=2.34,
       prompt_tokens=1245,
       completion_tokens=89,
       metadata={}
   )
   ```

### Example 2: Agentic Translation with Tools

```python
translator = AgenticTranslator(
    agent=OpenAIAgent(model="gpt-4o-mini", api_key="..."),
    system_prompt="You are an expert Owens Valley Paiute translator...",
    tools=[
        SearchEnglishTool(),
        SearchPaiuteTool(),
        PipelineTranslator(agent=agent, SentenceType=SubjectVerbSentence)
    ]
)

result = translator("I'm going to the store.")
```

**Step-by-step flow**:

1. **Input**: `"I'm going to the store."`

2. **Agent reasoning loop**:

   **Turn 1**: Agent decides to search for "going" in English dictionary
   - Tool call: `search_english(query="going", limit=3)`
   - Result: `[{"paiute_translation": "naau", "english": "go", ...}]`

   **Turn 2**: Agent searches for "store"
   - Tool call: `search_english(query="store", limit=3)`
   - Result: `[{"paiute_translation": "tukuupü", "english": "store", ...}]`

   **Turn 3**: Agent uses pipeline translator for structure
   - Tool call: `agentic_translator(text="I go to the store")`
   - Result: `"Nüü tukuupü-gai naau-dü"`

   **Turn 4**: Agent responds with final translation
   - Returns: `TranslationResponse(translation="...", confidence="high", evidence=[...])`

3. **Result**:
   ```python
   Translation(
       source="I'm going to the store.",
       target="Nüü tukuupü-gai naau-dü",
       translation_time=8.76,
       prompt_tokens=4521,
       completion_tokens=234,
       metadata={
           "confidence_level": "high",
           "evidence": [
               {"tool_name": "search_english", "tool_input": "going", ...},
               {"tool_name": "search_english", "tool_input": "store", ...},
               {"tool_name": "agentic_translator", "tool_input": "...", ...}
           ]
       }
   )
   ```

## Type System Architecture

### Generic Type Parameters

Yaduha uses Python generics extensively for type safety:

```python
# TypeVar bound to Sentence
TSentenceType = TypeVar("TSentenceType", bound=Sentence)

# Tools parameterized by sentence type
class EnglishToSentencesTool(Tool, Generic[TSentenceType]):
    def _run(self, text: str) -> AgentResponse[SentenceList[TSentenceType]]:
        ...

# Translators parameterized by sentence type
class PipelineTranslator(Translator, Generic[TSentenceType]):
    def _run(self, text: str) -> Translation:
        ...
```

**Benefits**:
- IDE autocomplete and type checking
- Catch errors at development time
- Self-documenting code
- Easier refactoring

### Runtime Type Validation

Tools validate parameter types at class definition time:

```python
class MyTool(Tool):
    def _run(self, query: str, limit: int) -> List[str]:
        ...

# Validation happens when class is defined:
# ✓ All parameters have type hints
# ✓ Return type is annotated
# ✓ Types are supported (str, int, List, etc.)
```

Supported types:
- Primitives: `str`, `int`, `float`, `bool`
- Collections: `List[T]`, `Dict[K, V]`, `Tuple[...]`
- Union types: `Union[A, B]`, `A | B`
- Pydantic models: `BaseModel` subclasses
- Generics: `TypeVar` with bounds

### Overloaded Methods

Agents use `@overload` for precise type inference:

```python
@overload
def get_response(
    self,
    messages: List[...],
    response_format: Type[str]
) -> AgentResponse[str]: ...

@overload
def get_response(
    self,
    messages: List[...],
    response_format: Type[T]
) -> AgentResponse[T]: ...

# Implementation
def get_response(
    self,
    messages: List[...],
    response_format: Type[T] = str
) -> AgentResponse[T]:
    ...
```

**Result**: Callers get correct type inference:
```python
# Type checker knows this is AgentResponse[str]
response1 = agent.get_response(messages, response_format=str)

# Type checker knows this is AgentResponse[MyModel]
response2 = agent.get_response(messages, response_format=MyModel)
```

## Error Handling

### Validation Errors

Tools validate at class definition time:

```python
# This raises ValueError immediately
class BadTool(Tool):
    name = "bad"
    description = "Bad tool"

    def _run(self, param):  # Missing type hint!
        return param
```

### API Errors

Agent calls can raise `OpenAIError`:

```python
from openai import OpenAIError

try:
    response = agent.get_response(messages)
except OpenAIError as e:
    logger.error(f"API call failed: {e}")
    # Handle rate limits, authentication, etc.
```

### Tool Execution Errors

Tool errors are passed back to the agent:

```python
class SearchTool(Tool):
    def _run(self, query: str) -> List[str]:
        response = requests.get(f"https://api.example.com/search?q={query}")
        response.raise_for_status()  # May raise RequestException
        return response.json()

# Agent receives tool error as message:
# {"role": "tool", "tool_call_id": "...", "content": "Error: 404 Not Found"}
```

## Performance Considerations

### Token Usage

Track and optimize token consumption:

```python
result = translator(text)
total_tokens = (
    result.prompt_tokens +
    result.completion_tokens
)

if result.back_translation:
    total_tokens += (
        result.back_translation.prompt_tokens +
        result.back_translation.completion_tokens
    )

# Log for monitoring
logger.info(f"Translation used {total_tokens} tokens")
```

### Caching

Consider caching for repeated translations:

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def translate_cached(text: str) -> str:
    return translator(text).target
```

### Parallel Tool Calls

Agents automatically support parallel tool calling:

```python
# Agent can call multiple tools simultaneously
# OpenAI API handles parallelization
tools = [
    SearchTool(),
    DictionaryTool(),
    GrammarTool()
]

translator = AgenticTranslator(agent=agent, tools=tools)
# Agent may call all three tools in parallel
```

## Extension Points

### Adding a New Agent

```python
from yaduha.agent import Agent, AgentResponse

class MyCustomAgent(Agent):
    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: Type[T] = str,
        tools: List[Tool] | None = None
    ) -> AgentResponse[T]:
        # Implement your agent logic
        # Call your LLM provider
        # Handle tool calling
        # Return AgentResponse[T]
        ...
```

### Adding a New Tool

```python
from yaduha.tool import Tool

class MyCustomTool(Tool):
    name: ClassVar[str] = "my_tool"
    description: ClassVar[str] = "Description for the LLM"

    def _run(self, param1: str, param2: int = 10) -> Dict:
        # Implement tool logic
        return {"result": "..."}

    def get_examples(self) -> List[Tuple[Dict, Dict]]:
        return [
            ({"param1": "test", "param2": 5}, {"result": "..."})
        ]
```

### Adding a New Translator

```python
from yaduha.translator import Translator, Translation

class MyCustomTranslator(Translator):
    def _run(self, text: str) -> Translation:
        # Implement translation logic
        # Return Translation object with metrics
        return Translation(
            source=text,
            target=translated_text,
            translation_time=elapsed_time,
            prompt_tokens=tokens_used,
            completion_tokens=tokens_generated,
            back_translation=None,
            metadata={}
        )
```

### Adding a New Language

```python
from yaduha.language import Sentence

class MyLanguageSentence(Sentence):
    subject: str
    verb: str
    object: str | None = None

    def __str__(self) -> str:
        # Render to target language
        if self.object:
            return f"{self.subject} {self.object} {self.verb}"
        return f"{self.subject} {self.verb}"

    @classmethod
    def get_examples(cls) -> List[Tuple[str, "MyLanguageSentence"]]:
        return [
            ("I run", MyLanguageSentence(subject="I", verb="run")),
            ("You eat food", MyLanguageSentence(subject="you", verb="eat", object="food"))
        ]
```

## Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
def test_tool_validation():
    class ValidTool(Tool):
        name = "valid"
        description = "Valid tool"
        def _run(self, x: int) -> str:
            return str(x)

    # Should not raise
    tool = ValidTool()

def test_sentence_rendering():
    sentence = MyLanguageSentence(subject="I", verb="run")
    assert str(sentence) == "I run"
```

### Integration Tests

Test components working together:

```python
def test_pipeline_translation():
    agent = OpenAIAgent(model="gpt-4o-mini", api_key="...")
    translator = PipelineTranslator(
        agent=agent,
        SentenceType=MySentence
    )

    result = translator("Hello world")
    assert result.target != ""
    assert result.back_translation is not None
```

### Mock Testing

Mock expensive API calls:

```python
from unittest.mock import Mock

def test_agent_with_mock():
    mock_client = Mock()
    mock_client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Mocked response"))]
    )

    # Test agent logic without real API calls
```

## Best Practices

### 1. Always Use Type Hints

```python
# Good
def process(text: str, limit: int = 10) -> List[str]:
    ...

# Bad
def process(text, limit=10):
    ...
```

### 2. Validate Inputs

```python
def translate(text: str) -> Translation:
    if not text.strip():
        raise ValueError("Text cannot be empty")
    ...
```

### 3. Track Metrics

```python
result = translator(text)
logger.info(f"Translation completed in {result.translation_time:.2f}s")
logger.info(f"Used {result.prompt_tokens + result.completion_tokens} tokens")
```

### 4. Handle Errors Gracefully

```python
from openai import OpenAIError

try:
    result = translator(text)
except OpenAIError as e:
    logger.error(f"Translation failed: {e}")
    return fallback_translation(text)
```

### 5. Provide Examples

```python
class MyTool(Tool):
    def get_examples(self) -> List[Tuple[Dict, Any]]:
        return [
            ({"query": "test"}, ["result1", "result2"]),
            ({"query": "example"}, ["result3"])
        ]
```

## Conclusion

Yaduha's architecture prioritizes:

- **Type Safety**: Catch errors early with comprehensive type hints
- **Composability**: Mix and match components as needed
- **Extensibility**: Easy to add new languages, tools, and agents
- **Observability**: Track metrics for every operation
- **Flexibility**: Choose structured or free-form translation

This design enables building robust, maintainable translation systems for low-resource languages.
