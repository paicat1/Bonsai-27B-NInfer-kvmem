# Bonsai-27B-NInfer-kvmem — engine-main 分支（引擎层）复现索引

> 本分支 = **官方 NInfer v0.11.0（+ KVMem 环）** 完整 C++ / CUDA 源码 + 本项目为 **Windows / MSVC / sm_120a** 所打的补丁（**可复现构建**）。
> 这是**引擎层**；项目层（启动器 / 构建史 / 报告）在 `main` 分支，**两分支配合才是一个完整项目**。
> 本 README 是**复现索引**：每一处改动、怎么重编，都列出来，让复现者自行照单查证。

---

## 0. 先看这几样（搞清楚全貌再动手）

| 要看什么 | 在哪 |
|---|---|
| 完整开发史（双线背景、S0–S6、补丁来历） | `main` 分支 `docs/Bonsai-27B-NInfer-kvmem-项目构建史.md` |
| 官方全库导读 | `main` 分支 `docs/官方全库导读【CODE】-20261006.md` |
| 官方包自带教程（KVMem 与短测） | `main` 分支 `docs/教程-KVMem与短测-给agent与使用者.md` |
| 引擎成品（官方 exe，非本分支） | `main` 分支 `engine\`（不入库） |

## 一、血统（这份源码从哪来）

- **基座**：NInfer `VERSION 0.11.0-rtx3090` + **KVMem 环**融合。
- **来源**：`github.com/1314521gjy/ninfer-fusion-kvmem`（Release `engine-v0.11.0-kvmem-20261003`）；本分支从 `src-tree/fusion-engine-src` 重建（**2463 文件** + 根 `NOTICE.md`）。
- **许可**：Apache-2.0，**保留上游 `LICENSE` / `NOTICE.md`**。
- **提示**：本分支与自建线（Ambolio v1.0.8 移植树）是**两支不同代码线**，**不可混编 / 互打补丁**。

## 二、本项目相对上游的补丁（复现要点）

> 全部补丁带 `NOTE(S6 patch)` 注释；**相对上游 tag 的 diff = 恰好这些补丁**。

### 2.1 三类 MSVC 编译兼容补丁（Windows + sm_120a 是官方未验证路径）

| 类别 | 位置 | 症状 → 修法 |
|---|---|---|
| **C2326**（4 处） | `src/ops/linear/{fp8,bf16,nvfp4}/*_template_launch.cuh`、`src/ops/linear/nvfp4/nvfp4_a4_tma.cuh` | MSVC 禁 lambda 捕获 `constexpr __global__` 函数指针 → 保留外层 kernel + 回调内写完整模板实例 |
| **C3495**（2 处） | `src/ops/gdn_gating_proj/bf16/bf16_gdn_gating_proj_kernels.cu`、`src/ops/softmax_attention/dense/causal_cache/small_t_i8_launch.cuh` | 外层泛型 lambda 内 constexpr 局部被内层 `[&]` 回调捕获作模板实参 → `if constexpr` 双分支 + `[]` 空捕获字面量特化 |
| **C2026**（1 处生成模板） | `device_profiles_builtin.cpp.in`（CMake 侧切分） | 单 raw string 字面量（30,566 字符）超 MSVC 单字面量上限 16,380 → 按 16000/段切、相邻 raw string 拼接（内容逐字节不变） |

### 2.2 Design C 补丁（思考区空正文 —— 自编核心价值）

- **主体**：`src/models/qwen3_5/frontend/output_session.cpp`（thinking 区 stop_token 分支强制走 target-control，让思考闭合、模型进正文区）。
- **单测同步**：`tests/models/qwen3_5/test_frontend.cpp`（原断言钉死"终止优先"，改为 Design C 新行为）。
- **STANDALONE 测试机制**：`ninfer_qwen3_5_frontend_test` 独立 exe（绕开上游多文件破损测试）。
- **实测**：自编 serve 的思考预算生效（稳定输出正文）；官方成品不解析该字段（对照见 `main` 构建史 A2-1）。

## 三、复现构建（Windows / MSVC / CUDA 13.3 / sm_120a）

- **工具链**：CUDA 13.3、VS BuildTools 2022（cl 14.43）、CMake 3.31.6、Ninja、vcpkg（curl / ffmpeg / pkgconf）。
- **配置**：`-DCMAKE_CUDA_ARCHITECTURES=120a -DNINFER_SM120_NATIVE=ON`。
- **构建**：`cmd /c call vcvars64.bat && ninja -k 0`（**必须先 init vcvars**，否则 C1083 `cstddef/array`——环境问题非代码问题）。
- **结果**：**全树构建成功**（`ninfer-serve` 链路 149/149 + 全图 `ninja -k 0` 28/28，FAILED=0 / error=0）。

**MSVC 规避写法清单（踩坑沉淀）**：
- ✅ 回调内不引用外层 constexpr 局部（`if constexpr` 分支 + 字面量特化、`[]` 空捕获）；
- ✅ constexpr 上提为函数模板形参后直接引用；
- ✅ `template <auto Kernel>` 助手；
- ❌ 泛型 lambda 经 configure helper 传入；
- ❌ 运行时拷贝 constexpr 局部当模板实参。

## 四、与上游的关系 / 红线

- 本 fork 的补丁**只进私有库** `paicat1/Bonsai-27B-NInfer-kvmem`（engine-main 分支），**不推作者官方库** `1314521gjy/ninfer-fusion-kvmem`。
- 引擎成品 exe 与模型制品**不入库**（见 `main` 分支 `.gitignore`）；本分支只承载**源码 + 补丁**（clone 检出即得含补丁的完整可构建源码）。

## 五、上游血统与鸣谢

- **Neroued**：NInfer 官方上游作者（C++20/CUDA）。[`Neroued/ninfer`](https://github.com/Neroued/ninfer)
- **1314521gjy**：本线引擎血统来源 `ninfer-fusion-kvmem`（NInfer v0.11.0 基座 + KVMem 环融合）。
- **ashalliants / Warlax / TertiumOrganum1 / UDPSendToFailed / IMGillusion / Wallawalla47 / tmark00** 等 NInfer 整合线与各 fork 作者：官方引擎的整合与内核贡献者（上游 README 血统段落另见官方仓）。
- **沈三殊（shensanshu）**：三元-Bonsai 技术论文作者（技术起点）。
- **模型根基**：Qwen Team 架构 + unsloth NVFP4 量化 + z-lab DFlash 权重。
