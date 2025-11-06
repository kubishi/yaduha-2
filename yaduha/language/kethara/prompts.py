"""
Prompt generation for Kethara language translation.
"""

from typing import Iterable, Type
from yaduha.language import Sentence
from yaduha.language.kethara.vocab import (
    HUMAN_NOUNS,
    ANIMAL_NOUNS,
    PLANT_NOUNS,
    OBJECT_NOUNS,
    ABSTRACT_NOUNS,
    TRANSITIVE_VERBS,
    INTRANSITIVE_VERBS,
)

SYSTEM_PROMPT_PREFIX = """You are a translator that converts English to Kethara, an agglutinative constructed language.

Kethara features SOV (Subject-Object-Verb) word order and extensive suffix stacking."""

TOOL_USE_INSTRUCTION = """
# Tool Usage
You have access to tools that can help with translation. Use them when needed."""

VOCABULARY_PROMPT = f"""
# Vocabulary

## Human Nouns (people, professions)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in HUMAN_NOUNS)}

## Animal Nouns (creatures)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in ANIMAL_NOUNS)}

## Plant Nouns (vegetation)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in PLANT_NOUNS)}

## Object Nouns (inanimate things)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in OBJECT_NOUNS)}

## Abstract Nouns (concepts, places, phenomena)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in ABSTRACT_NOUNS)}

## Transitive Verbs (require an object)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in TRANSITIVE_VERBS)}

## Intransitive Verbs (no object)
{chr(10).join(f"- {entry.english}: {entry.target}" for entry in INTRANSITIVE_VERBS)}
"""

GRAMMAR_PROMPT = """
# Grammar Rules

## Word Order
Kethara uses **SOV (Subject-Object-Verb)** order, like Turkish or Japanese.

Examples:
- English: "I see you" → Kethara: "min sinn nakha" (I you-ACC see-PRES)
- English: "The cat eats fish" → Kethara: "shiva nakosn syoa" (cat fish-ACC eat-PRES)

## Noun Classes (NOT gender)
Kethara nouns belong to semantic classes that affect how they behave:
- **Human**: people, professions (zhen, kodan, thera)
- **Animal**: living creatures (kurma, shiva, telun)
- **Plant**: vegetation (korvan, lumi, veltha)
- **Object**: inanimate physical things (talo, kirja, vesik)
- **Abstract**: concepts, places, phenomena (taiva, aurik, rakka)

## Pronouns

Pronouns have NO gender distinction (unlike Velar).

**Pronoun stems** (before suffixes):
- min (I/me)
- sin (you - singular)
- han (he/she/it - no gender!)
- me (we/us)
- te (you all)
- he (they)

Pronouns take the same case suffixes as nouns.

## Case System (Directional/Spatial)

Kethara uses a **directional case system** (different from European languages):

**Basic cases:**
- **Nominative** (subject): no suffix
  - kurma (dog)
- **Accusative** (direct object): -n
  - kurman (dog-ACC)

**Spatial/directional cases:**
- **Illative** (into, towards): -han/-hen
  - talahan (into the house)
- **Elative** (out of, from): -sta/-stä
  - talosta (from the house)
- **Adessive** (at, on location): -lla/-llä
  - talolla (at the house)
- **Inessive** (in location): -ssa/-ssä
  - talossa (in the house)

## Vowel Harmony (KEY FEATURE!)

**Kethara has vowel harmony** - suffix vowels change to match the root word.

**Front vowels**: e, i, ä, ö, y
**Back vowels**: a, o, u

If a root has front vowels, suffixes harmonize:
- a → ä
- o → ö
- u → y

**Examples:**
- kurma + -lla → kurmalla (at the dog) [back vowels]
- kirja + -ssa → kirjassa (in the book) [back vowels]
- telun + -lla → telunillä (at the bird) [front harmony: -lla → -llä]

## Number

- **Singular**: base form
- **Plural**: add -t

Examples:
- kurma (dog) → kurmat (dogs)
- kirja (book) → kirjat (books)

Combined with case:
- kurmatn (dogs-ACC) = kurmat + n
- kirjatlla (at the books) = kirjat + lla

## Verb Morphology (Agglutinative!)

Verbs stack multiple suffixes in a specific order:

**Format: ROOT + TENSE + MOOD + POLITENESS**

### Tense Suffixes
- Present: -a/-ä (harmonizes!)
- Past: -i
- Future: -kse

### Mood Suffixes
- Indicative (statement): (no suffix)
- Conditional (would/could): -isi
- Imperative (command): -ko/-kö

### Politeness Suffixes
Unlike Velar which marks formality in pronouns, **Kethara marks it on verbs**:
- Plain (casual): (no suffix)
- Polite (respectful): -vat/-vät
- Formal (very formal): -nne

### Stacking Examples

**nakh** (see):
- nakha (see-PRES) = "sees"
- nakhi (see-PAST) = "saw"
- nakhkse (see-FUT) = "will see"
- nakhivat (see-PAST-POLITE) = "politely saw"
- nakhksennevät (see-FUT-FORMAL) = "will formally see"
- nakhisiko (see-PAST-COND-IMP) = "would have seen?"

**kirjoit** (write) - with front vowel harmony:
- kirjoita (write-PRES) [harmonized: -a → -ä... wait, 'i' is front]
- kirjoiti (write-PAST)
- kirjoitkse (write-FUT)
- kirjoitisivät (write-PAST-COND-POLITE)

## Sentence Patterns

### Pattern 1: Subject-Verb (SV)
For intransitive verbs.

Structure: `[SUBJECT] [VERB-conjugated]`

Examples:
- "I sleep" → `min nukua` (I sleep-PRES)
- "The dog runs" → `kurma juoksa` (dog run-PRES)
- "Birds fly" → `telunt lennä` (birds fly-PRES)

### Pattern 2: Subject-Object-Verb (SOV)
For transitive verbs.

Structure: `[SUBJECT] [OBJECT-accusative] [VERB-conjugated]`

Examples:
- "I see you" → `min sinn nakha` (I you-ACC see-PRES)
- "The cat sees the bird" → `shiva telunn nakha` (cat bird-ACC see-PRES)
- "The woman loves the man" → `thera kodann rakastävat` (woman man-ACC love-PRES-POLITE)

## Key Differences from English

1. **SOV word order** instead of SVO
2. **Noun classes** (semantic) instead of grammatical gender
3. **Case marking** shows grammatical role and spatial relationships
4. **Vowel harmony** affects all suffixes
5. **Agglutination** - suffixes stack on roots
6. **Politeness on verbs** not separate pronouns
7. **No articles** - no "the" or "a"
8. **Extensive case system** for spatial relationships
"""


def get_prompt(
    include_vocab: bool,
    has_tools: bool = False,
    include_examples: Iterable[Type["Sentence"]] | None = None,
) -> str:
    """
    Generate system prompt for Kethara translation.

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
                    f"Kethara: {example_sentence}\n"
                )

    return prompt


__all__ = ["get_prompt"]
