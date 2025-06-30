from pydantic import BaseModel, Field, validator
import re
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class VideoProcessingRequest(BaseModel):
    video_path: str
    output_path: str


class VideoProcessingResponse(BaseModel):
    success: bool
    message: str
    output_path: Optional[str] = None
