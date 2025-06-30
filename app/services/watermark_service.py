import os
import tempfile
import subprocess
import shutil


class WatermarkService:
    @staticmethod
    def add_watermark(
        video_path: str,
        watermark_path: str,
        output_path: str = None,
        opacity: float = 0.5,
        scale: float = 0.5
    ) -> str:
        """
        Adiciona marca d'água ao vídeo usando apenas FFmpeg (mais rápido e confiável)
        Se output_path for None ou igual ao video_path, usa um arquivo temporário e depois substitui o original.
        """
        temp_dir = None

        try:
            same_file = False
            if output_path is None or output_path == video_path:
                same_file = True
                temp_dir = tempfile.mkdtemp()
                temp_filename = os.path.basename(video_path)
                final_output = os.path.join(temp_dir, temp_filename)
                actual_output_path = video_path
            else:
                final_output = output_path
                actual_output_path = output_path

            os.makedirs(os.path.dirname(final_output), exist_ok=True)

            # Obter informações do vídeo original para preservar características
            probe_cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=width,height,r_frame_rate',
                '-of', 'csv=p=0',
                video_path
            ]

            try:
                probe_result = subprocess.check_output(
                    probe_cmd, universal_newlines=True).strip().split(',')
                width, height, framerate = probe_result
                print(f"Vídeo original: {width}x{height} a {framerate}fps")
            except Exception as e:
                print(
                    f"Aviso: Não foi possível obter informações do vídeo: {e}")
                width, height, framerate = None, None, None

            cmd = [
                'ffmpeg',
                '-y',  # Sobrescrever arquivo de saída se existir
                '-i', video_path,  # Vídeo original
                '-i', watermark_path,  # Imagem da marca d'água
                '-filter_complex',
                # Aplicar transparência à marca d'água
                '[1:v]format=rgba,colorchannelmixer=aa={:.1f}[watermark];'.format(opacity) +
                # Redimensionar marca d'água
                '[watermark]scale=iw*{:.1f}:ih*{:.1f}[watermarkscaled];'.format(scale, scale) +
                # Centralizar
                '[0:v][watermarkscaled]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:format=auto[outv]',
                '-map', '[outv]',  # Usar o vídeo processado
                '-map', '0:a?',  # Manter áudio original se existir
                '-c:v', 'libx264',  # Codec de vídeo
                '-crf', '23',  # Qualidade de vídeo (menor = melhor qualidade)
                '-preset', 'medium',  # Balancear velocidade e qualidade
                '-c:a', 'aac',  # Converter áudio para AAC para melhor compatibilidade
                '-b:a', '192k',  # Bitrate de áudio
                '-pix_fmt', 'yuv420p',  # Formato de pixel para máxima compatibilidade
                '-movflags', '+faststart',
            ]

            if framerate:
                cmd.extend(['-r', framerate])

            cmd.append(final_output)

            print(f"Executando comando FFmpeg: {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )

            stderr_output = []
            for line in process.stderr:
                print(f"FFmpeg: {line.strip()}")
                stderr_output.append(line)

            return_code = process.wait()

            if return_code != 0:
                error_msg = ''.join(stderr_output)
                print(f"Erro FFmpeg (código {return_code}): {error_msg}")
                raise RuntimeError(
                    f"FFmpeg falhou com código {return_code}: {error_msg}")

            if not os.path.exists(final_output) or os.path.getsize(final_output) == 0:
                raise RuntimeError(
                    f"O arquivo de saída não foi criado corretamente: {final_output}")

            if same_file:
                print(
                    f"Substituindo o arquivo original ({video_path}) com a versão com marca d'água")
                if os.path.exists(video_path):
                    os.remove(video_path)
                shutil.move(final_output, video_path)
                print(f"Arquivo original substituído com sucesso")

            try:
                check_cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-select_streams', 'v:0',
                    '-show_entries', 'stream=codec_name',
                    '-of', 'csv=p=0',
                    actual_output_path
                ]
                codec_info = subprocess.check_output(
                    check_cmd, universal_newlines=True).strip()
                print(f"Vídeo processado com sucesso. Codec: {codec_info}")
            except Exception as e:
                print(f"Aviso: Não foi possível verificar o vídeo final: {e}")

            print(
                f"Vídeo com marca d'água criado com sucesso: {actual_output_path}")
            return actual_output_path

        except Exception as e:
            raise RuntimeError(f"Erro ao processar vídeo: {str(e)}")
        finally:
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
