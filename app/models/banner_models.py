from pydantic import BaseModel


class AddBannerRequest(BaseModel):
    video_path: str
    image_path: str
    output_path: str
    position: str = "top"
    banner_scale: float = 1.0
    padding: int = 0
