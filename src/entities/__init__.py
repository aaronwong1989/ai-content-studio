"""
实体层（Entities）- 核心业务对象

整洁架构最内层，定义核心业务实体和规则。

特点：
- 纯 Python 对象（dataclass）
- 无外部依赖
- 包含业务验证逻辑
- 不可变（frozen=True）
"""

from .audio_segment import AudioSegment
from .tts_request import TTSRequest
from .engine_result import EngineResult
from .voice_config import VoiceConfig
from .enums import (
    LanguageCode,
    EmotionType,
    AudioFormat,
    TTSEngineType,
    MiniMaxVoiceID,
    QwenVoiceID,
)

__all__ = [
    "AudioSegment",
    "TTSRequest",
    "EngineResult",
    "VoiceConfig",
    "LanguageCode",
    "EmotionType",
    "AudioFormat",
    "TTSEngineType",
    "MiniMaxVoiceID",
    "QwenVoiceID",
]
