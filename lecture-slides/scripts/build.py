#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lecture-slides build：把 .deck.md 装配成单文件 HTML 演示页。

设计取舍（重要）：
  屏内正文一律按原样 HTML 输出，不猜、不重排。
  只有三类结构由本脚本处理：
    ::: screen  切屏，收 id / steps / title 三个属性
    ::: note    演讲者备注，进 <div class="spk">（放映时不显示）
    ::: md      显式声明「这段按 markdown 转」，才做轻量转换
  之所以不做 md→任意版式的编译器：一份讲稿的版式密度靠 CSS 决定，
  自动排版只会把手工调过的结果做得更差。版式请照 references/layouts.md 选片段。

用法：
  python3 build.py 课程.deck.md -o 课程.html
  python3 build.py 课程.deck.md -o 课程.html --check-only
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SHELL = SKILL_DIR / "assets" / "deck-shell.html"
TOKENS = SKILL_DIR / "assets" / "tokens.css"


def load_tokens(path=None):
    """
    读配色表。整段注入 shell，不解析、不改写——所以 tokens.css 里可以写注释、
    可以分组，人看着就是一张调色板。
    """
    p = Path(path).expanduser().resolve() if path else TOKENS
    if not p.exists():
        sys.exit("[build] 找不到配色表：%s\n"
                 "        默认位置是 <skill>/assets/tokens.css，可用 --tokens 指定。" % p)
    css = p.read_text(encoding="utf-8").strip()
    if ":root" not in css:
        sys.exit("[build] 配色表里没有 :root 块：%s" % p)
    return css


SCREEN_OPEN = re.compile(
    r'^:::\s*screen\s+(?P<attrs>.*)$', re.MULTILINE
)
ATTR = re.compile(r'(\w+)\s*=\s*"([^"]*)"|(\w+)\s*=\s*(\S+)')


def parse_meta(text):
    """读 front matter：--- 包起来的 key: value。"""
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, text[m.end():]


def parse_attrs(s):
    out = {}
    for m in ATTR.finditer(s):
        if m.group(1):
            out[m.group(1)] = m.group(2)
        else:
            out[m.group(3)] = m.group(4)
    return out


def split_screens(text):
    """
    按 ::: screen 切块，用深度计数处理内层的 ::: note / ::: md。
    返回 [(attrs, body)]。
    """
    screens, cur, buf, depth = [], None, [], 0
    for line in text.split("\n"):
        s = line.strip()
        if s.startswith("::: screen"):
            if cur is not None:          # 上一屏没正确收口，兜底
                screens.append((cur, "\n".join(buf)))
            cur, buf, depth = parse_attrs(s[len("::: screen"):]), [], 1
            continue
        if cur is None:
            continue                     # 屏外的杂物丢掉
        if s.startswith(":::"):
            if s == ":::":
                depth -= 1
                if depth == 0:
                    screens.append((cur, "\n".join(buf)))
                    cur, buf = None, []
                    continue
            else:
                depth += 1
            buf.append(line)
        else:
            buf.append(line)
    if cur is not None:
        screens.append((cur, "\n".join(buf)))
    return screens


def _consume_block(body, tag, cls, render=None):
    """
    把 ::: tag ... ::: 收成一个 div，支持同类不嵌套、异类嵌套。
    返回替换后的正文。
    """
    out, inner, depth = [], [], 0
    head = re.compile(r"^:::\s*" + tag + r"\b")
    for line in body.split("\n"):
        s = line.strip()
        if depth == 0 and head.match(s):
            depth = 1
            inner = []
            continue
        if depth:
            if s == ":::":
                depth -= 1
                if depth == 0:
                    raw = "\n".join(inner)
                    out.append('<div class="%s">\n%s\n</div>' % (cls, render(raw) if render else raw))
                    continue
            elif s.startswith(":::"):
                depth += 1
            inner.append(line)
        else:
            out.append(line)
    if depth:  # 没收口，原样吐回去，交给 audit 报错
        out.append(":::%s\n%s\n:::" % (tag, "\n".join(inner)))
    return "\n".join(out)


def md_lite(src):
    """极简 markdown：只处理段落、无序列表、**粗体**、`代码`。"""
    blocks, cur = [], []

    def flush():
        if not cur:
            return
        txt = "\n".join(cur).strip()
        if txt.startswith("- "):
            items = [ln[2:].strip() for ln in txt.split("\n") if ln.startswith("- ")]
            blocks.append("<ul>" + "".join("<li>%s</li>" % _inline(i) for i in items) + "</ul>")
        else:
            for para in re.split(r"\n\s*\n", txt):
                if para.strip():
                    blocks.append("<p>%s</p>" % _inline(para.strip().replace("\n", "")))
        cur.clear()

    for line in src.split("\n"):
        if line.strip().startswith("- "):
            cur.append(line)
        elif not line.strip():
            flush()
        else:
            if cur and not cur[-1].strip().startswith("- "):
                cur.append(line)
            elif cur:
                flush()
                cur.append(line)
            else:
                cur.append(line)
    flush()
    return "\n".join(blocks)


def note_md(src):
    """
    备注专用：每行一段，保留写稿时的断行。
    备注是「一条一条照着说」的，合并成一段就没法一眼扫。
    """
    lines = [ln.strip() for ln in src.split("\n")]
    out = []
    for ln in lines:
        if not ln:
            continue
        if ln.startswith("- "):
            out.append("<li>%s</li>" % _inline(ln[2:]))
        else:
            out.append("<p>%s</p>" % _inline(ln))
    html_out = "\n".join(out)
    # 相邻 li 包进 ul
    html_out = re.sub(r"(?:<li>.*?</li>\n?)+",
                      lambda m: "<ul>%s</ul>" % m.group(0).replace("\n", ""), html_out)
    return html_out


def _inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    return s


def build_body(body):
    body = _consume_block(body, "note", "spk", render=note_md)
    # ::: md 块内做转换
    def md_block(m):
        return md_lite(m.group(1))
    body = re.sub(r':::\s*md\s*\n(.*?)\n:::', md_block, body, flags=re.S)
    return body.strip()


def auto_toc(screens):
    rows = []
    for attrs, _ in screens:
        sid = attrs.get("id") or "s%d" % (len(rows) + 1)
        rows.append('  <a href="#%s">%s</a>' % (sid, html.escape(attrs.get("title", sid))))
    return "\n".join(rows)


def build(md_path, out_path, check_only=False, tokens=None):
    text = md_path.read_text(encoding="utf-8")
    meta, rest = parse_meta(text)
    screens = split_screens(rest)
    if not screens:
        sys.exit("[build] 没找到任何 ::: screen 块。检查标记是否为「::: screen id=xx」。")

    parts = []
    for i, (attrs, body) in enumerate(screens, 1):
        sid = attrs.get("id") or "s%d" % i
        steps = attrs.get("steps", "0")
        title = attrs.get("title", "")
        parts.append(
            '<section class="screen" id="%s" data-steps="%s" data-title="%s">\n%s\n</section>'
            % (sid, steps, html.escape(title, quote=True), build_body(body))
        )

    shell = SHELL.read_text(encoding="utf-8")
    doc = (shell
           .replace("{{TOKENS}}", load_tokens(tokens))
           .replace("{{TITLE}}", html.escape(meta.get("title", md_path.stem)))
           .replace("{{SCREENS}}", "\n\n".join(parts))
           .replace("{{TOC}}", auto_toc(screens)))
    if re.search(r"\{\{[A-Z_]+\}\}", doc):
        left = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", doc)))
        sys.exit("[build] 模板里还有没替换掉的占位符：%s" % ", ".join(left))

    if check_only:
        print("[build] 干跑：%d 屏，%d 字节" % (len(screens), len(doc.encode())))
        return doc

    out_path.write_text(doc, encoding="utf-8")
    print("[build] 写出 %s（%d 屏，%.1f KB）"
          % (out_path, len(screens), len(doc.encode()) / 1024))
    return doc


def main():
    ap = argparse.ArgumentParser(description="lecture-slides：把 .deck.md 装配成单文件 HTML")
    ap.add_argument("src", help="源稿路径（.deck.md）")
    ap.add_argument("-o", "--out", help="输出 html 路径")
    ap.add_argument("--check-only", action="store_true", help="只干跑，不写文件")
    ap.add_argument("--tokens", help="另指定配色表（默认 <skill>/assets/tokens.css）")
    a = ap.parse_args()

    src = Path(a.src).resolve()
    if not src.exists():
        sys.exit("[build] 源稿不存在：%s" % src)
    out = Path(a.out).resolve() if a.out else src.with_suffix(".html")
    build(src, out, a.check_only, a.tokens)


if __name__ == "__main__":
    main()
