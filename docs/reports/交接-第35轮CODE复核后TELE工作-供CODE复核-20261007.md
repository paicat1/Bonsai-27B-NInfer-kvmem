# 【TELE 稿】S6 收尾交接：Design C 探针与恢复工作（供 CODE 复核）

> 日期：2026-10-07
> 维护：TeleAgent（TELE）｜标识：【TELE 稿】｜性质：过程实录 + 交接清单（非批准）
> 复核对象：请 CODE 独立复核本报告所有 [EVIDENCE] 与结论，默认假设有错，逐条取证。
> 边界：本报告只由 TELE 维护；不代改 CODE 文档；验证 ≠ 修复授权。

---

## 〇、本报告范围（相对上次 CODE 复核的增量）

上次 CODE 复核点 = **构建史 §Z / CODE 第 35 轮**（Design C 移植五关全过、engine-main 同步推送）。之后 TELE 完成：
1. **官方 v3 模型误删事故 → 恢复 + 立 T-PROTECT-ASSET 铁律**（构建史 §A1）
2. **对照启动器**（Design C serve 可启动）
3. **S6 终局双 exe 探针实测**（含方法性纠正）

三块均以证据落笔，供 CODE 复核。

---

## 二、事故与恢复（构建史 §A1，commit d4f42a3）

### 2.1 事故
- 官方 v3 模型 `Ternary-Bonsai-2-27B-ninfer-v3.ninfer`（9,520,051,456 B）在 `models\` 丢失。
- 根因（TELE 自认）：`models\` 被 .gitignore 排除（无 git 备份）+ 全程未 T-BACKUP + 同日多次 `Remove-Item -Recurse -Force` 高危删除未保护 models。
- **已立 T-PROTECT-ASSET 铁律**（USER.md + 构建史 §A1，T0 级）。

### 2.2 恢复（已闭环）
- **SHA256 全量校验通过**（**机器落盘，非手抄**）：
  `[EVIDENCE]` `Get-FileHash models\Ternary-Bonsai-2-27B-ninfer-v3.ninfer -Algorithm SHA256` = `CDC4810B0FF17C40D0F62CF214B6E0BCD08346E9EB05CA53371507037793C14A`（64 位），与构建史记录全 64 位逐字匹配。
  ⚠️ 本报告首稿哈希为**手抄残缺串**（60 位、`0B→B0` 错位、中段缺 4 字符）——已被 CODE 第 36 轮复核抓出。教训：**哈希必须机器落盘，禁止手抄**。
- ✅ 模型已放回 `models\`（9,079.03 MB），根目录残留已清空。
- ✅ `start-pq2-dflash.bat` 命中（L18 指向 `models\...v3.ninfer`，模型就位）。
- ⚠️ 另两启动器指向 `v3-mtponly` / `ptq1_native_mtp` 版，本次未恢复（仅恢复全量 v3）。

## 3. 对照启动器（Design-C serve 可跑）

- 生成 `start-pq2-dflash-designc.bat`：端口 **8095**，引擎指向自编 `.temp\build-120a\apps\ninfer-serve.exe`（Design C，13:00:55），模型与官方同款。
- **启动曾两次失败 + 根因纠正**（诚实记录）：
  - 初版含中文注释 → cmd ANSI 乱码 → **已改纯 ASCII**。
  - 误判 "LF 行尾导致空输出" → 实测官方源本身也是 LF 且能跑 → **纠正：LF 非根因**。
  - **真根因**：自编 serve 缺 `cudart64_13.dll`（动态链接 CUDA 运行时）。已从官方分发包 `J:\分发\正式版50系\infer-engine-sm120a-20261002\engine\` 复制到 `apps\`（0.525 MB）。`[EVIDENCE]` serve 启动日志 `engine-v0.11.0-kvmem-20261003-7-g41beb3b` + weights 8.43 GiB + listening 8095 成功。

## 4. S6 双探针实测 + 方法纠正

### 4.1 探针方法纠正（关键，CODE 复核确认 ✅）
- **初始错误**：用 `max_tokens` 阶梯制造 length 截断，得"官方空正文 vs 自编也空" → 误判 Design C 无效。
- **纠正**：Design C 触发条件 = `stop_token && in_reasoning && budget`（`output_session.cpp` L553-571），**治"思考区 stop"非"max_tokens length 截断"**。length 截断空正文是另一路径（L564 limit 分支），非 Design C 修复目标。
  `[EVIDENCE] src-tree/fusion-engine-src/src/models/qwen3_5/frontend/output_session.cpp:553-571`：`if (stop_token) { if(in_reasoning && budget){...ApplyTargetControl} }`。
- **诚实追加**：我第 36 轮前对 CODE 的规格原话"限 max_tokens 使 stop 落在思考区"同型不精确——max_tokens 走 limit 路径而非 stop 分支。CODE 已自纠，我采纳。

### 4.2 自编 Design C（8095）探针实测（**撤回 ✅ 表结论，CODE 复核定**）
⚠️ 下表**不构成 Design C 行为证据**，只证明"serve 能出正文"。CODE 第 36 轮判定：`finish=length` 全 6 行 ⇒ 全部走 max_tokens 路径，**Design C 的 stop 分支整轮探针一次都没触发**；且 budget=8 若生效 th 应为 8，实际 th=166 恒定 ⇒ **`thinking_budget` 在自编 serve 上同样未生效**。

| budget | finish | th | ct | 判定 |
|---|---|---|---|---|
| 8 | length | 166 | 7399 | 只证 serve 能出正文，非 Design C 证据 |
| 16 | length | 166 | 7399 | 同上 |
| 32 | length | 166 | 7399 | 同上 |
| 64 | length | 166 | 7399 | 同上 |
| 128 | length | 166 | 7399 | 同上 |
| 无预算 | length | 166 | 7399 | 同上 |

- **Design C 接线的真证明** = 单测绿（第 35 轮 `ninfer_qwen3_5_frontend_test` 退出码 0）+ fork diff（第 32 轮）——**早已足够，不靠探针**。
- **本表唯一有效结论**：自编 serve 能正常输出完整正文（th 166 / ct 7399）。

### 4.3 官方 exe（8094）对照 —— **路径混淆已自纠**
- **上一稿错误**：把官方 mt=64 的 **length 截断空正文**当"官方 bug 对照"——这与 §4.1 刚纠正的"length 截断 ≠ Design C 范围"自相矛盾（CODE 复核第 36 轮抓出）。
- **更正**：官方 exe 在思考截断（无预算、小 max_tokens）时空正文，**属 length/limit 路径的既有行为，与 Design C（stop 路径）无关**。
- **实测补充**：官方 `thinking_budget` 参数不生效（budget 0/8/2048 三档 th 恒 65）。
  `[EVIDENCE]` 官方 8094：budget=0→th65/ct65、budget=8→th65/ct65、budget=2048→th65/ct65。
- **不得用本探针判定 Design C**；Design C 的确定性证明 = 单测 + fork diff。

## 5. 四问裁决（采纳 CODE 第 36 轮） + 后续行动

| 项 | 裁决 |
|---|---|
| Q1 补丁接线 | 接线证明**不靠探针**——单测绿 + fork diff 已足；**真正要查的是 budget 为何无效**（参数名/字段/协议），探针需交完整请求 JSON + serve argv |
| Q2 方法理解 | ✅ 正确（length 截断 ≠ stop 路径） |
| Q3 无法同参对照 | **不影响 S6 结论**——确定性证明=单测（已完成）；负控=官方 BUG（第 3 轮实证）；e2e=实流 soak（自建线 78 请求先例）。放弃"同参 A/B"框架 |
| Q4 d4f42a3 | ✅ 合规（仅构建史 +9 行，无模型二进制） |

**S6 验收口径（采纳）**：**单测绿 + 实流 soak**，不再用探针表格作为 Design C 证据。

### 6. 追加：`thinking_budget` 无效根因（源码级，2026-10-07 查出）
**根因**：OpenAI chat 协议解析层 `src/serve/openai_chat_request.cpp` **从未解析 `thinking_budget` 字段**（只解析 `enable_thinking`/`preserve_thinking`/`reasoning_effort`/`post_thinking`，grep 全文无 `thinking_budget` 赋值）。
- 全仓唯一把 JSON 字段写入 `request.thinking_budget` 的位置 = **Anthropic 协议** `anthropic_messages_request.cpp:883`（读 Anthropic 的 `thinking.budget_tokens`）。
- 我发的 OpenAI 请求带 `thinking_budget` → 字段被静默丢弃 → `request.thinking_budget` 恒空 → 走 `server.default_thinking_budget`（启动器未设 = 空）→ `options.execution.thinking.budget` 恒空 → **Design C 的 `budget` 条件永不成立**。
- **正确设 budget 的路径**（OpenAI 协议下）：
  1. **启动器 argv** `--default-thinking-budget <N>`（serve_options.cpp:535 全局默认），或
  2. **Anthropic 协议**请求带 `thinking.budget_tokens`。
- **待办**：如需在 OpenAI 协议实测 Design C，需给启动器加 `--default-thinking-budget`，重编/重启自编 serve 后再探针。

---

*【TELE 稿】本文档只由 TELE 维护。验证 ≠ 修复授权；落地与否由用户裁决。*