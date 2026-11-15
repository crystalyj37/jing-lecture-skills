---
name: lecture-slides
description: "把一份讲稿做成可放映的单文件 HTML 演示页：流式排版、按空格分步出内容、演讲者备注（S 键）、阅读模式、单文件离线可开。适用于讲课/分享/答辩的 slides，尤其是单屏内容密度大、需要「讲的时候一行一行出、课后还能当材料读」的场景。当用户说「做个讲座 HTML」「把这门课做成 slides」「这页要能分步演示」「要演讲者备注」时使用；也用于修改已有的 .deck.md / 由本 skill 生成的 html。只做 slides；要同时出讲稿与详细材料，用 lecture-pack。不适用于 .pptx（转 workbuddy-pptx）、Bento 画布式演示（转 bento-slides）、资料库学习页（转 library）。也适合带 LaTeX 公式、可切换数据图的课件与学术报告。关键词：lecture-slides、讲座 HTML、讲课 slides、课件、组会/学术报告、单文件演示、分步揭示、演讲者备注、阅读模式、LaTeX 公式、HTML slides、speaker notes。"
agent_created: true
---

# lecture-slides

一份讲稿 → 一个 `.deck.md` → 一个 `.html`。单文件、离线、双击就放。

## 它解决什么

讲课用的 slides 有两个互相打架的要求：**讲的时候要少**（一次只出一行，观众才有注意力），
**课后要能读**（同一份东西，学生拿回去要能当材料看）。PPT 只能满足前者，PDF 两头都不占。

这套东西的答案是同一份内容两种形态：

| 形态 | 怎么进 | 长什么样 |
|---|---|---|
| 演示 | 直接打开 | 1920×1080，一屏一事，按空格逐行出 |
| 阅读 | 按 `R` 或地址加 `?mode=read` | 全部展开，侧栏目录，`.deep` 细读块全开 |

外加一条 PPT 没有、Bento 有的能力：**演讲者备注**（按 `S` 右侧拉出，观众看不到）。

## 边界

| 请求 | 走哪 |
|---|---|
| 讲座 / 分享 / 答辩的 HTML slides，要分步、要能课后读 | **本 skill** |
| 改已有的 `.deck.md`，或改本 skill 生成的 html | **本 skill** |
| 要 `.pptx` / 只说「做个 PPT」 | `workbuddy-pptx` |
| 要 Bento 画布、morph 转场、浏览器里可视化编辑 | `bento-slides` |
| 资料库里的学习页 / 门户页 | `library` 或页面类 skill |

本 skill **不做**：内容取舍（哪页该讲什么由人定）、画布式绝对定位、浏览器内可视化编辑器。

## 资源

| 路径 | 用途 |
|---|---|
| `assets/deck-shell.html` | 舞台壳：全部 CSS（约 740 行）+ 放映逻辑 + 备注面板。构建时被填充 |
| `assets/tokens.css` | **配色表（唯一事实源）**：墨水经典，54 个语义变量 + 注释。三份产物共用 |
| `assets/example.deck.md` | 两屏完整示例（表格分步 + 流程链 + 备注），起手先读它 |
| `assets/vendor/` | KaTeX 0.19。构建时读：JS 不进产物，CSS 与按需裁剪的字体内嵌进 HTML |
| `scripts/build.py` | `.deck.md` → 单文件 `.html` |
| `scripts/render_math.js` | 构建期公式渲染（node 调 KaTeX），由 build.py 自动调用 |
| `scripts/audit.py` | 静态体检，退出码非 0 不交付 |
| `references/authoring.md` | 源稿语法、分步写法、键位、常见写法错误 |
| `references/layouts.md` | **13 种版式片段**，直接复制改字 |
| `references/validation.md` | 浏览器量测脚本与判读表 |

## 工作流

`<SKILL>` = `~/.workbuddy/skills/lecture-slides`

### 1. 先有内容，再有版式

不要在没想清楚「每屏让人记住什么」的时候开写 HTML。先拿到讲稿（或提纲），
对着它分屏：**一屏一件事**。分屏时同步定三样：

- 屏序与 `title`（「二 · 模型分几类」，序号 + 短名，底栏和目录都显示这个）
- 哪些屏要分步（`steps`），分几步
- 每屏的口头补充（`::: note`）——这部分**不上屏**

### 2. 写源稿

照 `references/authoring.md`。屏内正文直接是 HTML，版式从 `references/layouts.md`
整段复制。**不要自己发明 class**：写错了不报错，只会在投影上变成裸文字。
起手时先看一遍 `assets/example.deck.md` —— 两屏，含表格分步、流程链、备注三种写法。

```markdown
::: screen id=n1 steps=3 title="二 · 模型分几类"
<header class="hd">
  <div class="kicker">二 · 模型</div>
  <h2>模型不止一种：看它吃什么、吐什么</h2>
  <p class="lead">换模型是<span class="hl">换大脑</span>，换产品是换整副身体。</p>
</header>
... 版式片段 ...
::: note
先讲文本模型，别提前把图像讲了——一讲就乱。
:::
:::
```

### 3. 构建

```bash
python3 <SKILL>/scripts/build.py 课程.deck.md -o 课程.html
python3 <SKILL>/scripts/audit.py 课程.html
```

### 4. 体检

`audit.py` 过 0 error 后，跑 `references/validation.md` 里的浏览器量测脚本，
再自己按一遍空格走完全程。**量测能抓越界和小字，抓不到「讲起来顺不顺」**，那部分必须人看。

### 5. 交付

交付前把 html 复制一份到别的目录再预览——预览会改写被预览的文件，源文件要留干净的。
文件名用 `<主题>_<场景>.html`，别把 `test`/`v2`/`最终` 留在正式文件名上。

## 公式

公式写成 `::: fml` 块，**在构建时**用 KaTeX 排好，产物里是静态 HTML：

```markdown
::: fml
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i | 样本均值
\mathrm{SE}(\bar{x})=\frac{\sigma}{\sqrt{n}} | 标准误
:::
```

这么设计是为了避开三件事：产物不必带 266 KB 的 katex.min.js；同步完成，放映时不会先闪一下
`\frac{a}{b}` 再跳成公式；写错公式在构建阶段就报错，而不是讲课当场白屏。

四条要记住：

1. **写 LaTeX，不要手搓 HTML**。`\sum_{i=1}^{n}` 的上下限、`\sqrt` 的横线、`\bar{x}` 的位置
   都由引擎处理；自己用 `<sub><sup>` 拼，上下限会并排、根号的勾和横线会散开。
2. **说明文字里提符号，用 `\(...\)`**。比如 `置换检验里 \(\hat p\) 的标准误`。
   不要直接打 `p̂` —— 中文字体对组合变音符号的定位是错的，帽子会飘到右下角。
   `audit.py` 会扫源稿把这类写法挑出来。
3. **一屏 3–4 条**。到 4 行会自动降一档字号，7 行以后就小了；更多请拆屏。
4. **构建需要 node**（产物不需要）。缺 node 时 build 直接报错并说明原因，不会静默降级成源码。
   空公式块、以及 `\href` / `\htmlClass` 这类需要 trust 的命令，也会在构建阶段报错——
   它们在页面上只会显示成一行红字，不能等到放映才发现。

公式写错的样子：

```
[build] 有 2 条公式写错了：
        · \barrac{x}
          ↳ KaTeX parse error: Undefined control sequence: \barrac
```

片段与更细的写法见 `references/layouts.md` 第 11 节。

## 交互图

一张图几种状态（换个量法、换个年份、看/不看某个样本），用 `.chart`：图在生成阶段就排成
SVG 内嵌，按钮只切 `display`。

```html
<div class="chart">
  <div class="ctl"><button class="on" data-st="a">方案 A</button><button data-st="b">方案 B</button></div>
  <div class="cv">
    <div class="fig on" data-st="a"><svg viewBox="0 0 1400 720">…</svg></div>
    <div class="fig" data-st="b"><svg viewBox="0 0 1400 720">…</svg></div>
  </div>
</div>
```

切换逻辑在壳里，源稿不用写 JS。两条硬要求：**图必须带 `viewBox`**，**页头用 `hd tight`**
（页头做满会把图压到半尺寸，字就糊了）。片段见 `references/layouts.md` 第 12 节。

## 改样式

**颜色只有一个出处：`assets/tokens.css`。** 一份「墨水经典」配色表（单主题，不设切换），
build 时整段注入 `deck-shell.html` 的 `{{TOKENS}}`。所以改颜色是改那张表，不是改壳：

```css
--paper:#fcfbf8;   /* 纸色（投屏那一档） */
--ink:#17150f;     /* 正文 */
--accent:#9c2f1e;  /* 朱红强调，一屏最多两处 */
--line:#b9ab92;    /* 分隔线 */
```

壳里其余样式照旧改 `deck-shell.html` 的 `<style>`，**一处改，所有 deck 同时生效**。

三条规矩：

1. 壳里不要再写新的 hex，只写 `var(--x)`。要新颜色，先加进 tokens.css（带一行注释说明用途）。
2. 底部工具条、目录遮罩、备注面板、黑场这几块是「仪器色」，刻意留在壳里，恒为暗色，不随配色走。
3. 改完跑 `audit.py`：它会查「用到的变量有没有定义」。漏定义不报错、只是静默失效，看着怪但查不出，
   `--split` 就这么漏过一次（对照屏直接不分栏）。

改完要重新 build 已有的 deck 才会生效（tokens 和壳都是构建时写进产物的）。

单个 deck 要脱离全局改，就在屏内写 `style="..."` 做一次性微调，别去动壳。

## 常见判断

| 问题 | 答 |
|---|---|
| 一屏塞不下 | 先删内容，不要缩字号。投影下限：正文 18px，脚注 14px |
| 要不要分步 | 观众需要「跟着你一句一句看」就分；一眼能看完的整屏出 |
| 要不要 `.deep` | 讲不完但值得带走的，放这；重复屏上文字的不放 |
| 要不要二维码 | 有要现场打开的链接就放，且必须是 `data:` 内嵌 |
| 多少屏 | 45–60 分钟 ≈ 40–55 屏，含开场扫码与收尾 |
