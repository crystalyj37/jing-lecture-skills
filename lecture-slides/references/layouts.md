# 版式片段

屏内正文一律是 HTML。下面每个片段都可以直接粘进 `::: screen` 块里，填字即可。
**不要凭想象改 class 名**——所有样式都在 `assets/deck-shell.html` 的 `<style>` 里，写错类名页面不会报错，只会静默变成裸文字；`audit.py` 会把壳里没有的类名列成 warn，并提示最接近的已知名（`--strict` 下变 error）。

画布固定 1920×1080，底部留 40px 给工具条。内容高度按 em 估：正文 20px 基准，
一屏放得下的量大致是「标题 + 4 行表格」或「标题 + 三列 × 两行卡片」。

---

## 1. 屏头（几乎每屏都要）

```html
<header class="hd">
  <div class="kicker">二 · 模型</div>
  <h2>模型不止一种：看它吃什么、吐什么</h2>
  <p class="lead">换模型是<span class="hl">换大脑</span>，换产品是换整副身体。</p>
</header>
```

- `kicker` 是左上角小字，写「第几节 · 主题」，同一节内保持一致
- `h2` 一屏只说明一件事，超过 22 字在投影上会换行挤压下方
- `lead` 一行，`<span class="hl">` 是朱红强调，**一屏最多两处**

## 2. 表格 `.tbl`

```html
<div class="tbl">
  <div class="tr th"><span>类别</span><span>吃什么 → 吐什么</span><span>豆包里的哪一环</span></div>
  <div class="tr" data-step="1"><span>文本模型</span><span>文字 → 文字</span><span>对话、写作</span></div>
  <div class="tr" data-step="2"><span>图像模型</span><span>文字 → 图片</span><span>配图、海报</span></div>
</div>
```

- 每行 `span` 数量必须一致，否则列会错位（`audit.py` 会拦）
- `data-step="n"` 让该行在第 n 步才出现，配合屏上的 `steps=n`
- 表头用 `class="tr th"`；不需要表头就省掉
- 追加类名改列宽/密度：`flat`（无边框横线风）、`src`（来源清单）、`tight`（紧凑）。
  需要特殊列宽时，**去正式文件里找同款屏，抄它的 class 串**，不要自己编。
- 四列数据用 `class="tbl t4"`：列宽固定成 `13rem 15rem 14rem 1fr`，末列右对齐并用等宽数字。
  三列的 `.tbl` 里塞四个 `span`，第四项会折到下一行、底部说明被压住

## 3. 四宫格 `.four`

```html
<div class="four">
  <div class="c"><div class="t">六个术语</div><span class="ghost">01</span><p class="d">定位一次失败的真正成因。</p></div>
  <div class="c"><div class="t">模型怎么选</div><span class="ghost">02</span><p class="d">四项指标。</p></div>
  <div class="c"><div class="t">工具分几层</div><span class="ghost">03</span><p class="d">按产物落点分层。</p></div>
  <div class="c"><div class="t">明天交什么</div><span class="ghost">04</span><p class="d">课程页面与组卷。</p></div>
</div>
```

`ghost` 是大号浅色序号，纯装饰。**四项是上限**，多一项改用 `.tbl`。

## 4. 翻面卡 `.cards`

```html
<div class="cards">
  <button class="card"><div class="inner">
    <div class="face front">
      <span class="idx">①</span><span class="w">Model</span><span class="organ">大脑</span>
      <span class="brief">按模式生成，不是资料库</span><span class="flip-hint">点 击 展 开</span>
    </div>
    <div class="face back">
      <p class="one">参数里是海量文本中学到的规律，不是可查询的数据库。</p>
      <p class="teach">教学场景：<b>问它没读过的书，它会编出目录。</b></p>
    </div>
  </div></button>
</div>
```

- 一张卡 = 一个 `button.card`，翻面靠 JS 给 `.card` 加 `.flip`，不用写事件
- 卡片张数 3 或 6 排得最好看；4 张会留空
- **别把要讲的内容只放在背面**——学生看不到翻过来的那一面，讲完就没了

## 5. 流程链 `.chain`

```html
<div class="chain">
  <div class="st" data-step="1">
    <div class="k">① 语 音 识 别　A S R</div>
    <b>声音变文字</b>
    <p>按住说话，先做听写。人名、数字转错，后面逐层放大。</p>
  </div>
  <div class="st" data-step="2">
    <div class="k">② 文 本 模 型</div>
    <b>想清楚怎么答</b>
    <p>真正理解语义的是这一层。</p>
  </div>
</div>
```

- 2–4 段；`.k` 里用小字 + 全角空格排字距，别写长句
- 分段用 `data-step` 逐段出，讲完一段再出下一段

## 6. 分层折叠 `.layers`

```html
<div class="layers">
  <div class="layer">
    <button class="lh">
      <span class="no">①</span><span class="nm">聊天助手</span>
      <span class="where">网页／桌面／手机同属这层</span><span class="rep">ChatGPT · Claude · 豆包</span>
      <span class="arrow">＋</span>
    </button>
    <div class="lb"><div class="lb-in">
      <div><h4>强 在 哪</h4><p>打开即用，问答改写总结。</p></div>
      <div class="bad"><h4>短 板</h4><p>止步于复制环节，不发布。</p></div>
      <div><h4>适 合 谁</h4><p>只需把一道题换个说法讲清。</p></div>
    </div></div>
  </div>
</div>
```

- 点 `.lh` 展开，同时只开一层（JS 已处理）
- 一屏 3–4 层；层里三栏固定是「强在哪 / 短板 / 适合谁」，短板那栏加 `class="bad"`

## 7. 一句话横条 `.strip`

```html
<div class="strip">三者都是模型，但<b>只有中间那个是通常说的「大模型」</b>。</div>
```

放在表格或链条下面做结论。一屏最多一条，写一句判断，不写解释。

## 8. 课后细读 `.deep`

```html
<div class="deep">
  <div class="dt">课 后 细 读</div>
  <h3>为什么「同一颗大脑」装进不同产品会像换了个人</h3>
  <p>因为它拿到的办公桌大小、档案室权限、手脚和规矩都不一样。</p>
</div>
```

- 演示时是屏幕右下的折叠块，阅读模式（按 R，或 `?mode=read`）整段展开
- 写「讲不完但值得看」的内容，**不要重复屏上已有的字**
- 一屏一块，超过 300 字考虑拆屏

## 9. 二维码排 `.qrrow`

```html
<div class="qrrow">
  <div class="qrtext">
    <div class="qmain">
      <div class="qtag">① 先扫它</div>
      <p class="qbig">讲义、例题、习题按章编排，集中于同一网址。</p>
      <ul class="qlist"><li>每章独立成页</li><li>案例已替换为当期素材</li></ul>
    </div>
    <p class="qnote">后两条在第四节展开。</p>
  </div>
  <div class="qrcard">
    <div class="qrhead"><b>① 课程网站</b><i>网页 · 整门课</i></div>
    <div class="qrbody">
      <div class="qrframe"><img class="qrimg" alt="课程站二维码" src="data:image/png;base64,..."></div>
    </div>
    <div class="qrfoot">
      <div class="qrcap">微 信 扫 一 扫</div>
      <div class="qrurl">example.link/p/xxxx</div>
    </div>
  </div>
</div>
```

- 二维码必须 `data:` 内嵌，否则换机器就掉图
- `qrcard--app` 用于「要装客户端」那种，视觉上与网页类区分开

## 10. 插图 SVG `.fig`

```html
<div class="fig">
  <svg viewBox="0 0 1200 560" role="img" aria-label="一句话说明这张图在讲什么">
    ...
  </svg>
  <p class="figcap">图注：一句话，不重复正文。</p>
</div>
```

- `viewBox` 宽高比按 `1200×560` 起，实际高度由宽度撑开
- `aria-label` 必写，既是无障碍也是给自己复盘的检查点
- SVG 里的字不要小于 18px，投影上看不清
- 图与图注是**竖向**两个兄弟节点：`svg` 按宽度撑满、高度自适应，图注在图下占满整宽。
  别给 `.fig` 再塞一个并排容器——横排会把图压到六成宽，图里的字跟着缩
- 两张图并排对比，用 `.pair` 包两个 `.fig`（各占一半），不要在 `.fig` 内部自己分栏

## 11. 公式 `::: fml`

```markdown
::: fml
\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i | 样本均值
\mathrm{SE}(\bar{x})=\frac{\sigma}{\sqrt{n}} | 标准误
\left|\frac{x-\mu}{\sigma}\right| \le 1 | 含竖线也照常
:::
```

- 一行一条，写法是 `LaTeX | 说明`，说明可省略。分隔符是**空格 + `|` + 空格**，取最右一处，
  所以公式里写 `|x|`、`\left|...\right|` 不会被切开
- **写 LaTeX，不要手搓 HTML**。`\bar{x}`、`\sqrt`、`\sum` 的上下限由排版引擎处理，
  自己用 `<sub><sup>` 拼出来的上下限会并排、根号的横线接不上勾尖
- 公式在**构建时**排好，产物里是静态 HTML：没有 katex.js、不会闪、写错直接构建报错
- 每条公式必须写在一行内。要多行对齐用 `\begin{aligned}...\end{aligned}`，中间用 `\\` 换行，
  但整段仍是一行文本
- 中文写在 `\text{}` 里，例如 `\text{披露溢价}`；上下标用 `_{\text{买入}}`
- 说明文字里要提符号，用行内公式 `\(...\)`：

```markdown
::: fml
\hat p=\frac{1}{B}\sum_{b=1}^{B}\hat p_b \quad | 置换检验里 \(\hat p\) 的标准误
:::
```

**不要直接打组合字符**（`p̂`、`x̄`、`σ̂` 这类「字母 + U+030x」）。中文字体对组合变音符号的
定位是错的，帽子会飘到字母右下角，看着像个小撇。`audit.py` 会扫源稿并提示改成 `\(...\)`。

**不要直接打 Unicode 根号 `√`**。它只是一个字符，不会盖住被开方的内容：`√n` 没有横线、`n` 悬在旁边，
斜杠两侧也只是普通打字间距。写 `\(\sqrt{n}\)`。`√` 同样会被 `audit.py` 扫出来（`::: note` 里的口头说法放行）。
表格里的 `±`、`×` 不用改——那是正规排印符号，换成 `\pm`、`\times` 反而字重不齐、等宽数字对不齐。

行内公式不止能用在这张表的「说明」里：屏内 HTML 的**任何可见文字**（导语、图注、卡片标题、大号数字块）
都写 `\(...\)`，构建时统一排版。`<script>` 与 `<style>` 段落里的反斜杠不会被当成公式。

- 行数到 4 行会自动降一档字号，7 行以后字会很小——**超过 4 条就拆成两屏**
- 太长的公式宁可 `\begin{split}` 手断，硬撑会顶出版心

构建公式需要 `node`（只在构建时用，产物不需要）。缺 node 时 build 会明确报错，不会静默降级。

## 12. 交互图 `.chart`

```html
<header class="hd tight">
  <div class="kicker">交互图 · 条形图</div>
  <h2>二十四位经理，四种量法</h2>
</header>

<div class="chart">
  <div class="ctl">
    <span class="lab">显示</span>
    <button class="on" data-st="rec">综合 z</button>
    <button data-st="wiki">原始值</button>
  </div>
  <div class="cv">
    <div class="fig on" data-st="rec"><svg viewBox="0 0 1400 720">…</svg></div>
    <div class="fig" data-st="wiki"><svg viewBox="0 0 1400 720">…</svg></div>
  </div>
  <div class="fcap">横轴：知名度指标</div>
</div>
```

- 图在**构建/生成阶段**就排成 SVG 内嵌，运行时只切 `display`，不引图表库、不现场重绘
- 按钮与图靠 `data-st` 配对；切换逻辑在壳里（`.chart` 存在即生效），源稿不用写 JS
- 图必须带 `viewBox`，否则只能按宽度撑开，会把页头挤走
- 图表屏用 `<header class="hd tight">`（kicker + 标题，不放导语和脚注）。页头做满时图只剩
  500px 高，会被缩到原尺寸的一半，图里的字投到幕布上是糊的
- 阅读模式下 `.chart` 会自动放宽到 1120px。820px 的正文栏会把 1400 宽的图缩到 0.59 倍，
  12px 的字只剩 7px

## 13. 视频 `.vbox`

```html
<div class="vbox">
  <video preload="metadata" playsinline poster="封面.jpg">
    <source src="视频.mp4" type="video/mp4">
  </video>
  <button class="vplay" type="button">播 放</button>
</div>
```

视频建议外链，别 base64 内嵌（几十 MB 会让文件打不开）。

---

## 选版式的顺序

1. 这一屏要让人**看见一个结构**（分类、顺序、层级、对照）→ 用 `.tbl` / `.chain` / `.layers`
2. 要让人**记住几个词** → 用 `.four` / `.cards`
3. 要让人**做一件事**（扫码、看视频）→ 用 `.qrrow` / `.vbox`
4. 都不是 → 老老实实 `hd` + 几段话，别硬套组件

**一屏只用一种主结构。** 表格 + 链条 + 四宫格堆在同一屏，是投影上最常见的失败。
