# Creating New Languages for Yaduha with AI Assistance

This guide shows you how to use AI (like Claude) to generate completely new constructed languages that integrate seamlessly with the Yaduha framework.

## Overview

You can prompt an AI to create an entire language implementation by understanding:
1. The architecture pattern used in existing languages
2. Key implementation requirements (especially `json_schema_extra`)
3. How to design unique grammatical features
4. The file structure and dependencies

## Quick Start: The Prompt Template

Here's a template prompt you can copy and customize:

```
I need you to create a new constructed language for the Yaduha translation framework.

REQUIREMENTS:
1. The language must be completely different from the existing languages (OVP, Velar, Kethara)
2. It should have unique grammatical features not present in the other languages
3. It must follow the Yaduha architecture pattern

EXISTING LANGUAGES (avoid duplicating these features):
- OVP: SOV word order, proximity distinction (this/that), inclusivity (we including/excluding you), dual number, fortis/lenis consonant mutation
- Velar: VSO word order, gendered pronouns (M/F/N), evidentiality (direct/hearsay/inference), animacy-based articles, formality levels
- Kethara: SOV word order, noun classes (human/animal/plant/object/abstract), vowel harmony, agglutinative morphology, directional case system

DESIGN A LANGUAGE WITH:
- [Specify unique feature 1, e.g., "tonal system with 4 tones"]
- [Specify unique feature 2, e.g., "classifier system like Chinese"]
- [Specify unique feature 3, e.g., "switch-reference marking"]
- [Word order: SVO/SOV/VSO/VOS/OVS/OSV]
- [Specify 30-50 nouns with a unique naming convention]
- [Specify 30-40 verbs]

CRITICAL IMPLEMENTATION REQUIREMENTS:
1. All Noun classes MUST use Field() with json_schema_extra={'enum': [list of English lemmas], 'description': '...'}
2. All Verb classes MUST use Field() with json_schema_extra={'enum': [list of English lemmas], 'description': '...'}
3. The 'head' field in Noun and 'lemma' field in Verb must be ENGLISH words from vocabulary
4. Implement both SubjectNoun/ObjectNoun and TransitiveVerb/IntransitiveVerb classes
5. Create at least 2 sentence types with get_examples() methods
6. Include field_validator decorators for validation

CREATE THE FOLLOWING FILES:
1. yaduha/language/[languagename]/vocab.py - vocabulary entries
2. yaduha/language/[languagename]/__init__.py - grammar implementation
3. yaduha/language/[languagename]/prompts.py - prompt generation
4. scripts/test_[languagename]_translator.py - test script

Look at the existing implementations in yaduha/language/velar/ and yaduha/language/kethara/ for the exact patterns to follow.
```

## Step-by-Step Process

### Step 1: Study Existing Implementations

Before creating a new language, examine these files:

**For architecture understanding:**
- [yaduha/language/velar/__init__.py](../yaduha/language/velar/__init__.py) - Clean, well-documented example
- [yaduha/language/kethara/__init__.py](../yaduha/language/kethara/__init__.py) - Shows agglutinative features

**For vocabulary structure:**
- [yaduha/language/velar/vocab.py](../yaduha/language/velar/vocab.py)
- [yaduha/language/kethara/vocab.py](../yaduha/language/kethara/vocab.py)

**For prompts:**
- [yaduha/language/velar/prompts.py](../yaduha/language/velar/prompts.py)
- [yaduha/language/kethara/prompts.py](../yaduha/language/kethara/prompts.py)

### Step 2: Design Unique Features

Choose grammatical features that differentiate your language. Consider:

**Typological Features:**
- Word order: SVO, SOV, VSO, VOS, OVS, OSV, free
- Head direction: head-initial vs head-final
- Morphological type: isolating, agglutinative, fusional, polysynthetic

**Grammatical Categories:**
- Tense/aspect/mood systems
- Case systems (nominative-accusative, ergative-absolutive, tripartite)
- Number (singular/plural/dual/trial/paucal)
- Gender/noun class systems
- Evidentiality (information source)
- Mirativity (surprise/new information)
- Animacy hierarchies

**Unique Features to Consider:**
- Tonal distinctions (like Chinese, Vietnamese)
- Classifiers/measure words (like Japanese, Chinese)
- Switch-reference (tracking subject changes)
- Obviation (distinguishing 3rd person participants)
- Clusivity (inclusive/exclusive "we")
- Politeness/honorific systems
- Directional/orientational systems
- Noun incorporation
- Serial verb constructions

**Features Already Used (avoid these combinations):**

| Feature | OVP | Velar | Kethara |
|---------|-----|-------|---------|
| Word Order | SOV | VSO | SOV |
| Proximity | ✓ | ✗ | ✗ |
| Gender | ✗ | ✓ | ✗ |
| Evidentiality | ✗ | ✓ | ✗ |
| Noun Classes | ✗ | ✗ | ✓ |
| Vowel Harmony | ✗ | ✗ | ✓ |
| Agglutination | ✗ | ✗ | ✓ |
| Inclusivity | ✓ | ✗ | ✗ |
| Dual Number | ✓ | ✗ | ✗ |
| Consonant Mutation | ✓ | ✗ | ✗ |
| Formality Levels | ✗ | ✓ | ✓ |

### Step 3: Create Vocabulary (vocab.py)

```python
"""
[Language Name] Vocabulary

Description of language features.
"""

from yaduha.language import VocabEntry

# Organize nouns by semantic category
CATEGORY1_NOUNS = [
    VocabEntry("person", "word1"),
    VocabEntry("dog", "word2"),
    # ... 10-15 per category
]

CATEGORY2_NOUNS = [
    # ...
]

# All nouns combined
NOUNS = CATEGORY1_NOUNS + CATEGORY2_NOUNS

# Transitive verbs
TRANSITIVE_VERBS = [
    VocabEntry("see", "verbword1"),
    VocabEntry("eat", "verbword2"),
    # ... 15-20 verbs
]

# Intransitive verbs
INTRANSITIVE_VERBS = [
    VocabEntry("sleep", "verbword3"),
    VocabEntry("run", "verbword4"),
    # ... 15-20 verbs
]
```

**Important:**
- Use consistent phonological rules for your vocabulary
- Consider phonotactic constraints (what sounds can appear where)
- Create distinctive, memorable words
- Avoid words from existing languages unless intentional

### Step 4: Create Grammar Implementation (__init__.py)

This is the core file. **CRITICAL: Follow this structure exactly:**

```python
"""
[Language Name] Grammar Implementation

Key Features:
1. [Feature 1]
2. [Feature 2]
...
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Type, Union
from pydantic import BaseModel, Field, field_validator
import random

from yaduha.language import Sentence
from yaduha.language.[languagename].vocab import (
    NOUNS,
    TRANSITIVE_VERBS,
    INTRANSITIVE_VERBS,
)

# ============================================================================
# LOOKUP DICTIONARIES
# ============================================================================

NOUN_LOOKUP: Dict[str, str] = {
    entry.english: entry.target for entry in NOUNS
}

TRANSITIVE_VERB_LOOKUP: Dict[str, str] = {
    entry.english: entry.target for entry in TRANSITIVE_VERBS
}

INTRANSITIVE_VERB_LOOKUP: Dict[str, str] = {
    entry.english: entry.target for entry in INTRANSITIVE_VERBS
}

def get_noun_target(lemma: str) -> str:
    return NOUN_LOOKUP[lemma]

def get_verb_target(lemma: str) -> str:
    if lemma in TRANSITIVE_VERB_LOOKUP:
        return TRANSITIVE_VERB_LOOKUP[lemma]
    return INTRANSITIVE_VERB_LOOKUP[lemma]

# ============================================================================
# GRAMMATICAL FEATURES (Enums)
# ============================================================================

class YourFeature(str, Enum):
    """Description"""
    value1 = "value1"
    value2 = "value2"

# Define all your grammatical features as Enums...

# ============================================================================
# PRONOUN SYSTEM
# ============================================================================

class Pronoun(BaseModel):
    """Your pronoun system"""
    person: Person
    number: Number
    # ... other features

    def __str__(self) -> str:
        """Render pronoun in target language"""
        # Implementation
        pass

# ============================================================================
# NOUN CLASSES
# ============================================================================

class Noun(BaseModel):
    """Base noun class"""
    head: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in NOUNS],
            'description': 'An English noun lemma from the [Language] vocabulary'
        }
    )
    # ... other fields (number, case, etc.)

    @field_validator("head")
    @classmethod
    def validate_head(cls, v: str) -> str:
        if v not in NOUN_LOOKUP:
            raise ValueError(f"Unknown noun: {v}")
        return v

    def __str__(self) -> str:
        """Render noun in target language"""
        # Implementation
        pass

class SubjectNoun(Noun):
    """Noun used as subject"""
    pass

class ObjectNoun(Noun):
    """Noun used as object"""
    pass

# ============================================================================
# VERB CLASSES
# ============================================================================

class Verb(BaseModel):
    """Base verb class"""
    lemma: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in TRANSITIVE_VERBS + INTRANSITIVE_VERBS],
            'description': 'An English verb lemma from the [Language] vocabulary'
        }
    )
    # ... tense, aspect, mood, etc.

    @field_validator("lemma")
    @classmethod
    def validate_lemma(cls, v: str) -> str:
        if v not in TRANSITIVE_VERB_LOOKUP and v not in INTRANSITIVE_VERB_LOOKUP:
            raise ValueError(f"Unknown verb: {v}")
        return v

    def get_conjugated_form(self) -> str:
        """Get fully conjugated verb form"""
        # Implementation
        pass

class TransitiveVerb(Verb):
    """Verb that requires an object"""
    lemma: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in TRANSITIVE_VERBS],
            'description': 'An English transitive verb lemma'
        }
    )

    @field_validator("lemma")
    @classmethod
    def validate_lemma(cls, v: str) -> str:
        if v not in TRANSITIVE_VERB_LOOKUP:
            raise ValueError(f"Not a transitive verb: {v}")
        return v

class IntransitiveVerb(Verb):
    """Verb that does not take an object"""
    lemma: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in INTRANSITIVE_VERBS],
            'description': 'An English intransitive verb lemma'
        }
    )

    @field_validator("lemma")
    @classmethod
    def validate_lemma(cls, v: str) -> str:
        if v not in INTRANSITIVE_VERB_LOOKUP:
            raise ValueError(f"Not an intransitive verb: {v}")
        return v

# ============================================================================
# SENTENCE STRUCTURES
# ============================================================================

class YourSentenceType1(Sentence["YourSentenceType1"]):
    """
    Description of sentence type.

    Word order: [your order]

    Example:
        English: "..."
        [Language]: "..."
    """
    subject: Union[SubjectNoun, Pronoun]
    verb: IntransitiveVerb
    # ... other components

    def __str__(self) -> str:
        """Render sentence in target language"""
        # Implement word order and rendering
        pass

    @classmethod
    def get_examples(cls) -> List[Tuple[str, "YourSentenceType1"]]:
        """Provide example sentences for few-shot learning"""
        return [
            (
                "English sentence 1",
                YourSentenceType1(
                    # Fully specified example
                ),
            ),
            # At least 2-3 examples
        ]

# Implement at least 2 sentence types...

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # List all public classes and functions
]
```

### Step 5: CRITICAL - The json_schema_extra Requirement

**This is the most important technical detail:**

The LLM (GPT-4, etc.) needs to know what English lemmas are valid. You MUST include `json_schema_extra` with an `enum` field in EVERY noun and verb class.

**Why this matters:**
- The LLM receives the Pydantic schema as JSON Schema
- The `enum` field tells the LLM: "these are the ONLY valid values"
- Without it, the LLM will guess or use target language words, causing validation errors

**Example of WRONG implementation:**
```python
class Noun(BaseModel):
    head: str  # ❌ NO! LLM doesn't know valid values
```

**Example of CORRECT implementation:**
```python
class Noun(BaseModel):
    head: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in NOUNS],  # ✓ YES!
            'description': 'An English noun lemma from the vocabulary'
        }
    )
```

**You need this on:**
1. `Noun.head` field
2. `Verb.lemma` field
3. `TransitiveVerb.lemma` field (override with only transitive verbs)
4. `IntransitiveVerb.lemma` field (override with only intransitive verbs)

### Step 6: Create Prompts (prompts.py)

```python
"""
Prompt generation for [Language] translation.
"""

from typing import Iterable, Type
from yaduha.language import Sentence
from yaduha.language.[languagename].vocab import (
    NOUNS,
    TRANSITIVE_VERBS,
    INTRANSITIVE_VERBS,
)

SYSTEM_PROMPT_PREFIX = """You are a translator that converts English to [Language].

[Language] features [key distinguishing features]."""

VOCABULARY_PROMPT = f"""
# Vocabulary

## Nouns
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in NOUNS)}

## Transitive Verbs
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in TRANSITIVE_VERBS)}

## Intransitive Verbs
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in INTRANSITIVE_VERBS)}
"""

GRAMMAR_PROMPT = """
# Grammar Rules

## Word Order
[Explain word order with examples]

## [Feature 1]
[Explain with examples]

## [Feature 2]
[Explain with examples]

## Sentence Patterns
[Show patterns with examples]
"""

def get_prompt(
    include_vocab: bool,
    has_tools: bool = False,
    include_examples: Iterable[Type["Sentence"]] | None = None,
) -> str:
    """Generate system prompt"""
    prompt = SYSTEM_PROMPT_PREFIX

    if has_tools:
        prompt += "\n\n# Tool Usage\nYou have access to tools..."

    if include_vocab:
        prompt += "\n\n" + VOCABULARY_PROMPT

    prompt += "\n\n" + GRAMMAR_PROMPT

    if include_examples:
        prompt += "\n\n# Examples\n"
        for sentence_cls in include_examples:
            for source, example_sentence in sentence_cls.get_examples():
                prompt += f"\nEnglish: {source}\n[Language]: {example_sentence}\n"

    return prompt

__all__ = ["get_prompt"]
```

### Step 7: Create Test Script

```python
"""Test script for [Language] translator."""

import os
from dotenv import load_dotenv

from yaduha.agent.openai import OpenAIAgent
from yaduha.translator.pipeline import PipelineTranslator
from yaduha.language.[languagename] import (
    SentenceType1,
    SentenceType2,
)

load_dotenv()

def main():
    print("=" * 70)
    print("[LANGUAGE NAME] TRANSLATOR TEST")
    print("=" * 70)
    print("\nFeatures:")
    print("  - [Feature 1]")
    print("  - [Feature 2]")
    print("\n" + "=" * 70 + "\n")

    agent = OpenAIAgent(
        model="gpt-4o-mini",
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0.0,
    )

    translator = PipelineTranslator(
        agent=agent,
        SentenceType=(SentenceType1, SentenceType2),
    )

    test_sentences = [
        "The dog sleeps.",
        "I see you.",
        "The cat eats fish.",
    ]

    for i, english_sentence in enumerate(test_sentences, 1):
        print(f"Test {i}: {english_sentence}")
        print("-" * 70)

        try:
            result = translator(english_sentence)
            print(f"English:          {result.source}")
            print(f"[Language]:       {result.target}")
            print(f"Back-translation: {result.back_translation.source}")
            print(f"\nTokens: {result.prompt_tokens + result.completion_tokens}")
            print(f"Time:   {result.translation_time:.2f}s\n")
        except Exception as e:
            print(f"ERROR: {e}\n")

        print("=" * 70 + "\n")

if __name__ == "__main__":
    main()
```

### Step 8: Testing and Debugging

**Common issues and solutions:**

1. **"Unknown noun/verb" errors:**
   - Check that `json_schema_extra` enum lists are correct
   - Verify NOUN_LOOKUP and VERB_LOOKUP dictionaries are populated

2. **LLM uses target language words instead of English:**
   - Missing `json_schema_extra` - add it!
   - Description should explicitly say "English lemma"

3. **Validation errors on sentence creation:**
   - Check field_validator decorators are present
   - Ensure validators check the lookup dictionaries

4. **Translation produces gibberish:**
   - Check `__str__()` methods render correctly
   - Test rendering manually before running translator

**Testing checklist:**
```python
# Test 1: Basic imports
from yaduha.language.yourlang import *

# Test 2: Create example sentence manually
sentence = YourSentenceType(...)
print(sentence)  # Should render correctly

# Test 3: Run validator
# Should accept valid values, reject invalid ones

# Test 4: Run full translator test
python scripts/test_yourlang_translator.py
```

## Example: Creating a Tonal Language

Here's a concrete example prompt:

```
Create a tonal language called "Manding" for Yaduha with these features:

UNIQUE FEATURES:
- 4 tones: high (¹), rising (²), falling (³), low (⁴)
- Classifier system (5 classifiers for different noun types)
- Topic-prominent (not subject-prominent)
- SVO word order
- Aspect-heavy (no tense, only aspect)
- Serial verb constructions

VOCABULARY:
- 40 nouns organized by classifier categories
- 35 verbs
- Monosyllabic roots with tone marks
- Inspired by West African language phonology

Follow the exact architecture pattern from yaduha/language/kethara/, including:
1. Field(..., json_schema_extra={'enum': [...]}) on all Noun.head and Verb.lemma fields
2. Separate TransitiveVerb and IntransitiveVerb classes
3. At least 2 sentence types with get_examples()
4. Complete prompts.py with grammar explanations

Create all 4 files: vocab.py, __init__.py, prompts.py, and test script.
```

## Tips for Unique Language Design

1. **Pick one "headline" feature** (e.g., evidentiality, classifiers, switch-reference)
2. **Avoid mixing too many rare features** - keep it learnable
3. **Think about which features interact** - e.g., vowel harmony affects all suffixes
4. **Consider morphological alignment** - how do features stack/combine?
5. **Test rendering manually first** - make sure `__str__()` works before AI translation
6. **Document thoroughly** - future users need to understand the grammar

## Resources

**Study these for inspiration:**
- [WALS Online](https://wals.info/) - World Atlas of Language Structures
- [Wikipedia: Language Typology](https://en.wikipedia.org/wiki/Linguistic_typology)
- Existing conlangs: Esperanto, Lojban, Toki Pona, Na'vi, Klingon

**Yaduha reference implementations:**
- Simple: [OVP](../yaduha/language/ovp/) - straightforward SOV language
- Medium: [Velar](../yaduha/language/velar/) - evidentiality and gender
- Complex: [Kethara](../yaduha/language/kethara/) - agglutination and vowel harmony

## Final Checklist

Before submitting your new language:

- [ ] Created all 4 required files
- [ ] Added `json_schema_extra` to ALL Noun and Verb Field() declarations
- [ ] Implemented `__str__()` methods for Pronoun, Noun, Verb, and all Sentence types
- [ ] Included `get_examples()` with 2-3 examples per sentence type
- [ ] Added field_validator decorators for head/lemma validation
- [ ] Wrote comprehensive grammar documentation in prompts.py
- [ ] Created test script
- [ ] Tested basic sentence construction manually
- [ ] Ran full translator test successfully
- [ ] Documented unique features clearly

## Conclusion

With this guide, you can prompt an AI to generate a complete, working constructed language for Yaduha in minutes. The key is understanding the architecture pattern (especially `json_schema_extra`) and designing truly unique grammatical features.

Happy language creation! 🌍✨
