from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
import os
from app.services.audio_service import AudioService
from app.models.audio_models import MixAudioRequest

router = APIRouter(
    prefix="/audio",
    tags=["Audio Mix"],
    responses={404: {"description": "Not found"}},
)


@router.post("/api/process/mix-audio-async")
async def mix_audio_async(request: MixAudioRequest):
    """
    Endpoint para mesclar áudio MP3 com vídeo usando threads.
    Aguarda a conclusão do processamento antes de retornar.
    """
    try:
        # Este método vai utilizar threads, mas ainda vai aguardar a conclusão
        result = AudioService.mix_audio_with_video_threaded(
            video_path=request.video_path,
            audio_path=request.audio_path,
            replace_original=request.replace_original,
            reduce_original_volume=request.reduce_original_volume
        )
        return {"status": "success", "message": "Processamento concluído com sucesso", "output_path": result}
    except Exception as e:
        print(f"Erro no endpoint mix-audio-async: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
