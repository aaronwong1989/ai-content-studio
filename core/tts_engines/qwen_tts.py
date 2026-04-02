"""
Qwen TTS 引擎实现 (qwen3-tts-flash)
专用语音合成引擎，49种音色 + 8大方言，0.001元/字符
关键：qwen-tts-flash 使用独立 API 端点（非 Chat Completions）
"""
import base64
import json
import logging
import requests
from typing import Optional, List, Dict, Any

from .base import BaseTTSEngine

logger = logging.getLogger(__name__)


class QwenTTSEngine(BaseTTSEngine):
    """Qwen TTS 引擎（专用 TTS API）"""

    DEFAULT_MODEL = "qwen3-tts-flash"
    DEFAULT_VOICE = "Aurora"
    SAMPLE_RATE = 16000

    # 音色名称标准化映射（统一转为小写，API 需要小写音色名）
    VOICE_ALIASES = {
        v: v.lower() for v in [
            "Aurora", "Nannuann", "Clara", "Terri", "Harry", "Eric", "Emma",
            "Ada", "Alice", "Emily", "Hannah", "Cherry", "Vera", "Bella", "Luna",
            "Lily", "Ruby", "Coco", "Andy", "Amy", "Daisy", "Sophia",
            "Dylan", "Jada", "Sunny",
        ]
    }
    # 确保小写 key 也能用
    VOICE_ALIASES.update({
        v.lower(): v.lower() for v in VOICE_ALIASES.values()
    })

    # 支持的语言
    SUPPORTED_LANGUAGES = [
        "Auto",  # 自动检测
        "zh",    # 中文
        "en",    # 英文
        "yue",   # 粤语
        "sh",    # 上海话
        "sichuan",  # 四川话
        "tianjin",  # 天津话
        "wu",    # 吴语
    ]

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        default_voice: Optional[str] = None,
        **kwargs
    ):
        super().__init__(api_key, base_url, **kwargs)
        self.model = model or self.DEFAULT_MODEL
        self.default_voice = self._normalize_voice(default_voice or self.DEFAULT_VOICE)

        # Qwen TTS 使用独立的 API 端点
        if self.base_url:
            # 从 OpenAI 兼容端点转换为原生端点
            self.api_endpoint = self.base_url.replace("/compatible-mode/v1", "").rstrip("/")
        else:
            self.api_endpoint = "https://dashscope.aliyuncs.com"

    def synthesize(
        self,
        text: str,
        output_file: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        language: str = "Auto",
        **kwargs
    ) -> bool:
        """
        合成语音

        Args:
            text: 待合成文本
            output_file: 输出文件路径
            voice: 音色 ID
            speed: 语速
            language: 语言类型（Auto/zh/en/yue/sh/sichuan/tianjin/wu）
            **kwargs: 其他参数

        Returns:
            成功返回 True，失败返回 False
        """
        audio_bytes = self._synthesize_api(
            text=text,
            voice=voice or self.default_voice,
            speed=speed,
            language=language
        )

        if audio_bytes:
            try:
                # Qwen TTS 返回 WAV 格式
                import subprocess
                from pathlib import Path

                out_path = Path(output_file)
                if out_path.suffix.lower() == ".mp3":
                    # 先写 WAV，再转 MP3
                    wav_path = out_path.with_suffix(".wav")
                    with open(wav_path, "wb") as f:
                        f.write(audio_bytes)
                    subprocess.run(
                        ["ffmpeg", "-y", "-i", str(wav_path),
                         "-codec:a", "libmp3lame", "-b:a", "128k", str(out_path)],
                        capture_output=True,
                        check=True
                    )
                    wav_path.unlink(missing_ok=True)
                else:
                    with open(out_path, "wb") as f:
                        f.write(audio_bytes)

                logger.info(f"音频已保存: {output_file}")
                return True
            except Exception as e:
                logger.error(f"保存音频失败: {e}")
                return False

        return False

    def _synthesize_api(
        self,
        text: str,
        voice: str,
        speed: float = 1.0,
        language: str = "Auto"
    ) -> Optional[bytes]:
        """
        Qwen TTS API 调用

        Args:
            text: 待合成文本
            voice: 音色 ID
            speed: 语速
            language: 语言类型

        Returns:
            音频字节数据（WAV），失败返回 None
        """
        if not self.api_key:
            logger.error("未配置 DashScope API Key")
            return None

        voice_id = self._normalize_voice(voice).lower()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable"
        }

        payload = {
            "model": self.model,
            "input": {
                "text": text,
                "voice": voice_id,
                "language_type": language if language != "Auto" else "Auto"
            }
        }

        try:
            # Qwen TTS 使用独立的 API 端点
            url = f"{self.api_endpoint}/api/v1/services/aigc/multimodal-generation/generation"

            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=60,
                stream=True
            )

            # 检查状态码
            if resp.status_code != 200:
                logger.error(f"API 请求失败 ({resp.status_code}): {resp.text[:200]}")
                resp.raise_for_status()

            # 解析 SSE 响应
            audio_base64_chunks = []
            for line in resp.iter_lines():
                if not line or not line.startswith(b"data:"):
                    continue

                chunk_str = line.decode("utf-8")[5:].strip()
                if not chunk_str:
                    continue

                try:
                    chunk = json.loads(chunk_str)
                    audio_obj = chunk.get("output", {}).get("audio", {})
                    audio_data = audio_obj.get("data")
                    if audio_data:
                        audio_base64_chunks.append(audio_data)
                except json.JSONDecodeError:
                    continue

            if not audio_base64_chunks:
                logger.error("响应中未包含音频数据")
                return None

            # 合并所有音频分片
            full_b64 = "".join(audio_base64_chunks)
            audio_bytes = base64.b64decode(full_b64)

            logger.info(f"合成成功 ({len(audio_bytes):,} bytes, {len(text)} chars)")
            return audio_bytes

        except Exception as e:
            logger.error(f"Qwen TTS 调用失败: {e}")
            return None

    def _normalize_voice(self, voice: str) -> str:
        """标准化音色名称"""
        if not voice:
            return "Aurora"
        lower = voice.lower()
        return self.VOICE_ALIASES.get(lower, voice)

    def is_available(self) -> bool:
        """检查引擎是否可用"""
        return self.api_key is not None

    def get_supported_voices(self) -> list:
        """获取支持的音色列表"""
        return list(self.VOICE_ALIASES.keys())

    def get_supported_languages(self) -> list:
        """获取支持的语言列表"""
        return self.SUPPORTED_LANGUAGES.copy()

    def get_info(self) -> Dict[str, Any]:
        """获取引擎信息"""
        info = super().get_info()
        info["model"] = self.model
        info["default_voice"] = self.default_voice
        info["sample_rate"] = self.SAMPLE_RATE
        info["supported_languages"] = self.SUPPORTED_LANGUAGES
        return info
