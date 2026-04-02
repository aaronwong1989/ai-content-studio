# 测试套件

## 目录结构

```
tests/
├── conftest.py                     # 全局 fixtures 和配置
├── test_entities/                  # 实体层测试
│   ├── test_audio_segment.py      # AudioSegment 实体
│   ├── test_engine_result.py       # EngineResult 实体
│   ├── test_enums.py               # 枚举类型
│   ├── test_tts_request.py         # TTSRequest 实体
│   └── test_voice_config.py        # VoiceConfig 实体
├── test_use_cases/                 # 用例层测试
│   └── test_tts_use_cases.py       # TTS 合成用例
├── test_adapters/                  # 适配器层测试
│   └── test_base_tts_engine.py    # TTS 引擎基类
└── test_infrastructure/           # 基础设施层测试
    └── test_container.py           # 依赖注入容器
```

## 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定层
pytest tests/test_entities/ -v
pytest tests/test_use_cases/ -v

# 运行特定文件
pytest tests/test_entities/test_audio_segment.py -v

# 显示覆盖率
pytest tests/ --cov=src --cov-report=term-missing

# 只运行快速测试（跳过 integration）
pytest tests/ -m "not integration"
```

## 测试标记

- `@pytest.mark.unit` - 单元测试（快速，无外部依赖）
- `@pytest.mark.integration` - 集成测试（可能需要外部服务）

## 添加新测试

1. 在对应层的 `test_*.py` 文件中添加测试类
2. 使用 `conftest.py` 中的 fixtures
3. 遵循命名规范：`Test<ClassName>::test_<method>_<scenario>`

```python
class TestMyClass:
    def test_method_success(self, temp_output_dir):
        """测试成功场景"""
        ...

    def test_method_failure(self):
        """测试失败场景"""
        with pytest.raises(ValueError):
            ...
```
