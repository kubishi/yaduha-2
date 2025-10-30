from typing import TYPE_CHECKING, ClassVar, Generic, List, Type, TypeVar
from pydantic import create_model, BaseModel

from yaduha import Sentence
from yaduha.tool import Tool

if TYPE_CHECKING:
    from yaduha.agent import Agent

TSentenceType = TypeVar("TSentenceType", bound=Sentence)
class SentenceList(BaseModel, Generic[TSentenceType]):
    sentences: List[TSentenceType]

class EnglishToSentencesTool(Tool, Generic[TSentenceType]):
    agent: "Agent"
    name: ClassVar[str] = "english_to_sentences"
    description: ClassVar[str] = "Translate natural English into a structured sentence."
    SentenceType: Type[TSentenceType]

    def __call__(self, english: str) -> List[TSentenceType]:
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

        return response.sentences

    def get_examples(self) -> List:
        return []