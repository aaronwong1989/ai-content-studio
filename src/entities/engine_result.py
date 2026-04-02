"""
引擎结果实体
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class EngineResult:
    """
    TTS 引擎执行结果

    表示 TTS 合成的结果（成功或失败）

    Attributes:
        success: 是否成功
        file_path: 输出文件路径（成功时）
        duration: 音频时长（秒）
        error_message: 错误信息（失败时）
        engine_name: 引擎名称

    Example:
        >>> # 成功结果
        >>> result = EngineResult.success(
        ...     file_path=Path("output.mp3"),
        ...     duration=5.5
        ... )
        >>> result.success
        True

        >>> # 失败结果
        >>> result = EngineResult.failure("API 调用失败")
        >>> result.success
        False
    """

    success: bool
    file_path: Optional[Path] = None
    duration: float = 0.0
    error_message: Optional[str] = None
    engine_name: Optional[str] = None

    def __post_init__(self):
        """验证逻辑"""
        # 转换路径
        if self.file_path is not None and not isinstance(self.file_path, Path):
            object.__setattr__(self, 'file_path', Path(self.file_path))

        # 验证一致性
        if self.success and self.file_path is None:
            raise ValueError("成功结果必须包含文件路径")

        if not self.success and self.error_message is None:
            raise ValueError("失败结果必须包含错误信息")

    @classmethod
    def success(
        cls,
        file_path: Path,
        duration: float = 0.0,
        engine_name: Optional[str] = None
    ) -> "EngineResult":
        """
        创建成功结果

        Args:
            file_path: 输出文件路径
            duration: 音频时长
            engine_name: 引擎名称

        Returns:
            EngineResult 实例
        """
        return cls(
            success=True,
            file_path=Path(file_path),
            duration=duration,
            engine_name=engine_name
        )

    @classmethod
    def failure(
        cls,
        error_message: str,
        engine_name: Optional[str] = None
    ) -> "EngineResult":
        """
        创建失败结果

        Args:
            error_message: 错误信息
            engine_name: 引擎名称

        Returns:
            EngineResult 实例
        """
        return cls(
            success=False,
            error_message=error_message,
            engine_name=engine_name
        )

    def __bool__(self) -> bool:
        """支持 bool(result) 语法"""
        return self.success

    def __str__(self) -> str:
        """字符串表示"""
        if self.success:
            return f"EngineResult(success=True, file={self.file_path}, duration={self.duration:.2f}s)"
        else:
            return f"EngineResult(success=False, error={self.error_message})"
