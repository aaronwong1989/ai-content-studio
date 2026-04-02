"""
实体层测试 - EngineResult
"""
import pytest
from pathlib import Path

from src.entities import EngineResult


class TestEngineResult:
    """EngineResult 实体测试"""

    def test_create_success_result(self, temp_output_dir):
        """测试创建成功结果"""
        audio_file = temp_output_dir / "output.mp3"
        audio_file.write_bytes(b"fake audio")

        result = EngineResult(
            success=True,
            file_path=audio_file,
            duration=5.5,
            engine_name="minimax",
        )

        assert result.success is True
        assert result.file_path == audio_file
        assert result.duration == 5.5
        assert result.engine_name == "minimax"
        assert result.error_message is None

    def test_create_failure_result(self):
        """测试创建失败结果"""
        result = EngineResult(
            success=False,
            error_message="API 调用失败",
            engine_name="minimax",
        )

        assert result.success is False
        assert result.file_path is None
        assert result.duration == 0.0
        assert result.error_message == "API 调用失败"
        assert result.engine_name == "minimax"

    def test_success_without_file_path_fails(self):
        """测试成功结果必须包含文件路径"""
        with pytest.raises(ValueError, match="成功结果必须包含文件路径"):
            EngineResult(success=True)

    def test_failure_without_error_message_fails(self):
        """测试失败结果必须包含错误信息"""
        with pytest.raises(ValueError, match="失败结果必须包含错误信息"):
            EngineResult(success=False)

    def test_class_method_success(self, temp_output_dir):
        """测试类方法创建成功结果"""
        audio_file = temp_output_dir / "output.mp3"

        result = EngineResult.success(
            file_path=audio_file,
            duration=10.5,
            engine_name="qwen",
        )

        assert result.success
        assert result.file_path == audio_file
        assert result.duration == 10.5
        assert result.engine_name == "qwen"

    def test_class_method_failure(self):
        """测试类方法创建失败结果"""
        result = EngineResult.failure(
            error_message="网络超时",
            engine_name="minimax",
        )

        assert not result.success
        assert result.error_message == "网络超时"
        assert result.engine_name == "minimax"

    def test_bool_conversion(self, temp_output_dir):
        """测试布尔转换"""
        audio_file = temp_output_dir / "output.mp3"
        audio_file.write_bytes(b"data")

        success_result = EngineResult.success(file_path=audio_file)
        failure_result = EngineResult.failure(error_message="错误")

        assert bool(success_result) is True
        assert bool(failure_result) is False

    def test_str_representation_success(self, temp_output_dir):
        """测试成功结果的字符串表示"""
        audio_file = temp_output_dir / "output.mp3"
        audio_file.write_bytes(b"data")

        result = EngineResult.success(file_path=audio_file, duration=5.5)

        str_repr = str(result)
        assert "success=True" in str_repr
        assert "output.mp3" in str_repr
        assert "5.50" in str_repr

    def test_str_representation_failure(self):
        """测试失败结果的字符串表示"""
        result = EngineResult.failure(error_message="网络错误")

        str_repr = str(result)
        assert "success=False" in str_repr
        assert "网络错误" in str_repr

    def test_path_string_conversion(self, temp_output_dir):
        """测试路径字符串自动转换"""
        audio_file = temp_output_dir / "output.mp3"
        audio_file.write_bytes(b"data")

        # 使用字符串路径
        result = EngineResult.success(
            file_path=str(audio_file),
            duration=5.0,
        )

        assert isinstance(result.file_path, Path)
        assert result.file_path == audio_file

    def test_immutability(self, temp_output_dir):
        """测试不可变性"""
        audio_file = temp_output_dir / "output.mp3"
        audio_file.write_bytes(b"data")

        result = EngineResult.success(file_path=audio_file, duration=5.0)

        with pytest.raises(Exception):  # FrozenInstanceError
            result.success = False

        with pytest.raises(Exception):  # FrozenInstanceError
            result.duration = 10.0
