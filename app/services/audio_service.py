import os
import subprocess
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor


class AudioService:
    _video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}
    _executor = ThreadPoolExecutor(max_workers=max(4, os.cpu_count() or 4))

    @staticmethod
    def mix_audio_with_video(video_path: str, audio_path: str, replace_original: bool = True, reduce_original_volume: bool = False):
        """
        Mescla um arquivo de áudio MP3 com um vídeo e opcionalmente reduz o volume do áudio original.
        O áudio será cortado para corresponder exatamente à duração do vídeo.

        Args:
            video_path: Caminho para o arquivo de vídeo
            audio_path: Caminho para o arquivo de áudio MP3
            replace_original: Se True, substitui o arquivo original. Se False, cria um novo arquivo.
            reduce_original_volume: Se True, reduz o volume do áudio original do vídeo

        Returns:
            str: Caminho do arquivo de saída processado
        """
        # Verifica se os arquivos de entrada existem
        if not os.path.exists(video_path):
            raise FileNotFoundError(
                f"Arquivo de vídeo não encontrado: {video_path}")

        if not os.path.exists(audio_path):
            raise FileNotFoundError(
                f"Arquivo de áudio não encontrado: {audio_path}")

        # Determina o caminho de saída final
        final_output_path = video_path if replace_original else AudioService._generate_output_path(
            video_path)

        # Cria um arquivo temporário para o processamento
        temp_dir = tempfile.gettempdir()
        temp_filename = f"temp_{os.path.basename(video_path)}"
        temp_output_path = os.path.join(temp_dir, temp_filename)

        try:
            # Comando FFmpeg baseado no parâmetro reduce_original_volume
            if reduce_original_volume:
                # Reduz o volume do áudio original para 0.2 (20%) e adiciona o novo áudio
                # Usando 'shortest=1' para garantir que o áudio termine quando o vídeo terminar
                cmd = [
                    "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
                    "-filter_complex", "[0:a]volume=0.2[a1];[a1][1:a]amix=inputs=2:duration=shortest[aout]",
                    "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-strict", "experimental",
                    "-shortest",  # Adiciona flag shortest para cortar na duração do vídeo
                    temp_output_path
                ]
            else:
                # Apenas adiciona o novo áudio sem reduzir o volume original
                # Usando 'shortest=1' para garantir que o áudio termine quando o vídeo terminar
                cmd = [
                    "ffmpeg", "-y", "-i", video_path, "-i", audio_path,
                    "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest[aout]",
                    "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-strict", "experimental",
                    "-shortest",  # Adiciona flag shortest para cortar na duração do vídeo
                    temp_output_path
                ]

            # Executa o comando FFmpeg
            print(f"Executando comando: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)

            # Se for para substituir o original, copia o arquivo temporário sobre o original
            if replace_original:
                print(f"Substituindo arquivo original: {video_path}")
                # Em alguns sistemas, é necessário remover o arquivo de destino antes
                if os.path.exists(video_path):
                    os.remove(video_path)
                shutil.move(temp_output_path, video_path)
            else:
                # Se não for para substituir, move para o caminho de saída final
                if not os.path.exists(os.path.dirname(final_output_path)):
                    os.makedirs(os.path.dirname(
                        final_output_path), exist_ok=True)
                shutil.move(temp_output_path, final_output_path)

            print(f"Processamento concluído: {final_output_path}")
            return final_output_path

        except subprocess.CalledProcessError as e:
            error_msg = f"Erro ao processar vídeo com FFmpeg: {str(e)}"
            print(error_msg)
            # Limpar arquivo temporário em caso de erro
            if os.path.exists(temp_output_path):
                try:
                    os.remove(temp_output_path)
                except:
                    pass
            raise RuntimeError(error_msg)

        except Exception as e:
            error_msg = f"Erro durante o processamento: {str(e)}"
            print(error_msg)
            # Limpar arquivo temporário em caso de erro
            if os.path.exists(temp_output_path):
                try:
                    os.remove(temp_output_path)
                except:
                    pass
            raise RuntimeError(error_msg)

    @staticmethod
    def _generate_output_path(video_path):
        """Gera um caminho de saída baseado no caminho de entrada"""
        dir_name = os.path.dirname(video_path)
        file_name = os.path.basename(video_path)
        name, ext = os.path.splitext(file_name)

        output_path = os.path.join(dir_name, f"{name}_mixed{ext}")

        # Se por acaso esse arquivo já existir, adiciona um contador
        counter = 1
        while os.path.exists(output_path):
            output_path = os.path.join(
                dir_name, f"{name}_mixed_{counter}{ext}")
            counter += 1

        return output_path

    @staticmethod
    def mix_audio_with_video_threaded(video_path: str, audio_path: str, replace_original: bool = True, reduce_original_volume: bool = False):
        """
        Versão do mix_audio_with_video que utiliza o thread pool para processamento paralelo.
        Aguarda a conclusão do processamento antes de retornar.

        Returns:
            str: Caminho do arquivo de saída processado
        """
        future = AudioService._executor.submit(
            AudioService.mix_audio_with_video,
            video_path,
            audio_path,
            replace_original,
            reduce_original_volume
        )

        # Aguarda a conclusão e retorna o resultado ou levanta a exceção
        try:
            return future.result()  # Isso vai bloquear até o processamento terminar
        except Exception as e:
            # Re-levanta a exceção para ser tratada pelo endpoint
            raise e
