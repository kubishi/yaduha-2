import json
from pathlib import Path
from typing import List
from openai import OpenAI
import argparse
import dotenv
import os

from model_ovp import Sentence, SentenceList

dotenv.load_dotenv()


THISDIR = Path(__file__).parent.resolve()
EXAMPLEDIR = THISDIR / "data" / "examples_ovp_to_eng.json"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_examples():
    examples = []
    while True:
        sentence = Sentence.sample(1)[0]
        translation = input("Enter English translation (or 's' to skip, 'q' to quit): ")
        if translation.lower() == 'q':
            break
        if translation.lower() == 's':
            continue
        example = {
            "json": json.loads(sentence.model_dump_json()),
            "paiute": str(sentence),
            "english": translation
        }
        examples.append(example)
    
    EXAMPLEDIR.parent.mkdir(parents=True, exist_ok=True)
    EXAMPLEDIR.write_text(json.dumps(examples, indent=2, ensure_ascii=False))

def get_examples() -> List[dict]:
    examples_text = EXAMPLEDIR.read_text()
    examples = json.loads(examples_text)
    return examples

def translate_sentence_to_english(sentence: Sentence, model: str) -> str:
    examples = get_examples()
    example_messages = []
    for example in examples:
        example_messages.append({
            "role": "user",
            "content": json.dumps(example['json'], ensure_ascii=False)
        })
        example_messages.append({
            "role": "assistant",
            "content": example['english']
        })

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a translator that transforms structured sentences into natural English. "
                    "The sentences may be strange and unusual, but you must translate them as accurately as possible. "
                )
            },
            *example_messages,
            {
                "role": "user",
                "content": json.dumps(sentence.model_dump_json(), ensure_ascii=False)
            }
        ],
        temperature=0.0
    )
    if not response.choices[0].message.content:
        raise ValueError("No content in response")
    return response.choices[0].message.content.strip()

def translate_sentence_to_ovp(sentence: Sentence) -> str:
    return str(sentence)

def translate_input_to_sentences(input_text: str, model: str) -> SentenceList:
    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a translator that transforms natural language sentences into structured sentences. "
                    "Given the output format, you may not be able to represent all the details of the input sentence, "
                    "but you must capture as much as meaning as possible. "
                )
            },
            {
                "role": "user",
                "content": input_text
            }
        ],
        temperature=0.0,
        response_format=SentenceList
    )
    sentences = response.choices[0].message.parsed
    if not sentences:
        raise ValueError("No sentences parsed from response")
    return sentences


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Translate OVP sentences to English.")
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4",
        help="The language model to use for translation."
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    parser_examples = subparsers.add_parser("create-examples", help="Create example translations.")
    parser_examples.add_argument('-f', '--force', action='store_true', help="Force re-creation of examples.")

    parser_ovp_to_eng = subparsers.add_parser("ovp-to-eng", help="Translate sample sentences.")
    parser_ovp_to_eng.add_argument('-n', '--num', type=int, default=1, help="Number of sample sentences to translate.")
    parser_ovp_to_eng.add_argument('-m', '--model', type=str, default="gpt-4o", help="The language model to use for translation.")

    parser_eng_to_struct = subparsers.add_parser("eng-to-struct", help="Translate English sentences to structured format.")
    parser_eng_to_struct.add_argument('input', type=str, help="The English sentence to translate.")
    parser_eng_to_struct.add_argument('-m', '--model', type=str, default="gpt-4o", help="The language model to use for translation.")

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    if getattr(args, 'command', None) is None:
        parser.print_help()
        return

    if args.command == "create-examples":
        if args.force or not EXAMPLEDIR.exists():
            create_examples()
        else:
            print(f"Examples file {EXAMPLEDIR} already exists. Use --force to recreate.")
    elif args.command == "ovp-to-eng":
        for i, sentence in enumerate(Sentence.sample(args.num)):
            print(f"Paiute: {sentence}")
            translation = translate_sentence_to_english(sentence, model=args.model)
            print(f"English: {translation}")
            if i < args.num - 1:
                print()
    elif args.command == "eng-to-struct":
        sentence_list = translate_input_to_sentences(args.input, model=args.model)
        for sentence in sentence_list.sentences:
            print(f"Paiute: {translate_sentence_to_ovp(sentence)}")
            print(f"English: {translate_sentence_to_english(sentence, model=args.model)}")

if __name__ == "__main__":
    main()