"""
实体层测试 - TTSRequest
"""
import pytest
from pathlib import Path

from src.entities import TTSRequest, VoiceConfig, LanguageCode, AudioFormat, EmotionType


class TestTTSRequest:
    """TTSRequest 实体测试"""

    def test_create_tts_request_minimal(self, temp_output_dir):
        """测试创建最小 TTS 请求"""
        output_file = temp_output_dir / "output.mp3"

        request = TTSRequest(
            text="测试文本",
            output_file=output_file,
        )

        assert request.text == "测试文本"
        assert request.output_file == output_file
        assert request.voice_config == VoiceConfig()
        assert request.language == LanguageCode.AUTO
        assert request.format == AudioFormat.MP3

    def test_create_tts_request_full(self, temp_output_dir):
        """测试创建完整 TTS 请求"""
        output_file = temp_output_dir / "output.mp3"
        voice_config = VoiceConfig(
            voice_id="female-shaonv",
            speed=1.2,
            emotion=EmotionType.HAPPY,
        )

        request = TTSRequest(
            text="欢迎收听",
            output_file=output_file,
            voice_config=voice_config,
            language=LanguageCode.ZH,  # 使用 ZH 而不是 ZH_CN
            format=AudioFormat.WAV,
        )

        assert request.text == "欢迎收听"
        assert request.voice_config.voice_id == "female-shaonv"
        assert request.voice_config.speed == 1.2
        assert request.language == LanguageCode.ZH
        assert request.format == AudioFormat.WAV

    def test_empty_text_fails(self, temp_output_dir):
        """测试空文本失败"""
        output_file = temp_output_dir / "output.mp3"

        with pytest.raises(ValueError, match="文本内容不能为空"):
            TTSRequest(text="", output_file=output_file)

    def test_whitespace_text_fails(self, temp_output_dir):
        """测试纯空白文本失败"""
        output_file = temp_output_dir / "output.mp3"

        with pytest.raises(ValueError, match="文本内容不能为空"):
            TTSRequest(text="   \n\t", output_file=output_file)

    def test_string_language_conversion(self, temp_output_dir):
        """测试语言字符串自动转换"""
        output_file = temp_output_dir / "output.mp3"

        request = TTSRequest(
            text="文本",
            output_file=output_file,
            language="zh",  # 字符串
        )

        assert request.language == LanguageCode.ZH

    def test_string_format_conversion(self, temp_output_dir):
        """测试格式字符串自动转换"""
        output_file = temp_output_dir / "output.mp3"

        request = TTSRequest(
            text="文本",
            output_file=output_file,
            format="wav",  # 字符串
        )

        assert request.format == AudioFormat.WAV

    def test_voice_id_shortcut_property(self, temp_output_dir):
        """测试 voice_id 快捷属性"""
        output_file = temp_output_dir / "output.mp3"
        voice_config = VoiceConfig(voice_id="male-qn-qingse")

        request = TTSRequest(
            text="文本",
            output_file=output_file,
            voice_config=voice_config,
        )

        assert request.voice_id == "male-qn-qingse"

    def test_speed_shortcut_property(self, temp_output_dir):
        """测试 speed 快捷属性"""
        output_file = temp_output_dir / "output.mp3"
        voice_config = VoiceConfig(speed=1.5)

        request = TTSRequest(
            text="文本",
            output_file=output_file,
            voice_config=voice_config,
        )

        assert request.speed == 1.5

    def test_emotion_shortcut_property(self, temp_output_dir):
        """测试 emotion 快捷属性"""
        output_file = temp_output_dir / "output.mp3"
        voice_config = VoiceConfig(emotion=EmotionType.SAD)

        request = TTSRequest(
            text="文本",
            output_file=output_file,
            voice_config=voice_config,
        )

        assert request.emotion == EmotionType.SAD

    def test_path_string_conversion(self, temp_output_dir):
        """测试路径字符串自动转换"""
        output_file = temp_output_dir / "output.mp3"

        request = TTSRequest(
            text="文本",
            output_file=str(output_file),
        )

        assert isinstance(request.output_file, Path)
        assert request.output_file == output_file

    def test_immutability(self, temp_output_dir):
        """测试不可变性"""
        output_file = temp_output_dir / "output.mp3"

        request = TTSRequest(
            text="文本",
            output_file=output_file,
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            request.text = "新文本"

        with pytest.raises(Exception):  # FrozenInstanceError
            request.format = AudioFormat.WAV
