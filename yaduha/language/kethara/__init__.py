"""
Kethara Language Grammar Implementation

Key Features:
1. Noun Classes: semantic categories (human/animal/plant/object/abstract) not gender
2. Agglutinative Morphology: suffixes stack onto roots
3. SOV Word Order: Subject-Object-Verb (like Turkish/Japanese)
4. Directional Cases: towards, away, at location (not just subject/object)
5. Vowel Harmony: suffix vowels adapt to root vowels
6. Politeness Levels: shown through verb suffixes, not separate pronouns
7. No Articles: definiteness from context
8. Tense-Aspect-Mood stacking on verbs
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Type, Union
from pydantic import BaseModel, Field, field_validator
import random

from yaduha.language import Sentence
from yaduha.language.kethara.vocab import (
    NOUNS,
    HUMAN_NOUNS,
    ANIMAL_NOUNS,
    PLANT_NOUNS,
    OBJECT_NOUNS,
    ABSTRACT_NOUNS,
    TRANSITIVE_VERBS,
    INTRANSITIVE_VERBS,
)

# ============================================================================
# LOOKUP DICTIONARIES
# ============================================================================

def _get_noun_class(english: str) -> str:
    """Determine which class a noun belongs to"""
    for entry in HUMAN_NOUNS:
        if entry.english == english:
            return "human"
    for entry in ANIMAL_NOUNS:
        if entry.english == english:
            return "animal"
    for entry in PLANT_NOUNS:
        if entry.english == english:
            return "plant"
    for entry in OBJECT_NOUNS:
        if entry.english == english:
            return "object"
    for entry in ABSTRACT_NOUNS:
        if entry.english == english:
            return "abstract"
    raise ValueError(f"Unknown noun: {english}")

NOUN_LOOKUP: Dict[str, tuple] = {
    entry.english: (entry.target, _get_noun_class(entry.english))
    for entry in NOUNS
}

TRANSITIVE_VERB_LOOKUP: Dict[str, str] = {
    entry.english: entry.target for entry in TRANSITIVE_VERBS
}

INTRANSITIVE_VERB_LOOKUP: Dict[str, str] = {
    entry.english: entry.target for entry in INTRANSITIVE_VERBS
}


def get_noun_target(lemma: str) -> str:
    """Get target form of noun"""
    return NOUN_LOOKUP[lemma][0]


def get_noun_class(lemma: str) -> str:
    """Get semantic class of noun"""
    return NOUN_LOOKUP[lemma][1]


def get_transitive_verb_target(lemma: str) -> str:
    """Get target form of transitive verb"""
    return TRANSITIVE_VERB_LOOKUP[lemma]


def get_intransitive_verb_target(lemma: str) -> str:
    """Get target form of intransitive verb"""
    return INTRANSITIVE_VERB_LOOKUP[lemma]


def get_verb_target(lemma: str) -> str:
    """Get target form of any verb"""
    if lemma in TRANSITIVE_VERB_LOOKUP:
        return TRANSITIVE_VERB_LOOKUP[lemma]
    return INTRANSITIVE_VERB_LOOKUP[lemma]


# ============================================================================
# VOWEL HARMONY
# ============================================================================

def has_front_vowels(word: str) -> bool:
    """Check if word contains front vowels (e, i, ä, ö, y)"""
    front_vowels = set('eiäöy')
    return any(char in front_vowels for char in word.lower())


def harmonize_suffix(suffix: str, root: str) -> str:
    """
    Apply vowel harmony to suffix based on root.

    Front harmony variants:
    - a -> ä
    - o -> ö
    - u -> y

    This is a key agglutinative feature!
    """
    if has_front_vowels(root):
        # Apply front vowel harmony
        suffix = suffix.replace('a', 'ä')
        suffix = suffix.replace('o', 'ö')
        suffix = suffix.replace('u', 'y')
    return suffix


# ============================================================================
# GRAMMATICAL FEATURES (Enums)
# ============================================================================

class NounClass(str, Enum):
    """
    Semantic noun classes (NOT grammatical gender).
    This is common in Bantu and other languages.
    """
    human = "human"        # people
    animal = "animal"      # living creatures
    plant = "plant"        # vegetation
    object = "object"      # inanimate physical things
    abstract = "abstract"  # concepts, places, phenomena


class Person(str, Enum):
    """Grammatical person"""
    first = "first"
    second = "second"
    third = "third"


class Number(str, Enum):
    """Grammatical number"""
    singular = "singular"
    plural = "plural"


class Case(str, Enum):
    """
    Directional/spatial case system (different from European nominative/accusative).
    Shows motion and location, not just subject/object.
    """
    nominative = "nominative"      # subject (no suffix)
    accusative = "accusative"      # direct object: -n
    illative = "illative"          # into, towards: -han/-hen
    elative = "elative"            # out of, from: -sta/-stä
    adessive = "adessive"          # at, on (location): -lla/-llä
    inessive = "inessive"          # in (location): -ssa/-ssä


# Case suffix mappings (with vowel harmony variants)
CASE_SUFFIX: Dict[Case, str] = {
    Case.nominative: "",
    Case.accusative: "n",
    Case.illative: "han",    # will harmonize to -hen
    Case.elative: "sta",     # will harmonize to -stä
    Case.adessive: "lla",    # will harmonize to -llä
    Case.inessive: "ssa",    # will harmonize to -ssä
}


class Tense(str, Enum):
    """Tense"""
    past = "past"
    present = "present"
    future = "future"


class Mood(str, Enum):
    """
    Grammatical mood - different from evidentiality.
    Shows speaker's attitude toward action.
    """
    indicative = "indicative"      # factual statement
    conditional = "conditional"    # would/could
    imperative = "imperative"      # command


class Politeness(str, Enum):
    """
    Politeness level expressed through verb suffix (not pronouns).
    This is like Japanese/Korean honorifics.
    """
    plain = "plain"          # casual
    polite = "polite"        # respectful
    formal = "formal"        # very formal/honorific


# Verb suffix mappings (stack in specific order)
TENSE_SUFFIX: Dict[Tense, str] = {
    Tense.past: "i",
    Tense.present: "a",     # will harmonize to -ä
    Tense.future: "kse",
}

MOOD_SUFFIX: Dict[Mood, str] = {
    Mood.indicative: "",
    Mood.conditional: "isi",
    Mood.imperative: "ko",   # will harmonize to -kö
}

POLITENESS_SUFFIX: Dict[Politeness, str] = {
    Politeness.plain: "",
    Politeness.polite: "vat",  # will harmonize to -vät
    Politeness.formal: "nne",
}

# Plural marker for nouns
PLURAL_SUFFIX = "t"


# ============================================================================
# PRONOUN SYSTEM
# ============================================================================

class Pronoun(BaseModel):
    """
    Kethara pronouns.

    Key differences from Velar/OVP:
    - No gender marking
    - No formality in pronouns (it's in verbs)
    - Case-marked like nouns
    """
    person: Person
    number: Number
    case: Case = Case.nominative

    def get_pronoun_stem(self) -> str:
        """Get pronoun root (before case suffix)"""
        if self.person == Person.first:
            if self.number == Number.singular:
                return "min"  # I/me
            else:
                return "me"   # we/us
        elif self.person == Person.second:
            if self.number == Number.singular:
                return "sin"  # you
            else:
                return "te"   # you all
        else:  # third person
            if self.number == Number.singular:
                return "han"  # he/she/it
            else:
                return "he"   # they

    def __str__(self) -> str:
        """Render pronoun with case marking"""
        stem = self.get_pronoun_stem()
        case_suffix = CASE_SUFFIX[self.case]

        # Apply vowel harmony
        case_suffix = harmonize_suffix(case_suffix, stem)

        return f"{stem}{case_suffix}"


# ============================================================================
# NOUN CLASSES
# ============================================================================

class Noun(BaseModel):
    """
    Kethara noun with semantic class and case marking.

    Key features:
    - Semantic noun class (not gender)
    - Case suffixes (directional/spatial)
    - Vowel harmony in suffixes
    - No articles
    """
    head: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in NOUNS],
            'description': 'An English noun lemma from the Kethara vocabulary'
        }
    )
    number: Number
    case: Case = Case.nominative

    @field_validator("head")
    @classmethod
    def validate_head(cls, v: str) -> str:
        if v not in NOUN_LOOKUP:
            raise ValueError(f"Unknown noun: {v}")
        return v

    def get_noun_class(self) -> NounClass:
        """Get semantic class of this noun"""
        class_str = get_noun_class(self.head)
        return NounClass(class_str)

    def __str__(self) -> str:
        """Render noun with number and case suffixes"""
        root = get_noun_target(self.head)
        result = root

        # Add plural suffix if plural
        if self.number == Number.plural:
            result += PLURAL_SUFFIX

        # Add case suffix
        case_suffix = CASE_SUFFIX[self.case]
        case_suffix = harmonize_suffix(case_suffix, root)
        result += case_suffix

        return result


class SubjectNoun(Noun):
    """Noun used as subject (nominative case)"""
    case: Case = Case.nominative


class ObjectNoun(Noun):
    """Noun used as object (accusative case)"""
    case: Case = Case.accusative


# ============================================================================
# VERB CLASSES
# ============================================================================

class Verb(BaseModel):
    """
    Kethara verb with agglutinative morphology.

    Suffix order: ROOT + TENSE + MOOD + POLITENESS
    All suffixes undergo vowel harmony!
    """
    lemma: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in TRANSITIVE_VERBS + INTRANSITIVE_VERBS],
            'description': 'An English verb lemma from the Kethara vocabulary'
        }
    )
    tense: Tense
    mood: Mood = Mood.indicative
    politeness: Politeness = Politeness.plain

    @field_validator("lemma")
    @classmethod
    def validate_lemma(cls, v: str) -> str:
        if v not in TRANSITIVE_VERB_LOOKUP and v not in INTRANSITIVE_VERB_LOOKUP:
            raise ValueError(f"Unknown verb: {v}")
        return v

    def get_conjugated_form(self) -> str:
        """
        Get fully inflected verb form with stacked suffixes.

        Format: ROOT + TENSE + MOOD + POLITENESS
        Example: nakh-i-isi-vat (see-PAST-COND-POLITE) = "politely would have seen"
        """
        root = get_verb_target(self.lemma)

        # Get suffixes
        tense_suffix = TENSE_SUFFIX[self.tense]
        mood_suffix = MOOD_SUFFIX[self.mood]
        pol_suffix = POLITENESS_SUFFIX[self.politeness]

        # Apply vowel harmony to each suffix
        tense_suffix = harmonize_suffix(tense_suffix, root)
        mood_suffix = harmonize_suffix(mood_suffix, root)
        pol_suffix = harmonize_suffix(pol_suffix, root)

        # Stack them together (agglutination!)
        return f"{root}{tense_suffix}{mood_suffix}{pol_suffix}"


class TransitiveVerb(Verb):
    """Verb that requires an object"""
    lemma: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in TRANSITIVE_VERBS],
            'description': 'An English transitive verb lemma from the Kethara vocabulary'
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
            'description': 'An English intransitive verb lemma from the Kethara vocabulary'
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

class SubjectVerbSentence(Sentence["SubjectVerbSentence"]):
    """
    Simple intransitive sentence in Kethara.

    Word order: SUBJECT-VERB (SV, with SOV when object present)

    Example:
        English: "The dog sleeps."
        Kethara: "kurma nukua"
                 dog sleep-PRES
    """
    subject: Union[SubjectNoun, Pronoun]
    verb: IntransitiveVerb

    def __str__(self) -> str:
        """Render sentence in Kethara (SOV order)"""
        # Get subject
        subject_str = str(self.subject)

        # Get verb
        verb_str = self.verb.get_conjugated_form()

        # SOV order: Subject Verb
        return f"{subject_str} {verb_str}"

    @classmethod
    def get_examples(cls) -> List[Tuple[str, "SubjectVerbSentence"]]:
        """Provide example sentences for few-shot learning"""
        return [
            (
                "I sleep.",
                SubjectVerbSentence(
                    subject=Pronoun(
                        person=Person.first,
                        number=Number.singular,
                        case=Case.nominative,
                    ),
                    verb=IntransitiveVerb(
                        lemma="sleep",
                        tense=Tense.present,
                        mood=Mood.indicative,
                        politeness=Politeness.plain,
                    ),
                ),
            ),
            (
                "The dog runs.",
                SubjectVerbSentence(
                    subject=SubjectNoun(
                        head="dog",
                        number=Number.singular,
                        case=Case.nominative,
                    ),
                    verb=IntransitiveVerb(
                        lemma="run",
                        tense=Tense.present,
                        mood=Mood.indicative,
                        politeness=Politeness.plain,
                    ),
                ),
            ),
            (
                "The birds are singing.",
                SubjectVerbSentence(
                    subject=SubjectNoun(
                        head="bird",
                        number=Number.plural,
                        case=Case.nominative,
                    ),
                    verb=IntransitiveVerb(
                        lemma="sing",
                        tense=Tense.present,
                        mood=Mood.indicative,
                        politeness=Politeness.plain,
                    ),
                ),
            ),
        ]


class SubjectObjectVerbSentence(Sentence["SubjectObjectVerbSentence"]):
    """
    Transitive sentence in Kethara.

    Word order: SUBJECT-OBJECT-VERB (SOV like Turkish/Japanese)

    Example:
        English: "The cat sees the bird."
        Kethara: "shiva telun nakha"
                 cat bird-ACC see-PRES
    """
    subject: Union[SubjectNoun, Pronoun]
    object: Union[ObjectNoun, Pronoun]
    verb: TransitiveVerb

    def __str__(self) -> str:
        """Render sentence in Kethara (SOV order)"""
        # Get subject (nominative)
        subject_str = str(self.subject)

        # Get object (accusative)
        object_str = str(self.object)

        # Get verb
        verb_str = self.verb.get_conjugated_form()

        # SOV order: Subject Object Verb
        return f"{subject_str} {object_str} {verb_str}"

    @classmethod
    def get_examples(cls) -> List[Tuple[str, "SubjectObjectVerbSentence"]]:
        """Provide example sentences for few-shot learning"""
        return [
            (
                "I see you.",
                SubjectObjectVerbSentence(
                    subject=Pronoun(
                        person=Person.first,
                        number=Number.singular,
                        case=Case.nominative,
                    ),
                    object=Pronoun(
                        person=Person.second,
                        number=Number.singular,
                        case=Case.accusative,
                    ),
                    verb=TransitiveVerb(
                        lemma="see",
                        tense=Tense.present,
                        mood=Mood.indicative,
                        politeness=Politeness.plain,
                    ),
                ),
            ),
            (
                "The cat sees the bird.",
                SubjectObjectVerbSentence(
                    subject=SubjectNoun(
                        head="cat",
                        number=Number.singular,
                        case=Case.nominative,
                    ),
                    object=ObjectNoun(
                        head="bird",
                        number=Number.singular,
                        case=Case.accusative,
                    ),
                    verb=TransitiveVerb(
                        lemma="see",
                        tense=Tense.present,
                        mood=Mood.indicative,
                        politeness=Politeness.plain,
                    ),
                ),
            ),
            (
                "The woman loves the man.",
                SubjectObjectVerbSentence(
                    subject=SubjectNoun(
                        head="woman",
                        number=Number.singular,
                        case=Case.nominative,
                    ),
                    object=ObjectNoun(
                        head="man",
                        number=Number.singular,
                        case=Case.accusative,
                    ),
                    verb=TransitiveVerb(
                        lemma="love",
                        tense=Tense.present,
                        mood=Mood.indicative,
                        politeness=Politeness.polite,  # polite form
                    ),
                ),
            ),
        ]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "NounClass",
    "Person",
    "Number",
    "Case",
    "Tense",
    "Mood",
    "Politeness",
    # Classes
    "Pronoun",
    "Noun",
    "SubjectNoun",
    "ObjectNoun",
    "Verb",
    "TransitiveVerb",
    "IntransitiveVerb",
    # Sentences
    "SubjectVerbSentence",
    "SubjectObjectVerbSentence",
    # Helpers
    "get_noun_target",
    "get_verb_target",
    "get_noun_class",
    "has_front_vowels",
    "harmonize_suffix",
]
