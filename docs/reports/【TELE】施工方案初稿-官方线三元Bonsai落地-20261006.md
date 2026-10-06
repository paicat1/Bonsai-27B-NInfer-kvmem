# 【TELE 稿】施工方案初稿：官方线三元 Bonsai 落地（探讨稿 · 未收敛 · 未落地）

- 作者：TeleAgent（第二环境，TELE）｜**文档标识：【TELE 稿】**
- 日期：2026-10-06
- 上游依据：`J:\Bonsai-Official\official-repo\ninfer-fusion-kvmem\`（GitHub `1314521gjy/ninfer-fusion-kvmem`，本地全库 clone，2575 文件，CODE 2026-10-06 拉取）
- 对象：官方线 `J:\Bonsai-Official\`（引擎 `ninfer-serve-120a.exe` E3E0486A + 模型 `Ternary-Bonsai-2-27B-ninfer-v3.ninfer` 9,520,051,456 B）
- **⚠️ 文档边界（用户 2026-10-06 令）**：本稿**只由 TELE 维护**；CODE 的方案稿（`【CODE】方案v2-…md`）只由 CODE 维护，**双方不互改对方文档**。
- **⚠️ 阶段声明**：本稿是**施工草案**，N0–S6 仅为**讨论骨架**，**不是落地方案、未到落地阶段**；任何目录/文件写入仍须用户逐次批准。
- 定位：与 CODE 方案**交叉核对**的独立施工草案；差异以各自文档提出，收敛后由用户裁决。
- **版本：四稿**（2026-10-06；首起档=dflash（双方收敛）+ 官方工具五分支表 + draft 三来源 + S0.1 只读实证 + **§4 既有成果移植（引擎 BUG 官方 0.11.0 仍在）**）

---

## 0. 全库通读后的三条总纲（本稿的立足点）

1. **官方线 ≠ 自建线的升级，是另一支代码线**：官方引擎 = NInfer `VERSION 0.11.0-rtx3090` 基座 + KVMem 环融合（`patches/` 92 改 + 44 增）；我们自建线 = Ambolio `v1.0.8` 移植树。**两条线不可混编、不可互相打补丁**。
2. **官方库文档分两批口径（docs/README.md 明写）**——**读错批次会误判**：
   - **当前口径**（仓根 5 份：`README.md` / `NOTICE.md` / `编译指南-怎么编.md` / `已知问题-初期版本.md` / `实测回执与反馈.md`）
   - **历史口径**（`docs/00~12`、`判据.txt`、`docs/方案/`）：数字/文件名/端口是**早期单档 8090 包**的读数（权重 7.28 GiB / 池 152 页 / 端口 8090），**机制仍有效，数字无效**。
3. **官方已自陈"初期版本、含大量未解决 bug"**（`已知问题-初期版本.md` B01–B20），**唯一正确性级缺陷**=超池中段针静默丢失 ⇒ 施工必须把"池 ≥ 题面"当铁律。

---

## 1. 施工目标与范围

| 项 | 内容 |
|---|---|
| 目标 | 在 **RTX 5080 / 16 GB / sm_120** 上把官方线跑通、取证、与自建线做同口径 A/B（判决 H2） |
| 不做 | ① 不改官方线任何文件（改则复制 `.local` 副本）；② 不在"池 < 题面"状态评长文（踩官方 §1.1 缺陷）；③ 不开磁盘层（本构建零收益）；④ 不开并发（ring 硬要求单路） |
| 前提 | 引擎与模型已就位（N0.1–N0.3 完成，TELE 已核 22 文件无丢失、exe/cudart 哈希与官方 manifest 逐字一致） |
| 产物 | ① 起服就绪日志 ② 两轮复用证据 ③ 数数字 + 散文两语料读数 ④ 与自建线 A/B 表 |

---

## 2. 前置自检（S0 · 零风险，先做）

| # | 动作 | 命令（工作目录 `J:\Bonsai-Official\`） | 判据（可 grep） | 变红 |
|---|---|---|---|---|
| S0.1 | **模型体检**（先探组件再配 `--spec`） | `powershell -File .\official-repo\ninfer-fusion-kvmem\tools\自检-模型件.ps1 -Model .\models\Ternary-Bonsai-2-27B-ninfer-v3.ninfer -VramGb 16` | `COMPONENTS=dflash2,mtp,text,vision`、`SPEC_CHOICES=dflash2,mtp`、`MODELCHECK_VERDICT=PASS` | 退出码 3=裸件（禁加 `--spec`）；`LENGTH_MATCH=NO`=下坏了 |
| S0.2 | **引擎与卡匹配** | `powershell -File .\official-repo\ninfer-fusion-kvmem\verify\自检-引擎与卡匹配.ps1` | `HWCARD_VERDICT=PASS` | 架构不符=**起不来**（非慢）；⚠ 脚本 VRAM 门槛写死 12，16G 卡必过，但**别被它带偏砍池** |
| S0.3 | 路径纯 ASCII | 目视 `J:\Bonsai-Official\` | 全 ASCII | 中文路径 ⇒ `invalid UTF-8 byte` 启动即挂 |
| S0.4 | 无其它 `ninfer-serve*` 在跑 | `Get-Process ninfer-serve*` | 空 | 有则先停（N2 的 `verify-arch-engine.ps1` 会 `Stop-Process` 同路径者，误杀风险） |
| S0.5 | 显存余量 | `nvidia-smi` | free ≥ ~13 GiB | 权重 8.87 GiB + runtime |

> **S0.1 是本方案最关键的前置**：官方原话——"拿到文件先体检，过了再起服务"；裸件加 `--spec` 会 `FATAL missing component`，不加则慢 3.9×。

> **✅ S0.1 已实跑（TELE 2026-10-06，只读零写入；输出逐字）**：
> ```
> MODEL_BYTES=9520051456
> SHA256=CDC4810B0FF17C40D0F62CF214B6E0BCD08346E9EB05CA53371507037793C14A
> CONTAINER_MAGIC=NINFER   CONTAINER_VERSION=3
> LENGTH_MATCH=YES   PAYLOAD_BYTES_DECLARED=9519645952   FILE_BYTES_EXPECTED=9520051456
> COMPONENTS=dflash2,mtp,text,vision   HAS_PROPOSAL_HEAD=YES   SPEC_CHOICES=dflash2,mtp
> RECOMMENDED_ARGV=--spec dflash2 --draft-tokens 4 --lm-head-draft   ACCELERATION=DFLASH2
> MODELCHECK_VERDICT=PASS
> ```
> ⇒ 结论：**① 模型完整（未截断）② 组件齐（dflash2+mtp+text+vision+proposal）③ 官方工具对本机（16 G，判为非小卡）首选 dflash2** ⇒ **S1 首起档=dflash 获官方工具直接背书**；且 `--vision` 合法（vision 组件在）。

---

## 3. 分阶段施工

### S1 起服（**首起档 = dflash 档**，官方原样）

**本机 `models\` 只有全量档**（实核仅 `Ternary-Bonsai-2-27B-ninfer-v3.ninfer`，无 `...-mtponly.ninfer`）：
- ⇒ 官方 `start-pq2.bat`（写死 mtponly）**跑不了**（`REFUSE: model not found`，exit 3）；
- ⇒ 官方 `start-pq2-dflash.bat`（写死全量档）**路径命中、可直接双击**。

**首起档采用 dflash 档 = 官方 `start-pq2-dflash.bat` 原样**（官方 shipped 配对 + 官方工具对"全量档 + 非小卡 + 有 proposal"也首选 dflash2）。

等价逐字 argv（供核对；**直接双击即可，不要手敲**）：

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

**判据（三行日志，逐字）**：
```
INFO  engine ready | ... | weights ... GiB
INFO  capacity | KV 17,920 tokens, k8v4, explicit | pages 280/4,096 | runtime ... GiB | free ... GiB
[ninfer] reuse host-backed: on
```
+ 启动期 `[ring] content scoring ON by default`。

**⚠️ 本机专属（5080）**：
- **内建档位表无 5080** ⇒ 首次启动出现 `calibrating routes for ...`，**10–50s 别杀进程**；测完写 `%LOCALAPPDATA%\ninfer\device-profiles.json`，第二次不再测。
- dflash 档带 `--vision`（吃显存）⇒ 若报 `runtime reservation requires ... but only ... available`：**按实际报错定**——先试 `--gdn-state-fp16`（≈ −130 MiB），仍不够再摘 `--vision`，或改走 **S1c 备用 MTP 档**。

### S1b 官方工具的五分支推荐表（实核；与启动器配对对照）

**官方工具 `tools\自检-模型件.ps1` L211–L235 是完整五分支表**（本机取哪支由"组件/有无 proposal/显存档"共同决定）：

| 分支条件 | 工具输出 `RECOMMENDED_ARGV` | 本机适用 |
|---|---|---|
| `hasDflash && hasProposal && !smallCard` ← **本机（16 GB > 10 GB）** | `--spec dflash2 --draft-tokens 4 --lm-head-draft` | ✅ **首选** |
| `hasMtp && hasProposal` | `--spec mtp --draft-tokens 4 --lm-head-draft` | 备用（S1c） |
| `hasDflash`（无 proposal） | `--spec dflash2 --draft-tokens 4`（不带 `--lm-head-draft`） | — |
| `hasMtp`（无 proposal） | `--spec mtp --draft-tokens 4`（不带 `--lm-head-draft`） | — |
| 无任何头（裸件） | `(no --spec at all)` | — |

**关键行**：L203 `$smallCard = ($VramGb -gt 0 -and $VramGb -le 10)` ⇒ **16 GB 判为非小卡** ⇒ 走第一分支 ⇒ **官方工具对本机也首选 dflash2**（与官方启动器 `start-pq2-dflash.bat` 一致）。

**启动器配对对照（官方 shipped）**：

| 来源 | 模型 | argv 尾部 |
|---|---|---|
| `start-pq2.bat` L46 | mtponly（无 proposal） | `--spec mtp --draft-tokens 4`（不带 `--lm-head-draft`/`--vision`） |
| `start-pq2-dflash.bat` L46 | 全量档（有 proposal） | `--spec dflash2 --draft-tokens 12 --lm-head-draft --vision` |

> **✓ 已收敛（CODE 2026-10-06 修 v1.1 认错，TELE 实核）**：CODE 曾判"全量档 + `--spec mtp --lm-head-draft` 是官方没有的组合"，经 TELE 提供工具 L211–L235 证据后，CODE 核实并**撤回**（承认"只读前 70 行就外推，超出证据"）。⇒ **官方有五分支；本机（16 GB）取 dflash2 分支**。**双方结论一致：首起档 = dflash 档**。

### S1c 备用档：MTP（dflash 档 VRAM 不足时）

```bat
... --spec mtp --draft-tokens 4 --lm-head-draft ^   （其余同 S1，端口 8091，去掉 --vision）
```
- 依据：官方工具 L217（mtp+proposal 的推荐配对）；全量档有 proposal ⇒ 不会被拒。
- **⚠️ 未验组合**：官方启动器没用过；若要作为结论，须**带负控**（同 argv 去掉 `--lm-head-draft` 对比行为）。
- 更干净的替代（路线 B）：补下 `...-v3-mtponly.ninfer`（7.65 GB），用官方 `start-pq2.bat` 原样（**照抄 `--spec mtp --draft-tokens 4`，不带 `--lm-head-draft`**）。

### S2 就绪判据（**不能用 200 当健康**）

| # | 动作 | 判据 |
|---|---|---|
| S2.1 | `curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:8094/v1/models` | **200** 且 body `context_window=262144` |
| S2.2 | **真发一条请求**（`/v1/chat/completions`，`max_tokens=64`） | 返回 token 且 `finish_reason` 合理 |
| S2.3 | 中文散文烟测（64 token） | 输出非空、非退化 |

> ⚠️ 官方 B02/口径陷阱：**worker 死后 `/v1/models` 仍返 200** ⇒ 判活**必须真发请求**。

### S3 KVMem 检索证据 + 短测（在 S1 起服后的同一档上做）

**两条 KVMem 证据**：
1. 启动期 `[ring] content scoring ON by default`
2. 发过请求后 `kvmem_score: SELECT ...` **≥1 行**（=0 ⇒ 打分没跑、退回词法 ⇒ 超池静默答错；短题面本来就不产生 SELECT，属正常）

**数数字短测**（1000 进/1000 出，temp=0）→ 抄引擎控制台权威行 `req#1 done | prefill / decode / TTFT / dflash2 accepted a/b`。对照锚：官方 4080S dflash2 draft12 = 571.9 tok/s、接受 91.5%（**卡不同，2 倍内正常，3 倍以上再排查**）。

> ⚠️ **draft 深度三来源不一致（CODE 也发现，双方一致）**：
> | 来源 | dflash2 | mtp |
> |---|---|---|
> | 官方启动器 | **12** | 4 |
> | 官方工具 L212 | **4** | 4 |
> | 官方台账（复现白皮书 §6.2） | **依语料**：数数字 4→12 = 278→600；随机四位数 4→12 = 265→184 | — |
>
> ⇒ 不矛盾，是"保守默认（工具 4） vs 场景偏好（启动器 12） vs 语料律（台账）"。**施工含义**：S1 短测照启动器用 **12**（与官方 571.9 tok/s 同口径、可比）；**S5 的 A/B 必须按语料各扫 4/7/12**；别把 4 或 12 当"正确值"。

### S4 长文第二轮（**本档全部意义**）

同一会话两轮：第一轮 ~40k token 冷预填，第二轮追问；把唯一标记放题面**中段**。

**判据（两条同时成立）**：
- 第二轮 `cache ≥ 90%`
- 第二轮 `TTFT` 掉到百毫秒级

（本机对照锚：官方 4080S 实测 80,063 token 冷启动 TTFT 70,829 ms → 第二轮 cache 100% / TTFT 126.5 ms。）

### S5 同语料同 draft A/B（判决 H2）

| 项 | 要求 |
|---|---|
| 语料 | ① 数数字（对齐官方口径）② 散文（对齐自建 M6 口径）——**两线都跑两组** |
| draft | **分两件事，别混**：① **最优 draft 依语料**——每组语料先在**同一支引擎**上扫 4/7/12，取该语料最优；② **可比性**——两线对比时用**同一个 draft**。⇒ 记录时分开记（"该语料最优值" 与 "跨线对比所用值"） |
| 对齐 | 同 prompt、同 `max_tokens`、同 greedy、同 KV dtype、同上下文 |
| 读数 | 两边都抄 `prefill / decode / TTFT / accepted a/b` |
| 判据 | **同语料同 draft 下**官方每步成本/decode 是否显著优于自建当前配置——**记录差值，不判"是否=88%"** |

### S6（可选 · 第三条路）从官方源码自编 120a

官方库 `src-tree/fusion-engine-src/` 是**完整可编译源码**（VERSION `0.11.0-rtx3090`）。若要用 5080 原生 120a 自编：`-DCMAKE_CUDA_ARCHITECTURES=120a` + `-DNINFER_SM120_NATIVE=ON` + `-DNINFER_SM120_NVFP4=1 -DNINFER_SM120_FP8=1`；工具链 driver≥580 / CUDA 13.3 / VS18 BuildTools / CMake≥3.25 / vcpkg（需网络）；**每架构空目录清编**（否则 0xC0000005 启动崩溃），首次 1–2 小时。**未验**，仅列为备选。

**⚠️ 若自编用于思考场景，必打 §4.2 的方案 C 补丁**（官方源码缺该兜底）；否则思考开启时仍会出现"思考完、空正文"。

---

## 4. 既有研究成果移植：思考死循环 + 引擎 BUG（方案 C）

> 我方（自建线）此前对"思考死循环"有两份研究 + 一次引擎修复。在新项目（官方线）里逐项判定价值。

### 4.1 雷霆大思考死循环（客户端复合现象）—— 大部分被官方覆盖

- 我方文档：`J:\Bonsai\docs\雷霆大思考死循环-客户端复合现象分析.md`。核心结论：**非引擎缺陷**，是"模型长思考 + 工具集约束 + 会话丢 `reasoning_content` + 贫瘠上下文"多条件耦合的**客户端现象**，只能业务层规避。
- **官方全库 `docs\04-卡死与循环的防治.md`（2026-10-01，295 行）覆盖更全**，且已用**单变量臂**坐实主触发器="**回灌上一轮推理**"，另给五态护栏（EMPTY/TRUNCATED/FIXED_POINT/SAME_PLAN/SHELL_LOOP）、`--presence-penalty`、`max_tokens ≥ 思考预算`。
- ⇒ **客户端部分：以官方 docs/04 为准**（本项目已收录）。
- ⇒ **保留我方一条独特维度**：**"工具集稀缺 ⇒ 思考缺收敛出口 ⇒ 死循环概率↑"**（官方 §1 第 6 条 SHELL_LOOP 只擦边）——作客户端设计参考。

### 4.2 引擎 BUG：思考区提前 stop → 空正文（方案 C）—— **官方 0.11.0 仍存在，可移植** 🔴

**我方修复**（自建树 `src/targets/qwen3_6/impl/frontend/frontend.cpp` L1160–1172，方案 C，commit `145bccb`）：思考区 `stop` 且已启用预算时，**强制走 `ApplyTargetControl` 进正文区**，而非直接终止（防空正文）。

**官方 0.11.0 实核（源码级）**：

| 位置 | 代码 | 判定 |
|---|---|---|
| 官方 `src/models/qwen3_5/frontend/output_session.cpp` L553–560 | `if (stop_token) { terminalize(...); return StopToken; }` | ❌ **无强制进正文兜底**（与修复前同构） |
| 官方 同文件 L568–571 | `if (in_reasoning && budget && tokens==budget) { control_pending=true; return ApplyTargetControl; }` | ✅ 仅"预算用尽"兜底 |
| 官方 同文件 L338–356（terminalize） | 思考区终止只"隐式关闭"，无关闭标记 ⇒ Content 为空 | ❌ 空正文 |

⇒ **官方 0.11.0 的 stop 分支与我方修复前代码逐字同构 ⇒ 该 BUG 官方未修**。官方只在"预算用尽"兜底（L568），"提前 stop"仍空正文。

**⚠️ 触发条件**：仅 **思考开启** 时触发（官方默认 `--default-reasoning-effort none` 关思考 ⇒ 默认不踩；启用思考即相关）。

**移植方式**：把方案 C 的一处改动（复用 `ApplyTargetControl` 通路）打进官方源码 → 重编（见 S6）。**这是 S6 自编的必打补丁**（凡要用思考的场景）。

**附加战略价值**：这是**官方未识别的引擎级正确性 gap**（官方只在平台层兜症状）⇒ 可**回馈上游**（issue/PR）。

---

## 5. 施工陷阱清单（逐条带官方证据，施工时贴墙）

| # | 陷阱 | 后果 | 处方 | 出处 |
|---|---|---|---|---|
| 1 | **不带 `--max-shared-prefixes 0`** | 超池题面逐字节重发 ⇒ 实例打砖，此后全 503 | argv 必带（默认值 `max(concurrency,7)`，**必须显式 0**） | 05 §2 |
| 2 | **ring 五开关缺一**（尤其漏 `NINFER_KV_RETRIEVE`） | 起得来、缓存 99.9%、**但中段答错、零报错** | 五个都设 | 05 §3 |
| 3 | **`max_tokens` > 池 token 数** | worker 崩、**全 503 不自愈**、`/v1/models` 仍 200 | `max_tokens ≤ 17920`（本包用 ≤2048 安全） | 06 §1.2 |
| 4 | 用 `/v1/models` 200 当"可服务" | 崩了也返 200 | 判活**真发一条请求** | 06 §3-5 |
| 5 | 路径含中文 | 启动即 `invalid UTF-8 byte` | 纯 ASCII 路径 | 06 §4-6 |
| 6 | 在"池 < 题面"下测长文 | 复现官方**未解决**的中段静默丢失 | 池 ≥ 题面（N3.5 超池对比**建议不做**） | 06 §1.1 / 红线 §4-7 |
| 7 | 给 Swift 档配行粒度 KV | 只吐 2 token 就 EOS | 用 `k8v4`/`bf16`（本机用三元档，风险低） | 05 §1 |
| 8 | 开 `--disk-kv-*` | 本构建零收益（回灌≈全量重填） | 别开 | 05 §4 |
| 9 | `--max-concurrency > 1` | ring 硬拒 | 保持 1 | 02 §2.1 |
| 10 | 图捕获在部分 WDDM/驱动组合失败 | 启动失败 | 兜底 `--no-cuda-graph`（**速度代价≈0**） | 06 §B11 |
| 11 | 拿别的包的数字照用 | docs/00~12 是历史口径 | 本包只看 `00`/`12` + 仓根 5 份 | docs/README |
| **12** | **给制品配错 `--spec`/`--lm-head-draft`** | mtponly 档加 `--lm-head-draft` ⇒ **`FATAL selected proposal head is absent from artifact` 拒启动** | 按 S1b 三种配对：**mtponly 不带；有 proposal 的才可带** | `docs/12` / `load.cpp:99-103` |
| **13** | **首起用 `start-pq2.bat`** | 本机无 mtponly ⇒ `REFUSE: model not found` | 首起用 **`start-pq2-dflash.bat`**（S1） | 实核 models\ |
| **14** | **思考开启时"思考完空正文"** | 引擎仅在"预算用尽"兜底；"提前 stop"无兜底（官方 0.11.0 未修）⇒ 空正文 | 用 S6 自编时打 §4.2 方案C补丁；或业务层：不回灌推理 + 平台护栏 + `max_tokens` 给足 | §4.2 源码证据 |

---

## 6. 与 CODE 方案的交叉核对（我发现 / 补充的点）

> CODE 方案 v2.7 已吸收绝大部分（H1 撤回、H2 重述、引擎真值、全库导读、B01 止血开关、口径分层陷阱等）。以下为 TELE 独立通读后**补充或提请挑战**的点：

| # | 点 | 说明 | 状态 |
|---|---|---|---|
| 1 | **MTP 档的模型指向 / `--spec` 配对** | CODE 方案 v2.7 N1.1 写"起 mtp 档用 `start-pq2.bat`"，但该 bat 指向 mtponly、**本机没有** ⇒ **CODE 已认错**。TELE 补充官方工具五分支证据后，**CODE 修 v1.1（864DB3B8）、方案 v2.8（482D4010）并完全撤回"混搭"判定** ⇒ **双方收敛：首起档 = dflash 档（S1）** | ✅ **完全收敛** |
| 2 | `--gdn-state-fp16` 进 16G 备用旋钮 | 12GB 卡靠它救回 105 MB 缺口（06 §1.3）；16G 跑 dflash+vision 若 FATAL 同样适用 | ✅ 双方一致 |
| 3 | draft 依语料，不能一刀切 K=12 | 官方台账 §3-6：数数字 4→12 更快、随机四位数 4→12 更慢。**CODE 指出我一稿 §3 S5 又写"DFlash 两边同 K=12"，与其自相矛盾——成立，本稿已改（S5 draft 行拆成"最优/可比"两件事）** | 🤝 已改 |
| 4 | 5080 不在档位表 ⇒ 首次自校准 | `calibrating routes` 10–50s 别杀 | ✅ 双方一致 |
| 5 | KV dtype 需本机实测 | 官方 5080 回执用 `rk2v4-e8`（非默认 `k8v4`） | ✅ 双方一致 |
| 6 | B01 止血开关白捡 | `--kv-lease-growth`/`--recover-invariant-failures` 在 exe 里但启动器 0 命中 | ✅ 双方一致（CODE 先提） |
| 7 | N3.5 超池对比取消 | 官方自陈未解决 | ✅ 双方一致 |
| **8** | **首起档应是 dflash 档**（CODE 提） | 本机无 mtponly + 官方原样配对 | ✅ **TELE 采纳** |
| **9** | **`--vision` 吃显存**（CODE 提） | 16G 若 FATAL，先 `--gdn-state-fp16` 还是先摘 `--vision`，按实测报错定 | ✅ 采纳（并入 S1） |
| **10** | **日后补下 mtponly 必须照抄 `--spec mtp --draft-tokens 4`（不带 `--lm-head-draft`）**（CODE 提） | 加了被拒启动 | ✅ 采纳（并入 S1c/陷阱 12） |

---

## 7. 风险与未验（不许当已验读）

1. **官方 sm_120a 在 5080 的真机验证**：官方 `实测回执与反馈.md` §2 有**群内 5080 真机回执**（修复件 E3E0486A 起服 + 104,991 token 中段针命中）⇒ 本机属**复验**，非首验。**但那是别人那台 5080**，本机仍需 S1 实证。
2. **16 GB 跑 dflash+vision 是否够**：未验；不够则降 `--gdn-state-fp16` 或只跑 mtp 档。
3. **`k8v4` vs `rk2v4-e8` 在本机（sm_120）的可用性**：未验，需 S1 实测。
4. **长文复用（S4）**：官方机制在 4080S 已验（99.9%），**本机未验**。
5. **本稿未做任何写操作**：全部为草案；引擎/模型已在位（用户已做），后续任何步骤执行前须用户批准。

---

## 8. 附录：证据索引（一个事实一个出处）

- 引擎真值：`J:\Bonsai-Official\engine\ninfer-serve-120a.exe` = SHA256 `E3E0486A…` / 1,329,240,576 B；GitHub Release asset digest `sha256:e3e0486a…`（TELE 实测一致）
- 模型：`models\Ternary-Bonsai-2-27B-ninfer-v3.ninfer` = 9,520,051,456 B / SHA256 `CDC4810B…`
- 五开关与 argv：`official-repo\...\docs\12` §2/§5、`start-pq2*.bat`
- 禁忌与陷阱：`docs\05-已知问题与禁忌.md`、`docs\06-Bug手册.md`、`docs\04-卡死与循环的防治.md`
- 全库实测回执（含 5080）：`实测回执与反馈.md` §2
- 缺陷台账 B01–B20：`已知问题-初期版本.md`
- 源码头：`src-tree\fusion-engine-src\VERSION` = `0.11.0-rtx3090`；`device_profiles.json`（7 档，**无 5080**）
- **思考区空正文 BUG 证据链**：官方 `output_session.cpp` L553–560（stop 分支无兜底）、L568–571（仅预算用尽兜底）、L338–356（terminalize 空正文）；我方修复在自建树 `frontend.cpp` L1160–1172（方案 C，commit `145bccb`）
- 我方思考研究：`docs\雷霆大思考死循环-客户端复合现象分析.md`、`docs\ninfer-思考区空正文问题与治本方案-20260927.md`
- 官方思考循环防治：`official-repo\...\docs\04-卡死与循环的防治.md`
- CODE 方案与导读：`J:\Bonsai\【CODE】方案v2-…md`、`J:\Bonsai-Official\docs\官方全库导读【CODE】-20261006.md`
- TELE 交叉审核：`J:\Bonsai\docs\reports\交叉审核-官方正式版50系方案与对比-TELE-20261006.md`

---

*【TELE 稿】本稿只由 TELE 维护；施工草案 ≠ 落地批准，所有步骤执行前须用户逐次批准。分歧以各自文档提出、交叉复核。*
