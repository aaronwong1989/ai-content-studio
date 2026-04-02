"""
Qwen Omni TTS 引擎实现 (qwen3-omni-flash)
基于 DashScope OpenAI 兼容接口，支持全模态原生语音生成
关键：Qwen-Omni 必须使用 stream=True 才能返回音频数据
"""
import base64
import json
import logging
import requests
from typing import Optional, List, Dict, Any

from .base import BaseTTSEngine
from services.sse_parser import parse_sse_audio_stream
from scripts.studio.audio_utils import make_wav_header

logger = logging.getLogger(__name__)


class QwenOmniTTSEngine(BaseTTSEngine):
    """Qwen Omni TTS 引擎"""

    DEFAULT_MODEL = "qwen3-omni-flash"
    DEFAULT_VOICE = "cherry"
    SAMPLE_RATE = 24000

    # 支持的音色列表
    SUPPORTED_VOICES = [
        "cherry",
        "ethan",
        "chelsie",
        # 更多音色见：https://help.aliyun.com/zh/model-studio/omni-voice-list
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
        self.default_voice = default_voice or self.DEFAULT_VOICE

    def synthesize(
        self,
        text: str,
        output_file: str,
        voice: Optional[str] = None,
        system_prompt: Optional[str] = None,
        format: str = "wav",
        **kwargs
    ) -> bool:
        """
        合成语音

        Args:
            text: 待合成文本
            output_file: 输出文件路径
            voice: 音色 ID
            system_prompt: 系统提示词（用于稳定语音风格）
            format: 输出格式（wav/mp3）
            **kwargs: 其他参数

        Returns:
            成功返回 True，失败返回 False
        """
        audio_bytes = self._synthesize_stream(
            text=text,
            voice=voice or self.default_voice,
            system_prompt=system_prompt,
            format=format
        )

        if audio_bytes:
            try:
                with open(output_file, "wb") as f:
                    f.write(audio_bytes)
                logger.info(f"音频已保存: {output_file}")
                return True
            except Exception as e:
                logger.error(f"保存音频失败: {e}")
                return False

        return False

    def _synthesize_stream(
        self,
        text: str,
        voice: str,
        system_prompt: Optional[str] = None,
        format: str = "wav"
    ) -> Optional[bytes]:
        """
        流式合成语音（Qwen Omni 必须使用流式 API）

        Args:
            text: 待合成文本
            voice: 音色 ID
            system_prompt: 系统提示词
            format: 输出格式

        Returns:
            音频字节数据，失败返回 None
        """
        if not self.api_key:
            logger.error("未配置 DashScope API Key")
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构造消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            # 默认系统提示词，用于稳定语音风格
            messages.append({
                "role": "system",
                "content": "You are a professional voice-over reader. You output ONLY the exact text you are asked to read. Zero extra words. No greetings. No conclusions. No questions. Read exactly what is provided."
            })

        messages.append({
            "role": "user",
            "content": f"Read aloud the following text exactly, word for word, with no additions:\n{text}"
        })

        # Qwen Omni 只支持 wav/pcm，不支持 mp3
        audio_format = "wav" if format == "mp3" else format

        payload = {
            "model": self.model,
            "messages": messages,
            "modalities": ["text", "audio"],
            "audio": {
                "voice": voice,
                "format": audio_format
            },
            "stream": True,
            "stream_options": {"include_usage": True}
        }

        try:
            # 流式读取 SSE 响应（使用统一的 SSE 解析器）
            with requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120,
                stream=True
            ) as resp:
                if not resp.ok:
                    logger.error(f"API 请求失败 ({resp.status_code}): {resp.text[:200]}")
                    resp.raise_for_status()

                # 使用统一的 SSE 解析器
                audio_chunks, response_text = parse_sse_audio_stream(
                    resp,
                    get_audio_data=lambda chunk: (
                        chunk.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("audio", {})
                        .get("data")
                    ),
                    get_text_content=lambda chunk: (
                        chunk.get("choices", [{}])[0]
                        .get("delta", {})
                        .get("content")
                    )
                )

            if not audio_chunks:
                logger.error(f"响应中未包含音频数据。文本回复: {response_text[:200]}")
                return None

            # 分块解码后拼接字节（避免字符串拼接的 O(n²) 复杂度）
            audio_bytes_list = [
                base64.b64decode(chunk) for chunk in audio_chunks
            ]
            pcm_data = b"".join(audio_bytes_list)

            # 使用现有的 make_wav_header 函数
            num_samples = len(pcm_data) // 2
            audio_bytes = make_wav_header(num_samples, self.SAMPLE_RATE) + pcm_data

            logger.info(f"合成成功 ({len(audio_bytes):,} bytes, {len(response_text)} chars)")
            if response_text:
                logger.debug(f"文本回复: {response_text[:100]}...")

            return audio_bytes

        except Exception as e:
            logger.error(f"Qwen Omni TTS 调用失败: {e}")
            return None

    def is_available(self) -> bool:
        """检查引擎是否可用"""
        return self.api_key is not None

    def get_supported_voices(self) -> list:
        """获取支持的音色列表"""
        return self.SUPPORTED_VOICES.copy()

    def get_info(self) -> Dict[str, Any]:
        """获取引擎信息"""
        info = super().get_info()
        info["model"] = self.model
        info["default_voice"] = self.default_voice
        info["sample_rate"] = self.SAMPLE_RATE
        return info
