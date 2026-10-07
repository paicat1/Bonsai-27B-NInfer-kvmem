# Bonsai-27B-NInfer-kvmem — 三元 Bonsai 27B 本地推理工程

> 在 **RTX 5080（16GB，sm_120a）** 上，把 **Bonsai-2-27B 三元量化模型** 跑起来——**并编译出本引擎（含 Design C 补丁）与运行环境**。
> **官方成品是底子；"自编引擎 + 运行环境"是本项目的成果。**
> 私有库：`paicat1/Bonsai-27B-NInfer-kvmem`（**非官方发布方**；名字里的 "kvmem" 表示本线血统）。

---

## 一、本仓与姊妹仓（同一模式 · 两条技术路线）

> 本仓与姊妹仓是**同一个模式**：**上游给的底子 + 我们的编译与优化**。**唯一区别 = 技术路线不同。**

| 维度 | **本仓** [`paicat1/Bonsai-27B-NInfer-kvmem`](https://github.com/paicat1/Bonsai-27B-NInfer-kvmem) | **姊妹仓** [`paicat1/Bonsai-27B-NInfer`](https://github.com/paicat1/Bonsai-27B-NInfer) |
|---|---|---|
| **上游给的底子** | NInfer **v0.11.0 + KVMem 环**（`1314521gjy` 融合）+ 沈三殊三元 **v3** 成品包 | **沈三殊**（三元-Bonsai 论文 + `ada-ternary` 工具链 = **技术起点**）+ **Ambolio** `ninfer-4090-windows`（4090/sm_89 移植）+ **CraneBW** 内核 |
| **我们的** | **自编引擎**（编译补丁 C2326/C3495/C2026 + **Design C**） | 移植适配 / 改 CMake / 合内核 / 自产 **v2** 制品 |
| **架构** | 原生 **sm_120a** | 改 CMake `89\|120a` |
| **KV / 显存机制** | **KVMem 环**：显存小池 + 主机内存卸载，`--kv-capacity` 可**小于**上下文；KV 精度多档（`k8v4`/`nvfp4`/`rk*`/`fp8`/`bf16`…） | Device/Host **双层 KV**（被动容量）；精度档 `fp8`/`bf16`/`k8v4`/`nvfp4` |
| **长上下文** | **内容打分主动检索**（KVMem 环） | 被动容量（无检索） |
| **投机解码** | **dflash2（K1–15）· MTP（K1–5）·以及二者 + ngram 混合**（启动器可切；实跑首选 dflash2 K=7 + ngram） | **MTP（K1–5）· DFlash2（K1–15）**（无 ngram 混合） |
| **预填充极值** | **3,820 tok/s**（`nvfp4` / 224K 档） | **2,850 tok/s**（S8 内核；窗口口径极值 2,660） |
| **解码极值** | **748.6 tok/s**（窗口口径；dflash2 K7 + ngram，真实工具语料） | **396.9 tok/s**（窗口口径；全库 78 份日志） |
| **满上下文显存** | KVMem 环可**卸载到主机**；实跑 free 0.79–1.14 GiB | `k8v4` 256K 满血 **15.36 GiB**（另 pinned 主机 ~9.2 GiB） |
| **模型制品** | 沈三殊三元 **v3**（9.52 GB） | 自产 **v2**（9.81 GiB） |
| **服务端口** | 8094 / 8091 / 8095 | 18787 |

> ⚠️ **口径**：两仓极值来自**不同语料与投机组合**（本仓 = 真实工具语料 + dflash2 K7 + ngram；姊妹仓 = 各自历史档位），**不是严格同口径对决**，仅作量级对照。

- **本仓 = 进阶**：姊妹仓是初步的；本仓在**预测解码（+ngram 混合）**与**融合 KVMem**上更全。
- 两仓**彼此隔离、互为对照**（2026-10-06 裁决）。

## 二、本引擎（自编 · 含 Design C）

| 项 | 值 |
|---|---|
| 产物 | `engine\self-built\` —— `ninfer-serve.exe`（**自编 · 含 Design C**）+ `ninfer.exe` / `ninfer-perplexity.exe` / `ninfer-calibrate.exe` + 全套运行 DLL |
| SHA256 | `65E3A264E456A2207C05DCAC5FA5C690F3DA3840C664E9EADD5287BD283D68BA`（`ninfer-serve.exe`） |
| 源码锚点 | `engine-main` 分支 @ `240fe23`（含补丁：C2326×4 / C3495×2 / C2026 + **Design C**） |
| 复现材料 | `build/`（构建脚本 + 复现说明）；产物清单：`build\产物清单.md`（12 文件 SHA256） |
| 怎么用 | 启动器「**引擎**」下拉 = **自编(Design C)** / 官方成品 → 起服 |

> **Design C 治的是"官方成品没有"的能力**：模型在思考区 `stop` 时**空正文**（思考没闭合）——Design C 强制走进正文区。详见 `build/`、构建史 §九 与 A2-1。

## 三、两分支一体

| 分支 | 角色 | 内容 |
|---|---|---|
| **`main`**（本分支） | **项目层** | 启动器、起服 BAT、构建史 / 报告 / **复现材料** |
| **`engine-main`** | **引擎层** | NInfer v0.11.0（+ KVMem 环）源码 + 本项目补丁 + Design C（**可复现构建**） |

- 要看**引擎代码、改了哪些补丁、怎么重编** → 切到 `engine-main`，读它的 `README.md`。
- 要看**项目怎么跑起来、自编引擎在哪、历史/报告** → 留在 `main`。

> 引擎成品（~1.27 GB 级二进制）、模型制品、上游全库 clone **不入库**（体积 / 上游内容，见 `.gitignore`）；**自编引擎靠 `build/` 复现 + `build\产物清单.md` 哈希锚定**。

## 四、快速上手（起服）

1. **GUI 启动器**：运行 `ninfer_launcher.py`（或双击 `启动器.bat`）——下拉配置参数，右侧实时预览命令，一键起服（**新控制台窗口，关窗 = 停服**）；可「环境自检」「就绪自测」；含命名组合 + 场景预设；顶部有 **「引擎」下拉：官方成品 / 自编(Design C)**。
2. **启动脚本**：
   - 官方引擎：`start-pq2-dflash.bat`（端口 8094）/ `start-pq2.bat`（8091）/ `start-ptq1-mtp.bat`（8095）；
   - **自编引擎**：`start-pq2-dflash-designc.bat`。
3. **手动**：
   - 自编：`engine\self-built\ninfer-serve.exe models\Ternary-Bonsai-2-27B-ninfer-v3.ninfer --host 127.0.0.1 --port 8094 ...`
   - 官方：`engine\ninfer-serve-120a.exe models\Ternary-Bonsai-2-27B-ninfer-v3.ninfer --host 127.0.0.1 --port 8094 ...`

> ⚠️ **serve 启停一律由用户双击完成**——"关窗 = 停服"的心智模型不能被后台进程破坏。

### 运行前提（两笔账：显存 + 主机内存）

- **显存**：引擎 + KV 池 + 视觉塔需占相当显存；起服前建议腾出 **~13 GiB**。显存紧时先摘 `--vision`、再降 KV 精度 / 池。
- **主机内存**：引擎启动会锁定 **pinned（不可换出）主机内存**（host state + host KV，默认 `--host-kv-mib 16384`）。内存紧张机器可能在启动阶段失败（报错对着 host KV）。降配：`--host-kv-mib 8192` / 调小 host state。

### 5080 注意

首次启动的 `calibrating routes` 会花 **10–50s**，**别杀**。

## 五、项目结构（本地 = 库）

> 下表 = **本地实际结构**；标 **✅入库** 的随库分发，标 **❌不入库** 的因体积/上游原因忽略（clone 后需自行获取或按 `build/` 复现）。

| 路径 | 入库 | 内容 |
|---|---|---|
| `ninfer_launcher.py` / `启动器.bat` | ✅ | GUI 启动器（参数下拉 + 命令预览 + 起服 + 自检/就绪自测 + 命名组合 + **「引擎」下拉：官方 / 自编**） |
| `serve_tee.py` | ✅ | 日志转存（着色 + 精简/全部；全文落盘 `logs\serve_<时间戳>.log`） |
| `start-pq2-dflash.bat` / `start-pq2.bat` / `start-ptq1-mtp.bat` | ✅ | **官方引擎**三档启动器 |
| `start-pq2-dflash-designc.bat` | ✅ | **自编引擎（Design C）**启动器 |
| **`build/`** | ✅ | **自编引擎的构建 / 复现材料**（构建脚本 + 复现说明 + 产物清单） |
| `README.md` / `docs/` | ✅ | 项目层文档（构建史 / 报告 / 教程 / 截图） |
| `ninfer_launcher_profiles.json` | ✅ | 启动器命名组合（含实跑档） |
| **`engine/`** | ❌ 体积 | 引擎成品：**`self-built/ninfer-serve.exe` = 本引擎（含 Design C）**；`ninfer-serve-120a.exe` = 官方成品（对照）。均配全套运行 DLL |
| `models/` | ❌ 体积 | 模型制品 `Ternary-Bonsai-2-27B-ninfer-v3.ninfer` |
| `official-repo/` | ❌ 上游 | 上游全库 clone（引擎源码，复现输入） |
| `logs/` | ❌ | 运行日志（含 `kvmem_score` 检索证据） |
| `.temp/` | ❌ | 临时中间物（草稿 / 一次性脚本 / 日志），不入库 |
| `_safety_backups/` | ❌ | 备份快照 |

**上手**：① 按 `build/README.md` 复现引擎（或自备 `engine/`、`models/`）；② 启动器里选「引擎」= 自编 / 官方 → 起服。

## 六、关键结论（速览）

### 引擎 / 模型真值

| 项 | 值 |
|---|---|
| **自编引擎** | `engine\self-built\ninfer-serve.exe` = **`65E3A264…`** / ~1.27 GB（**含 Design C**） |
| 官方引擎 | `engine\ninfer-serve-120a.exe` = `E3E0486A…` / 1,329,240,576 B（对照用；Release asset digest 交叉验证同源） |
| 模型 | `models\Ternary-Bonsai-2-27B-ninfer-v3.ninfer` = **9,520,051,456 B** / SHA256 `CDC4810B0FF17C40D0F62CF214B6E0BCD08346E9EB05CA53371507037793C14A` |
| 上下文 / KV 池 | 官方默认 **262144（256K）** / **17920** token（设备池） |

> ⚠️ 上游资料里写 `42CD0735…` / 1,343,609,856 B 的是**修复前旧包**的 hash，勿照用。

### KVMem 机制要点

- **KVMem 环 = 显存小池 + 主机内存大盘卸载**：`--kv-capacity` 可**小于**上下文，超出设备池的 KV 分页下放主机内存，靠**内容打分检索**决定哪些块常驻。
- **五环境变量必设**（缺一 = 起得来但**静默答错**）：`NINFER_KV_WINDOW` / `NINFER_KV_RETRIEVE` / `NINFER_KV_RING` / `NINFER_HOST_PAGEABLE` / `NINFER_KV_REUSE_HOSTBACKED`（启动器自动注入）。
- **内容打分默认 ON**；判活看日志 `kvmem_score: SELECT …` 行（无 = 打分没跑）。
- **口径陷阱**：上游 docs 分"当前 / 历史"两批，读错必误判。

### 实测（本机 5080）

- **S1–S2**：起服监听 `127.0.0.1:8094`；`GET /v1/models` 200 + **真发一条请求** 200（判活必须真发请求，`/v1/models` 200 ≠ 健康）。
- **S4 长文检索三层判据**（G14）：正文埋针 + **问句独立成回合** ⇒ 问句 span ≤ `MAXQ=256` ⇒ 打分真跑（`scored_kept>0`）、针被答出、kept 覆盖针位。
- **S5 同口径 A/B（数数字 / 中文散文 / 英文散文）**：同一 dflash 档下，数数字接受率 **91.5%** 而散文骤降到 **3.7%（中）/ 13.4%（英）** ⇒ "decode 高"**仅对数数字语料成立**；差距本质是**语料效应**（接受率是强内容依赖指标，不能用合成填充文本测）。
- **S5 判决（H2）**：同语料同 draft 口径下，本仓原生**并未显著优于**姊妹仓当前配置（散文两组对方反超）。
- **S6 自编 120a**：源码**全树 MSVC 构建成功**（3 类编译补丁）+ **Design C**——双 exe 探针实测：**自编 serve 的思考预算生效（稳定输出正文），官方成品不解析该字段**。
- **真实负载实跑（2026-10-07，19 请求，32 工具对话）**：档位 **dflash2 K=7 + 思考预算 16000**，KV 163,840 **全驻显存**（free 0.84 GiB）。**瞬时峰值 decode 748.6 tok/s**；请求级 decode 180–655、**mixed speculation 接受率 35.7–94.4%**（长输出 ngram 命中 ≈98%）；续写缓存 99.9–100%、TTFT 0.18–0.29 s。⇒ 真实负载同样能跑高——**关键在 K=7 + ngram 混合投机**。
- **预填充极值 3,820 tok/s**（2026-10-07 配置 `--kv-dtype nvfp4 --max-context 229376`，KV 全驻）：`req#2 done | prompt 8,979 | prefill 3.82k tok/s` —— 全区间最高。

![真实负载实跑 —— CMD 控制台日志：decode 峰值 748.6 tok/s（KVMem SELECT / throughput / req#done）](docs/images/run-20261007-decode748.png)

### DFlash2 深度与语料

- **dflash 深度收益强依语料**：数数字（可预测）K 越深越快（K4 322 → K12 654 tok/s）；散文（不可预测）**K=7 最优**，K12 反而略降 ⇒ 与上游教程"不可预测输出 draft 12 更慢"吻合。
- **K=7 = 日常甜点**：真实工具对话用 **dflash2 K=7 + ngram 混合投机** → 接受率 35.7–94.4%、decode 峰值 748.6；而 **d12 + 纯 dflash** 同场景接受率仅 ~22.7%。⇒ **K≥10 断崖、K=7 最优**；日常建议 **K=7**。

### 思考预算

- `--default-thinking-budget N`（服务端 argv 级）治"**思考墙死循环**"（思考烧光输出预算 → 空正文）。⚠️ **OpenAI chat 端点不解析请求体里的 `thinking_budget`**（仅 Anthropic 的 `thinking.budget_tokens` 被读），只能靠服务端此参数（启动器「思考预算」档）。

## 鸣谢（上游作者）

本项目站在上游作者肩上落地，致谢：

- **沈三殊（shensanshu）· UP主**：**三元-Bonsai 作者**——发布三元 Bonsai 论文 / 工具链（[`shensanshu/ninfer-ada-ternary`](https://modelscope.cn/models/shensanshu/ninfer-ada-ternary)，ModelScope）**及本仓所用的"三元 Bonsai 成品引擎包"（`infer-engine-sm120a-20261002`）与三元 v3 制品**；**也是姊妹仓的技术起点**（三元-Bonsai 论文 + `ada-ternary` 工具链），是**两条线共同的源头**。
- **Neroued**：NInfer 上游作者（C++20/CUDA）。[`Neroued/ninfer`](https://github.com/Neroued/ninfer)
- **1314521gjy**：本线引擎血统来源 [`1314521gjy/ninfer-fusion-kvmem`](https://github.com/1314521gjy/ninfer-fusion-kvmem)（NInfer v0.11.0 基座 + KVMem 环融合）。
- **Ambolio**（[`Ambolio/ninfer-4090-windows`](https://github.com/Ambolio/ninfer-4090-windows) 移植树）+ **CraneBW**（[`CraneBW/ninfer-ternary-bonsai-ada`](https://github.com/CraneBW/ninfer-ternary-bonsai-ada) 三元内核）：姊妹仓的上游底子。
- **ashalliants / Warlax / TertiumOrganum1 / UDPSendToFailed / IMGillusion** 等 NInfer 整合线与各 fork 作者：引擎整合与内核贡献者。
- **模型根基**：Qwen Team 架构 + unsloth NVFP4 量化 + z-lab DFlash 权重。

## 分支说明

本 `main` 分支承载**项目层**（启动器 / 起服 BAT / 构建史 / 报告 / **复现材料**）；引擎源码与补丁在 **`engine-main`** 分支（含复现索引 README）。两分支配合使用。
