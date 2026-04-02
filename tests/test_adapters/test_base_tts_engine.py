"""
适配器层测试 - BaseTTSEngine
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from src.adapters import BaseTTSEngine
from src.entities import TTSRequest, EngineResult, VoiceConfig


class ConcreteTTSEngine(BaseTTSEngine):
    """用于测试的具体 TTS 引擎实现"""

    def synthesize(self, request: TTSRequest) -> EngineResult:
        pass

    def _build_payload(self, request: TTSRequest) -> dict:
        return {"text": request.text}

    def get_engine_name(self) -> str:
        return "test"

    def _estimate_duration(self, audio_data: bytes) -> float:
        return len(audio_data) / 1000.0


class TestBaseTTSEngine:
    """BaseTTSEngine 测试"""

    def test_init(self):
        """测试初始化"""
        engine = ConcreteTTSEngine(
            api_key="test_key",
            base_url="https://api.example.com",
        )

        assert engine.api_key == "test_key"
        assert engine.base_url == "https://api.example.com"
        assert engine._session is None  # 延迟初始化

    def test_base_url_strips_trailing_slash(self):
        """测试 base_url 末尾斜杠处理"""
        engine = ConcreteTTSEngine(
            api_key="test_key",
            base_url="https://api.example.com/",
        )

        assert engine.base_url == "https://api.example.com"

    def test_session_lazy_initialization(self):
        """测试 Session 延迟初始化"""
        import requests

        engine = ConcreteTTSEngine(
            api_key="test_key",
            base_url="https://api.example.com",
        )

        # 访问前为 None
        assert engine._session is None

        # 访问后创建 session
        session = engine.session
        assert isinstance(session, requests.Session)

        # 再次访问返回同一实例
        assert engine.session is session

    def test_normalize_enum_value_with_enum(self):
        """测试枚举值标准化（枚举对象）"""
        from src.entities import EmotionType

        engine = ConcreteTTSEngine(api_key="key", base_url="url")

        result = engine._normalize_enum_value(EmotionType.HAPPY)
        assert result == "happy"

    def test_normalize_enum_value_with_string(self):
        """测试枚举值标准化（字符串）"""
        engine = ConcreteTTSEngine(api_key="key", base_url="url")

        result = engine._normalize_enum_value("neutral")
        assert result == "neutral"

    def test_normalize_enum_value_with_custom_object(self):
        """测试枚举值标准化（自定义对象）"""

        class CustomEnum:
            value = "custom_value"

        engine = ConcreteTTSEngine(api_key="key", base_url="url")

        result = engine._normalize_enum_value(CustomEnum())
        assert result == "custom_value"

    def test_save_audio_file(self, temp_output_dir):
        """测试保存音频文件"""
        audio_data = b"fake audio data"
        output_file = temp_output_dir / "test.mp3"

        engine = ConcreteTTSEngine(api_key="key", base_url="url")
        engine._save_audio_file(audio_data, output_file)

        assert output_file.exists()
        assert output_file.read_bytes() == audio_data

    def test_save_audio_file_creates_parent_dirs(self, temp_output_dir):
        """测试保存音频文件时自动创建父目录"""
        audio_data = b"fake audio data"
        output_file = temp_output_dir / "subdir" / "test.mp3"

        assert not output_file.parent.exists()

        engine = ConcreteTTSEngine(api_key="key", base_url="url")
        engine._save_audio_file(audio_data, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_call_api_success(self, temp_output_dir):
        """测试 API 调用成功"""
        expected_data = b"audio data"

        with patch("requests.Session") as MockSession:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.content = expected_data
            mock_response.raise_for_status = MagicMock()
            mock_session.post.return_value = mock_response
            MockSession.return_value = mock_session

            engine = ConcreteTTSEngine(api_key="key", base_url="https://api.example.com")
            result = engine._call_api("/test", {"param": "value"})

            assert result == expected_data
            mock_session.post.assert_called_once()

    def test_cleanup(self):
        """测试清理资源"""
        engine = ConcreteTTSEngine(api_key="key", base_url="url")

        # 先创建 session
        _ = engine.session
        assert engine._session is not None

        # 清理
        engine.cleanup()
        assert engine._session is None

    def test_cleanup_idempotent(self):
        """测试清理幂等性（多次清理无影响）"""
        engine = ConcreteTTSEngine(api_key="key", base_url="url")

        engine.cleanup()
        engine.cleanup()  # 不应抛出异常

        assert engine._session is None
