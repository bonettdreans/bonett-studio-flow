import os
import subprocess
import tempfile
import shutil
import ffmpeg
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor


class BannerService:
    _video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}
    _executor = ThreadPoolExecutor(max_workers=max(4, os.cpu_count() or 4))

    @staticmethod
    def add_banner(
        video_path: str,
        image_path: str,
        output_path: str,
        position: str = "top",
        banner_scale: float = 1.0,
        padding: int = 0,
        num_threads: int = None,  # Agora opcional
        segment_duration: int = None  # Agora opcional
    ) -> str:
        """
        Adiciona um banner a um vídeo criando uma área estendida para o banner usando processamento paralelo.

        Args:
            video_path (str): Caminho do vídeo de entrada
            image_path (str): Caminho da imagem do banner
            output_path (str): Caminho do vídeo de saída
            position (str): Posição do banner ('top', 'bottom')
            banner_scale (float): Fator de escala do banner (1.0 = 100% da largura do vídeo)
            padding (int): Padding em pixels do banner em relação à borda
            num_threads (int, optional): Número de threads para processamento paralelo. Se None, usa o executor compartilhado
            segment_duration (int, optional): Duração em segundos de cada segmento. Se None, calcula com base na duração do vídeo

        Returns:
            str: Caminho do vídeo de saída
        """
        def get_video_duration(video_path):
            """Obtém a duração do vídeo em segundos."""
            try:
                probe = ffmpeg.probe(video_path)
                duration = float(probe['format']['duration'])
                return duration
            except Exception as e:
                raise RuntimeError(f"Erro ao obter duração do vídeo: {str(e)}")

        def process_video_segment(args):
            """Processa um segmento de vídeo."""
            segment_path, image_path, output_path, position, banner_scale, padding, start_time, duration = args

            try:
                # Obter dimensões do vídeo original
                probe = ffmpeg.probe(segment_path)
                video_stream = next(
                    (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
                if not video_stream:
                    raise ValueError(
                        "Nenhuma stream de vídeo encontrada no arquivo.")

                video_width = int(video_stream['width'])
                video_height = int(video_stream['height'])

                # Obter dimensões do banner
                banner_probe = ffmpeg.probe(image_path)
                banner_stream = next(
                    (stream for stream in banner_probe['streams'] if stream['codec_type'] in ['video', 'image']), None)

                if banner_stream is None:
                    raise ValueError(
                        "Não foi possível ler as dimensões do banner.")

                # Calcular dimensões do banner redimensionado
                banner_width = int(video_width * banner_scale)
                original_banner_width = float(banner_stream.get(
                    'width', banner_stream.get('coded_width', video_width)))
                original_banner_height = float(banner_stream.get(
                    'height', banner_stream.get('coded_height', video_height)))
                banner_height = int(original_banner_height *
                                    (banner_width / original_banner_width))

                # Calcular nova altura total do vídeo
                new_height = video_height + banner_height + (padding * 2)

                # Input streams
                input_video = ffmpeg.input(
                    segment_path, ss=start_time, t=duration)
                input_banner = ffmpeg.input(image_path)

                # Extrair áudio do vídeo original
                audio = input_video.audio

                # Criar tela preta usando pad
                padded_video = ffmpeg.filter(
                    input_video,
                    'pad',
                    width=video_width,
                    height=new_height,
                    x='(out_w-in_w)/2',
                    y='0' if position == "bottom" else str(
                        banner_height + padding),
                    color='black'
                )

                # Redimensionar o banner
                scaled_banner = ffmpeg.filter(
                    input_banner,
                    'scale',
                    w=banner_width,
                    h=banner_height
                )

                # Calcular posição do banner
                banner_y = video_height + padding if position == "bottom" else padding

                # Aplicar overlay do banner
                final = ffmpeg.filter(
                    [padded_video, scaled_banner],
                    'overlay',
                    x=f'(main_w-overlay_w)/2',
                    y=str(banner_y)
                )

                # Criar vídeo final com áudio original
                stream = ffmpeg.output(
                    final,
                    audio,
                    output_path,
                    vcodec='libx264',
                    acodec='aac',
                    pix_fmt='yuv420p',
                    preset='medium',
                    crf=23
                )

                # Executar o comando para criar o vídeo final
                cmd = ffmpeg.compile(stream, overwrite_output=True)
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()

                if process.returncode != 0:
                    raise RuntimeError(
                        f"Erro ao processar segmento: {stderr.decode('utf-8', errors='ignore')}")

                return True
            except Exception as e:
                raise RuntimeError(f"Erro ao processar segmento: {str(e)}")

        try:
            # Validar arquivos de entrada
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Vídeo não encontrado: {video_path}")
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Imagem não encontrada: {image_path}")

            # Criar diretório temporário para armazenar segmentos
            temp_dir = tempfile.mkdtemp()

            # Obter a duração total do vídeo
            total_duration = get_video_duration(video_path)

            # Usar executor compartilhado se num_threads não for especificado
            if num_threads is None:
                executor = BannerService._executor
            else:
                executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=num_threads)

            # Ajustar segment_duration dinamicamente se não for especificado
            if segment_duration is None:
                # Ajuste dinâmico baseado na duração total do vídeo
                # Idealmente queremos entre 8-16 segmentos para paralelização eficiente
                target_segments = min(16, max(8, os.cpu_count() * 2))
                segment_duration = max(
                    30, int(total_duration / target_segments))
                # Garantir que segment_duration não seja muito pequeno ou muito grande
                segment_duration = min(120, max(30, segment_duration))

            # Dividir o vídeo em segmentos
            num_segments = max(1, int(total_duration // segment_duration) +
                               (1 if total_duration % segment_duration > 0 else 0))
            segment_files = []

            for i in range(num_segments):
                start_time = i * segment_duration
                current_duration = min(
                    segment_duration, total_duration - start_time)

                segment_output = os.path.join(temp_dir, f"segment_{i:03d}.mp4")
                segment_files.append(
                    (segment_output, start_time, current_duration))

                # Extrair segmento do vídeo original
                cmd = ffmpeg.input(video_path, ss=start_time, t=current_duration).output(
                    segment_output, c='copy').global_args('-loglevel', 'error', '-y').compile()

                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process.communicate()

            # Processar cada segmento em paralelo
            processed_segments = []
            tasks = []

            for i, (segment_path, start_time, duration) in enumerate(segment_files):
                output_segment = os.path.join(
                    temp_dir, f"processed_{i:03d}.mp4")
                processed_segments.append(output_segment)

                task = (segment_path, image_path, output_segment,
                        position, banner_scale, padding, 0, duration)
                tasks.append(task)

            success_count = 0
            # Usar o executor definido anteriormente
            results = list(executor.map(process_video_segment, tasks))
            success_count = sum(1 for r in results if r)

            # Limpar o executor criado localmente se necessário
            if num_threads is not None:
                executor.shutdown(wait=True)

            if success_count < len(tasks):
                raise RuntimeError(
                    "Alguns segmentos não foram processados corretamente")

            # Combinar segmentos em um único vídeo
            list_file = os.path.join(temp_dir, "file_list.txt")
            with open(list_file, 'w') as f:
                for segment in processed_segments:
                    f.write(f"file '{segment}'\n")

            # Concatenar segmentos
            concat_cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', list_file, '-c', 'copy', output_path
            ]

            process = subprocess.Popen(
                concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise RuntimeError(
                    f"Erro ao concatenar segmentos: {stderr.decode('utf-8', errors='ignore')}")

            return output_path

        except Exception as e:
            raise RuntimeError(f"Erro durante o processamento: {str(e)}")
        finally:
            # Limpar arquivos temporários
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                print(
                    f"Aviso: Não foi possível excluir o diretório temporário: {str(e)}")
