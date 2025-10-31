from typing import TYPE_CHECKING, ClassVar, Generic, List, Type, TypeVar, Union, Tuple
from pydantic import create_model, BaseModel

from yaduha.language import Sentence
from yaduha.tool import Tool
from yaduha.agent import Agent, AgentResponse

TSentenceType = TypeVar("TSentenceType", bound=Sentence)
class SentenceList(BaseModel, Generic[TSentenceType]):
    sentences: List[TSentenceType]

class EnglishToSentencesTool(Tool, Generic[TSentenceType]):
    agent: "Agent"
    name: ClassVar[str] = "english_to_sentences"
    description: ClassVar[str] = "Translate natural English into a structured sentence."
    SentenceType: Type[TSentenceType] | Tuple[Type[Sentence], ...]

    def __call__(self, english: str) -> AgentResponse[SentenceList[TSentenceType]]:
        # Handle both single type and union of types
        if isinstance(self.SentenceType, tuple):
            # Create a discriminated union type for multiple sentence types
            if len(self.SentenceType) == 1:
                sentence_union = self.SentenceType[0]
            else:
                sentence_union = Union[tuple(self.SentenceType)]

            TargetSentenceList = create_model(
                "TargetSentenceList",
                sentences=(List[sentence_union], ...),
                __base__=BaseModel
            )
        else:
            # Single sentence type (backward compatible)
            TargetSentenceList = create_model(
                "TargetSentenceList",
                sentences=(List[self.SentenceType], ...),
                __base__=SentenceList[self.SentenceType]
            )

        response = self.agent.get_response(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a translator that transforms natural English sentences into structured sentences. "
                        "Given the output format, you may not be able to represent all the details of the input sentence, "
                        "but you must capture as much as meaning as possible. "
                    )
                },
                {
                    "role": "user",
                    "content": english
                }
            ],
            response_format=TargetSentenceList
        )

        return response
