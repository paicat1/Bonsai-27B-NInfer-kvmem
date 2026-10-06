# -*- coding: utf-8 -*-
"""NInfer 官方线启动器 —— Bonsai-27B-NInfer-kvmem（第一版）

用途：点选参数 → 实时预览启动命令 → 起服（可见窗口，关窗=停服）→ 就绪自测。
零外部依赖（仅 Python 自带 tkinter / urllib / json / subprocess）。

对照施工方案：
  · S1 起服：首起档 = dflash 档（默认组合即官方 start-pq2-dflash.bat 的等价 argv）
  · S2 就绪判据：判活必须真发请求（/v1/models 200 ≠ 能服务）
  · 参数铁律：KVMem 五环境变量自动注入；--max-shared-prefixes 0 / --max-concurrency 1 强制

版本：v1（覆盖起服 + 自检/就绪自测）。后续版本继续补齐全部参数维度（见文件尾 TODO）。
"""

import json
import os
import queue
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import urllib.request
import urllib.error

# ---------------------------------------------------------------
# 常量：路径与基础参数
# ---------------------------------------------------------------
ROOT        = os.path.dirname(os.path.abspath(__file__))          # 项目根（便携：不写死盘符）
ENGINE      = os.path.join(ROOT, "engine", "ninfer-serve-120a.exe")
ENGINE_DIR  = os.path.dirname(ENGINE)
MODEL       = os.path.join(ROOT, "models", "Ternary-Bonsai-2-27B-ninfer-v3.ninfer")
CONFIG_FILE = os.path.join(ROOT, "ninfer_launcher_profiles.json")
PORT_DEFAULT = 8094

# 池 token 数（= config 里的 --kv-capacity）。客户端请求的 max_tokens 必须 ≤ 它，
# 否则 worker 崩且不自愈（官方 docs/04 L1 表；--default-max-tokens 是服务端默认上限）。
KV_POOL_TOKENS = 17920

# KVMem 五开关：缺一 = 起得来但静默答错（缓存命中率高、中段答错、零报错）。GUI 内固定注入。
KV_ENV = {
    "NINFER_KV_WINDOW":          "16384",
    "NINFER_KV_RETRIEVE":        "8192",
    "NINFER_KV_RING":            "1",
    "NINFER_HOST_PAGEABLE":      "1",
    "NINFER_KV_REUSE_HOSTBACKED": "1",
}

# ---------------------------------------------------------------
# 维度定义：key -> {value: (显示名, 附加参数列表)}
# ---------------------------------------------------------------
SPEC_OPTIONS = {
    "dflash2": ("DFlash2 · draft 12（首起档）", ["--spec", "dflash2", "--draft-tokens", "12", "--lm-head-draft"]),
    "mtp":     ("MTP · draft 4（备用档）",      ["--spec", "mtp", "--draft-tokens", "4", "--lm-head-draft"]),
    "none":    ("无投机（裸档 · 慢）",           []),
}
KV_OPTIONS = {
    "k8v4":     ("k8v4（发货默认）", ["--kv-dtype", "k8v4"]),
    "rk8v4":    ("rk8v4",           ["--kv-dtype", "rk8v4"]),
    "rk4v4":    ("rk4v4",           ["--kv-dtype", "rk4v4"]),
    "rk4v4-e8": ("rk4v4-e8",        ["--kv-dtype", "rk4v4-e8"]),
    "rk2v4-e8": ("rk2v4-e8（5080 回执用）", ["--kv-dtype", "rk2v4-e8"]),
    "nvfp4":    ("nvfp4",           ["--kv-dtype", "nvfp4"]),
    "fp8":      ("fp8",             ["--kv-dtype", "fp8"]),
    "int8":     ("int8",            ["--kv-dtype", "int8"]),
    "bf16":     ("bf16",            ["--kv-dtype", "bf16"]),
}
CTX_OPTIONS = {
    "32k":  ("32K",             ["--max-context", "32768"]),
    "128k": ("128K",            ["--max-context", "131072"]),
    "224k": ("224K",            ["--max-context", "229376"]),
    "256k": ("256K（发货默认）",  ["--max-context", "262144"]),
}
KVCAP_OPTIONS = {
    "17920": ("17920（发货默认）",         ["--kv-capacity", "17920"]),
    "auto":  ("auto（按剩余显存最大化）",   ["--kv-capacity", "auto"]),
    "32768": ("32768",                    ["--kv-capacity", "32768"]),
    "65536": ("65536",                    ["--kv-capacity", "65536"]),
}
HOSTKV_OPTIONS = {
    "16384": ("16384（发货默认）", ["--host-kv-mib", "16384"]),
    "8192":  ("8192",            ["--host-kv-mib", "8192"]),
    "32768": ("32768",           ["--host-kv-mib", "32768"]),
}
PREFILL_OPTIONS = {
    "1024": ("1024（发货默认）", ["--prefill-chunk", "1024"]),
    "512":  ("512",            ["--prefill-chunk", "512"]),
    "2048": ("2048",           ["--prefill-chunk", "2048"]),
}
THINK_OPTIONS = {
    "none":   ("none（发货默认 · 关思考）", ["--default-reasoning-effort", "none"]),
    "low":    ("low",                      ["--default-reasoning-effort", "low"]),
    "medium": ("medium",                   ["--default-reasoning-effort", "medium"]),
    "high":   ("high",                     ["--default-reasoning-effort", "high"]),
    "off":    ("--no-thinking（强制关）",    ["--no-thinking"]),
}
MAXOUT_OPTIONS = {
    "32768": ("32768（发货默认）", ["--default-max-tokens", "32768"]),
    "16384": ("16384",           ["--default-max-tokens", "16384"]),
    "8192":  ("8192",            ["--default-max-tokens", "8192"]),
    "1024":  ("1024",            ["--default-max-tokens", "1024"]),
}
VISION_OPTIONS = {
    "on":  ("开（发货默认）", ["--vision"]),
    "off": ("关（省显存）",   []),
}
SAMPLE_OPTIONS = {
    "shipped":  ("发货(0.7/0.9/20, presence0)", ["--presence-penalty", "0", "--temperature", "0.7", "--top-p", "0.9", "--top-k", "20"]),
    "thinking": ("思考档(1.0/0.95/20)",          ["--presence-penalty", "0", "--temperature", "1.0", "--top-p", "0.95", "--top-k", "20"]),
    "greedy":   ("贪心(greedy)",                 ["--greedy"]),
}

DIMENSIONS = [
    ("spec",   "档位 / 投机解码", SPEC_OPTIONS),
    ("kv",     "KV 类型",         KV_OPTIONS),
    ("ctx",    "上下文",          CTX_OPTIONS),
    ("kvcap",  "KV 容量",         KVCAP_OPTIONS),
    ("hostkv", "Host KV (MiB)",   HOSTKV_OPTIONS),
    ("prefill","prefill 块",      PREFILL_OPTIONS),
    ("think",  "思考",            THINK_OPTIONS),
    ("maxout", "输出上限",        MAXOUT_OPTIONS),
    ("vision", "视觉",            VISION_OPTIONS),
    ("sample", "采样",            SAMPLE_OPTIONS),
]

# 默认组合 = 官方 start-pq2-dflash.bat 的等价参数
DEFAULTS = {
    "spec": "dflash2", "kv": "k8v4", "ctx": "256k", "kvcap": "17920", "hostkv": "16384",
    "prefill": "1024", "think": "none", "maxout": "32768", "vision": "on", "sample": "shipped",
}

DIM_TIPS = {
    "spec":   "投机解码（只加速解码）。dflash2 为首起档（官方工具对本机 16G 首选）；MTP 为备用档（省显存）。改档需重启 serve。",
    "kv":     "KV 缓存精度。发货默认 k8v4；官方 5080 回执另用 rk* 系列。可用性随架构变，异常时换一档试。",
    "ctx":    "上下文长度（--max-context）。发货默认 256K。",
    "kvcap":  "KV 池容量（--kv-capacity）。default 17920 = 池 token 数；auto 按剩余显存最大化。",
    "hostkv": "Host 侧 KV 预算（MiB，--host-kv-mib）。发货默认 16384。",
    "prefill":"文本 prefill 分块（--prefill-chunk，128 的倍数）。发货默认 1024。",
    "think":  "思考模式。发货默认 none（关思考）。启用思考后注意 §4.2 的“思考完空正文”已知问题。",
    "maxout": "服务端默认输出上限（--default-max-tokens）。⚠ 客户端请求的 max_tokens 必须 ≤ 池 token 数(17920)，否则 worker 崩。",
    "vision": "视觉（多模态）。发货默认开；显存紧时关掉省一大块。",
    "sample": "采样预设。默认 = 官方发货值 0.7/0.9/20、presence 0。",
}

# 命名组合预置（首次运行若无配置文件则落盘）
PRESET_PROFILES = {
    "起服-dflash档": dict(DEFAULTS),
    "备用-MTP档":    dict(DEFAULTS, spec="mtp"),
    "省显存-无视觉": dict(DEFAULTS, vision="off"),
}


# ---------------------------------------------------------------
# 校验 / 命令构造
# ---------------------------------------------------------------
def validate(combo):
    """返回告警列表（空 = 无告警）。"""
    warns = []
    if combo.get("maxout") and int(combo["maxout"]) > KV_POOL_TOKENS:
        warns.append(f"输出上限({combo['maxout']}) > 池 token 数({KV_POOL_TOKENS})——发货默认如此；"
                     f"客户端请求的 max_tokens 请务必 ≤ {KV_POOL_TOKENS}")
    if not os.path.exists(ENGINE):
        warns.append(f"未找到引擎：{ENGINE}")
    if not os.path.exists(MODEL):
        warns.append(f"未找到模型：{MODEL}")
    if any(ord(c) > 127 for c in ROOT):
        warns.append("项目路径含非 ASCII 字符——引擎会以 invalid UTF-8 byte 启动即挂")
    return warns


def build_command(combo, port=PORT_DEFAULT):
    """返回 (exe, argv)。argv 为引擎参数（不含 exe）；组合与官方 start-pq2-dflash.bat 等价。"""
    argv = [MODEL, "--host", "127.0.0.1", "--port", str(port), "--model-id", "qwen3.8-27b"]
    argv += CTX_OPTIONS[combo["ctx"]][1]
    argv += KVCAP_OPTIONS[combo["kvcap"]][1]
    argv += KV_OPTIONS[combo["kv"]][1]
    argv += HOSTKV_OPTIONS[combo["hostkv"]][1]
    argv += PREFILL_OPTIONS[combo["prefill"]][1]
    argv += SPEC_OPTIONS[combo["spec"]][1]
    argv += VISION_OPTIONS[combo["vision"]][1]
    argv += MAXOUT_OPTIONS[combo["maxout"]][1]
    argv += THINK_OPTIONS[combo["think"]][1]
    argv += ["--max-concurrency", "1", "--max-shared-prefixes", "0"]   # 铁律：ring 单路 / 防打砖
    argv += SAMPLE_OPTIONS[combo["sample"]][1]
    return ENGINE, argv


def env_for_launch():
    env = dict(os.environ)
    env.update(KV_ENV)
    env["PATH"] = ENGINE_DIR + os.pathsep + env.get("PATH", "")
    return env


# ---------------------------------------------------------------
# 组合持久化
# ---------------------------------------------------------------
def load_profiles():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and data:
                return data
        except Exception:
            pass
    return dict(PRESET_PROFILES)


def save_profiles(profiles):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(profiles, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------
# 探测：S0 环境自检 / S2 就绪自测（全部只读）
# ---------------------------------------------------------------
def env_check():
    lines = []
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.free", "--format=csv,noheader"],
                           capture_output=True, text=True, timeout=20)
        lines.append("GPU: " + (r.stdout.strip() or r.stderr.strip()))
    except Exception as e:
        lines.append("GPU: 探测失败 " + str(e))
    try:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ninfer-serve*", "/FO", "CSV", "/NH"],
                           capture_output=True, text=True, timeout=20)
        out = r.stdout.strip()
        lines.append("ninfer-serve 进程: " + (out if out else "(无)"))
    except Exception as e:
        lines.append("ninfer-serve 进程: 探测失败 " + str(e))
    return lines


def readiness_test(port=PORT_DEFAULT):
    """S2：/v1/models + 真发一条请求。返回 [ (标题, 结果, 摘要) ]。"""
    res = []
    base = f"http://127.0.0.1:{port}"
    # 1) /v1/models
    try:
        with urllib.request.urlopen(base + "/v1/models", timeout=15) as r:
            body = r.read().decode("utf-8", "replace")
            res.append(("GET /v1/models", str(r.status), body[:400]))
    except Exception as e:
        res.append(("GET /v1/models", "ERR", str(e)))
    # 2) 真发请求（判活必须真发；max_tokens 取安全小值）
    payload = json.dumps({
        "model": "qwen3.8-27b",
        "messages": [{"role": "user", "content": "用一句话回答：1+1 等于几？"}],
        "max_tokens": 64, "temperature": 0,
    }).encode("utf-8")
    req = urllib.request.Request(base + "/v1/chat/completions", data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            j = json.loads(r.read().decode("utf-8", "replace"))
            ch = (j.get("choices") or [{}])[0]
            content = (ch.get("message") or {}).get("content", "")
            fin = ch.get("finish_reason", "?")
            res.append(("POST /v1/chat/completions", str(r.status),
                        f"finish_reason={fin}\ncontent={content[:300]}"))
    except Exception as e:
        res.append(("POST /v1/chat/completions", "ERR", str(e)))
    return res


# ---------------------------------------------------------------
# 悬停提示
# ---------------------------------------------------------------
class ToolTip:
    def __init__(self, widget, text):
        self.widget, self.text, self.tip = widget, text, None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _show(self, _e=None):
        if not self.text or self.tip is not None:
            return
        try:
            self.tip = tk.Toplevel(self.widget)
            self.tip.wm_overrideredirect(True)
            self.tip.attributes("-topmost", True)
            tk.Label(self.tip, text=self.text, bg="#ffffe4", fg="#222",
                     font=("Microsoft YaHei UI", 9), wraplength=340, justify="left",
                     padx=8, pady=6).pack()
            x, y = self.widget.winfo_rootx(), self.widget.winfo_rooty()
            self.tip.wm_geometry(f"+{x+24}+{y+self.widget.winfo_height()+6}")
        except Exception:
            pass

    def _hide(self, _e=None):
        if self.tip is not None:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None


# ---------------------------------------------------------------
# 图形界面
# ---------------------------------------------------------------
class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NInfer 官方线启动器 · Bonsai-27B-NInfer-kvmem")
        self.root.geometry("900x700")
        self.root.minsize(780, 660)
        self.bg, self.fg = "#f4f8ff", "#1a3a6b"
        self.root.configure(bg=self.bg)

        self.profiles = load_profiles()
        self.selection = dict(DEFAULTS)
        self.var = {}
        self._label2key = {}
        self._build_widgets()
        self._refresh()

    def _build_widgets(self):
        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill="both", expand=True, padx=14, pady=12)

        tk.Label(main, text="NInfer 官方线启动器", font=("Microsoft YaHei UI", 15, "bold"),
                 bg=self.bg, fg="#1b4d8a").pack(anchor="w")
        tk.Label(main, text="Bonsai-27B-NInfer-kvmem · 官方 sm_120a 引擎 · 端口 8094",
                 font=("Microsoft YaHei UI", 9), bg=self.bg, fg="#5a6b8a").pack(anchor="w", pady=(0, 6))

        # 左：参数区（可滚动）
        left_outer = tk.Frame(main, bg=self.bg)
        left_outer.pack(side="left", fill="y", padx=(0, 14))
        canvas = tk.Canvas(left_outer, bg=self.bg, highlightthickness=0, width=210)
        scroll = ttk.Scrollbar(left_outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=self.bg)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="y")
        scroll.pack(side="right", fill="y")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", lambda ev: canvas.yview_scroll(-1 * (ev.delta // 120), "units")))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        for key, label, opts in DIMENSIONS:
            box = tk.LabelFrame(inner, text=label, font=("Microsoft YaHei UI", 10), bg=self.bg, fg="#2b3a6b")
            box.pack(fill="x", pady=4)
            ToolTip(box, DIM_TIPS.get(key, ""))
            self._label2key[key] = {lbl: val for val, (lbl, _) in opts.items()}
            self.var[key] = tk.StringVar(value=opts[DEFAULTS[key]][0])
            cb = ttk.Combobox(box, state="readonly", textvariable=self.var[key], width=24,
                              font=("Microsoft YaHei UI", 9))
            cb["values"] = list(self._label2key[key].keys())
            cb.bind("<<ComboboxSelected>>", lambda _e: self._on_change())
            cb.pack(anchor="w", padx=8, pady=4)

        # 右：预览 + 操作
        right = tk.Frame(main, bg=self.bg)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(right, text="启动命令预览", bg=self.bg, fg="#9b8c5a",
                 font=("Microsoft YaHei UI", 10, "bold")).pack(anchor="w", pady=(0, 2))
        self.cmd_box = tk.Text(right, height=10, width=62, wrap="word", bg="white", fg="#1a1a1a",
                               bd=1, relief="solid", font=("Consolas", 9))
        self.cmd_box.pack(fill="both", expand=True)
        self.cmd_box.configure(state="disabled")

        self.status = tk.Label(right, text="", bg=self.bg, fg="#4a6b4a",
                               font=("Microsoft YaHei UI", 9), justify="left", anchor="w", wraplength=560)
        self.status.pack(anchor="w", pady=(6, 0))

        # 操作按钮
        btns = tk.Frame(right, bg=self.bg)
        btns.pack(fill="x", pady=(10, 4))
        ttk.Button(btns, text="启 动", command=self._launch, width=12).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="环境自检", command=self._env_check, width=10).pack(side="left", padx=6)
        ttk.Button(btns, text="就绪自测", command=self._readiness, width=10).pack(side="left", padx=6)

        # 命名组合
        combox = tk.Frame(right, bg=self.bg)
        combox.pack(fill="x", pady=(6, 2))
        tk.Label(combox, text="命名组合:", bg=self.bg, fg="#2b3a6b",
                 font=("Microsoft YaHei UI", 10)).pack(side="left")
        self.profile_cb = ttk.Combobox(combox, state="readonly", width=20, values=list(self.profiles.keys()))
        self.profile_cb.pack(side="left", padx=(6, 0))
        ttk.Button(combox, text="加载", command=self._load_profile).pack(side="left", padx=4)
        ttk.Button(combox, text="保存当前", command=self._save_profile).pack(side="left", padx=4)
        ttk.Button(combox, text="删除", command=self._del_profile).pack(side="left", padx=4)

        tk.Label(right, text="提示：启动后引擎在“新控制台窗口”里运行 —— 关掉那个窗口 = 停服。",
                 bg=self.bg, fg="#8a6b3a", font=("Microsoft YaHei UI", 9), wraplength=560,
                 justify="left").pack(anchor="w", pady=(6, 0))

    # ---- 事件 ----
    def _on_change(self):
        for key in self.var:
            self.selection[key] = self._label2key[key].get(self.var[key].get(), self.selection.get(key))
        self._refresh()

    def _refresh(self):
        self.selection = {k: self.selection.get(k, DEFAULTS[k]) for k in DEFAULTS}
        exe, argv = build_command(self.selection)
        envs = " ".join(f"{k}={v}" for k, v in KV_ENV.items())
        text = f"[env  {envs}]\n\n{exe}\n  " + "\n  ".join(argv)
        self.cmd_box.configure(state="normal")
        self.cmd_box.delete("1.0", "end")
        self.cmd_box.insert("1.0", text)
        self.cmd_box.configure(state="disabled")
        warns = validate(self.selection)
        if warns:
            self.status.config(text="⚠ " + "\n⚠ ".join(warns), fg="#b07a20")
        else:
            self.status.config(text="✓ 配置合法，可启动", fg="#4a6b4a")

    # ---- 异步执行小工具（避免 GUI 卡死）----
    def _run_async(self, fn, on_done):
        q = queue.Queue()

        def worker():
            try:
                q.put(("ok", fn()))
            except Exception as e:
                q.put(("err", str(e)))

        threading.Thread(target=worker, daemon=True).start()

        def poll():
            try:
                kind, val = q.get_nowait()
            except queue.Empty:
                self.root.after(300, poll)
                return
            on_done(kind, val)

        self.root.after(300, poll)

    def _show_lines(self, title, lines):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=self.bg)
        win.geometry("760x420")
        t = tk.Text(win, wrap="word", bg="white", fg="#1a1a1a", font=("Consolas", 9))
        t.pack(fill="both", expand=True, padx=10, pady=10)
        t.insert("1.0", lines)
        t.configure(state="disabled")

    def _env_check(self):
        self.status.config(text="环境自检中…", fg="#2b3a6b")
        self._run_async(env_check, lambda k, v: self._show_lines(
            "环境自检（S0 只读）", "\n".join(v) if k == "ok" else "探测失败: " + v))

    def _readiness(self):
        self.status.config(text="就绪自测中…（首次请求可能较慢）", fg="#2b3a6b")

        def done(kind, val):
            if kind != "ok":
                self.status.config(text="自测失败: " + val, fg="#b03030")
                return
            lines = []
            ok = True
            for name, code,摘要 in val:
                lines.append(f"[{code}] {name}\n    {摘要}\n")
                if code == "ERR":
                    ok = False
            self._show_lines("就绪自测（S2）", "\n".join(lines))
            self.status.config(text=("✓ 就绪自测完成" if ok else "⚠ 就绪自测有问题（见弹窗）"),
                               fg=("#4a6b4a" if ok else "#b03030"))

        self._run_async(lambda: readiness_test(PORT_DEFAULT), done)

    # ---- 启动 ----
    def _launch(self):
        warns = validate(self.selection)
        hard = [w for w in warns if "未找到" in w or "非 ASCII" in w]
        if hard:
            messagebox.showerror("无法启动", "\n".join(hard))
            return
        exe, argv = build_command(self.selection)
        if not messagebox.askyesno("启动确认", f"确认启动 serve？\n\n{exe}\n\n端口: {PORT_DEFAULT}\n\n"
                                               f"（会在新控制台窗口运行；关窗 = 停服）"):
            return
        try:
            CREATE_NEW_CONSOLE = 0x00000010
            subprocess.Popen([exe] + argv, env=env_for_launch(), cwd=ROOT,
                             creationflags=CREATE_NEW_CONSOLE)
            self.status.config(text="✓ 已启动（新控制台窗口，关窗即停）—— 首次启动见 calibrating routes 请勿杀进程",
                               fg="#4a6b4a")
        except Exception as e:
            messagebox.showerror("启动失败", str(e))

    # ---- 命名组合 ----
    def _load_profile(self):
        name = self.profile_cb.get()
        if not name or name not in self.profiles:
            self.status.config(text="未选择或找不到组合", fg="#b03030")
            return
        combo = self.profiles[name]
        for key, val in combo.items():
            if key in self._label2key and val in self._label2key[key]:
                self.var[key].set(self._label2key[key][val])
        self._on_change()
        self.status.config(text=f"已加载组合 '{name}'", fg="#4a6b4a")

    def _save_profile(self):
        name = simpledialog.askstring("保存组合", "输入组合名称：")
        if not name:
            return
        self.profiles[name] = dict(self.selection)
        save_profiles(self.profiles)
        self.profile_cb["values"] = list(self.profiles.keys())
        self.profile_cb.set(name)
        self.status.config(text=f"已保存组合 '{name}'", fg="#4a6b4a")

    def _del_profile(self):
        name = self.profile_cb.get()
        if not name or name not in self.profiles:
            return
        del self.profiles[name]
        save_profiles(self.profiles)
        self.profile_cb["values"] = list(self.profiles.keys())
        self.profile_cb.set("")


def main():
    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

# ---------------------------------------------------------------
# TODO（后续版本补齐，对齐自建线 ninfer_launcher.py 的全部功能）：
#   · 场景预设（一键推荐组合）
#   · 更多维度：spec draft 1..15 二级联动、--thinking-budget、--prefill-cublas、
#     --lookup-ngram、--vision-residency、--kv-headroom-mib、--seed 等
#   · 日志落盘（serve_tee 等价物，写 logs\serve_<时间戳>.log）
#   · 端口可改、S3 KVMem 检索证据（kvmem_score: SELECT）采集
# ---------------------------------------------------------------
