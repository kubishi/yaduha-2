import os
from dotenv import load_dotenv
from openai import project

from yaduha import agent
from yaduha.agent.openai import OpenAIAgent
from yaduha.translator.pipeline import PipelineTranslator
from yaduha.language.ovp import SubjectVerbSentence, SubjectVerbObjectSentence
from yaduha.logger import PrintLogger, WandbLogger

import weave

load_dotenv()

def main():


    logger = WandbLogger(
        project="kubishi",
        name="test3",
    )

    translator = PipelineTranslator(
        agent=OpenAIAgent(
            model="gpt-4o-mini",
            api_key=os.environ["OPENAI_API_KEY"]
        ),
        SentenceType=(SubjectVerbObjectSentence, SubjectVerbSentence),
        logger = logger
    )

    translation = translator("The dog is sleeping.")
    
    logger.stop()
if __name__ == "__main__":
    main()