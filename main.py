import json
from pathlib import Path
from typing import List
from langchain.agents import create_agent
import argparse

from model_ovp import Sentence

import dotenv
dotenv.load_dotenv()


THISDIR = Path(__file__).parent.resolve()
EXAMPLEDIR = THISDIR / "data" / "examples_ovp_to_eng.json"

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

def translate_ovp_to_english(sentence: Sentence, model: str) -> str:
    agent = create_agent(
        model=model,
        system_prompt=(
            "You are a translator that transforms structured sentences into natural English. "
            "The sentences may be strange and unusual, but you must translate them as accurately as possible. "
        )
    )

    examples = get_examples()
    messages = []
    for example in examples:
        messages.append({
            "role": "user",
            "content": json.dumps(example['json'], ensure_ascii=False)
        })
        messages.append({
            "role": "assistant",
            "content": example['english']
        })

    messages.append({
        "role": "user",
        "content": json.dumps(sentence.model_dump_json(), ensure_ascii=False)
    })
    response = agent.invoke({"messages": messages})
    message = response['messages'][-1]
    return message.content


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
    parser_translate = subparsers.add_parser("translate", help="Translate sample sentences.")
    parser_translate.add_argument('-n', '--num', type=int, default=1, help="Number of sample sentences to translate.")

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
    elif args.command == "translate":
        for i, sentence in enumerate(Sentence.sample(args.num)):
            print(f"Paiute: {sentence}")
            translation = translate_ovp_to_english(sentence, model=args.model)
            print(f"English: {translation}")
            if i < args.num - 1:
                print()

if __name__ == "__main__":
    main()