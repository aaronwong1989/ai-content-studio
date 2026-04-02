"""
实体层测试 - VoiceConfig
"""
import pytest

from src.entities import VoiceConfig, EmotionType


class TestVoiceConfig:
    """VoiceConfig 实体测试"""

    def test_create_voice_config_default(self):
        """测试创建默认音色配置"""
        config = VoiceConfig(voice_id="male-qn-qingse")

        assert config.voice_id == "male-qn-qingse"
        assert config.speed == 1.0
        assert config.volume == 1.0
        assert config.pitch == 0
        assert config.emotion == EmotionType.NEUTRAL

    def test_create_voice_config_custom(self):
        """测试创建自定义音色配置"""
        config = VoiceConfig(
            voice_id="female-shaonv",
            speed=1.2,
            volume=0.8,
            pitch=2,
            emotion=EmotionType.HAPPY,
        )

        assert config.voice_id == "female-shaonv"
        assert config.speed == 1.2
        assert config.volume == 0.8
        assert config.pitch == 2
        assert config.emotion == EmotionType.HAPPY

    def test_emotion_string_conversion(self):
        """测试情感字符串自动转换"""
        config = VoiceConfig(
            voice_id="voice",
            emotion="happy",  # 字符串
        )

        # 应该转换为枚举
        assert config.emotion == EmotionType.HAPPY

    def test_invalid_speed(self):
        """测试无效语速"""
        with pytest.raises(ValueError, match="语速必须在 0.5-2.0 之间"):
            VoiceConfig(voice_id="voice", speed=0.3)

        with pytest.raises(ValueError, match="语速必须在 0.5-2.0 之间"):
            VoiceConfig(voice_id="voice", speed=2.5)

    def test_invalid_volume(self):
        """测试无效音量"""
        with pytest.raises(ValueError, match="音量必须在 0.1-2.0 之间"):
            VoiceConfig(voice_id="voice", volume=0.05)

        with pytest.raises(ValueError, match="音量必须在 0.1-2.0 之间"):
            VoiceConfig(voice_id="voice", volume=2.5)

    def test_invalid_pitch(self):
        """测试无效音调"""
        with pytest.raises(ValueError, match="音调必须在 -12 到 \\+12 之间"):
            VoiceConfig(voice_id="voice", pitch=-13)

        with pytest.raises(ValueError, match="音调必须在 -12 到 \\+12 之间"):
            VoiceConfig(voice_id="voice", pitch=13)

    def test_empty_voice_id(self):
        """测试空音色 ID"""
        with pytest.raises(ValueError, match="音色 ID 不能为空"):
            VoiceConfig(voice_id="")

        with pytest.raises(ValueError, match="音色 ID 不能为空"):
            VoiceConfig(voice_id="   ")

    def test_to_dict(self):
        """测试转换为字典"""
        config = VoiceConfig(
            voice_id="male-qn-qingse",
            speed=1.2,
            volume=0.8,
            pitch=2,
            emotion=EmotionType.HAPPY,
        )

        data = config.to_dict()

        assert data["voice"] == "male-qn-qingse"
        assert data["speed"] == 1.2
        assert data["volume"] == 0.8
        assert data["pitch"] == 2
        assert data["emotion"] == "happy"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "voice": "female-shaonv",
            "speed": 1.5,
            "volume": 1.2,
            "pitch": -3,
            "emotion": "sad",
        }

        config = VoiceConfig.from_dict(data)

        assert config.voice_id == "female-shaonv"
        assert config.speed == 1.5
        assert config.volume == 1.2
        assert config.pitch == -3
        assert config.emotion == "sad"

    def test_from_dict_defaults(self):
        """测试从字典创建（使用默认值）"""
        data = {}

        config = VoiceConfig.from_dict(data)

        assert config.voice_id == "male-qn-qingse"  # 默认值
        assert config.speed == 1.0
        assert config.volume == 1.0
        assert config.pitch == 0
        assert config.emotion == EmotionType.NEUTRAL

    def test_immutability(self):
        """测试不可变性"""
        config = VoiceConfig(voice_id="voice")

        with pytest.raises(Exception):  # FrozenInstanceError
            config.speed = 1.5

        with pytest.raises(Exception):  # FrozenInstanceError
            config.emotion = EmotionType.HAPPY
