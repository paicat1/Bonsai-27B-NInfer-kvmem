# 【CODE/CodeBuddy 稿】施工方案 v1.1：官方线三元 Bonsai 落地（探讨稿 · 未收敛 · 未落地）

> 作者：**CODE（CodeBuddy 环境）** ｜ 文档标识：**【CODE 稿】**
> 日期：2026-10-06 ｜ 版本：**v1.1**（v1.0 → v1.1：**认错并修正"mtp + `--lm-head-draft`"的判定**、补入官方工具五分支表、补 `--draft-tokens` 三来源不一致的发现）｜ 对象：官方线 `J:\Bonsai-Official\`
> **⚠️ 文档边界（用户 2026-10-06 令）**：本稿**只由 CODE 维护**；TELE 的施工草案**只由 TELE 维护**。**双方不互改对方文档**；分歧以各自文档提出、交叉复核，收敛后由用户裁决。
> **⚠️ 阶段声明**：本稿是**施工草案**，**未落地、未执行任何写操作**；所有步骤执行前须用户逐次批准。
> 上游依据：官方全库 clone `J:\Bonsai-Official\official-repo\ninfer-fusion-kvmem\`；全库导读 `docs\官方全库导读【CODE】-20261006.md`；CODE 方案 v2.7 `【CODE】方案v2-官方正式版50系切换与验证-20261006.md`。

---

## 0. 结论先行

**本机事实（实测）**：`J:\Bonsai-Official\` = `engine\`（`ninfer-serve-120a.exe` 1,329,240,576 B + 9 DLL）· `models\`（**仅** `Ternary-Bonsai-2-27B-ninfer-v3.ninfer` 9,520,051,456 B）· 三个启动器 · `docs\` · `official-repo\`。

**两条独立的官方证据都指向同一个首起档**：

| 证据 | 对本机（全量档 = dflash2 + mtp + proposal + vision；16 GB **非**小卡）的推荐 |
|---|---|
| 官方**启动器** `start-pq2-dflash.bat` | `--spec dflash2 --draft-tokens 12 --lm-head-draft --vision`（且模型路径已命中 ⇒ **可直接双击**） |
| 官方**工具** `自检-模型件.ps1` L211-212（`hasDflash && hasProposal && !smallCard`） | **`--spec dflash2 --draft-tokens 4 --lm-head-draft`** |

⇒ **首起档 = dflash 档**（双方已收敛）。**本机无 mtponly ⇒ `start-pq2.bat` 会 `REFUSE: model not found`（exit 3），不可作首起。**

**唯一差异**：draft 取 12（启动器）还是 4（工具）⇒ 见 §3.4（**不是矛盾，是"场景值 vs 保守默认"**）。

---

## 1. 与 TELE 稿的交叉核对（两轮累计）

### 1.1 TELE 第 1 轮 7 点

| # | TELE 的点 | CODE 判定（v1.1） |
|---|---|---|
| **1** | **"MTP 档无需另下 mtponly；CODE 方案 N1 写 `start-pq2.bat` 而该 bat 指向 mtponly（本机没有）⇒ 需改指向全量档"** | **✅ 全部采纳（CODE 认错）**。① **CODE 方案 v2.7 §5 N1.1 确实写了"起服 mtp 档（`start-pq2.bat`）"**，而同一份 §1/§9 记着该 bat 指向 mtponly 且**未取** ⇒ **自相矛盾**（CODE 实质错误，v2.8 待改）；② 本机 `models\` 仅全量档一件（实测）；③ **首起档改 dflash** —— 与官方工具 L211 分支一致 |
| 2 | `--gdn-state-fp16` 进备用旋钮 | ✅ 采纳 |
| 3 | draft 依语料，不能一刀切 K=12 | ✅ 采纳（**TELE 稿 §3 S5 原写"DFlash 两边同 K=12"与之自相矛盾，TELE 已自查改正**） |
| 4 | 5080 不在档位表 ⇒ 首次自校准 | ✅ 采纳 |
| 5 | KV dtype 需本机实测（`rk2v4-e8`） | ✅ 采纳 |
| 6 | B01 止血开关白捡 | ✅（CODE 先提，双方一致） |
| 7 | N3.5 超池对比取消 | ✅ 双方一致 |

### 1.2 TELE 第 2 轮的反驳（★ CODE 认错）

**TELE 指出**：CODE 判"全量档 + `--spec mtp --lm-head-draft`"是"官方没有的组合/混搭"**不成立**——官方工具 `自检-模型件.ps1` **L217** 明确把该配对列为 `RECOMMENDED_ARGV`。

**CODE 独立核实（已做，结论：TELE 对，CODE 错）**：该文件 L211–L235 是**完整的五分支推荐表**：

| 条件 | `RECOMMENDED_ARGV` | `ACCELERATION` |
|---|---|---|
| `hasDflash && hasProposal && !smallCard` ← **本机** | **`--spec dflash2 --draft-tokens 4 --lm-head-draft`** | DFLASH2 |
| `hasMtp && hasProposal`（无 dflash2 **或**小卡） | **`--spec mtp --draft-tokens 4 --lm-head-draft`** | MTP_ONLY |
| `hasDflash`（无 proposal） | `--spec dflash2 --draft-tokens 4`（**无** `--lm-head-draft`，否则拒启动） | DFLASH2_NO_PROPOSAL |
| `hasMtp`（无 proposal） | `--spec mtp --draft-tokens 4`（**无** `--lm-head-draft`） | MTP_NO_PROPOSAL |
| 无任何头 | `(no --spec at all)` | NONE |

**L214-217 原文**：`# mtp + proposal head is the small-card answer, and it is also the fallback when there is no dflash2 at all. --lm-head-draft is legal here because the proposal head is present.`

⇒ **CODE 错在哪（自我剖析）**：只读了该文件**前 70 行** + 两个启动器 + `load.cpp`，就断言"官方从未使用该组合"——**把"启动器没用过"外推成"官方没有"**，是**超出证据的断言**。**TELE 只对一半的判定不成立，TELE 是全对。**
⇒ 但 CODE 的**机制推导本身没错**（"全量档有 proposal ⇒ `--lm-head-draft` 合法"），**与工具注释同义**；错的是"断言官方没有"这一步。**收敛**。

### 1.3 CODE 另提 3 条（TELE 二稿已采纳）

| # | 点 |
|---|---|
| 8 | **首起档应是 dflash 档**（本机无 mtponly；且官方工具 L211 对本机同样首选 dflash2）⇒ **双方收敛** |
| 9 | `--vision` 吃显存（R12）：16 GB 若 FATAL，先 `--gdn-state-fp16` 还是先摘 `--vision`，**按实际报错定**，别预设 |
| 10 | 日后补下 mtponly 时按官方配对 `--spec mtp --draft-tokens 4`（**不带** `--lm-head-draft`）——**注意**：带不带取决于该文件**有无 proposal**（工具 L214/L228 两分支），mtponly **无** proposal ⇒ 不带 |

---

## 2. 前置自检（N0 · 只读，零风险）

工作目录 `J:\Bonsai-Official\`。

| # | 动作 | 命令 | 判据（可 grep） | 变红 |
|---|---|---|---|---|
| N0.1 | **模型体检** | `powershell -NoProfile -ExecutionPolicy Bypass -File .\official-repo\ninfer-fusion-kvmem\tools\自检-模型件.ps1 -Model .\models\Ternary-Bonsai-2-27B-ninfer-v3.ninfer -VramGb 16` | `COMPONENTS=` 含 **dflash2,mtp,text,vision**；`HAS_PROPOSAL_HEAD=YES`；**`RECOMMENDED_ARGV=--spec dflash2 --draft-tokens 4 --lm-head-draft`**（L211 分支 ⇒ 也证明 16 GB 被判为**非小卡**）；`MODELCHECK_VERDICT=PASS` | 退出码 **3** = 裸件（**禁加任何 `--spec`**）；`MODELCHECK_REASON=truncated download` = 下坏了 |
| N0.2 | 引擎哈希 | `Get-FileHash .\engine\ninfer-serve-120a.exe -Algorithm SHA256` | **`E3E0486A…`**（GitHub Release digest 同源） | 不符 ⇒ 不是修复件（`42CD0735` 是修复前旧包） |
| N0.3 | 引擎与卡匹配 | `powershell -NoProfile -ExecutionPolicy Bypass -File .\official-repo\ninfer-fusion-kvmem\verify\自检-引擎与卡匹配.ps1` | `HWCARD_VERDICT=PASS` | 架构不符 = **起不来**（不是慢） |
| N0.4 | 路径纯 ASCII | 目视 `J:\Bonsai-Official\` | 全 ASCII | 中文 ⇒ `invalid UTF-8 byte` 启动即挂 |
| N0.5 | 无同名进程 | `Get-Process ninfer-serve* -ErrorAction SilentlyContinue` | 空 | 有则先停（`verify-arch-engine.ps1` 会 `Stop-Process` 同路径者） |
| N0.6 | 显存余量 | `nvidia-smi --query-gpu=memory.used,memory.total --format=csv` | free ≥ ~13 GiB（权重 8.87 GiB + runtime） | 不足 ⇒ 见 §6 |

> **N0.1 的关键读数**：`RECOMMENDED_ARGV` 一行直接给出**官方针对本文件的推荐 argv**，且 `-VramGb 16` 会同时验证"非小卡"判定。
> **N0.1 亦是最关键前置**（官方原话："拿到文件先体检，过了再起服务"）。

---

## 3. 起服（N1）

### 3.1 首选：dflash 档

**直接双击 `J:\Bonsai-Official\start-pq2-dflash.bat`**（官方原样、模型路径已命中 `models\`）。

等价逐字 argv（供核对，**不要手敲**）：
```bat
set NINFER_KV_WINDOW=16384
set NINFER_KV_RETRIEVE=8192
set NINFER_KV_RING=1
set NINFER_HOST_PAGEABLE=1
set NINFER_KV_REUSE_HOSTBACKED=1

engine\ninfer-serve-120a.exe "models\Ternary-Bonsai-2-27B-ninfer-v3.ninfer" ^
  --host 127.0.0.1 --port 8094 --model-id qwen3.8-27b ^
  --max-context 262144 --kv-capacity 17920 --kv-dtype k8v4 --host-kv-mib 16384 ^
  --prefill-chunk 1024 --spec dflash2 --draft-tokens 12 --lm-head-draft --vision ^
  --default-max-tokens 32768 --default-reasoning-effort none --max-concurrency 1 ^
  --max-shared-prefixes 0 ^
  --presence-penalty 0 --temperature 0.7 --top-p 0.9 --top-k 20
```

**判据（三行，逐字）**：
```
INFO  engine ready | ... | weights ... GiB
INFO  capacity | KV 17,920 tokens, k8v4, explicit | pages 280/4,096 | runtime ... GiB | free ... GiB
[ninfer] reuse host-backed: on
```
+ 启动期 `[ring] content scoring ON by default`。

**⚠️ 本机专属**：首次启动会出现 **`calibrating routes for ...`**（5080 不在内置 7 档表）⇒ **10–50 s，千万别杀进程**；测完写 `%LOCALAPPDATA%\ninfer\device-profiles.json`，第二次不再测。

### 3.2 `--spec` / `--lm-head-draft` 的完整配对表（★ v1.1 更正）

**判定机制（源码，三条）**：
1. `serve_options.cpp:603-604`：`--lm-head-draft` ⇒ `options.speculative.proposal_head = ProposalHead::Optimized`
2. `product\speculative_options.h:65-72`：**默认是 `ProposalHead::Full`**；`--draft-tokens` / `--lm-head-draft` 只要求 `--spec mtp|dflash|dflash2`（⇒ **语法上 mtp 允许**）
3. `models\qwen3_5\load.cpp:99-103`：**`if (options.proposal_enabled())` ⇒ 读 `text.proposal`，缺失抛 `selected proposal head is absent from artifact`**

⇒ **一句话规则：`--lm-head-draft` 是否合法，只看"制品有没有 proposal"**（不看 `--spec` 是 mtp 还是 dflash2）。这与官方工具注释**逐字同义**。

### 3.3 MTP 档怎么跑（三条路，待用户选）

| 路 | 做法 | 状态 | 评价 |
|---|---|---|---|
| **A（推荐）** | **N1 只跑 dflash 档**，MTP 对照延到 N3 前按需 | ✅ 官方启动器 + 官方工具**双首选** | 最简单，且是官方 571.9 tok/s 的口径 |
| **B** | 补下 **mtponly 档**（7.65 GB），用 `start-pq2.bat` 原样（`--spec mtp --draft-tokens 4`，**不带** `--lm-head-draft`——该文件无 proposal） | ✅ 官方配对（需下载） | 最干净，受网络 |
| **C** | 全量档 + **`--spec mtp --draft-tokens 4 --lm-head-draft`** | ✅ **官方工具 L217 明列配对**（前提=有 proposal，本机满足）⚠️ 官方启动器未用过 | **v1.1 更正：不是"未验混搭"**，而是"工具推荐、启动器未用"的合法配对；首次仍建议只作探索臂，与路 A 的 dflash 档对照 |

### 3.4 ⭐ 新发现（v1.1）：`--draft-tokens` 官方**自己给的值不一致**

| 来源 | dflash2 档 | mtp 档 |
|---|---|---|
| 官方**启动器**（`start-pq2-dflash.bat` / `start-pq2.bat`） | **12** | **4** |
| 官方**工具**（`自检-模型件.ps1` L212 / L217 / L223 / L229） | **4** | **4** |
| 官方**台账**（复现白皮书 §6.2） | **依语料**：数数字 4→12 = 278→**600**；随机四位数 4→12 = 265→**184**（更深更慢） | — |

⇒ 三者**不矛盾**，是"**保守默认（工具 4）** vs **场景偏好（启动器 12，其场景=数数字/短输出）** vs **语料律（台账）**"。
⇒ **施工含义**：N1 短测**先照启动器 12**（与官方 571.9 tok/s 同口径、可比）；**N3 的 A/B 必须按语料各扫 4/7/12**（§7）。**不要把 4 或 12 当成"正确值"。**

---

## 4. 就绪判据（N1 收口 · **不能用 200 当健康**）

| # | 动作 | 判据 |
|---|---|---|
| N1.5 | `curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8094/v1/models` | **200** 且 body `context_window=262144` |
| N1.6 | **真发一条请求**（`/v1/chat/completions`，`max_tokens=64`） | 返回 token、`finish_reason` 合理 |
| N1.7 | 中文散文烟测（64 token） | 输出非空、非退化（退化形态见 `docs/04` §1 十四态） |

> ⚠️ **B02**：worker 死后 `/v1/models` 仍返 200 ⇒ **判活必须真发请求**。

---

## 5. KVMem 检索证据 + 短测

1. 启动期 **`[ring] content scoring ON by default`**
2. 发过请求后 **`kvmem_score: SELECT` ≥1 行**（`SELECT=0` 有两种含义：短题面正常 / 超窗却没跑 ⇒ 打分失效）
3. **数数字短测**（1000 进 / 1000 出，温度 0）⇒ 抄引擎控制台 `req#1 done | … | prefill … | decode … | dflash2 accepted a/b`
4. 对照锚（官方 4080S）：dflash2 draft 12 ⇒ **571.9 tok/s**、接受 91.5%；**卡不同，2 倍以内正常**，差 3 倍以上再排查

---

## 6. 备用旋钮（仅报错时按需）

| 报错 / 现象 | 处方 | 依据 |
|---|---|---|
| `runtime reservation requires … but only … available`（显存差一点） | `--gdn-state-fp16`（≈ −130 MiB）；仍不够则摘 `--vision` | `docs/03` §3 |
| 图捕获启动失败（部分 WDDM/驱动） | `--no-cuda-graph`（**速度代价实测 0**） | B11 |
| 超池 + 大输出租约崩溃（B01） | 加 **`--kv-lease-growth`** / **`--recover-invariant-failures`**（**已在出厂 exe 里，包内启动器 0 命中**）+ **`--prefill-chunk 256`** | B01 §三 |
| 🔴 **请求侧硬约束** | **`max_tokens` ≤ 池 token 数（17,920）** ⇒ 建议 ≤2048 | `docs/04` L1 表（`docs/00`/`docs/12` 都没写） |

---

## 7. 同口径 A/B（N3 · 判决 H2）

| 项 | 要求 |
|---|---|
| 语料 | ① **数数字**（对齐官方口径）② **散文**（对齐自建线 M6 口径）——**两线都跑两组** |
| draft | **最优值**：每组语料先在**同一支引擎**上扫 **4/7/12**，取该语料最优；**可比值**：跨线对比时用**同一个 draft**。**两件事分开记**，别混 |
| 对齐 | 同 prompt、同 `max_tokens`、同 greedy、同 KV dtype、同上下文 |
| 读数 | 两边都抄 `prefill / decode / TTFT / accepted a/b` |
| 判据 | 同语料同 draft 下官方每步成本/decode 是否显著优于自建当前配置 ⇒ **记录差值，不判"是否 = 88%"**（H1 已撤回） |

**N3.5 超池对比：取消**（双方一致；官方自陈未解决，`docs/06` §1.1）。
**N3.6 / N3.7**（沿用 v2.7）：**KV dtype 本机实测**（先 `k8v4`，异常试 **`rk2v4-e8`**——官方 5080 回执用的就是它）；`--adaptive-mtp`（仅 `--spec mtp`）留探索。

---

## 8. 可选：从官方源码自编 sm_120a

官方 `src-tree/fusion-engine-src/` 是**完整可编译源码**（Apache-2.0，`VERSION 0.11.0-rtx3090`、无子模块）。工具链：驱动 ≥580 · CUDA 13.3 · MSVC（官方 VS18 BuildTools / 14.51）· CMake ≥3.25 · Ninja · **vcpkg（首次需网络）**。
**硬规矩：一个架构一个空目录 clean build**（增量构建会做出"启动即崩"的二进制 `0xC0000005 @ 0x18c729`）。单架构首次 **1–2 小时**。**未验，仅备选。**

---

## 9. 陷阱清单（施工时贴墙）

| # | 陷阱 | 后果 | 处方 |
|---|---|---|---|
| 1 | 不带 `--max-shared-prefixes 0` | 超池题面逐字节重发 ⇒ 实例打砖、此后全 503 | argv 必带 |
| 2 | ring 五开关缺一（尤其 `NINFER_KV_RETRIEVE`） | 起得来、缓存 99.9%、**中段答错、零报错** | 五个都设 |
| 3 | **`max_tokens` > 池 token 数** | worker 崩、全 503 不自愈、`/v1/models` 仍 200 | ≤17920（建议 ≤2048） |
| 4 | 用 `/v1/models` 200 当"可服务" | 崩了也 200 | 判活真发请求 |
| 5 | 路径含中文 | 启动即 `invalid UTF-8 byte` | 纯 ASCII |
| 6 | 在"池 < 题面"下测长文 | 复现官方**未解决**的中段静默丢失 | 池 ≥ 题面；N3.5 取消 |
| 7 | **给无 proposal 的制品加 `--lm-head-draft`** | **`FATAL selected proposal head is absent from artifact`** | 按 §3.2：**只看有无 proposal**（mtponly 无 ⇒ 不带） |
| 8 | 开 `--disk-kv-*` | 本构建零收益 | 别开 |
| 9 | `--max-concurrency > 1` | ring 硬拒 | 保持 1 |
| 10 | 拿 `docs/00~12` 的数字照用 | 那是**早期 8090 单档包**读数 | 只看仓根 5 份当前口径 |
| 11 | **首起用 `start-pq2.bat`** | `REFUSE: model not found`（本机无 mtponly） | 首起用 **`start-pq2-dflash.bat`** |
| 12 | 首次看到 `calibrating routes` 就杀进程 | 校准中断 | 10–50 s 内**别动** |
| 13 | **只看文档不看工具**（CODE v1.0 之误） | 漏掉 `RECOMMENDED_ARGV` 五分支表 ⇒ 误判 | **体检工具的输出本身就是权威推荐**，先跑 N0.1 再谈 argv |

---

## 10. 未验与风险

1. **本机 5080 仍需 N1 实证**：官方 `实测回执与反馈.md` §2 是**别人那台 5080** ⇒ 本机属**复验**。
2. **16 GB 跑 dflash + vision 是否够**：**未验**（R12）；不够时先 `--gdn-state-fp16` 还是先摘 `--vision`，按报错定。
3. **`k8v4` vs `rk2v4-e8` 在本机（sm_120）的可用性**：**未验**。
4. **长文复用**：官方机制在 4080S 已验（99.9%），**本机未验**。
5. **§3.3 路 C（全量档 + mtp spec）**：**工具推荐但启动器未用** ⇒ 首次只作探索臂。
6. **本稿未做任何写操作**。

---

## 11. 待用户裁决

| # | 事项 | 选项 |
|---|---|---|
| **E1** | **首起档** | ① **采纳双方收敛结论：双击 `start-pq2-dflash.bat`**（官方原样，draft 12）② 按官方工具口径跑 `--spec dflash2 --draft-tokens 4 --lm-head-draft`（保守默认）③ 其他 |
| E2 | 是否批准执行 N0（前置自检，**只读零风险**） | 批准 / 暂缓 |
| E3 | MTP 档（§3.3）走哪条路 A / B / C | — |
| E4 | KV dtype 策略（先 `k8v4`，异常试 `rk2v4-e8`） | 确认 / 另定 |
| E5 | 是否把 B01 止血开关补进启动器（**零编译**，但改官方线文件 ⇒ 建议 `.local` 副本） | 批准 / 暂缓 |

---

*【CODE 稿】本稿只由 CODE 维护；施工草案 ≠ 落地批准。分歧以各自文档提出、交叉复核。*
*v1.1 变更摘要：① §1.2 **认错**（"mtp + `--lm-head-draft`"是官方工具明列配对，CODE 漏读 L211-235）；② §3.2 改为完整配对表 + 判定规则（只看有无 proposal）；③ §3.3 路 C 从"未验混搭"改判为"官方工具推荐、启动器未用"；④ **新增 §3.4**：`--draft-tokens` 三来源（启动器 12 / 工具 4 / 台账依语料）；⑤ §9 陷阱 +第 13 条（只看文档不看工具）。*
