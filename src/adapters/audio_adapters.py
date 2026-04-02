"""
音频处理器适配器
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional
import subprocess
import logging

from ..entities import EngineResult
from ..use_cases.tts_use_cases import AudioProcessorInterface


logger = logging.getLogger(__name__)


class FFmpegAudioProcessor(AudioProcessorInterface):
    """
    FFmpeg 音频处理器适配器

    职责：
    - 实现 AudioProcessorInterface
    - 调用 FFmpeg 命令
    - 并行处理音频任务
    """

    def __init__(self, max_workers: int = 4):
        """
        初始化 FFmpeg 音频处理器

        Args:
            max_workers: 最大并行工作线程数
        """
        self.max_workers = max_workers
        self._executor: Optional[ThreadPoolExecutor] = None

    @property
    def executor(self) -> ThreadPoolExecutor:
        """延迟初始化线程池"""
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self._executor

    def merge_audio_files(
        self,
        audio_files: List[Path],
        output_file: Path,
        pan_list: Optional[List[float]] = None,
        bgm_file: Optional[Path] = None,
        sample_rate: int = 32000,
    ) -> EngineResult:
        """
        合并多个音频文件（支持立体声定位和 BGM 混音）

        Args:
            audio_files: 音频文件列表
            output_file: 输出文件路径
            pan_list: 每段的声道值（-1.0=左, 0.0=中, 1.0=右）
            bgm_file: 背景音乐文件路径
            sample_rate: 采样率

        Returns:
            EngineResult: 处理结果
        """
        if not audio_files:
            return EngineResult.failure("音频文件列表为空")

        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            has_pan = pan_list and len(pan_list) == len(audio_files)
            has_bgm = bgm_file is not None and bgm_file.exists()

            # ---- 单文件或无特效：直接复制 ----
            if len(audio_files) == 1 and not has_pan and not has_bgm:
                output_file.write_bytes(audio_files[0].read_bytes())
                return EngineResult.success(
                    file_path=output_file,
                    duration=self._get_duration(output_file),
                    engine_name="ffmpeg",
                )

            # ---- 构建 filter_complex ----
            filter_parts: List[str] = []
            concat_inputs = ""

            for i, audio_file in enumerate(audio_files):
                pan_val = pan_list[i] if has_pan else 0.0
                # stereo pan: distribute mono input across L/R
                # pan=stereo|c0=<gain_left>|c1=<gain_right>
                gain_l = max(0.0, (1.0 - pan_val) / 2)
                gain_r = max(0.0, (1.0 + pan_val) / 2)
                filter_parts.append(
                    f"[{i}:a]pan=stereo|c0={gain_l:.3f}*c0|c1={gain_r:.3f}*c0[a{i}]"
                )
                concat_inputs += f"[a{i}]"

            if len(audio_files) > 1:
                filter_parts.append(f"{concat_inputs}concat=n={len(audio_files)}:v=0:a=1[out]")

            if has_bgm:
                # Mix dialogue output with BGM at 60% volume
                if filter_parts:
                    last_filter = filter_parts[-1]
                    last_label = f"[out]"
                    # Replace concat output to include BGM
                    filter_parts[-1] = (
                        f"{concat_inputs}concat=n={len(audio_files)}:v=0:a=1[pre];"
                        f"[pre]volume=1.0[pre];"
                        f"[{len(audio_files)}:a]volume=0.4[bgm];"
                        f"[pre][bgm]amix=inputs=2:duration=first[out]"
                    )
                else:
                    filter_parts.append(
                        f"[0:a]volume=1.0[pre];"
                        f"[{len(audio_files)}:a]volume=0.4[bgm];"
                        f"[pre][bgm]amix=inputs=2:duration=first[out]"
                    )

            filter_complex = ";".join(filter_parts)
            all_inputs = [str(f) for f in audio_files]
            if has_bgm:
                all_inputs.append(str(bgm_file))

            cmd = [
                "ffmpeg",
                "-y",
                *sum([["-i", p] for p in all_inputs], []),
                "-filter_complex",
                filter_complex,
                "-map",
                "[out]",
                "-ar",
                str(sample_rate),
                "-ac",
                "2",
                "-q:a",
                "2",
                str(output_file),
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=120
            )

            duration = self._get_duration(output_file)
            return EngineResult.success(
                file_path=output_file, duration=duration, engine_name="ffmpeg"
            )

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg 合并失败: {e.stderr}")
            return EngineResult.failure(
                f"FFmpeg 合并失败: {e.stderr}", engine_name="ffmpeg"
            )
        except Exception as e:
            logger.error(f"音频合并异常: {str(e)}")
            return EngineResult.failure(
                f"音频合并异常: {str(e)}", engine_name="ffmpeg"
            )

    def convert_format(
        self, input_file: Path, output_file: Path, format: str = "mp3"
    ) -> EngineResult:
        """
        转换音频格式

        Args:
            input_file: 输入文件
            output_file: 输出文件
            format: 目标格式

        Returns:
            EngineResult: 处理结果
        """
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                "ffmpeg",
                "-i",
                str(input_file),
                "-c:a",
                "libmp3lame" if format == "mp3" else "copy",
                "-y",
                str(output_file),
            ]

            subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)

            duration = self._get_duration(output_file)
            return EngineResult.success(
                file_path=output_file, duration=duration, engine_name="ffmpeg"
            )

        except Exception as e:
            return EngineResult.failure(
                f"格式转换失败: {str(e)}", engine_name="ffmpeg"
            )

    def adjust_volume(
        self, input_file: Path, output_file: Path, volume: float = 1.0
    ) -> EngineResult:
        """
        调整音量

        Args:
            input_file: 输入文件
            output_file: 输出文件
            volume: 音量倍数

        Returns:
            EngineResult: 处理结果
        """
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                "ffmpeg",
                "-i",
                str(input_file),
                "-af",
                f"volume={volume}",
                "-y",
                str(output_file),
            ]

            subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)

            duration = self._get_duration(output_file)
            return EngineResult.success(
                file_path=output_file, duration=duration, engine_name="ffmpeg"
            )

        except Exception as e:
            return EngineResult.failure(
                f"音量调整失败: {str(e)}", engine_name="ffmpeg"
            )

    def _get_duration(self, audio_file: Path) -> float:
        """
        获取音频时长（使用共享工具，带回退估算）

        Args:
            audio_file: 音频文件

        Returns:
            float: 时长（秒）
        """
        try:
            # 延迟导入避免循环依赖
            from services.audio_utils import get_duration
            return get_duration(audio_file)
        except Exception:
            # 估算时长（假设 128kbps MP3）
            file_size = audio_file.stat().st_size
            bitrate = 128 * 1024 / 8
            return file_size / bitrate

    def batch_process(
        self,
        tasks: List[dict],
        timeout: Optional[float] = 300.0,
    ) -> List[EngineResult]:
        """
        批量并行处理音频任务

        Args:
            tasks: 任务列表，每个任务是一个字典，包含:
                   - method: 方法名（merge, convert, adjust_volume）
                   - args: 参数字典
            timeout: 单个任务超时时间（秒），默认 300

        Returns:
            List[EngineResult]: 结果列表
        """
        futures = []

        for task in tasks:
            method = task.get("method")
            args = task.get("args", {})

            if method == "merge":
                future = self.executor.submit(self.merge_audio_files, **args)
            elif method == "convert":
                future = self.executor.submit(self.convert_format, **args)
            elif method == "adjust_volume":
                future = self.executor.submit(self.adjust_volume, **args)
            else:
                logger.warning(f"未知方法: {method}")
                # 添加失败结果代替 future
                futures.append(None)
                continue

            futures.append(future)

        # 等待所有任务完成，收集结果
        results: List[EngineResult] = []
        for future in futures:
            if future is None:
                results.append(EngineResult.failure(f"未知方法: {method}"))
                continue

            try:
                result = future.result(timeout=timeout)
                results.append(result)
            except TimeoutError:
                logger.error(f"任务超时: {timeout}秒")
                results.append(EngineResult.failure(f"任务执行超时: {timeout}秒"))
            except Exception as e:
                logger.error(f"任务执行异常: {str(e)}")
                results.append(EngineResult.failure(f"任务执行异常: {str(e)}"))

        return results

    def cleanup(self):
        """清理资源"""
        if self._executor is not None:
            self._executor.shutdown(wait=True)
            self._executor = None
