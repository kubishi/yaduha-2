# API Reference

Complete reference for all Yaduha classes, methods, and functions.

## Table of Contents

- [Agent Module](#agent-module)
- [Tool Module](#tool-module)
- [Translator Module](#translator-module)
- [Language Module](#language-module)

---

## Agent Module

### `Agent` (Abstract Base Class)

Base class for all AI agents.

```python
from yaduha.agent import Agent, AgentResponse
```

#### Methods

##### `get_response()`

Generate a response from the agent.

**Overload 1: Text Response**
```python
def get_response(
    messages: List[ChatCompletionMessageParam],
    response_format: Type[str] = str,
    tools: List[Tool] | None = None
) -> AgentResponse[str]
```

**Overload 2: Structured Response**
```python
def get_response(
    messages: List[ChatCompletionMessageParam],
    response_format: Type[TAgentResponseContentType],
    tools: List[Tool] | None = None
) -> AgentResponse[TAgentResponseContentType]
```

**Parameters:**
- `messages`: List of conversation messages in OpenAI format
- `response_format`: Expected response type (`str` or Pydantic BaseModel class)
- `tools`: Optional list of tools the agent can call

**Returns:** `AgentResponse[T]` containing the response and metadata

**Example:**
```python
# Text response
response = agent.get_response(
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.content)  # str

# Structured response
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

response = agent.get_response(
    messages=[{"role": "user", "content": "Tell me about Alice"}],
    response_format=Person
)
print(response.content.name)  # "Alice"
```

---

### `OpenAIAgent`

OpenAI implementation of the Agent interface.

```python
from yaduha.agent.openai import OpenAIAgent
```

#### Constructor

```python
OpenAIAgent(
    model: Literal["gpt-4o", "gpt-4o-mini", "gpt-5"],
    api_key: str,
    temperature: float = 0.0
)
```

**Parameters:**
- `model`: OpenAI model to use
- `api_key`: Your OpenAI API key
- `temperature`: Sampling temperature (0.0 = deterministic, 1.0 = creative)

**Example:**
```python
agent = OpenAIAgent(
    model="gpt-4o-mini",
    api_key=os.environ["OPENAI_API_KEY"],
    temperature=0.0
)
```

---

### `AgentResponse[T]`

Response from an agent, parameterized by content type.

```python
from yaduha.agent import AgentResponse
```

#### Attributes

- `content: T` - The actual response (str or BaseModel instance)
- `response_time: float` - Execution time in seconds
- `prompt_tokens: int` - Number of tokens in the prompt
- `completion_tokens: int` - Number of tokens in the completion

**Example:**
```python
response = agent.get_response(...)
print(f"Response: {response.content}")
print(f"Time: {response.response_time}s")
print(f"Cost: ${(response.prompt_tokens * 0.15 + response.completion_tokens * 0.60) / 1_000_000}")
```

---

## Tool Module

### `Tool` (Abstract Base Class)

Base class for creating LLM-callable tools.

```python
from yaduha.tool import Tool
```

#### Class Attributes

- `name: ClassVar[str]` - Tool name (must be valid Python identifier)
- `description: ClassVar[str]` - Tool description for the LLM

#### Methods

##### `_run()` (Abstract)

Implement the tool's functionality.

```python
@abstractmethod
def _run(self, *args, **kwargs) -> Any:
    pass
```

**Type Requirements:**
- All parameters must have type annotations
- Supported types: `str`, `int`, `float`, `bool`, `BaseModel`, `List`, `Dict`, `Union`, `TypeVar`
- Return type must be annotated
- No parameters with defaults are allowed to be omitted from calls

**Example:**
```python
class SearchTool(Tool):
    name: ClassVar[str] = "search"
    description: ClassVar[str] = "Search for information"

    def _run(self, query: str, limit: int = 5) -> List[Dict]:
        # Implementation
        return [{"title": "Result 1", "url": "..."}]
```

##### `get_examples()`

Provide example inputs/outputs for few-shot learning.

```python
def get_examples(self) -> List[Tuple[Any, Any]]:
    return []
```

**Returns:** List of `(input, output)` tuples

**Example:**
```python
class MyTool(Tool):
    def _run(self, query: str) -> str:
        return query.upper()

    def get_examples(self) -> List[Tuple[Dict[str, str], str]]:
        return [
            ({"query": "hello"}, "HELLO"),
            ({"query": "world"}, "WORLD")
        ]
```

##### `get_tool_call_schema()`

Generate OpenAI function calling schema (automatically called).

```python
def get_tool_call_schema(self) -> ChatCompletionToolParam:
    ...
```

##### `__call__()`

Call the tool (supports automatic BaseModel parsing).

```python
result = tool(query="test", limit=10)
```

---

### `EnglishToSentencesTool[TSentenceType]`

Convert English text to structured sentences.

```python
from yaduha.tool.english_to_sentences import EnglishToSentencesTool
```

#### Constructor

```python
EnglishToSentencesTool(
    agent: Agent,
    SentenceType: Type[TSentenceType] | Tuple[Type[Sentence], ...]
)
```

**Parameters:**
- `agent`: AI agent to use for parsing
- `SentenceType`: Single sentence class or tuple of classes

**Example:**
```python
tool = EnglishToSentencesTool(
    agent=agent,
    SentenceType=(SubjectVerbSentence, SubjectVerbObjectSentence)
)

response = tool("The dog runs.")
sentences = response.content.sentences  # List[SubjectVerbSentence | SubjectVerbObjectSentence]
```

---

### `SentenceToEnglishTool[TSentenceType]`

Convert structured sentences back to English.

```python
from yaduha.tool.sentence_to_english import SentenceToEnglishTool
```

#### Constructor

```python
SentenceToEnglishTool(
    agent: Agent,
    SentenceType: Type[TSentenceType] | Tuple[Type[Sentence], ...]
)
```

**Example:**
```python
tool = SentenceToEnglishTool(agent=agent, SentenceType=SubjectVerbSentence)
response = tool(my_sentence)
english = response.content  # str
```

---

## Translator Module

### `Translation`

Result of a translation operation.

```python
from yaduha.translator import Translation
```

#### Attributes

- `source: str` - Original English text
- `target: str` - Translated text
- `translation_time: float` - Execution time in seconds
- `prompt_tokens: int` - Tokens used in forward translation
- `completion_tokens: int` - Tokens generated in forward translation
- `back_translation: BackTranslation | None` - Verification back-translation
- `metadata: dict` - Additional information (confidence, evidence, etc.)

---

### `BackTranslation`

Back-translation verification details.

```python
from yaduha.translator import BackTranslation
```

#### Attributes

- `source: str` - Text translated back to English
- `target: str` - Original target language text
- `translation_time: float` - Back-translation execution time
- `prompt_tokens: int` - Tokens used in back-translation
- `completion_tokens: int` - Tokens generated in back-translation

---

### `Translator` (Abstract Base Class)

Base class for all translators.

```python
from yaduha.translator import Translator
```

#### Methods

##### `_run()`

Perform translation (abstract method).

```python
@abstractmethod
def _run(self, text: str) -> Translation:
    pass
```

##### `__call__()`

Translate text (calls `_run` internally).

```python
result = translator("Text to translate")
```

---

### `PipelineTranslator[TSentenceType]`

Structured translation using sentence pipelines.

```python
from yaduha.translator.pipeline import PipelineTranslator
```

#### Constructor

```python
PipelineTranslator(
    agent: Agent,
    SentenceType: Type[TSentenceType] | Tuple[Type[Sentence], ...]
)
```

**Parameters:**
- `agent`: AI agent to use
- `SentenceType`: Sentence structure(s) to use for translation

**Pipeline:**
1. English → Structured Sentences (via `EnglishToSentencesTool`)
2. Each Sentence → `__str__()` → Target Language
3. Each Sentence → English (via `SentenceToEnglishTool` for verification)

**Example:**
```python
translator = PipelineTranslator(
    agent=OpenAIAgent(model="gpt-4o-mini", api_key="..."),
    SentenceType=(SubjectVerbObjectSentence, SubjectVerbSentence)
)

result = translator("The dog sleeps.")
print(result.target)  # "Ishapugu-uu üwi-dü"
```

---

### `AgenticTranslator`

Free-form translation with tool support.

```python
from yaduha.translator.agentic import AgenticTranslator
```

#### Constructor

```python
AgenticTranslator(
    agent: Agent,
    system_prompt: str = "...",
    tools: List[Tool] | None = None
)
```

**Parameters:**
- `agent`: AI agent to use
- `system_prompt`: Instructions for the agent
- `tools`: Optional tools the agent can use

**Output Format:**
Uses structured output with:
- `translation`: The translated text
- `confidence`: "high" | "medium" | "low"
- `evidence`: List of tool calls used

**Example:**
```python
translator = AgenticTranslator(
    agent=agent,
    system_prompt="Translate to Owens Valley Paiute accurately.",
    tools=[DictionaryTool(), PipelineTranslator(...)]
)

result = translator("Hello, how are you?")
print(result.target)
print(result.metadata["confidence_level"])  # "high"
print(result.metadata["evidence"])  # [{"tool_name": "...", ...}]
```

---

## Language Module

### `Sentence` (Abstract Base Class)

Base class for defining language sentence structures.

```python
from yaduha.language import Sentence
```

#### Methods

##### `__str__()` (Abstract)

Convert sentence to target language representation.

```python
@abstractmethod
def __str__(self) -> str:
    pass
```

##### `get_examples()` (Class Method, Abstract)

Provide training examples.

```python
@classmethod
@abstractmethod
def get_examples(cls) -> List[Tuple[str, "Sentence"]]:
    pass
```

**Returns:** List of `(english, sentence)` tuples

**Example:**
```python
class MyLanguageSentence(Sentence):
    subject: str
    verb: str

    def __str__(self) -> str:
        return f"{self.subject}-{self.verb}"

    @classmethod
    def get_examples(cls):
        return [
            ("I sleep", MyLanguageSentence(subject="I", verb="sleep")),
            ("You run", MyLanguageSentence(subject="you", verb="run"))
        ]
```

---

### `VocabEntry`

Vocabulary mapping between English and target language.

```python
from yaduha.language import VocabEntry
```

#### Attributes

- `english: str` - English word
- `target: str` - Target language word

**Example:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class VocabEntry:
    english: str
    target: str

NOUNS = [
    VocabEntry("dog", "ishapugu"),
    VocabEntry("cat", "tüsü"),
    # ...
]
```

---

### Owens Valley Paiute (OVP)

#### `SubjectVerbSentence`

Subject-verb sentence structure.

```python
from yaduha.language.ovp import SubjectVerbSentence
```

**Attributes:**
- `subject: Union[SubjectNoun, Pronoun]`
- `verb: TransitiveVerb | IntransitiveVerb`

**Output Format:** `[subject]-[subject_suffix] [verb]-[tense_suffix]`

**Example:**
```python
sentence = SubjectVerbSentence(
    subject=Pronoun(
        person=Person.first,
        plurality=Plurality.singular,
        proximity=Proximity.proximal,
        inclusivity=Inclusivity.exclusive,
        reflexive=False
    ),
    verb=IntransitiveVerb(lemma="sleep", tense_aspect=TenseAspect.present_simple)
)
print(str(sentence))  # "nüü üwi-dü"
```

#### `SubjectVerbObjectSentence`

Subject-verb-object sentence structure.

```python
from yaduha.language.ovp import SubjectVerbObjectSentence
```

**Attributes:**
- `subject: Union[SubjectNoun, Pronoun]`
- `verb: TransitiveVerb`
- `object: Union[ObjectNoun, Pronoun]`

**Output Format:** `[subject] [object] [object_pronoun]-[verb]-[tense_suffix]`

**Example:**
```python
sentence = SubjectVerbObjectSentence(
    subject=Pronoun(...),
    verb=TransitiveVerb(lemma="read", tense_aspect=TenseAspect.present_simple),
    object=ObjectNoun(head="mountain", proximity=Proximity.distal, plurality=Plurality.plural)
)
print(str(sentence))  # "üü toyabi-noka ui-nia-dü"
```

---

## Type Hints & Generics

Yaduha makes extensive use of Python's type system for safety and IDE support.

### Generic Classes

```python
# Agent response parameterized by content type
AgentResponse[str]  # Text response
AgentResponse[Person]  # Structured response

# Tools parameterized by sentence type
EnglishToSentencesTool[SubjectVerbSentence]
PipelineTranslator[SubjectVerbObjectSentence]
```

### TypeVars

```python
from typing import TypeVar
from yaduha.language import Sentence

TSentenceType = TypeVar("TSentenceType", bound=Sentence)
```

Used to create generic tools and translators that work with any sentence type.

---

## Error Handling

### Common Exceptions

**`ValueError`** - Invalid tool parameters or validation failure
```python
try:
    tool = Tool()  # Invalid: name not set
except ValueError as e:
    print(e)  # "Tool name must be set"
```

**`OpenAIError`** - API-related errors
```python
from openai import OpenAIError

try:
    response = agent.get_response(...)
except OpenAIError as e:
    print(f"API Error: {e}")
```

**`TypeError`** - Type validation errors
```python
# Tool parameter type mismatch
tool._run(query=123)  # TypeError: expected str, got int
```

---

## Best Practices

### 1. Use Type Hints

Always annotate tool parameters and return types:

```python
# Good
def _run(self, query: str, limit: int = 5) -> List[Dict]:
    ...

# Bad
def _run(self, query, limit=5):
    ...
```

### 2. Provide Examples

Implement `get_examples()` for better LLM performance:

```python
def get_examples(self):
    return [
        ({"query": "test"}, ["result1", "result2"]),
        ({"query": "example"}, ["result3"])
    ]
```

### 3. Track Token Usage

Monitor costs in production:

```python
result = translator(text)
total_tokens = result.prompt_tokens + result.completion_tokens

if result.back_translation:
    total_tokens += (result.back_translation.prompt_tokens +
                     result.back_translation.completion_tokens)

# Log or store for monitoring
print(f"Translation used {total_tokens} tokens")
```

### 4. Handle Errors Gracefully

```python
from openai import OpenAIError

try:
    result = translator(text)
except OpenAIError as e:
    logger.error(f"Translation failed: {e}")
    # Fallback logic
except ValueError as e:
    logger.error(f"Validation error: {e}")
    # Handle validation issues
```
