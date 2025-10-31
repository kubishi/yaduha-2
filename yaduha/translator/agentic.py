from typing import ClassVar, Generic, Type, List
from pydantic import Field, BaseModel
import time

from yaduha.agent import Agent, AgentResponse, TAgentResponseContentType
from yaduha.translator import Translation, Translator
from yaduha.tool import Tool

from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam


class TranslationResponse(BaseModel):
    translation: str = Field(..., description="The translated text.")

class AgenticTranslator(Translator, Generic[TAgentResponseContentType]):
    name: ClassVar[str] = "agentic_translator"
    description: ClassVar[str] = "Translate text using an agentic approach."

    agent: Agent
    tools: List[Tool] | None = Field(
        None,
        description="A list of tools that the agent can use for translation.",
    )

    def _run(self, text: str) -> Translation:
        
        start_time = time.time()
        response = self.agent.get_response(
            messages=[
                {
                    "role": "system",
                    "content": "You are a translation agent. Use the provided tools to translate the given text accurately.",
                },
                {
                    "role": "user",
                    "content": f"Translate the following text:\n\n{text}",
                }
            ],
            response_format=TranslationResponse,
            tools=self.tools
        )
        end_time = time.time()

        translation = Translation(
            source=text,
            target=response.content.translation,
            translation_time=end_time - start_time,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            back_translation=None,
            metadata={}
        )

        return translation