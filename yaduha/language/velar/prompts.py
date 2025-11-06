"""
Prompt generation for Velar language translation.
"""

from typing import Iterable, Type
from yaduha.language import Sentence
from yaduha.language.velar.vocab import (
    ANIMATE_NOUNS,
    INANIMATE_NOUNS,
    TRANSITIVE_VERBS,
    INTRANSITIVE_VERBS,
)

SYSTEM_PROMPT_PREFIX = """You are a translator that converts English to Velar, a constructed language.

Velar is a VSO (Verb-Subject-Object) language with unique grammatical features."""

TOOL_USE_INSTRUCTION = """
# Tool Usage
You have access to tools that can help with translation. Use them when you need assistance breaking down complex sentences or validating translations."""

VOCABULARY_PROMPT = f"""
# Vocabulary

## Animate Nouns (beings capable of movement)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in ANIMATE_NOUNS)}

## Inanimate Nouns (objects, places, concepts)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in INANIMATE_NOUNS)}

## Transitive Verbs (require an object)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in TRANSITIVE_VERBS)}

## Intransitive Verbs (no object)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in INTRANSITIVE_VERBS)}
"""

GRAMMAR_PROMPT = """
# Grammar Rules

## Word Order
Velar uses **VSO (Verb-Subject-Object)** order, unlike English's SVO.

Examples:
- English: "I see you" → Velar: "Viden-as-vi jo te" (see-PRES-DIRECT I you)
- English: "The cat eats fish" → Velar: "Manjan-as-vi le miavor la peskol" (eat-PRES-DIRECT the.ANIM cat the.INAN fish)

## Pronouns

### Subject Pronouns
Velar has **gendered pronouns** (unlike some languages):

**First Person:**
- jo (I - singular)
- nos (we - plural)

**Second Person (with formality levels):**
- tu (you - informal singular)
- vos (you - formal singular)
- dom (you - honorific singular)
- tus (you all - informal plural)
- voses (you all - formal plural)

**Third Person (with gender):**
- el (he - masculine singular)
- ela (she - feminine singular)
- lo (it - neuter singular)
- els (they - masculine plural)
- elas (they - feminine plural)
- los (they - neuter plural)

### Object Pronouns
- me (me)
- te (you)
- nos (us)
- vos (you all)
- lo (him/it)
- la (her)
- los (them - masculine/neuter)
- las (them - feminine)

## Verb Conjugation

Verbs conjugate with **four components** in this order:
1. **Stem** (the base verb form)
2. **Aspect** suffix
3. **Tense** suffix
4. **Evidentiality** suffix

Format: `stem + aspect + tense + evidentiality`

### Aspect Suffixes
- Simple: (no suffix)
- Progressive: -ik
- Perfect: -um

### Tense Suffixes
- Past: -et
- Present: -as
- Future: -os

### Evidentiality Suffixes (unique feature!)
Evidentiality marks how the speaker knows the information:
- Direct witness: -vi (I saw it happen)
- Hearsay: -au (I heard about it)
- Inferential: -if (I infer it from evidence)

### Examples
- "see" (present, simple, direct): viden-as-vi
- "run" (past, progressive, direct): kurir-ik-et-vi
- "eat" (future, simple, hearsay): manjan-os-au
- "love" (present, perfect, inferential): amar-um-as-if

## Nouns

### Number
- Singular: base form
- Plural: add -es

Examples:
- kanir (dog) → kanires (dogs)
- arbos (tree) → arboses (trees)

### Definiteness & Animacy
Velar has **two definite articles** based on animacy:
- **le**: for animate nouns (people, animals)
  - le kanir (the dog)
  - le renok (the person)
- **la**: for inanimate nouns (objects, concepts)
  - la arbos (the tree)
  - la petra (the stone)

No article means indefinite:
- kanir (a dog)
- arbos (a tree)

### Animate vs Inanimate
This is a **grammatical distinction** that affects article choice:
- Animate: beings capable of independent movement (people, animals)
- Inanimate: objects, places, natural phenomena, concepts

## Sentence Patterns

### Pattern 1: Verb-Subject (VS)
For intransitive verbs (no object).

Structure: `[VERB-conjugated] [SUBJECT]`

Examples:
- "I sleep" → `Dormir-as-vi jo` (sleep-PRES-DIRECT I)
- "The dog runs" → `Kurir-as-vi le kanir` (run-PRES-DIRECT the.ANIM dog)
- "She was dancing" → `Dansar-ik-et-vi ela` (dance-PROG-PAST-DIRECT she)

### Pattern 2: Verb-Subject-Object (VSO)
For transitive verbs (require an object).

Structure: `[VERB-conjugated] [SUBJECT] [OBJECT]`

Examples:
- "I see you" → `Viden-as-vi jo te` (see-PRES-DIRECT I you)
- "The cat sees the bird" → `Viden-as-vi le miavor le avizel` (see-PRES-DIRECT the.ANIM cat the.ANIM bird)
- "He was reading the book" → `Lektar-ik-et-vi el la librek` (read-PROG-PAST-DIRECT he the.INAN book)

## Key Differences from English

1. **Word Order**: VSO instead of SVO
2. **Gendered Pronouns**: Third person pronouns distinguish gender
3. **Formality Levels**: Second person has informal/formal/honorific forms
4. **Evidentiality**: Verbs must indicate information source (direct/hearsay/inference)
5. **Animacy**: Articles differ based on whether noun is animate or inanimate
6. **No "to be"**: Use main verbs directly
"""


def get_prompt(
    include_vocab: bool,
    has_tools: bool = False,
    include_examples: Iterable[Type["Sentence"]] | None = None,
) -> str:
    """
    Generate system prompt for Velar translation.

    Args:
        include_vocab: Whether to include full vocabulary list
        has_tools: Whether translator has access to tools
        include_examples: Sentence types to include examples from

    Returns:
        Complete system prompt string
    """
    prompt = SYSTEM_PROMPT_PREFIX

    if has_tools:
        prompt += "\n\n" + TOOL_USE_INSTRUCTION

    if include_vocab:
        prompt += "\n\n" + VOCABULARY_PROMPT

    prompt += "\n\n" + GRAMMAR_PROMPT

    # Add examples if requested
    if include_examples:
        prompt += "\n\n# Examples\n"
        for sentence_cls in include_examples:
            for source, example_sentence in sentence_cls.get_examples():
                prompt += (
                    f"\nEnglish: {source}\n"
                    f"Velar: {example_sentence}\n"
                )

    return prompt


__all__ = ["get_prompt"]
