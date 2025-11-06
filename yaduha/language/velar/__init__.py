"""
Velar Language Grammar Implementation

Key Features:
1. Gendered Pronouns: masculine, feminine, neuter (unlike OVP's ungendered system)
2. Evidentiality: markers indicating information source (direct, hearsay, inference)
3. Animacy: grammatical distinction between animate and inanimate nouns
4. VSO Word Order: Verb-Subject-Object (unlike OVP's SOV)
5. No Proximity: doesn't distinguish this/that (unlike OVP)
6. Formality Levels: informal, formal, honorific
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Type, Union, ClassVar
from pydantic import BaseModel, Field, field_validator
import random

from yaduha.language import Sentence
from yaduha.language.velar.vocab import (
    NOUNS,
    ANIMATE_NOUNS,
    INANIMATE_NOUNS,
    TRANSITIVE_VERBS,
    INTRANSITIVE_VERBS,
)

# ============================================================================
# LOOKUP DICTIONARIES
# ============================================================================

NOUN_LOOKUP: Dict[str, tuple] = {
    entry.english: (entry.target, entry in ANIMATE_NOUNS)
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


def is_animate_noun(lemma: str) -> bool:
    """Check if noun is animate"""
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
# GRAMMATICAL FEATURES (Enums)
# ============================================================================

class Gender(str, Enum):
    """
    Grammatical gender for pronouns and agreement.
    Unlike OVP which has no gender, Velar distinguishes three genders.
    """
    masculine = "masculine"
    feminine = "feminine"
    neuter = "neuter"


class Person(str, Enum):
    """Grammatical person (1st, 2nd, 3rd)"""
    first = "first"
    second = "second"
    third = "third"


class Number(str, Enum):
    """
    Grammatical number.
    Unlike OVP which has singular/dual/plural, Velar only has singular/plural.
    """
    singular = "singular"
    plural = "plural"


class Formality(str, Enum):
    """
    Formality level for second person pronouns.
    This feature doesn't exist in OVP.
    """
    informal = "informal"  # used with friends, children
    formal = "formal"      # used with strangers, superiors
    honorific = "honorific"  # used with elders, nobility


class Tense(str, Enum):
    """Tense marking"""
    past = "past"
    present = "present"
    future = "future"


class Aspect(str, Enum):
    """Aspect marking"""
    simple = "simple"
    progressive = "progressive"
    perfect = "perfect"


class Evidentiality(str, Enum):
    """
    Evidentiality: marks the source of information.
    This is a unique feature not present in OVP.
    """
    direct = "direct"        # speaker witnessed it directly
    hearsay = "hearsay"      # speaker heard about it from others
    inferential = "inferential"  # speaker infers it from evidence


# Suffix mappings for tense
TENSE_SUFFIX: Dict[Tense, str] = {
    Tense.past: "-et",
    Tense.present: "-as",
    Tense.future: "-os",
}

# Suffix mappings for aspect
ASPECT_SUFFIX: Dict[Aspect, str] = {
    Aspect.simple: "",
    Aspect.progressive: "-ik",
    Aspect.perfect: "-um",
}

# Suffix mappings for evidentiality
EVIDENTIALITY_SUFFIX: Dict[Evidentiality, str] = {
    Evidentiality.direct: "-vi",      # "I saw"
    Evidentiality.hearsay: "-au",     # "I heard"
    Evidentiality.inferential: "-if",  # "I infer"
}

# Plural marker for nouns
PLURAL_SUFFIX = "-es"

# Definite article based on animacy
DEFINITE_ARTICLE_ANIMATE = "le"    # for people, animals
DEFINITE_ARTICLE_INANIMATE = "la"  # for objects, concepts


# ============================================================================
# PRONOUN SYSTEM
# ============================================================================

class Pronoun(BaseModel):
    """
    Velar pronoun with gender, person, number, and formality.

    Key differences from OVP:
    - Has gender (masculine/feminine/neuter)
    - Has formality levels for 2nd person
    - No proximity distinction
    - No inclusivity distinction
    - No dual number (only singular/plural)
    """
    person: Person
    number: Number
    gender: Gender  # NEW: Not in OVP
    formality: Optional[Formality] = None  # NEW: Only used for 2nd person

    def get_subject_pronoun(self) -> str:
        """Get nominative pronoun form"""
        if self.person == Person.first:
            if self.number == Number.singular:
                return "jo"  # I
            else:
                return "nos"  # we

        elif self.person == Person.second:
            if self.number == Number.singular:
                if self.formality == Formality.informal:
                    return "tu"  # you (informal)
                elif self.formality == Formality.formal:
                    return "vos"  # you (formal)
                else:  # honorific
                    return "dom"  # you (honorific)
            else:  # plural
                if self.formality == Formality.informal:
                    return "tus"  # you all (informal)
                else:  # formal/honorific
                    return "voses"  # you all (formal)

        else:  # third person
            if self.number == Number.singular:
                if self.gender == Gender.masculine:
                    return "el"  # he
                elif self.gender == Gender.feminine:
                    return "ela"  # she
                else:  # neuter
                    return "lo"  # it
            else:  # plural
                if self.gender == Gender.masculine:
                    return "els"  # they (masculine)
                elif self.gender == Gender.feminine:
                    return "elas"  # they (feminine)
                else:  # neuter
                    return "los"  # they (neuter)

    def get_object_pronoun(self) -> str:
        """Get accusative pronoun form"""
        if self.person == Person.first:
            if self.number == Number.singular:
                return "me"  # me
            else:
                return "nos"  # us

        elif self.person == Person.second:
            if self.number == Number.singular:
                return "te"  # you
            else:
                return "vos"  # you all

        else:  # third person
            if self.number == Number.singular:
                if self.gender == Gender.masculine:
                    return "lo"  # him
                elif self.gender == Gender.feminine:
                    return "la"  # her
                else:  # neuter
                    return "lo"  # it
            else:  # plural
                if self.gender == Gender.masculine:
                    return "los"  # them (masculine)
                elif self.gender == Gender.feminine:
                    return "las"  # them (feminine)
                else:  # neuter
                    return "los"  # them (neuter)


# ============================================================================
# NOUN CLASSES
# ============================================================================

class Noun(BaseModel):
    """
    Base noun class for Velar.

    Key differences from OVP:
    - Has animacy (animate vs inanimate)
    - Has definiteness marker
    - No proximity distinction (no this/that)
    - No possessive determiners (simplified for now)
    """
    head: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in NOUNS],
            'description': 'An English noun lemma from the Velar vocabulary'
        }
    )
    number: Number
    definite: bool = False  # whether to use definite article

    @field_validator("head")
    @classmethod
    def validate_head(cls, v: str) -> str:
        if v not in NOUN_LOOKUP:
            raise ValueError(f"Unknown noun: {v}")
        return v

    def get_target(self) -> str:
        """Render noun in Velar"""
        target = get_noun_target(self.head)

        # Add plural suffix if plural
        if self.number == Number.plural:
            target += PLURAL_SUFFIX

        # Add definite article if definite
        if self.definite:
            if is_animate_noun(self.head):
                return f"{DEFINITE_ARTICLE_ANIMATE} {target}"
            else:
                return f"{DEFINITE_ARTICLE_INANIMATE} {target}"

        return target

    def get_gender(self) -> Gender:
        """
        Infer grammatical gender from noun.
        Animate nouns can be any gender; inanimate are neuter.
        For simplicity, we default to neuter.
        """
        return Gender.neuter

    def is_animate(self) -> bool:
        """Check if this noun is animate"""
        return is_animate_noun(self.head)


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
            'description': 'An English verb lemma (transitive or intransitive) from the Velar vocabulary'
        }
    )
    tense: Tense
    aspect: Aspect
    evidentiality: Evidentiality

    @field_validator("lemma")
    @classmethod
    def validate_lemma(cls, v: str) -> str:
        """Validate that lemma is a known English verb"""
        if v not in TRANSITIVE_VERB_LOOKUP and v not in INTRANSITIVE_VERB_LOOKUP:
            valid_verbs = ", ".join(sorted(list(TRANSITIVE_VERB_LOOKUP.keys())[:5] + list(INTRANSITIVE_VERB_LOOKUP.keys())[:5]))
            raise ValueError(
                f"Unknown verb: '{v}'. "
                f"Must be an English lemma from vocabulary (e.g., {valid_verbs})"
            )
        return v

    def get_conjugated_form(self) -> str:
        """
        Get fully conjugated verb form.

        Format: stem + aspect + tense + evidentiality
        Example: viden-ik-et-vi (see-PROG-PAST-DIRECT)
        """
        stem = get_verb_target(self.lemma)
        aspect_suffix = ASPECT_SUFFIX[self.aspect]
        tense_suffix = TENSE_SUFFIX[self.tense]
        evid_suffix = EVIDENTIALITY_SUFFIX[self.evidentiality]

        return f"{stem}{aspect_suffix}{tense_suffix}{evid_suffix}"


class TransitiveVerb(Verb):
    """Verb that requires an object"""
    lemma: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in TRANSITIVE_VERBS],
            'description': 'An English transitive verb lemma from the Velar vocabulary'
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
            'description': 'An English intransitive verb lemma from the Velar vocabulary'
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

class VerbSubjectSentence(Sentence["VerbSubjectSentence"]):
    """
    Simple intransitive sentence in Velar.

    Word order: VERB-SUBJECT (VS)

    Example:
        English: "The dog sleeps."
        Velar: "Dormir-as-vi le kanir"
               sleep-PRES-DIRECT the.ANIM dog
    """
    verb: IntransitiveVerb
    subject: Union[SubjectNoun, Pronoun]

    def __str__(self) -> str:
        """Render sentence in Velar"""
        # Get conjugated verb
        verb_str = self.verb.get_conjugated_form()

        # Get subject
        if isinstance(self.subject, Pronoun):
            subject_str = self.subject.get_subject_pronoun()
        else:
            subject_str = self.subject.get_target()

        # VSO order: Verb Subject
        return f"{verb_str} {subject_str}"

    @classmethod
    def get_examples(cls) -> List[Tuple[str, "VerbSubjectSentence"]]:
        """Provide example sentences for few-shot learning"""
        return [
            (
                "I sleep.",
                VerbSubjectSentence(
                    verb=IntransitiveVerb(
                        lemma="sleep",
                        tense=Tense.present,
                        aspect=Aspect.simple,
                        evidentiality=Evidentiality.direct,
                    ),
                    subject=Pronoun(
                        person=Person.first,
                        number=Number.singular,
                        gender=Gender.neuter,
                    ),
                ),
            ),
            (
                "The dog runs.",
                VerbSubjectSentence(
                    verb=IntransitiveVerb(
                        lemma="run",
                        tense=Tense.present,
                        aspect=Aspect.simple,
                        evidentiality=Evidentiality.direct,
                    ),
                    subject=SubjectNoun(
                        head="dog",
                        number=Number.singular,
                        definite=True,
                    ),
                ),
            ),
            (
                "She was dancing.",
                VerbSubjectSentence(
                    verb=IntransitiveVerb(
                        lemma="dance",
                        tense=Tense.past,
                        aspect=Aspect.progressive,
                        evidentiality=Evidentiality.direct,
                    ),
                    subject=Pronoun(
                        person=Person.third,
                        number=Number.singular,
                        gender=Gender.feminine,
                    ),
                ),
            ),
        ]


class VerbSubjectObjectSentence(Sentence["VerbSubjectObjectSentence"]):
    """
    Transitive sentence in Velar.

    Word order: VERB-SUBJECT-OBJECT (VSO)

    Example:
        English: "The cat sees the bird."
        Velar: "Viden-as-vi le miavor le avizel"
               see-PRES-DIRECT the.ANIM cat the.ANIM bird
    """
    verb: TransitiveVerb
    subject: Union[SubjectNoun, Pronoun]
    object: Union[ObjectNoun, Pronoun]

    def __str__(self) -> str:
        """Render sentence in Velar"""
        # Get conjugated verb
        verb_str = self.verb.get_conjugated_form()

        # Get subject
        if isinstance(self.subject, Pronoun):
            subject_str = self.subject.get_subject_pronoun()
        else:
            subject_str = self.subject.get_target()

        # Get object
        if isinstance(self.object, Pronoun):
            object_str = self.object.get_object_pronoun()
        else:
            object_str = self.object.get_target()

        # VSO order: Verb Subject Object
        return f"{verb_str} {subject_str} {object_str}"

    @classmethod
    def get_examples(cls) -> List[Tuple[str, "VerbSubjectObjectSentence"]]:
        """Provide example sentences for few-shot learning"""
        return [
            (
                "I see you.",
                VerbSubjectObjectSentence(
                    verb=TransitiveVerb(
                        lemma="see",
                        tense=Tense.present,
                        aspect=Aspect.simple,
                        evidentiality=Evidentiality.direct,
                    ),
                    subject=Pronoun(
                        person=Person.first,
                        number=Number.singular,
                        gender=Gender.neuter,
                    ),
                    object=Pronoun(
                        person=Person.second,
                        number=Number.singular,
                        gender=Gender.neuter,
                        formality=Formality.informal,
                    ),
                ),
            ),
            (
                "The cat sees the bird.",
                VerbSubjectObjectSentence(
                    verb=TransitiveVerb(
                        lemma="see",
                        tense=Tense.present,
                        aspect=Aspect.simple,
                        evidentiality=Evidentiality.direct,
                    ),
                    subject=SubjectNoun(
                        head="cat",
                        number=Number.singular,
                        definite=True,
                    ),
                    object=ObjectNoun(
                        head="bird",
                        number=Number.singular,
                        definite=True,
                    ),
                ),
            ),
            (
                "He was reading the book.",
                VerbSubjectObjectSentence(
                    verb=TransitiveVerb(
                        lemma="read",
                        tense=Tense.past,
                        aspect=Aspect.progressive,
                        evidentiality=Evidentiality.direct,
                    ),
                    subject=Pronoun(
                        person=Person.third,
                        number=Number.singular,
                        gender=Gender.masculine,
                    ),
                    object=ObjectNoun(
                        head="book",
                        number=Number.singular,
                        definite=True,
                    ),
                ),
            ),
            (
                "They heard that the woman loves the man.",
                VerbSubjectObjectSentence(
                    verb=TransitiveVerb(
                        lemma="love",
                        tense=Tense.present,
                        aspect=Aspect.simple,
                        evidentiality=Evidentiality.hearsay,  # KEY: hearsay evidential
                    ),
                    subject=SubjectNoun(
                        head="woman",
                        number=Number.singular,
                        definite=True,
                    ),
                    object=ObjectNoun(
                        head="man",
                        number=Number.singular,
                        definite=True,
                    ),
                ),
            ),
        ]


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Enums
    "Gender",
    "Person",
    "Number",
    "Formality",
    "Tense",
    "Aspect",
    "Evidentiality",
    # Classes
    "Pronoun",
    "Noun",
    "SubjectNoun",
    "ObjectNoun",
    "Verb",
    "TransitiveVerb",
    "IntransitiveVerb",
    # Sentences
    "VerbSubjectSentence",
    "VerbSubjectObjectSentence",
    # Helpers
    "get_noun_target",
    "get_verb_target",
    "is_animate_noun",
]
