import os
import io
import asyncio
import tempfile
from typing import Optional, Tuple
from pathlib import Path
import aiofiles
import aiohttp
from pydub import AudioSegment
from gtts import gTTS
import openai
from config import config
import logging

logger = logging.getLogger(__name__)

class VoiceService:
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=config.OPENAI_API_KEY) if config.OPENAI_API_KEY else None
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def transcribe_with_whisper(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper API"""
        if not self.openai_client:
            return None

        try:
            async with aiofiles.open(audio_file_path, 'rb') as audio_file:
                audio_data = await audio_file.read()

            # Create a file-like object from bytes
            audio_file = io.BytesIO(audio_data)
            audio_file.name = Path(audio_file_path).name

            response = await self.openai_client.audio.transcriptions.create(
                model=config.WHISPER_MODEL,
                file=audio_file,
                response_format="text"
            )

            return response
        except Exception as e:
            logger.error(f"Whisper transcription error: {e}")
            return None

    async def transcribe_with_google(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio using Google Speech-to-Text (fallback)"""
        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()

            # Convert audio to WAV if needed
            audio = AudioSegment.from_file(audio_file_path)
            wav_path = audio_file_path.replace(Path(audio_file_path).suffix, '.wav')
            audio.export(wav_path, format='wav')

            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)

            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                None,
                lambda: recognizer.recognize_google(audio_data, language='auto')
            )

            # Clean up temporary file
            if wav_path != audio_file_path:
                os.remove(wav_path)

            return text
        except Exception as e:
            logger.error(f"Google STT error: {e}")
            return None

    async def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """Transcribe audio using available services"""
        # Try Whisper first
        if config.OPENAI_API_KEY:
            text = await self.transcribe_with_whisper(audio_file_path)
            if text:
                return text

        # Fallback to Google
        return await self.transcribe_with_google(audio_file_path)

    async def generate_speech_gtts(self, text: str, language: str = 'en',
                                  speed: float = 1.0) -> Optional[bytes]:
        """Generate speech using gTTS (Google Text-to-Speech)"""
        try:
            # Map language codes for gTTS
            gtts_lang_map = {
                'en': 'en',
                'ru': 'ru',
                'es': 'es',
                'fr': 'fr',
                'de': 'de',
                'it': 'it',
                'pt': 'pt',
                'ja': 'ja',
                'zh': 'zh-CN',
                'ko': 'ko',
                'ar': 'ar',
                'hi': 'hi',
                'tr': 'tr',
                'pl': 'pl',
                'nl': 'nl',
                'sv': 'sv',
                'da': 'da',
                'no': 'no',
                'fi': 'fi',
                'cs': 'cs',
                'hu': 'hu',
                'ro': 'ro',
                'uk': 'uk',
                'he': 'iw',
                'th': 'th',
                'vi': 'vi'
            }

            lang_code = gtts_lang_map.get(language, 'en')

            # Generate speech
            tts = gTTS(text=text, lang=lang_code, slow=(speed < 1.0))

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                tmp_path = tmp_file.name

            # Read the file
            async with aiofiles.open(tmp_path, 'rb') as f:
                audio_data = await f.read()

            # Adjust speed if needed
            if speed != 1.0 and speed > 0:
                audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
                # Speed up or slow down
                audio = audio.speedup(playback_speed=speed)
                buffer = io.BytesIO()
                audio.export(buffer, format='mp3')
                audio_data = buffer.getvalue()

            # Clean up
            os.remove(tmp_path)

            return audio_data
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            return None

    async def generate_speech_elevenlabs(self, text: str, language: str = 'en',
                                        voice_id: str = None) -> Optional[bytes]:
        """Generate speech using ElevenLabs API (premium quality)"""
        if not config.ELEVENLABS_API_KEY:
            return None

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id or 'default'}"
        headers = {
            "xi-api-key": config.ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }

        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error(f"ElevenLabs error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"ElevenLabs exception: {e}")
            return None

    async def generate_speech_openai(self, text: str, language: str = 'en',
                                    voice: str = 'alloy', speed: float = 1.0) -> Optional[bytes]:
        """Generate speech using OpenAI TTS API"""
        if not self.openai_client:
            return None

        try:
            response = await self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,  # alloy, echo, fable, onyx, nova, shimmer
                input=text,
                speed=speed,  # 0.25 to 4.0
                response_format="mp3"
            )

            # Convert response to bytes
            audio_data = response.content
            return audio_data
        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}")
            return None

    async def generate_speech(self, text: str, language: str = 'en',
                            premium: bool = False, speed: float = 1.0,
                            voice_type: str = 'alloy') -> Optional[bytes]:
        """Generate speech using available services"""
        # For premium users, try higher quality services first
        if premium:
            # Try ElevenLabs first
            if config.ELEVENLABS_API_KEY:
                audio = await self.generate_speech_elevenlabs(text, language)
                if audio:
                    return audio

            # Try OpenAI TTS with user settings
            if config.OPENAI_API_KEY:
                audio = await self.generate_speech_openai(text, language, voice=voice_type, speed=speed)
                if audio:
                    return audio

        # Fallback to gTTS (free)
        return await self.generate_speech_gtts(text, language, speed)

    async def convert_audio_format(self, audio_data: bytes, input_format: str,
                                  output_format: str = 'mp3') -> bytes:
        """Convert audio between formats"""
        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=input_format)
            buffer = io.BytesIO()
            audio.export(buffer, format=output_format)
            return buffer.getvalue()
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return audio_data

    async def download_voice_message(self, file_url: str, bot_token: str) -> Optional[bytes]:
        """Download voice message from Telegram"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            async with self.session.get(file_url) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error(f"Failed to download voice message: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Voice download error: {e}")
            return None

    async def process_voice_message(self, file_id: str, bot) -> Optional[str]:
        """Process voice message from Telegram"""
        try:
            # Get file info
            file = await bot.get_file(file_id)
            file_url = f"https://api.telegram.org/file/bot{config.BOT_TOKEN}/{file.file_path}"

            # Download the file
            audio_data = await self.download_voice_message(file_url, config.BOT_TOKEN)
            if not audio_data:
                return None

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name

            try:
                # Try to transcribe OGG directly with Whisper first (it supports OGG)
                if config.OPENAI_API_KEY:
                    text = await self.transcribe_with_whisper(tmp_path)
                    if text:
                        os.remove(tmp_path)
                        return text

                # If Whisper fails or is not available, try to convert using pydub
                audio = AudioSegment.from_ogg(tmp_path)
                mp3_path = tmp_path.replace('.ogg', '.mp3')
                audio.export(mp3_path, format='mp3')

                # Transcribe converted file
                text = await self.transcribe_audio(mp3_path)

                # Clean up
                os.remove(tmp_path)
                os.remove(mp3_path)

                return text
            except Exception as conversion_error:
                logger.error(f"Audio conversion error (ffmpeg might be missing): {conversion_error}")

                # If conversion fails, try transcribing OGG directly with Google (may not work)
                try:
                    text = await self.transcribe_with_google(tmp_path)
                    os.remove(tmp_path)
                    return text
                except Exception as google_error:
                    logger.error(f"Google STT with OGG failed: {google_error}")
                    os.remove(tmp_path)
                    return None

        except Exception as e:
            logger.error(f"Voice processing error: {e}")
            return None

    async def validate_audio_duration(self, audio_data: bytes, max_duration: int = None) -> bool:
        """Validate audio duration"""
        if max_duration is None:
            max_duration = config.MAX_VOICE_DURATION

        try:
            audio = AudioSegment.from_file(io.BytesIO(audio_data))
            duration_seconds = len(audio) / 1000
            return duration_seconds <= max_duration
        except Exception as e:
            logger.error(f"Audio validation error: {e}")
            return False