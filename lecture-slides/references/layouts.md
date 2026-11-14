# 版式片段

屏内正文一律是 HTML。下面每个片段都可以直接粘进 `::: screen` 块里，填字即可。
**不要凭想象改 class 名**——所有样式都在 `assets/deck-shell.html` 的 `<style>` 里，写错类名不会报错，只会静默变成裸文字。

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

## 11. 视频 `.vbox`

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
