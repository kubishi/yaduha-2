from typing import List, Literal, Type, ClassVar, overload
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
import json
from pydantic import Field

from yaduha.agent import Agent, ModelType
from yaduha.tool import Tool


class OpenAIAgent(Agent):
    model: Literal["gpt-4o", "gpt-4o-mini", "gpt-5"]
    name: ClassVar[str] = "openai_agent"
    api_key: str = Field(..., description="The OpenAI API key.", exclude=True)

    @overload
    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: None = None,
        tools: List["Tool"] | None = None,
    ) -> str: ...

    @overload
    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: Type[ModelType],
        tools: List["Tool"] | None = None,
    ) -> ModelType: ...

    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: None | Type[ModelType] = None,
        tools: List["Tool"] | None = None,
    ) -> ModelType | str:
        client = OpenAI()

        chat_tools = [
            tool.get_tool_call_schema() for tool in (tools or [])
        ]
        tool_map = {tool.name: tool for tool in (tools or [])}

        while True:
            if response_format is None:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=chat_tools,
                )
                messages.append(
                    json.loads(
                        response.choices[0].message.model_dump_json()
                    )
                )
                if not response.choices[0].message.tool_calls:
                    if response.choices[0].message.content:
                        return response.choices[0].message.content
                    else:
                        raise ValueError("No content in response")
            else:
                response = client.beta.chat.completions.parse(
                    model=self.model,
                    messages=messages,
                    response_format=response_format
                )
                messages.append(
                    json.loads(
                        response.choices[0].message.model_dump_json()
                    )
                )
                if not response.choices[0].message.tool_calls:
                    if response.choices[0].message.parsed:
                        return response.choices[0].message.parsed
                    else:
                        raise ValueError("No content in response")
        
            for tool_call in response.choices[0].message.tool_calls:
                if tool_call.type == "function":
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)

                    result = tool_map[name](**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })

    