# lecture-slides · 技术说明

讲稿 `.deck.md` → 单文件 `.html`。1920×1080 放映，按空格逐行出，带演讲者备注与阅读模式。

**只做 slides。** 要同时出讲稿与详细材料，用 `lecture-pack`；它产出的 `deck.deck.md` 交给本 skill 构建。

---

## 1. 目录

| 文件 | 职责 |
|---|---|
| `SKILL.md` | 给模型看的路由说明：什么时候用、边界、工作流 |
| `assets/deck-shell.html` | 舞台壳。含全部 CSS、放映逻辑、备注面板。构建时被填充 |
| `assets/tokens.css` | **配色表**（墨水经典，54 个语义变量）。三份产物共用的唯一事实源 |
| `assets/example.deck.md` | 两屏完整示例（表格分步 + 流程链 + 备注） |
| `assets/showcase.deck.md` | 九屏样张（统计直觉），含公式与交互图的写法 |
| `assets/vendor/` | KaTeX 0.19，MIT。构建时读：JS 不进产物，CSS 与字体按需内嵌 |
| `scripts/build.py` | `.deck.md` → `.html`，含公式块的构建期渲染 |
| `scripts/render_math.js` | node 侧公式渲染器，由 `build.py` 调用 |
| `scripts/audit.py` | 静态体检（含变量闭环、公式），退出码非 0 不交付 |
| `references/authoring.md` | 源稿语法、键位、常见写法错误 |
| `references/layouts.md` | 13 种版式片段，复制改字 |
| `references/validation.md` | 浏览器量测脚本与判读表 |

依赖：**Python 3 标准库**，没有 pip 包。**只有写公式时**构建需要 node——KaTeX 在构建期把
LaTeX 排成静态 HTML，产物里既没有 katex.js 也没有字体请求。
浏览器验收用 `ego-browser`（可选，静态检查不需要）。

---

## 2. 构建链路

```
deck.deck.md
    │  build.py
    ├─ ① 读 front matter（--- 包起来的 title）
    ├─ ② 切屏：按 ::: screen 深度计数
    ├─ ③ 收内层块：::: note → <div class="spk">，::: md → 轻量 md
    ├─ ④ 公式：扫出 ::: fml 与屏内的 \(...\)，一次 node 调用交给 KaTeX 排成静态 HTML
    ├─ ⑤ 生成 <section class="screen" id data-steps data-title>
    ├─ ⑥ 填壳：{{MATH_CSS}} {{TOKENS}} {{TITLE}} {{SCREENS}} {{TOC}}
    └─ ⑦ 直接写单文件（无第三方运行时）
                │
                ▼
        deck.html（约 51 KB 空壳 + 你的内容；用了公式再加排好的 HTML 与裁剪后的字体）
```

### 五个占位符

`deck-shell.html` 里只有五处占位，`build.py` 一次性替换：

| 占位 | 填什么 |
|---|---|
| `{{TITLE}}` | front matter 的 `title`，进 `<title>` |
| `{{SCREENS}}` | 所有 `<section class="screen">` |
| `{{TOC}}` | 阅读模式侧栏的静态目录，由屏 `title` 自动生成 |
| `{{TOKENS}}` | `assets/tokens.css` 整段（含注释）。配色只有这一个出处 |
| `{{MATH_CSS}}` | KaTeX 样式（按源稿用字裁过字体）。没有公式时为空 |

替换完还有残留占位符，`build.py` 直接退出——不给你一个「看着正常、其实少了东西」的产物。
**壳里不允许有第六处占位**。要加构建期变量，改 `build.py` 的 `build()`。

### 为什么屏切分用深度计数

源稿是嵌套的：

```
::: screen ...        ← 深度 1
::: note ...          ← 深度 2
:::                   ← 回到 1
:::                   ← 回到 0，这一屏结束
```

如果简单地「遇到 `:::` 就结束」，`::: note` 的闭合会提前把屏截断。
`split_screens()` 用 `depth` 计数，`_consume_block()` 同理。

### 屏内正文为什么是 HTML，不是 Markdown

试过 md → 任意版式的编译路线，放弃了。原因：一屏的版式密度靠 CSS 决定
（列宽、行高、留白、字号阶梯），自动排版只会把手工调过的结果做得更差，
而且错的时候是**静默错**——不报错，只是投影上难看。

现在的取舍：**结构由标记管，版式由组件片段管，内容原样输出。**
`build.py` 一个字都不改屏内 HTML。想要 md，用 `::: md` 显式声明。

---

## 3. 源稿

```markdown
---
title: 课程名 · 演示页
---

::: screen id=n1 steps=5 units=U2.0 title="二 · 模型分几类"
<header class="hd">
  <div class="kicker">二 · 模型</div>
  <h2>模型不止一种：看它吃什么、吐什么</h2>
  <p class="lead">换模型是<span class="hl">换大脑</span>。</p>
</header>

<div class="tbl">
  <div class="tr th"><span>类别</span><span>吃什么</span><span>在哪</span></div>
  <div class="tr" data-step="1"><span>文本</span><span>文字 → 文字</span><span>对话</span></div>
</div>
::: note
第一步行只出 LLM，停一下。
:::
:::
```

| 属性 | 说明 |
|---|---|
| `id` | 锚点，不写则 `s<序号>` |
| `steps` | 必须等于屏内最大 `data-step`，否则 `audit.py` 报错 |
| `title` | 底栏与目录显示，**必填** |
| `units` | 可选，给 `lecture-pack` 对账用；`build.py` 不读它 |

---

## 4. 运行时

一个 IIFE，四件事：状态机、分步、翻页、装饰。

### 状态

```js
var screens = [...document.querySelectorAll('.screen')];
var state = screens.map(() => 0);   // 每屏各自记到第几步
var idx = 0, step = 0;
```

`state[]` 是关键：翻回上一屏时停在上次走到的步数，不会退回到第 0 步。

### 走一步

```js
function next(){
  if (step < nsteps(screens[idx])) { step++; state[idx]=step; paint(); }
  else if (idx < screens.length-1)  { idx++; step=state[idx]; paint(); }
}
```

**先走完本屏的步，再翻屏。** `prev()` 是镜像：先退步，退完再退屏。

### 分步怎么生效

```js
el.classList.toggle('on', i<idx ? true : i>idx ? false : (+el.dataset.step <= st));
```

已经翻过去的屏，所有 `data-step` 元素强制打开（回看时不能缺内容）。

### 显示切换用 opacity，不是 display

```css
.screen{position:absolute;inset:0;opacity:0;pointer-events:none}
.screen.active{opacity:1;pointer-events:auto}
```

这样有 0.35s 淡入，且所有屏始终在布局里——**量测脚本要按 `.screen` 逐个打开再量**，
不能靠 `display:none` 过滤。

### 演讲者备注

- 源稿 `::: note` → `<div class="spk">`，CSS 里 `.screen .spk{display:none!important}`
- 按 `S` 切换 `#spk.on`，从右侧滑出 560px 面板
- 面板内容：`标题 · 屏号` / 步数 / 备注正文 / 下一屏标题
- **不能用 `N`**：`N` 在原键位里已经绑了「直接翻下一页」（`ArrowDown`/`Enter`/`N`）
- `paint()` 末尾调 `spkPaint()`，面板开着时跟着翻页更新

### 阅读模式

按 `R` 或地址加 `?mode=read`，切 `html.demo` ↔ `html.read`：

| | `html.demo` | `html.read` |
|---|---|---|
| 根字号 | 20px | 15px |
| 溢出 | `overflow:hidden` | `overflow:auto` |
| 舞台 | 1920×1080 缩放 | 取消 transform，变成流式长页 |
| `.deep` 细读 | `display:none` | `display:block` |
| 卡片刻度 | 翻面 3D | 拆成平铺 |
| 侧栏目录 | 隐藏 | 显示 |

`html.read [data-step]{opacity:1!important}` 是兜底：阅读模式下所有分步内容一次性展开。

### 缩放

```js
var s = Math.min(innerWidth/1920, innerHeight/1080);
stage.style.transform = 'scale('+s+')';
```

舞台固定 1920×1080，整体缩放并居中。所以**任何元素的坐标都是绝对 1920×1080 坐标**，
量测时把视口锁成 1920×1080 才能拿到 1:1 的结果。

---

## 5. 命令

```bash
python3 scripts/build.py 课程.deck.md -o 课程.html
python3 scripts/build.py 课程.deck.md --check-only    # 干跑，只看屏数与体积
python3 scripts/audit.py 课程.html                    # 退出码 0 才算过
```

`build.py` 不传 `-o` 时输出同目录同名 `.html`（`课程.deck.md` → `课程.html`），输出目录不存在会自动建；
`--title` 可覆盖 front matter 的标题。源稿带 BOM（Windows 记事本存的）也能正常读。

---

## 6. audit 查什么

| 检查 | 级别 | 为什么 |
|---|---|---|
| 屏 `id` 重复 | error | 目录跳转会错 |
| `data-step` 最大值 > `steps` | error | 最后一步永远出不来 |
| `steps` > `data-step` 最大值 | warn | 多按几次空翻 |
| 步号不连续 | warn | 中间那步是死步 |
| `data-step="0"` | error | 第 0 步不会被点亮 |
| 表格行 `span` 数不一致 | error | 列错位 |
| `data-title` 为空 | error | 底栏显示 undefined |
| 图片不是 `data:` 或 `http` | warn | 换机器掉图 |
| 成品里还有 `:::` | error | 有块没被解析 |
| 占位符未替换 | error | 壳没填对 |
| `var(--x)` 的 `--x` 没定义 | error | 整条声明静默失效，页面只是「看着怪」 |
| 产物里残留 `katex.min.js` / 字体请求 | error | 说明退回了运行时渲染，放映会闪 |
| 公式渲染失败（`.katex-error`） | error | 构建期就该拦住，不该等放映白屏 |
| 说明文字里有组合字符（`p̂`） | warn | 中文字体会把帽子排到字母右下角 |
| 超过 4 MB | warn | 首屏会慢 |

**它查不出**：字压到边、第三列折行、字号太小、讲起来顺不顺。这些必须浏览器量测 + 人看一遍。

---

## 7. 改与扩

### 改配色

**只有一个主题：墨水经典。** 暖纸底 + 墨黑正文 + 朱红点色，对比 17.3:1（正文对纸）。
不再提供「换主题」开关，是有意的取舍：切换机制一旦存在，每次动颜色都要把 4 套 × 3 份产物
重新验一遍；而这一版已经验到「0 越界、0 缺页、同源两次构建 sha256 一致」，
不该为了一个不会用的功能重新开这个口子。

配色表在 `assets/tokens.css`，54 个语义变量，分六组：

| 组 | 例 | 说明 |
|---|---|---|
| 纸面 | `--paper` `--paper-card` `--paper-soft` `--paper-0` | 由暖到白，按层用 |
| 纸面·产品档 | `--paper-print` `--paper-script` | 值已统一为 `#fcfbf8`，留作将来分档的接入点 |
| 墨 | `--ink` `--ink2` `--muted` `--ghost` | 正文 → 次级 → 弱 → 水印 |
| 线 | `--line` `--line-card` `--line-soft` | 投屏线深一档，投影才看得见 |
| 点色 | `--accent` `--accent-soft` `--accent-wash` `--green` | 朱红是唯一强调色 |
| 局部 | `--fig-*` `--qr-*` `--tint-*` | 图示、二维码卡、占位；换纸色时一起看 |

改颜色 = 改这张表 → **三份产物同时变**（slides 由 `build.py` 注入，
A4 两份由 `theme.py` 注入）。改完必须重新 build，壳不会自动同步。

三个设计决定，值得知道为什么：

1. **纸面只有一档** `#fcfbf8`，三份产物同纸。`--paper-print` / `--paper-script`
   原来是历史微差（`#fdfcf9` / `#fffefb`，肉眼不可辨），已统一；两个名字保留着，
   是因为两份 A4 的别名块指着它们，将来真要分档只改这两个值。
2. **仪器色不在这张表里**：底部工具条、帮助/目录遮罩、备注面板、黑场。
   它们恒为暗色，属于放映设备而不是版面——换纸色时它们本不该跟着变。
   位置在 `deck-shell.html` 的 `.bar` / `.overlay` / `#spk` / `.black` / `html.bo`。
3. **`@page` 里不用 `var()`**：页眉页码的 margin box 不是元素，自定义属性在那里能否继承
   各引擎不一致。`theme.py` 提供 `value("--mark-print")` 取字面值填进去。

加新颜色的规矩：**先加进 tokens.css，再在组件里 `var()`**。判据是「换一套配色时它该不该跟着变」。
壳里写死新 hex，`audit.py` 查不出来，但下次改配色它就会是一块改不动的孤岛。

**校验方式（改完照做一遍）**：把改动前的 skill 复制一份到 `/tmp`，同一份源稿各构建一次，
再把两份产物的 `<style>` 里所有 `var()` 解到字面值、归一化 `#fff`/`#ffffff`、去掉 `:root` 和注释，逐字比。
抽取 token 那一轮实测：slides 34,738 字符、材料 3,786、讲稿 3,869，**逐字相同**；
正文（`</style>` 之后）也逐字相同。纸色统一之后再比，会看到 `--paper-print` / `--paper-script`
两处值变了——那是预期，不是回归。比截图可靠——截图看不出 1 个色阶，逐字比看得出。

### 加一种版式

1. 在 `<style>` 里写 `.myblock{...}`
2. **必须自己写分步样式**，否则 `data-step` 不生效：

```css
.myblock[data-step]{opacity:0;transform:translateY(8px);
  transition:opacity .35s ease,transform .35s ease}
.myblock[data-step].on{opacity:1;transform:none}
```

> 这是本 skill 最容易踩的坑：`data-step` 的隐藏**不是统一机制**，
> 是每个组件在 CSS 里各自写的（`.tr`、`.chain .st`、`.fig`、`.four .c`、
> `.pair .b`、`.steps li` 都各写了一份）。
> 新组件只写 `data-step` 属性不写这段 CSS，元素会一开始就显示，看着像"分步坏了"。

3. 在 `references/layouts.md` 补一段可复制的片段
4. 在 `assets/example.deck.md` 里加一屏示例

### 加一个键位

在 `deck-shell.html` 的 `keydown` 里加分支，注意避开已占用的：

`空格 → ← PageUp PageDown ↑ ↓ N Enter Home End B T G R F S ? H Esc`

### 加构建期变量

`build.py` 的 `build()` 末尾是三个 `.replace()`。加第四个别忘了
在 `audit.py` 的占位符检查里补一行，否则漏替换不会被发现。

---

## 8. 已知限制

1. **不做自动排版**。屏内就是 HTML，版式要选片段、要改字。
2. **不做画布定位**。没有 x/y/w/h，没有 morph 补间。要那种效果用 `bento-slides`。
3. **不内嵌视频**。视频走外链，几十 MB 的 base64 会让文件打不开。
4. **公式没有编号与交叉引用**。KaTeX 不支持 `\label`/`\eqref`，要编号只能手写 `\tag{1}`；
   长公式要在 `\begin{aligned}` 里自己断行，没有自动断行。
5. **阅读模式不是详细材料**。它只展开屏上的字 + `.deep` 块。
   真正的长文材料用 `lecture-pack` 的 `handout.py`。
6. **预览会改写文件**。交给客户端预览前先 `cp` 一份，源文件留干净的。

---

## 9. 一次完整验证（可复跑）

```bash
cd lecture-slides                              # 仓库里，或 ~/.workbuddy/skills/lecture-slides
python3 scripts/build.py assets/example.deck.md -o /tmp/t.html
python3 scripts/audit.py /tmp/t.html          # 期望 0 error / 0 warn
```

浏览器侧量测脚本在 `references/validation.md`，复制即用。
