# Seed 配置说明

每个 `designs/<id>/` 对应确定的顶层和参数配置。`seed.json` 的 `id` 与目录名一致，字段沿用 EDAForge Seed 1.1。

| 字段 | 含义 |
| --- | --- |
| `rtl.top` | 顶层模块 |
| `rtl.files` | 按构建顺序排列的 RTL 源码 |
| `rtl.language` | 语言标准与识别依据 |
| `rtl.include_dirs` | 头文件搜索目录 |
| `rtl.defines` | 预处理宏 |
| `rtl.parameters` | 顶层参数覆盖值 |
| `rtl.resources` | RTL 使用的初始化资源 |
| `source` | 上游仓库、固定提交和已记录的许可证 |
| `build_inputs` | 已整理的依赖、特殊构造、端口、时钟和复位 |
| `verification` | 已有验证入口和历史结果 |
| `completion` | 每项能力的状态、运行标识和输入摘要 |

Seed 内登记的文件路径相对于该设计目录。CircuitNet3 的上游仓库、固定提交和原 testbench 对应关系另外保存在 `provenance.json`。

## 测试资产

| 路径 | 用途 |
| --- | --- |
| `tests/lint.sh` | Verilator lint 入口 |
| `tests/synth.ys` | Yosys/ABC 技术映射脚本 |
| `tests/aig.ys` | Yosys AIG 转换脚本 |
| `tests/simulation.sh` | 对应设计的仿真入口 |
| `tests/cocotb/` | Python 自检测试 |
| `tests/verilog/` | CircuitNet3 原始 HDL testbench 及运行资源 |
| `constraints/` | 已有时序约束 |

PicoRV32 的 `verification.cocotb` 登记测试文件、模块、资源、后端和超时。`scripts/run_seed_simulation.py` 为每项测试建立临时目录，按 RTL 配置编译，并检查 xUnit 中确有测试执行且无失败、错误或跳过。

可用 `timescale: ["1ns", "1ps"]` 指定默认时间单位和精度。cocotb verifier 默认超时为 1800 秒，显式配置也须至少为 1800 秒。测试资源复制到临时目录后运行，源码目录保留为输入资产。

CircuitNet3 的 `tests/simulation.sh` 调用 `scripts/run_circuitnet3_testbench.py`。该入口保留原有行为，默认每阶段超时 60 秒，支持指定 testbench 文件和顶层。

```bash
./seeds/designs/circuitnet3_0308_multi_32bit/tests/simulation.sh tb_01.v --timeout 120
```

若有 `tests/verilog/runtime.json`，执行器按其中的 `working_directory` 准备运行目录，并复制 `runtime/` 里的资源。原 testbench 的进程正常结束记录为执行成功，需结合其自检逻辑理解功能结论。

## 综合脚本占位符

| 占位符 | 使用前填入 |
| --- | --- |
| `@LIBERTY@` | 目标 Liberty 文件 |
| `@FUNCTIONAL_MODELS@` | 库单元的可综合 Verilog 功能模型 |
| `@PRE_STAT_JSON@` | 映射前统计的输出文件 |
| `@STAT_JSON@` | 映射后统计的输出文件 |
| `@NETLIST_V@` | 门级 Verilog 网表的输出文件 |
| `@NETLIST_JSON@` | 门级 JSON 网表的输出文件 |
| `@AIG_JSON@` | AIG JSON 的输出文件 |

在设计目录运行替换后的 `.ys` 脚本。所有路径需使用适合 Yosys 脚本的引号。`@LIBERTY@` 可填写本仓库 `seeds/libs/nangate45/nangate45.lib` 或所选 SKY130 HD 库的绝对路径。`@FUNCTIONAL_MODELS@` 使用运行环境从对应库生成的功能模型。

共享库的完整名单和读取检查结果见 [libs/manifest.json](libs/manifest.json)。17 份 Liberty 均已与源文件逐字节核对，并通过 Yosys `read_liberty -lib` 读取检查。

## 历史状态

`completion` 包含 `missing`、`unverified`、`passed`、`partial`、`failed`、`inconclusive` 和 `stale`。缺失字段或 `null` 表示对应信息尚未提供。

历史 `run_id`、日志路径、摘要和指标保留在设计配置中。复核状态时需使用匹配的 RTL、工具、库和执行证据。`selection.json` 固定本批筛选所用的统计版本，`catalog.csv` 列出每个设计对应的 Nangate45 映射单元数。
