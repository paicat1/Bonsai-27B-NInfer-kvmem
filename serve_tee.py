# -*- coding: utf-8 -*-
"""serve_tee.py <logfile> <command...>

以"可见控制台窗口"运行 <command...>（引擎），把它的 stdout+stderr **实时转发到控制台**
并**同时落盘**到 <logfile> —— 供 grep 取证（如 `kvmem_score: SELECT`）。
关闭本控制台窗口 = 终止本进程 = 引擎随控制台退出（**关窗=停服**）。
颜色：控制台窗口给关键数字上色（decode 绿 / prefill 黄 / 接受率红）；**日志文件始终原文**（不带色，保 grep）。
colorama 可选：有则启用 Windows ANSI/VT 色码；无则降级无色，不阻断 serve。
"""
import os
import re
import subprocess
import sys
import time

try:
    import colorama  # 可选依赖：启用 Windows ANSI/VT 色码渲染（缺失时降级为无色）
    colorama.init()
except ImportError:
    colorama = None

# ---- 颜色（ANSI 256 / VT100）----
C_RED    = "\033[91m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_RESET  = "\033[0m"


def is_kept_noise(line):
    """判定是否为 KVMem KEPT 刷屏行（`kvmem_score: KEPT ...` 大段数字）。
    这类行由引擎硬编码 fprintf 无条件输出（无环境变量可关），只在**控制台窗口**过滤掉，
    **日志文件仍全文落盘**（保留 grep 取证）。保留 `kvmem_score: SELECT ...` 与业务行。"""
    return line.startswith("kvmem_score: KEPT")


def colorize(line):
    """给日志行中的关键数据上色：decode数值(绿)、接受率%(红)、prefill数值(黄)。
    直接输出 ANSI/VT 色码 —— 本终端原生支持，无需 colorama。"""
    # decode 数值 -> 绿："decode 129.6 tok/s"
    line = re.sub(r"(decode )(\d+(?:\.\d+)?)( tok/s)",
                  lambda m: m.group(1) + C_GREEN + m.group(2) + C_RESET + m.group(3), line)
    # 接受率（mtp / dflash2 accepted）-> 红："(83.0%)"
    line = re.sub(r"((?:mtp|dflash2) accepted[^()]*\()(\d+(?:\.\d+)?%)\)",
                  lambda m: m.group(1) + C_RED + m.group(2) + C_RESET + ")", line)
    # prefill 数值 -> 黄："prefill 1.43k tok/s" / "prefill 146.7 tok/s"
    line = re.sub(r"(prefill )([\d.]+k?)( tok/s)",
                  lambda m: m.group(1) + C_YELLOW + m.group(2) + C_RESET + m.group(3), line)
    return line


def main(argv):
    if len(argv) < 3:
        sys.stderr.write("usage: serve_tee.py <logfile> <command...>\n")
        return 2
    logfile = argv[1]
    cmd = argv[2:]
    d = os.path.dirname(logfile)
    if d:
        os.makedirs(d, exist_ok=True)
    log = open(logfile, "ab", buffering=0)
    header = ("\n===== serve_tee start {} =====\nCMD: {}\n".format(
        time.strftime("%Y-%m-%d %H:%M:%S"), " ".join(cmd))).encode("utf-8", "replace")
    log.write(header)
    try:
        sys.stdout.buffer.write(header)
        sys.stdout.buffer.flush()
    except Exception:
        pass

    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0)
    except Exception as e:
        log.write(("LAUNCH FAILED: {}\n".format(e)).encode("utf-8", "replace"))
        log.close()
        return 1

    out = proc.stdout
    while True:
        raw = out.readline()
        if not raw:
            break
        text = raw.decode("utf-8", "replace")
        # 窗口显示：KEPT 刷屏行只在窗口过滤（日志文件仍全文写盘，保 grep）
        if not is_kept_noise(text):
            try:
                colored = colorize(text).encode("utf-8", "replace")
                sys.stdout.buffer.write(colored)
                sys.stdout.buffer.flush()
            except Exception:
                pass
        try:
            log.write(raw)  # 日志文件始终原文（不带色，保 grep 取证）
        except Exception:
            pass

    code = proc.wait()
    tail = ("===== serve_tee end (exit={}) {} =====\n".format(
        code, time.strftime("%Y-%m-%d %H:%M:%S"))).encode("utf-8", "replace")
    try:
        sys.stdout.buffer.write(tail)
        sys.stdout.buffer.flush()
    except Exception:
        pass
    log.write(tail)
    log.close()
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
