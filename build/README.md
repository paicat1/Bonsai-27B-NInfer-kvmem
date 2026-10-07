# 自编引擎构建 · 复现说明（Windows / MSVC / CUDA 13.3 / sm_120a）

> 本目录 = 把 **NInfer v0.11.0（+KVMem 环）** 源码，在 **RTX 5080 / sm_120a** 上编成**我们自己的引擎与运行环境**的**构建脚本**。
> 目标：**任何人照此可重现** `ninfer-serve.exe`（含 Design C 补丁）及配套 DLL —— 而不是重走几十小时、还走错。

## 一、依赖（版本）
| 组件 | 版本 / 说明 |
|---|---|
| CUDA | **13.3**（提供 `nvcc`） |
| vcpkg | triplet = **x64-windows** |
| MSVC | **Visual Studio 2022 BuildTools**（`vcvars64.bat`） |
| CMake / Ninja | VS 自带即可 |
| GPU | sm_120a（RTX 50 系） |

## 二、构建步骤
1. **准备源码**：本仓 `engine-main` 分支（已含本项目补丁：C2326/C3495/C2026 + **Design C**）；或本地 `official-repo\ninfer-fusion-kvmem\src-tree\fusion-engine-src`。
2. **改路径**：`s6_configure.bat` / `s6_build.bat` 顶部写死了**本机绝对路径**，改成你自己的（见下表）。
3. **配置**：`cmd /c s6_configure.bat`
4. **编译**：`cmd /c s6_build.bat`（target = `ninfer-serve`）
5. **产物**：`<BUILD>\apps\ninfer-serve.exe` + 同目录 DLL（`.exe` 与 `.dll` 必须放一起）。

## 三、需改的绝对路径（脚本内写死的本机值）
| 脚本 | 变量 | 本机值（改成你的） |
|---|---|---|
| `s6_configure.bat` | CUDA nvcc | `J:/Bonsai/landing/cuda-13.3/bin/nvcc.exe` |
| `s6_configure.bat` | vcpkg toolchain | `J:/vcpkg/scripts/buildsystems/vcpkg.cmake` |
| `s6_configure.bat` | `SRC`（源码） | `…\official-repo\ninfer-fusion-kvmem\src-tree\fusion-engine-src` |
| `s6_configure.bat` / `s6_build.bat` | `BUILD`（**构建输出目录**） | `…\.temp\build-120a` |
| `s6_build.bat` | `PATH` 里的 CUDA bin | `J:\Bonsai\landing\cuda-13.3\bin` |

> `BUILD` 只是**构建中间目录**（可任意，例如 `build-out\`）；产物 `apps\` 建完即可拷出使用。

## 四、关键配置参数
```
-G Ninja
-DCMAKE_BUILD_TYPE=Release
-DCMAKE_CUDA_ARCHITECTURES=120a
-DNINFER_SM120_NATIVE=ON
-DNINFER_BUILD_APPS=ON -DBUILD_TESTING=OFF -DNINFER_BUILD_BENCHMARKS=OFF
```
- **必须先 init `vcvars64.bat`**，否则 MSVC 报 `c1083 cstddef`（环境问题，非代码问题）。
- 编译补丁（C2326×4 / C3495×2 / C2026）已含在源码里，无需另打。

## 五、脚本清单
| 脚本 | 用途 |
|---|---|
| `s6_configure.bat` | CMake 配置（生成 Ninja 工程） |
| `s6_build.bat` | 编译 `ninfer-serve` |
| `s6_build_runtime.bat` | 编运行时整套（apps） |
| `designc_build_frontend.ps1` / `designc_build_test.ps1` / `designc_build_tests.ps1` / `designc_rebuild_serve.ps1` | Design C 相关（前端/单测/serve 重编） |
| `g1_build.ps1` / `g2_build.ps1` | 分阶段构建 |
| `s6_k0_full.ps1` / `s6_k0_scan.ps1` | 构建/扫描辅助 |

## 六、产物落位（重要）
- 编译产物（`ninfer-serve.exe` + DLL）是**我们要用的引擎与环境**，必须放在**正式目录**：本仓 `engine\self-built\`。
- **不要**把成品留在构建中间目录里——构建目录是中间物，**产物是成品**，两者不能混。
