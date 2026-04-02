"""
TTS 引擎抽象基类
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Dict, Any
import requests
import logging

from ..entities import (
    TTSRequest,
    EngineResult,
    EmotionType,
    AudioFormat,
)


logger = logging.getLogger(__name__)


class BaseTTSEngine(ABC):
    """
    TTS 引擎抽象基类

    提供公共方法，减少代码重复。
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
    ):
        """
        初始化基类

        Args:
            api_key: API 密钥
            base_url: API 基础 URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')  # 移除末尾斜杠
        self._session: requests.Session = None

    @property
    def session(self) -> requests.Session:
        """延迟初始化 HTTP Session"""
        if self._session is None:
            self._session = requests.Session()
        return self._session

    @abstractmethod
    def synthesize(self, request: TTSRequest) -> EngineResult:
        """
        合成语音（子类实现）

        Args:
            request: TTS 请求

        Returns:
            EngineResult: 合成结果
        """
        pass

    @abstractmethod
    def _build_payload(self, request: TTSRequest) -> dict:
        """
        构建 API 请求参数（子类实现）

        Args:
            request: TTS 请求

        Returns:
            dict: API 请求参数
        """
        pass

    @abstractmethod
    def get_engine_name(self) -> str:
        """
        获取引擎名称（子类实现）

        Returns:
            str: 引擎名称
        """
        pass

    @abstractmethod
    def _estimate_duration(self, audio_data: bytes) -> float:
        """
        估算音频时长（子类实现，因为不同格式算法不同）

        Args:
            audio_data: 音频数据

        Returns:
            float: 时长（秒）
        """
        pass

    def _call_api(
        self,
        endpoint: str,
        payload: dict,
        headers: dict = None,
        method: str = "POST",
    ) -> bytes:
        """
        调用 API（通用实现）

        Args:
            endpoint: API 端点（如 /v1/text_to_speech）
            payload: 请求参数
            headers: 请求头（可选）
            method: HTTP 方法（默认 POST）

        Returns:
            bytes: 音频数据

        Raises:
            requests.RequestException: API 调用失败
        """
        url = f"{self.base_url}{endpoint}"

        if headers is None:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

        try:
            if method.upper() == "POST":
                response = self.session.post(url, json=payload, headers=headers)
            elif method.upper() == "GET":
                response = self.session.get(url, params=payload, headers=headers)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            response.raise_for_status()
            return response.content

        except requests.RequestException as e:
            logger.error(f"API 调用失败: {url}, 错误: {str(e)}")
            raise

    def _normalize_enum_value(self, value: Union[str, object]) -> str:
        """
        标准化枚举值（通用方法）

        Args:
            value: 枚举值或字符串

        Returns:
            str: 标准化后的值
        """
        if hasattr(value, "value"):
            return value.value
        return str(value)

    def _save_audio_file(
        self,
        audio_data: bytes,
        output_file: Path,
    ) -> None:
        """
        保存音频文件（通用方法）

        Args:
            audio_data: 音频数据
            output_file: 输出文件路径
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_bytes(audio_data)
        logger.info(f"音频文件已保存: {output_file}")

    def cleanup(self):
        """清理资源"""
        if self._session is not None:
            self._session.close()
            self._session = None
            logger.debug(f"{self.get_engine_name()} 引擎资源已清理")
