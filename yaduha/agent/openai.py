import time
import json
from typing import ClassVar, List, Literal, Type, overload
from openai import OpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import Field, BaseModel

from yaduha.agent import Agent, AgentResponse, TAgentResponseContentType
from yaduha.tool import Tool


class OpenAIAgent(Agent):
    model: Literal["gpt-4o", "gpt-4o-mini", "gpt-5"]
    name: ClassVar[str] = "openai_agent"
    api_key: str = Field(..., description="The OpenAI API key.", exclude=True)

    # overload: text
    @overload
    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: Type[str] = str,
        tools: List["Tool"] | None = None,
    ) -> AgentResponse: ...
    # overload: model
    @overload
    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: Type[TAgentResponseContentType],
        tools: List["Tool"] | None = None,
    ) -> AgentResponse: ...

    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: Type[BaseModel] | Type[str] = str,
        tools: List["Tool"] | None = None,
    ) -> AgentResponse:
        start_time = time.time()

        client = OpenAI(api_key=self.api_key)
        chat_tools = [tool.get_tool_call_schema() for tool in (tools or [])]
        tool_map = {tool.name: tool for tool in (tools or [])}

        while True:
            if response_format is str:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=chat_tools,
                )
                msg = json.loads(response.choices[0].message.model_dump_json())
                messages.append(msg)

                if not response.choices[0].message.tool_calls:
                    content = response.choices[0].message.content
                    if not content:
                        raise ValueError("No content in response")
                    return AgentResponse(
                        content=content,
                        response_time=time.time() - start_time,
                        prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                        completion_tokens=response.usage.completion_tokens if response.usage else 0,
                    )
            else:
                response = client.beta.chat.completions.parse(
                    model=self.model,
                    messages=messages,
                    tools=chat_tools,
                    response_format=response_format,
                )
                msg = json.loads(response.choices[0].message.model_dump_json())
                messages.append(msg)

                if not response.choices[0].message.tool_calls:
                    parsed = response.choices[0].message.parsed
                    if not parsed:
                        raise ValueError("No content in response")
                    return AgentResponse(
                        content=parsed,
                        response_time=time.time() - start_time,
                        prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
                        completion_tokens=response.usage.completion_tokens if response.usage else 0,
                    )

            for tool_call in response.choices[0].message.tool_calls or []:
                if tool_call.type == "function":
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    result = tool_map[name](**args)
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": str(result),
                        }
                    )
