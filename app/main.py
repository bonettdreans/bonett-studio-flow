from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
from app.routers import banner_router, cut_router, video_processing_router, watermark_router, green_screen_router, audio_router

app = FastAPI(
    title="Bonett Studio Flow API",
    description="API para processamento de videos e geração de shorts",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(banner_router.router, prefix="/api/v1")
app.include_router(cut_router.router, prefix="/api/v1")
app.include_router(watermark_router.router, prefix="/api/v1")
app.include_router(video_processing_router.router, prefix="/api/v1")
app.include_router(green_screen_router.router, prefix="/api/v1")
app.include_router(audio_router.router, prefix="/api/v1")


@app.get("/")
async def root():
    """
    Endpoint raiz da API - Bonett Studio Flow API"
    """
    return {
        "message": "Bonett Studio Flow API",
        "version": "1.0.0",
        "description": "API para processamento de videos e geração de shorts",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "banner_endpoints": "/api/v1/banner/*",
            "cut_endpoints": "/api/v1/cut/*",
            "watermark_endpoints": "/api/v1/watermark/*",
            "video_processing_endpoints": "/api/v1/video/*",
            "green_screen_endpoints": "/api/v1/green-screen/*",
            "audio_endpoints": "/api/v1/audio/*"
        },
        "features": [
            "Adição de Banner em Vídeos",
            "Corte e Edição de Vídeos",
            "Aplicação de Marca D'água",
            "Processamento Geral de Vídeos",
            "Remoção de Fundo Verde (Chroma Key)",
            "Processamento e Mixagem de Áudio"
        ],
        "supported_formats": {
            "video": [".mp4"],
            "audio": [".mp3"],
            "image": [".png"]
        },
        "status": "active",
        "health": "ok"
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de verificação de saúde geral da API de processamento de vídeo
    """
    return {
        "status": "healthy",
        "message": "Video Processing API funcionando corretamente",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "banner_service": "healthy",
            "cut_service": "healthy",
            "watermark_service": "healthy",
            "video_processing_service": "healthy",
            "green_screen_service": "healthy",
            "audio_service": "healthy"
        },
        "dependencies": {
            "ffmpeg": "required - check installation",
            "temp_directory": "accessible",
            "thread_pool": "active"
        },
        "endpoints_status": {
            "banner": "/api/v1/banner/health",
            "cut": "/api/v1/cut/health",
            "watermark": "/api/v1/watermark/health",
            "video_processing": "/api/v1/video/health",
            "green_screen": "/api/v1/green-screen/health",
            "audio": "/api/v1/audio/health"
        },
        "version": "1.0.0"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Handler global para capturar exceções não tratadas
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
