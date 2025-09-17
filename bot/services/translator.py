import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any, Tuple
from langdetect import detect, LangDetectException
import openai
from config import config
import logging

logger = logging.getLogger(__name__)

class TranslatorService:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of the text"""
        try:
            lang = detect(text)
            return lang
        except LangDetectException:
            return None

    async def translate_with_yandex(self, text: str, target_lang: str,
                                   source_lang: str = None) -> Optional[str]:
        """Translate text using Yandex Translate API"""
        if not config.YANDEX_API_KEY:
            return None

        url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
        headers = {
            "Authorization": f"Api-Key {config.YANDEX_API_KEY}",
            "Content-Type": "application/json"
        }

        if not source_lang:
            source_lang = await self.detect_language(text)
            if not source_lang:
                return None

        data = {
            "texts": [text],
            "targetLanguageCode": target_lang,
            "sourceLanguageCode": source_lang
        }

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["translations"][0]["text"]
                else:
                    logger.error(f"Yandex Translate error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Yandex Translate exception: {e}")
            return None

    async def translate_with_deepl(self, text: str, target_lang: str,
                                  source_lang: str = None) -> Optional[str]:
        """Translate text using DeepL API"""
        if not config.DEEPL_API_KEY:
            return None

        url = "https://api-free.deepl.com/v2/translate"
        headers = {
            "Authorization": f"DeepL-Auth-Key {config.DEEPL_API_KEY}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # DeepL uses different language codes
        deepl_lang_map = {
            'en': 'EN-US',
            'ru': 'RU',
            'de': 'DE',
            'fr': 'FR',
            'es': 'ES',
            'it': 'IT',
            'pt': 'PT-BR',
            'nl': 'NL',
            'pl': 'PL',
            'ja': 'JA',
            'zh': 'ZH'
        }

        target_lang = deepl_lang_map.get(target_lang, target_lang.upper())

        data = {
            "text": text,
            "target_lang": target_lang
        }

        if source_lang:
            source_lang = deepl_lang_map.get(source_lang, source_lang.upper())
            data["source_lang"] = source_lang

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.post(url, headers=headers, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["translations"][0]["text"]
                else:
                    logger.error(f"DeepL error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"DeepL exception: {e}")
            return None

    async def translate_with_google(self, text: str, target_lang: str,
                                   source_lang: str = None) -> Optional[str]:
        """Translate text using Google Translate (via googletrans-py library)"""
        try:
            try:
                from googletrans_py import Translator
            except ImportError:
                from googletrans import Translator

            translator = Translator()

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: translator.translate(text, dest=target_lang, src=source_lang or 'auto')
            )

            # Check if we have a result
            if hasattr(result, 'text'):
                return result.text
            elif isinstance(result, str):
                return result
            else:
                logger.error(f"Unexpected Google Translate result format: {type(result)}")
                return None

        except Exception as e:
            logger.error(f"Google Translate exception: {e}")
            logger.error(f"Trying to translate '{text}' from {source_lang} to {target_lang}")
            return None

    async def translate_with_openai_fallback(self, text: str, target_lang: str,
                                           source_lang: str = None) -> Optional[str]:
        """Simple translation using OpenAI as fallback when other services fail"""
        if not config.OPENAI_API_KEY:
            return None

        try:
            # Language mapping for better results
            lang_names = {
                'en': 'English',
                'ru': 'Russian',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
                'it': 'Italian',
                'pt': 'Portuguese',
                'ja': 'Japanese',
                'zh': 'Chinese',
                'ko': 'Korean',
                'ar': 'Arabic',
                'hi': 'Hindi',
                'tr': 'Turkish',
                'pl': 'Polish',
                'nl': 'Dutch',
                'sv': 'Swedish',
                'da': 'Danish',
                'no': 'Norwegian',
                'fi': 'Finnish',
                'cs': 'Czech',
                'hu': 'Hungarian',
                'ro': 'Romanian',
                'uk': 'Ukrainian',
                'he': 'Hebrew',
                'th': 'Thai',
                'vi': 'Vietnamese'
            }

            target_lang_name = lang_names.get(target_lang, target_lang)
            source_lang_name = lang_names.get(source_lang, source_lang) if source_lang else "auto-detect"

            response = await self.openai_client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a professional translator. Translate the given text to {target_lang_name}. Return only the translation, no explanations."
                    },
                    {
                        "role": "user",
                        "content": f"Translate this text to {target_lang_name}: {text}"
                    }
                ],
                temperature=0.3,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"OpenAI fallback translation error: {e}")
            return None

    async def enhance_with_gpt(self, original_text: str, translated_text: str,
                              target_lang: str, style: str = 'informal',
                              explain_grammar: bool = False) -> Dict[str, Any]:
        """Enhance translation using GPT for natural language and style"""
        style_prompts = {
            'informal': 'casual and friendly, as if talking to a friend',
            'formal': 'formal and polite, suitable for official documents',
            'business': 'professional and business-like',
            'travel': 'simple and clear, suitable for tourists',
            'academic': 'academic and scholarly'
        }

        style_description = style_prompts.get(style, style_prompts['informal'])

        system_prompt = f"""You are a professional translator and language expert specializing in accurate, contextual translation enhancement.

CRITICAL RULES:
1. PRESERVE the original meaning and accuracy of the basic translation
2. DO NOT change the core message or interpretation
3. Focus on style adaptation and providing synonyms, NOT reinterpretation
4. Target style: {style_description}"""

        # Get user's interface language for explanations
        from bot.database import db
        user_info = await db.get_user(user_id) if user_id else {}
        interface_lang = user_info.get('interface_language', 'ru')

        # Language-specific explanation text
        explanation_languages = {
            'ru': {
                'instruction': 'Объясните на русском языке:',
                'style_text': 'Стилистически улучшенная версия, которая сохраняет тот же смысл, но соответствует стилю',
                'synonyms_text': '2-3 синонимических альтернативы для ключевых слов/фраз (сохраняя тот же смысл)',
                'explanation_text': 'Краткое объяснение выбора слов и культурных/контекстных заметок',
                'reasoning_text': 'Почему эта улучшенная версия более естественна, оставаясь верной оригиналу',
                'grammar_text': 'Грамматическое объяснение для изучающих язык'
            },
            'en': {
                'instruction': 'Explain in English:',
                'style_text': 'A stylistically improved version that maintains the same meaning but fits the style',
                'synonyms_text': '2-3 synonym alternatives for key words/phrases (maintain same meaning)',
                'explanation_text': 'Brief explanation of word choices and any cultural/contextual notes',
                'reasoning_text': 'Why this enhanced version is more natural while staying faithful to the original',
                'grammar_text': 'Grammar explanation for language learners'
            }
        }

        # Default to English if interface language not supported
        lang_config = explanation_languages.get(interface_lang, explanation_languages['en'])

        user_prompt = f"""Original text ({await self.detect_language(original_text) or 'unknown'}): {original_text}
Basic translation ({target_lang}): {translated_text}

Your task: Enhance this accurate translation while preserving its meaning exactly.

{lang_config['instruction']}
1. {lang_config['style_text']} {style_description}
2. {lang_config['synonyms_text']}
3. {lang_config['explanation_text']}
4. {lang_config['reasoning_text']}

IMPORTANT: Do not change the translation's meaning or add interpretations not present in the original text."""

        if explain_grammar:
            user_prompt += f"\n5. {lang_config['grammar_text']}"

        try:
            response = await self.openai_client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            content = response.choices[0].message.content

            # Parse the response with improved parsing for new format
            lines = content.split('\n')
            result = {
                'enhanced_translation': translated_text,
                'alternatives': [],
                'explanation': '',
                'grammar': '',
                'synonyms': []
            }

            current_section = None
            for line in lines:
                line = line.strip()
                if line.startswith('1.') and 'improved' in line.lower():
                    # Extract the enhanced translation
                    enhanced_text = line[2:].strip()
                    # Remove any prefixes like "Improved version:"
                    if ':' in enhanced_text:
                        enhanced_text = enhanced_text.split(':', 1)[1].strip()
                    result['enhanced_translation'] = enhanced_text
                elif line.startswith('2.') and 'synonym' in line.lower():
                    current_section = 'synonyms'
                elif line.startswith('3.') and 'explanation' in line.lower():
                    current_section = 'explanation'
                elif line.startswith('4.') and ('natural' in line.lower() or 'why' in line.lower()):
                    current_section = 'explanation'
                elif explain_grammar and 'grammar' in line.lower():
                    current_section = 'grammar'
                elif line and current_section:
                    if current_section == 'synonyms':
                        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                            synonym_text = line[1:].strip()
                            result['alternatives'].append(synonym_text)
                    elif current_section == 'alternatives':
                        if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                            result['alternatives'].append(line[1:].strip())
                    elif current_section == 'explanation':
                        result['explanation'] += line + ' '
                    elif current_section == 'grammar':
                        result['grammar'] += line + ' '

            return result

        except Exception as e:
            logger.error(f"GPT enhancement error: {e}")
            return {
                'enhanced_translation': translated_text,
                'alternatives': [],
                'explanation': '',
                'grammar': ''
            }

    async def translate(self, text: str, target_lang: str, source_lang: str = None,
                       style: str = 'informal', enhance: bool = True) -> Tuple[str, Dict[str, Any]]:
        """Main translation method with enhancement"""
        logger.info(f"Translation request: text='{text[:30]}...', target_lang={target_lang}, source_lang={source_lang}")

        # Detect source language if not provided
        if not source_lang:
            source_lang = await self.detect_language(text)
            logger.info(f"Auto-detected source language: {source_lang}")
            if not source_lang:
                return None, {'error': 'Could not detect source language'}

        # Try translation services in order of preference
        translated = None

        # Try DeepL first (highest quality)
        if config.DEEPL_API_KEY:
            translated = await self.translate_with_deepl(text, target_lang, source_lang)

        # Try Yandex if DeepL failed
        if not translated and config.YANDEX_API_KEY:
            translated = await self.translate_with_yandex(text, target_lang, source_lang)

        # Fallback to Google Translate
        if not translated:
            logger.info(f"Trying Google Translate for: {text[:50]} -> {target_lang}")
            translated = await self.translate_with_google(text, target_lang, source_lang)
            if translated:
                logger.info(f"Google Translate success: {translated[:50]}")
            else:
                logger.error("Google Translate failed")

        # If all translation services fail, try a simple OpenAI-based translation
        if not translated and config.OPENAI_API_KEY:
            logger.info("All translation services failed, trying OpenAI fallback")
            translated = await self.translate_with_openai_fallback(text, target_lang, source_lang)
            if translated:
                logger.info(f"OpenAI fallback translation success: {translated[:50]}")

        if not translated:
            logger.error("All translation methods failed")
            return None, {'error': 'Translation failed'}

        # Enhance with GPT if requested
        metadata = {
            'source_lang': source_lang,
            'target_lang': target_lang,
            'style': style,
            'basic_translation': translated
        }

        if enhance and config.OPENAI_API_KEY:
            logger.info(f"Starting GPT enhancement for text: {text[:50]}...")
            enhancement = await self.enhance_with_gpt(text, translated, target_lang, style)
            logger.info(f"GPT enhancement result: {enhancement.get('enhanced_translation', 'No enhancement')[:50]}...")
            if enhancement['enhanced_translation']:
                translated = enhancement['enhanced_translation']
            metadata.update(enhancement)
        else:
            logger.info(f"GPT enhancement skipped: enhance={enhance}, openai_key_exists={bool(config.OPENAI_API_KEY)}")

        logger.info(f"Translation completed: {source_lang} -> {target_lang}, result='{translated[:50]}...'")
        return translated, metadata

    async def get_language_name(self, lang_code: str, interface_lang: str = 'ru') -> str:
        """Get language name in the interface language"""
        names = {
            'ru': {
                'en': 'Английский',
                'ru': 'Русский',
                'es': 'Испанский',
                'fr': 'Французский',
                'de': 'Немецкий',
                'it': 'Итальянский',
                'pt': 'Португальский',
                'ja': 'Японский',
                'zh': 'Китайский',
                'ko': 'Корейский',
                'ar': 'Арабский',
                'hi': 'Хинди',
                'tr': 'Турецкий',
                'pl': 'Польский',
                'nl': 'Нидерландский',
                'sv': 'Шведский',
                'da': 'Датский',
                'no': 'Норвежский',
                'fi': 'Финский',
                'cs': 'Чешский',
                'hu': 'Венгерский',
                'ro': 'Румынский',
                'uk': 'Украинский',
                'he': 'Иврит',
                'th': 'Тайский',
                'vi': 'Вьетнамский'
            },
            'en': {
                'en': 'English',
                'ru': 'Russian',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
                'it': 'Italian',
                'pt': 'Portuguese',
                'ja': 'Japanese',
                'zh': 'Chinese',
                'ko': 'Korean',
                'ar': 'Arabic',
                'hi': 'Hindi',
                'tr': 'Turkish',
                'pl': 'Polish',
                'nl': 'Dutch',
                'sv': 'Swedish',
                'da': 'Danish',
                'no': 'Norwegian',
                'fi': 'Finnish',
                'cs': 'Czech',
                'hu': 'Hungarian',
                'ro': 'Romanian',
                'uk': 'Ukrainian',
                'he': 'Hebrew',
                'th': 'Thai',
                'vi': 'Vietnamese'
            }
        }

        lang_names = names.get(interface_lang, names['en'])
        return lang_names.get(lang_code, lang_code.upper())