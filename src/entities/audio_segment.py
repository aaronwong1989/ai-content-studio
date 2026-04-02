"""
音频片段实体
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class AudioSegment:
    """
    音频片段实体

    表示一个待合成或已合成的音频片段

    Attributes:
        text: 待合成的文本内容
        voice_id: 音色 ID
        duration: 音频时长（秒），合成前为 0.0
        file_path: 音频文件路径，合成前为 None

    Example:
        >>> segment = AudioSegment(
        ...     text="大家好，欢迎收听本期节目",
        ...     voice_id="male-qn-qingse"
        ... )
        >>> segment.text
        '大家好，欢迎收听本期节目'
    """

    text: str
    voice_id: str
    duration: float = 0.0
    file_path: Optional[Path] = None

    def __post_init__(self):
        """验证逻辑"""
        # 验证文本不为空
        if not self.text or not self.text.strip():
            raise ValueError("文本内容不能为空")

        # 验证音色 ID
        if not self.voice_id or not self.voice_id.strip():
            raise ValueError("音色 ID 不能为空")

        # 验证时长非负
        if self.duration < 0:
            raise ValueError("时长不能为负数")

        # 验证文件路径（如果提供）
        if self.file_path is not None and not isinstance(self.file_path, Path):
            object.__setattr__(self, 'file_path', Path(self.file_path))

    def with_file(self, file_path: Path, duration: float) -> "AudioSegment":
        """
        创建包含文件信息的新实例

        Args:
            file_path: 音频文件路径
            duration: 音频时长

        Returns:
            新的 AudioSegment 实例
        """
        return AudioSegment(
            text=self.text,
            voice_id=self.voice_id,
            duration=duration,
            file_path=Path(file_path)
        )

    @property
    def is_synthesized(self) -> bool:
        """是否已合成"""
        return self.file_path is not None and self.duration > 0

    @property
    def char_count(self) -> int:
        """文本字符数"""
        return len(self.text)
