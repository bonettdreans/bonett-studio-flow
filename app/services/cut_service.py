import os
import subprocess
from typing import Optional, Callable


class CutService:
    @staticmethod
    def cut_video(
        input_path: str,
        output_path: str,
        start_time: str,
        end_time: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> str:
        """Corta vídeo entre os tempos especificados"""
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

        if progress_callback:
            progress_callback(
                f"Cortando vídeo de {start_time} até {end_time}...", 0.3)

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        cmd = [
            "ffmpeg", "-i", input_path,
            "-ss", start_time, "-to", end_time,
            "-c:v", "copy", "-c:a", "copy",
            "-y", output_path
        ]

        try:
            if progress_callback:
                progress_callback("Processando corte de vídeo...", 0.5)

            subprocess.run(cmd, check=True, capture_output=True, text=True)

            if progress_callback:
                progress_callback(
                    f"Vídeo cortado salvo em: {output_path}", 1.0)

            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erro ao cortar o vídeo: {e.stderr}")
