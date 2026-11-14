#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
handout.py：把 handout.md 转成单文件 html（单栏、可打印、手机可读、自动目录）。

只支持写讲稿材料真正会用到的那几样语法：
  标题 h1–h4 / 段落 / 无序与有序列表 / 管道表格 / 引用 / 代码块 / 分隔线
  行内 **粗体** `代码` [链接](url) ![图](path)
不支持脚注语法与数学公式——要公式就写进 <span class="math">…</span>。

本地图片会转成 base64 内嵌，换机器不掉图。

用法：
  python3 handout.py handout.md -o handout.html
  python3 handout.py handout.md -o handout.html --title "标题" --no-toc
"""

import argparse
import base64
import html
import mimetypes
import re
import sys
from pathlib import Path

import theme

CSS = """
{{TOKENS}}
/* 产品别名：通用角色 → A4 材料那一档纸墨（配色表在 lecture-slides/assets/tokens.css） */
:root{
  --ink:var(--ink-print); --ink2:var(--ink2-print); --muted:var(--muted-print);
  --paper:var(--paper-print); --line:var(--line-print);
}
*{box-sizing:border-box}
html{font-size:16px;-webkit-font-smoothing:antialiased}
body{
  margin:0;padding:0;background:var(--gutter);color:var(--ink);
  font-family:"Songti SC","Source Han Serif SC","Noto Serif SC","PingFang SC",
    "Hiragino Sans GB","Microsoft YaHei",serif;
  line-height:1.92;
}
.page{
  max-width:760px;margin:0 auto;background:var(--paper);
  padding:64px 72px 96px;box-shadow:0 1px 3px rgba(0,0,0,.08);
}
h1{font-size:1.95rem;line-height:1.35;margin:0 0 .4em;letter-spacing:-.01em}
h2{font-size:1.42rem;line-height:1.45;margin:2.6em 0 .8em;padding-bottom:.32em;
   border-bottom:1px solid var(--line)}
h3{font-size:1.12rem;margin:2em 0 .6em}
h4{font-size:1rem;margin:1.6em 0 .5em;color:var(--ink2)}
p{margin:0 0 1.05em;text-align:justify;text-justify:inter-ideograph}
p,li,td,th,blockquote{overflow-wrap:anywhere}
.brk{word-break:break-all}   /* 超长 ASCII 串允许从任意处断开，避免整行被拉开 */   /* 长网址/长英文串不顶出边界 */
ul,ol{margin:0 0 1.1em;padding-left:1.6em}
li{margin:.3em 0}
strong{font-weight:700;color:var(--ink-strong)}
a{color:var(--accent);text-decoration:none;border-bottom:1px solid var(--accent-line)}
a:hover{border-bottom-color:var(--accent)}
code{background:var(--code);padding:.12em .38em;border-radius:3px;
     font-family:ui-monospace,Menlo,monospace;font-size:.9em}
pre{background:var(--code);padding:16px 18px;border-radius:6px;overflow-x:auto;
    font-size:.88rem;line-height:1.65;margin:0 0 1.2em}
pre code{background:none;padding:0}
blockquote{margin:1.2em 0;padding:.2em 0 .2em 1.1em;border-left:3px solid var(--accent);
           color:var(--ink2)}
blockquote p{margin:.45em 0}
hr{border:0;border-top:1px solid var(--line);margin:2.4em 0}
table{border-collapse:collapse;width:100%;margin:1.2em 0 1.6em;font-size:.92rem;
      line-height:1.6;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.tw{margin:1.2em 0 1.6em;overflow-x:auto;-webkit-overflow-scrolling:touch}
.tw table{margin:0}
th,td{border-bottom:1px solid var(--line);padding:.55em .7em;text-align:left;vertical-align:top}
th{background:var(--th-bg);font-weight:600;white-space:nowrap}
tr:last-child td{border-bottom:1px solid var(--line)}
img{max-width:100%;height:auto;display:block;margin:1.4em auto;border-radius:4px}

.toc{background:var(--toc-bg);border:1px solid var(--line);border-radius:8px;
     padding:22px 26px;margin:2.2em 0 2.8em;font-family:"PingFang SC","Hiragino Sans GB",sans-serif}
.toc .tt{font-size:.78rem;letter-spacing:.16em;color:var(--muted);margin-bottom:.8em}
.toc a{display:block;padding:.18em 0;border:0;color:var(--ink2);font-size:.94rem}
.toc a.lv3{padding-left:1.3em;font-size:.88rem;color:var(--muted)}
.meta{font-size:.86rem;color:var(--muted);font-family:"PingFang SC","Hiragino Sans GB",sans-serif;
      margin-bottom:2.2em;padding-bottom:1.4em;border-bottom:1px solid var(--line)}
.math{font-family:"Times New Roman",serif;font-style:italic}

@media print{
  body{background:var(--paper-0);font-size:10.5pt;line-height:1.85}
  .page{box-shadow:none;max-width:none;padding:0}
  h1{font-size:18pt}
  h2{font-size:13.5pt;break-after:avoid}
  h3{font-size:11.5pt;break-after:avoid}
  h1,h2,h3,h4{break-inside:avoid}
  p{orphans:3;widows:3}
  pre,blockquote,img{break-inside:avoid}
  thead{display:table-header-group}
  tr{break-inside:avoid}
  .tw{overflow:visible;margin:1.2em 0 1.6em}
  table{width:100%;max-width:100%;table-layout:auto}
  .toc{break-inside:avoid}
  a{color:inherit;border:0;text-decoration:none}
  /* 打印后链接仍可点（Chrome 会把 <a> 写成 PDF 注释），但默认色被抹平后
     读者看不出哪里能点。给外链/邮箱留一条极细点线 + 强调色，可点性不变。 */
  a[href^="http"]{color:var(--accent);border-bottom:1px dotted var(--accent-dot)}
  a[href^="mailto"]{color:var(--accent);border-bottom:1px dotted var(--accent-dot)}
  .toc a,.toc a.lv3{color:inherit;border:0}
}
@media (max-width:640px){
  .page{padding:32px 22px 56px}
  h1{font-size:1.55rem}
  h2{font-size:1.24rem}
  table{font-size:.86rem}
  th,td{padding:.45em .5em}
}
"""


_TAG = re.compile(r"(<[^>]+>)")
_LONG = re.compile(r"([A-Za-z0-9][A-Za-z0-9_\-./:?&=#%~+@]{27,})")


def _brk(s):
    """把超长 ASCII 串（网址、长单词）包成可任意断行的 span。

    只处理文本节点，不碰 <a href> 之类标签内部，避免改坏属性。
    """
    parts = _TAG.split(s)
    return "".join(
        p if p.startswith("<") else _LONG.sub(r'<span class="brk">\1</span>', p)
        for p in parts
    )


def inline(s, base):
    s = html.escape(s, quote=False)
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: img_tag(m.group(1), m.group(2), base), s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return _brk(s)


def img_tag(alt, src, base):
    p = (base / src).resolve()
    if not src.startswith(("http://", "https://", "data:")) and p.exists():
        mime = mimetypes.guess_type(p.name)[0] or "image/png"
        data = base64.b64encode(p.read_bytes()).decode()
        src = "data:%s;base64,%s" % (mime, data)
    return '<img src="%s" alt="%s">' % (src, html.escape(alt))


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(md, base, want_toc=True):
    lines = md.split("\n")
    out, toc, i, n = [], [], 0, len(lines)
    code_buf, in_code = [], False

    while i < n:
        ln = lines[i]
        s = ln.strip()

        if s.startswith("```"):
            if in_code:
                out.append("<pre><code>%s</code></pre>"
                           % html.escape("\n".join(code_buf)))
                code_buf, in_code = [], False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_buf.append(ln)
            i += 1
            continue

        if not s:
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            lv = len(m.group(1))
            txt = inline(m.group(2), base)
            hid = "h%d-%d" % (lv, len(toc))
            if lv in (2, 3) and want_toc:
                toc.append((lv, txt, hid))
            out.append('<h%d id="%s">%s</h%d>' % (lv, hid, txt, lv))
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            out.append("<hr>")
            i += 1
            continue

        # 表格：当前行含 | 且下一行是分隔行
        if "|" in s and i + 1 < n and re.match(r"^\|?[\s:|-]+\|[\s:|-]*$", lines[i + 1].strip()):
            head = split_row(s)
            i += 2
            body = []
            while i < n and "|" in lines[i] and lines[i].strip():
                body.append(split_row(lines[i]))
                i += 1
            t = ["<table><thead><tr>"]
            t += ["<th>%s</th>" % inline(c, base) for c in head]
            t.append("</tr></thead><tbody>")
            for row in body:
                t.append("<tr>" + "".join("<td>%s</td>" % inline(c, base) for c in row) + "</tr>")
            t.append("</tbody></table>")
            out.append('<div class="tw">' + "".join(t) + "</div>")
            continue

        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>%s</blockquote>"
                       % "".join("<p>%s</p>" % inline(x, base) for x in buf if x))
            continue

        if re.match(r"^[-*+]\s+", s):
            items = []
            while i < n and re.match(r"^[-*+]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*+]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>%s</ul>"
                       % "".join("<li>%s</li>" % inline(x, base) for x in items))
            continue

        if re.match(r"^\d+\.\s+", s):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>%s</ol>"
                       % "".join("<li>%s</li>" % inline(x, base) for x in items))
            continue

        # 段落：吃到空行或块级标记
        buf = []
        while i < n:
            cur = lines[i]
            cs = cur.strip()
            if not cs or re.match(r"^(#{1,4}\s|```|>|[-*+]\s|\d+\.\s)", cs) \
               or re.match(r"^(-{3,}|\*{3,}|_{3,})$", cs):
                break
            if "|" in cs and i + 1 < n and re.match(r"^\|?[\s:|-]+\|[\s:|-]*$", lines[i + 1].strip()):
                break
            buf.append(cs)
            i += 1
        if buf:
            out.append("<p>%s</p>" % inline(" ".join(buf), base))

    body = "\n".join(out)
    if want_toc and len(toc) >= 3:
        rows = ['<div class="toc"><div class="tt">目 录</div>']
        for lv, txt, hid in toc:
            rows.append('<a class="lv%d" href="#%s">%s</a>' % (lv, hid, txt))
        rows.append("</div>")
        # 插到第一个 h2 之前
        idx = body.find("<h2")
        toc_html = "\n".join(rows)
        body = body[:idx] + toc_html + "\n" + body[idx:] if idx > 0 else toc_html + body
    return body


TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}
{page_css}</style>
</head>
<body>
<main class="page">
{body}
</main>
</body>
</html>
"""


def page_css(title, head="right", foot="center"):
    """A4 版心与页眉页脚。只在打印/导出 PDF 时生效，屏幕上完全看不到。

    Chrome 从 2023 年后的版本支持 @page 的 margin box，
    页眉页脚用 content + counter(page) 就能出，不必依赖打印接口的模板。
    """
    safe = title.replace("\\", "\\\\").replace('"', '\\"')
    rules = ['@page{size:A4;margin:20mm 18mm 20mm;',
             'font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}']
    if head == "right":
        rules.append('@page{@top-right{content:"%s";font-size:8pt;color:%s}}'
             % (safe, theme.value("--mark-print")))
        rules.append("@page:first{@top-right{content:none}}")
    if foot == "center":
        rules.append('@page{@bottom-center{content:counter(page) " / " counter(pages);'
                     'font-size:8.5pt;color:%s}}' % theme.value("--mark-print"))
    return "\n".join(rules)



def main():
    ap = argparse.ArgumentParser(description="handout.md → 单文件 html")
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("--title")
    ap.add_argument("--no-toc", action="store_true")
    ap.add_argument("--no-print-marks", action="store_true",
                    help="打印时不加页眉页脚（默认带标题与页码）")
    ap.add_argument("--tokens", help="另指定配色表（默认 lecture-slides/assets/tokens.css）")
    a = ap.parse_args()

    src = Path(a.src).resolve()
    if not src.exists():
        sys.exit("源文件不存在：%s" % src)
    md = src.read_text(encoding="utf-8")

    title = a.title
    if not title:
        m = re.search(r"^#\s+(.+)$", md, re.M)
        title = m.group(1).strip() if m else src.stem

    body = convert(md, src.parent, want_toc=not a.no_toc)
    css = CSS.replace("{{TOKENS}}", theme.css(a.tokens))
    doc = TEMPLATE.format(title=html.escape(title), css=css, body=body,
                          page_css=page_css(title,
                                            head=None if a.no_print_marks else "right",
                                            foot=None if a.no_print_marks else "center"))

    out = Path(a.out).resolve() if a.out else src.with_suffix(".html")
    out.write_text(doc, encoding="utf-8")
    print("[handout] 写出 %s（%.1f KB）" % (out, len(doc.encode()) / 1024))


if __name__ == "__main__":
    main()
