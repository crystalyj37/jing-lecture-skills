#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crosscheck.py：三份产物对账。

一份内容写成 handout / deck / script，最大的风险是改了一处、三份不同步。
这个脚本拿 content-map.md 当基准，查五件事：

  1. 单元齐不齐 —— 清单里有、某份里没有的单元
  2. 顺序对不对 —— 三份的单元序列是否一致
  3. 收口句在不在 —— 清单里写的收口，讲稿里是否原样出现
  4. 数字对不对 —— 同屏出现的数字，材料里有没有；三份有没有互相打架
  5. 时长够不够 —— 清单各单元时长合计、讲稿每单元字数换算

用法：
  python3 crosscheck.py content-map.md --script script.md --handout handout.md --deck deck.deck.md
退出码：0 = 无 error；1 = 有 error。
"""

import argparse
import re
import sys
from pathlib import Path

WPM = 240            # 中文口播字/分钟
TOL = 0.25           # 单单元字数允许超出 25%

errs, warns, infos = [], [], []


def read(p):
    if not p:
        return None
    if not Path(p).exists():
        sys.exit("文件不存在：%s" % p)
    return Path(p).read_text(encoding="utf-8-sig")


def units_of_map(text):
    """清单单元：### U2.0 · 标题，后跟 - 时长：2′"""
    out = []
    cur = None
    for line in text.split("\n"):
        m = re.match(r"^###\s+(U[\d.]+)\s*[·:：]?\s*(.*)$", line)
        if m:
            cur = {"id": m.group(1), "title": m.group(2).strip(),
                   "min": None, "close": None}
            out.append(cur)
            continue
        if cur:
            mm = re.match(r"^-\s*时长[：:]\s*([\d.]+)", line)
            if mm:
                cur["min"] = float(mm.group(1))
            mc = re.match(r"^-\s*收口[：:]\s*(.+)$", line)
            if mc:
                cur["close"] = mc.group(1).strip()
    return out


def units_of_doc(text, level=2):
    pat = r"^#{%d}\s+(U[\d.]+)" % level
    return [m.group(1) for m in re.finditer(pat, text, re.M)]


def sections(text, level=2):
    """切成 {uid: 正文}，按标题层级。"""
    pat = re.compile(r"^#{%d}\s+(U[\d.]+)[^\n]*\n" % level, re.M)
    ms = list(pat.finditer(text))
    out = {}
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        body = text[m.end():end]
        body = re.sub(r"〔[^〕]*〕", "", body)          # 去掉舞台提示
        body = re.sub(r"^\s*[-*>].*$", "", body, flags=re.M)  # 去掉行首标记行
        body = re.sub(r"\|.*\|", "", body)             # 表格不计入字数
        out[m.group(1)] = len(re.sub(r"\s", "", body))
    return out


def deck_screens(text):
    """按 ::: 深度切屏，返回 [(属性行, 正文)]；屏内的 fml / note 块不会提前截断。"""
    out, cur, buf, depth = [], None, [], 0
    for line in text.split("\n"):
        s = line.strip()
        if depth == 0:
            m = re.match(r"^:::\s*screen\b(.*)$", s)
            if m:
                cur, buf, depth = m.group(1), [], 1
            continue
        if s == ":::":
            depth -= 1
            if depth == 0:
                out.append((cur, "\n".join(buf)))
                continue
        elif s.startswith(":::"):
            depth += 1
        buf.append(line)
    return out


def nums(text):
    """提取需要核对的数字：百分数、两位以上的数。年份和编号不算。"""
    got = set()
    for m in re.finditer(r"\d+(?:\.\d+)?\s*%|\d{2,}(?:\.\d+)?", text):
        s = m.group(0).replace(" ", "")
        if re.fullmatch(r"(19|20)\d{2}", s):
            continue
        got.add(s.rstrip("%") if s.endswith("%") else s)
    return got


def main():
    ap = argparse.ArgumentParser(description="三份产物对账")
    ap.add_argument("map", help="content-map.md")
    ap.add_argument("--script")
    ap.add_argument("--handout")
    ap.add_argument("--deck", help=".deck.md")
    ap.add_argument("--total", type=float, help="总时长（分钟），不填只提示、不判超时")
    a = ap.parse_args()

    mp = read(a.map)
    if mp is None:
        sys.exit("清单不存在：%s" % a.map)

    us = units_of_map(mp)
    if not us:
        sys.exit("清单里没找到单元。格式应为：### U2.0 · 标题")
    order = [u["id"] for u in us]
    infos.append("清单 %d 个单元" % len(us))

    total = sum(u["min"] or 0 for u in us)
    missing_min = [u["id"] for u in us if u["min"] is None]
    if missing_min:
        warns.append("这些单元没写时长：%s" % "、".join(missing_min))
    if total:
        infos.append("清单时长合计 %.1f 分钟" % total)
        if a.total and total > a.total:
            errs.append("单元时长合计 %.1f 分钟，已超过给定的 %.0f 分钟" % (total, a.total))
        elif not a.total:
            warns.append("没给 --total，无法判断是否超时；合计 %.1f 分钟" % total)

    # ---- 讲稿 ----
    if a.script:
        sp = read(a.script) or ""
        su = units_of_doc(sp, 2)
        if not su:
            errs.append("讲稿里没找到 `## U2.0` 形式的单元标题")
        else:
            lack = [u for u in order if u not in su]
            extra = [u for u in su if u not in order]
            if lack:
                errs.append("讲稿缺单元：%s" % "、".join(lack))
            if extra:
                errs.append("讲稿有清单外的单元：%s" % "、".join(extra))
            if [u for u in su if u in order] != [u for u in order if u in su]:
                errs.append("讲稿单元顺序与清单不一致")

            chars = sections(sp, 2)
            for u in us:
                if u["id"] not in chars or not u["min"]:
                    continue
                budget = u["min"] * WPM
                got = chars[u["id"]]
                if got > budget * (1 + TOL):
                    warns.append("%s 讲稿 %d 字，按 %.1f 分钟应约 %d 字（超 %.0f%%）"
                                 % (u["id"], got, u["min"], budget,
                                    (got / budget - 1) * 100))
            infos.append("讲稿正文约 %d 字，按 %d 字/分钟 ≈ %.1f 分钟"
                         % (sum(chars.values()), WPM, sum(chars.values()) / WPM))

            for u in us:
                if u["close"]:
                    punct = "[，。、；：？！…\\s“”‘’\"'（）()*]"
                    core = re.sub(punct, "", u["close"])[:14]
                    if core and core not in re.sub(punct, "", sp):
                        warns.append("%s 的收口句没在讲稿里出现：" % u["id"]
                                     + u["close"][:24])

    # ---- 材料 ----
    if a.handout:
        hp = read(a.handout) or ""
        hu = units_of_doc(hp, 2)
        if hu:
            lack = [u for u in order if u not in hu]
            if lack:
                warns.append("材料缺单元：%s（若非有意裁剪，应补齐）" % "、".join(lack))
        else:
            infos.append("材料未按 Uxx 标题组织，跳过单元对账（长文常按章组织，可接受）")

        sc = read(a.script) or ""
        if sc:
            miss = nums(sc) - nums(hp)
            if miss:
                warns.append("讲稿里有、材料里没出现的数字：%s"
                             % "、".join(sorted(miss)[:12]))

    # ---- 幻灯片 ----
    if a.deck:
        dp = read(a.deck) or ""
        tagged, bodies = {}, []
        for i, (s, body) in enumerate(deck_screens(dp), 1):
            sid = re.search(r'\bid="?([\w.-]+)', s)
            sid = sid.group(1) if sid else "s%d" % i
            uu = re.search(r'units="?([^"\s]+)', s)
            if uu:
                bodies.append((sid, body))
                for x in uu.group(1).split(","):
                    tagged.setdefault(x.strip(), []).append(sid)
        if not tagged:
            warns.append("slides 的 screen 没写 units=\"U2.0\"，无法核对单元覆盖")
        else:
            uncovered = [u for u in order if u not in tagged]
            if uncovered:
                warns.append("这些单元在 slides 里没有对应屏：%s" % "、".join(uncovered))

            hp = read(a.handout) or ""
            if hp:
                for sid, body in bodies:
                    dnum = nums(body) - nums(hp)
                    if dnum:
                        errs.append("[%s] 屏上出现、材料里没有的数字：%s"
                                    % (sid, "、".join(sorted(dnum))))
            else:
                warns.append("没给 --handout，屏上数字没有核对")

    # ---- 半成品标记 ----
    for name, txt in (("讲稿", read(a.script)), ("材料", read(a.handout)),
                      ("slides", read(a.deck))):
        if not txt:
            continue
        for kw in ("待补", "待定", "TODO", "TBD", "XXX"):
            if kw in txt:
                errs.append("%s 里还有「%s」" % (name, kw))

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
