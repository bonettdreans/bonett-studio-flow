from fastapi import HTTPException, APIRouter
from typing import Dict
from datetime import datetime
from app.services.video_processing_service import VideoProcessor
from app.models.video_processing import (
    VideoProcessingRequest,
    VideoProcessingResponse
)
import uuid
import os

router = APIRouter(
    prefix="/Video",
    tags=["Cycle Video"],
    responses={404: {"description": "Not found"}},
)

tasks_history: Dict[str, Dict] = {}


@router.post("/api/process/create-cyclic")
def process_video_sync(request: VideoProcessingRequest):
    """
    Endpoint para processamento de vídeo - processa de forma síncrona
    Só retorna quando o processamento estiver completamente finalizado
    """

    task_id = str(uuid.uuid4())

    if not os.path.exists(request.video_path):
        raise HTTPException(
            status_code=400, detail=f"Arquivo de vídeo não encontrado: {request.video_path}")

    tasks_history[task_id] = {
        "id": task_id,
        "status": "processing",
        "video_path": request.video_path,
        "output_path": request.output_path,
        "start_time": datetime.now().isoformat()
    }

    try:
        result = VideoProcessor.create_cyclic_video(
            video_path=request.video_path,
            output_path=request.output_path,
            progress_callback=lambda msg, prog: update_task_progress(
                task_id, msg, prog)
        )

        tasks_history[task_id].update({
            "status": "completed" if result["success"] else "failed",
            "message": result["message"],
            "output_path": result.get("output_path"),
            "end_time": datetime.now().isoformat()
        })

        if result["success"]:
            return VideoProcessingResponse(
                success=True,
                message=result["message"],
                output_path=result["output_path"]
            )
        else:
            raise HTTPException(status_code=500, detail=result["message"])

    except Exception as e:
        tasks_history[task_id].update({
            "status": "failed",
            "message": f"Erro: {str(e)}",
            "end_time": datetime.now().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))


def update_task_progress(task_id: str, message: str, progress: float):
    """
    Função auxiliar para atualizar o progresso da tarefa no histórico
    """
    if task_id in tasks_history:
        tasks_history[task_id].update({
            "message": message,
            "progress": progress
        })
