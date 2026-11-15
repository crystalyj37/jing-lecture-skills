#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
lecture-slides build：把 .deck.md 装配成单文件 HTML 演示页。

设计取舍（重要）：
  屏内正文一律按原样 HTML 输出，不猜、不重排。
  只有四类结构由本脚本处理：
    ::: screen  切屏，收 id / steps / title 三个属性
    ::: note    演讲者备注，进 <div class="spk">（放映时不显示）
    ::: md      显式声明「这段按 markdown 转」，才做轻量转换
    ::: fml     公式块，构建期用 KaTeX 渲染成静态 HTML
  之所以不做 md→任意版式的编译器：一份讲稿的版式密度靠 CSS 决定，
  自动排版只会把手工调过的结果做得更差。版式请照 references/layouts.md 选片段。

公式为什么要构建期渲染：
  幻灯片里的公式是静态的，没有任何理由留到浏览器里算。
  构建期渲染的产物不带 katex.min.js（省 266 KB），同步完成不会闪，
  写错公式在构建时就报错而不是讲课当场白屏。代价是构建需要 node。

  写法（每行一条，说明可省）：
      ::: fml
      \bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i | 样本均值
      :::
  分隔符是「空格 + | + 空格」，取最右一处，所以公式里可以正常用 |x|。

用法：
  python3 build.py 课程.deck.md -o 课程.html
  python3 build.py 课程.deck.md -o 课程.html --check-only
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SHELL = SKILL_DIR / "assets" / "deck-shell.html"
TOKENS = SKILL_DIR / "assets" / "tokens.css"
KATEX_CSS = SKILL_DIR / "assets" / "vendor" / "katex.css"
RENDER_JS = SKILL_DIR / "scripts" / "render_math.js"


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


# ---------- 公式块 ----------

FML_SEP = re.compile(r"^(?P<tex>.*)\s+\|\s+(?P<cap>.*)$")
FML_BLOCK = re.compile(r"^:::\s*fml\s*\n(.*?)\n\s*:::\s*$", re.S | re.M)
INLINE_MATH = re.compile(r"\\\((.+?)\\\)", re.S)
# <script>/<style> 段落里的 \( 不当作公式：c4 的 canvas 脚本里有反斜杠转义。
RAW_SPLIT = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>)", re.S | re.I)


def _strip_raw(body):
    """去掉脚本、样式与 ::: fml 块，剩下的才是允许写行内公式的区域。"""
    return RAW_SPLIT.sub("", FML_BLOCK.sub("", body))


def _apply_inline(text, table):
    r"""把屏内 HTML 里的 \(...\) 换成构建期排好的行内公式。"""
    def repl(m):
        got = table.get((m.group(1).strip(), False))
        return got if got else m.group(0)
    out = []
    for seg in RAW_SPLIT.split(text):
        low = seg[:7].lower()
        if low.startswith("<script") or low.startswith("<style"):
            out.append(seg)
        else:
            out.append(INLINE_MATH.sub(repl, seg))
    return "".join(out)



def scan_fml(body):
    """
    扫出一屏里所有公式，返回 [(tex, display)]。
    说明文字里的 \\(...\\) 也算：中文字体对组合变音符号（p̂、x̄）定位是错的，
    所以说明里提符号一律走 LaTeX，不要直接打组合字符。
    """
    items = []
    for m in FML_BLOCK.finditer(body):
        for line in m.group(1).split("\n"):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            hit = FML_SEP.match(s)
            tex = hit.group("tex").strip() if hit else s
            cap = hit.group("cap").strip() if hit else ""
            items.append((tex, True))
            for im in INLINE_MATH.finditer(cap):
                items.append((im.group(1).strip(), False))
    # 屏内 HTML 里的行内公式（说明文字、图注、数字块）
    for im in INLINE_MATH.finditer(_strip_raw(body)):
        items.append((im.group(1).strip(), False))
    return items


def render_math(items):
    """
    一次 node 调用渲染全部公式，返回 {(tex, display): html}。
    故意不逐条起进程：几十条公式会让构建慢到没法用。
    """
    uniq = list(dict.fromkeys(items))
    if not uniq:
        return {}
    node = shutil.which("node")
    if not node:
        sys.exit("[build] 源稿里有公式（::: fml 或 \\(...\\)），但环境里没有 node。\n"
                 "        公式在构建期用 KaTeX 排版，需要 node 22+（https://nodejs.org）；装好再跑。\n"
                 "        暂时装不了，就先把公式换成图片，不要手拼 <sub><sup>。")
    if not KATEX_CSS.exists():
        sys.exit("[build] 缺少 %s" % KATEX_CSS)
    payload = [{"tex": t, "display": d} for t, d in uniq]
    try:
        proc = subprocess.run(
            [node, str(RENDER_JS)],
            input=json.dumps(payload, ensure_ascii=False),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        sys.exit("[build] 公式渲染超时（120s），检查是否有死循环宏。")
    if proc.returncode != 0:
        sys.exit("[build] 公式渲染失败：%s" % (proc.stderr.strip() or proc.returncode))
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.exit("[build] 公式渲染器返回了非 JSON：%s" % proc.stdout[:300])

    table, bad = {}, []
    for (tex, display), r in zip(uniq, rows):
        if r.get("ok"):
            table[(tex, display)] = r["html"]
        else:
            bad.append((tex, display, r.get("err", "")))
    if bad:
        msg = "\n".join("        · %s%s\n          ↳ %s"
                        % ("行内 " if not d else "", t, e)
                        for t, d, e in bad[:8])
        sys.exit("[build] 有 %d 条公式写错了：\n%s" % (len(bad), msg))
    return table


def katex_css(texs):
    """
    读 vendor 里的完整 KaTeX 样式，按源稿实际用到的字形裁掉没用到的字体。
    书法体、黑板体（AMS）是常用装饰，一律保留；花体、打字机体、无衬线体
    只在真用到时保留——它们合起来约 69 KB，绝大多数讲稿用不上。
    """
    css = KATEX_CSS.read_text(encoding="utf-8")
    joined = "\n".join(texs)

    # 组名对应 @font-face 里 font-family 去掉 KaTeX_ 前缀。
    # 判定要覆盖「所有会落到该字族的命令」，不只是 \mathsf/\mathtt：
    # \textsf 一样走 SansSerif，\texttt / \verb 一样走 Typewriter，
    # 漏判的后果是字体被删、字形掉回系统字体（不报错，只是难看）。
    keep = {"Main", "Math", "Size1", "Size2", "Size3", "Size4", "AMS", "Caligraphic", "Script"}
    if re.search(r"\\mathfrak\b", joined):
        keep.add("Fraktur")
    if re.search(r"\\mathtt\b|\\texttt\b|\\verb\b", joined):
        keep.add("Typewriter")
    if re.search(r"\\mathsf\b|\\textsf\b", joined):
        keep.add("SansSerif")

    def drop_unused(m):
        # vendor 里的 @font-face 有的 family 带引号、有的不带，两种都要认
        fam = re.search(r'font-family:\s*"?\s*(?:KaTeX_)?([A-Za-z0-9]+)\s*"?\s*;', m.group(0))
        if fam and fam.group(1) not in keep:
            return ""
        return m.group(0)

    return re.sub(r"@font-face\{.*?\}", drop_unused, css, flags=re.S)


def _consume_fml(body, table):
    """把 ::: fml 块换成排好版的行。渲染表里查不到 = 构建阶段就报过错，不会走到这。"""

    def render_cap(cap):
        """说明文字：普通部分转义，\\(...\\) 换成行内公式。"""
        out, pos = [], 0
        for m in INLINE_MATH.finditer(cap):
            out.append(html.escape(cap[pos:m.start()], quote=False))
            got = table.get((m.group(1).strip(), False))
            out.append(got if got else html.escape(m.group(0), quote=False))
            pos = m.end()
        out.append(html.escape(cap[pos:], quote=False))
        return "".join(out)

    def row(line):
        s = line.strip()
        if not s or s.startswith("#"):
            return ""
        hit = FML_SEP.match(s)
        tex, cap = (hit.group("tex").strip(), hit.group("cap").strip()) if hit else (s, "")
        html_math = table.get((tex, True))
        if html_math is None:
            return '<div class="fmlrow"><div class="fml">%s</div></div>' % html.escape(tex)
        out = '<div class="fmlrow"><div class="fml">%s</div>' % html_math
        if cap:
            out += '<div class="fmlcap">%s</div>' % render_cap(cap)
        return out + "</div>"

    def repl(m):
        rows = [row(ln) for ln in m.group(1).split("\n")]
        rows = [r for r in rows if r]
        # 空块不能静默通过：它会生成一个 0 行的容器，页面上只是一片空白，
        # 而 audit 看到的是「有公式样式、没有错误」，照样 0 error。
        if not rows:
            sys.exit("[build] 有空公式块（::: fml 里没有内容）。删掉它，或补上公式。")
        # data-n 让壳按行数决定字号档位；行数多时不缩就会顶出屏幕
        return '<div class="fmlset" data-n="%d">\n%s\n</div>' % (len(rows), "\n".join(rows))

    return FML_BLOCK.sub(repl, body)


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


def build_body(body, math_table):
    body = _consume_block(body, "note", "spk", render=note_md)
    body = _consume_fml(body, math_table)
    body = _apply_inline(body, math_table)
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


def build(md_path, out_path, check_only=False, tokens=None, page_title=None):
    text = md_path.read_text(encoding="utf-8-sig")
    meta, rest = parse_meta(text)
    screens = split_screens(rest)
    if not screens:
        sys.exit("[build] 没找到任何 ::: screen 块。检查标记是否为「::: screen id=xx」。")

    parts = []
    items = []
    for _, body in screens:
        items.extend(scan_fml(body))
    math_table = render_math(items)

    for i, (attrs, body) in enumerate(screens, 1):
        sid = attrs.get("id") or "s%d" % i
        steps = attrs.get("steps", "0")
        title = attrs.get("title", "")
        parts.append(
            '<section class="screen" id="%s" data-steps="%s" data-title="%s">\n%s\n</section>'
            % (sid, steps, html.escape(title, quote=True), build_body(body, math_table))
        )

    shell = SHELL.read_text(encoding="utf-8")
    doc = (shell
           .replace("{{MATH_CSS}}", katex_css([t for t, _ in items]) if items else "")
           .replace("{{TOKENS}}", load_tokens(tokens))
           .replace("{{TITLE}}", html.escape(page_title or meta.get("title") or re.sub(r"(\.deck)?\.md$", "", md_path.name)))
           .replace("{{SCREENS}}", "\n\n".join(parts))
           .replace("{{TOC}}", auto_toc(screens)))
    if re.search(r"\{\{[A-Z_]+\}\}", doc):
        left = sorted(set(re.findall(r"\{\{[A-Z_]+\}\}", doc)))
        sys.exit("[build] 模板里还有没替换掉的占位符：%s" % ", ".join(left))

    if check_only:
        print("[build] 干跑：%d 屏，%d 字节" % (len(screens), len(doc.encode())))
        return doc

    out_path.parent.mkdir(parents=True, exist_ok=True)
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
    ap.add_argument("--title", help="页面 <title>，默认取 front matter 的 title")
    a = ap.parse_args()

    src = Path(a.src).resolve()
    if not src.exists():
        sys.exit("[build] 源稿不存在：%s" % src)
    out = Path(a.out).resolve() if a.out else src.with_name(re.sub(r"(\.deck)?\.md$", "", src.name) + ".html")
    build(src, out, a.check_only, a.tokens, a.title)


if __name__ == "__main__":
    main()
