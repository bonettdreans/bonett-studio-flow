from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import os
from app.services.banner_service import BannerService
from app.models.banner_models import AddBannerRequest

router = APIRouter(
    prefix="/banner",
    tags=["Banner Video"],
    responses={404: {"description": "Not found"}},
)


@router.post("/api/process/add-banner")
async def add_banner(request: AddBannerRequest):
    """Endpoint para adicionar banner ao vídeo"""
    try:
        result = BannerService.add_banner(
            video_path=request.video_path,
            image_path=request.image_path,
            output_path=request.output_path,
            position=request.position,
            banner_scale=request.banner_scale,
            padding=request.padding
        )
        return {"status": "success", "output_path": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
