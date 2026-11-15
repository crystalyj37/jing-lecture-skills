#!/usr/bin/env python3
"""brand/brand.json → README.md / docs/index.html / LICENSE / docs/img/

一个事实源，六处落点。换自己的 IP 只改 brand.json + 两张图，然后跑本脚本。

用法：
    python3 scripts/apply_brand.py            # 写入
    python3 scripts/apply_brand.py --check    # 只检查有没有漂，退出码 1 表示不一致
    python3 scripts/apply_brand.py --json other.json

只依赖 Python 3 标准库。
"""

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_JSON = ROOT / "brand" / "brand.json"

PAGE = ROOT / "docs" / "index.html"
README = ROOT / "README.md"
LICENSE = ROOT / "LICENSE"

MARKER = "<!--brand:%s-->"
MARKER_END = "<!--brand:%s:end-->"
REGION_RE = r"<!--brand:%s-->.*?<!--brand:%s:end-->"


class Brand:
    def __init__(self, data):
        self.data = data
        for key in ("name", "tagline", "owner", "repo"):
            if not data.get(key):
                raise SystemExit("[brand] brand.json 缺少必填字段：%s" % key)
        self.name = data["name"]
        self.tagline = data["tagline"]
        self.owner = data["owner"]
        self.repo = data["repo"]
        self.year = str(data.get("year") or date.today().year)
        self.copyright = data.get("copyright", self.owner)
        self.description = data.get(
            "description",
            "把一份内容做成三份互相咬合的产物：可投屏 slides、可分享材料、讲者讲稿。",
        )
        self.footer_note = data.get(
            "footer_note", "MIT · 内容示例为通用科普，与任何机构无关"
        )
        # 允许整段覆盖，否则按 owner/repo 推导
        self.github = data.get("github") or "https://github.com/%s/%s" % (self.owner, self.repo)
        self.site = data.get("site") or "https://%s.github.io/%s/" % (self.owner, self.repo)

        assets = data.get("assets", {})
        self.avatar = assets.get("avatar", "brand/assets/avatar.png")
        self.mark = assets.get("mark", "brand/assets/mark.png")

    @property
    def avatar_name(self):
        return Path(self.avatar).name

    @property
    def mark_name(self):
        return Path(self.mark).name

    # ---------- 六个落点 ----------
    def regions(self):
        r = {}

        r["head"] = (
            "<title>%s · 一份内容做成三份产物</title>\n"
            '<link rel="icon" href="img/%s">\n'
            '<meta name="description" content="%s · %s">\n'
            '<meta name="author" content="%s">\n'
            '<meta property="og:title" content="%s · 一份内容做成三份产物">\n'
            '<meta property="og:description" content="%s">\n'
            '<meta property="og:image" content="%simg/deck.png">\n'
            '<meta property="og:type" content="website">\n'
            '<meta name="twitter:card" content="summary_large_image">'
            % (self.repo, self.mark_name, self.name, self.description, self.name,
               self.repo, self.description, self.site)
        )

        r["topbar"] = (
            '<div class="brand">\n'
            '  <img src="img/%s" alt="%s">\n'
            '  <span class="bt"><b>%s</b><i>%s</i></span>\n'
            "</div>\n"
            '<a href="%s">GitHub ↗</a>'
            % (self.avatar_name, self.name, self.name, self.tagline, self.github)
        )

        r["clone-html"] = (
            "<pre>git clone %s.git\n"
            "cp -R %s/lecture-slides %s/lecture-pack ~/.workbuddy/skills/</pre>"
            % (self.github, self.repo, self.repo)
        )

        r["footer"] = (
            '<span class="fbrand"><img src="img/%s" alt="">%s</span>\n'
            '<span><a href="%s">源码</a> · <a href="%s/blob/main/lecture-slides/README.md">'
            'slides 文档</a> · <a href="%s/blob/main/lecture-pack/README.md">pack 文档</a></span>'
            % (self.mark_name, self.footer_note, self.github, self.github, self.github)
        )

        r["sub"] = "<sub>%s · %s</sub>" % (self.name, self.tagline)

        r["demo"] = (
            "- [slides 示例](%sdeck.html)（按空格推进）\n"
            "- [九屏样张](%sshowcase.html)（公式、数据图、可拖参数）\n"
            "- [材料 PDF](%shandout.pdf)\n"
            "- [讲稿 PDF](%sscript.pdf)" % (self.site, self.site, self.site, self.site)
        )

        r["clone-md"] = (
            "```bash\n"
            "git clone %s.git\n"
            "cp -R %s/lecture-slides %s/lecture-pack ~/.workbuddy/skills/\n"
            "```" % (self.github, self.repo, self.repo)
        )
        return r

    # ---------- 图片落点 ----------
    def asset_jobs(self):
        out = []
        for src_rel, dst_name in ((self.avatar, self.avatar_name), (self.mark, self.mark_name)):
            out.append((ROOT / src_rel, ROOT / "docs" / "img" / dst_name))
        return out


def indent_block(body, indent):
    lines = body.split("\n")
    return "\n".join((indent + ln) if ln.strip() else ln for ln in lines)


def new_block(key, body, indent=""):
    return "%s\n%s\n%s%s" % (
        MARKER % key,
        indent_block(body, indent),
        indent,
        MARKER_END % key,
    )


def check_markers(text, keys, path):
    for key in keys:
        op, cl = MARKER % key, MARKER_END % key
        if text.count(op) != 1 or text.count(cl) != 1:
            raise SystemExit(
                "[brand] %s 里 `%s` 区域应恰好出现一次（现在 open=%d close=%d）"
                % (path.name, op, text.count(op), text.count(cl))
            )


def apply_regions(text, path, spec):
    """spec: [(key, indent)]，按 marker 原地替换。"""
    check_markers(text, [k for k, _ in spec], path)
    for key, indent in spec:
        pat = re.compile(REGION_RE % (key, key), re.S)
        text = pat.sub(lambda m, k=key, i=indent: new_block(k, _BODY[k], i), text, count=1)
    return text


_BODY = {}


def main():
    ap = argparse.ArgumentParser(description="把 brand.json 注入页面、README 与 LICENSE")
    ap.add_argument("--check", action="store_true", help="只检查，不写文件")
    ap.add_argument("--json", default=str(DEFAULT_JSON), help="另指定 brand.json")
    a = ap.parse_args()

    path = Path(a.json)
    if not path.exists():
        sys.exit("[brand] 找不到 %s" % path)
    brand = Brand(json.loads(path.read_text(encoding="utf-8")))
    _BODY.update(brand.regions())

    if not PAGE.exists():
        sys.exit("[brand] 找不到 %s" % PAGE)
    if not README.exists():
        sys.exit("[brand] 找不到 %s" % README)

    html = PAGE.read_text(encoding="utf-8")
    md = README.read_text(encoding="utf-8")

    html_new = apply_regions(
        html, PAGE, [("head", ""), ("topbar", "    "), ("clone-html", ""), ("footer", "    ")]
    )
    md_new = apply_regions(md, README, [("sub", ""), ("demo", ""), ("clone-md", "")])

    # README 一级标题跟仓库名走
    md_new = re.sub(r"\A# .*", "# %s" % brand.repo, md_new, count=1)

    # LICENSE 的版权行
    lic_old = lic_new = None
    if LICENSE.exists():
        lic_old = LICENSE.read_text(encoding="utf-8")
        lic_new = re.sub(
            r"(?m)^Copyright \(c\) .*$",
            "Copyright (c) %s %s" % (brand.year, brand.copyright),
            lic_old,
            count=1,
        )

    jobs = brand.asset_jobs()
    missing = [str(src) for src, _ in jobs if not src.exists()]

    if missing:
        for m in missing:
            print("[brand] 缺图：%s" % m, file=sys.stderr)
        sys.exit(1)

    if a.check:
        bad = []
        if html_new != html:
            bad.append("docs/index.html 与 brand.json 不一致")
        if md_new != md:
            bad.append("README.md 与 brand.json 不一致")
        if lic_new is not None and lic_new != lic_old:
            bad.append("LICENSE 版权行与 brand.json 不一致")
        for src, dst in jobs:
            if not dst.exists() or dst.read_bytes() != src.read_bytes():
                bad.append("图片没同步：%s" % dst.relative_to(ROOT))
        if bad:
            for b in bad:
                print("[brand] ✗ %s" % b, file=sys.stderr)
            print("[brand] 跑 `python3 scripts/apply_brand.py` 修好", file=sys.stderr)
            sys.exit(1)
        print("[brand] ✓ 六处落点、两张图与 brand.json 一致")
        return

    PAGE.write_text(html_new, encoding="utf-8")
    README.write_text(md_new, encoding="utf-8")
    if lic_new is not None:
        LICENSE.write_text(lic_new, encoding="utf-8")
    for src, dst in jobs:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    print("[brand] 写入完成 → %s" % brand.name)
    for key in ("head", "topbar", "clone-html", "footer"):
        print("   docs/index.html   <!--brand:%s-->" % key)
    for key in ("sub", "demo", "clone-md"):
        print("   README.md         <!--brand:%s-->" % key)
    print("   LICENSE           Copyright (c) %s %s" % (brand.year, brand.copyright))
    for _, dst in jobs:
        print("   %s" % dst.relative_to(ROOT))


if __name__ == "__main__":
    main()
