---
name: lecture-pack
description: "把同一个议题/课程/分享写成两到三份互相咬合的文件：① 可分享给听众或学生的详细材料（长文或网页）；② 可放映的 HTML slides；③ 讲者自己的讲稿（口播句 + 时间 + 现场提示）。适用于要上台讲、同时又要把内容留给听众的场合（讲座、公开课、答辩、培训）。当用户说「一份内容出两版/三版」「同时要讲稿和材料」「讲座材料整理成可分享的」时使用。产出经 crosscheck 对账，保证三份的单元、顺序、数字一致。slides 部分交给 lecture-slides 构建。不适用于只做 slides（用 lecture-slides）、只做 Word/PPT 单件（用 workbuddy-docx / workbuddy-pptx）。四份源稿齐了用 scripts/pack.py 一条命令出全套并对账。关键词：一份内容三版、讲稿+材料+slides、讲座材料、讲义、课件配讲稿、handout、speaker script、lecture pack、三产物同步。"
agent_created: true
---

# lecture-pack

一份内容，三份文件。核心不是「复制三遍」，是**三种写作共用一份事实**。

## 先说清楚这不是什么

不是把一份稿子排版三遍。同一句「AI 不是一个模型」：

| | 写成 |
|---|---|
| 材料 | 为什么这个区分重要 → 六类各是什么 → 出处。读者没到场也能懂 |
| 屏上 | `模型不止一种：看它吃什么、吐什么` + 一张六行表 |
| 讲稿 | 「你们觉得，画图和聊天，是同一个模型吗？……不是。看这张表。」 |

内容一致，句子不能互搬。搬了就会：屏上字太多、材料像提纲、讲稿像念稿。

## 三份东西

| 产物 | 文件 | 读者 | 判断标准 |
|---|---|---|---|
| 详细材料 | `handout.md` → `handout.html` → `.pdf` | 听众、学生，会后独自读 | 一个没来现场的人，读它能不能懂 |
| 讲稿 | `script.md` → `script.html` → `.pdf` | 只有你 | 扫一眼能不能接着说下去 |
| 演示 | `deck.deck.md` → `.html` | 台下抬头看 3 秒的人 | 一屏能不能只说一件事 |

**html 是源，pdf 是打印产物。** 只改 md，不要手改 html——下次重新生成就覆盖了。
出 pdf 用本机 Chrome（命令见 `references/handout.md`「打印」一节）。

**什么时候不必三份都做**：内部同步只做 slides；录播做讲稿 + slides；投稿存档只做 handout。
判断标准是「散场后听众手里还剩什么」——什么都没有，就必须有材料。

## 流程

```
议题 / 受众 / 时长
      ↓
content-map.md         ← 唯一事实源（25–40 个单元）
      ↓
   script.md           ← 先写讲稿：逼自己把话说完整
      ↓
   handout.md          ← 再写材料：把「不上台」的部分展开
      ↓
   deck.deck.md        ← 最后做 slides：只留结论与结构
      ↓
crosscheck.py          ← 对账：单元 / 顺序 / 收口句 / 数字 / 时长
      ↓
handout.pdf / script.pdf  ← 打印：A4、有页眉页码、逐页不出界
```

顺序不能倒。先做 slides 会把「话」压成「词」，回头写讲稿时已经想不起原来要说什么。

## 资源

`<SKILL>` = `~/.workbuddy/skills/lecture-pack`

| 路径 | 用途 |
|---|---|
| `references/pipeline.md` | 三产物分工、铁律、时长与字数换算表 |
| `references/content-map.md` | 单元字段规范（断言/证据/例子/误区/收口/不上台/来源） |
| `references/script.md` | 讲稿写法、`〔 〕` 标记、通读检查 |
| `references/handout.md` | 材料写法、结构、长度、交付清单 |
| `assets/example/` | 一份真实样张：清单 + 讲稿 + 材料 + deck（同一单元） |
| `scripts/handout.py` | `handout.md` → 单文件网页（单栏、可打印、自动目录、图片内嵌） |
| `scripts/script.py` | `script.md` → A4 讲稿网页（分单元、`〔〕` 灰底、页眉页码） |
| `scripts/crosscheck.py` | 三份对账 |
| `scripts/pack.py` | 一条命令跑完：材料 → 讲稿 → slides → audit → 对账 →（`--pdf`）打印 |
| `scripts/theme.py` | 配色表读取器：拿 `../lecture-slides/assets/tokens.css` 注入两份 A4 |

配色表不在本 skill：`../lecture-slides/assets/tokens.css`（单主题「墨水经典」，54 个变量）。
`theme.py` 负责把它注入两份 A4，并用别名把 `--paper/--ink/--line` 指到 A4 那一档。
**不要在本 skill 的 CSS 里写新的 hex**，也不要在 `:root` 里另起一套颜色。

### 工具

四份源稿放同一目录时，优先用一条命令跑完（产物在 `<目录>/dist/`，任一步没过退出码 1）：

```bash
python3 <SKILL>/scripts/pack.py <目录> --total 90 --pdf
```

单独跑某一步：

```bash
# 材料：md → 网页
python3 <SKILL>/scripts/handout.py handout.md -o handout.html

# 讲稿：md → A4 网页（打印用；--one-unit-per-page 一单元一页）
python3 <SKILL>/scripts/script.py script.md -o script.html

# 对账：清单为基准，查三份
python3 <SKILL>/scripts/crosscheck.py content-map.md \
  --script script.md --handout handout.md --deck deck.deck.md --total 90

# slides：交给 lecture-slides
python3 <SKILL>/../lecture-slides/scripts/build.py deck.deck.md -o deck.html
```

出 PDF（材料与讲稿同一条命令，只是换文件）：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf=handout.pdf --no-pdf-header-footer handout.html
```

`--no-pdf-header-footer` 不能省，否则 Chrome 自带的页眉页脚会叠在 CSS 的 `@page` 之上。

## 执行要点

### 1. 单元先于文字

先定 25–40 个单元，每个单元写死 `断言 / 例子 / 收口` 三个字段。
**写不出收口句的单元，说明它还不是一个单元**，合并到相邻的去。

### 2. 数字只写一次

清单里写一次，三份都引用。改数字先改清单，再跑 `crosscheck.py`。
屏上出现 460、材料里还是 400，是这类工作最典型的翻车，也是最难自己看出来的。

### 3. 讲稿按 240 字/分钟配

一个 `[2′]` 的单元约 480 字。**各单元时长加总要比总时长少 5–8%**，留给现场卡顿和问答。
加总刚好等于总时长，实际一定超。

### 4. slides 走 lecture-slides

`deck.deck.md` 的屏块加 `units="U2.0"`，crosscheck 才能核对单元覆盖：

```
::: screen id=n1 steps=5 units=U2.0 title="二 · 模型分几类"
```

版式与构建规则见 `lecture-slides` skill，不要在 lecture-pack 里另写一套。

### 5. 交付前一定跑对账

```bash
python3 <SKILL>/scripts/crosscheck.py ... --total <分钟>
```

退出码非 0 不交付。它查：单元缺失/多余/顺序错、收口句改了、屏上的数字材料里没有、
讲稿单单元超时 25%、还没写完的「待补」。

**它查不出的是「写得好不好」**，那部分只能自己通读。

### 6. 打印后再量一次

PDF 出来不要直接发，先量四件事（命令见 `references/handout.md`）：

1. **页码**：`pdftotext -f 1 -l 1` 看首页有没有页眉（应当没有）、页脚有没有 `1 / N`；
2. **出界**：`pdftotext -bbox` 逐词比右边距（A4 20mm ≈ 51pt），越界的词应为 0；
3. **空白页**：逐页数字数，少于 80 字的页要确认是「图版页」而不是表格被整体推下去了；
4. **链接**：PDF 里 `/Subtype /Link` 注释数应与 md 的 `[文字](url)` 个数一致；
   裸网址不会变链接。**微信里 PDF 链接多数点不动**，发群时同时给 html 版。

已知会咬人的三处：长网址被 `justify` 拉开（已在 CSS 里用 `.brk` 处理）、
给 `table` 加 `break-inside:avoid` 会造出半页空白、换机器打印字体回退会改页数。
打印版的外链带一条暗红点线（`a[href^="http"]`），否则纸上链接与正文同色，读者不知道能点。

## 常见问题

| 现象 | 原因与处理 |
|---|---|
| 材料写得像提纲 | 每节只写了结论没有论证。补「为什么」和「反例」 |
| 讲稿念着别扭 | 书面语混进来了。出声读一遍，改成能说出口的句子 |
| slides 和材料对不上 | 没走 `crosscheck.py`。先改清单，再重新生成 |
| 时长总是超 | 清单单元太多，或每单元字数超 25%。砍单元，不要赶语速 |
| 材料太长没人看 | 缺「上不上台」的取舍。把细节放进附录，正文只留主干 |

## 边界

- **不做内容取舍**：讲什么、砍什么由人定。这个 skill 只保证三份一致。
- **不做设计**：版式交给 lecture-slides（slides）与 handout.py 的阅读版式（材料）。
- **不代写观点**：素材从用户的讲稿、论文、课程里取，不替他生成立场。
