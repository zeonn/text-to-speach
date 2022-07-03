from dataclasses import dataclass

from google.cloud.texttospeech_v1 import (SsmlVoiceGender, AudioEncoding)


@dataclass
class Config:
    language: str = 'en-US'
    voice_name: str = 'en-US-Wavenet-B'  # https://cloud.google.com/text-to-speech/docs/voices
    speaking_rate: float = 1.0
    gender: SsmlVoiceGender = SsmlVoiceGender.MALE
    encoding: AudioEncoding = AudioEncoding.MP3
    month_char_limit: int = 1_000_000  # Free month limit
