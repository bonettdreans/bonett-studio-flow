from fastapi import APIRouter, HTTPException
from app.services.watermark_service import WatermarkService
from app.models.watermark_models import AddWatermarkRequest

router = APIRouter(
    prefix="/watermark",
    tags=["Watermark Video"],
    responses={404: {"description": "Arquivo não encontrado"}},
)


@router.post("/api/process/add-watermark")
async def add_watermark(request: AddWatermarkRequest):
    """Endpoint para adicionar marca d'água ao vídeo"""
    try:
        result = WatermarkService.add_watermark(
            video_path=request.video_path,
            watermark_path=request.watermark_path,
            output_path=request.output_path,
            opacity=request.opacity,
            scale=request.scale
        )
        return {"status": "success", "output_path": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
