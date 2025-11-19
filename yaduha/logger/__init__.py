from openai import project
from pydantic import BaseModel
from abc import abstractmethod, ABC
from typing import Any, Dict
import os
from dotenv import load_dotenv

import wandb

load_dotenv()

class Logger(BaseModel, ABC):
    @abstractmethod
    def log(self, data: Dict[str, Any]):
        pass

class WandbLogger(Logger):
    project_name: str
    config_items = None

    def start(self, project: str, config: Dict[str, Any]) -> None:
        self.project_name = project
        self.config_items = config

        self.run = wandb.init(
            project=self.project_name,
            config = self.config_items
        )
        
        return

    def log(self, data: Dict[str, Any]) -> None:        
        wandb.log(data)
        return

    def stop(self):
        self.run.finish()
        return
    

class PrintLogger(Logger):
    def log(self, data: Dict):
        print(data)
