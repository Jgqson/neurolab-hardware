# SMCV100B + SGT100A 自动化测试项目

该项目用于快速搭建两类射频测试流程：

1. **接收灵敏度（Sensitivity）测试**
2. **邻道干扰（Adjacent Channel Interference, ACI）测试**

> 目标：提供一个可扩展、可配置、可追溯（CSV 输出）的自动化测试基础框架。

## 1. 功能特性

- 使用 `pyvisa` 通过 SCPI 控制仪器。
- 支持对 Rohde & Schwarz **SMCV100B**（主信号源）发送电平与频点配置。
- 支持对 **SGT100A**（干扰源）发送干扰电平与频偏配置。
- 所有测试参数通过 YAML 文件配置。
- 输出 CSV 结果，便于导入 Excel/数据分析工具。
- 支持 `--dry-run`，便于在无仪器环境先验证流程。

## 2. 项目结构

```text
rf_test_automation/
├─ configs/
│  └─ example_test_plan.yaml
├─ results/
├─ src/
│  └─ rf_test_automation/
│     ├─ __init__.py
│     ├─ cli.py
│     ├─ config.py
│     ├─ instruments.py
│     └─ procedures.py
├─ pyproject.toml
└─ README.md
```

## 3. 环境准备

```bash
cd rf_test_automation
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 4. 配置文件

参考 `configs/example_test_plan.yaml`，核心分为四块：

- `visa`
  - SMCV100B 与 SGT100A 的 VISA 地址。
- `common`
  - 测试通用参数（频点、调制、衰减、步进间隔等）。
- `sensitivity`
  - 灵敏度测试起始电平/最小电平/BER 门限。
- `aci`
  - 邻道偏移列表、干扰电平扫描区间。

> 如果你的 DUT BER 读取需要串口/TCP/专有 API，可在 `procedures.py` 的 `ber_reader` 回调中接入。

## 5. 运行示例

```bash
# 干跑模式（不连接真实仪器）
rf-test --config configs/example_test_plan.yaml --dry-run

# 真实执行
rf-test --config configs/example_test_plan.yaml
```

## 6. 扩展建议

- 增加频点循环（多 channel sweep）。
- 增加测试前自检（*IDN?*、输出保护状态、告警状态）。
- 增加 DUT 自动控制接口（发包、收包、读取 PER/BER）。
- 结果同时写入 SQLite 或 InfluxDB。
