import json
from pathlib import Path
from typing import List
from langchain.agents import create_agent

from model_ovp import Sentence

import dotenv
dotenv.load_dotenv()


THISDIR = Path(__file__).parent.resolve()
EXAMPLEDIR = THISDIR / "examples_ovp_to_eng.json"

def create_examples():
    examples = []
    while True:
        sentence = Sentence.sample(1)[0]
        print(sentence)
        translation = input("Enter English translation (or 's' to skip, 'q' to quit): ")
        if translation.lower() == 'q':
            break
        if translation.lower() == 's':
            continue
        example = {
            "json": sentence.model_dump_json(),
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
    

def main():
    # # Uncomment to create examples
    # create_examples()

    # Sample sentences and translate them
    sentences = Sentence.sample(1)
    for sentence in sentences:
        print(f"Paiute: {sentence}")
        translation = translate_ovp_to_english(sentence, model="gpt-4")
        print(f"English: {translation}")
        print()

if __name__ == "__main__":
    main()