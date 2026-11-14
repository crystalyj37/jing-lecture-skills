#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme.py：给 handout.py / script.py 用的配色表读取器。

配色只有一份：lecture-slides/assets/tokens.css。
所以不在这里备份副本（副本必然漂），找不到就直接报错并告诉你怎么指定。

为什么 @page 里的页眉页码要取「字面值」而不是 var()：
  @page 的 margin box 不是元素，自定义属性在那里能不能继承到，各引擎不一致；
  直接算出字面值最稳，且页眉本来就不该随配色微调而变。
"""

import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CANDIDATES = [
    SKILL_DIR / "assets" / "tokens.css",                                  # 本 skill 自带（如果有）
    SKILL_DIR.parent / "lecture-slides" / "assets" / "tokens.css",        # 权威位置
]

_cache = {}


def path(explicit=None):
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.exists():
            sys.exit("[theme] 指定的配色表不存在：%s" % p)
        return p
    for p in CANDIDATES:
        if p.exists():
            return p
    sys.exit("[theme] 找不到配色表 tokens.css。\n"
             "        默认找：%s\n"
             "        它由 lecture-slides 提供；两个 skill 通常装在一起。\n"
             "        单独用本 skill 的话，用 --tokens 指向一份 tokens.css 即可。"
             % " 或 ".join(str(p) for p in CANDIDATES))


def css(explicit=None):
    """整段配色表文本，原样注入 <style>。"""
    key = ("css", str(explicit))
    if key not in _cache:
        _cache[key] = path(explicit).read_text(encoding="utf-8").strip()
    return _cache[key]


def value(name, explicit=None):
    """取单个 token 的字面值，供 @page 这类不能可靠用 var() 的地方。"""
    m = re.search(re.escape(name) + r"\s*:\s*([^;]+);", css(explicit))
    if not m:
        sys.exit("[theme] 配色表里没有 %s：%s" % (name, path(explicit)))
    return m.group(1).strip()
