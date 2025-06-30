from pydantic import BaseModel


class CutVideoRequest(BaseModel):
    input_path: str
    output_path: str
    start_time: str
    end_time: str
