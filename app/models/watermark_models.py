from pydantic import BaseModel


class AddWatermarkRequest(BaseModel):
    video_path: str
    watermark_path: str
    output_path: str
    opacity: float = 0.5
    scale: float = 0.5
