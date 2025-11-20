from re import A
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from abc import abstractmethod, ABC
from typing import Any, Dict, Mapping, Optional
from dotenv import load_dotenv

import wandb

load_dotenv()

class Logger(BaseModel, ABC):
    @abstractmethod
    def log(self, data: Dict[str, Any]):
        pass

class WandbLogger(Logger):
    model_config = ConfigDict(populate_by_name=True)

    project_name: str = Field(..., description="The W&B project name.", alias="project")
    name: str
    config_items: Dict[str, Any] = Field(default_factory=dict, description="The W&B config items.", alias="config")
    
    _run: wandb.Run | None = PrivateAttr(default=None)

    def model_post_init(self, __context: Any) -> None:
        """
        Called by Pydantic *after* the model has been initialized and validated.
        This is the right place for side effects like wandb.init().
        """
        self._run = wandb.init(
            project=self.project_name,
            config=self.config_items,
            name=self.name,
        )


    def log(self, data: Mapping[str, Any], **kwargs: Any) -> None:
        """
        Log a dictionary of metrics to this W&B run.

        Args:
            data: Metrics to log.
            step: Optional global step (epoch, iteration, etc.).
            **kwargs: Forwarded to Run.log (e.g., commit=False).
        """
        if self._run is None:
            raise RuntimeError("Cannot log: W&B run is not active.")

        self._run.log(dict(data), **kwargs)

    def stop(self) -> None:
        """Finish the W&B run if it is still active."""
        if self._run is not None:
            self._run.finish()
            self._run = None

class PrintLogger(Logger):
    def log(self, data: Dict[str, Any]):
        print(data)
