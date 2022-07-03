import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Iterator

from google.cloud import texttospeech
from google.cloud.texttospeech_v1 import (VoiceSelectionParams, AudioConfig, SynthesizeSpeechResponse)
from google.oauth2.service_account import Credentials

from audio_processing import concatenate_audio


class TextToSpeach:
    """ Use Google Text-To-Speach API to convert text to mp3 audio file """

    def __init__(self, config: dataclass) -> None:
        self.config = config
        service_account_key_file: str = 'credentials.json'
        self.statistics_file: str = 'usage_statistics.json'
        self.month_char_limit: int = self.config.month_char_limit
        self.request_char_limit: int = 5_000  # Google limitation for one request

        credentials = Credentials.from_service_account_file(service_account_key_file)
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)
        self.voice = VoiceSelectionParams(
            language_code=self.config.language,
            ssml_gender=self.config.gender,
            name=self.config.voice_name,
        )
        self.audio_config = AudioConfig(audio_encoding=self.config.encoding, speaking_rate=self.config.speaking_rate)

    def generate(self, text: str, output_filename: str = 'output.mp3') -> None:
        """
        Main entrypoint
        :param text: Text with one or many paragraphs joined by "\n"
        :param output_filename: The name of result audio file
        """
        if not self._is_limit_accept(text=text):
            print('Your chars limit is exited')
            return None

        result_files: list[str] = []
        for i, text_chunk in enumerate(self._text_iterator(text=text)):
            synthesis_input = texttospeech.SynthesisInput(text=text_chunk)
            response: SynthesizeSpeechResponse = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config,
            )
            filename: str = output_filename.replace('.mp3', f'_{i}.mp3')
            self._save_response(response=response, filename=filename)
            self._save_statistics(text=text)
            result_files.append(filename)

        # Concatenate audio fragments to one file and remove temp files
        if len(result_files) > 1:
            concatenate_audio(audio_clip_paths=result_files, output_path=output_filename)
            for filename in result_files:
                os.remove(filename)
        elif len(result_files) == 1:
            os.rename(src=result_files[0], dst=output_filename)

    def _text_iterator(self, text: str) -> Iterator[str]:
        """
        Split long text by paragraphs to the list of chunks. Every chunk is less than self.request_char_limit chars
        :param text: Text with one or many paragraphs joined by "\n"
        :return: Iterator with text chunks
        """
        paragraphs: list[str] = text.split('\n')
        paragraphs: list[str] = [paragraph for paragraph in paragraphs if paragraph]
        paragraphs: list[str] = [paragraph.strip() for paragraph in paragraphs]
        used_chars: int = 0
        paragraphs_to_return: list[str] = []
        for paragraph in paragraphs:
            paragraph_chars: int = len(paragraph)
            if paragraph_chars + used_chars < self.request_char_limit:
                paragraphs_to_return.append(paragraph)
                used_chars += paragraph_chars
            else:
                text_to_return: str = '\n'.join(paragraphs_to_return)
                paragraphs_to_return: list[str] = [paragraph]
                used_chars: int = paragraph_chars
                yield text_to_return
        if paragraphs_to_return:
            text_to_return: str = '\n'.join(paragraphs_to_return)
            yield text_to_return

    def _is_limit_accept(self, text: str) -> bool:
        """
        Get the usage statistics from file and check is monthly limit not exceeded
        :param text: text to use
        :return: True if limit is not exceeded in the current month or False otherwise
        """
        statistics: Optional[dict] = self._load_statistics()
        if not statistics:
            return True
        key: str = self._get_statistics_key()
        chars_count: int = len(text)
        used_chars: int = statistics.get(key, 0)
        return used_chars + chars_count < self.month_char_limit

    @staticmethod
    def _save_response(response: SynthesizeSpeechResponse, filename: str) -> None:
        """
        Save Google API response to the file
        :param response: SynthesizeSpeechResponse
        :param filename: str
        """
        with open(file=filename, mode="wb") as out:
            out.write(response.audio_content)

    def _load_statistics(self) -> Optional[dict]:
        """ Load usage statistics from json file """
        if not os.path.exists(self.statistics_file):
            return None
        with open(file=self.statistics_file, mode='r') as file:
            data = json.load(fp=file)
        return data

    @staticmethod
    def _get_statistics_key() -> str:
        """" Get key with <current year>.<current month> """
        now_date: datetime = datetime.utcnow()
        key: str = f'{now_date.year}.{now_date.month}'
        return key

    def _save_statistics(self, text: str) -> None:
        """ Save usage statistics to json file """
        chars_count: int = len(text)
        statistics: Optional[dict] = self._load_statistics()
        if not statistics:
            statistics: dict = {}
        key: str = self._get_statistics_key()
        value: int = statistics.get(key, 0)
        value += chars_count
        statistics[key] = value

        with open(file=self.statistics_file, mode='w') as file:
            json.dump(obj=statistics, fp=file)
