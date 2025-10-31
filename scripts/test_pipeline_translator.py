from yaduha.translator.pipeline import PipelineTranslator
from yaduha.agent.openai import OpenAIAgent
from yaduha.language.ovp import SubjectVerbSentence, SubjectVerbObjectSentence

from dotenv import load_dotenv
import os

load_dotenv()

def main():
    translator = PipelineTranslator(
        agent=OpenAIAgent(
            model="gpt-4o-mini",
            api_key=os.environ["OPENAI_API_KEY"]
        ),
        SentenceType=(SubjectVerbObjectSentence, SubjectVerbSentence)
    )

    print(translator.get_examples())
    print(translator("The dog is sitting at the lakeside, drinking some water."))

if __name__ == "__main__":
    main()

