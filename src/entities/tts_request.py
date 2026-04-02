"""
TTS 请求实体
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union

from .voice_config import VoiceConfig
from .enums import LanguageCode, EmotionType, AudioFormat


@dataclass(frozen=True)
class TTSRequest:
    """
    TTS 请求实体

    表示一个完整的 TTS 合成请求

    Attributes:
        text: 待合成文本
        output_file: 输出文件路径
        voice_config: 音色配置
        language: 语言类型
        format: 输出格式

    Example:
        >>> from .enums import EmotionType
        >>> request = TTSRequest(
        ...     text="大家好",
        ...     output_file=Path("output.mp3"),
        ...     voice_config=VoiceConfig(
        ...         voice_id="male-qn-qingse",
        ...         emotion=EmotionType.NEUTRAL
        ...     )
        ... )
    """

    text: str
    output_file: Path
    voice_config: VoiceConfig = field(default_factory=lambda: VoiceConfig())
    language: Union[str, LanguageCode] = LanguageCode.AUTO
    format: Union[str, AudioFormat] = AudioFormat.MP3

    def __post_init__(self):
        """验证逻辑"""
        # 转换路径
        if not isinstance(self.output_file, Path):
            object.__setattr__(self, 'output_file', Path(self.output_file))

        # 验证文本
        if not self.text or not self.text.strip():
            raise ValueError("文本内容不能为空")

        # 标准化枚举参数（支持字符串输入）
        if isinstance(self.language, str):
            try:
                object.__setattr__(self, 'language', LanguageCode(self.language))
            except ValueError:
                pass  # 保持字符串

        if isinstance(self.format, str):
            try:
                object.__setattr__(self, 'format', AudioFormat(self.format))
            except ValueError:
                pass  # 保持字符串

    @property
    def voice_id(self) -> str:
        """快捷访问音色 ID"""
        return self.voice_config.voice_id

    @property
    def speed(self) -> float:
        """快捷访问语速"""
        return self.voice_config.speed

    @property
    def emotion(self) -> Union[str, EmotionType]:
        """快捷访问情感"""
        return self.voice_config.emotion
