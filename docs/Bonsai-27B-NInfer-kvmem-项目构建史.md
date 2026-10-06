# Bonsai 官方线（J:\Bonsai-Official）项目构建史

> **文档性质**：官方线项目的**过程实录**（边做边记），参照自建线 `J:\Bonsai\docs\项目构建史.md` 体例：**只写有证据的；证据不足标【待补】；没掌握的明说没掌握。**
> **建立日期**：2026-10-06（TeleAgent，TELE）
> **修订记录**：2026-10-06 首建（覆盖 10-02 触发 → 10-06 物料落地、交叉评审、施工方案、引擎 BUG 发现、工作区交接）；2026-10-06 晚增补（S0 只读自检完成、建本地 git 库待提交、分工变更 TELE 施工 / CODE 复核、CODE 反向复核四修正核验）。
> **写作背景**：防"会话记忆拼凑/编造"的教训——历史必须落纸带证据。（初建时本项目无 git 库；**2026-10-06 晚已 `git init`，见 §8-B**。）
> **协作模式**：CODE（CodeBuddy 环境）+ TELE（TeleAgent 环境）双侧协作，**双方不互改对方文档、各自加标识**。

---

## 一、一句话概括

2026-10-06，依据 UP主发布的**三元 Bonsai 官方成品引擎包** `infer-engine-sm120a-20261002`，用户裁决**双线并行、两项目完全隔离**：**官方线**（`J:\Bonsai-Official`，官方原生 sm_120a 引擎 + 官方三元 v3 制品）与**自建线**（`J:\Bonsai`，既有 Ambolio v1.0.8 移植树 + 自产 v2 制品，**冻结只读对照**）。当日完成：引擎/模型物料落地与校验、目录重构、双方交叉评审收敛（首起档=dflash）、双方施工方案初稿、**"思考区空正文"引擎 BUG 在官方 0.11.0 仍存在的源码级发现**、以及工作区交接。

---

## 二、前置背景（上游，非本项目产出）

- **官方包来源**：UP主 2026-10-02 发布的 `infer-engine-sm120a-20261002`（本地分发副本 `J:\分发\正式版50系\`）。引擎 `ninfer-serve-120a.exe` 构建于 **2026-10-02 21:47**，**原生 sm_120a 单架构**（无 PTX 兜底）。
- **官方开源仓**：`github.com/1314521gjy/ninfer-fusion-kvmem`（**2026-10-04 12:04:52 创建**，GitHub API 实证），C++ / 92 stars；Release `engine-v0.11.0-kvmem-20261003`（**2026-10-04 12:29:46 发布**）。魔搭镜像 `shensanshu/ninfer-master-shensanshu-kvmem`（**只含源码**）。
- **血统**：官方引擎 = **NInfer `VERSION 0.11.0-rtx3090` 基座 + KVMem 环融合**（`patches/` 92 改 + 44 增）；与自建线 **Ambolio v1.0.8 移植树**是**两支不同代码线**，**不可混编/互打补丁**（本仓 `src-tree\fusion-engine-src\VERSION` 实证）。
- **官方自陈**：初期版本、含大量未解决 bug（`已知问题-初期版本.md` B01–B20）；**唯一正确性级缺陷 = 超池中段针静默丢失**（官方"别等我们修"）。
- **官方文档两批口径**（`docs/README.md` 明写）：**当前口径**=仓根 5 份；**历史口径**=`docs/00~12`、`判据.txt`、`docs/方案/`（早期单档 8090 包读数，**机制有效、数字无效**）。

---

## 三、触发与双线裁决（2026-10-02 → 10-06）

- **10-02**：UP主发布引擎包。CODE 逐文件核实：包**不是通用 ninfer 包，而是三元 Bonsai 官方成品专包**（`start-pq2.bat` 写死 `...-v3-mtponly.ninfer`；`start-pq2-dflash.bat` 写死 `...-v3.ninfer`）。
- **10-06**：TELE 独立核实引擎包完整性——实跑 `verify-kit-manifest.ps1` → **`ok=18 mismatch=0 missing=0`**。
- **10-06**：用户裁决 **"双线并行、两项目完全隔离、彼此验证"**（不再做"主线二选一"）。方案由 CODE 演进（v2.0→v2.8），TELE 交叉审核。

---

## 四、物料落地与目录重构（2026-10-06）

- **模型下载**：用户将官方 v3 全量档下载到 `J:\Bonsai-Official\`。⚠️ 曾误落 `J:\bonsai offical`（含空格路径），后按规范名 `J:\Bonsai-Official` 到位。
- **模型校验**（TELE 实测）：`Ternary-Bonsai-2-27B-ninfer-v3.ninfer` = **9,520,051,456 B / SHA256 `CDC4810B…`**（LastWriteTime 2026-10-06 20:11:05）。
- **目录重构**（CODE 执行，TELE 独立审核通过）：按方案 §4.1 重构为 `engine\ / models\ / verify-out\ / docs\{reports}\` + 三个启动器在根。审核结果：**22 文件无丢失、抽查 exe/cudart 哈希与官方 manifest 逐字一致、启动器 `%ROOT%` 命中**。
- **引擎真值**：`engine\ninfer-serve-120a.exe` = **`E3E0486A…` / 1,329,240,576 B**（GitHub Release asset `digest=sha256:e3e0486a…` 交叉验证同源）。
  - ⚠️ **README-pack §2 写的 `42CD0735…` / 1,343,609,856 B 是"修复前旧包"的 hash**（官方缺陷台账 B16），**勿照用**。
- **官方全库 clone**：`J:\Bonsai-Official\official-repo\ninfer-fusion-kvmem\`（**2575 文件**（含 `.git`）/ 88.8 MB；源码口径 2547 文件 / 75.4 MB；`src-tree` 子树 2463 文件 / 72.3 MB，CODE 拉取）；CODE 产出 `docs\官方全库导读【CODE】-20261006.md`；TELE 独立通读 24+ 份文档与源码树结构。

---

## 五、交叉评审实录（2026-10-06）

> 双方互检而非互相盖章（用户严令"不要当彼此的应声虫"）。以下为关键交锋与收敛。

- **H1 撤回**：CODE 原立 H1（"接受率差距根因在制品代际"）。**TELE 抓出致命口径错误**——官方接受率是**"数数字"语料**、自建线 M6 是**散文语料**，两端不可比。CODE 复核后**撤回 H1** 并认错。
- **H2 立**：改立新核心假设（同语料同 draft 下比"每步成本/decode"）。
- **TELE 二审**：核实 `38.7%/6.4%`（09-30 复测）与 `44.0%/5.4%`（M6 09-22）**不是"同语料复测"，是"不同引擎配置代次"** ⇒ H2 立论数据须用当前配置。
- **CUDA 路径复核**：TELE 曾判 `verify-arch-engine.ps1` 三处 E 盘硬编码"必须改否则跑不起来"；**CODE 反驳 + TELE 实测后自我更正**——实际仅 L61（输出位置）建议改，L25 可传参绕过、L88 无害（引擎自带 9 DLL 从自身目录加载）。
- **五分支表交锋**：CODE 曾判"全量档 + `--spec mtp --lm-head-draft` 是官方没有的组合"；**TELE 提供官方工具 `tools\自检-模型件.ps1` L211–L235 五分支表证据**（L217 明确推荐该配对），CODE **核实后撤回"混搭"判定并认错**（承认"只读前 70 行就外推"）。
- **收敛点：首起档 = dflash 档**（官方启动器 `start-pq2-dflash.bat` + 官方工具 L211 分支 + 官方 5080 回执，三源一致）。

---

## 六、施工方案与实证（2026-10-06）

- **双方施工方案**（各自维护）：`docs\reports\【CODE】施工方案初稿-…md`（CODE，v1.1）、`docs\reports\【TELE】施工方案初稿-…md`（TELE，四稿）。
- **TELE 只读实证（S0.1 模型体检）**：实跑官方工具 → `LENGTH_MATCH=YES`、`COMPONENTS=dflash2,mtp,text,vision`、`HAS_PROPOSAL_HEAD=YES`、**`RECOMMENDED_ARGV=--spec dflash2 --draft-tokens 4 --lm-head-draft`**、`MODELCHECK_VERDICT=PASS` ⇒ **模型完整、组件齐、官方工具对 16G 首选 dflash2**。
- **🔴 引擎 BUG 发现（TELE，源码级）**：我方（自建线）曾修"思考区提前 stop → 空正文"BUG（方案 C，commit `145bccb`，落点自建树 `frontend.cpp` L1160–1172）。**TELE 核实官方 0.11.0 仍在**：
  - 官方 `src/models/qwen3_5/frontend/output_session.cpp` **L553–560（stop 分支）无强制进正文兜底**（与修复前同构）；
  - 仅 **L568–571（预算用尽）** 才走 `ApplyTargetControl`；
  - **L338–356（terminalize）** 思考区终止只"隐式关闭"，无关闭标记 ⇒ **正文为空**。
  - ⇒ 官方未识别/未修的**引擎级正确性 gap**；触发条件 = **仅思考开启**（官方默认 `--default-reasoning-effort none`）。**可移植（自编时必打补丁）、可回馈上游。**
  - ⚠️ **2026-10-06 晚订正（见 §8-D-B）**：该行为实为**官方既定、被单测钉住**（`tests\models\qwen3_5\test_frontend.cpp:2141-2148`），非单纯疏漏；"可回馈上游"须**同改该测试**。（"自建树已修"亦须限定为开发树 `ninfer-4090-windows`，见 §8-D-C1。）

---

## 七、关键事实台账（施工前必读，均带证据）

| 项 | 值 / 判据 |
|---|---|
| 引擎 | `ninfer-serve-120a.exe` = `E3E0486A…` / 1,329,240,576 B（Release digest 同源） |
| 模型 | `Ternary-Bonsai-2-27B-ninfer-v3.ninfer` = 9,520,051,456 B / `CDC4810B…` |
| 首起档 | **dflash 档**（`start-pq2-dflash.bat` 原样；本机无 mtponly） |
| 参数铁律 | 五环境变量必设；`--max-shared-prefixes 0` 必带；`max_tokens ≤ 17,920`；`--max-concurrency 1` |
| 判活 | **必须真发请求**（`/v1/models` 200 ≠ 健康，B02） |
| 5080 专属 | 内置档位表无 5080 ⇒ 首次 `calibrating routes` 10–50s **别杀**；dflash 带 `--vision`，显存紧先 `--gdn-state-fp16` |
| draft 深度 | 三来源不一致（启动器 12 / 工具 4 / 台账依语料）⇒ 短测用 12、A/B 按语料扫 |
| 口径陷阱 | 官方 docs 分"当前/历史"两批，读错必误判 |

---

## 八、待续（此后在本工作区继续记录）

> **本节为活动台账**：到 `J:\Bonsai-Official` 工作区后的新工作情况，**按时间顺序追加在此节之下**（沿用本文体例：时间 + 做了什么 + 证据）。

- **未决项（用户裁决，截至 10-06）**：E1 首起档（已收敛=dflash）/ E2 批准 S0 剩余只读自检（**已于 10-06 晚完成，见下**）/ E3 MTP 档路线 / E4 KV dtype 策略 / E5 B01 止血开关是否进启动器。
- **下一步**：批准 S0 → S1 起服（dflash 档）→ S2 就绪 → S3 KVMem 证据 → S4 长文复用 → S5 同口径 A/B。
- **交接**：`【TELE】交接文档-官方线接续-20261006.md`（本工作区根目录）。

### 2026-10-06 晚（工作区转移后·本工作区实录）

**A｜S0 前置自检（只读）跑完**
- S0.1 模型体检上轮已跑（`MODELCHECK_VERDICT=PASS`）；本轮补 S0.2–S0.5，**全程只读零写入**。
- `[EVIDENCE]` S0.2 `verify\自检-引擎与卡匹配.ps1 -Root J:\Bonsai-Official` → `HWCARD_VERDICT=PASS`（`HWCARD_GPU=NVIDIA GeForce RTX 5080`、`cc=12.0 -> engine\ninfer-serve-120a.exe`）。
- S0.3 路径纯 ASCII → `J:\Bonsai-Official` ✅；S0.4 无 `ninfer-serve*` 进程 ✅。
- ⚠️ **S0.5 显存黄灯**：total 16,303 / used 3,997 / **free 11,983 MiB（≈11.7 GiB）**，低于判据 ~13 GiB（占用者并肩 Edge×2 / CodeBuddy / Quark×3 / 豆包 / LM Studio / NVIDIA Overlay）。起服前需腾显存，或备降档（先 `--gdn-state-fp16`，再摘 `--vision`）。
- ⚠️ **订正**：`docs\verify-arch-engine.ps1` **非只读**（硬编码 `E:\infer-build\…` 输出与 `E:\cuda-13.3\bin`、`Start-Process`/`Stop-Process`、起服务发请求）⇒ 属 N2 端到端验收台，**不得放进 S0**；S0.2 用 `verify\自检-引擎与卡匹配.ps1`（纯只读，已读源码确认）。

**B｜建本地 git 库（承用户"建私库"指令）**
- 2026-10-06 晚执行 `git init -b main`（`core.quotepath false` / `core.autocrlf false`）。
- `.gitignore` 只收本线产品本身，排除 `engine/`、`models/`、`official-repo/`、`verify-out/`、`logs/`、`.temp/`、`__pycache__/`、`_safety_backups/`。
- 暂存 **17 文件 / +2,830 行**；**token/私钥模式扫描 CLEAN**。**（订正 10-06 深夜）**：随后加入本文档成 **18 文件 / +2,957 行**，**已 commit `ef3171b`、已配 remote、已 push**（详见 §8-F）。
- 命名决策（用户）：私库名取 **`Bonsai-27B-NInfer-kvmem`**（沿用族名 `Bonsai-27B-NInfer`，`-kvmem` 区分本线血统；**避免含 "Official" 以免冒充官方发布方**）。

**C｜分工变更（用户 2026-10-06 22:37 决定）**
- **TELE = 官方线唯一施工实施方**（改文件 / 编译 / 起服 / 落地）；**CODE = 每轮施工的独立复核 + 建议**（不落地、不代改 TELE 文档）。
- TELE 每轮对 CODE 交付：**施工清单 + commit hash/diff + 端到端读数**。

**D｜CODE 反向复核 TELE 文档/断言 → TELE 独立复核（不回声，逐条取证）**
- **B 成立且更重**：`[EVIDENCE]` 官方 `tests\models\qwen3_5\test_frontend.cpp:2141-2148`（budget=1、喂 `{6}`、OutputLimit ⇒ 断言 `StopToken && Decode`，文案 "terminal token at the thinking boundary did not take priority"）；同文件 `:262` `{"eos_token_id":[6]}`。⇒ **§6 定性升级**：该行为是**官方既定、被单测钉住**，非单纯疏漏；回馈上游须**同改该测试**（已回填 §6）。
- **C1 成立**：`[EVIDENCE]` 仅 `ninfer-4090-windows\src\targets\qwen3_6\impl\frontend\frontend.cpp:1160-1179` 有 Design C 分支（L1164）；`cranebw-ninfer-ternary-bonsai-ada\...\frontend.cpp:1160-1167` **无**（与官方 stop 分支同构）。⇒ **§6 的"自建树已修"须限定为开发树 `ninfer-4090-windows`**。（TELE 一度怀疑 C1、读原文后**撤回**怀疑。）
- **C2 成立**：Design C 已入库、工作区干净；commit `145bccbd`（2026-09-27）仅改 `frontend.cpp +12`。
- **C3 成立（静态推演·未实测）**：`[EVIDENCE]` 自建 `tests\targets\qwen3_6\test_frontend.cpp:1816-1823` 断言 `budget=1 + {6} → StopToken && Decode`，与 Design C 返回 `None + ApplyTargetControl` 互斥 ⇒ 预计 FAIL。定论需重编 `_build_5080` + 跑单测（写操作）。
- **否定性断言载体排查**：全库 `ApplyTargetControl` **实现侧仅 `output_session.cpp:571`**（全库 6 处）。

**E｜未决项（截至 10-06 晚）**
- 基线 commit / 建私库 / 首推：**已完成**（commit `ef3171b`、私库 `paicat1/Bonsai-27B-NInfer-kvmem`、已 push；见 §8-F）。E3 MTP 档路线（建议 A）/ E4 KV dtype（先 `k8v4`）/ E5 B01 止血开关（建议批准）仍待裁决。
- C3 定论（重编 `_build_5080` + 跑单测，写操作，待批）。

**F｜基线 commit 与首推（2026-10-06 深夜）**
- 基线 commit：`ef3171b`（root-commit，`main`，**18 文件 / +2,957 行**），作者 `paicat1`，2026-10-06 23:19:07 +0800。
- 私库：`paicat1/Bonsai-27B-NInfer-kvmem`（**private**）；remote `https://github.com/paicat1/Bonsai-27B-NInfer-kvmem.git`（不含 token）。
- 首推：`main → origin/main`；验收＝`ls-remote` 与本地 HEAD 哈希一致（`ef3171be…`）+ `status -sb` 无 ahead/behind。
- 分支：本次只上 `main`；`engine-main` 缓建到 S6（届时用 `git checkout --orphan` 建孤儿分支，装"我方 fork + 方案C补丁"，保留上游 `LICENSE`/`NOTICE`）。
- **订正 G2（口径）**：上游体量三数验明为**口径差**、非无出处——全仓 **2575 文件 / 88.8 MB**（含 `.git` 28 文件 / 13.4 MB）＝ 源码口径 **2547 文件 / 75.4 MB** ＋ `.git`；`src-tree` 子树 **2463 文件 / 72.3 MB**（我此前回复的"72.3 MB / 2463"即此子树口径）。
- **订正 G4**：commit 正文相对展示草案**少一行**（草案里的"引擎成品 / 模型制品 / 上游 clone 不入库（见 .gitignore）"已删）——删得好（合"连'不入库'的声明本身也不准入库"），但改动了已展示内容未即时说明，此处补记。
- **外部发现（不属本稿，留 CODE 定夺）**：`【CODE】交接文档` L19/L47 将上游目录写作 `official-repo\infer-fusion-kvmem`（**缺 n**），真实目录为 `ninfer-fusion-kvmem`；本稿与 `【TELE】` 各稿路径正确。

**G｜G1 实测闭环 + 启动器 v1 入库 + E1–E5 裁决（2026-10-06 深夜 → 10-07 凌晨）**
- **G1 实测闭环（用户批准）**：自建线 `_build_5080` 重配 `BUILD_TESTING=ON`（`configure_exit=0`）→ 编 `ninfer_qwen3_6_frontend_test`（`BUILD_EXIT=0`）→ 跑测 **`TEST_EXIT=1`**，失败断言 = `tests\targets\qwen3_6\test_frontend.cpp:1821-1823` + `:1825-1826`（"terminal token at the thinking boundary did not take priority" / "terminal thinking boundary left control pending"）。⇒ **CODE 的静态推演成立**：Design C 补丁与既有单测断言互斥（定性＝"补丁未同步单测"）。首跑 `0xC0000135`（缺 FFMPEG 的 avcodec/avformat/avutil/swscale，补 PATH 后正常）。
- **旧项目同步单测（用户"旧项目动手吧"）**：把 `test_frontend.cpp:1821-1826` 两条断言改为 Design C 新行为（`FinishReason::None + ApplyTargetControl`、`pending_control_tokens()` 非空）→ 重编（`BUILD_EXIT=0`）→ 重跑 **`TEST_EXIT=0`（转绿）**。旧项目改动**尚在工作区、未提交**。
- **启动器 v1 入库**：commit `63f237b`（`feat(launcher)`，3 文件 / +584 行）→ push 成功（`362108c..63f237b`；验收远端 `refs/heads/main = 63f237be…`）。
- **E1–E5 最终裁决（用户 2026-10-07）**：E1 首起档=dflash ✅；E2 S0 只读自检 ✅ 已跑；**E3=A**（MTP 档暂不弄；官方两 MTP 档分别指向 `v3-mtponly` / `bonsai2_27b_ternary_ptq1_native_mtp` 两模型件，本机均无 ⇒ **挂账，以后决策**）；**E4=A**（KV dtype 先 `k8v4`，异常试 `rk2v4-e8`；两者均已入启动器）；**E5=加**（B01 止血开关 `--kv-lease-growth` + `--recover-invariant-failures` 入启动器，默认开、可关）。
- **启动器 E5 增量**：新增「止血(B01)」维度（默认开）；自证 `CORE_MATCH_LIST=True`（核心参数仍与官方 bat 逐字一致，两条止血为**有意新增**）。
- **CODE 稿入库**：commit `cfd41f9`（`docs:`，2 文件 / +44−8）→ ~~push 待网络~~ **已补推**（代理恢复后 `63f237b..cfd41f9` 成功；见 §8-H）。

**H｜G11/G12 收尾 + S1 起服 + S2 就绪自测（2026-10-07 凌晨）**
- **G11 订正（启动器等价注释）**：`ninfer_launcher.py` 3 处过时注释（L8 文档串 / L132 默认组合 / L179 函数串）改为“核心逐字等价 + E5 止血两旗（有意新增）”；commit **`bc11f8c`**（`docs(launcher)`，+3/−3）→ push `b1caa7b..bc11f8c`（远端 `refs/heads/main = bc11f8c…`）。复验 `py_compile=0` / `CORE_MATCH_LIST=True` / `KV_COUNT=9` / `hemostat=on`。
- **G12 旧引擎仓推送（用户“只推我们自己的仓”）**：旧引擎仓 `J:\Bonsai\landing\repos\ninfer-4090-windows` 的 `main` 跟踪 **`origin/main` = `github.com/Ambolio/ninfer-4090-windows`（公开上游移植仓）**、`ahead 20` ⇒ **裸 `git push` 会把 20 个本地提交推给公开上游，严禁**；那 20 个全是我们自建线 M0–M6 的引擎改动，只应进私库。**实推（显式远端，未碰 origin）**：`git push paicat1 main:engine-main` → `f90e30c1..ca4196ac`；验收远端 `paicat1/Bonsai-27B-NInfer → refs/heads/engine-main` = `ca4196ac` = 本地 HEAD。
- **S1 起服（用户双击启动器）**：`ninfer-serve-120a` pid **25992**，监听 **`127.0.0.1:8094`**（dflash 档）。
- **S2 就绪自测（TELE 实跑，复用启动器同款代码）**：`GET /v1/models` **200**（id=`qwen3.8-27b`、`context_window=262144`、`status=loaded`、`vision=true`）；`POST /v1/chat/completions`（真发，`max_tokens=64`）**200**、`finish_reason=stop`、**content="1+1 等于 2。"** ⇒ **真在服务，非假健康**。
- **对侧 stale 订正**：CODE 报“旧 repo `_build_5080` 仍 `BUILD_TESTING=ON` 待还原”——实测 **`BUILD_TESTING:BOOL=OFF`**（无需再动）；对侧另报“`.temp\g1_backup` 全盘不存在”——实测**存在**（在 `J:\Bonsai-Official\.temp\g1_backup\`，即**备份放在了己方工作区**，对侧在别处搜未果）。
- **网络观测**：本时段**直连 `github.com:443` 不通 / 代理 `127.0.0.1:7890` 通**（代理由用户控制；关闭时表现为握手失败）。
- **未做**：S3（KVMem 检索证据）与 S4/S5。
- **挂账（属旧项目，用户裁定先不管）**：`docs\reports\【TELE】DEEPSEEK报告核查与接纳评估-20261006.md`（核查**自建线**的第三方 DEEPSEEK 审核报告）——旧项目正按其报告审核；**待旧项目跑通、本项目全部搞好后再评估其价值**。
- **对侧质询的两处澄清（TELE 自查，2026-10-07）**：① **"00:14 说现为 ON / 后来又说 OFF"** —— 两者**都是实测、都对**，是**两个不同时点**：G1 之前原始值=`OFF` → 我为 G1 重配=`**ON**`（00:14 报的"现为 ON"即此）→ 事后被还原=`OFF`（第三方/旧项目侧操作；见②订正）；措辞未点明时点，易被读成矛盾，**我的表述不够严谨**。② **"CODE 早先报过已还原 OFF"** —— 依据是**用户转来的会话记录**（其中确有"② 完成：BUILD_TESTING 已还原 OFF"），但我**无法确认该记录作者就是 CODE**（可能来自别的会话/agent）⇒ **不该直接归到 CODE 名下**，属我的转述不严谨。**【2026-10-07 用户裁定·订正】ON→OFF 的还原 = 第三个智能体在旧项目 + TELE 在旧项目跑修复时所做的操作，与 CODE 无关**；我上文写成"CODE 事后还原"是**误归因**，此处更正。**流程规则（新增，与 CODE 侧对齐）：旧项目的写操作不在本线构建史台账内；归属不明时直接问用户，不要猜。**

**I｜S3 KVMem 检索证据（2026-10-07 凌晨）**
- **前置（日志转存 tee）**：启动器加日志转存（commit `2091b1a`：新增 `serve_tee.py` + `_launch` 走 tee）→ 用户用启动器重启 → `ninfer-serve-120a` pid **27012** + tee 进程（python pid 24516），日志 **`logs\serve_20261007_011441.log`** 已落盘 ✅。
- **探针（TELE 实跑）**：发超窗长题面（`prompt_chars=66,608`）→ **`usage.prompt_tokens=18,423`**（> `NINFER_KV_WINDOW=16384`，触发检索）→ **HTTP 200**、`finish_reason=stop`、content="The quick brown fox jumps"。
- **判据达成（口径已订正）**：日志 `kvmem_score` 总行 **41**、其中 **`SELECT` = 18 行**（我先前报"38 行"是**把 SELECT/KEPT/fallback 全计**的粗口径；按 CODE 口径应为 SELECT **18**）⇒ **S3 通过**（`SELECT` ≥ 1）。
- **⚠️ CODE 亲读日志补正（我漏报了）**：每条 `SELECT` 均 `scored_kept=0 / candidates=0 / recent_kept=0`，**内容打分一块未留、只保 sink 块** ⇒ **本次长文检索实质未生效**（退化为尾部规则）；**S3 的 SELECT 判据只证明"管线活着"，不证明"检索有效"**。⇒ **新挂账 G13**：官方台账明示 B05 触发条件是 query span 超 `MAXQ=256`（与题长无关），那官方 5080 回执"104,991 token 中段针命中"是怎么做到的？**不查清不能开 S4**（否则拿"只有尾部规则"的 KVMem 验长文复用，结论必失真）。
- **⚠️ 本机复现官方 B05**：日志另有 `kvmem_score: query span [3,18416) not usable for chunk [0,1024) (empty overlap or longer than MAXQ=256) -- falling back to the tail rule (QUERY_TAIL)` 与 `kvmem_score: KEPT 0` —— 与官方缺陷台账 **B05**（"低显存池检索退化：query span 超 `MAXQ=256` ⇒ 退化成尾部规则 + `KEPT 0`"）**逐字吻合**。
- 日志文件在 `logs/`（gitignored），故此处仅记关键行；`[EVIDENCE]` = 上述 `kvmem_score` 行原文。

**J｜G13 调研：B05 触发真因与规避路径（2026-10-07 凌晨，只读读码）**
- **B05 触发条件（源码级）**：`kvmem_score.h:292-323` —— D-12 的"绝对 query span（最后一轮 user）与本 chunk 求交"：交集**为空**、或**长于 `MAXQ=256`** ⇒ 回落尾窗规则（`QUERY_TAIL`，默认 64）。源码注释明写根因：**题面把长正文与问句放在同一条 user 消息里时，span = 整条消息（> MAXQ）** ⇒"我们没能定位到一个问句"⇒ 回落（自陈为"honest failure mode"）。本机实测日志 `query span [3,18416)` 正是此形。
- **官方 5080 回执为何没踩**（`实测回执与反馈.md:13`）：那台跑的是 **`KV 262,144 tokens`（rk2v4-e8，pages 4096/4096，runtime 4.90 GiB）** —— **池 = 整个上下文**，104,991 token 题面**全量常驻**，**根本没走检索路径** ⇒ 回执的"中段针命中"**不构成"低池检索有效"的证据**。
- **规避路径（候选，待 S4 探针验证）**：① **把长正文与问句分成两条 user 消息**（问句 span ≤ 256 ⇒ D-12 生效 ⇒ 期望 `scored_kept>0`）；② 池开大至 ≥ 题面（= 不触发检索，但那就不算检索验证）；③ 调 `NINFER_TERNARY_KVMEM_SCORE_*`（`QUERY_TAIL`/`MAXQ`/`SPAN_OFF`）——但源码自陈 `TAIL=256` 会令 turn2 掉到 2/6，**勿乱调**。官方根治方案 = 附二 §10 **ShadowKV**（逐 token 打分 + query 维并集，Apache-2.0）+ 上游 `span_accumulate`(#343)。
- **S4 探针设计（建议）**：形态改用"**正文一段 user + 独立问句一段 user**"；判据从"`SELECT` ≥1"升级为"**`scored_kept>0`**（内容打分真留块）"；否则拿"只有尾部规则"的检索去验长文复用，结论必然失真。**待用户裁决后开跑**。

**K｜S4 探针：长文检索三层判据全过（2026-10-07 凌晨，用户批准 G14）**
- **探针形态（按 G14 定案）**：正文（埋真针 `ARK-SECRET-CODE-5731` 于 ~55%）+ **问句独立成第二条 user**；`prompt_tokens=17,220`（> 窗口 16,384）。
- **判据① 针被答出**：content = **`ARK-SECRET-CODE-5731`**（`finish_reason=stop`）✅
- **判据② kept 覆盖针位**：末条 SELECT `kept_range=[0,287]`（全保留；针估块 ~147 在其中）✅
- **判据③ `scored_kept>0`**：`scored_kept=224 candidates=224 sum_score=24.000` ✅
- **机理确认（对比 S3）**：末条 SELECT 明写 **`span_mode=abs`、`query_tokens=24`、`span_abs=[17189,17213)`** ⇒ **问句独立成条 ⇒ query span = 24 ≤ `MAXQ=256` ⇒ D-12 生效、打分真跑**；而 S3（正文+问句同条）span=18,416 > 256 ⇒ 回落、`scored_kept=0`。⇒ **B05 可经"问句独立成回合"规避**。
- **诚实局限**：本次题面（17,220）< 池（17,920）⇒ `kept=288/288`（**无淘汰**）⇒ 本发只证"打分生效 + 针可检索"，**未证"池压下的淘汰式检索"**；若要压测，需再加一发"题面 > 池"的紧探针。
- 全程**未调任何 `NINFER_TERNARY_KVMEM_SCORE_*`**（遵 CODE 警告）。
- **对侧独立复现（2026-10-07）**：CODE 用**它自己的针**（`CODE-NEEDLE-8842`）+ 独立请求复现三层判据（其 `span_abs=[17024,17039)`、`query_tokens=15`、`scored_kept=224`）⇒ **机理双确认（两根不同的针）** → **G14 闭环**。
- **对侧 P3（query_tokens）复读结论（TELE 反向复核）**：同一请求的 SELECT 行里 `query_tokens` **有两种取值**——尾窗规则块=**64**；D-12 span 生效块=**我探针 24 / CODE 探针 15**（= 各自 `span_abs` 长度）。我引的那条（L163）**确为 `query_tokens=24`**，**读数无误**；对侧 P3 疑为引了"尾窗块"那一行 ⇒ **此 P3 不成立**。
- **元数据滞后未复现**：对侧记"J 盘 size/mtime 元数据缓存滞后"；本轮实测 `meta.Length == realfile.size == 100,356`（一致）。仍遵"读日志以实读内容为准"。

---

*【TELE 稿】本文档只由 TELE 维护（CODE 的过程记录见其自维护文档）。本文为过程实录，不是落地批准；所有写操作执行前须用户逐次批准。*
