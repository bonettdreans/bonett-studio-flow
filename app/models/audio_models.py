from pydantic import BaseModel


class MixAudioRequest(BaseModel):
    video_path: str
    audio_path: str
    replace_original: bool = True
    reduce_original_volume: bool = False
