---
title: 示例 · 模型分几类
---

::: screen id=n1 steps=5 title="二 · 模型分几类"
<header class="hd">
  <div class="kicker">二 · 模型地图</div>
  <h2>模型不止一种：看它吃什么、吐什么</h2>
  <p class="lead">大家口中的「AI」，是一组分工不同的模型串起来的。<span class="hl">以豆包为例拆开看，最直观。</span></p>
</header>

<div class="tbl">
  <div class="tr th">
    <span>类别</span><span>吃什么 → 吐什么</span><span>豆包里的哪一环</span>
  </div>
  <div class="tr" data-step="1"><span>文本模型（LLM）</span><span>文字 → 文字</span><span>打字提问，返回文字</span></div>
  <div class="tr" data-step="2"><span>语音识别（ASR）</span><span>声音 → 文字</span><span>按住说话，先把语音转成文字</span></div>
  <div class="tr" data-step="2"><span>语音合成（TTS）</span><span>文字 → 声音</span><span>把回答的文字念出来</span></div>
  <div class="tr" data-step="3"><span>端到端语音（S2S）</span><span>声音 → 声音</span><span>按「打电话」，全程语音，不产生文字</span></div>
  <div class="tr" data-step="4"><span>图像生成（文生图）</span><span>文字 → 图片</span><span>说「画一张」，输出图片</span></div>
  <div class="tr" data-step="4"><span>视频生成（Seedance）</span><span>文字或图 → 视频</span><span>给一张图，输出视频</span></div>
</div>

<p class="foot" data-step="5">同一个产品里，六类模型各司其职。<b>「豆包会聊天」与「豆包能画图」，背后不是同一个模型。</b></p>

<div class="deep">
  <div class="dt">课 后 细 读</div>
  <h3>为什么要先分这一刀</h3>
  <p><strong>因为「AI 好不好用」这个问题，八成是分类没分对。</strong>拿聊天模型去评画图，拿语音识别去评回答质量，结论一定是错的——评测的对象根本不是同一个东西。</p>
  <p><strong>一个产品里往往不止一个模型。</strong>豆包的对话是文本模型，说话前的听写是 ASR，念给你听的是 TTS，画图是图像生成模型，视频是 Seedance。你在一个窗口里换着用，背后换了好几台发动机。</p>
  <p><strong>端到端语音是另一条路，不是第三段。</strong>ASR → 大模型 → TTS 是「三段式串联」，中间落一层文字；端到端（Speech2Speech）把理解与生成放进同一个模型，语音直接进、语音直接出。豆包打电话走的是后者，所以它接得住语气和打断，也所以——<strong>没有一份「它听成了什么」的文字</strong>，要核对只能回听录音。要留痕、要审核、要拿转写做后续处理，三段式更合适。</p>
  <p><strong>还有一类看不见的：向量模型（embedding）。</strong>它把文字压成一串数字，用来算「这两段话像不像」。知识库能搜到你的文件、推荐能猜到你想要什么，靠的是它，不是聊天模型。它不上台讲，但「为什么它能找到我的 pdf」这个问题，答案在它身上。</p>
  <div class="box"><p><strong>一句收口：</strong>先问「这是哪一类模型」，再问「它强不强」。<strong>类别不对，比较就没有意义。</strong></p></div>
</div>
::: note
第一步行只出 LLM，停一下——先让他们看见「文字进文字出」这一条基线。
第二步 ASR 和 TTS 同时出，因为是一进一出的两端，分开讲会显得零碎。
第三步才讲 S2S，务必说清「不是第三段，是另一条路」，这是全场最容易混的点。
第五步收口原话：「豆包会聊天」和「豆包能画图」，背后不是同一个模型。这句说完再翻页。
:::
:::

::: screen id=n2 steps=3 title="二 · 语音接力"
<header class="hd">
  <div class="kicker">二 · 模型地图</div>
  <h2>一次语音问答，要经过三个模型</h2>
  <p class="lead">一句话要过三道：<span class="hl">听写、理解、表达</span>。任何一环偏弱，整句都会走样。</p>
</header>

<div class="chain">
  <div class="st" data-step="1">
    <div class="k">① 语 音 识 别　A S R</div>
    <b>声音变文字</b>
    <p>按住说话，先做听写。人名、数字、术语一旦转错，后面逐层放大。</p>
  </div>
  <div class="st" data-step="2">
    <div class="k">② 文 本 模 型</div>
    <b>想清楚怎么答</b>
    <p>真正理解语义的是这一层。回答是否切题、可用，由它决定。</p>
  </div>
  <div class="st" data-step="3">
    <div class="k">③ 语 音 合 成　T T S</div>
    <b>文字变声音</b>
    <p>它只负责把文字念出来。音色再自然，也改不了上一层的答案。</p>
  </div>
</div>

<div class="strip">三者都是模型，但<b>只有中间那个是通常说的「大模型」</b>。ASR 与 TTS 规模小、任务单一，成本低得多——主要开销在中段。</div>
<p class="qnote fw">「打电话」走的是端到端路径，中间不产生文字；画图与视频分别由图像模型、Seedance 承担，都不在这条链上。</p>
::: note
链条按段出，每段停两秒。第①段务必举例：一个人名被听错，后面全歪。
第③段是重点：音色再好也改不了答案，别让他们以为「声音自然 = 回答好」。
收口的 qnote 是给懂行的人看的，不用念，留着答问。
:::
:::
