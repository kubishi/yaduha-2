"""Language class for wrapping sentence types and metadata."""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


class Language:
    """Container for a language's sentence types and metadata.

    Attributes:
        code: ISO 639-3 language code (e.g., 'ovp')
        name: Human-readable language name (e.g., 'Owens Valley Paiute')
        sentence_types: Tuple of Sentence subclasses supported by this language
    """

    def __init__(
        self,
        code: str,
        name: str,
        sentence_types: tuple[type[Any], ...],
        get_instructions: Callable[[], str] | None = None,
        get_examples: Callable[[], list[tuple[str, list[Any]]]] | None = None,
    ) -> None:
        """Initialize a Language instance.

        Args:
            code: Language code identifier
            name: Human-readable language name
            sentence_types: Tuple of Sentence subclasses
            get_instructions: Optional callable that returns natural language
                grammar instructions (vocabulary, rules, examples) suitable
                for use as an LLM system prompt.
            get_examples: Optional callable returning few-shot examples as
                (english, [sentence, ...]) pairs. One English input maps to a
                list of sentences (of possibly different types), so unlike
                Sentence.get_examples() an example may decompose one input into
                several. Omitted, get_examples() falls back to the per-type
                singles from examples_from_sentence_types().

        Raises:
            ValueError: If code or name is empty, or sentence_types is empty
            TypeError: If sentence_types contains non-Sentence types
        """
        # Import here to avoid circular imports
        from yaduha.language import Sentence

        if not code or not isinstance(code, str):
            raise ValueError("code must be a non-empty string")
        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")
        if not sentence_types:
            raise ValueError("sentence_types must not be empty")

        for sentence_type in sentence_types:
            if not (isinstance(sentence_type, type) and issubclass(sentence_type, Sentence)):
                raise TypeError(f"{sentence_type} is not a Sentence subclass")

        self.code: str = code
        self.name: str = name
        self.sentence_types: tuple[type[Sentence], ...] = sentence_types
        self._get_instructions = get_instructions
        self._get_examples = get_examples

    @staticmethod
    def examples_from_sentence_types(
        sentence_types: tuple[type[Any], ...],
    ) -> list[tuple[str, list[Any]]]:
        """Each type's Sentence.get_examples(), each wrapped as a one-element list.

        The default for get_examples(), and a building block languages reuse when
        they add their own multi-sentence examples.
        """
        examples: list[tuple[str, list[Any]]] = []
        for sentence_type in sentence_types:
            for english, sentence in sentence_type.get_examples():
                examples.append((english, [sentence]))
        return examples

    def get_examples(self) -> list[tuple[str, list[Any]]]:
        """Few-shot examples as (english, [sentence, ...]) pairs.

        Falls back to the per-type singles when no get_examples callable was given.
        """
        if self._get_examples:
            return self._get_examples()
        return self.examples_from_sentence_types(self.sentence_types)

    def get_instructions(self) -> str | None:
        """Return natural language grammar instructions for this language.

        Language packages should provide a callable via the get_instructions
        constructor parameter that returns vocabulary, grammar rules, and
        examples as a text prompt suitable for an LLM system message.

        Returns:
            Instructions string, or None if not provided.
        """
        if self._get_instructions:
            return self._get_instructions()
        return None

    def __repr__(self) -> str:
        """Return a string representation of the Language."""
        return f"Language(code={self.code!r}, types={len(self.sentence_types)})"

    def __eq__(self, other: object) -> bool:
        """Check equality based on code."""
        if not isinstance(other, Language):
            return NotImplemented
        return self.code == other.code

    def __hash__(self) -> int:
        """Make Language hashable."""
        return hash(self.code)
