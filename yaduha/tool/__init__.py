import json
from pydantic import BaseModel, create_model
from typing import Any, ClassVar, Dict, List
from abc import abstractmethod
import random
import string
import inspect

from openai.types.chat.chat_completion_function_tool_param import ChatCompletionFunctionToolParam
from openai.types.shared_params import FunctionDefinition

def _add_additional_properties_false(schema: Dict | List) -> None:
    """Recursively add 'additionalProperties': False to all object schemas."""
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            schema["additionalProperties"] = False
        for value in schema.values():
            _add_additional_properties_false(value)
    elif isinstance(schema, list):
        for item in schema:
            _add_additional_properties_false(item)

class Tool(BaseModel):
    name: ClassVar[str]
    description: ClassVar[str]

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.name.isidentifier():
            raise ValueError(f"Tool name '{self.name}' is not a valid Python identifier.")
        if self.name in {"print", "input", "len", "str", "int", "float", "list", "dict", "set", "tuple"}:
            raise ValueError(f"Tool name '{self.name}' is a reserved Python keyword or built-in function name.")

    def __call__(self, *args, **kwargs) -> Any:
        """Call the tool with the given arguments.
        
        Automatically parses BaseModel arguments.
        """
        signature = inspect.signature(self._run)
        bound_args = signature.bind(*args, **kwargs)
        for name, value in bound_args.arguments.items():
            param = signature.parameters[name]
            if issubclass(param.annotation, BaseModel) and not isinstance(value, param.annotation):
                bound_args.arguments[name] = param.annotation(**value)
        return self._run(*bound_args.args, **bound_args.kwargs)

    @abstractmethod
    def _run(self, *args, **kwargs) -> Any:
        pass

    @staticmethod
    def get_random_tool_call_id():
        """Generate a random tool call id of the form call_aSENunZCF31ob7zV89clvL4n"""
        return "call_" + ''.join(random.choices(string.ascii_letters + string.digits, k=24))

    def get_tool_call_schema(self) -> ChatCompletionFunctionToolParam:
        signature = inspect.signature(self._run)
        properties = {}
        for name, param in signature.parameters.items():
            if name == "self":
                continue
            annotation = param.annotation
            if annotation == inspect._empty:
                annotation = Any
            default = param.default
            if default == inspect._empty:
                default = ...
            properties[name] = (annotation, default)

        model = create_model(self.name, **properties)
        schema = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": model.model_json_schema(),
                "strict": True,
            }
        }
        _add_additional_properties_false(schema["function"]["parameters"])
        return ChatCompletionFunctionToolParam(**schema)
    
    def get_tool_call_output_schema(self) -> Dict:
        signature = inspect.signature(self._run)
        return_type = signature.return_annotation
        if return_type == inspect._empty:
            return_type = Any
        model = create_model(f"{self.name}_output", output=(return_type, ...))
        schema = model.model_json_schema()
        return schema
    

