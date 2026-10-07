# NInfer 引擎层 — Bonsai-27B-NInfer-kvmem（官方线 / engine-main 分支）

> 本分支 = **官方 NInfer 引擎完整源码（v0.11.0，sm_120a）+ 本 fork 的编译兼容补丁**。
> 配套 `main` 分支 = 项目层（部署/构建史/方案/启动器）。**两分支一体才是完整项目**：
> 要复现构建 → 在本分支操作；要看项目怎么跑/历史/档位 → 回 `main`。

## 引擎版本与来源

- 上游：`Neroued/ninfer`（sm_120a / RTX 5090 目标），v0.11.0
- 本 fork：Windows + RTX 5080（sm_120a，16GB）+ NVFP4/FP8 路径
- 构建目标：`ninfer-serve`（Release，CUDA 13.3，VS BuildTools 2022 + vcpkg + Ninja/CMake）

## 本 fork 补丁（自编 120a 必须）

官方源码在 **Windows + sm_120a** 组合下从未被编译过，共暴露 **3 类系统性 MSVC 编译不兼容**，均已在本分支修复：

| # | 错误 | 根因 | 修复 | 文件 |
|---|---|---|---|---|
| 1 | `C2326` | lambda 捕获 `constexpr __global__` 函数指针 | 回调内写完整模板实例（保留外层 `constexpr auto kernel` 供 `prepare_shared`） | `src/ops/linear/{bf16,fp8,nvfp4}/...template_launch.cuh`、`nvfp4_a4_tma.cuh` |
| 2 | `C3495` | lambda 简单捕获外层泛型 lambda 作用域 constexpr 局部 | `if constexpr` 双分支 + `[]` 空捕获字面量特化；或内联常量表达式 + 删死变量 | `gdn_gating_proj/bf16/...kernels.cu`、`causal_cache/small_t_i8_launch.cuh` |
| 3 | `C2026` | 单字符串字面量超 16380 上限 | CMake 侧将 JSON 切 <16000/段 + raw string 相邻拼接（`)ninfer_json" R"ninfer_json(`），模板零改动 | `src/runtime/CMakeLists.txt`（`device_profiles.json` 30,566 字符） |

## 复现构建

```powershell
# 1. 环境（本 fork 实测）
#    CUDA 13.3  / VS BuildTools 2022 (vcvars64) / CMake 3.31 / Ninja / vcpkg
# 2. vcpkg 依赖（第一次）
vcpkg install curl ffmpeg[zlib] pkgconf
# 3. CMake 配置 120a
cmake -S . -B build-120a -G Ninja -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_CUDA_ARCHITECTURES=120a -DCMAKE_CUDA_COMPILER=<cuda>/bin/nvcc.exe \
      -DNINFER_SM120_NATIVE=ON -DCMAKE_TOOLCHAIN_FILE=<vcpkg>/scripts/buildsystems/vcpkg.cmake \
      -DVCPKG_TARGET_TRIPLET=x64-windows -DNINFER_BUILD_APPS=ON
# 4. 编译
cmake --build build-120a --target ninfer-serve -j 16
```

> 本分支补丁已包含在源码中，无需手动打补丁。

## 补丁验证
- 编译通过（C2326/C3495/C2026 全消）
- 与官方成品 exe 同探针对照（S2 就绪 / 数数字 decode 与接受率 / meta 一致）——见 main 分支构建史

## 提交历史
- 本分支首个 commit = 官方源码基线（v0.11.0，含补丁）
- 后续 fork 改动按 commit 记录