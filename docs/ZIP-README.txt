# zip 交付清单 · 2026-10-02（这一页随 zip 一起发）

> **这批包不含模型**（权重走独立模型包 `modelpack-*`）。每个包里的 `MODELS.txt` 写着：下哪个文件、
> 多少字节、sha256、放进 `models\` 哪里、怎么校验；教程 `教程-KVMem与短测-给agent与使用者.md` 的 **§0.0** 是四步前置。

## 一、五个 zip（全部做过"解压回验"：解出来按包内 `SHA256SUMS.txt` 逐文件重算 ⇒ `bad=0 missing=0`）

| zip 文件 | 解压后大小 | zip 大小 | sha256 |
|---|---|---|---|
| `betakit-pq2-v2-20261002.zip` | 4.75 GiB / 43 文件 | 3.24 GiB | `32D4C68A47159AA24E26585DB80E71A3FC91997ECA537A6DC7F0982209AEBCB9` |
| `betakit-ptq1-v2-20261002.zip` | 4.75 GiB / 42 文件 | 3.24 GiB | `BBD5CAE10A27280DA14D39D77F8FC599BE28D2A7E9DE80AD2B3CB3C160D67688` |
| `infer-engine-sm89-20261002.zip` | 2.03 GiB / 19 文件 | 1.41 GiB | `5CAE20F5081462BC9D155DED158254960A3225D9CEEED90DFB42300D034AC2E5` |
| `infer-engine-sm86-20261002.zip` | 2.09 GiB / 19 文件 | 1.43 GiB | `BC02384D4CFCF864DA31A1EF4A8A7D8097B7C04303D40A69E8A300DFF981BF7B` |
| `infer-engine-sm120a-20261002.zip` | 1.87 GiB / 19 文件 | 1.24 GiB | `FDA1D95B30BD6AEAC8A086CB770DEEFDF8601072A018BE87CA3C4BDE4504BA11` |

## 二、每个包里是什么

| 包 | 给谁 | 内容 |
|---|---|---|
| `betakit-pq2-v2-20261002` | **主力包**（配 `modelpack-pq2-v2-20261002`） | 三卡引擎 + 9 DLL + 4 个启动器（PQ2-mtponly 8091 / PQ2-dflash 8094 / GSQ 8092 / Swift 8093）+ 自检脚本 + `docs\` + 教程 |
| `betakit-ptq1-v2-20261002` | PTQ1_0 档（配 `modelpack-ptq1-20261002`） | 三卡引擎 + 9 DLL + `start-ptq1-mtp.bat`（8095）+ 自检脚本 + 参考文档 + 教程 |
| `infer-engine-sm89 / sm86 / sm120a` | 只要引擎的人（各自一张卡） | 单架构引擎 + 9 DLL + 三个档位启动器 + 清单校验器 + 教程（**不含 `docs\`**） |

## 三、两条交付提醒（请一并转给接收方）

1. **解压用 7-Zip / WinRAR / `tar -xf`**。Windows 资源管理器**自带**的解压对中文文件名会乱码
   （`教程-…md`、`自检-….ps1` 会变成乱码名）—— 那是它的老毛病，不是包坏了。
   解压路径**必须全 ASCII**（原生 exe 读不了中文路径）。
2. **先放模型，再起服务**：`models\` 默认是空的（设计如此）。放好后用 `start-*.bat` 起，
   就绪判据 `curl.exe -s -o NUL -w "%{http_code}" http://127.0.0.1:<端口>/v1/models` ⇒ `200`。

## 四、这批包的验收读数（构建机 RTX 4080 SUPER / 32 GB / sm_89，池 17,920，数数字语料 1000 进 / 1000 出）

| 档位 | 启动器 | TTFT | 预填 | 解码 | 1000 token 总耗时 |
|---|---|---|---|---|---|
| PQ2-mtponly | `start-pq2.bat` | 344 ms | 3.30k tok/s | 237.9 tok/s（mtp 接受 88.1%） | 4.6 s |
| PTQ1_0 | `start-ptq1-mtp.bat` | 565 ms | 2.01k tok/s | 196.8 tok/s | 5.7 s |
| **PQ2-dflash（`--draft-tokens 12`）** | `start-pq2-dflash.bat` | 396 ms | 2.87k tok/s | **571.9 tok/s**（dflash2 接受 91.5%） | **2.2 s** |

上面每一档都在**全新 ASCII 路径**上从零走了一遍（复制 → 放模型 → 校验哈希 → 体检 → 起服务 →
一条测速请求 → 两行 KVMem 证据 → 包自检 `PASS`），不是"在我们机器上能用"。

## 五、模型包（不在这些 zip 里）

| 模型包目录 | 内容 | 体量 |
|---|---|---|
| `E:\ship-next\modelpack-pq2-v2-20261002` | `Ternary-Bonsai-2-27B-ninfer-v3.ninfer`（9.52 GB）+ `…-v3-mtponly.ninfer`（7.65 GB）+ `MODELS.txt` + `SHA256SUMS.txt` | 17.2 GiB |
| `E:\ship-next\modelpack-ptq1-20261002` | `bonsai2_27b_ternary_ptq1_native_mtp.ninfer`（6.39 GB）+ `MODELS.txt` + `SHA256SUMS.txt` | 6.4 GiB |

权重压不动（本来就压不动），所以没有做成 zip —— 要压说一声。
