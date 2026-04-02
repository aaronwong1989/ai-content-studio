"""
用例层测试 - SynthesizeSpeechUseCase
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from src.entities import TTSRequest, EngineResult, VoiceConfig, EmotionType
from src.use_cases import SynthesizeSpeechUseCase


class TestSynthesizeSpeechUseCase:
    """SynthesizeSpeechUseCase 测试"""

    def test_execute_success(self, mock_minimax_engine, temp_output_dir):
        """测试执行成功"""
        output_file = temp_output_dir / "output.mp3"

        use_case = SynthesizeSpeechUseCase(engine=mock_minimax_engine)
        result = use_case.execute(
            text="测试文本",
            output_file=output_file,
            voice_id="male-qn-qingse",
        )

        assert result.success
        mock_minimax_engine.synthesize.assert_called_once()

        # 验证调用参数
        call_args = mock_minimax_engine.synthesize.call_args
        request = call_args[0][0]  # 第一个位置参数
        assert isinstance(request, TTSRequest)
        assert request.text == "测试文本"
        assert request.voice_id == "male-qn-qingse"

    def test_execute_with_custom_params(self, mock_minimax_engine, temp_output_dir):
        """测试带自定义参数执行"""
        output_file = temp_output_dir / "output.mp3"

        use_case = SynthesizeSpeechUseCase(engine=mock_minimax_engine)
        result = use_case.execute(
            text="自定义参数测试",
            output_file=output_file,
            voice_id="female-shaonv",
            speed=1.5,
            volume=0.8,
            pitch=2,
            emotion="happy",
            language="zh_cn",
            audio_format="wav",
        )

        assert result.success

        call_args = mock_minimax_engine.synthesize.call_args
        request = call_args[0][0]
        assert request.voice_config.speed == 1.5
        assert request.voice_config.volume == 0.8
        assert request.voice_config.pitch == 2
        assert request.voice_config.emotion == EmotionType.HAPPY

    def test_execute_failure(self, mock_minimax_engine, temp_output_dir):
        """测试执行失败"""
        # 配置 mock 返回失败结果
        output_file = temp_output_dir / "output.mp3"
        mock_minimax_engine.synthesize.return_value = EngineResult.failure(
            error_message="API 错误",
            engine_name="minimax",
        )

        use_case = SynthesizeSpeechUseCase(engine=mock_minimax_engine)
        result = use_case.execute(
            text="测试文本",
            output_file=output_file,
        )

        assert not result.success
        assert result.error_message == "API 错误"

    def test_execute_creates_voice_config(self, mock_minimax_engine, temp_output_dir):
        """测试执行时创建 VoiceConfig"""
        output_file = temp_output_dir / "output.mp3"

        use_case = SynthesizeSpeechUseCase(engine=mock_minimax_engine)
        use_case.execute(
            text="测试",
            output_file=output_file,
            voice_id="test-voice",
            speed=1.2,
            emotion="sad",
        )

        call_args = mock_minimax_engine.synthesize.call_args
        request = call_args[0][0]
        assert isinstance(request.voice_config, VoiceConfig)
        assert request.voice_config.voice_id == "test-voice"
        assert request.voice_config.emotion == EmotionType.SAD


class TestBatchSynthesizeUseCase:
    """BatchSynthesizeUseCase 测试"""

    def test_batch_synthesize_success(
        self, mock_minimax_engine, mock_audio_processor, temp_output_dir
    ):
        """测试批量合成成功"""
        from src.entities import AudioSegment

        output_file = temp_output_dir / "output.mp3"
        segments = [
            AudioSegment(text="第一段", voice_id="voice1"),
            AudioSegment(text="第二段", voice_id="voice2"),
        ]

        # 配置 mock
        mock_minimax_engine.synthesize.side_effect = [
            EngineResult.success(temp_output_dir / "temp1.mp3", duration=2.0),
            EngineResult.success(temp_output_dir / "temp2.mp3", duration=3.0),
        ]
        mock_audio_processor.merge_audio_files.return_value = EngineResult.success(
            output_file, duration=5.0
        )

        use_case = SynthesizeSpeechUseCase.__new__(SynthesizeSpeechUseCase)
        use_case.engine = mock_minimax_engine
        use_case.audio_processor = mock_audio_processor

        # 手动实现测试逻辑（避免重复导入 BatchSynthesizeUseCase）
        from src.use_cases.tts_use_cases import BatchSynthesizeUseCase

        use_case = BatchSynthesizeUseCase(
            engine=mock_minimax_engine,
            audio_processor=mock_audio_processor,
        )

        result = use_case.execute(
            segments=segments,
            output_file=output_file,
            merge=True,
        )

        assert result.success
        assert mock_minimax_engine.synthesize.call_count == 2
        mock_audio_processor.merge_audio_files.assert_called_once()

    def test_batch_synthesize_empty_segments_fails(
        self, mock_minimax_engine, mock_audio_processor, temp_output_dir
    ):
        """测试空片段列表失败"""
        output_file = temp_output_dir / "output.mp3"

        from src.use_cases.tts_use_cases import BatchSynthesizeUseCase

        use_case = BatchSynthesizeUseCase(
            engine=mock_minimax_engine,
            audio_processor=mock_audio_processor,
        )

        result = use_case.execute(
            segments=[],  # 空列表
            output_file=output_file,
        )

        assert not result.success
        assert "音频片段列表不能为空" in result.error_message
