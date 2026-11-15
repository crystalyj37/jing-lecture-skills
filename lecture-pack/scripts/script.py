#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
script.py：把讲稿 md 排成 A4 打印版（单栏、可朗读的字号、单元不拆行、提示灰底）。

与 handout.py 的分工：
  handout.py  给听众读，有目录、有图、版心 760px、五号字
  script.py   给自己读，无目录、无图、版心按 A4、11.5pt、右侧留白可手写

只支持讲稿真正用得到的语法：
  一级标题（文档名）/ 二级标题（单元，形如 `## U2.0 · 标题　[2′]　屏 n1`）/ 三级标题
  段落 / 列表 / 引用 / 代码块 / 分隔线 / 表格 / 粗体 / 行内代码 / 〔舞台提示〕

用法：
  python3 script.py script.md -o script.html
  python3 script.py script.md -o script.html --one-unit-per-page
  python3 script.py script.md -o script.html --no-print-marks
"""

import argparse
import html
import re
import sys
from pathlib import Path

import theme

WPM = 240          # 与 crosscheck.py 保持一致

CSS = """
{{TOKENS}}
/* 产品别名：通用角色 → A4 讲稿那一档纸墨（配色表在 lecture-slides/assets/tokens.css） */
:root{
  --ink:var(--ink-print); --ink2:var(--ink2-script); --muted:var(--muted-script);
  --paper:var(--paper-script); --line:var(--line-script); --code:var(--code-script);
}
*{box-sizing:border-box}
html{font-size:16px;-webkit-font-smoothing:antialiased}
body{
  margin:0;padding:0;background:var(--gutter);color:var(--ink);
  font-family:"Songti SC","Source Han Serif SC","Noto Serif SC","PingFang SC",
    "Hiragino Sans GB","Microsoft YaHei",serif;
  line-height:1.78;
}
.page{max-width:760px;margin:0 auto;background:var(--paper);padding:56px 64px 80px;
  box-shadow:0 1px 3px rgba(0,0,0,.08);font-size:15.5px}
h1{font-size:1.5rem;line-height:1.4;margin:0 0 .3em;letter-spacing:.01em}
.meta{font-size:.82rem;color:var(--muted);margin:0 0 2.4em;padding-bottom:1em;
  border-bottom:1px solid var(--line);
  font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
h3{font-size:1.02rem;margin:1.6em 0 .5em;font-weight:600}
p{margin:0 0 .85em;text-align:justify;text-justify:inter-ideograph}
p,li,td,th,blockquote{overflow-wrap:anywhere}
.brk{word-break:break-all}   /* 超长 ASCII 串允许任意处断开 */   /* 长网址/长英文串不顶出边界 */
ul,ol{margin:0 0 .9em;padding-left:1.5em}
li{margin:.25em 0}
strong{font-weight:700}
code{background:var(--code);padding:.1em .34em;border-radius:3px;
  font-family:ui-monospace,Menlo,monospace;font-size:.9em}
pre{background:var(--code);padding:12px 14px;border-radius:5px;overflow-x:auto;
  font-size:.86rem;line-height:1.6;margin:0 0 1em}
pre code{background:none;padding:0}
blockquote{margin:1em 0;padding:.1em 0 .1em 1em;border-left:3px solid var(--line);
  color:var(--ink2)}
hr{border:0;border-top:1px solid var(--line);margin:1.8em 0}
table{border-collapse:collapse;width:100%;margin:0 0 1.1em;font-size:.9rem;
  line-height:1.55;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
th,td{border-bottom:1px solid var(--line);padding:.4em .6em;text-align:left;vertical-align:top}
th{background:var(--th-bg-script);font-weight:600}
.tw{margin:0 0 1.1em;overflow-x:auto;-webkit-overflow-scrolling:touch}
.tw table{margin:0}

.unit{margin:0 0 2.2em;padding-top:1.4em;border-top:1px solid var(--line)}
.unit:first-of-type{border-top:0;padding-top:0}
.uh{display:flex;align-items:baseline;gap:.6em;margin:0 0 .9em;flex-wrap:wrap;
  font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.uid{font-size:.78rem;font-weight:600;color:var(--accent);letter-spacing:.06em}
.ut{font-size:1.16rem;font-weight:600;color:var(--ink);line-height:1.35}
.ub{margin-left:auto;font-size:.76rem;color:var(--muted);white-space:nowrap}
.ub b{font-weight:600;color:var(--ink2);font-variant-numeric:tabular-nums}

.cue{background:var(--cue-bg);color:var(--cue-ink);border-radius:3px;
  padding:.05em .4em;font-size:.88em;font-family:"PingFang SC","Hiragino Sans GB",sans-serif;
  font-style:normal;white-space:nowrap}
.cueblock{display:block;background:var(--cue-bg);color:var(--cue-ink);
  border-left:2px solid var(--cue-line);border-radius:0 4px 4px 0;
  padding:.3em .7em;margin:.2em 0 .9em;font-size:.88rem;
  font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.figref{color:var(--muted);font-size:.88em;font-style:normal}

@media print{
  body{background:var(--paper-0);font-size:11.5pt;line-height:1.8;color:var(--black)}
  .page{max-width:none;padding:0;box-shadow:none;font-size:11.5pt}
  h1{font-size:15pt;margin-bottom:.35em}
  .meta{font-size:8.5pt;margin-bottom:1.4em;padding-bottom:.6em}
  .ut{font-size:12pt}
  .uid,.ub{font-size:8.5pt}
  .unit{padding-top:.9em;margin-bottom:1.1em}
  .cue{font-size:9pt}
  .cueblock{font-size:9pt;break-inside:avoid}
  h3{font-size:10.5pt;break-after:avoid}
  p{orphans:3;widows:3}
  .uh{break-after:avoid}
  pre,blockquote{break-inside:avoid}
  thead{display:table-header-group}
  tr{break-inside:avoid}
  thead{display:table-header-group}
  tr{break-inside:avoid}
  .tw{overflow:visible}
  table{max-width:100%}
}
@media (max-width:640px){
  .page{padding:28px 20px 48px;font-size:15px}
  h1{font-size:1.28rem}
  .ut{font-size:1.04rem}
}
"""

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


def page_css(title, head="right", foot="center", one_per_page=False):
    """A4 版心：上 22mm 下 20mm，左 20mm，右 26mm（右侧留白给手写批注）。"""
    safe = title.replace("\\", "\\\\").replace('"', '\\"')
    rule = ('@page{size:A4;margin:22mm 26mm 20mm 20mm;'
            'font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}')
    if head:
        rule += ('@page{@top-right{content:"%s";font-size:8pt;color:%s}}'
                 % (safe, theme.value("--mark-script")))
        rule += "@page:first{@top-right{content:none}}"
    if foot:
        rule += ('@page{@bottom-center{content:counter(page) " / " counter(pages);'
                 'font-size:8.5pt;color:%s}}' % theme.value("--mark-script"))
    if one_per_page:
        rule += ".unit + .unit{break-before:page}"
    return rule


_TAG = re.compile(r"(<[^>]+>)")
_LONG = re.compile(r"([A-Za-z0-9][A-Za-z0-9_\-./:?&=#%~+@]{27,})")


def _brk(s):
    """把超长 ASCII 串（网址、长单词）包成可任意断行的 span，只处理文本节点。"""
    return "".join(
        p if p.startswith("<") else _LONG.sub(r'<span class="brk">\1</span>', p)
        for p in _TAG.split(s)
    )


def text_inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r'<span class="figref">［图：\1］</span>', s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)          # 讲稿里的链接只留文字
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"〔([^〕]*)〕", r'<span class="cue">〔\1〕</span>', s)
    return _brk(s)


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_table_start(lines, i):
    s = lines[i].strip()
    return ("|" in s and i + 1 < len(lines)
            and re.match(r"^\|?[\s:|-]+\|[\s:|-]*$", lines[i + 1].strip()) is not None)


def render_body(md):
    lines = md.split("\n")
    out, i, n = [], 0, len(lines)
    code_buf, in_code = [], False

    while i < n:
        ln = lines[i]
        s = ln.strip()

        if s.startswith("```"):
            if in_code:
                out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(code_buf)))
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

        m = re.match(r"^#{3,4}\s+(.*)$", s)
        if m:
            out.append("<h3>%s</h3>" % text_inline(m.group(1)))
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", s):
            out.append("<hr>")
            i += 1
            continue

        if is_table_start(lines, i):
            head = split_row(s)
            i += 2
            rows = []
            while i < n and lines[i].strip() and "|" in lines[i]:
                rows.append(split_row(lines[i]))
                i += 1
            t = ["<table><thead><tr>"]
            t += ["<th>%s</th>" % text_inline(c) for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join("<td>%s</td>" % text_inline(c) for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append('<div class="tw">' + "".join(t) + "</div>")
            continue

        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>%s</blockquote>"
                       % "".join("<p>%s</p>" % text_inline(x) for x in buf if x))
            continue

        if re.match(r"^[-*+]\s+", s):
            items = []
            while i < n and re.match(r"^[-*+]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*+]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>%s</ul>"
                       % "".join("<li>%s</li>" % text_inline(x) for x in items))
            continue

        if re.match(r"^\d+\.\s+", s):
            items = []
            while i < n and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>%s</ol>"
                       % "".join("<li>%s</li>" % text_inline(x) for x in items))
            continue

        buf = []
        while i < n:
            cs = lines[i].strip()
            if (not cs or re.match(r"^(#{1,4}\s|```|>|[-*+]\s|\d+\.\s)", cs)
                    or re.match(r"^(-{3,}|\*{3,}|_{3,})$", cs)
                    or is_table_start(lines, i)):
                break
            buf.append(cs)
            i += 1
        if buf:
            para = join_lines(buf)
            full = para.strip()
            if re.fullmatch(r"〔[^〕]*〕", full):
                out.append('<div class="cueblock">%s</div>' % text_inline(full))
            else:
                out.append("<p>%s</p>" % text_inline(para))
    return "\n".join(out)


def join_lines(parts):
    """中文硬换行直接相接；两侧都是拉丁字母/数字时补一个空格。"""
    out = parts[0] if parts else ""
    for p in parts[1:]:
        if re.match(r"[A-Za-z0-9]", out[-1:]) and re.match(r"[A-Za-z0-9]", p[:1]):
            out += " "
        out += p
    return out


def parse_heading(rest):
    """`U2.0 · 先分一刀　[2′]　屏 n1, n2` → (id, title, time, screens)"""
    uid, title, tmin, scr = "", rest, "", ""
    m = re.match(r"^(U[\d.]+)\s*[·:：]?\s*(.*)$", rest)
    if m:
        uid, title = m.group(1), m.group(2)
    m = re.search(r"\[([\d.]+)′\]", title)
    if m:
        tmin = m.group(1)
        title = title.replace(m.group(0), "")
    m = re.search(r"屏\s*([\w\s,，]+)$", title)
    if m:
        scr = m.group(1).strip(" ，,")
        title = title.replace(m.group(0), "")
    return uid, title.strip(" ·　"), tmin, scr


def build(md, one_per_page=False):
    lines = md.split("\n")
    title = ""
    body, intro = [], []
    units = []
    cur = None

    for ln in lines:
        if not title and re.match(r"^#\s+", ln):
            title = re.sub(r"^#\s+", "", ln).strip()
            continue
        m = re.match(r"^##\s+(.*)$", ln)
        if m:
            if cur:
                units.append(cur)
            cur = {"head": m.group(1).strip(), "buf": []}
            continue
        (cur["buf"] if cur else intro).append(ln)
    if cur:
        units.append(cur)

    spoken = 0
    for u in units:
        uid, ut, tmin, scr = parse_heading(u["head"])
        inner = render_body("\n".join(u["buf"]))
        badge = []
        if tmin:
            badge.append("<b>%s′</b>" % tmin)
        if scr:
            badge.append("屏 %s" % html.escape(scr))
        spoken += len(re.sub(r"〔[^〕]*〕|\s", "", "\n".join(u["buf"])))
        body.append(
            '<section class="unit">\n<div class="uh">'
            + ('<span class="uid">%s</span>' % html.escape(uid) if uid else "")
            + '<span class="ut">%s</span>' % text_inline(ut or u["head"])
            + ('<span class="ub">%s</span>' % " · ".join(badge) if badge else "")
            + "</div>\n%s\n</section>" % inner
        )
    if any(x.strip() for x in intro):
        body.insert(0, render_body("\n".join(intro)))
    title = title or "讲稿"

    meta = "全文约 %d 字 · 按 %d 字/分钟 ≈ %.1f 分钟" % (spoken, WPM, spoken / WPM) if spoken else ""
    head = "<h1>%s</h1>" % text_inline(title)
    if meta:
        head += '\n<p class="meta">%s</p>' % meta
    return title, head + "\n" + "\n".join(body)


def main():
    ap = argparse.ArgumentParser(description="讲稿 md → A4 打印版 html")
    ap.add_argument("src")
    ap.add_argument("-o", "--out")
    ap.add_argument("--one-unit-per-page", action="store_true",
                    help="每个单元从新页起（一单元一页，翻页与讲稿对齐）")
    ap.add_argument("--no-print-marks", action="store_true", help="打印时不加页眉页脚")
    ap.add_argument("--tokens", help="另指定配色表（默认 lecture-slides/assets/tokens.css）")
    a = ap.parse_args()

    src = Path(a.src).resolve()
    if not src.exists():
        sys.exit("源文件不存在：%s" % src)
    md = src.read_text(encoding="utf-8-sig")

    title, body = build(md, a.one_unit_per_page)
    doc = TEMPLATE.format(
        title=html.escape(title), css=CSS.replace("{{TOKENS}}", theme.css(a.tokens)), body=body,
        page_css=page_css(title,
                          head=None if a.no_print_marks else "right",
                          foot=None if a.no_print_marks else "center",
                          one_per_page=a.one_unit_per_page))

    out = Path(a.out).resolve() if a.out else src.with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print("[script] 写出 %s（%.1f KB）" % (out, len(doc.encode()) / 1024))


if __name__ == "__main__":
    main()
