# 第三方来源与声明

本仓库汇集不同来源的 RTL 和测试资产。每个文件保留原有版权和许可证声明，复用时按相应声明处理。

| 设计前缀 | 上游 | 固定提交 | 已整理的许可证信息 |
| --- | --- | --- | --- |
| `picorv32` | [YosysHQ/picorv32](https://github.com/YosysHQ/picorv32) | `ef203c2b0a3fb793280f5114941416c425c5b461` | ISC，保留在 `rtl/design.v` 文件头 |
| `openabcd_` | [NYU-MLDA/OpenABC](https://github.com/NYU-MLDA/OpenABC) | `ecd7dde67740556eaf842ccab4dc941c348ad8f6` | `source.license` 尚未逐例确认，按各 RTL 文件内的原声明核对 |
| `circuitnet3_` | [sklp-eda-lab/iclr-circuitnet_3.0](https://github.com/sklp-eda-lab/iclr-circuitnet_3.0) | `71984703fcd203ebc84c41b5c19f056cde4be43e` | 由 `provenance.json` 追溯来源，许可证尚未逐例确认 |

CircuitNet3 部分依赖另有原文件头或来源记录，随设计保留。现有配置中的未知值保持原样，具体设计的授权范围以其上游及文件声明为依据。

## 共享单元库

`seeds/libs/nangate45/nangate45.lib` 保留原有 Nangate 版权和文件头声明。随库附上的 [LICENSE](seeds/libs/nangate45/LICENSE) 取自 [OpenROAD-flow-scripts 的 Nangate45 平台](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/master/flow/platforms/nangate45/LICENSE)。

`seeds/libs/sky130/` 收录 SKY130 高密度标准单元库的 16 个工艺角。SkyWater PDK Authors 的 Apache-2.0 许可证副本保存在 [LICENSE](seeds/libs/sky130/LICENSE)，取自 [SkyWater HD 库上游](https://github.com/google/skywater-pdk-libs-sky130_fd_sc_hd/blob/main/LICENSE)。
