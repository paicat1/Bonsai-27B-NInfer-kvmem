# NInfer engine pack -- **sm_120a** -- 20261002

> **★ 先读这个：`教程-KVMem与短测-给agent与使用者.md`**（本包自带一份副本）。
> **本包不含模型**：权重是**独立分发**的模型包（`modelpack-*`）；文件名 / 字节 / sha256 / 放哪里，见模型包内的 `MODELS.txt`。
> It is a hard instruction set for the DEPLOYING AGENT, not background reading:
> 1. after deployment do a **15-minute short test only** (start -> two KVMem log lines -> **one counting-number
>    speed test, 1000 tokens in / 1000 tokens out** -> report three numbers). Do NOT run an exhaustive matrix:
>    a long test is what makes a working deployment look like a failed one;
> 2. **escalate to the uploader** for: thinking loops, repeated mid-truncation, or silent wrong answers at a
>    small device pool -- the uploader has complete solutions for all three;
> 3. **if any .ps1 in this pack refuses to run, that does not block deployment** -- the tutorial's section 0.5
>    is a pure-instruction path (no scripts) that completes the same acceptance;
> 4. **using a dflash2 model? the draft window is --draft-tokens 12** (the launcher in this pack already
>    ships 12). Measured on a counting corpus, 1000 tokens out: 278 -> 600 tok/s, 4.4 s -> 2.4 s.

> One binary per architecture. This pack carries **only** the sm_120a engine: an sm_89 cubin carries
> no PTX for sm_120 and vice versa, so the wrong one does not fall back -- it dies with no usable
> kernel image. Packs for other cards are separate downloads and share no DLL with this one.

## 1. What is in here

| path | what |
|---|---|
| `engine\ninfer-serve-120a.exe` | the engine (see the identity table below) |
| `engine\*.dll` | its runtime (CUDA + FFmpeg + curl) -- the engine loads these from its OWN directory |
| `engine\pick-engine.bat` | the arch selector the tier launchers call (kept for kit compatibility) |
| `start-ptq1-mtp.bat` | launcher: PTQ1_0 tier (port 8095, `--spec mtp`) |
| `start-pq2.bat` | launcher: PQ2 MTP-only tier (port 8091) -- the small-card tier |
| `start-pq2-dflash.bat` | launcher: PQ2 full tier (port 8094, `--spec dflash2 --lm-head-draft --vision`) |
| `verify-arch-engine.ps1` | acceptance for THIS card: does it start, does the over-pool warning fire, does the MID-prompt answer survive |
| `verify-kit-manifest.ps1` | checks `SHA256SUMS.txt` against the pack, byte-exact |
| `SHA256SUMS.txt` | the manifest |

Models are NOT in this pack -- weights ship as SEPARATE model packs (6-14 GiB each). Put the
launcher, or `set MODEL=D:\path\to\model.ninfer` before running a launcher.

## 2. Engine identity (verify before you trust any reading)

| | |
|---|---|
| sha256 | `42CD073572643C9720E1AB54AD056D19BA44A33578DDDF53BBD010295DE189FD` |
| bytes | 1343609856 |
| built | 10/02/2026 21:47:04 |

`powershell -File verify-kit-manifest.ps1 -Kit .` checks every file above against the manifest.

## 3. What is fixed in THIS build (2026-10-02)

1. **Small device pools no longer retrieve the wrong pages.** With the device pool far smaller than
   the prompt, the retrieval query window is now the QUESTION (64 rows), not the last 256 rows of the
   chunk. Measured on sm_89: device pool 4,032 tokens (63 pages) with a 42k-token prompt
   (10.6x over-pool): turn1 6/6 and turn2 6/6; the wide-window control on the SAME binary loses turn2
   (2/6). Where the last user turn is short, its exact token span is used instead.
2. **The scorer is ON by default** whenever the ring is configured -- no `NINFER_TERNARY_KVMEM*`
   variable has to be set, and the launchers deliberately do not set one. Before this, the shipped
   shape ran the LEXICAL ranking and answered a filler number instead of the needle.
3. **Order of magnitude**: at 23.5x over-pool (94.7k-token prompt, 63-page device pool, 16 GiB host
   pool) both needles were retrieved, 3/3 turns, zero silent errors.
4. **Connection layer**: Windows now gets the TCP keep-alive the Linux build always had
   (`SO_KEEPALIVE` + `SIO_KEEPALIVE_VALS`, 10 s idle / 3 s probes) and the HTTP server's keep-alive
   window is 120 s instead of cpp-httplib's 5 s default, with 300 s read/write timeouts.

## 4. Self-certification (one command, ~1 minute)

    powershell -ExecutionPolicy Bypass -File .\verify-arch-engine.ps1 -Exe .\engine\ninfer-serve-120a.exe -Tag my-sm_120a

Expected on a matching card: the engine starts, the over-pool arm prints a warning AND answers the
MID-prompt needle (a mid-prompt loss is a FAIL there), the fits arm prints no warning. `finish_reason
= length` or an empty answer is INCONCLUSIVE, never a missed needle -- turn thinking off or raise
`max_tokens` before reading any needle number.

The reading that proves the content ranking is actually running (not the lexical fallback) is one line
in the engine's stderr:

    kvmem_score: SELECT label=text_prefill_chunk n_blocks=... query_tokens=64 span_mode=...

If there is no `SELECT` line at all, the scorer did not run -- that is the failure the default flip
above exists to prevent. `NINFER_TERNARY_KVMEM=0` (the negative control) makes the startup line read
`the content scorer was EXPLICITLY DISABLED`.

## 5. NOT verified (do not read this page as more than it says)

| # | not verified | why |
|---|---|---|
| 1 | that this exact binary runs on the matching card | it is the same source as the sm_89 payload, compiled for sm_120a, and no sm_120a card exists on the build box -- run section 4 on your card |
| 2 | device pools SMALLER than 4,032 tokens | 4,032 (63 pages) is the smallest measured; below it the per-round restore budget (pool x 50%) gets thin and nothing has been measured |
| 3 | a 2-minute-plus cold prefill can still be closed at the transport layer | root cause NOT localized (engine stays alive and keeps prefilling, no error line). Section 3.4 is a mitigation aimed at exactly that class, not a proven fix |
| 4 | dtypes other than k8v4 at a small pool | the mask wiring is verified per dtype; the low-pool acceptance is not |
| 5 | long-answer speculation depth | `--draft-tokens` is left at the shipped 4. A deeper draft is much faster on predictable text (measured 600 vs 278 tok/s decoding a counting sequence) and SLOWER on unpredictable text; `--adaptive-mtp` (`--spec mtp` only) is the principled middle and is NOT tested |

## 6. Red lines this pack respects

Nothing under `E:\betakit-lite`, `E:\betakit-ptq1-v1` or `E:\ship` was written while building it;
those stay frozen. The tier argv in the launchers is copied verbatim from those kits (read-only) so a
tester sees the same shape, minus the env lines that the engine now defaults correctly.
