import os
import subprocess
import tempfile
import json
import shutil
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Callable


class VideoProcessor:
    _video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"}
    _executor = ThreadPoolExecutor(max_workers=max(4, os.cpu_count() or 4))

    @staticmethod
    def create_cyclic_video(
        video_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> dict:
        """
        Versão corrigida que resolve problemas de áudio e congelamento de vídeo.
        """

        FAST_DURATION = 25      # Duração de cada seção acelerada em segundos
        NORMAL_DURATION = 12    # Duração de cada seção normal em segundos
        FAST_SPEED = 4          # Aceleração (4x mais rápido)
        CYCLE_DURATION = FAST_DURATION + NORMAL_DURATION  # 37s por ciclo

        temp_dir = None

        try:
            video_path = os.path.abspath(video_path)
            output_path = os.path.abspath(output_path)

            if video_path == output_path:
                base, ext = os.path.splitext(output_path)
                output_path = f"{base}_cyclic{ext}"

            if not os.path.exists(video_path):
                raise FileNotFoundError(
                    f"Arquivo não encontrado: {video_path}")

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            if progress_callback:
                progress_callback("Iniciando análise do vídeo...", 0.05)

            cmd_probe = [
                "ffprobe", "-v", "quiet", "-print_format", "json",
                "-show_format", "-show_streams", video_path
            ]

            result = subprocess.run(
                cmd_probe, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                raise RuntimeError("Erro ao analisar vídeo")

            probe_data = json.loads(result.stdout)
            duration = float(probe_data['format']['duration'])

            video_stream = None
            for stream in probe_data['streams']:
                if stream['codec_type'] == 'video':
                    video_stream = stream
                    break

            if not video_stream:
                raise RuntimeError("Stream de vídeo não encontrado")

            fps_str = video_stream.get('r_frame_rate', '30/1')
            if '/' in fps_str:
                num, den = map(int, fps_str.split('/'))
                fps = num / den if den != 0 else 30
            else:
                fps = float(fps_str)

            if progress_callback:
                progress_callback(
                    f"Vídeo: {fps:.2f} FPS, {duration:.2f}s", 0.1)

            temp_dir = tempfile.mkdtemp(prefix="cyclic_video_")

            num_cycles = max(1, int(duration // CYCLE_DURATION))
            total_output_duration = 0

            video_segments = []
            audio_segments = []

            for cycle in range(num_cycles):
                cycle_start = cycle * CYCLE_DURATION

                fast_start = cycle_start
                fast_end = min(cycle_start + FAST_DURATION, duration)
                fast_duration = fast_end - fast_start

                if fast_duration > 0.5:
                    output_fast_duration = fast_duration / FAST_SPEED
                    video_segments.append({
                        'input_start': fast_start,
                        'input_duration': fast_duration,
                        'output_start': total_output_duration,
                        'output_duration': output_fast_duration,
                        'speed': FAST_SPEED,
                        'type': 'fast'
                    })
                    total_output_duration += output_fast_duration

                normal_start = cycle_start + FAST_DURATION
                normal_end = min(cycle_start + CYCLE_DURATION, duration)
                normal_duration = normal_end - normal_start

                if normal_duration > 0.5:
                    video_segments.append({
                        'input_start': normal_start,
                        'input_duration': normal_duration,
                        'output_start': total_output_duration,
                        'output_duration': normal_duration,
                        'speed': 1.0,
                        'type': 'normal'
                    })

                    audio_segments.append({
                        'input_start': normal_start,
                        'input_duration': normal_duration,
                        'output_start': total_output_duration,
                        'output_duration': normal_duration
                    })

                    total_output_duration += normal_duration

            if progress_callback:
                progress_callback(
                    f"Planejados {len(video_segments)} segmentos de vídeo", 0.15)

            segment_files = []

            for i, segment in enumerate(video_segments):
                segment_file = os.path.join(temp_dir, f"segment_{i:03d}.mp4")

                if segment['type'] == 'fast':
                    cmd_segment = [
                        'ffmpeg', '-y',
                        '-ss', str(segment['input_start']),
                        '-t', str(segment['input_duration']),
                        '-i', video_path,
                        '-vf', f'setpts=PTS/{segment["speed"]}',
                        '-an',
                        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                        segment_file
                    ]
                else:
                    cmd_segment = [
                        'ffmpeg', '-y',
                        '-ss', str(segment['input_start']),
                        '-t', str(segment['input_duration']),
                        '-i', video_path,
                        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                        '-an',
                        segment_file
                    ]

                result = subprocess.run(
                    cmd_segment, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"Erro no segmento {i}: {result.stderr}")
                    continue

                if os.path.exists(segment_file):
                    segment_files.append(segment_file)

                if progress_callback:
                    progress = 0.15 + 0.4 * ((i + 1) / len(video_segments))
                    progress_callback(
                        f"Processando segmento {i+1}/{len(video_segments)}", progress)

            if not segment_files:
                raise RuntimeError(
                    "Nenhum segmento de vídeo foi criado com sucesso")

            temp_video = os.path.join(temp_dir, "concatenated_video.mp4")
            concat_file = os.path.join(temp_dir, 'video_concat.txt')

            with open(concat_file, 'w', encoding='utf-8') as f:
                for segment_file in segment_files:
                    abs_path = os.path.abspath(segment_file).replace('\\', '/')
                    f.write(f"file '{abs_path}'\n")

            cmd_concat = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                temp_video
            ]

            result = subprocess.run(cmd_concat, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(
                    f"Erro na concatenação de vídeo: {result.stderr}")

            if progress_callback:
                progress_callback("Processando áudio...", 0.6)

            temp_audio = os.path.join(temp_dir, "final_audio.wav")

            if audio_segments:
                cmd_silence = [
                    'ffmpeg', '-y', '-f', 'lavfi',
                    '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                    '-t', str(total_output_duration),
                    '-c:a', 'pcm_s16le',
                    temp_audio
                ]

                result = subprocess.run(
                    cmd_silence, capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(
                        "Erro ao criar base de áudio silencioso")

                audio_files_to_mix = [temp_audio]

                for i, segment in enumerate(audio_segments):
                    segment_audio = os.path.join(
                        temp_dir, f"audio_segment_{i}.wav")
                    positioned_audio = os.path.join(
                        temp_dir, f"positioned_audio_{i}.wav")

                    cmd_extract = [
                        'ffmpeg', '-y',
                        '-ss', str(segment['input_start']),
                        '-t', str(segment['input_duration']),
                        '-i', video_path,
                        '-vn', '-c:a', 'pcm_s16le', '-ar', '44100', '-ac', '2',
                        segment_audio
                    ]

                    result = subprocess.run(
                        cmd_extract, capture_output=True, text=True)
                    if result.returncode != 0:
                        continue

                    if segment['output_start'] > 0:
                        cmd_position = [
                            'ffmpeg', '-y',
                            '-f', 'lavfi', '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                            '-i', segment_audio,
                            '-filter_complex',
                            f'[0]atrim=duration={segment["output_start"]}[silence];'
                            f'[silence][1]concat=n=2:v=0:a=1[positioned]',
                            '-map', '[positioned]',
                            '-t', str(total_output_duration),
                            '-c:a', 'pcm_s16le',
                            positioned_audio
                        ]
                    else:
                        cmd_position = [
                            'ffmpeg', '-y',
                            '-i', segment_audio,
                            '-af', f'apad=whole_dur={total_output_duration}',
                            '-c:a', 'pcm_s16le',
                            positioned_audio
                        ]

                    result = subprocess.run(
                        cmd_position, capture_output=True, text=True)
                    if result.returncode == 0 and os.path.exists(positioned_audio):
                        audio_files_to_mix.append(positioned_audio)

                    if progress_callback:
                        progress = 0.6 + 0.2 * ((i + 1) / len(audio_segments))
                        progress_callback(
                            f"Processando áudio {i+1}/{len(audio_segments)}", progress)

                if len(audio_files_to_mix) > 1:
                    mixed_audio = os.path.join(temp_dir, "mixed_audio.wav")

                    input_args = []
                    for audio_file in audio_files_to_mix:
                        input_args.extend(['-i', audio_file])

                    cmd_mix = [
                        'ffmpeg', '-y'
                    ] + input_args + [
                        '-filter_complex', f'amix=inputs={len(audio_files_to_mix)}:duration=longest:dropout_transition=0',
                        '-c:a', 'pcm_s16le',
                        mixed_audio
                    ]

                    result = subprocess.run(
                        cmd_mix, capture_output=True, text=True)
                    if result.returncode == 0:
                        temp_audio = mixed_audio
            else:
                cmd_silence = [
                    'ffmpeg', '-y', '-f', 'lavfi',
                    '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100',
                    '-t', str(total_output_duration),
                    '-c:a', 'pcm_s16le',
                    temp_audio
                ]
                subprocess.run(cmd_silence, capture_output=True, text=True)

            if progress_callback:
                progress_callback("Combinando vídeo e áudio...", 0.9)

            cmd_final = [
                'ffmpeg', '-y',
                '-i', temp_video,
                '-i', temp_audio,
                '-c:v', 'copy',
                '-c:a', 'aac', '-b:a', '128k',
                '-shortest',
                output_path
            ]

            result = subprocess.run(cmd_final, capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(
                    f"Erro na combinação final: {result.stderr}")

            if not os.path.exists(output_path):
                raise RuntimeError("Arquivo final não foi criado")

            if progress_callback:
                progress_callback("Processamento concluído!", 1.0)

            return {
                "success": True,
                "message": "Vídeo cíclico criado com sucesso",
                "output_path": output_path,
                "stats": {
                    "original_duration": duration,
                    "final_duration": total_output_duration,
                    "cycles_processed": num_cycles,
                    "video_segments": len(video_segments),
                    "audio_segments": len(audio_segments)
                }
            }

        except Exception as e:
            if progress_callback:
                progress_callback(f"ERRO: {str(e)}", 1.0)

            return {
                "success": False,
                "message": f"Erro no processamento: {str(e)}",
                "output_path": None
            }

        finally:
            # Limpeza do diretório temporário
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception:
                    pass
