from pydantic import BaseModel
from typing import Tuple


class RemoveGreenScreenRequest(BaseModel):
    image_path: str
    lower_bound: Tuple[int, int, int] = (40, 100, 20)
    upper_bound: Tuple[int, int, int] = (80, 255, 255)
