#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf.py：用本机 Chrome / Chromium / Edge 把 html 打印成 PDF。

slides（build.py 的产物）每屏一页 16:9；--steps 时分步屏一步一页。
handout / script 的 A4 网页也能用它打印，页眉页码由页面自己的 @page 规则生成。

用法：
  python3 pdf.py 课程.html                 # → 课程.pdf
  python3 pdf.py 课程.html --steps -o 课程_逐步.pdf
找不到浏览器时，用环境变量 CHROME 指定可执行文件路径。
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHROMES = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
           "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
           "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
           "chrome", "msedge"]


def chrome():
    for c in [os.environ.get("CHROME")] + CHROMES:
        p = c and (shutil.which(c) or (c if Path(c).exists() else None))
        if p:
            return p
    return None


def to_pdf(src, out, steps=False):
    ch = chrome()
    if not ch:
        sys.exit("[pdf] 没找到 Chrome / Chromium / Edge；用环境变量 CHROME 指定路径")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.unlink(missing_ok=True)
    url = src.as_uri() + ("?print=steps" if steps else "")
    r = subprocess.run([ch, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--no-pdf-header-footer", "--virtual-time-budget=3000",
                        "--print-to-pdf=%s" % out, url], capture_output=True)
    if r.returncode or not out.exists():
        sys.exit("[pdf] 打印失败：%s" % (r.stderr.decode(errors="replace").strip()[-300:] or r.returncode))
    pages = len(re.findall(rb"/Type\s*/Page\b", out.read_bytes()))
    print("[pdf] 写出 %s（%d 页）" % (out, pages))


def main():
    ap = argparse.ArgumentParser(description="html → PDF（本机 Chrome）")
    ap.add_argument("src", help="build.py / handout.py / script.py 生成的 html")
    ap.add_argument("-o", "--out", help="输出 pdf 路径，默认同名 .pdf")
    ap.add_argument("--steps", action="store_true", help="slides 分步屏一步一页（默认只出最终态）")
    a = ap.parse_args()
    src = Path(a.src).resolve()
    if not src.exists():
        sys.exit("[pdf] 文件不存在：%s" % src)
    to_pdf(src, Path(a.out).resolve() if a.out else src.with_suffix(".pdf"), a.steps)


if __name__ == "__main__":
    main()
