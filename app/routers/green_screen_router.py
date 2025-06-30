from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.green_screen_service import GreenScreenService
from app.models.green_screen_models import RemoveGreenScreenRequest
import os
import tempfile
import cv2

router = APIRouter(
    prefix="/green_screen",
    tags=["Green Screen"],
    responses={404: {"description": "Arquivo não encontrado"}},
)


@router.post("/api/process/remove-green-screen")
async def remove_green_screen(request: RemoveGreenScreenRequest):
    """Endpoint para remoção de fundo verde"""
    try:
        result = GreenScreenService.remove_green_screen(
            image_path=request.image_path,
            lower_bound=request.lower_bound,
            upper_bound=request.upper_bound
        )

        # Salvar temporariamente para retornar
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "output.png")
        cv2.imwrite(output_path, result)

        return FileResponse(
            output_path,
            media_type="image/png",
            filename="output.png"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
