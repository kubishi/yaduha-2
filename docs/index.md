# Yaduha Documentation

Welcome to the Yaduha documentation! Yaduha is a type-safe, AI-powered framework for building structured language translation systems.

## What is Yaduha?

Yaduha combines the flexibility of Large Language Models with the precision of formal linguistic structures. It allows you to:

- Define language grammars as typed Python models
- Build translation pipelines with guaranteed grammatical correctness
- Create AI agents that can use tools for enhanced translation
- Track token usage and performance metrics
- Verify translations through back-translation

## Key Features

### 🔧 Type-Safe Tool Framework
Build LLM-callable tools with automatic parameter validation and schema generation. Tools integrate seamlessly with OpenAI's function calling.

### 🤖 Agent Abstraction
Unified interface for AI agents with support for OpenAI models (gpt-4o, gpt-4o-mini, gpt-5). Easily extensible to other providers.

### 📝 Structured Sentences
Define language grammars as Pydantic models. Yaduha ensures generated sentences follow your defined structures.

### 🔄 Multiple Translation Strategies
- **Pipeline Translator**: Structured, grammatically-guaranteed translation
- **Agentic Translator**: Flexible, tool-augmented free-form translation

### ✅ Back-Translation Verification
Every translation includes automatic back-translation for quality verification.

### 📊 Comprehensive Tracking
Built-in monitoring for:
- Token usage (prompt and completion)
- Execution time
- API costs
- Tool call evidence

## Quick Links

- [Getting Started](getting-started.md) - Installation and first translation
- [Architecture](architecture.md) - Understanding Yaduha's design
- [API Reference](api-reference.md) - Complete API documentation
- [Examples](examples.md) - Practical examples and tutorials
- [Custom Languages](custom-languages.md) - Adding support for new languages
- [Building Tools](building-tools.md) - Creating custom tools

## Supported Languages

Currently, Yaduha includes a complete implementation for **Owens Valley Paiute** (OVP), a Uto-Aztecan language spoken in California.

### Owens Valley Paiute Features

- 37 nouns (coyote, dog, water, mountain, etc.)
- 35 verbs (14 transitive, 21 intransitive)
- Full pronoun system with person, number, proximity, and inclusivity
- 6 tense/aspect combinations
- Complex morphological rules (fortis/lenis mutation, proximity suffixes)

Additional languages can be added by implementing the `Sentence` interface.

## Use Cases

Yaduha is designed for:

- **Linguistic Research**: Study language structure and translation patterns
- **Language Preservation**: Document and digitize endangered languages
- **Educational Tools**: Build language learning applications
- **Translation Systems**: Create domain-specific translators with quality guarantees
- **AI Research**: Experiment with structured vs. free-form LLM outputs

## Getting Help

- Check the [Examples](examples.md) for common use cases
- Read the [API Reference](api-reference.md) for detailed documentation
- Review the [Architecture](architecture.md) to understand the design

## Next Steps

1. [Install Yaduha](getting-started.md#installation)
2. [Run your first translation](getting-started.md#basic-usage)
3. [Explore the examples](examples.md)
4. [Build a custom tool](building-tools.md)
