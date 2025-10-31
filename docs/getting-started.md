# Getting Started

This guide will help you get up and running with Yaduha in just a few minutes.

## Prerequisites

- Python 3.12 or higher
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Basic understanding of Python and type hints

## Installation

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/[your-username]/yaduha.git
cd yaduha
pip install -e .
```

### Dependencies

Yaduha requires:
- `openai` - OpenAI API client
- `pydantic` - Data validation and serialization
- `python-dotenv` - Environment variable management

These will be installed automatically.

## Configuration

### Set Up Your API Key

Create a `.env` file in your project root:

```bash
OPENAI_API_KEY=sk-...your-key-here...
```

Or export it in your shell:

```bash
export OPENAI_API_KEY="sk-...your-key-here..."
```

## Your First Translation

### Basic Example

Create a file `my_first_translation.py`:

```python
from yaduha.translator.pipeline import PipelineTranslator
from yaduha.agent.openai import OpenAIAgent
from yaduha.language.ovp import SubjectVerbSentence, SubjectVerbObjectSentence
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create an AI agent
agent = OpenAIAgent(
    model="gpt-4o-mini",
    api_key=os.environ["OPENAI_API_KEY"],
    temperature=0.0  # For deterministic outputs
)

# Create a translator
translator = PipelineTranslator(
    agent=agent,
    SentenceType=(SubjectVerbObjectSentence, SubjectVerbSentence)
)

# Translate!
result = translator("The dog is sleeping.")

print(f"English: {result.source}")
print(f"Paiute: {result.target}")
print(f"Back-translation: {result.back_translation.source}")
print(f"Time: {result.translation_time:.2f}s")
print(f"Tokens: {result.prompt_tokens + result.completion_tokens}")
```

Run it:

```bash
python my_first_translation.py
```

### Expected Output

```
English: The dog is sleeping.
Paiute: Ishapugu-uu üwi-dü
Back-translation: The dog sleeps.
Time: 2.34s
Tokens: 1245
```

## Understanding the Code

Let's break down what's happening:

### 1. Agent Creation

```python
agent = OpenAIAgent(
    model="gpt-4o-mini",  # Model to use
    api_key=os.environ["OPENAI_API_KEY"],
    temperature=0.0  # 0.0 = deterministic, 1.0 = creative
)
```

The agent is responsible for calling the OpenAI API and managing tool calls.

### 2. Translator Creation

```python
translator = PipelineTranslator(
    agent=agent,
    SentenceType=(SubjectVerbObjectSentence, SubjectVerbSentence)
)
```

`PipelineTranslator` uses a structured approach:
1. Parse English into structured sentences
2. Convert each sentence to target language
3. Back-translate for verification

`SentenceType` can be:
- A single sentence class: `SubjectVerbSentence`
- A tuple of classes: `(SubjectVerbObjectSentence, SubjectVerbSentence)`
  - The LLM will choose the appropriate structure for each sentence

### 3. Translation

```python
result = translator("The dog is sleeping.")
```

Returns a `Translation` object with:
- `source`: Original English text
- `target`: Translated text
- `back_translation`: Verification translation
- `translation_time`: How long it took
- `prompt_tokens`, `completion_tokens`: API usage
- `metadata`: Additional information

## Next Steps

### Try Different Sentences

```python
# Simple intransitive sentence
result = translator("I sleep.")
print(result.target)  # nüü üwi-dü

# Transitive sentence with object
result = translator("You read the mountains.")
print(result.target)  # üü toyabi-noka ui-nia-dü

# Complex multi-clause
result = translator("The coyote runs and the dog sleeps.")
print(result.target)  # Multiple sentences joined
```

### Explore Agentic Translation

For more flexible translation with tool support:

```python
from yaduha.translator.agentic import AgenticTranslator

translator = AgenticTranslator(
    agent=agent,
    system_prompt=(
        "You are an expert translator for Owens Valley Paiute. "
        "Translate accurately while preserving meaning."
    )
)

result = translator("How are you?")
print(result.target)
print(f"Confidence: {result.metadata['confidence_level']}")
```

### Check Token Usage

Monitor your API costs:

```python
result = translator("Your sentence here")

# Approximate cost for gpt-4o-mini
# Input: $0.150 per 1M tokens
# Output: $0.600 per 1M tokens
input_cost = (result.prompt_tokens / 1_000_000) * 0.15
output_cost = (result.completion_tokens / 1_000_000) * 0.60
total_cost = input_cost + output_cost

print(f"Estimated cost: ${total_cost:.6f}")
```

## Common Issues

### API Key Not Found

**Error**: `OpenAIError: The api_key client option must be set`

**Solution**: Ensure your `.env` file exists and `load_dotenv()` is called, or export the variable:
```bash
export OPENAI_API_KEY="sk-..."
```

### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'yaduha'`

**Solution**: Install the package:
```bash
pip install -e .
```

### Rate Limit Errors

**Error**: `RateLimitError: Rate limit exceeded`

**Solution**:
- Add delays between calls
- Upgrade your OpenAI plan
- Use a lower-tier model (gpt-4o-mini instead of gpt-4o)

## What's Next?

- [Explore Examples](examples.md) - More complex use cases
- [Build Custom Tools](building-tools.md) - Extend translator capabilities
- [Add a Language](custom-languages.md) - Support new languages
- [Understand Architecture](architecture.md) - Learn how it works

## Example Scripts

Yaduha includes example scripts in the `scripts/` directory:

```bash
# Basic pipeline translation
python scripts/test_pipeline_translator.py

# Agentic translation with external tools
python scripts/test_agentic_translator.py

# Raw agent functionality
python scripts/test_agent.py
```

Feel free to modify these as starting points for your own projects!
