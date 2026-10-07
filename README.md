# Bonsai-27B-NInfer-kvmem — 三元 Bonsai 27B 本地推理工程

> 在 **RTX 5080（16 GB / sm_120a）** 上部署 **Bonsai-2-27B 三元量化模型**：基于上游源码**自行编译整套引擎与工具链**（含修复补丁），并配套 GUI 启动器、日志工具与复现材料。
> 私有仓库：`paicat1/Bonsai-27B-NInfer-kvmem`（**非官方发布方**）。

---

## 一、上游给的 vs 本项目做的

### 上游提供
| 项 | 内容 | 来源 |
|---|---|---|
| **模型制品** | `Ternary-Bonsai-2-27B-ninfer-v3.ninfer`（9.52 GB，三元量化） | 沈三殊（shensanshu） |
| **引擎源码** | NInfer v0.11.0 + KVMem 环 | Neroued（NInfer）· 1314521gjy（KVMem 环融合） |
| **引擎成品** | `ninfer-serve-120a.exe` + 依赖 DLL | 沈三殊成品包 `infer-engine-sm120a-20261002` |

### 本项目做的 —— `engine/self-built/`
| 项 | 内容 |
|---|---|
| **自行编译的引擎 + 工具链** | `ninfer-serve`（推理服务）· `ninfer`（主程序）· `ninfer-perplexity`（评估）· `ninfer-calibrate`（校准）＋ 运行环境（DLL） |
| **8 处源码补丁** | ① **MSVC 编译兼容 ×7**（让上游源码在 Windows / MSVC 下编得过）；② **思考区收尾补丁** —— 治"模型在思考区 `stop` 导致**空正文**"（官方成品不具备该能力） |
| **GUI 启动器** | `ninfer_launcher.py`：参数下拉 + 命令预览 + 一键起服 + 环境自检 / 就绪自测 + 命名组合 + 场景预设 + **引擎选择（自编 / 官方）** |
| **日志工具** | `serve_tee.py`：关键读数着色 + 精简 / 全部模式；日志全文落盘 |
| **验证与结论** | KVMem 长上下文检索的判活与有效性验证；投机解码的语料效应与档位结论（见下文「关键结论」） |
| **复现材料** | `build/`：构建脚本 + 复现说明 + 产物清单（12 文件 SHA256） |

## 二、两分支

| 分支 | 角色 | 内容 |
|---|---|---|
| **`main`**（本分支） | **项目层** | 启动器 · 启动脚本 · 文档 · 复现材料 |
| **`engine-main`** | **引擎层** | 上游源码 + 本项目全部补丁（**可复现构建**） |

## 三、快速上手

1. **GUI 启动器**：运行 `ninfer_launcher.py`（或双击 `启动器.bat`）——选参数 → 预览命令 → 起服；顶部「引擎」可选 **自编 / 官方**。（**起服后那个控制台窗口就是服务本体，关闭窗口即停止服务**。）
2. **脚本**：
   - 官方引擎：`start-pq2-dflash.bat`（端口 8094）· `start-pq2.bat`（8091）· `start-ptq1-mtp.bat`（8095）
   - 自编引擎：`start-pq2-dflash-designc.bat`
3. **手动**：
```
# 自编引擎
engine/self-built/ninfer-serve.exe models/Ternary-Bonsai-2-27B-ninfer-v3.ninfer --host 127.0.0.1 --port 8094 ...
# 官方引擎
engine/ninfer-serve-120a.exe      models/Ternary-Bonsai-2-27B-ninfer-v3.ninfer --host 127.0.0.1 --port 8094 ...
```

### 运行前提
- **显存**：起服前建议腾出约 **13 GiB**；紧张时先摘 `--vision`、再降 KV 精度或池。
- **主机内存**：启动会锁定 **pinned（不可换出）内存**（默认 `--host-kv-mib 16384`）。
- 首次启动的 `calibrating routes` 需 **10–50 秒**，请勿中断。

## 四、项目结构

> 标 **✅入库** 的随仓库分发；标 **❌不入库** 的因体积 / 上游原因忽略（按 `build/` 可复现）。

| 路径 | 入库 | 内容 |
|---|---|---|
| `ninfer_launcher.py` / `启动器.bat` | ✅ | GUI 启动器（含引擎选择） |
| `serve_tee.py` | ✅ | 日志工具 |
| `start-*.bat` | ✅ | 官方 / 自编 启动脚本 |
| `build/` | ✅ | 自编引擎的构建 / 复现材料 + 产物清单 |
| `docs/` | ✅ | 文档（构建史 / 报告 / 教程 / 截图） |
| `ninfer_launcher_profiles.json` | ✅ | 启动器命名组合 |
| `engine/self-built/` | ❌ 体积 | **自编引擎 + 工具链（4 exe）+ 运行环境** |
| `engine/ninfer-serve-120a.exe` | ❌ 体积 | 官方引擎成品（对照） |
| `models/` | ❌ 体积 | 模型制品 |
| `official-repo/` | ❌ 上游 | 上游源码（复现输入） |
| `logs/` · `.temp/` · `_safety_backups/` | ❌ | 运行日志 / 临时中间物 / 备份 |

**上手**：① 按 `build/README.md` 复现自编引擎（或自备 `engine/`、`models/`）；② 启动器选「引擎」→ 起服。

## 五、关键结论

### 引擎 / 模型真值
| 项 | 值 |
|---|---|
| **自编引擎** | `engine/self-built/ninfer-serve.exe` = `65E3A264…` / ~1.27 GB |
| 官方引擎（对照） | `engine/ninfer-serve-120a.exe` = `E3E0486A…` / 1,329,240,576 B |
| 模型 | `models/Ternary-Bonsai-2-27B-ninfer-v3.ninfer` = 9,520,051,456 B / `CDC4810B…` |
| 上下文 / KV 池 | 默认 262144（256K）/ 17920 token |

### KVMem 环（长上下文机制）
- **显存小池 + 主机内存卸载**：`--kv-capacity` 可**小于**上下文，超出设备池的 KV 分页下放主机内存，由**内容打分检索**决定哪些块常驻。
- **五个环境变量必设**（缺一 = 能起服但**静默答错**）：`NINFER_KV_WINDOW` / `NINFER_KV_RETRIEVE` / `NINFER_KV_RING` / `NINFER_HOST_PAGEABLE` / `NINFER_KV_REUSE_HOSTBACKED`（启动器自动注入）。
- **内容打分默认开**；判活看日志 `kvmem_score: SELECT …` 行。

### 投机解码（dflash2 / MTP / ngram）
- 档位：**dflash2（K1–15）· MTP（K1–5）·以及二者 + ngram 混合**；启动器可切换。
- **K 并非越大越好**：dflash2 **K≥10 收益崩塌**，**K=7 为日常优选**。
- **接受率强依赖语料**：数数字语料接受率 ~91%，散文骤降至 3.7%（中）/ 13.4%（英）。

### 实测（RTX 5080）
- **预填充极值 3,820 tok/s**（`nvfp4` / 224K 档）。
- **解码峰值 748.6 tok/s**（真实工具对话；dflash2 K=7 + ngram 混合）。
- 两值均取自引擎自报日志。

### 思考预算
- `--default-thinking-budget N`（服务端级）治"思考烧光输出预算 → 空正文"。
- 注意：**OpenAI chat 端点不解析请求体里的 `thinking_budget`**（只有 Anthropic 的 `thinking.budget_tokens` 会被读），故只能由服务端参数设置。

## 六、与姊妹仓的关系（同一模式 · 两条技术路线）

> 本仓与 [`paicat1/Bonsai-27B-NInfer`](https://github.com/paicat1/Bonsai-27B-NInfer) 是**同一个模式**：上游给的底子 + 自行编译与优化。唯一区别 = 技术路线不同。

| 维度 | 本仓 | 姊妹仓 |
|---|---|---|
| 上游底子 | NInfer v0.11.0 + KVMem 环 + 沈三殊 v3 成品包 | 沈三殊（技术起点）+ Ambolio 移植 + CraneBW 内核 |
| 本项目做的 | 自行编译引擎 + 工具链 + 启动器 / 日志工具 + 验证 | 移植适配 / 改 CMake / 合内核 / 自产 v2 制品 |
| 架构 | 原生 sm_120a | 改 CMake `89\|120a` |
| **KV / 显存机制** | **KVMem 环**：显存小池 + 主机内存卸载（`--kv-capacity` 可**小于**上下文） | Device/Host **双层 KV**（被动容量） |
| 长上下文 | **KVMem 环（主动检索）** | 双层 KV（被动容量） |
| 投机解码 | dflash2 + MTP + ngram 混合 | MTP / DFlash2 |
| 预填充极值 | 3,820 tok/s | 2,850 tok/s |
| 解码极值 | 748.6 tok/s | 396.9 tok/s |
| **满上下文显存** | 可**卸载到主机**；实跑 free 0.79–1.14 GiB | `k8v4` 256K 满血 **15.36 GiB**（另 pinned 主机 ~9.2 GiB） |
| 模型制品 | 上游 v3（9.52 GB） | 自产 v2（9.81 GiB） |
| 服务端口 | 8094 / 8091 / 8095 | 18787 |

> ⚠️ 两仓极值来自**不同语料与投机组合**，仅作量级对照。

## 鸣谢（上游作者）

- **沈三殊（shensanshu）**：三元-Bonsai 作者——[`shensanshu/ninfer-ada-ternary`](https://modelscope.cn/models/shensanshu/ninfer-ada-ternary)（ModelScope），提供三元补丁 / 转换 / 校验工具链；**两条线共同的技术起点**。
- **Neroued**：NInfer 上游作者（C++20 / CUDA）。[`Neroued/ninfer`](https://github.com/Neroued/ninfer)
- **1314521gjy**：KVMem 环融合。[`1314521gjy/ninfer-fusion-kvmem`](https://github.com/1314521gjy/ninfer-fusion-kvmem)
- **Ambolio**（[`Ambolio/ninfer-4090-windows`](https://github.com/Ambolio/ninfer-4090-windows)）+ **CraneBW**（[`CraneBW/ninfer-ternary-bonsai-ada`](https://github.com/CraneBW/ninfer-ternary-bonsai-ada)）：姊妹仓上游底子。
- **模型根基**：Qwen Team 架构 + unsloth NVFP4 量化 + z-lab DFlash 权重。

## 声明

本仓为**私有仓库**，非官方发布方；上游内容版权归原作者。
