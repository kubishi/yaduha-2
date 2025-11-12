import os
from dotenv import load_dotenv
import wandb
import weave

from yaduha import agent
from yaduha.agent.openai import OpenAIAgent
from yaduha.translator.pipeline import PipelineTranslator
from yaduha.language.ovp import SubjectVerbSentence, SubjectVerbObjectSentence

load_dotenv()

def main():
    # Start a new wandb run to track this script.
    run = wandb.init(
        # Set the wandb project where this run will be logged.
        project="kubishi",
        # Track hyperparameters and run metadata.
        config={
            "app": "yaduha",
        },
    )

    translator = PipelineTranslator(
        agent=OpenAIAgent(
            model="gpt-4o-mini",
            api_key=os.environ["OPENAI_API_KEY"]
        ),
        SentenceType=(SubjectVerbObjectSentence, SubjectVerbSentence)
    )

    translation = translator("The dog is sleeping.")
    run.log({"chat/response": translation.model_dump_json()})
    print("uploading data", translation)
    # Finish the run and upload any remaining data.
    run.finish()

if __name__ == "__main__":
    main()