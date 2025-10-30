

import json
from typing import TYPE_CHECKING, ClassVar, List
from yaduha import Sentence

from yaduha.tool import Tool

if TYPE_CHECKING:
    from yaduha.agent import Agent

class SentenceToEnglishTool(Tool):
    agent: "Agent"
    name: ClassVar[str] = "sentence_to_english"
    description: ClassVar[str] = "Translate a structured sentence into natural English."

    def __call__(self, sentence: Sentence) -> str:
        example_messages = []
        for english, example_sentence in sentence.get_examples():
            example_messages.append({
                "role": "user",
                "content": json.dumps(example_sentence.model_dump_json(), ensure_ascii=False)
            })
            example_messages.append({
                "role": "assistant",
                "content": english
            })

        response = self.agent.get_response(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a translator that transforms structured sentences into natural English. "
                        "The sentences may be strange and unusual, but you must translate them as accurately as possible. "
                    )
                },
                *example_messages,
                {
                    "role": "user",
                    "content": json.dumps(sentence.model_dump_json(), ensure_ascii=False)
                }
            ]
        )
        return response

    def get_examples(self) -> List:
        return []
