import re
import time
from typing import ClassVar, Generic, Type

from yaduha.translator import Translator, Translation, BackTranslation
from yaduha.tool.english_to_sentences import EnglishToSentencesTool, TSentenceType
from yaduha.tool.sentence_to_english import SentenceToEnglishTool
from yaduha.agent import Agent

class PipelineTranslator(Translator, Generic[TSentenceType]):    
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
        start_time = time.time()
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

        sentences_response = translate_input_to_sentences(text)
        end_time = time.time()

        targets = []
        back_translations = []
        prompt_tokens = sentences_response.prompt_tokens
        completion_tokens = sentences_response.completion_tokens
        prompt_tokens_bt = 0
        completion_tokens_bt = 0

        start_time_bt = time.time()
        for sentence in sentences_response.content.sentences:
            targets.append(clean_text(str(sentence)))
            back_translation = translate_sentence_to_english(sentence)
            back_translations.append(clean_text(back_translation.content))
            prompt_tokens_bt += back_translation.prompt_tokens
            completion_tokens_bt += back_translation.completion_tokens
        end_time_bt = time.time()

        return Translation(
            source=text,
            target=" ".join(targets),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            translation_time=end_time - start_time,
            back_translation=BackTranslation(
                source=" ".join(back_translations),
                target=" ".join(targets),
                prompt_tokens=prompt_tokens_bt,
                completion_tokens=completion_tokens_bt,
                translation_time=end_time_bt - start_time_bt
            ),
        )
