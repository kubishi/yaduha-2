from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from yaduha.language.exceptions import LanguageNotFoundError, LanguageValidationError
from yaduha.language.language import Language

S = TypeVar("S", bound="Sentence")


class Sentence(BaseModel, ABC, Generic[S]):
    """Base class for all sentence types in Yaduha.

    All language packages must define sentence types that inherit from this class.
    """

    @abstractmethod
    def __str__(self) -> str:
        """Render this sentence in the target language."""
        pass

    def str_masked(self) -> str:
        """Render this sentence in the target language with out-of-vocabulary
        content words replaced by role-based placeholders (e.g. [NOUN], [VERB]).

        The default implementation returns the same string as ``__str__``.
        Language packages that emit ``[lemma]`` fallbacks for OOV vocab
        should override this to produce a cheat-proof surface form that
        hides the English lemma from downstream decoders.
        """
        return self.__str__()

    def masked_copy(self) -> tuple["Sentence", list[str]]:
        """Return ``(copy_with_OOV_fields_masked, masked_tokens)``.

        The returned copy has any vocabulary-constrained fields (e.g. noun
        heads, verb lemmas) whose values fall outside the language's
        vocabulary replaced with role-tagged sentinels like ``[NOUN]`` or
        ``[VERB]``. The second element lists the original OOV tokens in the
        order they were encountered.

        This is used by the evaluation pipeline's "comparator" arm and by
        the fine-tuning datagen to produce cheat-proof training pairs where
        the downstream decoder cannot read English lemmas directly from the
        structured JSON.

        The default implementation returns an unmasked deep copy and an
        empty token list. Language packages with vocabulary-constrained
        fields should override this on each Sentence subclass.
        """
        return self.model_copy(deep=True), []

    @classmethod
    @abstractmethod
    def get_examples(cls: type[S]) -> list[tuple[str, S]]:
        """Return example structured sentences and their English translations.

        Returns:
            List[Tuple[str, SentenceType]]: A list of tuples containing English
            translations and their corresponding structured sentences.
        """
        pass


class VocabEntry(BaseModel):
    """Vocabulary entry linking English and the target language."""

    model_config = ConfigDict(frozen=True)

    english: str
    target: str


__all__ = [
    "Sentence",
    "VocabEntry",
    "Language",
    "LanguageNotFoundError",
    "LanguageValidationError",
]
