from abc import abstractmethod
from typing import TYPE_CHECKING, List, ClassVar, Type, TypeVar, overload, Generic
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from yaduha.tool import Tool

ModelType = TypeVar("ModelType", bound=BaseModel)
TModel = TypeVar("TModel", bound=str)

class Agent(BaseModel, Generic[TModel]):
    model: TModel
    name: ClassVar[str] = Field(..., description="The name of the agent.")

    # --- Overload 1: response_format=None ---
    @overload
    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: None = None,
        tools: List["Tool"] | None = None,
    ) -> str: ...

    # --- Overload 2: response_format=Type[ModelType] ---
    @overload
    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: Type[ModelType],
        tools: List["Tool"] | None = None,
    ) -> ModelType: ...

    # --- Implementation ---
    @abstractmethod
    def get_response(
        self,
        messages: List[ChatCompletionMessageParam],
        response_format: None | Type[ModelType] = None,
        tools: List["Tool"] | None = None,
    ) -> ModelType | str:
        raise NotImplementedError
