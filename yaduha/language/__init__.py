from pydantic import BaseModel
from pydantic.dataclasses import dataclass
from typing import List, Tuple, TypeVar, Type
from abc import abstractmethod

# Define a TypeVar bounded by Sentence
SentenceType = TypeVar("SentenceType", bound="Sentence")

class Sentence(BaseModel):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_examples(cls: Type["SentenceType"]) -> List[Tuple[str, "SentenceType"]]:
        """Return example structured sentences and their English translations.
        
        Returns:
            List[Tuple[str, SentenceType]]: A list of tuples containing English translations and their corresponding structured sentences.
        """
        pass

@dataclass(frozen=True)
class VocabEntry:
    """Immutable vocabulary entry linking English and the target language"""
    english: str
    target: str
