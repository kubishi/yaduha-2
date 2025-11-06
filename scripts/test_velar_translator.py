"""
Test script for Velar language translator.

This demonstrates the Velar constructed language with its unique features:
- VSO word order
- Gendered pronouns
- Evidentiality markers
- Animacy distinctions
"""

import os
from dotenv import load_dotenv

from yaduha.agent.openai import OpenAIAgent
from yaduha.translator.pipeline import PipelineTranslator
from yaduha.language.velar import (
    VerbSubjectSentence,
    VerbSubjectObjectSentence,
)

# Load environment variables
load_dotenv()


def main():
    agent = OpenAIAgent(
        model="gpt-4o-mini",
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0.0,
    )

    translator = PipelineTranslator(
        agent=agent,
        SentenceType=(VerbSubjectSentence, VerbSubjectObjectSentence),
    )

    # Test sentences
    test_sentences = [
        "The dog sleeps.",
        # "I see you.",
        # "The cat eats the fish.",
        # "She was dancing.",
        # "He reads the book.",
        # "They run in the forest.",
    ]

    for i, english_sentence in enumerate(test_sentences, 1):
        print(f"Test {i}: {english_sentence}")
        print("-" * 70)

        result = translator(english_sentence)

        print(f"English:         {result.source}")
        print(f"Velar:           {result.target}")
        if result.back_translation:
            print(f"Back-translation: {result.back_translation.source}")
        print(f"Tokens used:     {result.prompt_tokens + result.completion_tokens}")
        print(f"Time:            {result.translation_time:.2f}s")
        print()

        print("=" * 70)
        print()


if __name__ == "__main__":
    main()
