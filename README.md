# eda-open-designs

43 个独立构建的 RTL 设计，供逻辑综合、优化和验证实验使用。每个设计保留 RTL、`seed.json`、已有测试、约束及来源声明。

首批收录全部 8 个 PicoRV32 顶层，以及当前标准设计中 Nangate45 映射单元数严格大于 2000 的设计。40 个设计满足门数阈值，其中 5 个属于 PicoRV32，去重后共 43 个。

| 来源 | 设计数 | 来源记录 |
| --- | ---: | --- |
| CircuitNet3 | 17 | 每个设计的 `provenance.json` |
| OpenABC-D | 18 | 每个设计的 `seed.json` 中的 `source` |
| PicoRV32 | 8 | 每个设计的 `seed.json` 中的 `source` |

完整名单及单元数见 [catalog.csv](catalog.csv)，筛选条件、库标识和统计版本见 [selection.json](selection.json)。单元数来自 Nangate45 技术映射后的 `baseline.cell_count`，包含组合和时序单元。旧统计中的 `circuitnet3_0123_picorv32__picorv32` 已移出当前标准设计目录，本批依据现存目录导出。

```text
seeds/
  designs/<id>/
    seed.json
    rtl/
    tests/
    constraints/
    provenance.json
  templates/
  libs/
    nangate45/
    sky130/
scripts/
  run_seed_simulation.py
  run_circuitnet3_testbench.py
```

可选文件按实际资产保留。字段含义见 [Seed 配置说明](seeds/README.md)，第三方来源和许可证记录见 [NOTICE.md](NOTICE.md)。

## 共享 Liberty 库

`seeds/libs/` 收录 Nangate45 典型角和 SKY130 HD 的 16 个工艺角，共 17 份 Liberty，原始文件总大小约 202.5 MiB。库路径、运行条件、SHA-256 和 Yosys 读取结果见 [库清单](seeds/libs/manifest.json)。

门数筛选使用的库为 `seeds/libs/nangate45/nangate45.lib`，其摘要与 `selection.json` 一致。库的标识沿用相对于 `seeds/libs/` 去掉 `.lib` 后的路径，例如 `nangate45/nangate45`。许可证副本随各库保存。

## 运行已有测试

PicoRV32 使用 Python 3.12+、cocotb 和 Icarus Verilog。先准备 `iverilog`、`vvp`，再安装 Python 依赖。

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
./seeds/designs/picorv32/tests/simulation.sh
```

将 `picorv32` 换为 `catalog.csv` 中其他 PicoRV32 ID，可运行对应测试。脚本从自身位置查找仓库，支持从其他工作目录调用。

CircuitNet3 保留原始 Verilog testbench，通过独立的 Icarus 入口运行。

```bash
./seeds/designs/circuitnet3_0308_multi_32bit/tests/simulation.sh
```

这个入口报告编译和仿真进程的执行结果。各 testbench 原有的检查逻辑和结束条件决定其功能验证范围。

有 `tests/lint.sh` 的设计可以直接用 Verilator 检查。例如运行 `./seeds/designs/picorv32/tests/lint.sh`。`tests/synth.ys` 和 `tests/aig.ys` 保留运行时占位符，使用前按 [配置说明](seeds/README.md) 提供目标库、功能模型和输出路径。

## 验证记录

导出时逐字节核对 470 份设计资产，并检查 RTL、测试和约束的文件引用。43 个设计按各自配置的语言标准通过 Icarus Verilog 编译。PicoRV32 的 8 个顶层在 Python 3.12、cocotb 2.0.1、Icarus Verilog 13.0 下重新运行已有 cocotb 测试，全部通过。验证摘要见 [validation.json](validation.json)。

门数筛选使用已有综合结果，并核对其输入摘要、当前 RTL 和对应的映射统计。`seed.json` 中保留原有补全状态及历史结果，各项结论的适用范围由实际运行记录决定。功能仿真覆盖已执行用例，形式等价与时序结果需按各自流程验证。
