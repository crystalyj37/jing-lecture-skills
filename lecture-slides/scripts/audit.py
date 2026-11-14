#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lecture-slides audit：交付前的静态体检。

只查「不用打开浏览器就能确定错了」的事。真正的位置/字号问题必须用浏览器量，
命令见 references/validation.md。

用法：
  python3 audit.py 课程.html
  python3 audit.py 课程.deck.md      # 也接受源稿，先查结构
退出码：0 = 无 error；1 = 有 error。
"""

import re
import sys
from pathlib import Path

# 屏幕安全区：1920×1080，底部工具条 40px
SCREEN_W, SCREEN_H, BAR_H = 1920, 1080, 40

errs, warns, infos = [], [], []


def err(m):
    errs.append(m)


def warn(m):
    warns.append(m)


def info(m):
    infos.append(m)


def check_source(text):
    """源稿层面的检查：标记是否配对、属性是否齐全。"""
    opens = len(re.findall(r'(?m)^:::\s*screen\b', text))
    info("屏块 %d 个" % opens)
    if opens == 0:
        err("没有 ::: screen 块，检查标记写法")

    # ::: 深度必须归零
    depth = 0
    for i, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if not s.startswith(":::"):
            continue
        if s == ":::":
            depth -= 1
            if depth < 0:
                err("第 %d 行：多余的 :::（深度变负）" % i)
                depth = 0
        else:
            depth += 1
    if depth != 0:
        err(":: 标记未闭合，结余深度 %d" % depth)

    for m in re.finditer(r'(?m)^:::\s*screen\s*(.*)$', text):
        attrs = m.group(1)
        if "id=" not in attrs:
            warn("有屏未写 id，build 会用 s<序号> 兜底")
        if "title=" not in attrs:
            err("屏缺 title=，目录与底栏会空：%s" % attrs.strip()[:60])

    # 公式块：空块会让整屏排版塌成一条空白
    for i, m in enumerate(re.finditer(r'(?ms)^:::\s*fml\s*$\n(.*?)^:::\s*$', text), 1):
        if not m.group(1).strip():
            warn("第 %d 个 ::: fml 块是空的" % i)

    # 组合变音符号：p̂ / x̄ / ž 这类「字母 + U+030x」在中文字体里定位是错的，
    # 帽子会飘到右下角，看起来像个撇。要让用户改写成 \(...\)，不能只靠肉眼发现。
    for i, line in enumerate(text.split("\n"), 1):
        if re.search(r"[\u0300-\u036f]", line):
            warn("第 %d 行有组合符号（%s），中文字体里会盖歪；"
                 "公式里写 \\hat{p}，说明文字里写 \\(\\hat p\\)"
                 % (i, line.strip()[:36]))


def check_html(doc):
    screens = re.findall(r'<section class="screen"[^>]*>', doc)
    if not screens:
        err("成品里没有 <section class=\"screen\">")
        return

    ids = re.findall(r'<section class="screen" id="([^"]*)"', doc)
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        err("屏 id 重复：%s" % "、".join(sorted(dup)))
    if len(ids) != len(screens):
        err("%d 个屏里有 %d 个带 id" % (len(screens), len(ids)))

    # 逐屏：steps 与 data-step 是否自洽
    for sec in re.findall(r'<section class="screen".*?</section>', doc, re.S):
        sid = (re.search(r'id="([^"]*)"', sec) or [None, "?"])[1]
        title = (re.search(r'data-title="([^"]*)"', sec) or [None, ""])[1]
        steps = int((re.search(r'data-steps="(\d+)"', sec) or [None, "0"])[1])
        marks = [int(x) for x in re.findall(r'data-step="(\d+)"', sec)]

        if not title:
            err("[%s] data-title 为空" % sid)
        if steps and not marks:
            err("[%s] 声明 steps=%d 却没有 [data-step] 元素" % (sid, steps))
        if marks:
            if 0 in marks:
                err("[%s] 出现 data-step=\"0\"，第 0 步永远不会被点亮" % sid)
            if max(marks) > steps:
                err("[%s] 最大 data-step=%d 超过 data-steps=%d，最后一步走不到"
                    % (sid, max(marks), steps))
            if max(marks) < steps:
                warn("[%s] data-steps=%d 但最大只到 %d，多出的步数是空翻"
                     % (sid, steps, max(marks)))
            gaps = [n for n in range(1, max(marks) + 1) if n not in marks]
            if gaps:
                warn("[%s] 步号不连续，缺 %s" % (sid, gaps))

        if 'class="spk"' not in sec:
            info("[%s] 无演讲者备注" % sid)

        # 表格列数一致
        for tbl in re.findall(r'<div class="tbl[^"]*"[^>]*>(.*?)\n</div>\n', sec, re.S):
            counts = [len(re.findall(r"<span[ >]", row))
                      for row in re.findall(r'<div class="tr[^"]*"[^>]*>.*?</div>', tbl, re.S)]
            if len(set(counts)) > 1:
                err("[%s] 表格列数不一致：%s" % (sid, counts))

        # 显式超宽
        for m in re.finditer(r'(?:width|min-width)\s*:\s*(\d{4,})px', sec):
            if int(m.group(1)) > SCREEN_W:
                err("[%s] 出现 width:%spx，超出 %d 画布" % (sid, m.group(1), SCREEN_W))

    # 图片：必须是内嵌或明确外链
    imgs = re.findall(r'<img[^>]+src="([^"]{0,80})', doc)
    local = [s for s in imgs if not s.startswith("data:") and not s.startswith("http")]
    if local:
        warn("%d 张图不是内嵌/外链，移动文件会掉图：%s" % (len(local), local[:3]))
    info("图片 %d 张，其中内嵌 %d 张"
         % (len(imgs), len([s for s in imgs if s.startswith("data:")])))

    if ":::" in doc:
        err("成品里还有 ::: 标记，说明有块没被 build 吃掉")
    for ph in ("{{TITLE}}", "{{SCREENS}}", "{{TOC}}", "{{TOKENS}}", "{{MATH_CSS}}"):
        if ph in doc:
            err("占位符未替换：%s" % ph)

    check_math(doc)
    check_vars(doc)


def check_math(doc):
    """
    公式是构建期排好的静态 HTML，所以这里查的是「排完之后还缺什么」。
    最容易出的两种静默坏法：样式没注入（符号挤成一团）、字体被裁掉了（字形变方框）。
    """
    nodes = len(re.findall(r'class="katex[ "]', doc))
    if not nodes:
        return

    bad = len(re.findall(r'class="katex-error"', doc))
    if bad:
        err("有 %d 处公式渲染失败（页面上会显示红字源码）" % bad)

    head = doc.split("</style>")[0]
    if ".katex{" not in head and ".katex " not in head and ".katex-display" not in head:
        err("页面里有公式，但没有注入 KaTeX 样式——符号会挤成一团")
    for need in ("KaTeX_Main", "KaTeX_Math", "KaTeX_Size1"):
        if need not in head:
            err("公式缺少字体 %s，字形会掉成方框" % need)

    if "katex.render" in doc or "renderToString" in doc or "katex.min.js" in doc:
        warn("产物里还带着 KaTeX 运行时脚本；公式应在构建期排好，运行时不需要它")

    info("公式 %d 处，字体 %d 个"
         % (nodes, len(set(re.findall(r'font-family:\s*"?(KaTeX_[A-Za-z0-9]+)', head)))))


def check_vars(doc):
    """
    自定义属性闭环：用到 var(--x) 的，--x 必须在某处定义。
    漏定义的后果是静默失效（整条声明按 initial 走），页面上只是"看起来怪"，不报错。
    曾经 --split 就藏在 :root 里被漏掉过，对照屏直接不分栏。
    """
    used = set(re.findall(r"var\(\s*(--[A-Za-z0-9_-]+)", doc))
    defined = set(re.findall(r"(?<![\w-])(--[A-Za-z0-9_-]+)\s*:", doc))
    missing = sorted(used - defined)
    if missing:
        err("用到了没定义的变量：%s" % ", ".join(missing))
    orphan = sorted(defined - used)
    if orphan:
        info("定义的变量有 %d 个本文件没用上（跨产品共用是正常的）" % len(orphan))


def main():
    if len(sys.argv) < 2:
        sys.exit("用法：python3 audit.py <deck.md|deck.html>")
    p = Path(sys.argv[1]).resolve()
    if not p.exists():
        sys.exit("文件不存在：%s" % p)
    text = p.read_text(encoding="utf-8")

    if p.suffix.lower() in (".md", ".markdown"):
        check_source(text)
    else:
        check_source(text) if "::: screen" in text else None
        check_html(text)
        size = len(text.encode()) / 1024
        info("单文件 %.0f KB" % size)
        if size > 4 * 1024:
            warn("超过 4 MB，首次打开会慢；考虑把大视频改成外链")

    for m in infos:
        print("  信息  " + m)
    for m in warns:
        print("  注意  " + m)
    for m in errs:
        print("  错误  " + m)
    print("\n结论：%d error / %d warn" % (len(errs), len(warns)))
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
