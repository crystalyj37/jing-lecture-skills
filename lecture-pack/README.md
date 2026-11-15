# lecture-pack · 技术说明

一份内容，三份产物：详细材料 `handout` / 讲稿 `script` / 演示 `deck`。
核心不是排版三遍，是**三种写作共用一份事实清单**。

**只做 slides 用 `lecture-slides`。** 本 skill 产出的 `deck.deck.md` 交给它构建。

---

## 1. 目录

| 文件 | 行数 | 职责 |
|---|---|---|
| `SKILL.md` | 170 | 给模型看的路由说明：何时用、五步流程、边界 |
| `references/pipeline.md` | 75 | 三种读者三种写法、六条铁律、时长与字数换算 |
| `references/content-map.md` | 75 | 单元字段规范与切分口径 |
| `references/script.md` | 112 | 讲稿写法、`〔 〕` 三类标记、通读检查 |
| `references/handout.md` | 120 | 材料写法、结构、长度、交付清单 |
| `scripts/crosscheck.py` | 246 | 三份对账，退出码非 0 不交付 |
| `scripts/handout.py` | 343 | `handout.md` → 单文件网页（含打印页眉页码） |
| `scripts/script.py` | 389 | `script.md` → A4 讲稿网页（分单元、`〔〕` 灰底、防跨页） |
| `scripts/pack.py` | 98 | 一条命令跑完材料、讲稿、slides、audit、对账与 PDF（`--slides-pdf` 连 slides 一起） |
| `scripts/theme.py` | 56 | 读配色表 `../lecture-slides/assets/tokens.css`，给两份 A4 注入 |
| `assets/example/content-map.md` | 29 | 样张清单（1 个单元） |
| `assets/example/script.md` | 47 | 样张讲稿 |
| `assets/example/handout.md` | 51 | 样张材料 |
| `assets/example/deck.deck.md` | 75 | 样张 slides 源稿（2 屏） |

依赖：**只有 Python 3 标准库**。没有 pip 包，不需要 node。
slides 那一步、以及两份 A4 的配色表，都依赖同级目录 `../lecture-slides/`。

---

## 2. 为什么不是「一份稿排版三遍」

同一句断言，三份里的写法必须不同：

| 产物 | 写成 | 判断标准 |
|---|---|---|
| 材料 | 为什么这个区分重要 → 六类各是什么 → 出处 | 一个没来现场的人，读它能不能懂 |
| 屏上 | `模型不止一种：看它吃什么、吐什么` + 一张六行表 | 抬头看 3 秒能不能抓住一件事 |
| 讲稿 | 「你们觉得，画图和聊天，是同一个模型吗？……不是。看这张表。」 | 扫一眼能不能接着说下去 |

内容一致，**句子不能互搬**。搬过去必然出现三种症状：屏上字太多、材料像提纲、讲稿像念稿。

所以这个 skill 里没有「一键生成三份」这种东西。它提供的是：

- 一套**字段约束**，逼你在写第一句话之前把事实定下来（`content-map.md`）
- 一份**写作口径**，三种产物各自该长什么样（`references/`）
- 一个**对账器**，改了一处忘了另外两处时能查出来（`crosscheck.py`）

---

## 3. 数据模型：清单是唯一事实源

`content-map.md` 里一个单元长这样：

```markdown
### U2.0 · 先分一刀：AI 不是一个模型

- 时长：2′
- 断言：豆包不是一个模型，是六类模型叠着用。
- 证据：

  | 类别 | 吃什么 → 吐什么 | 豆包里的哪一环 |
  | --- | --- | --- |
  | 文本模型（LLM） | 文字 → 文字 | 打字提问，返回文字 |

- 例子：按「打电话」走的是 S2S，中间不落文字。
- 误区：拿聊天模型的表现，去评价「这个 AI 好不好用」。
- 收口：先问这是哪一类模型，再问它强不强。类别不对，比较就没有意义。
- 屏：n1, n2
- 不上台：向量模型（embedding），只在材料里展开。
- 来源：依各产品公开文档与 OpenRouter 目录整理，2026 年 11 月。
```

| 字段 | 必填 | 落到哪 |
|---|---|---|
| 标题 `U<n>.<k> · 断言` | ✓ | 三份共用，**断言不是主题词** |
| 时长 | ✓ | 讲稿配速，`crosscheck` 用来判超时 |
| 断言 | ✓ | slides 标题、材料首句 |
| 证据 | 有数据就填 | 三份共用，不许各写一遍 |
| 例子 | ✓ | 讲稿必用，材料展开 |
| 误区 | | 讲稿设问，材料纠偏 |
| 收口 | ✓ | 讲稿原话，slides 可当 `.strip` |
| 屏 | 有 slides 就填 | `crosscheck` 核对覆盖 |
| 不上台 | | 只进材料，是有意的取舍记录 |
| 来源 | 有数字就填 | 材料脚注 |

### 标题层级是不对称的（容易踩）

| 文件 | 单元标题层级 |
|---|---|
| `content-map.md` | `### U2.0 · …`（三级） |
| `script.md` | `## U2.0 · …`（二级） |
| `handout.md` | `## U2.0 · …`（二级） |

`crosscheck.py` 里这两个层级的正则是焊死的：清单用 `^###\s+(U[\d.]+)`，两份成品用 `^##\s+(U[\d.]+)`。
**把清单写成 `##` 会得到「清单里没找到单元」并直接退出**；把讲稿写成 `###` 会得到「讲稿里没找到单元」。

---

## 4. 链路

```
议题 / 受众 / 时长
      │
      ▼
content-map.md   ← 唯一事实源，25–40 个单元
      │
      ├──────────► script.md      先写讲稿：逼自己把话说完整
      │                │
      ├──────────► handout.md     再写材料：把「不上台」的展开
      │                │  handout.py
      │                ▼
      │            handout.html
      └──────────► deck.deck.md   最后做 slides：只留结论与结构
                       │  ../lecture-slides/scripts/build.py
                       ▼
                   deck.html
                       │
                       ▼
              crosscheck.py  ← 对账，退出码非 0 不交付
```

**顺序不能倒。** 先做 slides 会把「话」压成「词」，回头写讲稿时已经想不起原来要说什么。

`pipeline.md` 的图画成三份并行（讲稿、材料、deck 同时从清单派生），
`SKILL.md` 画成串行。两种都合法：串行是给第一版用的，并行是熟练之后的省时做法。
**内容依赖只有一个方向：全部读清单，互不读对方。**

---

## 5. crosscheck.py

### 用法

```bash
python3 scripts/crosscheck.py content-map.md \
  --script script.md \
  --handout handout.md \
  --deck deck.deck.md \
  --total 90
```

`--script / --handout / --deck` 都可省，只查给了的那几份。
`--total` 是总时长（分钟），不填会 warn「无法判断是否超时」，并且**不会**用清单合计当总时长去比。

退出码：`0` = 无 error，`1` = 有 error。warn 不影响退出码。

### 检查项（九条，归五组）

| # | 查什么 | 拿谁当基准 | 级别 |
|---|---|---|---|
| 1 | 清单各单元时长合计 > `--total` | 清单 | **error** |
| 2 | 讲稿缺单元 / 多出清单外单元 / 单元顺序与清单不一致 | 清单 | **error** |
| 3 | 讲稿单单元字数 > 时长×240×1.25 | 清单时长 | warn |
| 4 | 清单的「收口」句没在讲稿里出现 | 清单 | warn |
| 5 | 屏上出现、材料里没有的数字 | 材料 | **error** |
| 6 | 讲稿里有、材料里没有的数字 | 材料 | warn |
| 7 | 材料缺单元 | 清单 | warn |
| 8 | slides 的 `units=` 没覆盖某个单元 | 清单 | warn |
| 9 | 三份里还有 `待补` `待定` `TODO` `TBD` `XXX` | — | **error** |

### 三个实现细节，决定了它为什么有时「没报」

**① 数字只认两位以上**

```python
r"\d+(?:\.\d+)?\s*%|\d{2,}(?:\.\d+)?"
```

实测：`37.5%`、`12` 会抽出来；`6 类`、`1.5 倍` 抽不出来；`2026` 因年份规则被排除，`20261` 会被抽出来。
**所以「六类」写成「6 类」这种一位数差错，它抓不到。**

**② 收口句按前 14 字做子串匹配**

去掉中英标点后取清单收口句的前 14 字，看是否整体出现在讲稿里（讲稿也先去标点）。
只改后半句会漏；改开头两个字就会报。

**③ 比的是「材料有没有」，不是「清单写没写」**

屏上的数字只要在材料里出现过就算过。这条设计能抓住「屏改了、材料没改」，但抓不住
「清单和材料一起写错、屏跟着错」——见第 11 节。

### 字数怎么算

`WPM = 240`（中文口播字/分钟），`TOL = 0.25`。
讲稿正文先剔掉 `〔舞台提示〕`、行首 `-`/`*`/`>` 标记行、整行表格，再数非空白字符。
表格内容不计入字数——表格是给眼睛看的，不是念的。

---

## 6. handout.py

### 用法

```bash
python3 scripts/handout.py handout.md -o handout.html
python3 scripts/handout.py handout.md -o handout.html --title "示例分享" --no-toc
```

标题默认取 md 里第一个 `# `；输出路径默认同目录同名 `.html`。

### 支持的语法

标题 h1–h4 / 段落 / 无序与有序列表 / 管道表格 / 引用 / 代码块 / 分隔线 /
行内 `**粗体**` `` `代码` `` `[链接](url)` `![图](path)`。

**不支持**：脚注语法、数学公式、单元格内转义 `\|`、表格对齐标记（`:---:` 会被当成分隔行忽略）。

### 目录的触发条件

```python
if want_toc and len(toc) >= 3:
```

只收 h2 与 h3。**少于 3 个标题就不生成目录**，而且不提示——
一篇只有 1 个 h2 的材料会静默没有目录。要强制关掉用 `--no-toc`。

### 版式（实测值）

| 视口 | `.page` 宽 | 正文宽 | 表格宽 | 横向溢出 |
|---|---|---|---|---|
| 1440 | 760 | 616 | 616 | 无 |
| 1024 | 760 | 616 | 616 | 无 |
| 375 | 375 | 331 | 331（宽表最宽 570，在框内横滑） | 无，`scrollWidth` = 375 |

正文 16px / 行高 1.92（30.72px），衬线字体，`text-align:justify`。

`@media print` 里去阴影、满宽、加 A4 页边注（详见下一节）。

### 表格：手机上内部滚动，打印时满宽

每张表外面包了一层 `<div class="tw">`。屏幕上 `.tw{overflow-x:auto}`，
窄屏时表格在框内横向滑动，**页面本身不会被撑宽**（实测 375px 下
`documentElement.scrollWidth` 恒等于 375）；打印时 `.tw{overflow:visible}`，
表格满宽铺开。没有这层包裹，手机上十列表会把整页拉到 570px 宽。

### 超长串：`.brk`

网址和长英文单词由 `_brk()` 包成 `<span class="brk">`，CSS 是 `word-break:break-all`。

原因是实测出来的：只写 `overflow-wrap:break-word` 时，一个 100 字符的长词**能整行放下**，
于是浏览器把它整体推到下一行，上一行只剩「一个很长的英文单词：」七个字，
再被 `text-align:justify` 拉开——字间距大到像排版事故。改成 `anywhere` 也没用，
因为长词单独成行并不算溢出。真正的解法是让它**可以从中间断开**，行才会被填满。

`_brk()` 只处理文本节点（按标签切分后逐段替换），不会碰 `<a href>` 里的属性。

### 图片

本地图片直接转 base64 内嵌，换机器不掉图；`http(s)://` 与已是 `data:` 的原样保留。

### 两个会咬人的行为

**① 一个段落跨多行，行间会被插入空格**

段落是 `" ".join(buf)` 拼的。中文手写时习惯在 60 字处硬换行，结果正文里就多出空格：

```
第一行文字这里结束
第二行接着写同一段
```

→ `<p>第一行文字这里结束 第二行接着写同一段</p>`

**对策：一个自然段写成一行**（编辑器软换行即可，不要敲回车）。

**② `<span class="math">` 只是字体**

`.math` 只给了 `Times New Roman` + 斜体。它不排版公式，`x^2` 不会变成上标。
真公式用 slides 那边的 KaTeX 方案，或直接写 Unicode。

## 7. script.py（讲稿的 A4 排版）

### 用法

```bash
python3 scripts/script.py script.md -o script.html
python3 scripts/script.py script.md -o script.html --one-unit-per-page   # 一单元一页
python3 scripts/script.py script.md -o script.html --no-print-marks      # 不要页眉页码
```

和 `handout.py` 的区别：它是**给台上看的纸**，不是给读者看的网页。

| 项 | handout | script |
|---|---|---|
| 版心 | 760px 单栏，屏幕优先 | A4 20mm 边距，打印优先 |
| 正文字号 | 16px | 11.5pt（≈15.3px），行高 1.8 |
| 分节 | h2 起新节 | `## ` 即一个单元，单元间一条细分隔线 + 序号/标题/时长徽标 |
| 目录 | 有（≥3 个标题） | **没有**，台上没人翻目录 |
| `〔 〕` | 普通文字 | 整段只有它 → 独立灰底块；夹在句中 → 行内灰字 |
| 防跨页 | 表格/图可拆，行不拆 | 同左（`--one-unit-per-page` 强制一单元一页） |

页眉取 md 的 `# ` 标题，`@page:first` 不出；页脚是 `当前页 / 总页`。
`--no-print-marks` 两个一起去掉。

标题下的元信息行（`全文约 N 字 · 按 240 字/分钟 ≈ M 分钟`）是**脚本自己算的**，
不读 md 里手写的数字——手写的会过期。

**讲稿里 `[文字](url)` 只保留文字，`![图](path)` 变成「［图：说明］」。** 口播不会去点链接，
所以讲稿 PDF 里没有 `/Link` 注释——这是设计，不是漏了。要可点的地址，放材料那份。

## 8. 打印：@page 实测结论

**Chrome（headless=new，实测 157.0.8103.78）支持 `@page` 页边注。** 这一点和早期资料说的
「Chrome 不认 `@page` 的页边注、只能靠打印接口带页眉」不一致，以实测为准。

```css
@page{ size:A4; margin:20mm;
  @top-right{ content:"讲稿 · U2.0"; font-size:8pt; color:#9a9286 }
  @bottom-center{ content:counter(page) " / " counter(pages); font-size:8.5pt }
}
@page:first{ @top-right{content:none} }   /* 首页不出页眉 */
```

实测确认的四件事：

1. 页码 `1 / 56` 每页都有，末页总页数正确；
2. `@page:first` 生效——首页最上面的词 y≈55.9pt（正文顶），第二页页眉 y≈15.6pt；
3. **必须加 `--no-pdf-header-footer`**，否则 Chrome 自己的页眉页脚会再叠一层；
4. 打印时表格可以跨页（`thead` 重复表头），但**不要**给 `table` 加
   `break-inside:avoid`——一张长表会被整体推到下一页，前面留半页空白。

### 打印出来的链接：能点，但要让人看得出能点

Chrome 打印时会把 `<a>` 写成 PDF 注释（`/Subtype /Link` + `/URI`），**可点性不需要额外处理**。
实测对照：

| 写法 | PDF 里 | 可点 |
|---|---|---|
| `[文字](https://…)` | `/Link` + `/URI` | 是 |
| `[写信](mailto:…)` | `/Link` + `/URI` | 是，唤起邮件客户端 |
| 跨行的长链接 | 拆成两条注释，两行都能点 | 是 |
| 目录里的 `#锚点` | `/Link` + `/Dest` | 是，跳章节 |
| 裸网址（不写成 `[文字](url)`） | 纯文本 | **否** |

问题不在可点性，在**可见性**：早期打印规则写的是 `a{color:inherit;border:0}`，
把颜色和线一起抹平，PDF 里链接和正文长得一模一样，读者不知道哪能点。现在改成：

```css
@media print{
  a{color:inherit;border:0;text-decoration:none}
  a[href^="http"]{color:var(--accent);border-bottom:1px dotted rgba(156,47,30,.55)}
  a[href^="mailto"]{color:var(--accent);border-bottom:1px dotted rgba(156,47,30,.55)}
  .toc a,.toc a.lv3{color:inherit;border:0}   /* 目录保持无色，否则整框飘红 */
}
```

用属性选择器而不是给 `a` 加类，是因为不想让行内渲染多长出一个属性；`mailto` 单独一条，
否则只有 `http` 有标记、邮箱看不出来。加 1px 点线后 56 页的真实长文**仍是 56 页**、
出界词 0，说明这点高度没有推翻分页。

出 PDF 的命令：

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --no-sandbox \
  --print-to-pdf=out.pdf --no-pdf-header-footer in.html
```


---

## 9. 与 lecture-slides 的接缝

只有一个字段：

```
::: screen id=n1 steps=5 units=U2.0 title="二 · 模型分几类"
```

- `units="U2.0"` 给 `crosscheck.py` 用，多个用逗号：`units="U2.0,U2.1"`
- `build.py` **完全不读** `units`，它只认 `id` / `steps` / `title`
- 不写 `units` → `crosscheck` 报「slides 的 screen 没写 units=，无法核对单元覆盖」

`lecture-pack` 里**不实现任何排版**。版式、分步、备注都在 `lecture-slides`，
改那边改一处，这边不用动。

### 第二条接缝：配色表

除了 `units=` 字段，两个 skill 还共享一份文件：`../lecture-slides/assets/tokens.css`。
它是全库唯一的配色事实源，三份产物都从这里取色（见 §10「改配色」）。
所以目录结构上 `lecture-pack` 依赖同级 `lecture-slides` 存在；缺了会在生成时直接报错，
并提示用 `--tokens` 指定。

---

## 10. 改与扩

### 改配速或容差

`crosscheck.py` 顶部两个常量：

```python
WPM = 240     # 中文口播字/分钟；讲得快可调 280
TOL = 0.25    # 单单元允许超出 25%
```

调 `TOL` 要同步改 `references/pipeline.md` 的换算表，否则文档和脚本打架。

### 加一条检查

在 `main()` 里按现有三段（讲稿 / 材料 / slides）找位置，用 `errs.append` 或 `warns.append`。
**级别要想清楚**：error 会阻断交付，只留给「发出去会当场翻车」的问题；
风格类、可能是有意裁剪的，一律 warn。

新增检查必须同时加一条反例，跑一遍确认它真的会报——`audit` 类脚本最常见的失败是
「写了检查但条件永远为假」，跑出来 0 error 让人以为过了。

### 改配色

**两份 A4 没有自己的调色板。** 颜色只有一份：`../lecture-slides/assets/tokens.css`（墨水经典，54 个变量）。
`scripts/theme.py` 把它整段注入 `<style>` 的 `{{TOKENS}}` 位置，再用一小段「产品别名」把通用角色
绑到 A4 那一档：

```css
:root{ --ink:var(--ink-print); --ink2:var(--ink2-print); --muted:var(--muted-print);
       --paper:var(--paper-print); --line:var(--line-print); }   /* 讲稿另有 --code → --code-script */
```

于是 `p{color:var(--ink)}` 在两份 A4 里分别落到 `#1a1815`，在投屏里落到 `#17150f`——写一次，各走各的档。

三个要点：

1. **不存副本**。找不到配色表就报错退出，不静默回退到内置色（副本一定会漂）。
   单独用本 skill 时用 `--tokens <path>` 指向一份 tokens.css。
2. **`@page` 取字面值**。页眉页码写在 margin box 里，那地方不是元素，
   自定义属性能否继承各引擎不一致；`theme.py` 的 `value("--mark-print")` 直接算出 `#8a8378` 填进去。
3. **CSS 里已无硬编码色**，只剩页面投影 `rgba(0,0,0,.08)`（屏上看着像纸片，打印时去掉）与几种
   透明度叠加。要加新颜色，加进 tokens.css 再用 `var()`。

改完照 lecture-slides README「改配色」末尾的办法验一遍：前后各构建一次，
把 `var()` 解到字面值逐字比。本轮实测材料 3,786 字符、讲稿 3,869 字符逐字相同。

### 改材料版式

样式全在 `handout.py` 的 `CSS` 常量里（第 28–115 行）。三个断点/区间：

- 默认：760px 版心，正文 616
- `@media (max-width:640px)`：页边距 32/22，h1 降到 1.55rem，表格 0.86rem
- `@media print`：去阴影、满宽、避免断行

改完只需重新生成 handout，不需要动 md。

### 加一种产物

比如「一页纸摘要」。正确做法是：清单加字段 → 新写一份 `references/xxx.md` 定口径 →
在 `crosscheck.py` 加一个可选参数。**不要**让新产物去读 `handout.md`，
那会破坏「所有产物只读清单」这一条。

---

## 11. 已知限制

**能力边界**

1. **不做内容取舍**。讲什么、砍什么由人定；这个 skill 只保证三份一致。
2. **不代写观点**。素材从用户的讲稿、论文、课程里取。
3. **不生成 slides 版式**。交给 `lecture-slides`。
4. **handout.py 不是完整 Markdown 实现**。脚注、公式、单元格转义都没有。
5. **没有 Word 输出**。要 .docx 把 md 交给 `workbuddy-docx`，不要在这边加转换。

**对账查不出的（都是实测确认的）**

6. **清单与材料直接打架没人管。** 实测：清单写「460 个模型」、材料写「400 类」、
   屏也写 400 —— 0 error。因为它只比「屏 ⊂ 材料」，不比「清单 ⊂ 材料」。
7. **材料的单元顺序不查。** 实测把材料里的两个单元颠倒，0 error。只查缺不缺。
8. **一位数差错不查。** 「六类」写成「6 类」，两边都过。
9. **只给 `--deck` 不给 `--handout` 时，屏上数字没法核对**，只给一条 warn。**核对数字时三份都要给。**
10. **`待补` 是全文子串匹配。** 材料里正当地讨论「怎么避免待补」也会被判 error。
11. **收口句只比前 14 字**，改后半句抓不到。

**排版上仍然存在的（这一轮实测出来的）**

12. **PDF 靠本机 Chrome 打印，字形随字体走。** CSS 写的是 `Songti SC`，macOS 有；
    换到 Windows 会退到别的宋体，行高与页数会变。**页码要靠重新打印核对，不要手改。**
13. **`@page` 页边注依赖 Chrome 版本。** 实测 157 版可用；换浏览器（Safari/Firefox）
    页眉页码会消失或行为不同。只在 Chrome 里承诺这个格式。
14. **整页图会独占一页。** 源稿里放一张 1920×1080 的二维码图，打印就是接近满宽的一张，
    后半页留白。这是源稿的图文比例决定的，脚本不裁图；要密一点就在 md 里改图或用并排版式。
15. **手机上宽表只能在框内横滑。** 页宽不会被撑开（实测恒定 375），但十列表要
    左右滑动才看得全。手机端不承诺「一屏看全」。
16. **讲稿的单元边界认 `## `，不认 `### `。** 用三级标题分单元，整份讲稿会变成一个单元，
    元信息里的字数与时长也会算成一整段。
17. **微信里打开 PDF 基本点不动。** 微信内置阅读器多数不处理 PDF 注释，看着像链接、
    点了没反应。要发群就同时给 html 版——html 里的链接任何环境都能点。
18. **手写的 `#锚点` 会静默失效。** 标题 id 由脚本自动生成（`h2-0`、`h2-1`），
    在 md 里写 `[跳到第三节](#第三节)` 指不过去，**不报错**，PDF 里这条链接直接消失。
    要内部跳转就用目录，别手写锚点。

---

## 12. 一次完整验证（可复跑）

```bash
cd ~/.workbuddy/skills/lecture-pack/assets/example

# 对账：期望 0 error / 0 warn，退出码 0
python3 ../../scripts/crosscheck.py content-map.md \
  --script script.md --handout handout.md --deck deck.deck.md --total 6

# 材料：期望约 14 KB，1 个 h2 + 4 个 h3，目录 5 项
python3 ../../scripts/handout.py handout.md -o /tmp/h.html

# 讲稿：期望约 13 KB，1 个单元，元信息「全文约 552 字 ≈ 2.3 分钟」
python3 ../../scripts/script.py script.md -o /tmp/s.html

# slides：期望 2 屏约 69 KB，audit 0 error / 0 warn
python3 ~/.workbuddy/skills/lecture-slides/scripts/build.py deck.deck.md -o /tmp/d.html
python3 ~/.workbuddy/skills/lecture-slides/scripts/audit.py /tmp/d.html
```

上面四步也可以一条命令跑完：`python3 ../../scripts/pack.py . -o /tmp/dist --total 6 --pdf`。

打印两份 PDF 并体检（`pdftotext` 来自 poppler，macOS 可用 `brew install poppler`）：

```bash
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
for n in h s; do
  "$CH" --headless=new --disable-gpu --no-sandbox \
        --print-to-pdf=/tmp/$n.pdf --no-pdf-header-footer /tmp/$n.html
done
pdftotext -f 1 -l 1 /tmp/h.pdf -    # 期望：首行是标题，没有页眉；末行有 1 / N
pdftotext -bbox /tmp/h.pdf - | grep -c 'xMax'   # 出界词数应为 0
# 链接可点性：注释数应与 md 里的 [文字](url) 个数一致
python3 -c "import re;d=open('/tmp/h.pdf','rb').read();print('Link',len(re.findall(rb'/Subtype\s*/Link',d)))"
```

**这一轮的实测基线**（同一份 111 KB 真实提纲，1–6 号逐项验过）：

| 项 | 材料 handout | 讲稿 script |
|---|---|---|
| 页数 | 56 | 53（同一份源文按 `##` 切） |
| 出界词（PDF 逐词比右边距） | 0 | 0 |
| 缺页码的页 | 0 | 0 |
| 同源两次构建 sha256 | 一致 | 一致 |
| 375px 下 `scrollWidth` | 375（无溢出） | 375 |
| 首页页眉 | 无（`@page:first` 生效） | 无 |

**改这个 skill 之后，至少重跑一遍负样本**：把清单某单元的收口句改掉、
在屏上加一个材料里没有的三位数，确认分别报 warn 与 error；
再拿一张十列表 + 一条长网址的边界稿打印一次，确认没有词越过右边距。
只跑正样本会掉进「检查条件被自己改坏了」的坑。
