# Quickstart: Liuyao Najia Calculation Engine V1

**Date**: 2026-08-19 | **Feature**: specs/020-liuyao-najia-engine

## Operator Workflow

1. **显式爻录入推算**（P1 主线）：准备六爻 JSON（六爻阴阳与动爻 + 起卦时刻）→ `mingli-engine liuyao-calculate` 得装卦 JSON → `mingli-engine liuyao-report` 得 Markdown 报告。
2. **时间起卦**：仅提供公历时刻，引擎按文档化的数字换算得卦后装卦分析。
3. **数字起卦**：提供两个正整数与时刻，换算得卦后装卦分析。

## Example

`examples/liuyao-cast.explicit.json`:

```json
{
  "cast_mode": "explicit",
  "cast_datetime": "1990-01-01T08:30",
  "lines": [
    {"position": 1, "yin_yang": "yang", "moving": false},
    {"position": 2, "yin_yang": "yang", "moving": false},
    {"position": 3, "yin_yang": "yang", "moving": false},
    {"position": 4, "yin_yang": "yang", "moving": true},
    {"position": 5, "yin_yang": "yin", "moving": false},
    {"position": 6, "yin_yang": "yin", "moving": false}
  ],
  "request_id": null
}
```

```powershell
$env:PYTHONPATH='src'
uv run --frozen mingli-engine liuyao-calculate --input examples/liuyao-cast.explicit.json --pretty
uv run --frozen mingli-engine liuyao-report --input examples/liuyao-cast.explicit.json
```

Expected: chart JSON with 雷天大壮 palace assembly and a deterministic Markdown report; identical repeated invocations are byte-identical.

## Development Gates (per task)

```powershell
$env:PYTHONPATH='src'
$env:PYTHONDONTWRITEBYTECODE='1'
uv run --frozen --with pytest==8.4.1 python -m pytest tests/unit/test_liuyao_constants.py tests/unit/test_liuyao_casting.py tests/unit/test_liuyao_najia.py tests/unit/test_liuyao_analysis.py tests/unit/test_liuyao_report.py tests/integration/test_liuyao_cli.py -q -p no:cacheprovider
uv run --frozen --with mypy==1.17.1 python -m mypy src/mingli_engine/liuyao --follow-imports=skip
uv run --frozen --with ruff==0.12.11 ruff check src/mingli_engine/liuyao tests/unit/test_liuyao_constants.py tests/unit/test_liuyao_casting.py tests/unit/test_liuyao_najia.py tests/unit/test_liuyao_analysis.py tests/unit/test_liuyao_report.py tests/integration/test_liuyao_cli.py
git diff --check
```

## Boundary Reminders

- 引擎不模拟摇卦随机过程；显式录入以用户摇卦结果为信任根。
- 所有输出为传统方法的文化解读材料，含免责声明与不确定性措辞；高风险主题拒绝或降级。
- 输入与报告零持久化；不得把任何个人起卦记录写入仓库。
- 六爻知识链与八字知识链完全隔离；修改六爻内容前确认八字全套件不受影响。
