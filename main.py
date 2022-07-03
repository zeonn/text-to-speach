from glob import glob

from tqdm import tqdm

from config import Config
from text_to_speach import TextToSpeach


class MainPipeline:
    def __init__(self) -> None:
        self.data_dir: str = 'data'  # Directory with source and result files
        self.tts_processor = TextToSpeach(config=Config)

    def _read_src_files(self) -> list[str]:
        """ Get a list of not processed text files in data directory """
        txt_files: list[str] = glob(f'{self.data_dir}/*.txt')
        mp3_files: list[str] = glob(f'{self.data_dir}/*.mp3')
        existed_files: list[str] = [file.replace('.mp3', '.txt') for file in mp3_files]
        files_to_return: list[str] = list(set(txt_files) - set(existed_files))
        return files_to_return

    def _read_text(self, filename: str) -> str:
        """ Read text from the file """
        with open(file=filename, mode='r') as file:
            lines: list[str] = file.readlines()
        text: str = self._clean_text(lines=lines)
        return text

    @staticmethod
    def _clean_text(lines: list[str]) -> str:
        """ Remove empty lines from the text """
        lines: list[str] = [line for line in lines if line]
        lines: list[str] = [line.strip() for line in lines]
        return '\n'.join(lines)

    def run(self) -> None:
        """ Main entrypoint """
        files: list[str] = self._read_src_files()
        for txt_filename in tqdm(iterable=files, desc='Processing text files'):
            text: str = self._read_text(filename=txt_filename)
            result_filename: str = txt_filename.replace('.txt', '.mp3')
            self.tts_processor.generate(text=text, output_filename=result_filename)


if __name__ == '__main__':
    pipeline = MainPipeline()
    pipeline.run()
