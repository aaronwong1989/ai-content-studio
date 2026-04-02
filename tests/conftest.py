"""
Pytest 配置和公共 fixtures
"""
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

# 设置测试环境变量
os.environ["MINIMAX_API_KEY"] = "test_minimax_key"
os.environ["MINIMAX_GROUP_ID"] = "test_group_id"
os.environ["QWEN_API_KEY"] = "test_qwen_key"


@pytest.fixture
def temp_output_dir(tmp_path):
    """临时输出目录"""
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def sample_text():
    """示例文本"""
    return "大家好，欢迎收听本期节目"


@pytest.fixture
def sample_audio_data():
    """示例音频数据（模拟 MP3）"""
    # 模拟 MP3 文件头（ID3）
    return b"ID3\x03\x00\x00\x00\x00\x00" + b"\x00" * 1000


@pytest.fixture
def sample_wav_data():
    """示例 WAV 音频数据"""
    # RIFF WAV 头
    return (
        b"RIFF"
        b"\x24\x00\x00\x00"  # 文件大小 - 8
        b"WAVE"
        b"fmt "
        b"\x10\x00\x00\x00"  # fmt 块大小
        b"\x01\x00"  # PCM 格式
        b"\x01\x00"  # 单声道
        b"\x22\x56\x00\x00"  # 22050 Hz
        b"\x44\xac\x00\x00"  # 字节率
        b"\x02\x00"  # 块对齐
        b"\x10\x00"  # 位深度 16
        b"data"
        b"\x00\x00\x00\x00"  # 数据大小
    )


@pytest.fixture
def mock_minimax_engine():
    """Mock MiniMax TTS 引擎"""
    engine = Mock()
    engine.synthesize = MagicMock(return_value=Mock(
        success=True,
        file_path=Path("test_output.mp3"),
        duration=5.5,
        engine_name="minimax"
    ))
    return engine


@pytest.fixture
def mock_qwen_engine():
    """Mock Qwen TTS 引擎"""
    engine = Mock()
    engine.synthesize = MagicMock(return_value=Mock(
        success=True,
        file_path=Path("test_output.wav"),
        duration=6.0,
        engine_name="qwen"
    ))
    return engine


@pytest.fixture
def mock_audio_processor():
    """Mock 音频处理器"""
    processor = Mock()
    processor.merge_audio_files = MagicMock(return_value=Mock(
        success=True,
        file_path=Path("merged_output.mp3"),
        duration=15.0,
        engine_name="ffmpeg"
    ))
    return processor
