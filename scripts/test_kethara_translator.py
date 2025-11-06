"""
Test script for Kethara language translator.

This demonstrates the Kethara agglutinative language with its unique features:
- SOV word order
- Noun classes (human/animal/plant/object/abstract)
- Vowel harmony
- Case system (directional/spatial)
- Suffix stacking on verbs
- Politeness marked on verbs
"""

import os
from dotenv import load_dotenv

from yaduha.agent.openai import OpenAIAgent
from yaduha.translator.pipeline import PipelineTranslator
from yaduha.language.kethara import (
    SubjectVerbSentence,
    SubjectObjectVerbSentence,
)

# Load environment variables
load_dotenv()


def main():
    """Test Kethara language translation"""
    print("=" * 70)
    print("KETHARA LANGUAGE TRANSLATOR TEST")
    print("=" * 70)
    print()
    print("Kethara Features:")
    print("  - SOV (Subject-Object-Verb) word order (like Turkish/Japanese)")
    print("  - Noun classes: human/animal/plant/object/abstract")
    print("  - Vowel harmony (suffix vowels adapt to root)")
    print("  - Agglutinative morphology (suffix stacking)")
    print("  - Directional case system (spatial relationships)")
    print("  - Politeness marked on verbs, not pronouns")
    print("  - No articles (no 'the' or 'a')")
    print()
    print("=" * 70)
    print()

    # Create agent
    agent = OpenAIAgent(
        model="gpt-4o-mini",
        api_key=os.environ["OPENAI_API_KEY"],
        temperature=0.0,
    )

    # Create translator with both sentence types
    translator = PipelineTranslator(
        agent=agent,
        SentenceType=(SubjectVerbSentence, SubjectObjectVerbSentence),
    )

    # Test sentences
    test_sentences = [
        "The dog sleeps.",
        "I see you.",
        "The cat eats the fish.",
        "The birds are singing.",
        "The woman loves the man.",
    ]

    for i, english_sentence in enumerate(test_sentences, 1):
        print(f"Test {i}: {english_sentence}")
        print("-" * 70)

        try:
            result = translator(english_sentence)

            print(f"English:          {result.source}")
            print(f"Kethara:          {result.target}")
            if result.back_translation:
                print(f"Back-translation: {result.back_translation.source}")
                print()
            print(f"Tokens used:      {result.prompt_tokens + result.completion_tokens}")
            print(f"Time:             {result.translation_time:.2f}s")
            print()

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            print()

        print("=" * 70)
        print()


if __name__ == "__main__":
    main()
