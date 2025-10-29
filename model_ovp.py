from pydantic import BaseModel, Field, field_validator
from typing import Dict, Generator, List, Optional, Union
from enum import Enum
from random import choice, randint
from dataclasses import dataclass

# ============================================================================
# VOCABULARY DEFINITIONS - **ONLY** PLACE TO ADD NEW WORDS!
# ============================================================================

@dataclass(frozen=True)
class VocabEntry:
    """Immutable vocabulary entry linking English and Paiute"""
    english: str
    paiute: str

# Define all vocabulary in one place - this is the ONLY place you need to edit!
NOUNS = [
    VocabEntry("coyote", "isha'"),
    VocabEntry("dog", "ishapugu"),
    VocabEntry("cat", "kidi'"),
    VocabEntry("horse", "pugu"),
    VocabEntry("rice", "wai"),
    VocabEntry("pinenuts", "tüba"),
    VocabEntry("corn", "maishibü"),
    VocabEntry("water", "paya"),
    VocabEntry("river", "payahuupü"),
    VocabEntry("chair", "katünu"),
    VocabEntry("mountain", "toyabi"),
    VocabEntry("food", "tuunapi"),
    VocabEntry("tree", "pasohobü"),
    VocabEntry("house", "nobi"),
    VocabEntry("wickiup", "toni"),
    VocabEntry("cup", "apo"),
    VocabEntry("wood", "küna"),
    VocabEntry("rock", "tübbi"),
    VocabEntry("cottontail", "tabuutsi'"),
    VocabEntry("jackrabbit", "kamü"),
    VocabEntry("apple", "aaponu'"),
    VocabEntry("weasle", "tüsüga"),
    VocabEntry("lizard", "mukita"),
    VocabEntry("mosquito", "wo'ada"),
    VocabEntry("bird_snake", "wükada"),
    VocabEntry("worm", "wo'abi"),
    VocabEntry("squirrel", "aingwü"),
    VocabEntry("bird", "tsiipa"),
    VocabEntry("earth", "tüwoobü"),
    VocabEntry("coffee", "koopi'"),
    VocabEntry("bear", "pahabichi"),
    VocabEntry("fish", "pagwi"),
    VocabEntry("tail", "kwadzi"),
]

TRANSITIVE_VERBS = [
    VocabEntry("eat", "tüka"),
    VocabEntry("see", "puni"),
    VocabEntry("drink", "hibi"),
    VocabEntry("hear", "naka"),
    VocabEntry("smell", "kwana"),
    VocabEntry("hit", "kwati"),
    VocabEntry("talk_to", "yadohi"),
    VocabEntry("chase", "naki"),
    VocabEntry("climb", "tsibui"),
    VocabEntry("cook", "sawa"),
    VocabEntry("read", "nia"),
    VocabEntry("write", "mui"),
    VocabEntry("visit", "nobini"),
    VocabEntry("find", "tama'i"),
]

INTRANSITIVE_VERBS = [
    VocabEntry("sit", "katü"),
    VocabEntry("sleep", "üwi"),
    VocabEntry("sneeze", "kwisha'i"),
    VocabEntry("run", "poyoha"),
    VocabEntry("go", "mia"),
    VocabEntry("walk", "hukaw̃ia"),
    VocabEntry("stand", "wünü"),
    VocabEntry("lie_down", "habi"),
    VocabEntry("talk", "yadoha"),
    VocabEntry("fall", "kwatsa'i"),
    VocabEntry("work", "waakü"),
    VocabEntry("smile", "wükihaa"),
    VocabEntry("sing", "hubiadu"),
    VocabEntry("laugh", "nishua'i"),
    VocabEntry("climb", "tsibui"),
    VocabEntry("play", "tübinohi"),
    VocabEntry("fly", "yotsi"),
    VocabEntry("dance", "nüga"),
    VocabEntry("swim", "pahabi"),
    VocabEntry("read", "tünia"),
    VocabEntry("write", "tümui"),
    VocabEntry("chirp", "tsiipe'i"),
]


# Lookup dictionaries for easy access
NOUN_LOOKUP: Dict[str, VocabEntry] = {entry.english: entry for entry in NOUNS}
TRANSITIVE_VERB_LOOKUP: Dict[str, VocabEntry] = {entry.english: entry for entry in TRANSITIVE_VERBS}
INTRANSITIVE_VERB_LOOKUP: Dict[str, VocabEntry] = {entry.english: entry for entry in INTRANSITIVE_VERBS}


def get_noun_paiute(lemma: str) -> str:
    return NOUN_LOOKUP[lemma].paiute

def get_transitive_verb_paiute(lemma: str) -> str:
    return TRANSITIVE_VERB_LOOKUP[lemma].paiute

def get_intransitive_verb_paiute(lemma: str) -> str:
    return INTRANSITIVE_VERB_LOOKUP[lemma].paiute

def get_verb_paiute(lemma: str) -> str:
    if lemma in TRANSITIVE_VERB_LOOKUP:
        return TRANSITIVE_VERB_LOOKUP[lemma].paiute
    return INTRANSITIVE_VERB_LOOKUP[lemma].paiute


# ============================================================================
# GRAMMATICAL ENUMERATIONS
# ============================================================================

class Proximity(str, Enum):
    proximal = "proximal"
    distal = "distal"

    def get_object_suffix(self, does_end_in_glottal: bool) -> str:
        if self == Proximity.proximal:
            return "eika" if does_end_in_glottal else "neika"
        else:
            return "uka" if does_end_in_glottal else "noka"

    def get_subject_suffix(self) -> str:
        if self == Proximity.proximal:
            return "ii"
        else:
            return "uu"

class Person(str, Enum):
    first = "first"
    second = "second"
    third = "third"

class Plurality(str, Enum):
    singular = "singular"
    dual = "dual"
    plural = "plural"

class Inclusivity(str, Enum):
    inclusive = "inclusive"
    exclusive = "exclusive"

class Tense(str, Enum):
    past = "past"
    present = "present"
    future = "future"

class Aspect(str, Enum):
    continuous = "continuous"
    simple = "simple"
    perfect = "perfect"

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class Pronoun(BaseModel):
    person: Person
    plurality: Plurality
    proximity: Proximity
    inclusivity: Inclusivity
    reflexive: bool

    def get_subject_pronoun(self) -> str:
        if self.person == Person.first:
            if self.plurality == Plurality.singular:
                return 'nüü'
            elif self.plurality == Plurality.dual:
                return 'taa'
            elif self.plurality == Plurality.plural:
                if self.inclusivity == Inclusivity.inclusive:
                    return 'taagwa'
                else:
                    return 'nüügwa'
        elif self.person == Person.second:
            if self.plurality == Plurality.singular:
                return 'üü'
            else:
                return 'üügwa'
        elif self.person == Person.third:
            if self.plurality == Plurality.singular:
                if self.proximity == Proximity.proximal:
                    return 'mahu'
                else:
                    return 'uhu'
            else:
                if self.proximity == Proximity.proximal:
                    return 'mahuw̃a'
                else:
                    return 'uhuw̃a'

        raise ValueError("Invalid pronoun configuration")

    def get_object_pronoun(self) -> str:
        if self.person == Person.first:
            if self.plurality == Plurality.singular:
                return 'i'
            elif self.plurality == Plurality.dual:
                return 'ta'
            elif self.plurality == Plurality.plural:
                if self.inclusivity == Inclusivity.inclusive:
                    return 'tei'
                else:
                    return 'ni'
        elif self.person == Person.second:
            if self.plurality == Plurality.singular:
                return 'ü'
            else:
                return 'üi'
        elif self.person == Person.third:
            if self.reflexive:
                return 'na'
            if self.plurality == Plurality.singular:
                if self.proximity == Proximity.proximal:
                    return 'a'
                else:
                    return 'u'
            else:
                if self.proximity == Proximity.proximal:
                    return 'ai'
                else:
                    return 'ui'

        raise ValueError("Invalid pronoun configuration")

class Verb(BaseModel):
    lemma: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in TRANSITIVE_VERBS + INTRANSITIVE_VERBS],
            'description': 'A verb lemma (transitive or intransitive)'
        }
    )
    tense: Tense
    aspect: Aspect
    
    @field_validator('lemma')
    @classmethod
    def validate_lemma(cls, v: str) -> str:
        if v not in TRANSITIVE_VERB_LOOKUP and v not in INTRANSITIVE_VERB_LOOKUP:
            raise ValueError(f"Invalid verb: {v}")
        return v

    def get_verb_suffix(self) -> str:
        if self.tense == Tense.past:
            if self.aspect == Aspect.perfect:
                return 'pü'
            elif self.aspect == Aspect.continuous:
                return 'ti'
            elif self.aspect == Aspect.simple:
                return 'ku'
        elif self.tense == Tense.present:
            if self.aspect == Aspect.perfect:
                return 'pü'
            elif self.aspect == Aspect.continuous:
                return 'ti'
            elif self.aspect == Aspect.simple:
                return 'dü'
        elif self.tense == Tense.future:
            return 'wei'

        raise ValueError("Invalid tense/aspect combination")

class Noun(BaseModel):
    head: str = Field(
        ...,
        json_schema_extra={
            'enum': [entry.english for entry in NOUNS],
            'description': 'A noun lemma'
        }
    )
    possessive_determiner: Optional[Pronoun] = None
    proximity: Proximity
    plurality: Plurality
    
    @field_validator('head')
    @classmethod
    def validate_head(cls, v: str) -> str:
        if v not in NOUN_LOOKUP:
            raise ValueError(f"Invalid noun: {v}")
        return v

class SubjectNoun(Noun):
    pass

class ObjectNoun(Noun):
    def get_matching_pronoun_prefix(self) -> str:
        return Pronoun(
            person=Person.third,
            plurality=self.plurality,
            proximity=self.proximity,
            inclusivity=Inclusivity.exclusive,
            reflexive=False
        ).get_object_pronoun()

class Sentence(BaseModel):
    subject: Union[SubjectNoun, Pronoun]
    verb: Verb
    object: Optional[Union[ObjectNoun, Pronoun]] = None

    def __str__(self) -> str:
        object_pronoun_prefix = None
        if isinstance(self.object, Pronoun):
            object_pronoun_prefix = self.object.get_object_pronoun()
        elif isinstance(self.object, ObjectNoun):
            object_pronoun_prefix = self.object.get_matching_pronoun_prefix()

        verb_stem = get_transitive_verb_paiute(self.verb.lemma) if self.object is not None else get_intransitive_verb_paiute(self.verb.lemma)
        verb_str = ""
        verb_suffix = self.verb.get_verb_suffix()
        if object_pronoun_prefix is None:
            verb_str = f"{verb_stem}-{verb_suffix}"
        else:
            verb_stem = to_lenis(verb_stem)
            verb_str = f"{object_pronoun_prefix}-{verb_stem}-{verb_suffix}"

        object_str = None
        if isinstance(self.object, ObjectNoun):
            if isinstance(self.object.head, Pronoun):
                object_str = None
            else:
                paiute_word = get_noun_paiute(self.object.head)
                does_end_in_glottal = paiute_word.endswith("'")
                object_suffix = self.object.proximity.get_object_suffix(does_end_in_glottal)
                object_str = f"{paiute_word}-{object_suffix}"

        subject_str = None
        if isinstance(self.subject, Pronoun):
            subject_str = self.subject.get_subject_pronoun()
        elif isinstance(self.subject, SubjectNoun):
            if isinstance(self.subject.head, Pronoun):
                subject_str = None
            else:
                paiute_word = get_noun_paiute(self.subject.head)
                subject_suffix = self.subject.proximity.get_subject_suffix()
                subject_str = f"{paiute_word}-{subject_suffix}"

        if object_str is None:
            return f"{verb_str} {subject_str}"
        else:
            return f"{subject_str} {object_str} {verb_str}"

    @classmethod
    def sample_iter(cls, n: int) -> Generator['Sentence', None, None]:
        """Generate n sample sentences (string representations)"""
        for _ in range(n):
            # Random subject
            if randint(0, 1) == 0:
                subject = Pronoun(
                    person=choice(list(Person)),
                    plurality=choice(list(Plurality)),
                    proximity=choice(list(Proximity)),
                    inclusivity=choice(list(Inclusivity)),
                    reflexive=False
                )
            else:
                subject = SubjectNoun(
                    head=choice(list(NOUN_LOOKUP.keys())),
                    proximity=choice(list(Proximity)),
                    plurality=choice(list(Plurality))
                )

            # Random verb
            verb_lemma = choice(list(TRANSITIVE_VERB_LOOKUP.keys()) + list(INTRANSITIVE_VERB_LOOKUP.keys()))
            verb = Verb(
                lemma=verb_lemma,
                tense=choice(list(Tense)),
                aspect=choice(list(Aspect))
            )

            # Random object for transitive verbs
            obj = None
            if verb_lemma in list(TRANSITIVE_VERB_LOOKUP.keys()):
                if randint(0, 1) == 0:
                    obj = ObjectNoun(
                        head=choice(list(NOUN_LOOKUP.keys())),
                        proximity=choice(list(Proximity)),
                        plurality=choice(list(Plurality))
                    )
                else:
                    obj = Pronoun(
                        person=choice(list(Person)),
                        plurality=choice(list(Plurality)),
                        proximity=choice(list(Proximity)),
                        inclusivity=choice(list(Inclusivity)),
                        reflexive=False
                    )

            yield cls(subject=subject, verb=verb, object=obj)

    @classmethod
    def sample(cls, n: int) -> List['Sentence']:
        """Generate n sample sentences (string representations)"""
        return list(cls.sample_iter(n))

class SentenceList(BaseModel):
    sentences: List[Sentence]

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

LENIS_MAP = {
    'p': 'b',
    't': 'd',
    'k': 'g',
    's': 'z',
    'm': 'w̃'
}

def to_lenis(word: str) -> str:
    """Convert a word to its lenis form"""
    first_letter = word[0]
    if first_letter in LENIS_MAP:
        return LENIS_MAP[first_letter] + word[1:]
    else:
        return word

# ============================================================================
# MAIN
# ============================================================================

def main():
    # Test serialization
    print("=" * 60)
    print("Testing serialization (should only contain English)")
    print("=" * 60)
    sentence = Sentence(
        subject=SubjectNoun(
            head="dog",
            proximity=Proximity.proximal,
            plurality=Plurality.singular
        ),
        verb=Verb(
            lemma="eat",
            tense=Tense.present,
            aspect=Aspect.simple
        ),
        object=ObjectNoun(
            head="rice",
            proximity=Proximity.distal,
            plurality=Plurality.singular
        )
    )

    json_output = sentence.model_dump_json(indent=2)
    print(json_output)

    print(Sentence.model_json_schema())

if __name__ == "__main__":
    main()
