#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
mathx.py：给 handout.py / script.py 用的构建期公式。

渲染器不另写一份，直接调 lecture-slides 的 build.py（node + KaTeX），产物里是静态 HTML，
打印成 PDF 也是排好的公式。写法与 slides 保持一致：
  独占一段的 $$ ... $$（可以跨行）→ 块公式
  行内 \( ... \)                    → 行内公式
代码块里的不动。没有 node 时直接报错；加 --no-math 则原样保留公式源码。
"""

import html
import re
import shutil
import sys
from pathlib import Path

SLIDES = Path(__file__).resolve().parent.parent.parent / "lecture-slides" / "scripts"
BLOCK = re.compile(r"^[ \t]*\$\$(.+?)\$\$[ \t]*$", re.S | re.M)
INLINE = re.compile(r"\\\((.+?)\\\)", re.S)
FENCE = re.compile(r"(^```.*?^```[ \t]*$)", re.S | re.M)
TOK = re.compile("\ue000(\\d+)\ue001")
CSS = ".fmath{margin:1.1em 0;text-align:center;overflow-x:auto;overflow-y:hidden}\n"


def extract(md):
    """公式换成占位符，返回 (md, items)；items[i] = (tex, 是否块公式, 原文)。"""
    items = []

    def take(display):
        def f(m):
            items.append((m.group(1).strip(), display, m.group(0).strip()))
            tok = "\ue000%d\ue001" % (len(items) - 1)
            return "\n\n%s\n\n" % tok if display else tok
        return f

    parts = FENCE.split(md)
    for i in range(0, len(parts), 2):
        parts[i] = INLINE.sub(take(False), BLOCK.sub(take(True), parts[i]))
    return "".join(parts), items


def render(items, enabled, tool):
    """返回 (把占位符换成公式的函数, 要注入的 css)。"""
    if not items:
        return (lambda s: s), ""
    if not enabled:
        return (lambda s: TOK.sub(lambda m: html.escape(items[int(m.group(1))][2], quote=False), s)), ""
    if not (SLIDES / "build.py").exists():
        sys.exit("[%s] 公式要用 lecture-slides 的渲染器，没找到 %s；两个 skill 要并排放，"
                 "或加 --no-math 保留原文" % (tool, SLIDES / "build.py"))
    if not shutil.which("node"):
        sys.exit("[%s] 源稿里有公式（$$...$$ 或 \\(...\\)），但环境里没有 node。\n"
                 "        公式在构建期用 KaTeX 排版，需要 node 22+（https://nodejs.org）；装好再跑。\n"
                 "        暂时装不了，加 --no-math 原样保留公式源码。" % tool)
    sys.path.insert(0, str(SLIDES))
    import build
    table = build.render_math([(t, d) for t, d, _ in items])
    css = CSS + build.katex_css([t for t, _, _ in items])

    def html_of(i):
        t, d, _ = items[i]
        return table[(t, d)]

    def fill(s):
        s = re.sub(r"<p>\ue000(\d+)\ue001</p>",
                   lambda m: '<div class="fmath">%s</div>' % html_of(int(m.group(1))), s)
        return TOK.sub(lambda m: html_of(int(m.group(1))), s)
    return fill, css
