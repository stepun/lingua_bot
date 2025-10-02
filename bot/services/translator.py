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

    async def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration from database with fallback to config"""
        try:
            from bot.database import db

            # Get settings from database with fallback to config
            deepl_enabled = await db.get_setting('deepl_enabled', True)
            yandex_enabled = await db.get_setting('yandex_enabled', True)
            gpt_enhancement = await db.get_setting('gpt_enhancement', True)

            deepl_api_key = await db.get_setting('deepl_api_key', config.DEEPL_API_KEY or '')
            yandex_api_key = await db.get_setting('yandex_api_key', config.YANDEX_API_KEY or '')
            openai_api_key = await db.get_setting('openai_api_key', config.OPENAI_API_KEY or '')

            return {
                'deepl_enabled': deepl_enabled,
                'yandex_enabled': yandex_enabled,
                'gpt_enhancement': gpt_enhancement,
                'deepl_api_key': deepl_api_key.strip() if deepl_api_key else '',
                'yandex_api_key': yandex_api_key.strip() if yandex_api_key else '',
                'openai_api_key': openai_api_key.strip() if openai_api_key else '',
            }
        except Exception as e:
            logger.error(f"Failed to get API config from database: {e}")
            # Fallback to config values
            return {
                'deepl_enabled': True,
                'yandex_enabled': True,
                'gpt_enhancement': True,
                'deepl_api_key': config.DEEPL_API_KEY or '',
                'yandex_api_key': config.YANDEX_API_KEY or '',
                'openai_api_key': config.OPENAI_API_KEY or '',
            }

    async def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of the text"""
        try:
            lang = detect(text)
            return lang
        except LangDetectException:
            return None

    async def translate_with_yandex(self, text: str, target_lang: str,
                                   source_lang: str = None, api_key: str = None) -> Optional[str]:
        """Translate text using Yandex Translate API"""
        yandex_key = api_key or config.YANDEX_API_KEY
        if not yandex_key:
            return None

        url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
        headers = {
            "Authorization": f"Api-Key {yandex_key}",
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
                                  source_lang: str = None, api_key: str = None) -> Optional[str]:
        """Translate text using DeepL API"""
        deepl_key = api_key or config.DEEPL_API_KEY
        if not deepl_key:
            return None

        url = "https://api-free.deepl.com/v2/translate"
        headers = {
            "Authorization": f"DeepL-Auth-Key {deepl_key}",
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
                                           source_lang: str = None, api_key: str = None) -> Optional[str]:
        """Simple translation using OpenAI as fallback when other services fail"""
        openai_key = api_key or config.OPENAI_API_KEY
        if not openai_key:
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

            # Use custom API key if provided
            client = openai.AsyncOpenAI(api_key=openai_key) if openai_key != config.OPENAI_API_KEY else self.openai_client

            response = await client.chat.completions.create(
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
                              explain_grammar: bool = False, user_id: int = None,
                              api_key: str = None) -> Dict[str, Any]:
        """Enhance translation using GPT for natural language and style"""
        style_prompts = {
            'informal': 'casual and friendly, using colloquial expressions, contractions, and everyday language as if talking to a close friend',
            'formal': 'formal and polite, using proper grammar, respectful language, and avoiding contractions - suitable for official documents and business correspondence',
            'business': 'professional and business-oriented, using corporate terminology, concise language, and industry-appropriate expressions',
            'travel': 'simple, clear and practical for tourists - using basic vocabulary, essential phrases, and avoiding complex grammar',
            'academic': 'scholarly and precise, using technical terminology, complex sentence structures, and formal academic language'
        }

        style_description = style_prompts.get(style, style_prompts['informal'])

        # Get user's interface language for explanations
        from bot.database import db
        user_info = await db.get_user(user_id) if user_id else {}
        interface_lang = user_info.get('interface_language', 'ru')

        # Get target language name for prompts
        lang_names = {
            'ru': 'Russian', 'en': 'English', 'es': 'Spanish', 'fr': 'French',
            'de': 'German', 'it': 'Italian', 'pt': 'Portuguese', 'ja': 'Japanese',
            'zh': 'Chinese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi',
            'tr': 'Turkish', 'pl': 'Polish', 'nl': 'Dutch', 'sv': 'Swedish'
        }
        target_lang_name = lang_names.get(target_lang, target_lang)

        # Create prompt for enhanced features
        if explain_grammar:
            system_prompt = f"""You are a professional translator and language expert.
IMPORTANT: ALL translations and alternatives MUST be in {target_lang_name} language.
IMPORTANT: Grammar explanations and style explanations MUST be in Russian language.
Provide:
1. Enhanced translation in {target_lang_name} with {style_description} style
2. 2-3 alternative translations in {target_lang_name}
3. Grammar explanation in Russian language
4. Brief explanation of style choices in Russian language
5. Phonetic transcription (IPA) for the BASIC translation (not enhanced)"""

            user_prompt = f"""Original text: {original_text}
Basic translation in {target_lang_name}: {translated_text}
Target style: {style}
Target language: {target_lang_name}

IMPORTANT: Create IPA transcription for the BASIC translation ONLY: "{translated_text}"
NOT for the enhanced/styled version!

Format your response EXACTLY as:
Enhanced: [enhanced translation in {target_lang_name}]
Alternative1: [first alternative in {target_lang_name}]
Alternative2: [second alternative in {target_lang_name}]
Grammar: [grammar explanation in Russian]
Explanation: [brief style explanation in Russian]
Transcription: [IPA for "{translated_text}" ONLY, e.g. [həˈləʊ]]"""
        else:
            # Simple enhancement for non-premium
            system_prompt = f"""You are a professional translator specializing in natural, contextual translations.
IMPORTANT: Your response MUST be in {target_lang_name} language.
Transform the translation to be {style_description}.
Make the style difference clear and noticeable."""

            user_prompt = f"""Original: {original_text}
Current translation in {target_lang_name}: {translated_text}
Target language: {target_lang_name}

Provide ONLY the enhanced translation in {target_lang_name} with {style} style. No explanations."""

        try:
            # Use custom API key if provided
            openai_key = api_key or config.OPENAI_API_KEY
            client = openai.AsyncOpenAI(api_key=openai_key) if openai_key != config.OPENAI_API_KEY else self.openai_client

            response = await client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            content = response.choices[0].message.content.strip()

            # Parse response based on whether grammar was requested
            if explain_grammar:
                lines = content.split('\n')
                enhanced_translation = translated_text
                alternatives = []
                grammar_explanation = ''
                explanation = ''
                transcription = ''

                for line in lines:
                    line = line.strip()
                    if line.lower().startswith('enhanced:'):
                        enhanced_translation = line.split(':', 1)[1].strip()
                    elif line.lower().startswith('alternative1:'):
                        alt = line.split(':', 1)[1].strip()
                        if alt:
                            alternatives.append(alt)
                    elif line.lower().startswith('alternative2:'):
                        alt = line.split(':', 1)[1].strip()
                        if alt:
                            alternatives.append(alt)
                    elif line.lower().startswith('grammar:'):
                        grammar_explanation = line.split(':', 1)[1].strip()
                    elif line.lower().startswith('explanation:'):
                        explanation = line.split(':', 1)[1].strip()
                    elif line.lower().startswith('transcription:'):
                        transcription = line.split(':', 1)[1].strip()

                # Add a third alternative if we have space
                if len(alternatives) < 3 and translated_text != enhanced_translation:
                    alternatives.append(translated_text)

                result = {
                    'enhanced_translation': enhanced_translation,
                    'alternatives': alternatives,
                    'explanation': explanation or f'Style adapted to {style}',
                    'grammar': grammar_explanation,
                    'transcription': transcription,
                    'synonyms': []
                }
            else:
                # Simple parsing for non-premium
                enhanced_translation = content.strip()
                if enhanced_translation.startswith('"') and enhanced_translation.endswith('"'):
                    enhanced_translation = enhanced_translation[1:-1]
                if not enhanced_translation:
                    enhanced_translation = translated_text

                result = {
                    'enhanced_translation': enhanced_translation,
                    'alternatives': [],
                    'explanation': '',
                    'grammar': '',
                    'transcription': '',
                    'synonyms': []
                }

            logger.info(f"GPT enhancement result - alternatives: {result.get('alternatives', [])}, grammar: {result.get('grammar', '')[:50]}")
            return result

        except Exception as e:
            logger.error(f"GPT enhancement error: {e}")
            return {
                'enhanced_translation': translated_text,
                'alternatives': [],
                'explanation': '',
                'grammar': '',
                'transcription': ''
            }

    async def translate(self, text: str, target_lang: str, source_lang: str = None,
                       style: str = 'informal', enhance: bool = True, user_id: int = None,
                       explain_grammar: bool = False) -> Tuple[str, Dict[str, Any]]:
        """Main translation method with enhancement"""
        logger.info(f"Translation request: text='{text[:30]}...', target_lang={target_lang}, source_lang={source_lang}")

        # Get API configuration from database
        api_config = await self.get_api_config()
        logger.info(f"API config: deepl_enabled={api_config['deepl_enabled']}, yandex_enabled={api_config['yandex_enabled']}, gpt_enhancement={api_config['gpt_enhancement']}")

        # Detect source language if not provided
        if not source_lang:
            source_lang = await self.detect_language(text)
            logger.info(f"Auto-detected source language: {source_lang}")
            if not source_lang:
                return None, {'error': 'Could not detect source language'}

        # Try translation services in order of preference
        translated = None

        # Try DeepL first (highest quality)
        if api_config['deepl_enabled'] and api_config['deepl_api_key']:
            logger.info("Trying DeepL translation...")
            translated = await self.translate_with_deepl(text, target_lang, source_lang, api_config['deepl_api_key'])
            if translated:
                logger.info(f"DeepL translation success: {translated[:50]}")

        # Try Yandex if DeepL failed
        if not translated and api_config['yandex_enabled'] and api_config['yandex_api_key']:
            logger.info("Trying Yandex translation...")
            translated = await self.translate_with_yandex(text, target_lang, source_lang, api_config['yandex_api_key'])
            if translated:
                logger.info(f"Yandex translation success: {translated[:50]}")

        # Fallback to Google Translate
        if not translated:
            logger.info(f"Trying Google Translate for: {text[:50]} -> {target_lang}")
            translated = await self.translate_with_google(text, target_lang, source_lang)
            if translated:
                logger.info(f"Google Translate success: {translated[:50]}")
            else:
                logger.error("Google Translate failed")

        # If all translation services fail, try a simple OpenAI-based translation
        if not translated and api_config['openai_api_key']:
            logger.info("All translation services failed, trying OpenAI fallback")
            translated = await self.translate_with_openai_fallback(text, target_lang, source_lang, api_config['openai_api_key'])
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
            'basic_translation': translated,
            'original_text': text  # Store original text for re-translation
        }

        if enhance and api_config['gpt_enhancement'] and api_config['openai_api_key']:
            logger.info(f"Starting GPT enhancement for text: {text[:50]}... with style: {style}")
            enhancement = await self.enhance_with_gpt(text, translated, target_lang, style, explain_grammar=explain_grammar, user_id=user_id, api_key=api_config['openai_api_key'])
            logger.info(f"GPT enhancement result: {enhancement.get('enhanced_translation', 'No enhancement')[:50]}...")
            if enhancement['enhanced_translation']:
                translated = enhancement['enhanced_translation']
            metadata.update(enhancement)
        else:
            logger.info(f"GPT enhancement skipped: enhance={enhance}, gpt_enhancement_enabled={api_config['gpt_enhancement']}, openai_key_exists={bool(api_config['openai_api_key'])}")

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