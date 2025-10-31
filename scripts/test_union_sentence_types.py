"""Test script for union of sentence types in PipelineTranslator"""
from yaduha.translator.pipeline import PipelineTranslator
from yaduha.agent.openai import OpenAIAgent
from yaduha.language.ovp import SubjectVerbSentence, SubjectVerbObjectSentence

from dotenv import load_dotenv
import os

load_dotenv()

def main():
    # Test with a union of sentence types
    translator = PipelineTranslator(
        agent=OpenAIAgent(
            model="gpt-4o-mini",
            api_key=os.environ["OPENAI_API_KEY"]
        ),
        SentenceType=(SubjectVerbSentence, SubjectVerbObjectSentence)
    )

    # Test sentences that could be either SV or SVO
    test_cases = [
        "The dog runs.",  # Should use SubjectVerbSentence
        "The cat eats fish.",  # Should use SubjectVerbObjectSentence
        "I sleep.",  # Should use SubjectVerbSentence
        "You see the mountain.",  # Should use SubjectVerbObjectSentence
    ]

    print("Testing PipelineTranslator with union of sentence types:\n")
    for test in test_cases:
        print(f"Input: {test}")
        result = translator(test)
        print(f"Output: {result.target}")
        print(f"Back-translation: {result.back_translation.source}")
        print(f"Tokens: {result.prompt_tokens} prompt, {result.completion_tokens} completion")
        print(f"Time: {result.translation_time:.2f}s\n")

if __name__ == "__main__":
    main()
