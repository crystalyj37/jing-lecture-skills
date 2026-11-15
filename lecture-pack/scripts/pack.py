#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pack.py：一条命令跑完全流程。

在一个目录里找 content-map.md / script.md / handout.md / *.deck.md，依次：
材料 → 讲稿 → slides 构建 → audit → 对账 →（--pdf）两份 A4 打印。
缺哪份就跳过哪份；任何一步失败，退出码为 1。

用法：
  python3 pack.py 讲座目录 --total 45
  python3 pack.py 讲座目录 --total 45 --pdf -o 讲座目录/dist
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLIDES = HERE.parent.parent / "lecture-slides" / "scripts"
CHROMES = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
           "chrome", "msedge"]


def chrome():
    for c in [os.environ.get("CHROME")] + CHROMES:
        p = c and (shutil.which(c) or (c if Path(c).exists() else None))
        if p:
            return p
    return None


def main():
    ap = argparse.ArgumentParser(description="lecture-pack：一条命令出三份产物并对账")
    ap.add_argument("dir", help="放源稿的目录")
    ap.add_argument("-o", "--out", help="产物目录，默认 <dir>/dist")
    ap.add_argument("--total", type=float, help="总时长（分钟），交给 crosscheck 判超时")
    ap.add_argument("--pdf", action="store_true", help="用本机 Chrome 打印 handout / script 的 PDF")
    a = ap.parse_args()

    src = Path(a.dir).resolve()
    if not src.is_dir():
        sys.exit("[pack] 目录不存在：%s" % src)
    out = Path(a.out).resolve() if a.out else src / "dist"
    out.mkdir(parents=True, exist_ok=True)
    f = {n: src / n for n in ("content-map.md", "script.md", "handout.md")}
    f = {k: v for k, v in f.items() if v.exists()}
    decks = sorted(src.glob("*.deck.md"))
    if len(decks) > 1:
        sys.exit("[pack] 目录里有 %d 份 .deck.md，只能有一份：%s"
                 % (len(decks), "、".join(d.name for d in decks)))
    deck = decks[0] if decks else None
    if not (f or deck):
        sys.exit("[pack] %s 里没有 content-map.md / script.md / handout.md / *.deck.md" % src)
    if deck and not (SLIDES / "build.py").exists():
        sys.exit("[pack] 找不到 %s；lecture-slides 要和 lecture-pack 并排放" % (SLIDES / "build.py"))

    py, steps, failed = sys.executable, [], []
    if "handout.md" in f:
        steps.append(("材料", [py, HERE / "handout.py", f["handout.md"], "-o", out / "handout.html"]))
    if "script.md" in f:
        steps.append(("讲稿", [py, HERE / "script.py", f["script.md"], "-o", out / "script.html"]))
    if deck:
        html = out / (deck.name[:-len(".deck.md")] + ".html")
        steps.append(("slides", [py, SLIDES / "build.py", deck, "-o", html]))
        steps.append(("体检", [py, SLIDES / "audit.py", html]))
    if "content-map.md" in f:
        cmd = [py, HERE / "crosscheck.py", f["content-map.md"]]
        for k, flag in (("script.md", "--script"), ("handout.md", "--handout")):
            if k in f:
                cmd += [flag, f[k]]
        if deck:
            cmd += ["--deck", deck]
        if a.total:
            cmd += ["--total", str(a.total)]
        steps.append(("对账", cmd))
    else:
        print("[pack] 没有 content-map.md，跳过对账")

    for name, cmd in steps:
        print("\n== %s" % name, flush=True)
        if subprocess.run([str(c) for c in cmd]).returncode:
            failed.append(name)

    if a.pdf:
        ch = chrome()
        if not ch:
            failed.append("PDF")
            print("\n[pack] 没找到 Chrome / Chromium / Edge；用环境变量 CHROME 指定路径")
        for n in ("handout", "script"):
            page = out / (n + ".html")
            if ch and page.exists():
                pdf = out / (n + ".pdf")
                pdf.unlink(missing_ok=True)
                r = subprocess.run([ch, "--headless=new", "--disable-gpu", "--no-sandbox",
                                    "--no-pdf-header-footer", "--print-to-pdf=%s" % pdf,
                                    page.as_uri()], capture_output=True)
                print("[pack] %s %s" % ("写出" if pdf.exists() and not r.returncode else "失败", pdf))
                if r.returncode or not pdf.exists():
                    failed.append("PDF")

    print("\n[pack] 产物在 %s" % out)
    if failed:
        sys.exit("[pack] 没过：%s" % "、".join(dict.fromkeys(failed)))
    print("[pack] 全部通过")


if __name__ == "__main__":
    main()
