"""
实体层测试 - Enums
"""
import pytest

from src.entities import (
    EmotionType,
    AudioFormat,
    LanguageCode,
    TTSEngineType,
    MiniMaxVoiceID,
    QwenVoiceID,
)


class TestEmotionType:
    """EmotionType 枚举测试"""

    def test_all_emotions_exist(self):
        """测试所有情感类型都存在"""
        expected = [
            "neutral",
            "happy",
            "sad",
            "angry",
            "calm",
            "surprised",
            "fearful",
            "disgusted",
            "fluent",
        ]

        for emotion in expected:
            assert hasattr(EmotionType, emotion.upper())
            assert EmotionType[emotion.upper()].value == emotion

    def test_enum_values(self):
        """测试枚举值"""
        assert EmotionType.NEUTRAL.value == "neutral"
        assert EmotionType.HAPPY.value == "happy"
        assert EmotionType.SAD.value == "sad"

    def test_enum_from_string(self):
        """测试从字符串创建枚举"""
        assert EmotionType("happy") == EmotionType.HAPPY


class TestAudioFormat:
    """AudioFormat 枚举测试"""

    def test_all_formats_exist(self):
        """测试所有格式都存在"""
        expected = ["mp3", "wav", "pcm"]

        for fmt in expected:
            assert hasattr(AudioFormat, fmt.upper())
            assert AudioFormat[fmt.upper()].value == fmt

    def test_enum_from_string(self):
        """测试从字符串创建枚举"""
        assert AudioFormat("wav") == AudioFormat.WAV


class TestLanguageCode:
    """LanguageCode 枚举测试"""

    def test_auto_exists(self):
        """测试自动检测存在"""
        assert LanguageCode.AUTO.value == "Auto"

    def test_zh_exists(self):
        """测试中文存在"""
        assert LanguageCode.ZH.value == "zh"

    def test_enum_from_string(self):
        """测试从字符串创建枚举"""
        assert LanguageCode("Auto") == LanguageCode.AUTO

    def test_all_languages(self):
        """测试所有语言"""
        expected_languages = ["Auto", "zh", "en", "yue", "sh", "sichuan", "tianjin", "wu"]
        for lang in expected_languages:
            assert LanguageCode(lang)  # 能从字符串创建


class TestTTSEngineType:
    """TTSEngineType 枚举测试"""

    def test_all_engines_exist(self):
        """测试所有引擎类型都存在"""
        expected = ["minimax", "qwen", "qwen_tts", "qwen_omni"]

        for engine in expected:
            assert hasattr(TTSEngineType, engine.upper())
            assert TTSEngineType[engine.upper()].value == engine

    def test_enum_from_string(self):
        """测试从字符串创建枚举"""
        assert TTSEngineType("minimax") == TTSEngineType.MINIMAX


class TestMiniMaxVoiceID:
    """MiniMaxVoiceID 枚举测试"""

    def test_male_voice_exists(self):
        """测试男声存在"""
        assert hasattr(MiniMaxVoiceID, "MALE_QN_QINGSE")
        assert MiniMaxVoiceID.MALE_QN_QINGSE.value == "male-qn-qingse"

    def test_female_voice_exists(self):
        """测试女声存在"""
        assert hasattr(MiniMaxVoiceID, "FEMALE_SHAONV")
        assert MiniMaxVoiceID.FEMALE_SHAONV.value == "female-shaonv"

    def test_enum_from_string(self):
        """测试从字符串创建枚举"""
        assert MiniMaxVoiceID("male-qn-qingse") == MiniMaxVoiceID.MALE_QN_QINGSE


class TestQwenVoiceID:
    """QwenVoiceID 枚举测试"""

    def test_aurora_voice_exists(self):
        """测试 aurora 音色存在"""
        assert hasattr(QwenVoiceID, "AURORA")
        assert QwenVoiceID.AURORA.value == "aurora"

    def test_nannvann_voice_exists(self):
        """测试 nannvann 音色存在"""
        assert hasattr(QwenVoiceID, "NANNVANN")
        assert QwenVoiceID.NANNVANN.value == "nannuann"  # 枚举名有 v 但值是 nannuann

    def test_enum_from_string(self):
        """测试从字符串创建枚举"""
        assert QwenVoiceID("aurora") == QwenVoiceID.AURORA

    def test_has_multiple_voices(self):
        """测试有多个音色"""
        voices = list(QwenVoiceID)
        assert len(voices) > 10  # 至少有 10+ 个音色
