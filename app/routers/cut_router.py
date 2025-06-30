from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse
from app.models.cut_models import CutVideoRequest
from app.services.cut_service import CutService


router = APIRouter(
    prefix="/cut",
    tags=["Cut Video"],
    responses={404: {"description": "Not found"}},
)


@router.post("/api/process/cut-video")
async def cut_video(request: CutVideoRequest):
    """Endpoint para corte de vídeo"""
    try:
        result = CutService.cut_video(
            input_path=request.input_path,
            output_path=request.output_path,
            start_time=request.start_time,
            end_time=request.end_time
        )
        return {"status": "success", "output_path": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
