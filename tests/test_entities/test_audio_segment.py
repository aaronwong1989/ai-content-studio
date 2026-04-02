"""
实体层测试 - AudioSegment
"""
import pytest
from pathlib import Path

from src.entities import AudioSegment


class TestAudioSegment:
    """AudioSegment 实体测试"""

    def test_create_audio_segment_success(self):
        """测试成功创建音频片段"""
        segment = AudioSegment(
            text="大家好，欢迎收听本期节目",
            voice_id="male-qn-qingse",
        )

        assert segment.text == "大家好，欢迎收听本期节目"
        assert segment.voice_id == "male-qn-qingse"
        assert segment.duration == 0.0
        assert segment.file_path is None

    def test_create_audio_segment_with_file(self, temp_output_dir):
        """测试创建带文件的音频片段"""
        audio_file = temp_output_dir / "test.mp3"
        audio_file.write_bytes(b"fake audio data")

        segment = AudioSegment(
            text="测试文本",
            voice_id="female-shaonv",
            duration=5.5,
            file_path=audio_file,
        )

        assert segment.text == "测试文本"
        assert segment.voice_id == "female-shaonv"
        assert segment.duration == 5.5
        assert segment.file_path == audio_file
        assert segment.is_synthesized

    def test_audio_segment_empty_text_fails(self):
        """测试空文本创建失败"""
        with pytest.raises(ValueError, match="文本内容不能为空"):
            AudioSegment(text="", voice_id="male-qn-qingse")

    def test_audio_segment_whitespace_text_fails(self):
        """测试纯空白文本创建失败"""
        with pytest.raises(ValueError, match="文本内容不能为空"):
            AudioSegment(text="   \n\t  ", voice_id="male-qn-qingse")

    def test_audio_segment_empty_voice_id_fails(self):
        """测试空音色 ID 创建失败"""
        with pytest.raises(ValueError, match="音色 ID 不能为空"):
            AudioSegment(text="测试文本", voice_id="")

    def test_audio_segment_negative_duration_fails(self):
        """测试负数时长创建失败"""
        with pytest.raises(ValueError, match="时长不能为负数"):
            AudioSegment(
                text="测试文本",
                voice_id="male-qn-qingse",
                duration=-1.0,
            )

    def test_with_file_method(self, temp_output_dir):
        """测试 with_file 方法创建新实例"""
        segment = AudioSegment(
            text="原始文本",
            voice_id="male-qn-qingse",
        )

        audio_file = temp_output_dir / "new.mp3"
        new_segment = segment.with_file(audio_file, duration=3.5)

        # 原实例不变
        assert segment.file_path is None
        assert segment.duration == 0.0

        # 新实例更新
        assert new_segment.file_path == audio_file
        assert new_segment.duration == 3.5
        assert new_segment.text == segment.text
        assert new_segment.voice_id == segment.voice_id

    def test_is_synthesized_property(self, temp_output_dir):
        """测试 is_synthesized 属性"""
        # 未合成
        segment1 = AudioSegment(text="文本", voice_id="voice")
        assert not segment1.is_synthesized

        # 有文件但时长为 0
        audio_file = temp_output_dir / "test.mp3"
        audio_file.write_bytes(b"data")
        segment2 = AudioSegment(
            text="文本",
            voice_id="voice",
            file_path=audio_file,
            duration=0.0,
        )
        assert not segment2.is_synthesized

        # 完整合成
        segment3 = AudioSegment(
            text="文本",
            voice_id="voice",
            file_path=audio_file,
            duration=5.0,
        )
        assert segment3.is_synthesized

    def test_char_count_property(self):
        """测试 char_count 属性"""
        text = "大家好，欢迎收听"
        segment = AudioSegment(text=text, voice_id="voice")

        assert segment.char_count == len(text)
        assert segment.char_count == 8  # 8 个中文字符

    def test_path_conversion(self, temp_output_dir):
        """测试路径自动转换"""
        # 字符串路径
        audio_file = temp_output_dir / "test.mp3"
        audio_file.write_bytes(b"data")

        segment = AudioSegment(
            text="文本",
            voice_id="voice",
            file_path=str(audio_file),
            duration=3.0,
        )

        assert isinstance(segment.file_path, Path)
        assert segment.file_path == audio_file

    def test_immutability(self):
        """测试不可变性（frozen=True）"""
        segment = AudioSegment(text="文本", voice_id="voice")

        with pytest.raises(Exception):  # FrozenInstanceError
            segment.text = "新文本"

        with pytest.raises(Exception):  # FrozenInstanceError
            segment.duration = 5.0
