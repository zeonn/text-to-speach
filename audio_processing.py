from pydub import AudioSegment
import os


def concatenate_audio(audio_clip_paths: list[str], output_path: str) -> None:
    """ Concatenates two or more audio files into one audio file """

    def get_file_extension(filename: str) -> str:
        return os.path.splitext(filename)[1].lstrip(".")

    clips: list[AudioSegment] = []
    for clip_path in audio_clip_paths:
        extension: str = get_file_extension(filename=clip_path)
        clip: AudioSegment = AudioSegment.from_file(file=clip_path, format=extension)
        clips.append(clip)

    final_clip: AudioSegment = clips[0]
    for i in range(1, len(clips)):
        final_clip += clips[i]

    # export the final clip
    final_clip_extension: str = get_file_extension(filename=output_path)
    final_clip.export(out_f=output_path, format=final_clip_extension)
