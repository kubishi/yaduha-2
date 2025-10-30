import re
from typing import ClassVar, Generic, List, Type

from pydantic import Field

from yaduha import Sentence
from yaduha.tool import Tool
from yaduha.translator import Translator, Translation
from yaduha.tool.english_to_sentences import EnglishToSentencesTool, TSentenceType
from yaduha.tool.sentence_to_english import SentenceToEnglishTool
from yaduha.agent import Agent

# Rebuild models to resolve forward references
EnglishToSentencesTool.model_rebuild()
SentenceToEnglishTool.model_rebuild()

class PipelineTranslator(Translator, Generic[TSentenceType]):
    __exclude_parent_fields__ = ["tools"]
    
    name: ClassVar[str] = "pipeline_translator"
    description: ClassVar[str] = "Translate text using a pipeline of translators."
    
    agent: Agent
    SentenceType: Type[TSentenceType]

    def __call__(self, text: str) -> Translation:
        """Translate the text using a pipeline of translators.
        
        Args:
            text (str): The text to translate.
        Returns:
            Translation: The translation
        """
        translate_input_to_sentences = EnglishToSentencesTool(
            agent=self.agent,
            SentenceType=self.SentenceType
        )
        translate_sentence_to_english = SentenceToEnglishTool(agent=self.agent)

        def clean_text(s: str) -> str:
            s = s.strip()
            # add a period if it doesn't end with punctuation
            if not re.search(r'[.!?]$', s):
                s += '.'
            # capitalize the first letter
            s = s[0].upper() + s[1:]
            return s

        sentences = translate_input_to_sentences(text)
        targets = []
        back_translations = []
        for sentence in sentences:
            targets.append(clean_text(str(sentence)))
            back_translations.append(clean_text(translate_sentence_to_english(sentence)))

        return Translation(
            source=text,
            target=" ".join(targets),
            back_translation=" ".join(back_translations),
            prompt_tokens=0,
            completion_tokens=0,
            translation_time=0.0,
            back_translation_prompt_tokens=0,
            back_translation_completion_tokens=0,
            back_translation_time=0.0,
            metadata={}
        )
    
    def get_examples(self) -> List:
        return []